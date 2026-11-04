import { notFound } from "next/navigation";
import type { ReactNode } from "react";
import { SCENARIO_KINDS } from "@/lib/scenarioPlayback";

/** An unknown scenario ID is a real 404, decided before the page streams. */
export default async function ScenarioLayout({ children, params }: { children: ReactNode; params: Promise<{ scenarioId: string }> }) {
  const { scenarioId } = await params;
  if (!SCENARIO_KINDS.some((id) => id === scenarioId)) notFound();
  return children;
}
