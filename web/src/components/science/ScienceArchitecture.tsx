/** Conceptual sequence only. No anatomical edges, neural traces or live state. */
export function ScienceArchitecture() {
  return <figure className="science-loop" aria-labelledby="architecture-caption">
    <div className="science-loop-source" data-claim="structure">
      <span className="science-evidence-label">Biological source</span>
      <p>Selected MaleCNS identities &amp; connections</p>
      <span className="science-source-direction"><span aria-hidden="true">↘</span> Inform the circuit structure</span>
    </div>
    <ol className="science-loop-stages" aria-label="Conceptual runtime loop">
      <li data-claim="sensory"><span className="science-stage-number" aria-hidden="true">01</span><span className="science-stage-kind">Modelled input</span><h3>Observe</h3><p>Completed pose changes relative to geometric landmarks become signed visual descriptors.</p><span className="science-stage-arrow" aria-hidden="true">→</span></li>
      <li data-claim="circuit"><span className="science-stage-number" aria-hidden="true">02</span><span className="science-stage-kind">Neural model</span><h3>Compute</h3><p>Selected HS and DNp15 proxy states evolve through explicit numerical rules.</p><span className="science-stage-arrow" aria-hidden="true">→</span></li>
      <li data-claim="projection"><span className="science-stage-number" aria-hidden="true">03</span><span className="science-stage-kind science-stage-kind--engineering">Engineering projection</span><h3>Turn</h3><p>A bounded projection of the neural readout contributes to the heading command.</p><span className="science-stage-arrow" aria-hidden="true">→</span></li>
      <li data-claim="navigation"><span className="science-stage-number" aria-hidden="true">04</span><span className="science-stage-kind science-stage-kind--engineering">Engineering body</span><h3>Move</h3><p>Forward propulsion and boundary response produce the next accepted body pose.</p></li>
    </ol>
    <p className="science-loop-return"><span aria-hidden="true">↶</span><span>New pose. New observation.<small>The next model update uses the completed movement interval.</small></span><span className="science-return-line" aria-hidden="true" /></p>
    <figcaption id="architecture-caption">Conceptual architecture diagram · Explore ground navigation. Structural evidence informs the model; it is not queried on every update. The 3D renderer displays the state. Rendered pixels do not drive this observer.</figcaption>
  </figure>;
}
