import { chromium } from "playwright";
import AxeBuilder from "@axe-core/playwright";
// Run against an API started WITHOUT NEUROFLY_MORPHOLOGY_ARTIFACT_ROOT (like production today).
import { EXP, MOR_SIX as SIX } from "./routes.mjs";
const B = process.env.BASE ?? "http://localhost:3000";
const b=await chromium.launch({executablePath:process.env.CHROME || undefined,args:["--use-angle=swiftshader","--enable-unsafe-swiftshader"]});
let bad=0; const ok=(n,p,x="")=>{ if(!p) bad++; console.log(p?"PASS":"FAIL",n,x); };
for (const [name,path] of [["Neurons list","/morphology"],["Neurons detail",`/morphology/${SIX}`],["Cockpit",`/experiments/${EXP}/cockpit`]]) for (const theme of ["light","dark"]) for (const w of [390,1440]) {
  const p=await (await b.newContext({viewport:{width:w,height:900},colorScheme:theme})).newPage();
  const r=await p.goto(B+path,{waitUntil:"networkidle"}); await p.waitForTimeout(1500);
  const t=await p.locator("main").innerText();
  const axe=(await new AxeBuilder({page:p}).withTags(["wcag2a","wcag2aa","wcag21aa","wcag22aa"]).analyze()).violations.filter(v=>["serious","critical"].includes(v.impact));
  const msg=/not available on this deployment/.test(t), old=/isn.t responding/.test(t);
  const hs=await p.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+1);
  const phoneCockpit = name==="Cockpit" && w===390;
  ok(`${name} ${theme} ${w}`, r.status()===200 && (msg || phoneCockpit) && !old && axe.length===0 && !hs, `status=${r.status()} message=${msg} oldMessage=${old} axe=${axe.length} overflow=${hs}`);
  await p.context().close();
}
const p=await (await b.newContext()).newPage(); await p.goto(B+`/experiments/${EXP}/cockpit`,{waitUntil:"networkidle"}); await p.waitForTimeout(2500);
const t=await p.locator("main").innerText();
ok("Cockpit: playback still works", await p.locator('[role=slider]').count()===1 && /Replay of a completed run/.test(t) && /Experiment playback and stored telemetry remain available/.test(t));
await b.close(); process.exit(bad?1:0);
