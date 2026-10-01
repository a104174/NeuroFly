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
    <h1>Observe a causal world.</h1>
    <p className="scenario-intro">Choose a canonical control or circuit-validation world. Backend scientific state drives every frame; playback never invents a response.</p>
    <div className="scenario-catalog">{scenarios.map(s => <Link key={s.id} href={`/scenarios/${s.id}`} className="scenario-card">
      <span className="eyebrow">AVAILABLE · CANONICAL PRESET</span><h2>{s.title}</h2>
      <p>{s.description}</p><p className="scenario-caveat">{s.scientific_caveat}</p>
      <span className="scenario-card-action">Open scientific playback →</span>
    </Link>)}</div>
    <p className="subtle-note">These are the two executable presets. The broader strategic worlds remain future work.</p>
  </main></div>;
}
