import { PageShell } from "@/components/site/PageShell";
import { StatePanel } from "@/components/ui";

export default function Loading() {
  return (
    <PageShell title="Neurons" current="/morphology">
      <StatePanel state="loading" what="neuron shapes" />
    </PageShell>
  );
}
