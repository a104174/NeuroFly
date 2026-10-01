import Link from "next/link";
import { AppHeader } from "@/components/AppHeader";
import { StateMessage } from "@/components/StateMessage";
import { requestJson } from "@/lib/neuroflyClient";
import { parseScenarioCatalog } from "@/lib/scenarioPlayback";

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
    <p className="scenario-intro">Follow an approaching object through the visual circuit—and discover why a working simulation can still produce a stationary fly.</p>
    <div className="scenario-catalog">{[...scenarios].sort((a,b) => Number(b.id === "LOOMING_CIRCUIT_VALIDATION") - Number(a.id === "LOOMING_CIRCUIT_VALIDATION")).map(s => <Link key={s.id} href={`/scenarios/${s.id}`} className={`scenario-card ${s.id !== "BASELINE_CONTROL" ? "primary-scenario" : "baseline-scenario"}`}>
      <span className="eyebrow">{s.id === "LOOMING_CIRCUIT_VALIDATION" ? "1.4 MS CIRCUIT MICRO-WINDOW · START HERE" : s.id === "LOOMING_WORLD_EXPERIMENT" ? "40 MS EXPLORATORY WORLD EXPERIMENT" : "CONTROL · ZERO STIMULUS"}</span><h2>{s.title}</h2>
      <p>{s.description}</p>
      <div className="card-preview" aria-hidden="true">{s.id !== "BASELINE_CONTROL" ? "OBJECT → VISUAL CIRCUIT → DNp01 → BODY" : "NO STIMULUS · NO COMMAND · STATIONARY"}</div>
      <h3>What you will see</h3><p>{s.id === "LOOMING_CIRCUIT_VALIDATION" ? "One object approaches. Sensory activity changes, but DNp01 remains subthreshold. No genuine motor command occurs; the fly stays still." : s.id === "LOOMING_WORLD_EXPERIMENT" ? "A slower prescribed approach over a separately frozen model-space horizon. Inspect genuine neural, motor and body outputs as produced, including zero output. This is not a biological escape experiment." : "A prominent stationary fly with no object or sensory projection. Nothing is hidden: silence is the intentional scientific control."}</p>
      <p className="scenario-caveat">Canonical model-space presets. No calibrated retinal geometry, biomechanics or escape claim.</p>
      <span className="scenario-card-action">Open scientific playback →</span>
    </Link>)}</div>
    <p className="subtle-note">Three executable presets: control, circuit micro-window and exploratory world experiment. The broader strategic worlds remain future work.</p>
  </main></div>;
}
