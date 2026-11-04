import type { Metadata } from "next";
import Link from "next/link";
import { SiteHeader } from "@/components/site/SiteChrome";
import { LabScopeNotice } from "@/components/lab/LabScopeNotice";
import { BestOnLargerScreen } from "@/components/lab/BestOnLargerScreen";
import { ArenaCourseViewer } from "@/components/ArenaCourseViewer";
import "../../fly/viewer.css";

export const metadata: Metadata = { title: "Laboratory research tools · NeuroFly" };
/** Retains the complete historical interface outside the primary Lab experience. */
export default function LaboratoryResearchPage() {
  return <div className="app-shell"><SiteHeader tone="dark" /><LabScopeNotice tool="research" /><main id="main-content" tabIndex={-1} className="fly-viewer-page"><div className="fly-viewer-heading"><div><p className="eyebrow">NEUROFLY / RESEARCH</p><h1>Laboratory research tools.</h1><p>Historical modes, controlled experiments and integrity-checked replays.</p><Link href="/visual-lab/arena">← Return to Explore</Link></div></div><BestOnLargerScreen><ArenaCourseViewer /></BestOnLargerScreen></main></div>;
}
