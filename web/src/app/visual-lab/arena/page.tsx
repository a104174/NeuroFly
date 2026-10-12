import type { Metadata } from "next";
import { AppHeader } from "@/components/AppHeader";
import { FlyViewer } from "@/components/FlyViewer";
import "../fly/viewer.css";

export const metadata: Metadata = { title: "Experimental chamber · Visual Lab · NeuroFly", description: "A controlled laboratory presentation prototype. No scientific simulation." };
export default function ArenaPage() {
  return <div className="app-shell"><AppHeader /><main className="fly-viewer-page">
    <div className="fly-viewer-heading"><div><p className="eyebrow">NEUROFLY / VISUAL LAB</p><h1>A controlled setting.</h1><p>An experimental chamber study. Static specimen, presentation only.</p></div><span className="fly-viewer-badge">ARENA A+C · v0.1</span></div>
    <FlyViewer arena />
  </main></div>;
}
