import {validateProtocolExecution,validateProtocol,assertAppliedSchedule,replayProtocol,type Protocol,type ProtocolStatus} from './visualProtocol';
/** Browser-local inputs only; every open recomputes the pinned v3 model. */
import {ContinuousNavigationEngine,navigationHash} from './continuousArenaNavigation';
import {exportArenaSession,validateArenaSession,replayArenaSession,generateArenaPair,type ArenaSession} from './arenaSessionDispatch';
import type {NeuralArtifact} from './neuralLocomotion';
import {BODY_DT} from './interactiveNeuralLocomotion';
export const LIBRARY_DB='neurofly-experiment-library';
export const LIBRARY_STORE='sessions';
export const LIBRARY_VERSION=1;
type Inputs={log:ArenaSession['log'];config_sha256:string;log_sha256:string;result_sha256:string;artifact_id:string;protocol?:Protocol;protocol_status?:ProtocolStatus};
export type ComparisonReference={schema:'neural_contribution_comparison_v3_1'|'moving_visual_stimulus_comparison_v4'|'independent_visual_stimulus_comparison_v5';parent_session_id:string;config_sha256:string;artifact_id:string};
export type LibraryRecord={schema:'experiment_session_library_v3_2'|'experiment_session_library_v4'|'experiment_session_library_v5'|'experiment_session_library_v5_2';id:string;revision:string;name:string;created_at:string;modified_at:string;source_session_id:string;inputs:Inputs;summary:{duration_s:number;interventions:number;distance:number;status:'RECORDED_PREFIX'|'DURATION_COMPLETED'|'PROTOCOL_COMPLETED'|'OPERATOR_TERMINATED';mode:string};comparison:ComparisonReference|null;record_sha256:string};
export type LibraryEntry={id:string;record:LibraryRecord|null;error:string|null};
const keys=(value:object,names:string)=>{if(Object.keys(value).sort().join(',')!==names.split(',').sort().join(','))throw new Error('Unsupported local record fields');};
const digest=(x:unknown)=>typeof x==='string'&&/^[a-f0-9]{64}$/.test(x);
export function experimentName(value:string){const name=value.trim();if(!name||name.length>100||/[\u0000-\u001f\u007f]/.test(name))throw new Error('Nome obrigatório: 1–100 caracteres legíveis.');return name;}
async function seal(record:Omit<LibraryRecord,'record_sha256'>):Promise<LibraryRecord>{const body={...record} as Partial<LibraryRecord>;delete body.record_sha256;return {...body,record_sha256:await navigationHash(body)} as LibraryRecord;}
export async function inspectRecord(value:unknown):Promise<LibraryRecord>{
 const r=value as LibraryRecord;
 if(!r||typeof r!=='object'||!['experiment_session_library_v3_2','experiment_session_library_v4','experiment_session_library_v5','experiment_session_library_v5_2'].includes(r.schema))throw new Error('Versão de biblioteca não suportada; nenhum dado foi migrado.');
 keys(r,'schema,id,revision,name,created_at,modified_at,source_session_id,inputs,summary,comparison,record_sha256');
 if(typeof r.id!=='string'||! /^[a-f0-9-]{36}$/.test(r.id)||typeof r.revision!=='string'||! /^[a-f0-9-]{36}$/.test(r.revision)||experimentName(r.name)!==r.name||![r.created_at,r.modified_at].every(t=>typeof t==='string'&&Number.isFinite(Date.parse(t))&&new Date(t).toISOString()===t)||r.modified_at<r.created_at||!digest(r.source_session_id))throw new Error('Metadados locais inválidos.');
 keys(r.inputs,r.schema==='experiment_session_library_v5_2'?'log,config_sha256,log_sha256,result_sha256,artifact_id,protocol,protocol_status':'log,config_sha256,log_sha256,result_sha256,artifact_id');keys(r.summary,'duration_s,interventions,distance,status,mode');
 const {record_sha256,...body}=r;
 if(!digest(record_sha256)||await navigationHash(body)!==record_sha256||![r.inputs.config_sha256,r.inputs.log_sha256,r.inputs.result_sha256,r.inputs.artifact_id].every(digest)||await navigationHash(r.inputs.log)!==r.inputs.log_sha256||await navigationHash(r.inputs.log.config)!==r.inputs.config_sha256||await navigationHash({log_sha256:r.inputs.log_sha256,result_sha256:r.inputs.result_sha256})!==r.inputs.artifact_id)throw new Error('Integridade local inválida.');
 if(r.schema==='experiment_session_library_v5_2'){const p=r.inputs.protocol!;const {protocol_id,...body}=p;if(await navigationHash(body)!==protocol_id)throw new Error('Protocol identity mismatch');if(!['PROTOCOL_COMPLETED','OPERATOR_TERMINATED'].includes(String(r.inputs.protocol_status)))throw new Error('Invalid protocol termination');assertAppliedSchedule(p,r.inputs.log as import('./independentVisualStimuli').IndependentLog,r.inputs.protocol_status);if(await navigationHash({protocol_id:p.protocol_id,session_id:r.inputs.artifact_id,status:r.inputs.protocol_status})!==r.source_session_id)throw new Error('Scheduled source identity mismatch');}
 const s=r.summary,l=r.inputs.log;
 if(l.schema!==((r.schema==='experiment_session_library_v5'||r.schema==='experiment_session_library_v5_2')?'independent_visual_stimulus_event_log_v5':r.schema==='experiment_session_library_v4'?'moving_visual_stimulus_event_log_v4':'continuous_arena_navigation_event_log_v3'))throw new Error('Library/session version mismatch');
 if(!Number.isFinite(s.distance)||s.distance<0||s.duration_s!==l.stop_step*BODY_DT||!Number.isInteger(l.stop_step)||l.stop_step<1||l.stop_step>1500||s.interventions!==l.events.length||s.mode!==l.config.mode||s.status!==(r.schema==='experiment_session_library_v5_2'?r.inputs.protocol_status:l.stop_step===1500?'DURATION_COMPLETED':'RECORDED_PREFIX'))throw new Error('Resumo local contraditório.');
 if(r.comparison){keys(r.comparison,'schema,parent_session_id,config_sha256,artifact_id');if(r.comparison.schema!==((r.schema==='experiment_session_library_v5'||r.schema==='experiment_session_library_v5_2')?'independent_visual_stimulus_comparison_v5':r.schema==='experiment_session_library_v4'?'moving_visual_stimulus_comparison_v4':'neural_contribution_comparison_v3_1')||r.comparison.parent_session_id!==r.inputs.artifact_id||!digest(r.comparison.config_sha256)||!digest(r.comparison.artifact_id))throw new Error('Referência de comparação inválida.');}
 return structuredClone(r);
}
const yieldUI=()=>new Promise<void>(resolve=>setTimeout(resolve,0));
export async function createRecord(authority:NeuralArtifact,value:unknown,name:string):Promise<LibraryRecord>{
 const safeName=experimentName(name);await yieldUI();const scheduled=(value as {schema?:string})?.schema==='visual_protocol_execution_v5_2'?await validateProtocolExecution(authority,value):null;const original=await validateArenaSession(authority,scheduled?scheduled.session:value);
 // Imports may carry numerically equivalent cross-runtime output. Preserve that
 // identity as provenance for historical formats, then pin this browser's reconstruction.
 // New scheduled records bind the locally reconstructed execution ID to protocol + result.
 const reconstructed=scheduled?await replayProtocol(authority,scheduled.protocol,original.log.stop_step,scheduled.status==='OPERATOR_TERMINATED'):await replayArenaSession(authority,original.log),session=await exportArenaSession(reconstructed);
 if(session.log.stop_step<1)throw new Error('Execute pelo menos um intervalo antes de guardar.');
 const {schema:unused,telemetry,...plainInputs}=session;void unused;const inputs:Inputs=scheduled?{...plainInputs,protocol:scheduled.protocol,protocol_status:scheduled.status}:plainInputs;
 const now=new Date().toISOString();
 return seal({schema:scheduled?'experiment_session_library_v5_2':session.schema==='independent_visual_stimulus_session_v5'?'experiment_session_library_v5':session.schema==='moving_visual_stimulus_session_v4'?'experiment_session_library_v4':'experiment_session_library_v3_2',id:crypto.randomUUID(),revision:crypto.randomUUID(),name:safeName,created_at:now,modified_at:now,source_session_id:scheduled?await navigationHash({protocol_id:scheduled.protocol.protocol_id,session_id:session.artifact_id,status:scheduled.status}):original.artifact_id,inputs,summary:{duration_s:session.log.stop_step*BODY_DT,interventions:session.log.events.length,distance:telemetry.final_state.distance,status:scheduled?scheduled.status:session.log.stop_step===1500?'DURATION_COMPLETED':'RECORDED_PREFIX',mode:String(session.log.config.mode)},comparison:null});
}
export async function restoreRecord(authority:NeuralArtifact,value:unknown):Promise<{record:LibraryRecord;session:ArenaSession;engine:ContinuousNavigationEngine}>{
 await yieldUI();const record=await inspectRecord(value),engine=record.inputs.protocol?await replayProtocol(authority,await validateProtocol(authority,record.inputs.protocol),record.inputs.log.stop_step,record.inputs.protocol_status==='OPERATOR_TERMINATED'):await replayArenaSession(authority,record.inputs.log),session=await exportArenaSession(engine);
 for(const key of ['config_sha256','log_sha256','result_sha256','artifact_id'] as const)if(session[key]!==record.inputs[key])throw new Error('Reprodução divergiu da identidade científica guardada.');
 if(session.telemetry.final_state.distance!==record.summary.distance)throw new Error('Distância guardada contradiz a reprodução.');
 return {record,session,engine};
}
export async function compareRecord(authority:NeuralArtifact,value:unknown){
 const started=performance.now();
 const {record,session}=await restoreRecord(authority,value),pair=await generateArenaPair(authority,session);
 const reference:ComparisonReference={schema:pair.schema,parent_session_id:session.artifact_id,config_sha256:pair.config_sha256,artifact_id:pair.artifact_id};
 if(record.comparison&&await navigationHash(record.comparison)!==await navigationHash(reference))throw new Error('Comparação reconstruída divergiu da referência guardada.');
 return {pair,elapsed:performance.now()-started,record:await seal({...record,revision:crypto.randomUUID(),modified_at:new Date().toISOString(),comparison:reference})};
}
export async function renameRecord(value:unknown,name:string){const r=await inspectRecord(value);return seal({...r,revision:crypto.randomUUID(),name:experimentName(name),modified_at:new Date().toISOString()});}

/** One store/transaction: the optional comparison is dependent metadata, never an orphan. */
export class ExperimentLibrary {
 constructor(private readonly factory:IDBFactory|undefined=globalThis.indexedDB){}
 private open():Promise<IDBDatabase>{return new Promise((resolve,reject)=>{
  if(!this.factory){reject(new Error('IndexedDB indisponível. Use a exportação JSON.'));return;}
  let blocked=false;let request:IDBOpenDBRequest;try{request=this.factory.open(LIBRARY_DB,LIBRARY_VERSION);}catch(e){reject(e);return;}
  request.onupgradeneeded=()=>{if(!request.result.objectStoreNames.contains(LIBRARY_STORE))request.result.createObjectStore(LIBRARY_STORE,{keyPath:'id'});};
  request.onerror=()=>reject(request.error??new Error('Não foi possível abrir a biblioteca.'));
  request.onblocked=()=>{blocked=true;reject(new Error('Biblioteca bloqueada por outra aba; feche-a e tente novamente.'));};
  request.onsuccess=()=>{const db=request.result;if(blocked){db.close();return;}db.onversionchange=()=>db.close();resolve(db);};
 });}
 private async transaction<T>(mode:IDBTransactionMode,action:(store:IDBObjectStore,set:(v:T)=>void,fail:(e:Error)=>void)=>void):Promise<T>{
  const db=await this.open();return new Promise<T>((resolve,reject)=>{
   let result:T,error:Error|null=null;const tx=db.transaction(LIBRARY_STORE,mode);
   const fail=(e:Error)=>{error=e;tx.abort();};
   tx.oncomplete=()=>{db.close();resolve(result);};tx.onabort=()=>{db.close();reject(error??tx.error??new Error('Transação interrompida; nada foi guardado.'));};tx.onerror=()=>{error??=tx.error;};
   try{action(tx.objectStore(LIBRARY_STORE),v=>{result=v;},fail);}catch(e){fail(e instanceof Error?e:new Error(String(e)));}
  });
 }
 async list():Promise<LibraryEntry[]>{
  const rows=await this.transaction<unknown[]>('readonly',(store,set)=>{const req=store.getAll();req.onsuccess=()=>set(req.result);});
  return Promise.all(rows.map(async(value)=>{const id=String((value as {id?:unknown})?.id??'');try{return {id,record:await inspectRecord(value),error:null};}catch(e){return {id,record:null,error:String(e)};}}));
 }
 async get(id:string){const r=await this.transaction<unknown>('readonly',(store,set)=>{const req=store.get(id);req.onsuccess=()=>set(req.result);});if(!r)throw new Error('Experiência já não existe; atualize a lista.');return inspectRecord(r);}
 async insert(record:LibraryRecord){await inspectRecord(record);await this.transaction<void>('readwrite',(store)=>{store.add(record);});}
 async replace(record:LibraryRecord,previousRevision:string){await inspectRecord(record);await this.transaction<void>('readwrite',(store,_set,fail)=>{const req=store.get(record.id);req.onsuccess=()=>{if(!req.result||req.result.revision!==previousRevision){fail(new Error('Registo alterado noutra aba; atualize antes de guardar.'));return;}store.put(record);};});}
 async remove(id:string,confirmed:boolean,expectedRevision?:string){if(!confirmed)throw new Error('Eliminação exige confirmação explícita.');await this.transaction<void>('readwrite',(store,_set,fail)=>{const req=store.get(id);req.onsuccess=()=>{if(!req.result) {fail(new Error('Registo já eliminado.'));return;}if(expectedRevision&&req.result.revision!==expectedRevision){fail(new Error('Registo alterado noutra aba; confirme novamente após atualizar.'));return;}store.delete(id);};});}
}
