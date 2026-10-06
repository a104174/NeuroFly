import type { NeuralPlaybackFrame, NeuralPlaybackResult } from "@/lib/scenarioPlayback";
import { signed } from "./ScientificInstrument";

/** Identity-resolved display of only the six backend active routes.
 * Route widths are uniform: structural counts never encode efficacy. */
export function NeuralMotif({result,frame}:{result:NeuralPlaybackResult;frame:NeuralPlaybackFrame}) {
  const sources=result.sources.map((node,index)=>({node,index,x:node.side==="L" ? 125 : 555,y:150+["HSN","HSE","HSS"].indexOf(node.type)*70}));
  const targets=result.targets.map((node,index)=>({node,index,x:node.side==="L" ? 225 : 455,y:390}));
  return <svg className="neural-motif" viewBox="0 0 680 458" role="img" aria-label="Six HS sources and bilateral DNp15 targets; six active chemical feedforward routes only">
    <text x="125" y="30" textAnchor="middle" className="motif-side">LEFT · L</text><text x="555" y="30" textAnchor="middle" className="motif-side">RIGHT · R</text>
    <text x="125" y="88" textAnchor="middle" className="motif-input">Input {signed(frame.input_descriptor.L,3)}</text><text x="555" y="88" textAnchor="middle" className="motif-input">Input {signed(frame.input_descriptor.R,3)}</text>
    <text x="340" y="115" textAnchor="middle" className="motif-caption">HS source proxies</text>
    {result.provenance.active_routes.map(route=>{
      const source=sources.find(s=>s.node.body_id===route.source_id)!,target=targets.find(t=>t.node.body_id===route.target_id)!;
      return <path key={route.source_id} data-route={`${route.source_id}:${route.target_id}`} d={`M ${source.x} ${source.y+21} L ${target.x} ${target.y-26}`} className="motif-route"/>;
    })}
    {sources.map(({node,index,x,y})=><g key={node.body_id} data-identity={node.body_id} data-state={frame.hs_states[index]===0 ? "neutral" : "response"}>
      <rect x={x-82} y={y-24} width="164" height="60" rx="4"/><text x={x} y={y-7} textAnchor="middle" className="motif-type">{node.type} {node.side}</text><text x={x} y={y+9} textAnchor="middle" className="motif-id">{node.body_id}</text><text x={x} y={y+27} textAnchor="middle" className="motif-value">{signed(frame.hs_states[index],4)}</text>
    </g>)}
    <text x="340" y="338" textAnchor="middle" className="motif-caption">Six chemical feedforward routes</text>
    {targets.map(({node,index,x,y})=><g key={node.body_id} data-identity={node.body_id} data-state={frame.dnp15_states[index]===0 ? "neutral" : "response"}>
      <rect x={x-95} y={y-25} width="190" height="67" rx="4"/><text x={x} y={y-7} textAnchor="middle" className="motif-type">DNp15 {node.side}</text><text x={x} y={y+10} textAnchor="middle" className="motif-id">{node.body_id}</text><text x={x} y={y+30} textAnchor="middle" className="motif-value">{signed(frame.dnp15_states[index],6)}</text>
    </g>)}
    <text x="340" y="450" textAnchor="middle" className="motif-caption">Continuous readout · dnp15_state_eq · no body mapping</text>
  </svg>;
}
