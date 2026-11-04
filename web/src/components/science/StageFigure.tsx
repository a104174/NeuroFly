/* eslint-disable @next/next/no-img-element -- Pre-encoded WebP assets; no image service is needed for these static figures. */
import styles from "./Article.module.css";

/** A static render on a dark stage. The stage stays dark in both themes (brief question 3). */
export function StageFigure({ kind, caption }: { kind: "specimen" | "lab"; caption: React.ReactNode }) {
  return (
    <figure className={styles.figure} data-theme-scope="dark">
      {kind === "specimen" ? (
        <img
          src="/assets/site/fly-specimen.webp"
          srcSet="/assets/site/fly-specimen-small.webp 768w, /assets/site/fly-specimen.webp 1500w"
          sizes="(max-width: 800px) 92vw, 640px"
          width={1500}
          height={1400}
          loading="lazy"
          decoding="async"
          alt="Three-quarter render of NeuroFly's 3D male fruit fly model, showing its eyes, translucent wings and six legs."
        />
      ) : (
        <img
          src="/assets/site/neurofly-lab-preview.webp"
          width={1294}
          height={718}
          loading="lazy"
          decoding="async"
          alt="Screenshot of the NeuroFly 3D laboratory: a fruit fly model standing inside the transparent enclosure on a laboratory bench."
        />
      )}
      <figcaption>{caption}</figcaption>
    </figure>
  );
}
