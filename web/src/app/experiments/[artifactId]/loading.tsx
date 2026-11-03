import { PageShell } from "@/components/site/PageShell";
import { StatePanel } from "@/components/ui";

export default function ExperimentLoading() {
  return (
    <PageShell title="Experiment" current="/experiments">
      <StatePanel state="loading" what="the experiment" />
    </PageShell>
  );
}
