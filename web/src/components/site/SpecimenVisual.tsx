"use client";

/* eslint-disable @next/next/no-img-element -- Pre-encoded responsive WebP sizes avoid an image-optimizer service for this static render. */
import { useState } from "react";
import Link from "next/link";

/** Static render of the approved V2-F asset; no GLB, WebGL or simulation imports. */
export function SpecimenVisual({ variant }: { variant: "hero" | "chamber" }) {
  const [failed, setFailed] = useState(false);
  return <figure className={`nf-specimen nf-specimen--${variant}`}>
    <div className="nf-specimen-orbit" aria-hidden="true" />
    {variant === "chamber" ? <div className="nf-chamber-frame" aria-hidden="true"><span /><span /><span /></div> : null}
    <div className="nf-specimen-heading"><span className="nf-card-label">{variant === "hero" ? "The digital specimen" : "An environment to explore"}</span><span className="nf-specimen-cross" aria-hidden="true">+</span></div>
    {failed ? <div className="nf-image-fallback"><p>A closer look awaits.</p><Link prefetch={false} href="/visual-lab/fly">Open the digital specimen <span aria-hidden="true">↗</span></Link></div> : <img ref={image => { if (image?.complete && image.naturalWidth === 0) setFailed(true); }} className="nf-specimen-image" src="/assets/site/fly-specimen.webp" srcSet="/assets/site/fly-specimen-small.webp 768w, /assets/site/fly-specimen.webp 1500w" width={1500} height={1400} alt={variant === "hero" ? "Three-quarter render of NeuroFly’s digital male fruit fly, showing its eyes, translucent wings and six legs." : "The digital fly presented above an illustrative laboratory floor."} sizes={variant === "hero" ? "(max-width: 800px) 92vw, 52vw" : "(max-width: 800px) 88vw, 42vw"} fetchPriority={variant === "hero" ? "high" : "auto"} loading={variant === "hero" ? "eager" : "lazy"} decoding="async" onError={() => setFailed(true)} />}
    <figcaption><span><i>Drosophila melanogaster</i><small>{variant === "hero" ? "Artistic 3D model · male specimen" : "Static illustration · enter the Lab to interact"}</small></span><span className="nf-caption-line" aria-hidden="true" /></figcaption>
  </figure>;
}
