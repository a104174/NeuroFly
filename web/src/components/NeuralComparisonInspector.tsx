"use client";
import { useState } from "react";
import { displayText } from "@/lib/frozenText";
import { comparisonDelta } from "@/lib/neuralSteeringComparison";
import type { ArenaComparisonProps } from "./ArenaComparison";
export function NeuralComparisonInspector({states,overview,time}:ArenaComparisonProps) {
  const [against,setAgainst]=useState("C");
  const b=states[0], other=states.find(s=>s.key===against)!;
  const delta=comparisonDelta(b.scene,other.scene);
  return <section className="neural-comparison" aria-label="Synchronized comparison inspector">
    <div className="comparison-legend">{states.map(s=><span key={s.key} style={{borderColor:s.color}}><b style={{color:s.color}}>{s.symbol} {s.key}</b> {displayText(s.label)}</span>)}</div>
    <p className="arena-replay-note">One clock · {time.toFixed(2)} s · trails show the path recorded up to this time. A single fly in focus; symbols and arrows represent the other poses.</p>
    <details><summary>Compare poses and intervention</summary>
      <div className="comparison-table-scroll"><table><thead><tr><th>Condition</th><th>X / Z (units)</th><th>Heading (rad)</th><th>Drive neural (yaw_drive_eq)</th><th>Speed / propulsion</th><th>Distance</th><th>Contacto</th></tr></thead><tbody>
        {states.map(s=><tr key={s.key} data-comparison-condition={s.key} data-comparison-position={JSON.stringify(s.scene.pose.anchor)} data-comparison-heading={s.scene.pose.rotation} data-comparison-contact={s.scene.frame.contact??"NONE"}>
          <th>{s.symbol} {s.key}</th><td>{s.scene.pose.anchor[0].toFixed(5)} / {s.scene.pose.anchor[2].toFixed(5)}</td><td>{s.scene.pose.rotation.toFixed(5)}</td><td>{s.scene.frame.neural_summary?.mean_yaw_drive_eq?.toExponential(5)??"Unavailable (no next interval)"}</td><td>{s.scene.speed.toFixed(2)} / {s.scene.frame.propulsion_model_value.toFixed(2)}</td><td>{s.scene.distance.toFixed(5)}</td><td>{s.scene.frame.contact??"None"}</td>
        </tr>)}
      </tbody></table></div>
      <p>B/C: mesmos landmarks Z=+0.4; C keeps the neural computation and switches off only the contribution to steering. D: steering on, landmarks Z=−0.4. Visual markers X={overview.landmarkX.join(" / ")}; identical propulsion: {b.scene.frame.propulsion_model_value.toFixed(2)} units/s · ENGINEERING_PROPULSION.</p>
      <label htmlFor="comparison-against">Current difference B − </label><select id="comparison-against" value={against} onChange={e=>setAgainst(e.target.value)}><option>C</option><option>D</option></select>
      <p data-current-separation={delta.separation}>Heading: {delta.signedHeading.toFixed(5)} rad (signed difference, wrapped to ±π) · position separation: {delta.separation.toFixed(5)} units · difference in distance travelled: {delta.traveledDifference.toFixed(5)} units.</p>
      <details><summary>Maxima over the full record, and contacts</summary>{overview.maxima.map(m=><p key={m.pair}>{m.pair}: maximum |unwrapped heading difference| {m.heading.value.toFixed(5)} rad em {m.heading.time.toFixed(2)} s; maximum X/Z separation {m.separation.value.toFixed(5)} units at {m.separation.time.toFixed(2)} s.</p>)}{overview.tracks.map(t=><p key={t.key}>{t.key}: {t.contacts.map(c=>`${c.wall} em ${c.time.toFixed(2)} s`).join(", ")||"no contact"}. Translation stops; heading and neural activity continue as recorded.</p>)}</details>
      <p className="arena-science-limit">CONNECTOME_INFORMED_NEURAL_STEERING · PRECOMPUTED_PYTHON_SIMULATION_REPLAY. Model readouts, not measured firing rates. The comparison inspects existing evidence; and is not new biological evidence, gait, muscles or autonomous exploration.</p>
    </details>
  </section>;
}
