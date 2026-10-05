import Link from "next/link";
import { AppHeader } from "@/components/AppHeader";
import { StateMessage } from "@/components/StateMessage";
import { requestJson } from "@/lib/neuroflyClient";
import { parseScenarioCatalog } from "@/lib/scenarioPlayback";
import { scenarioCopy } from "@/lib/scenarioPresentation";

export const dynamic = "force-dynamic";
export default async function ScenariosPage() {
  let scenarios;
  try { scenarios = await requestJson("/api/v1/scenarios", parseScenarioCatalog); }
  catch (error) { return <div className="app-shell"><AppHeader /><main className="main-content">
    <StateMessage eyebrow="SCENARIO API UNAVAILABLE" title="Scenarios could not load." detail={error instanceof Error ? error.message : "Please check the backend."} tone="error" />
  </main></div>; }
  return <div className="app-shell"><AppHeader /><main className="scenario-route">
    <p className="eyebrow">NEUROFLY / SCIENTIFIC SCENARIOS</p>
    <h1>See the stimulus.<br />Understand the response.</h1>
    <p className="scenario-intro">Explore closed-loop looming experiments and a separate horizontal-motion neural circuit. Backend state, explicit assumptions and honest outcomes.</p>
    <div className="scenario-catalog">{[...scenarios].sort((a,b) => Number(b.id === "LOOMING_CIRCUIT_VALIDATION") - Number(a.id === "LOOMING_CIRCUIT_VALIDATION")).map(s => <Link key={s.id} href={`/scenarios/${s.id}`} className={`scenario-card ${s.id !== "BASELINE_CONTROL" ? "primary-scenario" : "baseline-scenario"}`}>
      <span className="eyebrow">{scenarioCopy[s.id].role}</span><h2>{s.title}</h2>
      <p>{s.description}</p>
      <div className="card-preview" aria-hidden="true">{scenarioCopy[s.id].preview}</div>
      <h3>What you will see</h3><p>{scenarioCopy[s.id].observation}</p>
      <p className="scenario-caveat">{s.scientific_caveat}</p>
      <span className="scenario-card-action">Open scientific playback →</span>
    </Link>)}</div>
    <p className="subtle-note">Four executable presets: control, circuit micro-window, exploratory world experiment and neural-only horizontal motion. Broader strategic worlds remain future work.</p>
  </main></div>;
}
