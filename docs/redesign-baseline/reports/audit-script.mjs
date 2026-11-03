// Phase 0 baseline audit. Read-only: only navigates, clicks one replay button, records.
import { chromium } from "playwright";
import AxeBuilder from "@axe-core/playwright";
import fs from "node:fs";
import path from "node:path";

const BASE = process.env.BASE ?? "http://localhost:3000";
const OUT = process.argv[2];
const EXP = "63a73b7ea3ba10a5850b166598f134a2dc0a752bf93c550e2371ee8d5b1bf656";
const MOR = "719426f0cd2db586b149943483abfe6519d45c4a39fb48aa1f4a566c514c84f3";
const ROUTES = [
  ["home", "/"],
  ["scenarios", "/scenarios"],
  ["scenario-looming", "/scenarios/LOOMING_CIRCUIT_VALIDATION"],
  ["scenario-looming-replay", "/scenarios/LOOMING_CIRCUIT_VALIDATION?replay=canonical"],
  ["scenario-course-replay", "/scenarios/EXPLORATORY_COURSE_CONTROL?replay=canonical"],
  ["experiments", "/experiments"],
  ["experiment-detail", `/experiments/${EXP}`],
  ["cockpit", `/experiments/${EXP}/cockpit`],
  ["morphology", "/morphology"],
  ["morphology-detail", `/morphology/${MOR}`],
  ["morphology-six", "/morphology/a3f090d5309d9ede0e9e0f78343a618a4bafba3fea91e5a27d37927d5ec55f79"],
  ["lab-arena", "/visual-lab/arena"],
  ["lab-research", "/visual-lab/arena/research"],
  ["lab-fly", "/visual-lab/fly"],
  ["science", "/science"],
  ["not-found", "/does-not-exist"],
  ["unknown-experiment", "/experiments/abc123"],
  ["unknown-experiment-hex", "/experiments/" + "0".repeat(64)],
];
const ALLW = { phone: { width: 390, height: 844 }, desktop: { width: 1440, height: 900 } };
const WIDTHS = Object.fromEntries(Object.entries(ALLW).filter(([k]) => !process.env.WIDTHS || process.env.WIDTHS.split(",").includes(k)));
const THEMES = (process.env.THEMES ?? "light,dark").split(",");
const only = process.env.ONLY ? process.env.ONLY.split(",") : null;

fs.mkdirSync(path.join(OUT, "shots"), { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.CHROME, args: process.env.NOWEBGL ? ["--disable-webgl", "--disable-3d-apis"] : ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const results = [];

for (const [name, route] of ROUTES) {
  if (only && !only.includes(name)) continue;
  for (const [wname, viewport] of Object.entries(WIDTHS)) {
    for (const theme of THEMES) {
      const ctx = await browser.newContext({ viewport, colorScheme: theme, deviceScaleFactor: 1, hasTouch: wname === "phone", isMobile: wname === "phone" });
      const page = await ctx.newPage();
      const requests = [], consoleErrors = [];
      page.on("request", r => requests.push({ method: r.method(), url: r.url().replace(BASE, ""), type: r.resourceType() }));
      page.on("console", m => { if (m.type() === "error") consoleErrors.push(m.text().slice(0, 300)); });
      page.on("pageerror", e => consoleErrors.push("pageerror: " + String(e).slice(0, 300)));
      const t0 = Date.now();
      let status = null;
      try {
        const resp = await page.goto(BASE + route, { waitUntil: "networkidle", timeout: 60000 });
        status = resp?.status() ?? null;
      } catch (e) { consoleErrors.push("goto: " + String(e).slice(0, 200)); }
      await page.waitForTimeout(name.startsWith("lab") || name.includes("cockpit") || name.includes("morphology-detail") || name.includes("replay") ? 4000 : 800);
      const info = await page.evaluate(() => {
        const vis = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.width > 0 && r.height > 0 && s.visibility !== "hidden" && s.display !== "none"; };
        const focusables = [...document.querySelectorAll('a[href],button,input,select,textarea,summary,[tabindex]:not([tabindex="-1"])')].filter(vis);
        const navs = [...document.querySelectorAll("nav")].map(n => ({ label: n.getAttribute("aria-label"), visible: vis(n), links: [...n.querySelectorAll("a")].map(a => ({ text: a.textContent.trim().replace(/\s+/g, " "), href: a.getAttribute("href"), current: a.getAttribute("aria-current") })) }));
        const disabled = [...document.querySelectorAll("button[disabled],input[disabled],select[disabled],[aria-disabled=true]")].map(b => ({ text: (b.textContent || b.getAttribute("aria-label") || b.getAttribute("name") || "").trim().replace(/\s+/g, " ").slice(0, 90), title: b.getAttribute("title"), describedby: b.getAttribute("aria-describedby") }));
        // Visible numeric text nodes in main: proxy for "values shown at load".
        const walker = document.createTreeWalker(document.querySelector("main") || document.body, NodeFilter.SHOW_TEXT);
        let numeric = 0; const samples = [];
        while (walker.nextNode()) { const t = walker.currentNode.textContent.trim(); const p = walker.currentNode.parentElement; if (/[-+−]?\d+(\.\d+)?/.test(t) && p && vis(p) && !p.closest("script,style,svg")) { numeric++; if (samples.length < 40) samples.push(t.slice(0, 60)); } }
        const smallText = [...document.querySelectorAll("main *")].filter(e => e.childElementCount === 0 && e.textContent.trim() && vis(e) && parseFloat(getComputedStyle(e).fontSize) < 12).length;
        const fonts = [...new Set([...document.querySelectorAll("body, h1, p, code, main *")].slice(0, 400).map(e => getComputedStyle(e).fontFamily.split(",")[0].trim()))];
        return {
          title: document.title,
          lang: document.documentElement.lang,
          h1: [...document.querySelectorAll("h1")].filter(vis).map(h => h.textContent.trim().replace(/\s+/g, " ")),
          mainCount: document.querySelectorAll("main").length,
          firstFocusable: focusables[0] ? (focusables[0].textContent.trim() || focusables[0].getAttribute("aria-label")).slice(0, 60) : null,
          hOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
          scrollWidth: document.documentElement.scrollWidth,
          pageHeight: document.documentElement.scrollHeight,
          canvases: [...document.querySelectorAll("canvas")].filter(vis).length,
          bodyBg: getComputedStyle(document.body).backgroundColor,
          navs, disabled, numeric, numericSamples: samples, smallText, fonts,
          hiddenWrappers: document.querySelectorAll("body > [hidden]").length,
        };
      });
      const shot = `${name}--${wname}--${theme}.jpg`;
      await page.screenshot({ path: path.join(OUT, "shots", shot), fullPage: true, type: "jpeg", quality: 55, timeout: 60000 }).catch(e => consoleErrors.push("shot: " + String(e).slice(0, 120)));
      let axe = null;
      if (process.env.AXE !== "0") {
        try {
          const r = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]).analyze();
          axe = r.violations.map(v => ({ id: v.id, impact: v.impact, help: v.help, nodes: v.nodes.length, targets: v.nodes.slice(0, 4).map(n => n.target.join(" ")) }));
        } catch (e) { axe = [{ id: "axe-error", impact: "n/a", help: String(e).slice(0, 200), nodes: 0 }]; }
      }
      const nonGet = requests.filter(r => !["GET", "HEAD", "OPTIONS"].includes(r.method));
      results.push({ name, route, width: wname, theme, status, ms: Date.now() - t0, ...info, consoleErrors, nonGet, requestCount: requests.length, threeLike: requests.filter(r => r.type === "script").map(r => r.url).length, axe, shot });
      console.log(`${name} ${wname} ${theme} status=${status} h1=${info.h1.length} overflow=${info.hOverflow} numeric=${info.numeric} axe=${axe ? axe.length : "-"} nonGet=${nonGet.length} errs=${consoleErrors.length}`);
      await ctx.close();
    }
  }
}

// Interaction check: the scenario "Run canonical preset" button (records request methods only).
{
  const ctx = await browser.newContext({ viewport: ALLW.desktop });
  const page = await ctx.newPage();
  const reqs = [];
  page.on("request", r => reqs.push({ method: r.method(), url: r.url().replace(BASE, ""), action: r.headers()["next-action"] ? "server-action" : null }));
  await page.goto(BASE + "/scenarios/BASELINE_CONTROL", { waitUntil: "networkidle" });
  const btn = page.getByRole("button", { name: /run canonical preset/i });
  const found = await btn.count();
  if (found) { await btn.click(); await page.waitForTimeout(4000); }
  results.push({ name: "interaction:run-canonical-preset", buttonFound: found, url: page.url().replace(BASE, ""), nonGet: reqs.filter(r => r.method !== "GET") });
  await ctx.close();
}

await browser.close();
fs.writeFileSync(path.join(OUT, `audit${process.env.TAG ? "-" + process.env.TAG : ""}.json`), JSON.stringify(results, null, 1));
console.log("done", results.length);
