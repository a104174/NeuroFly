import type { Metadata } from "next";
import { AppHeader } from "@/components/AppHeader";
import { ArenaCourseViewer } from "@/components/ArenaCourseViewer";
import "../fly/viewer.css";

export const metadata: Metadata = { title: "Experimental chamber · Visual Lab · NeuroFly", description: "Controlled arena with canonical replays, precomputed Python locomotion and interactive browser HS/DNp15 model simulation." };
export default function ArenaPage() {
  return <div className="app-shell"><AppHeader /><main className="fly-viewer-page">
    <div className="fly-viewer-heading"><div><p className="eyebrow">NEUROFLY / VISUAL LAB</p><h1>A controlled setting.</h1><p>Arena estática, replays Python e simulação neural interativa no browser.</p></div><span className="fly-viewer-badge">ARENA A+C · v0.2</span></div>
    <ArenaCourseViewer />
  </main></div>;
}
