/** Explicit schema routing. Historical v3 numerical paths remain unchanged. */
import {ContinuousNavigationEngine,replayNavigationInChunks,validateNavigation} from './continuousArenaNavigation';
import {generatePair,validatePair,type NavigationSession,type PairArtifact} from './neuralContributionComparison';
import {MovingVisualEngine,replayMoving,validateMoving,generateMovingPair,validateMovingPair,type MovingSession,type MovingPair} from './movingVisualStimuli';
import type {NeuralArtifact} from './neuralLocomotion';
export type ArenaSession=NavigationSession|MovingSession;
export type ArenaPair=PairArtifact|MovingPair;
export const isMovingSession=(value:unknown):value is MovingSession=>(value as MovingSession)?.schema==='moving_visual_stimulus_session_v4';
export const exportArenaSession=(e:ContinuousNavigationEngine)=>e instanceof MovingVisualEngine?e.exportMoving():e.exportNavigation();
export const arenaLog=(e:ContinuousNavigationEngine)=>e instanceof MovingVisualEngine?e.movingLog():e.navigationLog();
export async function replayArenaSession(authority:NeuralArtifact,log:ArenaSession['log']){return log.schema==='moving_visual_stimulus_event_log_v4'?replayMoving(authority,log):replayNavigationInChunks(authority,log);}
export const validateArenaSession=(authority:NeuralArtifact,value:unknown):Promise<ArenaSession>=>isMovingSession(value)?validateMoving(authority,value):validateNavigation(authority,value,true);
export const generateArenaPair=(authority:NeuralArtifact,value:ArenaSession,onProgress:(n:number)=>void=()=>{}):Promise<ArenaPair>=>isMovingSession(value)?generateMovingPair(authority,value,onProgress):generatePair(authority,value,onProgress);
export const validateArenaPair=(authority:NeuralArtifact,value:unknown):Promise<ArenaPair>=>(value as MovingPair)?.schema==='moving_visual_stimulus_comparison_v4'?validateMovingPair(authority,value):validatePair(authority,value);
