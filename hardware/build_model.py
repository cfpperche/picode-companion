"""PiCode Cyberpunk Rev C. Units: mm. Appearance and packaging study.
Run from this folder with numpy, trimesh, manifold3d, shapely, mapbox_earcut.
Supplier board outlines and proposed clearances are distinct in hardware.json.
"""
from pathlib import Path
import math, json, base64, gzip
import numpy as np
import trimesh as tm
from trimesh.visual.material import PBRMaterial
from geometry import rounded, loft, diff, cylinder, cap_mesh, glyph, contour

ROOT=Path(__file__).resolve().parent
PARTS=[]
GRAPHITE=[48,54,65,255]; ARMOR=[66,75,86,255]; BLACK=[12,16,24,255]
CYAN=[20,240,240,255]; MAGENTA=[247,31,124,255]; METAL=[137,159,176,255]
YELLOW=[250,190,49,255]; PCB=[23,103,91,255]; WHITE=[191,208,216,255]

def add(name,mesh,color=GRAPHITE,group='shell',explode=(0,0,0),metal=0,rough=.45,emit=0):
    PARTS.append(dict(n=name,mesh=mesh,c=color[:3],g=group,e=explode,m=metal,r=rough,l=emit))
    return mesh

def box(size,center):
    m=tm.creation.box(size);m.apply_translation(center);return m

def cyl(r,h,c,axis='z',segments=32):
    m=cylinder(r,h,(0,0,0),segments=segments)
    if axis=='y':m.apply_transform(tm.transformations.rotation_matrix(math.pi/2,[1,0,0]))
    elif axis=='x':m.apply_transform(tm.transformations.rotation_matrix(math.pi/2,[0,1,0]))
    m.apply_translation(c);return m

def ring(ro,ri,h,c,axis='z',segments=36):
    return diff(cyl(ro,h,c,axis,segments),cyl(ri,h+2,c,axis,segments))

def bar(a,b,r=.7):
    a,b=np.array(a),np.array(b);m=cyl(r,np.linalg.norm(b-a),(0,0,0),segments=8)
    m.apply_transform(tm.geometry.align_vectors([0,0,1],b-a));m.apply_translation((a+b)/2);return m

def wire(points,r=.7):return tm.util.concatenate([bar(a,b,r) for a,b in zip(points,points[1:])])

def screw(c,axis='y',group='shell',e=(0,0,0)):
    add('Parafuso',ring(1.85,.7,.8,c,axis,12),METAL,group,e,metal=.8,rough=.3)

def textmesh(text,size,c,axis='y',group='shell',color=WHITE,e=(0,0,0)):
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    from shapely.geometry import Polygon
    rings=[Polygon(p) for p in TextPath((0,0),text,size=size,prop=FontProperties(family='DejaVu Sans')).to_polygons() if len(p)>2]
    geom=None
    for p in rings: geom=p if geom is None else geom.symmetric_difference(p)
    polygons=list(geom.geoms) if hasattr(geom,'geoms') else [geom]
    m=tm.util.concatenate([tm.creation.extrude_polygon(p,.15,engine='earcut') for p in polygons if not p.is_empty])
    m.vertices[:,0]-=m.bounds[:,0].mean()
    if axis=='y':m.vertices=m.vertices[:,[0,2,1]]*[1,-1,1]
    if axis=='x':m.vertices=m.vertices[:,[2,0,1]]
    m.apply_translation(c);add(text,m,color,group,e,rough=.6)

# 128 x 182 mm base, split lid. The vertical 100 mm mic array fits the left wall.
base=diff(rounded(128,182,35,13,3,(0,91,22.5),n=8),rounded(122,176,43,10,2,(0,91,31),n=8),rounded(82,24,14,4,.5,(0,181,25),axis='y',n=6))
add('Base / 128 x 182 mm',base,GRAPHITE,'base')
add('Fundo',rounded(122,176,3,10,1,(0,91,5),n=8),BLACK,'base',(0,0,-22))
for x in [-48,48]:
    for y in [19,164]:add('Pé em elastômero',rounded(13,13,4,4,1,(x,y,2),n=6),BLACK,'base',(0,0,-25))
add('Deck do teclado',rounded(122,61,3,9,1,(0,32,37),n=8),BLACK,'deck',(0,-10,18))
add('Deck traseiro',rounded(120,121,3,9,1,(0,120,39),n=8),ARMOR,'base')
add('Pedestal',rounded(68,69,8,12,2,(0,118,44),n=8),BLACK,'base')
for s in [-1,1]:
    add('Luz de contorno da base',wire([(s*12,0,14),(s*50,0,14),(s*63.9,13,14),(s*63.9,168,14)],.45),CYAN if s<0 else MAGENTA,'base',emit=.92)

# Rounded CRT silhouette, straight enclosure axes to preserve exact millimetres.
head=diff(rounded(120,136,118,16,6,(0,119,116),axis='y',n=8),rounded(114,130,124,13,4,(0,114,116),axis='y',n=8),rounded(76,66,12,6,.3,(0,122,181),n=6))
add('Carcaça do monitor',head,GRAPHITE,'shell',(0,42,20),metal=.22)
# Face plate has actual openings for the display, camera and sensor windows.
face=rounded(115,130,4,13,1,(0,60,116),axis='y',n=8)
face=diff(face,rounded(76,76,12,5,1,(0,59,105),axis='y',n=8),cyl(6,12,(0,60,165),'y'),rounded(12,6,12,1,.3,(41,60,161),axis='y',n=5),cyl(2.2,12,(-40,60,161),'y'))
add('Moldura com aberturas',face,BLACK,'bezel',(0,-33,8),metal=.2)
trim=diff(rounded(110,125,1.0,11,.3,(0,57.8,116),axis='y',n=8),rounded(108,123,5,10,.2,(0,57.8,116),axis='y',n=8))
add('Friso eletroluminescente',trim,CYAN,'bezel',(0,-33,8),emit=.72)
for x in [-50,50]:
    for z in [61,171]:screw((x,57, z),e=(0,-33,8),group='bezel')

# Square 4-inch HDMI C display. Active area is 72.53 mm; board envelope reserved.
add('LCD · vidro 84 x 84',rounded(84,84,2.5,2,.3,(0,64.5,105),axis='y',n=6),BLACK,'display',(0,-55,2),rough=.12)
add('LCD · PCB 79.5 x 77.8',box((79.5,1.6,77.8),(0,69.5,105)),[23,64,117,255],'display',(0,-55,2))
add('Controlador HDMI do display',box((16,2,16),(0,71,105)),BLACK,'display',(0,-55,2))
add('Conector HDMI do display',box((15,12,11),(7,76,130)),METAL,'display',(0,-55,2),metal=.7)
add('USB-C do display',box((9,7,3.5),(28,74,140)),METAL,'display',(0,-55,2),metal=.7)
# Pixel face occupies a real-size active region; geometry is not an LED matrix.
active=72.53
add('Área ativa 72.53 x 72.53',box((active,.15,active),(0,62.95,105)),[5,14,25,255],'display',(0,-55,2))
tiles=[];lit=[];pink=[]
for row in range(24):
    for col in range(24):
        x=(col-11.5)*2.78;z=105+(11.5-row)*2.78
        eye=(5<=col<=8 or 15<=col<=18) and 7<=row<=12
        smile=(row==17 and 9<=col<=14) or (row==16 and col in [8,15])
        accent=(row==14 and col in [5,6,17,18])
        m=box((2.28,.1,2.28),(x,62.8,z))
        (lit if eye or smile else pink if accent else tiles).append(m)
add('Pixels escuros',tm.util.concatenate(tiles),[9,23,36,255],'display',(0,-55,2),emit=.4)
add('Expressão do agente',tm.util.concatenate(lit),CYAN,'display',(0,-55,2),emit=1)
add('Expressão magenta',tm.util.concatenate(pink),MAGENTA,'display',(0,-55,2),emit=.95)

# Camera Module 3 standard: actual 25 x 24 x 11.5 mm envelope, optical axis forward.
add('Camera Module 3 · PCB 25 x 24',box((25,1.2,24),(0,71.4,163)),PCB,'camera',(-26,-20,43))
add('Autofocus IMX708',box((8.5,6.9,8.5),(0,67.35,163)),BLACK,'camera',(-26,-20,43))
add('Lente da câmera',cyl(3.2,3.4,(0,62.2,163),'y'),[21,47,82,255],'camera',(-26,-20,43),metal=.7,rough=.1)
add('Aro da câmera',ring(6,4.2,2,(0,57.3,163),'y'),METAL,'camera',(-26,-20,43),metal=.85,rough=.2)
add('Reflexo lente',cyl(1.05,.15,(-.8,60.4,164),'y',20),[70,132,167,255],'camera',(-26,-20,43),emit=.7)
add('Indicador de câmera',cyl(1.2,.7,(11,57.2,163),'y',16),MAGENTA,'camera',(-26,-20,43),emit=.9)
add('Trilho de obturador',rounded(32,17,1.3,3,.4,(8,57.1,163),axis='y',n=6),ARMOR,'shutterrail',(-26,-20,43),metal=.45)
# Ring and lens must remain visible: rail is behind the shutter, with lens cutout.
PARTS[-1]['mesh']=diff(PARTS[-1]['mesh'],cyl(6.5,8,(0,57.1,163),'y'))
add('Obturador deslizante',rounded(13,14,1.2,2,.3,(18,55.8,163),axis='y',n=6),ARMOR,'shutter',(-26,-20,43),metal=.65)
for z in [159,162,165]:add('Ranhura obturador',box((7,.25,.45),(18,55.1,z)),BLACK,'shutter',(-26,-20,43))

# Front-facing distance and light sensors, physical optical apertures.
add('VL53L1X · portadora 13 x 18',box((13,2,18),(41,64,161)),PCB,'sensors',(32,-10,36))
add('Janela ToF bipartida',rounded(11,5.4,1.5,1,.3,(41,58,161),axis='y',n=5),[37,10,35,255],'sensors',(32,-10,36),rough=.12)
add('Separação óptica ToF',box((1,1.8,5.4),(41,57.9,161)),BLACK,'sensors',(32,-10,36))
add('ALS · reserva 20 x 20',box((20,2,20),(-40,65,161)),PCB,'sensors',(-36,-10,36))
add('Janela de luz ambiente',cyl(2.0,1.3,(-40,58,161),'y',20),[147,164,162,255],'sensors',(-36,-10,36),rough=.2)

# ReSpeaker moved intact to the left wall; original 100 mm diameter and 66 mm pattern.
# MEMS microphones face outward. Other board components face the interior.
mic_e=(-45,0,0)
add('ReSpeaker XVF3800 · Ø100 vertical',cyl(50,1.2,(-54.5,123,116),'x',64),PCB,'mic',mic_e)
add('Processador XMOS',box((2.2,15,15),(-52.8,123,116)),BLACK,'mic',mic_e)
add('USB-C de áudio',rounded(3.5,9,7,1,.3,(-52.1,170.5,116),axis='y',n=5),METAL,'mic',mic_e,metal=.7)
mic_openings=[]
for y in [90,156]:
    for z in [83,149]:
        mic_openings.append(cyl(3.1,15,(-57,y,z),'x',20))
        add('Mic MEMS lateral',box((1.5,3,4),(-55.85,y,z)),METAL,'mic',mic_e,metal=.5)
        add('Duto acústico lateral',ring(3.6,2.3,4.3,(-57.5,y,z),'x',24),BLACK,'mic',mic_e)
        add('Aro discreto de microfone',ring(3.4,2.7,.55,(-60.05,y,z),'x',24),METAL,'mic',mic_e,metal=.5)
        mesh=[]
        for dz in [-1.5,0,1.5]:
            span=math.sqrt(2.65**2-dz**2)
            mesh.append(box((.45,span*2,.35),(-60.15,y,z+dz)))
        add('Tela de microfone',tm.util.concatenate(mesh),[76,86,93,255],'mic',mic_e,metal=.3)
head=diff(head,*mic_openings)

# Embedded rectangular metal grille follows the smooth Rev B enclosure finish.
# It sits on the flat central roof, with a nominal seat and an underside locating rim.
roof=rounded(82,72,1.4,7,.3,(0,122,183.3),n=8)
top_skirt=diff(rounded(78,68,2.8,6.5,.2,(0,122,181.7),n=8),rounded(74,64,6,4.5,.2,(0,122,181.7),n=8))
roof=tm.boolean.union([roof,top_skirt],engine='manifold')
head=diff(head,roof)
PARTS[[p['n'] for p in PARTS].index('Carcaça do monitor')]['mesh']=head
grille_holes=[]
for row in range(17):
    for col in range(21):
        grille_holes.append(cyl(1.05,5,((col-10)*3.5,122+(row-8)*3.5,183.3),segments=12))
add('Grade metálica superior embutida',diff(roof,tm.util.concatenate(grille_holes)),[176,186,190,255],'roof',(0,0,64),metal=.7,rough=.5)

# Top-firing 40 mm speaker, baffle and separate proposed rear chamber.
speaker_e=(0,8,34)
chamber=rounded(78,68,30,6,1,(0,122,165.0),n=8)
chamber=diff(chamber,rounded(74,64,40,4,.5,(0,122,174),n=8))
add('Câmara acústica superior · 78 x 68 x 30',chamber,BLACK,'speaker',speaker_e)
baffle=diff(rounded(74,64,2,4,.4,(0,122,175),n=8),cyl(20,8,(0,122,175),'z',40))
add('Baffle do alto-falante',baffle,ARMOR,'speaker',speaker_e)
add('Ímã de alto-falante',cyl(12,9,(0,122,164)),METAL,'speaker',speaker_e,metal=.7)
add('Cone de 40 mm voltado para cima',cyl(19,4,(0,122,175.8),'z',40),[22,26,33,255],'speaker',speaker_e,rough=.7)
add('Aro de montagem do alto-falante',ring(23,19,1.6,(0,122,177.5),'z',48),METAL,'speaker',speaker_e,metal=.65)

# CM5 + carrier behind display, away from the speaker chamber.
add('CM5-NANO-B · 55 x 41',box((55,41,1.6),(-17,128,67)),PCB,'compute',(-45,24,0))
add('Conectores entre placas',box((48,32,5),(-17,128,71)),BLACK,'compute',(-45,24,0))
add('Compute Module 5 · 55 x 40',box((55,40,1.6),(-17,128,75)),[23,115,66,255],'compute',(-45,24,0))
add('SoC BCM2712',box((16,16,2),(-23,128,77)),METAL,'compute',(-45,24,0),metal=.75)
add('Memória 8 GB',box((12,13,1.5),(1,130,77)),BLACK,'compute',(-45,24,0))
add('Dissipador · reserva 55 x 40 x 12',box((55,40,3),(-17,128,81)),METAL,'compute',(-45,24,0),metal=.8)
for x in np.arange(-42,11,4):add('Aleta térmica',box((1.1,40,9),(x,128,87)),METAL,'compute',(-45,24,0),metal=.75)
fan=diff(box((40,40,10),(-17,128,98)),cyl(17,15,(-17,128,98)))
add('Ventoinha 40 x 40 x 10',fan,BLACK,'compute',(-45,24,0))
add('Rotor de ventoinha',cyl(5,3,(-17,128,98)),ARMOR,'compute',(-45,24,0))
for i in range(7):
    a=i*math.pi*2/7
    add('Pá',bar((-17+5*math.cos(a),128+5*math.sin(a),98),(-17+15*math.cos(a+.5),128+15*math.sin(a+.5),98),2),ARMOR,'compute',(-45,24,0))
for i,col in enumerate([CYAN,MAGENTA,YELLOW]):
    add('Chicote para áudio lateral',wire([(-40+i*2,147,74),(-45.5+i*.6,158,83),(-48.5+i*.5,164,110),(-50+i*.4,168,116)],.65),col,'cables')
add('Ribbon CSI · trajeto proposto',wire([(0,72,170),(0,78,166),(-28,80,163),(-32,82,141),(-32,106,77)],2),[206,164,98,255],'cables')
for i in range(2):add('Par de fios do alto-falante',wire([(10+i*2,136,77),(31+i*2,150,99),(43+i*2,160,147),(41+i*2,151,162),(38,144+i*2,165)],.6),MAGENTA if i==0 else BLACK,'cables')

# Real openings and back I/O panel; connector extensions remain a design task.
vents=[]
for x in range(-38,15,5):vents.append(rounded(2.8,32,8,1,.3,(x,177,112),axis='y',n=4))
PARTS[[p['n'] for p in PARTS].index('Carcaça do monitor')]['mesh']=diff(head,*vents)
add('Fundo de ventilação',box((59,1,37),(-13,173,112)),BLACK,'compute',(-45,24,0))
io=rounded(81,23,2,4,.5,(0,181.8,25),axis='y',n=6)
io=diff(io,rounded(10,4.5,6,1.6,.3,(-24,180,25),axis='y',n=6),rounded(14,6.5,6,1,.3,(-3,180,25),axis='y',n=6))
add('Painel de conexões',io,BLACK,'base')
add('USB-C alimentação',rounded(8.8,3,1,1,.2,(-24,180.8,25),axis='y',n=6),METAL,'ports',metal=.8)
add('USB-A serviço',box((12.3,1,4.5),(-3,181,25)),[46,108,157,255],'ports')
add('Chave física de mute',rounded(12,6,3,1,.3,(25,182,25),axis='y',n=5),YELLOW,'mute')
add('Chave de energia',rounded(7,7,2,1,.3,(48,178.5,152),axis='y',n=5),ARMOR,'shell',(0,42,20))

# Six mechanical controls retain the Ditoo-like layout; keycaps 18.6 mm wide.
for row in range(2):
    for col in range(3):
        x=-36+23*col;y=16+23*row;z=39+row*2
        add('Switch mecânico 14 mm',box((14,14,8),(x,y,z-2)),BLACK,'keys',(0,-15,23))
        add('RGB da tecla',rounded(19.7,19.7,1.1,2,.3,(x,y,z+2),n=5),CYAN if col<2 else MAGENTA,'keys',(0,-15,23),emit=.9)
        cap=cap_mesh();cap.vertices[:,:2]*=1.08;cap.apply_translation([x,y,z+2])
        add('Keycap '+str(row*3+col+1),cap,ARMOR if row==0 else [87,101,116,255],'keys',(0,-15,23),metal=.25)
        g=glyph([['left','-','right'],['m','+','sun']][row][col],z+10.65);g.apply_translation([x,y,0])
        add('Legenda da tecla',g,CYAN if col<2 else MAGENTA,'keys',(0,-15,23),emit=.8)
add('Boot de alavanca',rounded(12,21,3,5,.6,(45,36,43),n=6),BLACK,'keys',(0,-15,23))
add('Haste metálica',cyl(1.7,15,(45,36,52)),METAL,'keys',(0,-15,23),metal=.95,rough=.18)
ball=tm.creation.icosphere(subdivisions=2,radius=4.6);ball.apply_translation([45,36,61]);add('Esfera da alavanca',ball,METAL,'keys',(0,-15,23),metal=.95,rough=.14)
add('Botão de voz',cyl(4.2,3,(45,13,43)),YELLOW,'keys',(0,-15,23),metal=.65)
add('Estado do agente',rounded(37,2,1,1,.3,(0,53,42),n=5),CYAN,'deck',(0,-10,18),emit=.95)

# Cyberpunk armor and visual language; no decorative fictitious sensors.
textmesh('PiCode',7,(0,-.3,24),group='base',color=WHITE)
textmesh('COMPANION / C-01',3.5,(0,57.6,58),group='bezel',color=WHITE,e=(0,-33,8))
for x in [-43,-37,-31,31,37,43]:
    add('Faixa de atenção',wire([(x,58,52),(x+3,58,56)],.65),YELLOW,'bezel',(0,-33,8))
# Smooth satin side panels recall Rev B; cyberpunk accents remain on the face and base.

# Raise the camera 2 mm to retain 1 mm between its PCB and the LCD mount reserve.
for p in PARTS:
    if p['g'] in ['camera','shutterrail','shutter']:p['mesh'].apply_translation([0,0,2])

from interior import revise
revise(globals())
from rotation import revise as add_rotation, verify as verify_rotation
add_rotation(globals())
from unibody import revise as unify_exterior
unify_exterior(globals())
from front_panel import revise as close_front
close_front(globals())
from unibody import verify as verify_unibody
unibody_spec=verify_unibody(next(p['mesh'] for p in PARTS if p['n']=='Base / 160 x 182 mm'),next(p['mesh'] for p in PARTS if p['n']=='Carcaça do monitor'))

def export():
    view=[];scene=tm.Scene()
    for p in PARTS:
        m=tm.graph.smooth_shade(p['mesh'],angle=math.radians(28),facet_minarea=8)
        # Fixed point 0.01 mm for normal assembly, explosion is a separate offset.
        normals=np.clip(np.round(m.vertex_normals*127),-127,127).astype('i1')
        vertices=np.round(m.vertices*100).astype('<i2');faces=m.faces.astype('<u2')
        assert len(m.vertices)<65536
        assert np.max(np.abs(m.vertices*100))<32767, 'Fixed-point overflow'
        q={k:v for k,v in p.items() if k!='mesh'}
        for k,a in [('p',vertices),('v',normals),('i',faces)]:q[k]=base64.b64encode(a.tobytes()).decode()
        view.append(q)
        material=PBRMaterial(name=p['n'],baseColorFactor=p['c']+[255],metallicFactor=p['m'],roughnessFactor=p['r'],emissiveFactor=[c/255*p['l'] for c in p['c']],doubleSided=True)
        m.visual=tm.visual.TextureVisuals(material=material)
        m.vertices=m.vertices[:,[0,2,1]]*[.001,.001,-.001]
        scene.add_geometry(m,node_name=f"{len(view):03d}_{p['n']}")
    data=json.dumps(view,separators=(',',':')).encode();(ROOT/'meshes.json').write_bytes(data)
    (ROOT/'meshes.b64').write_text(base64.b64encode(gzip.compress(data,compresslevel=9,mtime=0)).decode())
    (ROOT/'PiCode_Companion_C04.glb').write_bytes(scene.export(file_type='glb'))
    bounds=np.array([p['mesh'].bounds for p in PARTS]); ext=bounds[:,1].max(axis=0)-bounds[:,0].min(axis=0)
    report={'parts':len(PARTS),'triangles':sum(len(p['mesh'].faces) for p in PARTS),'bounds_mm':np.round(ext,2).tolist(),'compressed_bytes':(ROOT/'meshes.b64').stat().st_size}
    report['groups_mm']={g: np.round([np.min([p['mesh'].bounds[0] for p in PARTS if p['g']==g],axis=0),np.max([p['mesh'].bounds[1] for p in PARTS if p['g']==g],axis=0)],3).tolist() for g in sorted(set(p['g'] for p in PARTS))}
    report['non_watertight_parts']=[p['n'] for p in PARTS if not p['mesh'].is_watertight]
    lid=next(p['mesh'] for p in PARTS if p['n']=='Grade metálica superior embutida')
    shell=next(p['mesh'] for p in PARTS if p['n']=='Carcaça do monitor')
    joined=tm.boolean.union([shell,lid],engine='manifold')
    intersection=tm.boolean.intersection([shell,lid],engine='manifold')
    shared_volume=intersection.volume if len(intersection.faces) else 0.0
    mic_reserve=cyl(50,8.3,(-52.45,123,156),'x',64)
    raised_skirt=top_skirt.copy(); raised_skirt.apply_translation([0,0,40])
    mic_contact=tm.boolean.intersection([raised_skirt,mic_reserve],engine='manifold')
    mic_interference=mic_contact.volume if len(mic_contact.faces) else 0.0
    # Float32 CSG can produce zero-volume slivers at coincident surfaces.
    # Count solid connected components above 0.0001 mm³, retaining raw counts.
    solid_bodies=[m for m in joined.split(only_watertight=False) if abs(m.volume)>0.0001]
    report['top_joint']={
      'revision':'C.04 — rotating head; C.03 top joint translated by 40 mm',
      'skirt_bottom_z_mm':220.3,
      'skirt_inner_opening_mm':[74,64],
      'grille_size_mm':[82,72,1.4],
      'grille_perforations':357,
      'grille_top_z_mm':224.0,
      'lid_watertight':bool(lid.is_watertight),
      'assembled_connected_solids':len(solid_bodies),
      'raw_boolean_components':int(joined.body_count),
      'component_volume_threshold_mm3':0.0001,
      'assembled_watertight':bool(joined.is_watertight),
      'lid_shell_overlap_mm3':float(shared_volume),
      'skirt_microphone_reserve_overlap_mm3':float(mic_interference),
      'fit':'Nominal contact; print tolerances and fasteners not defined.'}
    assert lid.is_watertight and joined.is_watertight and len(solid_bodies)==1
    assert abs(shared_volume)<.01 and abs(mic_interference)<.01
    report['scope']='Computed group bounds and top joint only. Supplier STEP tessellation for ReSpeaker; remaining electronics and proposed mounts are simplified. No complete interference, tolerance, cabling, acoustic or thermal validation.'

    report['rotation']={**rotation_spec,**verify_rotation(PARTS)}
    report['unibody']=unibody_spec
    report['front_panel']=front_panel_spec
    (ROOT/'verificacao.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report))

if __name__=='__main__':export()
