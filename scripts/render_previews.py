"""Render exact committed meshes into static previews. Requires numpy, Pillow and g++.
No browser, display server, GPU, supplier download or mechanical rebuild needed.
SVG files embed lossless PNGs; geometry/shading is computed from the source meshes.
"""
import base64,ctypes,gzip,hashlib,io,json,math,subprocess,tempfile
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'public/assets'
raw=json.loads(gzip.decompress(base64.b64decode((ASSETS/'companion-c04.b64').read_bytes())))
catalog=json.loads((ROOT/'public/catalog.json').read_text())
meshes=[]
for p in raw:
 meshes.append({**p,'vertices':np.frombuffer(base64.b64decode(p['p']),dtype='<i2').reshape(-1,3).astype(float)/100,'normals':np.frombuffer(base64.b64decode(p['v']),dtype='i1').reshape(-1,3).astype(float)/127,'faces':np.frombuffer(base64.b64decode(p['i']),dtype='<u2').reshape(-1,3)})
def view(item):
 if item=='ELE-05':return -1.12,.2
 if item.startswith(('MOT-','MNT-')) or item in ['ELE-01','ELE-02','ELE-07','ELE-08','ELE-09','ELE-10']:return .5,.95
 return .5,.4

def render(ids,target,raster,angles=(.5,.4),width=480,height=320,explode=False):
 yaw,pitch=angles;cy,sy,cp,sp=math.cos(yaw),math.sin(yaw),math.cos(pitch),math.sin(pitch)
 rotation=np.array([[cy,sy,0],[sy*sp,-cy*sp,-cp],[-sy*cp,cy*cp,-sp]])
 eye=np.array([sy*cp,-cy*cp,sp]);light=np.array([-.48,-.7,1.1]);light/=np.linalg.norm(light)
 half=(light+eye);half/=np.linalg.norm(half)
 triangles=[];colors=[]
 for idx in ids:
  m=meshes[idx];v=(m['vertices']+(np.array(m['e']) if explode else 0))@rotation.T;triangles.append(v[m['faces']])
  n=m['normals'][m['faces']].mean(1);length=np.linalg.norm(n,axis=1);n/=np.maximum(length[:,None],1e-9);n[np.dot(n,eye)<0]*=-1
  base=(np.array(m['c'])/255)**2.2
  color=base[None,:]*(.48+.75*np.maximum(0,n@light))[:,None]
  spec=np.maximum(0,n@half)**(12+160*(1-m['r'])**2)
  color+=(.13+.7*m['m'])*spec[:,None]*((1-m['m']*.5)+base*m['m']*.5)
  emit=min(1,m['l']);color=color*(1-emit)+base*1.1*emit
  colors.append(np.uint8(np.clip(color,0,1)**(1/2.2)*255))
 tri=np.concatenate(triangles);lo=tri.min((0,1));hi=tri.max((0,1));center=(hi+lo)/2
 scale=min(width*.78/max(hi[0]-lo[0],.01),height*.76/max(hi[1]-lo[1],.01))
 tri-=center;tri[:,:,:2]*=scale;tri[:,:,0]+=width/2;tri[:,:,1]+=height/2
 tri=np.ascontiguousarray(tri,dtype=np.float32);rgb=np.ascontiguousarray(np.concatenate(colors));out=np.zeros((height,width,4),dtype=np.uint8)
 raster(tri.ctypes.data,rgb.ctypes.data,len(tri),width,height,out.ctypes.data)
 assert np.count_nonzero(out[:,:,3])>10,target
 image=Image.fromarray(out);buf=io.BytesIO();image.save(buf,format='PNG',optimize=True)
 encoded=base64.b64encode(buf.getvalue()).decode()
 target.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><image width="{width}" height="{height}" href="data:image/png;base64,{encoded}"/></svg>\n')
 return len(tri)

if __name__=='__main__':
 folder=ASSETS/'parts';folder.mkdir(exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='picode-previews-') as work:
  library=Path(work)/'raster.so'
  subprocess.run(['g++','-O2','-shared','-fPIC',str(ROOT/'scripts/preview_rasterizer.cpp'),'-o',str(library)],check=True)
  raster=ctypes.CDLL(str(library)).rasterize
  raster.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_void_p];raster.restype=None
  manifest={'geometry_sha256':catalog['geometry_sha256'],'projection':'orthographic','previews':{}}
  for item in catalog['items']:
   if not item['previewIds']:continue
   target=folder/(item['id']+'.svg');count=render(item['previewIds'],target,raster,view(item['id']))
   manifest['previews'][item['id']]={'mesh_ids':item['previewIds'],'triangles':count,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
  all_ids=list(range(len(raw)))
  inside=[i for i,p in enumerate(raw) if p['g'] not in ['shell','bezel','roof','base','deck','keys','shutterrail','shutter','acoustic'] and not(p['g']=='display' and any(s in p['n'] for s in ['vidro','Área ativa','Pixels','Expressão']))]
  for mode,ids in [('exterior',all_ids),('inside',inside),('explode',all_ids)]:
   target=folder/f'assembly-{mode}.svg';render(ids,target,raster,(.59,.33),960,640,explode=mode=='explode')
   manifest['previews']['assembly-'+mode]={'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
  (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print('Rendered 53 part previews and 3 assembly views from the committed geometry.')
