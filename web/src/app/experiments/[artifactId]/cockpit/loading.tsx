import { SiteHeader } from "@/components/site/SiteChrome";
import { StatePanel } from "@/components/ui";

export default function ScientificCockpitLoading() {
  return (
    <div className="app-shell cockpit-shell" data-theme-scope="dark">
      <SiteHeader tone="dark" variant="tool" backHref="/experiments" backLabel="Experiments" title="Cockpit" />
      <main id="main-content" tabIndex={-1} className="cockpit-route">
        <StatePanel state="loading" what="the experiment replay" />
      </main>
    </div>
  );
}
