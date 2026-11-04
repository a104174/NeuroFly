import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { DataSection, DetailSection, ExperimentActions, ExperimentLead, LimitsSection, ResultsSection, SetupSection } from "@/components/experiment/ExperimentDetail";
import detail from "@/components/experiment/ExperimentDetail.module.css";
import { PlaybackWorkspace } from "@/components/PlaybackWorkspace";
import { PageShell } from "@/components/site/PageShell";
import { TimelineInspector } from "@/components/TimelineInspector";
import { ButtonLink, StatePanel } from "@/components/ui";
import { getExperiment, getTimeline, NeuroflyApiError } from "@/lib/neuroflyClient";
import { experimentName } from "@/lib/recordedExperimentPresentation";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Experiment · NeuroFly" };

export default async function ExperimentPage({ params }: { params: Promise<{ artifactId: string }> }) {
  const { artifactId } = await params;
  let data: { summary: Awaited<ReturnType<typeof getExperiment>>; timeline: Awaited<ReturnType<typeof getTimeline>> } | null = null;
  let requestError: unknown = null;
  try {
    const [summary, timeline] = await Promise.all([getExperiment(artifactId), getTimeline(artifactId)]);
    data = { summary, timeline };
  } catch (error) {
    requestError = error;
  }
  if (requestError instanceof NeuroflyApiError && requestError.code === "artifact_not_found") notFound();
  if (requestError || !data) {
    const integrity = requestError instanceof NeuroflyApiError && (requestError.status === 409 || requestError.code === "artifact_integrity_failure");
    return (
      <PageShell title="This experiment could not be read" current="/experiments">
        <StatePanel state={integrity ? "integrity-failure" : "api-down"} actions={<ButtonLink href="/experiments">Back to Experiments</ButtonLink>} />
      </PageShell>
    );
  }
  const { summary, timeline } = data;
  return (
    <PageShell eyebrow="Experiment" title={experimentName(summary.candidate.identifier)} current="/experiments" lead={<ExperimentLead summary={summary} />}>
      <ExperimentActions summary={summary} />
      <DetailSection id="replay" title="Replay">
        <div className={detail.replayFrame} data-theme-scope="dark">
          <PlaybackWorkspace key={timeline.artifact_id} timeline={timeline} validationStatus={summary.validation_status} />
          <TimelineInspector timeline={timeline} />
        </div>
      </DetailSection>
      <SetupSection summary={summary} />
      <ResultsSection summary={summary} />
      <LimitsSection />
      <DataSection summary={summary} />
    </PageShell>
  );
}
