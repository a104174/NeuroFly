import { notFound } from "next/navigation";
import { AppHeader } from "@/components/AppHeader";
import { ScenarioCockpit } from "@/components/ScenarioCockpit";
import { StateMessage } from "@/components/StateMessage";
import { requestJson } from "@/lib/neuroflyClient";
import { parseScenarioCatalog, SCENARIO_KINDS } from "@/lib/scenarioPlayback";
import { loadScenarioPlayback } from "@/app/scenarios/actions";

export const dynamic = "force-dynamic";
export default async function ScenarioPage({ params, searchParams }: { params: Promise<{ scenarioId: string }>; searchParams: Promise<{ replay?: string }> }) {
  const { scenarioId } = await params;
  if (!SCENARIO_KINDS.some(id => id === scenarioId)) notFound();
  let definitions;
  try { definitions = await requestJson("/api/v1/scenarios", parseScenarioCatalog); }
  catch (error) { return <div className="app-shell"><AppHeader /><main className="main-content"><StateMessage eyebrow="SCENARIO UNAVAILABLE" title="The preset could not load." detail={error instanceof Error ? error.message : "Backend unavailable."} tone="error" /></main></div>; }
  const scenario = definitions.find(s => s.id === scenarioId);
  if (!scenario) notFound();
  const query = await searchParams;
  const restored = query.replay === "canonical" ? await loadScenarioPlayback(scenario.id) : null;
  return <div className="app-shell"><AppHeader /><ScenarioCockpit scenario={scenario}
    initialResult={restored && "result" in restored ? restored.result : null}
    initialError={restored && "error" in restored ? restored.error : null} /></div>;
}
