import { DiscoveryShell, DiscoveryState } from "@/components/discovery/DiscoveryShell";
export default function Loading() {
  return <DiscoveryShell active="experiments"><header className="discovery-hero discovery-hero--records"><p className="nf-eyebrow">NeuroFly / Recorded experiments</p><h1>Return to<br /><span>the evidence.</span></h1></header><DiscoveryState kind="loading" title="Loading recorded experiments…"><p>Reading completed artifacts from the configured scientific API.</p></DiscoveryState></DiscoveryShell>;
}
