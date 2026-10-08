import { ScenarioCard } from "@/components/ScenarioCard";
import type { ScenarioDefinition } from "@/lib/scenarioPlayback";

export function ScenarioCards({ scenarios }: { scenarios: ScenarioDefinition[] }) {
  return (
    <div className="scenario-catalog">
      {scenarios.map((scenario, index) => (
        <ScenarioCard key={scenario.id} scenario={scenario} index={index} />
      ))}
    </div>
  );
}
