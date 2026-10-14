"use client";
import { useState } from "react";
import { comparisonDelta } from "@/lib/neuralSteeringComparison";
import type { ArenaComparisonProps } from "./ArenaComparison";
export function NeuralComparisonInspector({states,overview,time}:ArenaComparisonProps) {
  const [against,setAgainst]=useState("C");
  const b=states[0], other=states.find(s=>s.key===against)!;
  const delta=comparisonDelta(b.scene,other.scene);
  return <section className="neural-comparison" aria-label="Synchronized comparison inspector">
    <div className="comparison-legend">{states.map(s=><span key={s.key} style={{borderColor:s.color}}><b style={{color:s.color}}>{s.symbol} {s.key}</b> {s.label}</span>)}</div>
    <p className="arena-replay-note">Um relógio · {time.toFixed(2)} s · trilhos mostram o percurso já registado até este tempo. Um único fly em foco; símbolos e setas representam as outras poses.</p>
    <details><summary>Comparar poses e intervenção</summary>
      <div className="comparison-table-scroll"><table><thead><tr><th>Condição</th><th>X / Z (unidades)</th><th>Heading (rad)</th><th>Drive neural (yaw_drive_eq)</th><th>Velocidade / propulsão</th><th>Distância</th><th>Contacto</th></tr></thead><tbody>
        {states.map(s=><tr key={s.key} data-comparison-condition={s.key} data-comparison-position={JSON.stringify(s.scene.pose.anchor)} data-comparison-heading={s.scene.pose.rotation} data-comparison-contact={s.scene.frame.contact??"NONE"}>
          <th>{s.symbol} {s.key}</th><td>{s.scene.pose.anchor[0].toFixed(5)} / {s.scene.pose.anchor[2].toFixed(5)}</td><td>{s.scene.pose.rotation.toFixed(5)}</td><td>{s.scene.frame.neural_summary?.mean_yaw_drive_eq?.toExponential(5)??"Indisponível (sem intervalo seguinte)"}</td><td>{s.scene.speed.toFixed(2)} / {s.scene.frame.propulsion_model_value.toFixed(2)}</td><td>{s.scene.distance.toFixed(5)}</td><td>{s.scene.frame.contact??"Nenhum"}</td>
        </tr>)}
      </tbody></table></div>
      <p>B/C: mesmos landmarks Z=+0.4; C mantém a computação neural e desliga apenas a contribuição para steering. D: steering ativo, landmarks Z=−0.4. Marcadores visuais X={overview.landmarkX.join(" / ")}; propulsão idêntica: {b.scene.frame.propulsion_model_value.toFixed(2)} unidades/s · ENGINEERING_PROPULSION.</p>
      <label htmlFor="comparison-against">Diferença atual B − </label><select id="comparison-against" value={against} onChange={e=>setAgainst(e.target.value)}><option>C</option><option>D</option></select>
      <p data-current-separation={delta.separation}>Heading: {delta.signedHeading.toFixed(5)} rad (diferença assinada, wrapped em ±π) · separação das posições: {delta.separation.toFixed(5)} unidades · diferença de distância percorrida: {delta.traveledDifference.toFixed(5)} unidades.</p>
      <details><summary>Máximos do registo completo e contactos</summary>{overview.maxima.map(m=><p key={m.pair}>{m.pair}: |diferença de heading unwrapped| máxima {m.heading.value.toFixed(5)} rad em {m.heading.time.toFixed(2)} s; separação X/Z máxima {m.separation.value.toFixed(5)} unidades em {m.separation.time.toFixed(2)} s.</p>)}{overview.tracks.map(t=><p key={t.key}>{t.key}: {t.contacts.map(c=>`${c.wall} em ${c.time.toFixed(2)} s`).join(", ")||"sem contacto"}. Translação pára; heading neural continua conforme o registo.</p>)}</details>
      <p className="arena-science-limit">CONNECTOME_INFORMED_NEURAL_STEERING · PRECOMPUTED_PYTHON_SIMULATION_REPLAY. Readouts de modelo, não firing rates medidos. A comparação inspeciona evidência existente; não constitui nova evidência biológica, gait, músculos ou exploração autónoma.</p>
    </details>
  </section>;
}
