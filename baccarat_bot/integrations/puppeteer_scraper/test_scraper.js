// Test básico del microservicio Puppeteer Scraper usando Jest

import fetch from "node-fetch";

const BASE_URL = "http://localhost:3001";

describe("Puppeteer Scraper API", () => {
  it("debe devolver HTML válido para una URL pública", async () => {
    const response = await fetch(`${BASE_URL}/scrape`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: "https://example.com" })
    });
    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data.html).toContain("<html");
    expect(data.status).toBe(200);
  });

  it("debe detectar bloqueo/captcha en una URL inválida", async () => {
    const response = await fetch(`${BASE_URL}/scrape`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: "https://httpbin.org/status/403" })
    });
    expect(response.status).toBe(403);
    const data = await response.json();
    expect(data.error).toBeDefined();
  });
});
