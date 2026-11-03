import { PageShell } from "@/components/site/PageShell";
import { ScientificPlaybackLoading } from "@/components/ScientificInstrument";

export default function Loading() {
  return (
    <PageShell title="Preparing scenario" current="/scenarios">
      <div className="scenario-route" data-theme-scope="dark"><ScientificPlaybackLoading /></div>
    </PageShell>
  );
}
