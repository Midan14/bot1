// Dashboard básico para monitoreo del scraper

import express from "express";
import { MongoClient } from "mongodb";

const app = express();
const PORT = 3002;

// Configuración MongoDB
const MONGO_URL = process.env.MONGO_URL || null;
let mongoClient = null;
let mongoCollection = null;

async function initMongo() {
  if (MONGO_URL && !mongoClient) {
    mongoClient = new MongoClient(MONGO_URL);
    await mongoClient.connect();
    mongoCollection = mongoClient.db("scraping").collection("results");
    console.log("Dashboard conectado a MongoDB");
  }
}
initMongo().catch(() => {});

app.get("/", async (req, res) => {
  if (!mongoCollection) {
    return res.send("MongoDB no configurado.");
  }
  const count = await mongoCollection.countDocuments();
  const last10 = await mongoCollection.find().sort({ timestamp: -1 }).limit(10).toArray();
  res.send(`
    <h1>Dashboard Scraper</h1>
    <p>Total de resultados almacenados: ${count}</p>
    <h2>Últimos 10 resultados</h2>
    <ul>
      ${last10.map(r => `<li><b>${r.url}</b> [${r.status}] - ${r.timestamp}</li>`).join("")}
    </ul>
  `);
});

app.listen(PORT, () => {
  console.log(`Dashboard web escuchando en puerto ${PORT}`);
});
