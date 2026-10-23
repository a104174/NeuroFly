import type { Metadata } from "next";
import Link from "next/link";
import { BrandLogo } from "@/components/site/BrandLogo";
import { ContinuousNavigationArena } from "@/components/ContinuousNavigationArena";
import "../fly/viewer.css";
import "./lab.css";

export const metadata: Metadata = { title: "Explore · NeuroFly Lab", description: "Step inside the NeuroFly laboratory. Explore simulated movement, inspect the digital fly and observe selected model neural influence." };
export default function ArenaPage() {
  return <div className="lab-shell"><a className="lab-skip" href="#lab-main">Skip to laboratory</a><header className="lab-header"><Link prefetch={false} className="lab-brand" href="/" aria-label="NeuroFly home"><BrandLogo /><span>NeuroFly <small>Lab</small></span></Link><nav aria-label="Laboratory navigation"><Link prefetch={false} href="/">Home <span aria-hidden="true">↗</span></Link><Link prefetch={false} href="/scenarios">Research archive</Link></nav></header><main id="lab-main" tabIndex={-1}>
    <ContinuousNavigationArena presentation="explore" />
  </main></div>;
}
