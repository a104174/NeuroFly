"use client";

/* eslint-disable @next/next/no-img-element -- Optimized static viewport capture; no runtime renderer is mounted. */
import { useState } from "react";

export function LabPreview() {
  const [failed, setFailed] = useState(false);
  return <figure className="nf-lab-media">
    {failed ? <div className="nf-lab-media-fallback"><span>Inside the NeuroFly Lab</span><p>Preview unavailable. The Lab is still ready to explore.</p></div> : <img src="/assets/site/neurofly-lab-preview.webp" width={1294} height={718} loading="lazy" decoding="async" alt="Screenshot of the NeuroFly 3D laboratory: a digital fly standing inside the transparent enclosure on a laboratory bench." ref={image => { if (image?.complete && image.naturalWidth === 0) setFailed(true); }} onError={() => setFailed(true)} />}
    <figcaption><span className="nf-small-dot" aria-hidden="true" /> Actual Lab viewport <span>Static capture</span></figcaption>
  </figure>;
}
