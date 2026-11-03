import type { Metadata } from "next";
import { SiteHeader } from "@/components/site/SiteChrome";
import { LabScopeNotice } from "@/components/lab/LabScopeNotice";
import { FlyViewer } from "@/components/FlyViewer";
import "./viewer.css";

export const metadata: Metadata = { title: "Fly · Visual Lab · NeuroFly", description: "Interactive inspection of the NeuroFly male Drosophila visual asset. No scientific simulation." };
export default function FlyViewerPage() {
  return <div className="app-shell"><SiteHeader tone="dark" /><LabScopeNotice /><main id="main-content" tabIndex={-1} className="fly-viewer-page">
    <div className="fly-viewer-heading"><div><p className="eyebrow">NEUROFLY / VISUAL LAB</p><h1>A closer look.</h1><p>Explore the male Drosophila visual specimen.</p></div><span className="fly-viewer-badge">ASSET PREVIEW · V2-F</span></div>
    <FlyViewer />
  </main></div>;
}
