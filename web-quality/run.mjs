// Section 11 checks that can be automated. Usage: BASE=http://localhost:3000 CHROME=/path/to/chrome node run.mjs [group]
import { chromium } from "playwright";
import AxeBuilder from "@axe-core/playwright";
import fs from "node:fs";
import { EXP, MOR_SIX, NO_3D, ROUTES, WIDTHS } from "./routes.mjs";

const BASE = process.env.BASE ?? "http://localhost:3000";
const GROUPS = process.argv[2] ? [process.argv[2]] : ["routes", "a11y", "readonly", "keyboard", "motion", "resilience", "bundle"];
const GL = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"];
const results = [];
const record = (group, name, pass, detail = "") => { results.push({ group, name, pass, detail }); console.log(pass ? "PASS" : "FAIL", group, name, detail); };
const launch = (args = GL) => chromium.launch({ executablePath: process.env.CHROME || undefined, args });

const groups = {
  async routes() { // Regression: every route resolves; unknown IDs are real 404s.
    for (const [name, path, want] of ROUTES) {
      const r = await fetch(BASE + path, { redirect: "manual" });
      record("routes", name, r.status === want, `HTTP ${r.status}`);
    }
  },
  async a11y() { // axe, both themes; responsive: no page-level horizontal scroll at six widths.
    const b = await launch();
    for (const [name, path, want] of ROUTES) {
      if (want !== 200) continue;
      for (const theme of ["light", "dark"]) for (const w of [390, 1440]) {
        const ctx = await b.newContext({ viewport: { width: w, height: 900 }, colorScheme: theme }); const p = await ctx.newPage();
        await p.goto(BASE + path, { waitUntil: "networkidle" }); await p.waitForTimeout(1500);
        const v = (await new AxeBuilder({ page: p }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]).analyze()).violations.filter((x) => ["serious", "critical"].includes(x.impact));
        record("a11y", `${name} ${theme} ${w}`, v.length === 0, v.map((x) => `${x.id}:${x.nodes.length}`).join(","));
        await ctx.close();
      }
      for (const w of WIDTHS) {
        const ctx = await b.newContext({ viewport: { width: w, height: 900 } }); const p = await ctx.newPage();
        await p.goto(BASE + path, { waitUntil: "networkidle" }); await p.waitForTimeout(800);
        const over = await p.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
        record("responsive", `${name} ${w}px no horizontal scroll`, !over);
        await ctx.close();
      }
    }
    await b.close();
  },
  async readonly() { // Only GET, HEAD or OPTIONS, except the one named Server Action (the scenario replay read).
    const b = await launch(); const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } }); const p = await ctx.newPage();
    const writes = []; p.on("request", (r) => { if (!["GET", "HEAD", "OPTIONS"].includes(r.method()) && !r.headers()["next-action"]) writes.push(`${r.method()} ${r.url()}`); });
    for (const [, path, want] of ROUTES) { if (want === 200) { await p.goto(BASE + path, { waitUntil: "networkidle" }); await p.waitForTimeout(500); } }
    await p.goto(BASE + "/scenarios/LOOMING_CIRCUIT_VALIDATION", { waitUntil: "networkidle" });
    await p.getByRole("button", { name: /replay canonical scenario/i }).click(); await p.waitForTimeout(5000);
    record("readonly", "no write requests during a full run", writes.length === 0, writes.join("; "));
    await b.close();
  },
  async keyboard() { // Home to playback, and list to Cockpit to scrub, with no mouse.
    const b = await launch(); const p = await (await b.newContext({ viewport: { width: 1440, height: 900 } })).newPage();
    await p.goto(BASE + "/", { waitUntil: "networkidle" });
    await p.keyboard.press("Tab"); const skip = await p.evaluate(() => document.activeElement?.textContent?.trim());
    record("keyboard", "skip link is first", /skip/i.test(skip ?? ""), skip);
    await p.goto(BASE + `/experiments/${EXP}/cockpit`, { waitUntil: "networkidle" }); await p.waitForTimeout(2000);
    await p.locator('[role="slider"]').focus();
    const before = await p.locator('[role="slider"]').getAttribute("aria-valuenow");
    await p.keyboard.press("ArrowRight"); await p.keyboard.press("Shift+ArrowRight");
    const after = await p.locator('[role="slider"]').getAttribute("aria-valuenow");
    record("keyboard", "cockpit slider scrubs by keyboard", Number(after) === Number(before) + 11, `${before} -> ${after}`);
    const focusVisible = await p.evaluate(() => { const s = getComputedStyle(document.activeElement); return s.outlineStyle !== "none" || s.boxShadow !== "none"; });
    record("keyboard", "focus is visible on the slider", focusVisible);
    await b.close();
  },
  async motion() { // Reduced motion: no autoplay, motion tokens zero.
    const b = await launch(); const p = await (await b.newContext({ reducedMotion: "reduce" })).newPage();
    await p.goto(BASE + `/experiments/${EXP}/cockpit`, { waitUntil: "networkidle" }); await p.waitForTimeout(1500);
    const t0 = await p.locator('[role="slider"]').getAttribute("aria-valuenow"); await p.waitForTimeout(1500);
    const t1 = await p.locator('[role="slider"]').getAttribute("aria-valuenow");
    record("motion", "no autoplay", t0 === t1, `${t0} -> ${t1}`);
    const d = await p.evaluate(() => getComputedStyle(document.documentElement).getPropertyValue("--dur-base").trim());
    record("motion", "motion tokens are zero", /^0m?s$/.test(d), d);
    await b.close();
  },
  async resilience() { // WebGL off, context lost, unknown mesh source.
    let b = await launch(["--disable-webgl", "--disable-3d-apis"]); let p = await (await b.newContext()).newPage();
    await p.goto(BASE + `/morphology/${MOR_SIX}`, { waitUntil: "networkidle" }); await p.waitForTimeout(800);
    const neurons = await p.locator("main").innerText();
    record("resilience", "WebGL off: message, no claim that the data is the same, details still listed", /3D isn't available/.test(neurons) && !/data below is the same/i.test(neurons) && /Dataset/i.test(neurons));
    await p.goto(BASE + "/scenarios/LOOMING_CIRCUIT_VALIDATION?replay=canonical", { waitUntil: "networkidle" }); await p.waitForTimeout(3000);
    const stage = await p.locator("main").innerText();
    record("resilience", "WebGL off: scenario stage is not blank and the numbers below are available", /3D isn't available/.test(stage) && /data below is the same/i.test(stage));
    await b.close();
    b = await launch(); p = await (await b.newContext()).newPage();
    await p.goto(BASE + `/morphology/${MOR_SIX}`, { waitUntil: "networkidle" }); await p.waitForTimeout(2500);
    await p.evaluate(() => { const c = document.querySelector("canvas"); (c.getContext("webgl2") || c.getContext("webgl")).getExtension("WEBGL_lose_context").loseContext(); });
    await p.waitForTimeout(800);
    record("resilience", "context lost: message", /The 3D view stopped/.test(await p.locator("main").innerText()));
    await p.getByRole("button", { name: "Restart 3D view" }).click(); await p.waitForTimeout(2000);
    record("resilience", "context lost: restart restores the view", (await p.locator("canvas").count()) === 1);
    await b.close();
  },
  async bundle() { // three.js must not load on pages without a 3D view.
    const b = await launch(); const ctx = await b.newContext(); 
    for (const [name, path] of ROUTES.filter(([n]) => NO_3D.includes(n))) {
      const p = await ctx.newPage(); const scripts = [];
      p.on("response", async (r) => { if (r.request().resourceType() === "script") scripts.push(r); });
      await p.goto(BASE + path, { waitUntil: "networkidle" }); await p.waitForTimeout(500);
      let three = false;
      for (const r of scripts) { try { const t = await r.text(); if (/WebGLRenderer|THREE\.REVISION|"REVISION"/.test(t) && t.length > 100000) three = true; } catch { /* ignore */ } }
      record("bundle", `${name} loads no three.js`, !three);
      await p.close();
    }
    await b.close();
  },
};

for (const g of GROUPS) await groups[g]();
fs.mkdirSync(new URL("./reports/", import.meta.url), { recursive: true });
fs.writeFileSync(new URL("./reports/last-run.json", import.meta.url), JSON.stringify({ base: BASE, date: new Date().toISOString(), results }, null, 1));
const failed = results.filter((r) => !r.pass);
console.log(`\n${results.length - failed.length} passed, ${failed.length} failed`);
process.exit(failed.length ? 1 : 0);
