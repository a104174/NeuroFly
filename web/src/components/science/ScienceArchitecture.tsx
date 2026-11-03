import { KindGlyph } from "@/components/ui";
import styles from "./Article.module.css";

/**
 * Conceptual sequence only. No anatomical edges, neural traces or live state. The copy is the
 * reviewed text from the evidence table (docs/architecture/product_experience_v10_3b.md).
 */
export function ScienceArchitecture() {
  return <figure className={styles.loop} aria-labelledby="architecture-caption">
    <div className={styles.loopSource} data-claim="structure">
      <span><KindGlyph kind="structural" size={11} /> Biological source</span>
      <p>Selected MaleCNS identities &amp; connections</p>
      <span><span aria-hidden="true">↘</span> Inform the circuit structure</span>
    </div>
    <ol className={styles.stages} aria-label="Conceptual runtime loop">
      <li data-claim="sensory"><span className={styles.stageNumber} aria-hidden="true">01</span><span className={styles.stageKind}><KindGlyph kind="model-assumption" size={11} /> Modelled input</span><h3>Observe</h3><p>Completed pose changes relative to geometric landmarks become signed visual descriptors.</p></li>
      <li data-claim="circuit"><span className={styles.stageNumber} aria-hidden="true">02</span><span className={styles.stageKind}><KindGlyph kind="model-state" size={11} /> Neural model</span><h3>Compute</h3><p>Selected HS and DNp15 proxy states evolve through explicit numerical rules.</p></li>
      <li data-claim="projection"><span className={styles.stageNumber} aria-hidden="true">03</span><span className={styles.stageKind} data-role="engineering">Engineering projection</span><h3>Turn</h3><p>A bounded projection of the neural readout contributes to the heading command.</p></li>
      <li data-claim="navigation"><span className={styles.stageNumber} aria-hidden="true">04</span><span className={styles.stageKind} data-role="engineering">Engineering body</span><h3>Move</h3><p>Forward propulsion and boundary response produce the next accepted body pose.</p></li>
    </ol>
    <p className={styles.loopReturn}><span aria-hidden="true">↶</span><span>New pose. New observation.<small>The next model update uses the completed movement interval.</small></span></p>
    <figcaption id="architecture-caption">Conceptual architecture diagram · Explore ground navigation. Structural evidence informs the model; it is not queried on every update. The 3D renderer displays the state. Rendered pixels do not drive this observer.</figcaption>
  </figure>;
}
