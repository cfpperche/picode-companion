import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'hardware'))
import build_model as b
from rotation import CENTER_DISTANCE
import numpy as np
import trimesh as tm
parts=b.PARTS
# New rigid rotating transmission parts against fixed drivetrain. Existing head
# clearances have already been checked analytically over the whole yaw interval.
fixed=[p for p in parts if p.get('j')=='fixed' and p['g'] in ['rotation','rotation_cover'] and 'belt' not in p['n'] and 'Home' not in p['n']]
moving=[p for p in parts if p.get('j') in ['drive','head'] and p['g']=='rotation' and 'tooth' not in p['n']]
issues=[];checks=0
for angle in [-180,-90,0,90,180]:
 for p in moving:
  mesh=p['mesh'].copy();drive=p['j']=='drive'
  mesh.apply_transform(tm.transformations.rotation_matrix(np.deg2rad(angle/(1.5 if drive else 1)),[0,0,1],point=[-CENTER_DISTANCE if drive else 0,118,0]))
  for q in fixed:
   if np.any(np.minimum(mesh.bounds[1],q['mesh'].bounds[1])-np.maximum(mesh.bounds[0],q['mesh'].bounds[0])<=0.001):continue
   checks+=1
   m=tm.boolean.intersection([mesh,q['mesh']],engine='manifold')
   vol=abs(m.volume) if len(m.faces) else 0
   if vol>.01: issues.append([angle,p['n'],q['n'],round(float(vol),3)])
print({'boolean_pairs':checks,'issues':issues})
assert not issues
