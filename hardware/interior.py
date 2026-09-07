"""C.03 interior. Supplier geometry and proposed mechanical parts stay distinct."""
import json, math
import numpy as np
import trimesh as tm

def revise(ctx):
 globals().update(ctx)
 def remove(*names):
  PARTS[:]=[p for p in PARTS if p['n'] not in names]
 def named(n):return next(p for p in PARTS if p['n']==n)
 ce=(-45,24,0); came=(-26,-20,43)
 # Replace the impossible solid block with two narrow connector envelopes.
 remove('Conectores entre placas','Fundo de ventilação')
 for x in [-38,4]:
  add('Board-to-board connector · indicative',box((3,26,5),(x,128,71)),BLACK,'compute',ce)
  for y in np.arange(116,141,1):
   add('Board connector contacts · indicative',box((3.2,.25,2.8),(x,y,71)),[184,144,66,255],'compute',ce,metal=.7)
 # Board mounting holes and a removable tray, supported from the base deck.
 # These mount locations are proposed; no unverified supplier hole pattern is asserted.
 tray=diff(rounded(63,49,2,3,.3,(-17,128,58),n=5),rounded(47,32,6,2,.2,(-17,128,58),n=5))
 add('Compute cradle · proposed',tray,ARMOR,'mounts',ce)
 for x in [-45.5,11.5]:
  for y in [108,148]:
   add('Cradle support from deck · proposed',ring(2.5,1.25,17,(x,y,49.5)),ARMOR,'mounts',ce)
   add('Cradle screw · proposed M2',cyl(1,9,(x,y,56)),METAL,'mounts',ce,metal=.7)
   add('Cradle screw head',ring(2,.75,1.3,(x,y,59.6)),METAL,'mounts',ce,metal=.7)
 # Edge saddles avoid pretending to know the carrier's hole coordinates.
 for x in [-45.4,11.4]:
  add('Carrier edge saddle · proposed',box((1.8,30,8),(x,128,63)),ARMOR,'mounts',ce)
 # Connector blocks are explicit packing reserves, not a fabricated exact carrier CAD.
 for name,size,c in [
  ('RJ45 keep-out · position provisional',(16,21,13.5),(-29,130,58.45)),
  ('USB-A keep-out · position provisional',(14,17,7),(0,129,61.7)),
  ('Mini-HDMI keep-out · position provisional',(11,8,4),(-26,110,63.2)),
  ('USB-C keep-out · position provisional',(9,7,3.2),(-9,110,63.6))]:
  # Board underside; connector insertion/cable exits remain unresolved.
  add(name,box(size,c),METAL,'compute',ce,metal=.7)
  opening=np.array(size)*[.76,.1,.6]
  add(name+' aperture',box(opening,(c[0],c[1]-size[1]/2-.01,c[2])),BLACK,'compute',ce)
 add('CSI 22-pin connector reserve',box((13,3,2),(-32,109,77)),WHITE,'compute',ce)
 for i in range(22):add('CSI contacts',box((.2,2,.15),(-37.25+i*.5,108.5,78.1)),METAL,'compute',ce,metal=.5)
 # Flat FFC swept along a route with sampled rounded bends. Width tapers 16 -> 11.5 mm.
 remove('Ribbon CSI · trajeto proposto')
 def ribbon(points,widths,thickness=.18):
  verts=[]
  for i,(p,w) in enumerate(zip(points,widths)):
   p=np.array(p);t=np.array(points[min(i+1,len(points)-1)])-np.array(points[max(0,i-1)])
   side=np.array([1.,0,0]);normal=np.cross(side,t);normal/=np.linalg.norm(normal)
   for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]:verts.append(p+side*w/2*a+normal*thickness/2*b)
  faces=[]
  for i in range(len(points)-1):
   for j in range(4):
    a=4*i+j;b=4*i+(j+1)%4;c=b+4;d=a+4;faces.extend([[a,b,c],[a,c,d]])
  faces.extend([[0,2,1],[0,3,2]])
  k=4*(len(points)-1);faces.extend([[k,k+1,k+2],[k,k+2,k+3]])
  m=tm.Trimesh(verts,faces,process=True);m.fix_normals();return m
 pts=[(0,73.5,155),(0,78,154),(0,81,151),(-2,83,146),(-7,84,138),(-17,85,119),(-27,88,96),(-32,94,83),(-32,102,79),(-32,109,78)]
 add('CSI FFC 15-to-22 pin · proposed routing',ribbon(pts,np.linspace(16,11.5,len(pts))),[214,165,77,255],'cables')
 add('Camera FFC latch · indicative',box((17,2,3),(0,73,155)),BLACK,'camera',came)
 # Camera cradle captures PCB edges, staying clear of unconfirmed hole coordinates.
 for x in [-13.7,13.7]:
  add('Camera edge cradle · proposed',box((2,7,25),(x,68.5,165)),ARMOR,'mounts',came)
 add('Camera cradle crossbar · proposed',box((29.4,3,2),(0,63.5,152)),ARMOR,'mounts',came)
 # Display carrier, clips and serviceable bezel attachment.
 for x in [-44.5,44.5]:
  add('LCD edge carrier · proposed',box((3,12,90),(x,69,105)),ARMOR,'mounts',(0,-55,2))
  for z in [66,144]:
   add('LCD retaining clip · proposed',box((8,2,5),(x-2*np.sign(x),73,z)),YELLOW,'mounts',(0,-55,2))
   screw((x,74.5,z),group='mounts',e=(0,-55,2))
 # Replace the flat speaker disc with an actual conical diaphragm and open basket.
 remove('Cone de 40 mm voltado para cima')
 profile=np.array([[0,172.4],[5,172.4],[6,171.4],[17.5,176.8],[19,177],[19,177.5],[17.5,177.3],[6,172],[5,173],[0,173]])
 cone=tm.creation.revolve(profile,sections=48);cone.apply_translation([0,122,0])
 add('Speaker diaphragm · generic Ø40 reserve',cone,[35,38,43,255],'speaker',speaker_e,rough=.85)
 for a in np.linspace(0,2*math.pi,6,endpoint=False):
  add('Speaker basket · generic reserve',bar((12*math.cos(a),122+12*math.sin(a),168.5),(21*math.cos(a),122+21*math.sin(a),176.5),1.1),METAL,'speaker',speaker_e,metal=.6)
 add('Speaker compliant surround · generic',ring(20,17.5,.8,(0,122,177.8)),BLACK,'speaker',speaker_e)
 add('Speaker sealing gasket · proposed',ring(24,20,1,(0,122,174)),[85,87,90,255],'speaker',speaker_e)
 for x in [-29,29]:
  for y in [99,145]:
   add('Acoustic chamber mounting post · proposed',ring(2.8,1.2,8,(x,y,171)),ARMOR,'speaker',speaker_e)
   screw((x,y,178),axis='z',group='speaker',e=speaker_e)
 # USB audio cable with molded ends; the speaker pair originates at the audio board.
 remove('Chicote para áudio lateral','Par de fios do alto-falante')
 add('USB audio · proposed routing',wire([(-51.5,123,169),(-44,123,172),(-43,161,145),(-39,165,96),(-4,154,81),(0,145,62)],1.6),BLACK,'cables')
 for i in range(2):
  add('Amplified speaker pair · route reserve',wire([(-48,79+i*2,131),(-43,82+i*2,141),(-41,152+i*2,146),(-40,156+i*2,162),(-30,153+i*2,170),(-19,135+i*2,169)],.55),MAGENTA if i==0 else BLACK,'cables')
 for z in [66,166]:
  add('Microphone edge clip · proposed',box((3,12,3),(-53.2,123,z)),ARMOR,'mounts',mic_e)
 # Hide the bottom of the acoustic chamber only in inspection mode, keeping its real geometry.
 named('Câmara acústica superior · 78 x 68 x 30')['g']='acoustic'
 # Use supplier STEP-derived mesh when available, preserving native scale (never shrink to fit).
 path=ROOT/'respeaker-native.json.gz.b64'
 if not path.exists():
  raise FileNotFoundError('Run python hardware/prepare_supplier.py before building')
 if path.exists():
  import gzip,base64
  native=json.loads(gzip.decompress(base64.b64decode(path.read_text())))
  # Transformation is defined after inspecting the source coordinates.
  transform=json.loads((ROOT/'respeaker-transform.json').read_text())
  remove('ReSpeaker XVF3800 · Ø100 vertical','Processador XMOS','USB-C de áudio','Mic MEMS lateral')
  for i,s in enumerate(native):
   m=tm.Trimesh(s['vertices'],s['faces'],process=True);m.apply_transform(np.array(transform['matrix']))
   # Manufacturer solid geometry; finish is illustrative.
   ext=m.extents;color=PCB if max(ext)>80 else (METAL if max(ext)>7 and min(ext)<4 else BLACK)
   add('ReSpeaker supplier CAD · solid '+str(i),m,color,'mic',mic_e,metal=.35 if color==METAL else 0)
