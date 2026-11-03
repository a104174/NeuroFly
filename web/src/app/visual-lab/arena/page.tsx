import type { Metadata } from "next";
import { SiteHeader } from "@/components/site/SiteChrome";
import { LiveExploreArena } from "@/components/LiveExploreArena";
import "../fly/viewer.css";
import "./lab.css";

export const metadata: Metadata = { title: "Explore · NeuroFly Lab", description: "Step inside the NeuroFly laboratory. Explore simulated movement, inspect the digital fly and observe selected model neural influence." };
export default function ArenaPage() {
  return <div className="lab-shell"><SiteHeader variant="tool" backHref="/" backLabel="Home" title="Lab" /><main id="main-content" tabIndex={-1}>
    <LiveExploreArena />
  </main></div>;
}
