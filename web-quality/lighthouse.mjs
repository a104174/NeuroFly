// Lighthouse mobile on the routes with targets in brief section 11. Usage: BASE=... CHROME=... node lighthouse.mjs
import lighthouse from "lighthouse";
import { launch } from "chrome-launcher";
import os from "node:os";
import path from "node:path";
import fs from "node:fs";
import { ROUTES } from "./routes.mjs";
const BASE = process.env.BASE ?? "http://localhost:3000";
const PERF = ["home", "scenarios", "experiments", "science"];
// The browser profile goes to the system temp folder, never into the repository.
const profile = fs.mkdtempSync(path.join(os.tmpdir(), "neurofly-lh-"));
// userDataDir:false stops chrome-launcher choosing its own folder (on WSL it rewrote the path into a Windows-style
// name that became a folder inside the repository); the profile is passed as a plain flag instead.
const chrome = await launch({ chromePath: process.env.CHROME, userDataDir: false, chromeFlags: [`--user-data-dir=${profile}`, "--headless=new", "--no-sandbox"] });
let bad = 0;
for (const [name, path, want] of ROUTES) {
  if (want !== 200) continue;
  const { lhr } = await lighthouse(BASE + path, { port: chrome.port, output: "json", onlyCategories: ["accessibility", "performance"], formFactor: "mobile" });
  const a11y = Math.round(lhr.categories.accessibility.score * 100), perf = Math.round(lhr.categories.performance.score * 100);
  const ok = a11y >= 95 && (!PERF.includes(name) || perf >= 90);
  if (!ok) bad++;
  console.log(ok ? "PASS" : "FAIL", name, `accessibility ${a11y}`, PERF.includes(name) ? `performance ${perf}` : "");
}
await chrome.kill();
fs.rmSync(profile, { recursive: true, force: true });
process.exit(bad ? 1 : 0);
