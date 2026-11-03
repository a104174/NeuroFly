import { PageShell } from "@/components/site/PageShell";
import { StatePanel } from "@/components/ui";

export default function Loading() {
  return (
    <PageShell title="Experiments" current="/experiments">
      <StatePanel state="loading" what="the experiments" />
    </PageShell>
  );
}
