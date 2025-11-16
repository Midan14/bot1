// Microservicio básico de scraping con Puppeteer y Express

import express from "express";
import puppeteer from "puppeteer";
import fetch from "node-fetch";
import { MongoClient } from "mongodb";
import Tesseract from "tesseract.js";
// ...existing code...

const app = express();
const PORT = 3001;

// Configuración MongoDB
const MONGO_URL = process.env.MONGO_URL || null;
let mongoClient = null;
let mongoCollection = null;

async function initMongo() {
  if (MONGO_URL && !mongoClient) {
    mongoClient = new MongoClient(MONGO_URL);
    await mongoClient.connect();
    mongoCollection = mongoClient.db("scraping").collection("results");
    console.log("Conectado a MongoDB");
  }
}
initMongo().catch(() => {});

// Configuración de webhook para alertas (puede ser Telegram, Discord, etc.)
const ALERT_WEBHOOK_URL = process.env.ALERT_WEBHOOK_URL || null;

function sendAlert(message) {
  if (!ALERT_WEBHOOK_URL) return;
  fetch(ALERT_WEBHOOK_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: message })
  }).catch(() => {});
}

app.use(express.json());

app.post("/scrape", async (req, res) => {
  const { url, urls, proxy, imageUrl } = req.body;

  // OCR si se recibe imageUrl
  if (imageUrl) {
    try {
      const imageResp = await fetch(imageUrl);
      const buffer = await imageResp.buffer();
      const { data: { text } } = await Tesseract.recognize(buffer, "eng");
      return res.json({ ocr: text });
    } catch (error) {
      sendAlert(`[ERROR OCR] Error procesando imagen ${imageUrl}: ${error.message}`);
      return res.status(500).json({ error: error.message });
    }
  }

  // Permitir un solo URL o un array de URLs
  const urlList = [];
  if (url) urlList.push(url);
  if (Array.isArray(urls)) urlList.push(...urls);
  if (urlList.length === 0) {
    return res.status(400).json({ error: "Falta el parámetro 'url' o 'urls'" });
  }

  // Procesar en paralelo
  try {
    const results = await Promise.all(
      urlList.map(async (targetUrl) => {
        let browser;
        try {
          const puppeteerArgs = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-blink-features=AutomationControlled"
          ];
          if (proxy) {
            puppeteerArgs.push(`--proxy-server=${proxy}`);
          }
          browser = await puppeteer.launch({
            headless: "new",
            args: puppeteerArgs
          });
          const page = await browser.newPage();
          const response = await page.goto(targetUrl, { waitUntil: "domcontentloaded", timeout: 30000 });
          const status = response ? response.status() : null;
          const html = await page.content();

          if (status === 403 || status === 429 || /captcha/i.test(html)) {
            sendAlert(`[ALERTA SCRAPER] Bloqueo/captcha detectado en ${targetUrl} (status: ${status})`);
            await browser.close();
            return { url: targetUrl, error: "Bloqueo detectado o captcha encontrado", status, htmlPreview: html.slice(0, 500) };
          }

          await browser.close();
          // Guardar en MongoDB si está configurado
          if (mongoCollection) {
            await mongoCollection.insertOne({
              url: targetUrl,
              html,
              status,
              timestamp: new Date()
            });
          }
          return { url: targetUrl, html, status };
        } catch (error) {
          if (browser) await browser.close();
          sendAlert(`[ERROR SCRAPER] Error en ${targetUrl}: ${error.message}`);
          return { url: targetUrl, error: error.message };
        }
      })
    );
    res.json({ results });
  } catch (error) {
    sendAlert(`[ERROR SCRAPER] Error general: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
});

app.get("/", (req, res) => {
  res.send("Puppeteer Scraper API corriendo");
});

app.listen(PORT, () => {
  console.log(`Puppeteer Scraper API escuchando en puerto ${PORT}`);
});
