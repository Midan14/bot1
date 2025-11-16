// Centralización y monitoreo de selectores para scraping robusto

import { MongoClient } from "mongodb";
import puppeteer from "puppeteer";

const MONGO_URL = process.env.MONGO_URL || null;
let mongoClient = null;
let mongoCollection = null;

async function initMongo() {
  if (MONGO_URL && !mongoClient) {
    mongoClient = new MongoClient(MONGO_URL);
    await mongoClient.connect();
    mongoCollection = mongoClient.db("scraping").collection("selector_logs");
    console.log("Selector monitor conectado a MongoDB");
  }
}
initMongo().catch(() => {});

// Selectores centralizados
export const SELECTORS = [
  ".roadmap-results .result",
  ".history-results .result-item",
  ".game-history .result",
  "[class*='result'][class*='history']",
  "[class*='roadmap'] [class*='result']",
  ".bead-road .bead",
  ".big-road .result",
  "[data-result]",
  ".result-b, .result-p, .result-t",
  "div[class*='banker'], div[class*='player'], div[class*='tie']"
];

// Función para detectar cambios en el DOM y registrar diferencias
export async function monitorSelectors(url) {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30000 });

  const found = [];
  for (const selector of SELECTORS) {
    const elements = await page.$$(selector);
    found.push({ selector, count: elements.length });
  }

  await browser.close();

  // Guardar log en MongoDB
  if (mongoCollection) {
    await mongoCollection.insertOne({
      url,
      found,
      timestamp: new Date()
    });
  }
  return found;
}
