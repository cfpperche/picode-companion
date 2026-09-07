"""Tessellate a supplier STEP, retaining separate solids in native millimetres."""
import sys,json
import numpy as np
from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID,TopAbs_FACE,TopAbs_REVERSED
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopLoc import TopLoc_Location

def read(path):
 r=STEPControl_Reader();r.ReadFile(str(path));r.TransferRoots();shape=r.OneShape()
 BRepMesh_IncrementalMesh(shape,.15,False,.35,True)
 solids=[];exp=TopExp_Explorer(shape,TopAbs_SOLID)
 while exp.More():
  solid=exp.Current(); fexp=TopExp_Explorer(solid,TopAbs_FACE);vv=[];ff=[]
  while fexp.More():
   face=TopoDS.Face(fexp.Current());loc=TopLoc_Location();tri=BRep_Tool.Triangulation_s(face,loc)
   if tri:
    start=len(vv)
    for i in range(1,tri.NbNodes()+1):
     p=tri.Node(i).Transformed(loc.Transformation());vv.append([p.X(),p.Y(),p.Z()])
    for i in range(1,tri.NbTriangles()+1):
     a,b,c=tri.Triangle(i).Get()
     ff.append([start+a-1,start+c-1,start+b-1] if face.Orientation()==TopAbs_REVERSED else [start+a-1,start+b-1,start+c-1])
   fexp.Next()
  if vv:solids.append({'vertices':vv,'faces':ff})
  exp.Next()
 return solids
if __name__=='__main__':
 solids=read(sys.argv[1]);open(sys.argv[2],'w').write(json.dumps(solids,separators=(',',':')))
 bounds=np.array([[np.min(s['vertices'],axis=0),np.max(s['vertices'],axis=0)] for s in solids])
 print(json.dumps({'solids':len(solids),'bounds':[bounds[:,0].min(0).tolist(),bounds[:,1].max(0).tolist()], 'largest':sorted([(round(float(np.prod(b[1]-b[0])),2),i,np.round(b,3).tolist()) for i,b in enumerate(bounds)],reverse=True)[:12]}))
