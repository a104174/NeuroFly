/** Click jitter allowance in CSS px; independent of the 6 px geometry picking radius. */
export const NEURAL_CLICK_MOVEMENT_PX = 3;
type Input = {clientX:number;clientY:number;button:number;pointerId?:number;pointerType?:string;isPrimary?:boolean;shiftKey?:boolean;ctrlKey?:boolean;altKey?:boolean;metaKey?:boolean};
const finite=(e:Input)=>Number.isFinite(e.clientX)&&Number.isFinite(e.clientY);
const plain=(e:Input)=>e.button===0&&!e.shiftKey&&!e.ctrlKey&&!e.altKey&&!e.metaKey;
export class NeuralSelectionGesture {
  private active = new Set<number>();
  private gesture: {id:number;x:number;y:number;valid:boolean} | null = null;
  private completed: {id:number;x:number;y:number} | null = null;
  down(e:Input) {
    this.completed=null;
    if(!Number.isSafeInteger(e.pointerId)){this.cancel();return;}
    // Bound transient storage even for malformed/untrusted pointer streams.
    if(this.active.size>=2){this.cancel();return;}
    this.active.add(e.pointerId!);
    if(this.active.size!==1){this.gesture=null;return;}
    this.gesture={id:e.pointerId!,x:e.clientX,y:e.clientY,valid:finite(e)&&plain(e)&&e.isPrimary!==false&&(e.pointerType==='mouse'||e.pointerType==='touch'||e.pointerType==='pen')};
  }
  move(e:Input) {
    const g=this.gesture;
    if(g&&g.id===e.pointerId&&(!finite(e)||Math.hypot(e.clientX-g.x,e.clientY-g.y)>NEURAL_CLICK_MOVEMENT_PX||e.shiftKey||e.ctrlKey||e.altKey||e.metaKey))g.valid=false;
  }
  up(e:Input) {
    this.move(e);
    const g=this.gesture;
    this.completed=g&&g.id===e.pointerId&&g.valid&&plain(e)&&this.active.size===1?{id:g.id,x:e.clientX,y:e.clientY}:null;
    if(e.pointerId!==undefined)this.active.delete(e.pointerId);
    this.gesture=null;
  }
  lost(e:Input) { if(e.pointerId!==undefined&&this.active.has(e.pointerId))this.cancel(); }
  cancel() { this.active.clear();this.gesture=null;this.completed=null; }
  consume(e:Input) {
    const c=this.completed;this.completed=null; // also consumes compatibility/duplicate clicks
    return Boolean(c&&this.active.size===0&&plain(e)&&finite(e)&&(e.pointerId===undefined||e.pointerId===c.id)&&Math.hypot(e.clientX-c.x,e.clientY-c.y)<=NEURAL_CLICK_MOVEMENT_PX);
  }
}
/** Capture listeners observe DOM gestures before OrbitControls/R3F, without capturing or stopping events. */
export function bindNeuralSelectionGesture(canvas:HTMLElement, guard:NeuralSelectionGesture, owner:Window=window) {
  const down=(e:PointerEvent)=>guard.down(e),move=(e:PointerEvent)=>guard.move(e),up=(e:PointerEvent)=>guard.up(e),lost=(e:PointerEvent)=>guard.lost(e),cancel=()=>guard.cancel();
  canvas.addEventListener('pointerdown',down,true);
  owner.addEventListener('pointermove',move,true);owner.addEventListener('pointerup',up,true);
  owner.addEventListener('pointercancel',cancel,true);owner.addEventListener('blur',cancel);
  canvas.addEventListener('lostpointercapture',lost,true);canvas.addEventListener('pointerleave',cancel,true);canvas.addEventListener('wheel',cancel,{capture:true,passive:true});
  return ()=>{
    canvas.removeEventListener('pointerdown',down,true);
    owner.removeEventListener('pointermove',move,true);owner.removeEventListener('pointerup',up,true);
    owner.removeEventListener('pointercancel',cancel,true);owner.removeEventListener('blur',cancel);
    canvas.removeEventListener('lostpointercapture',lost,true);canvas.removeEventListener('pointerleave',cancel,true);canvas.removeEventListener('wheel',cancel,true);guard.cancel();
  };
}
