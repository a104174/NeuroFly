import type { Metadata } from "next";
import { SiteHeader } from "@/components/site/SiteChrome";
import { LabScopeNotice } from "@/components/lab/LabScopeNotice";
import { LiveExploreArena } from "@/components/LiveExploreArena";
import "../fly/viewer.css";
import "./lab.css";

export const metadata: Metadata = { title: "Explore · NeuroFly Lab", description: "Step inside the NeuroFly laboratory. Explore simulated movement, inspect the fly model and observe selected model neural influence." };
export default function ArenaPage() {
  return <div className="lab-shell"><SiteHeader tone="dark" variant="tool" backHref="/" backLabel="Home" title="Lab" /><LabScopeNotice /><main id="main-content" tabIndex={-1}>
    <LiveExploreArena />
  </main></div>;
}
