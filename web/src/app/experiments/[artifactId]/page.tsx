import Link from "next/link";
import { notFound } from "next/navigation";

import { AppHeader } from "@/components/AppHeader";
import { ExperimentSummaryView } from "@/components/ExperimentSummaryView";
import { PlaybackWorkspace } from "@/components/PlaybackWorkspace";
import { StateMessage } from "@/components/StateMessage";
import { TimelineInspector } from "@/components/TimelineInspector";
import {
  getExperiment,
  getTimeline,
  NeuroflyApiError,
} from "@/lib/neuroflyClient";

export const dynamic = "force-dynamic";

export default async function ExperimentPage({
  params,
}: {
  params: Promise<{ artifactId: string }>;
}) {
  const { artifactId } = await params;
  let data:
    | { summary: Awaited<ReturnType<typeof getExperiment>>; timeline: Awaited<ReturnType<typeof getTimeline>> }
    | null = null;
  let requestError: unknown = null;
  try {
    const [summary, timeline] = await Promise.all([
      getExperiment(artifactId),
      getTimeline(artifactId),
    ]);
    data = { summary, timeline };
  } catch (error) {
    requestError = error;
  }
  if (requestError instanceof NeuroflyApiError && requestError.code === "artifact_not_found") {
    notFound();
  }
  if (requestError || !data) {
    const detail =
      requestError instanceof NeuroflyApiError
        ? requestError.message
        : "The experiment API returned an invalid response.";
    return (
      <div className="app-shell">
        <AppHeader />
        <main className="main-content main-content-wide">
          <Link className="back-link" href="/">
            ← all experiments
          </Link>
          <StateMessage
            eyebrow="TIMELINE UNAVAILABLE"
            title="This experiment could not be read."
            detail={detail}
            tone="error"
          />
        </main>
      </div>
    );
  }
  return (
    <div className="app-shell">
      <AppHeader />
      <main className="main-content main-content-wide">
        <Link className="back-link" href="/">
          ← all experiments
        </Link>
        <Link className="experiment-cockpit-entry" href={`/experiments/${artifactId}/cockpit`}>
          Open Scientific Cockpit ↗
        </Link>
        <ExperimentSummaryView summary={data.summary} />
        <PlaybackWorkspace
          key={data.timeline.artifact_id}
          timeline={data.timeline}
          validationStatus={data.summary.validation_status}
        />
        <TimelineInspector timeline={data.timeline} />
      </main>
    </div>
  );
}
