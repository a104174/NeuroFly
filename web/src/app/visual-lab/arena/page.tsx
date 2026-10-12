import type { Metadata } from "next";
import { AppHeader } from "@/components/AppHeader";
import { ArenaCourseViewer } from "@/components/ArenaCourseViewer";
import "../fly/viewer.css";

export const metadata: Metadata = { title: "Experimental chamber · Visual Lab · NeuroFly", description: "A controlled laboratory presentation prototype. Static presentation with opt-in canonical model orientation replay." };
export default function ArenaPage() {
  return <div className="app-shell"><AppHeader /><main className="fly-viewer-page">
    <div className="fly-viewer-heading"><div><p className="eyebrow">NEUROFLY / VISUAL LAB</p><h1>A controlled setting.</h1><p>Arena estática com replay canónico opcional de orientação.</p></div><span className="fly-viewer-badge">ARENA A+C · v0.2</span></div>
    <ArenaCourseViewer />
  </main></div>;
}
