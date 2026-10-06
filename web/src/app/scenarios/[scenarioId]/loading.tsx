import { AppHeader } from "@/components/AppHeader";
import { ScientificPlaybackLoading } from "@/components/ScientificInstrument";
import Link from "next/link";

export default function Loading() {
  return <div className="app-shell"><AppHeader/><main className="scenario-route"><Link className="back-link" href="/scenarios">← All experiments</Link><header className="scenario-heading"><div><p className="eyebrow">SCIENTIFIC EXPERIMENT</p><h1>Preparing experiment</h1></div></header><ScientificPlaybackLoading/></main></div>;
}
