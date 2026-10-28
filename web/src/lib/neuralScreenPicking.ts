import { Camera, Matrix4, Vector3, Vector4 } from 'three';

/** Engineering interaction radius in CSS pixels, not anatomical thickness. */
export const NEURAL_PICK_RADIUS_CSS_PX = 6;
export type SegmentPick = { status: 'hit'; point: Vector3; depth: number; pixels: number; index: number } | { status: 'miss' | 'invalid' };

/** Exhaustive segment broad phase: clip outcodes and inflated projected AABBs.
 * No world-radius candidate set can discard a visible screen-space hit.
 * Runs only when R3F requests a raycast; never on simulation ticks or frames.
 */
export function pickNeuralSegments(positions: ArrayLike<number>, world: Matrix4, camera: Camera,
  viewport: { width: number; height: number }, pointer: { x: number; y: number }, radius = NEURAL_PICK_RADIUS_CSS_PX): SegmentPick {
  if (![viewport.width, viewport.height, pointer.x, pointer.y, radius, ...world.elements, ...camera.matrixWorldInverse.elements, ...camera.projectionMatrix.elements].every(Number.isFinite) || viewport.width <= 0 || viewport.height <= 0 || radius <= 0 || positions.length % 6 !== 0 || Math.abs(pointer.x) > 1 || Math.abs(pointer.y) > 1) return { status: 'invalid' };
  const viewWorld = new Matrix4().multiplyMatrices(camera.matrixWorldInverse, world);
  const clipMatrix = new Matrix4().multiplyMatrices(camera.projectionMatrix, viewWorld);
  const a = new Vector4(), b = new Vector4(), q = new Vector4();
  const px = (pointer.x + 1) * viewport.width / 2, py = (pointer.y + 1) * viewport.height / 2;
  let best: SegmentPick = { status: 'miss' };
  for (let i = 0; i < positions.length; i += 6) {
    const ax=positions[i], ay=positions[i+1], az=positions[i+2], bx=positions[i+3], by=positions[i+4], bz=positions[i+5];
    if (![ax,ay,az,bx,by,bz].every(Number.isFinite)) continue;
    a.set(ax,ay,az,1).applyMatrix4(clipMatrix); b.set(bx,by,bz,1).applyMatrix4(clipMatrix);
    // Homogeneous clipping against all six frustum planes, before division by w.
    let lo=0, hi=1;
    for (let plane=0;plane<6;plane++) {
      const axis=plane>>1, sign=plane%2===0 ? 1 : -1;
      const da=a.w+sign*a.getComponent(axis), db=b.w+sign*b.getComponent(axis);
      if (da<0 && db<0) { hi=-1; break; }
      if (da<0) lo=Math.max(lo, da/(da-db));
      else if (db<0) hi=Math.min(hi, da/(da-db));
    }
    if (lo>hi) continue;
    const aw=a.w+(b.w-a.w)*lo, bw=a.w+(b.w-a.w)*hi;
    if (!(aw>0 && bw>0)) continue;
    const x1=((a.x+(b.x-a.x)*lo)/aw+1)*viewport.width/2, y1=((a.y+(b.y-a.y)*lo)/aw+1)*viewport.height/2;
    const x2=((a.x+(b.x-a.x)*hi)/bw+1)*viewport.width/2, y2=((a.y+(b.y-a.y)*hi)/bw+1)*viewport.height/2;
    if (![x1,y1,x2,y2].every(Number.isFinite) || px<Math.min(x1,x2)-radius || px>Math.max(x1,x2)+radius || py<Math.min(y1,y2)-radius || py>Math.max(y1,y2)+radius) continue;
    const dx=x2-x1, dy=y2-y1, length=dx*dx+dy*dy;
    const t=length>0 ? Math.max(0,Math.min(1,((px-x1)*dx+(py-y1)*dy)/length)) : (aw <= bw ? 0 : 1);
    const pixels=Math.hypot(px-x1-t*dx,py-y1-t*dy);
    if (pixels>radius) continue;
    const u=t*aw/((1-t)*bw+t*aw), original=lo+(hi-lo)*u;
    q.set(ax+(bx-ax)*original,ay+(by-ay)*original,az+(bz-az)*original,1).applyMatrix4(viewWorld);
    const depth=-q.z;
    if (!Number.isFinite(depth) || depth<=0 || (best.status==='hit' && depth>=best.depth)) continue;
    const point=new Vector3(ax+(bx-ax)*original,ay+(by-ay)*original,az+(bz-az)*original).applyMatrix4(world);
    best={status:'hit',point,depth,pixels,index:i/3};
  }
  return best;
}
