// Проверка интерактивной страницы курса в headless Chrome (make page-check PAGE=…).
// Открывает страницу, ловит ошибки JS и консоли, снимает скриншот всей страницы в data/shots/.
// Код выхода 1, если на странице были ошибки. Chrome — сервис chrome слоя media (CDP, порт 9222).
//
//   node scripts/visuals/page_check.mjs <страница.html> [ширина=1100] [dark] [js-после-загрузки]
//   Вместо файла можно дать адрес сервиса в сети Docker: http://evidence:3071/ (модуль 10).
import fs from "node:fs";
import path from "node:path";

const [page, width = "1100", theme = "", script = ""] = process.argv.slice(2);
if (!page) {
  console.error("нужен путь к странице: make page-check PAGE=modules/…/visuals/x.html");
  process.exit(2);
}
const CDP = "http://127.0.0.1:9222";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

for (let i = 0; ; i++) {   // Chrome стартует 1–2 с
  try { await fetch(`${CDP}/json/version`); break; } catch { if (i > 50) throw new Error("Chrome не отвечает"); }
  await sleep(200);
}
const target = await (await fetch(`${CDP}/json/new?about:blank`, { method: "PUT" })).json();
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));

let seq = 0;
const pending = new Map();
const errors = [];
ws.addEventListener("message", (m) => {
  const d = JSON.parse(m.data);
  if (d.id && pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); }
  if (d.method === "Runtime.exceptionThrown")
    errors.push(d.params.exceptionDetails.exception?.description ?? d.params.exceptionDetails.text);
  if (d.method === "Runtime.consoleAPICalled" && ["error", "warning"].includes(d.params.type))
    errors.push(`console.${d.params.type}: ` + d.params.args.map((a) => a.value ?? a.description).join(" "));
  if (d.method === "Log.entryAdded" && d.params.entry.level === "error")
    errors.push(`${d.params.entry.source}: ${d.params.entry.text} ${d.params.entry.url ?? ""}`);
});
const send = (method, params = {}) => new Promise((r) => {
  const id = ++seq;
  pending.set(id, r);
  ws.send(JSON.stringify({ id, method, params }));
});

await send("Runtime.enable");
await send("Log.enable");
await send("Page.enable");
await send("Emulation.setDeviceMetricsOverride", { width: +width, height: 900, deviceScaleFactor: 1, mobile: +width < 500 });
if (theme === "dark")
  await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "dark" }] });
const isUrl = /^https?:\/\//.test(page);
await send("Page.navigate", { url: isUrl ? page : `file://${path.resolve(page)}` });
await sleep(1500);
if (script) {
  const res = await send("Runtime.evaluate", { expression: script, awaitPromise: true, returnByValue: true });
  if (res.result?.exceptionDetails) errors.push("script: " + res.result.exceptionDetails.exception?.description);
  else if (res.result?.result?.value !== undefined) console.log("script →", JSON.stringify(res.result.result.value));
}
await sleep(4000);   // анимации доходят до конца

const metrics = await send("Page.getLayoutMetrics");
const { width: w, height: h } = metrics.result.cssContentSize;
const overflow = Math.ceil(w) > +width;   // горизонтальная прокрутка страницы — ошибка вёрстки
const shot = await send("Page.captureScreenshot", {
  format: "png", captureBeyondViewport: true,
  clip: { x: 0, y: 0, width: Math.max(Math.ceil(w), +width), height: Math.ceil(h), scale: 1 },
});
fs.mkdirSync("data/shots", { recursive: true });
const name = isUrl ? new URL(page).host.replace(/[:.]/g, "_") : path.basename(page, ".html");
const out = `data/shots/${name}-${width}${theme ? "-" + theme : ""}.png`;
fs.writeFileSync(out, Buffer.from(shot.result.data, "base64"));

console.log(`${page}: ${Math.ceil(w)}×${Math.ceil(h)} → ${out}`);
if (overflow) errors.push(`страница шире окна: ${Math.ceil(w)} > ${width}`);
for (const e of errors) console.log("  ✗", e);
console.log(errors.length ? `ошибок: ${errors.length}` : "ошибок нет");
ws.close();
process.exit(errors.length ? 1 : 0);
