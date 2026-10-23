import type { Metadata } from "next";
import { DiscoveryShell, DiscoveryState } from "@/components/discovery/DiscoveryShell";
import { ScenarioDiscovery } from "@/components/discovery/ScenarioDiscovery";
import { listScenarios } from "@/lib/scenarioCatalog";
import { ActionLink } from "@/components/site/SitePrimitives";

export const metadata: Metadata = { title: "Explore · NeuroFly", description: "Enter the interactive laboratory or inspect five controlled NeuroFly model experiments and their canonical replays." };
// Five executable presets remain API-owned; presentation never starts a model.
export const dynamic = "force-dynamic";
export default async function ScenariosPage() {
  let scenarios;
  let error: string | null = null;
  try { scenarios = await listScenarios(); }
  catch (cause) { error = cause instanceof Error ? cause.message : "Please check the backend."; }
  return <DiscoveryShell active="scenarios">
    <header className="discovery-hero"><p className="nf-eyebrow">NeuroFly / Explore</p><h1>Explore the<br /><span>possibilities.</span></h1><p>Step into the laboratory. Follow a visual signal. Inspect a recorded response. Choose the question that draws you in.</p></header>
    {scenarios ? <ScenarioDiscovery scenarios={scenarios} /> : <DiscoveryState kind="error" title="Scenarios could not load."><p>SCENARIO API UNAVAILABLE</p><p>{error}</p><p>The catalogue is unavailable; no substitute scenarios are displayed.</p><ActionLink href="/visual-lab/arena">Enter the Lab</ActionLink></DiscoveryState>}
  </DiscoveryShell>;
}
