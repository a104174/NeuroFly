import { PageShell } from "@/components/site/PageShell";
import { StatePanel } from "@/components/ui";

export default function Loading() {
  return (
    <PageShell title="Scenarios" current="/scenarios">
      <StatePanel state="loading" what="the scenarios" />
    </PageShell>
  );
}
