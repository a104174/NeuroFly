import type { Metadata } from "next";
import { AppHeader } from "@/components/AppHeader";
import { ArenaCourseViewer } from "@/components/ArenaCourseViewer";
import "../fly/viewer.css";

export const metadata: Metadata = { title: "Experimental chamber · Visual Lab · NeuroFly", description: "A controlled laboratory presentation prototype. Canonical orientation replay and experimental Python kinematic locomotion." };
export default function ArenaPage() {
  return <div className="app-shell"><AppHeader /><main className="fly-viewer-page">
    <div className="fly-viewer-heading"><div><p className="eyebrow">NEUROFLY / VISUAL LAB</p><h1>A controlled setting.</h1><p>Arena estática, replay canónico e locomoção experimental calculada em Python.</p></div><span className="fly-viewer-badge">ARENA A+C · v0.2</span></div>
    <ArenaCourseViewer />
  </main></div>;
}
