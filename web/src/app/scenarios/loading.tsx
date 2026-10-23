import { DiscoveryShell, DiscoveryState } from "@/components/discovery/DiscoveryShell";
export default function Loading() {
  return <DiscoveryShell active="scenarios"><header className="discovery-hero"><p className="nf-eyebrow">NeuroFly / Explore</p><h1>Explore the<br /><span>possibilities.</span></h1></header><DiscoveryState kind="loading" title="Loading experiences…"><p>Reading the canonical scenario catalogue. No substitute experiment data are displayed.</p></DiscoveryState></DiscoveryShell>;
}
