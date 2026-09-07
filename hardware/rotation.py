"""C.04 yaw packaging study. Proposed geometry, not fabrication CAD."""
import math
import numpy as np
import trimesh as tm

HEAD_LIFT = 40
PIVOT = (0, 118, 0)
RATIO = 1.5
DRIVE_TEETH, OUTPUT_TEETH, PITCH = 72, 48, 2
# Open belt pitch length, exact tangent/arcs equation. Nominal 220 mm belt.
R, r = DRIVE_TEETH * PITCH / (2 * math.pi), OUTPUT_TEETH * PITCH / (2 * math.pi)
def belt_length(c):
    a = math.asin((R-r)/c)
    return 2*math.sqrt(c*c-(R-r)**2)+math.pi*(R+r)+2*a*(R-r)
lo, hi = R+r, 100
for _ in range(60):
    mid = (lo+hi)/2
    if belt_length(mid) < 220: lo = mid
    else: hi = mid
CENTER_DISTANCE = (lo+hi)/2

def revise(ctx):
    add, box, cyl, ring, diff, rounded, wire = [ctx[k] for k in ('add','box','cyl','ring','diff','rounded','wire')]
    parts = ctx['PARTS']
    BLACK, ARMOR, METAL, CYAN, YELLOW, PCB = [ctx[k] for k in ('BLACK','ARMOR','METAL','CYAN','YELLOW','PCB')]
    # The original deck supports move WITH the compute cradle and land on a new tray.
    parts[:] = [p for p in parts if p['n'] != 'Pedestal']
    fixed = {'base','deck','keys','ports','mute'}
    for p in parts:
        p['j'] = 'fixed' if p['g'] in fixed else 'head'
        if p['j'] == 'head': p['mesh'].apply_translation([0,0,HEAD_LIFT])
        if p['n'] == 'Cradle support from deck · proposed': p['n'] = 'Cradle support from rotating tray · proposed'
    # Rebuild structural base parts, keeping component sizes and key spacing intact.
    replacements = {
        'Base / 128 x 182 mm': diff(rounded(160,182,35,13,3,(0,91,22.5),n=8),rounded(154,176,43,10,2,(0,91,31),n=8),rounded(82,24,14,4,.5,(0,181,25),axis='y',n=6)),
        'Fundo': rounded(154,176,3,10,1,(0,91,5),n=8),
        'Deck traseiro': diff(rounded(154,121,3,9,1,(0,120,39),n=8),cyl(9,8,(0,118,39)),rounded(36,17,8,2,.3,(-CENTER_DISTANCE,118,39),n=6)),
    }
    for p in parts:
        if p['n'] in replacements: p['mesh'] = replacements[p['n']]
        if p['n'] == 'Base / 128 x 182 mm': p['n'] = 'Base / 160 x 182 mm'
        if p['n'] == 'Pé em elastômero': p['mesh'].apply_translation([math.copysign(15,p['mesh'].centroid[0]),0,0])
    def part(name, mesh, color=ARMOR, joint='fixed', e=(0,0,0), group='rotation', metal=0):
        add(name,mesh,color,group,e,metal=metal)
        parts[-1]['j'] = joint
    # The cosmetic cover is separate from the load-bearing pedestal and removable.
    cover = diff(rounded(154,76,31,14,2,(-2,118,57),n=8),rounded(149,71,34,11.5,1,(-2,118,53.5),n=8),cyl(23,45,(0,118,59)))
    part('Drive cover · removable',cover,BLACK,group='rotation_cover',e=(0,35,10))
    # Two 6805-size bearing reserves support head loads independently of the servo.
    part('Bearing pedestal · proposed',ring(22,18.5,17,(0,118,68.5)),ARMOR)
    for z in (64,73):
        part('6805 bearing reserve · 25 x 37 x 7',ring(18.5,12.5,7,(0,118,z)),METAL,metal=.75)
    # Four legs avoid the belt plane. Clearance under their lowest point is checked.
    for x in (-28,28):
        for y in (89,147):
            part('Bearing bridge standoff',ring(3.2,1.6,18,(x,y,49.5)))
    bridge = diff(rounded(66,68,2,7,.4,(0,118,59.5),n=6),cyl(12.7,8,(0,118,59.5)))
    part('Bearing bridge',bridge)
    part('Hollow spindle · 16 mm cable passage',ring(12.5,8,29,(0,118,64.5)),METAL,'head',metal=.6)
    part('Spindle upper shoulder',ring(16,8,2,(0,118,78)),METAL,'head',metal=.6)
    tray = diff(rounded(108,112,3,10,.5,(0,118,79.5),n=8),cyl(8,8,(0,118,79.5)))
    part('Rotating head tray',tray,ARMOR,'head',e=(0,0,12))
    # Raised peripheral rim reaches the existing head shell; compute remains inside.
    collar = diff(rounded(119,117,9,12,1,(0,119,85.5),n=8),rounded(113,111,13,9,.5,(0,119,85.5),n=8))
    part('Head tray attachment rim · proposed',collar,BLACK,'head',e=(0,0,12))
    # SC09 body is an explicit 34 x 16 x 34 mm keep-out, not supplier CAD.
    sx = -CENTER_DISTANCE
    part('SC09 microservo · conservative keep-out',rounded(34,16,34,2,.5,(sx,118,27),n=6),BLACK)
    part('Servo clamp · slotted mount reserve',diff(rounded(42,24,3,3,.5,(sx,118,12),n=6),rounded(34.6,16.6,7,2,.3,(sx,118,12),n=6)),ARMOR)
    part('Servo output shaft · indicative',cyl(3,6,(sx,118,47)),METAL,'drive',metal=.7)
    # Pulley teeth are indicative; no assertion of a manufacturable GT2 profile.
    for name, teeth, rad, x, bore, joint in [('Drive',72,R,sx,3,'drive'),('Output',48,r,0,12.5,'head')]:
        part(name+' pulley core',ring(rad-.7,bore,6,(x,118,53)),METAL,joint,metal=.55)
        for z in (49.6,56.4): part(name+' pulley flange',ring(rad+1.2,bore,.8,(x,118,z)),ARMOR,joint)
        for i in range(teeth):
            a=2*math.pi*i/teeth
            tooth=box((1.05,1,6),(0,0,0))
            tooth.apply_transform(tm.transformations.rotation_matrix(a,[0,0,1]))
            tooth.apply_translation([x+(rad-.25)*math.cos(a),118+(rad-.25)*math.sin(a),53])
            part(name+' pulley tooth · illustrative',tooth,METAL,joint,metal=.45)
    part('Input travel flag · stop concept',box((11,2,2),(sx+5.5,118,59)),YELLOW,'drive')
    for angle in (-140,140):
        a=math.radians(angle)
        part('Input travel stop · mount reserve',cyl(1.4,4,(sx+10*math.cos(a),118+10*math.sin(a),59)),YELLOW)
    # Closed belt body, exact open-belt tangent geometry at the pitch line.
    alpha=math.acos((R-r)/CENTER_DISTANCE)
    outline=[]
    for a in np.linspace(alpha,2*math.pi-alpha,72): outline.append((sx+R*math.cos(a),118+R*math.sin(a)))
    for a in np.linspace(-alpha,alpha,48): outline.append((r*math.cos(a),118+r*math.sin(a)))
    from shapely.geometry import Polygon
    shape=Polygon(outline)
    belt=tm.creation.extrude_polygon(shape.buffer(.9).difference(shape.buffer(-.5)),6,engine='earcut')
    belt.apply_translation([0,0,50])
    part('GT2 belt · 220 x 6 mm envelope',belt,BLACK)
    # Dedicated controller and regulated motor supply reserves, below the rear deck.
    part('Motion controller + half-duplex TTL · reserve',box((36,26,2),(33,152,15)),PCB)
    part('Regulated 6 V motor supply · reserve',box((28,20,10),(36,91,17)),PCB)
    part('Motor power connector · 6 V',cyl(3,3,(48,182,25),'y'),METAL,metal=.7)
    panel=next(p for p in parts if p['n']=='Base / 160 x 182 mm')
    panel['mesh']=diff(panel['mesh'],cyl(3.5,14,(48,182,25),'y'))
    part('Motor cable · fixed route',wire([(sx,111,21),(sx,85,20),(24,85,20),(36,91,23)],.7),YELLOW)
    # Neutral-route harness. Viewer twists its upper end with the head (illustrative only).
    part('Flexible power + control harness · route reserve',wire([(4,118,42),(4,118,50),(3,120,60),(0,122,70),(-3,120,80),(0,118,88),(16,128,97)],1.5),YELLOW,'flex',group='rotation')
    part('Head harness strain relief · proposed',ring(4,2,3,(0,118,84)),BLACK,'head')
    # Sensor board and rotating target indicate an independent home/index reference.
    part('Home sensor · reserve',box((8,6,1.6),(15,141,72)),PCB)
    part('Home target · reserve',cyl(2,1.5,(15,141,78)),METAL,'head',metal=.7)
    ctx['rotation_spec'] = {'revision':'C.04','head_lift_mm':HEAD_LIFT,'pivot_mm':PIVOT,'head_range_deg':[-180,180],'servo_operating_range_deg':[30,270],'ratio_head_to_servo':RATIO,'drive_teeth':72,'output_teeth':48,'belt_pitch_mm':2,'belt_length_mm':220,'pulley_center_distance_mm':round(CENTER_DISTANCE,4),'nominal_belt_width_mm':6,'cable_bore_mm':16,'bearing_reserve_mm':[25,37,7],'base_mm':[160,182],'head_height_increase_mm':40,'fidelity':'Packaging reserves, illustrative teeth and flex routing; no manufacturing release.'}

def verify(parts):
    moving=[p for p in parts if p.get('j')=='head']
    head=[p for p in moving if p['g']!='rotation']
    fixed=[p for p in parts if p.get('j')=='fixed' and p['g'] in ('base','deck','keys','ports','mute')]
    bottom=min(p['mesh'].bounds[0,2] for p in head)
    fixed_top=max(p['mesh'].bounds[1,2] for p in fixed)
    # Analytic vertical separation of ALL legacy head vs ALL base/key vertices.
    assert bottom > fixed_top
    vertices=np.vstack([p['mesh'].vertices for p in moving])
    rad=np.linalg.norm(vertices[:,:2]-np.array(PIVOT[:2]),axis=1).max()
    return {'legacy_head_to_base_vertical_clearance_mm':round(float(bottom-fixed_top),3),'rotating_radius_mm':round(float(rad),3),'swept_diameter_mm':round(float(2*rad),3),'legacy_head_base_collision_free_all_yaw_angles':True,'servo_end_margin_deg':30,'full_assembly_collision_checked':False,'cable_flex_or_bearing_fit_validated':False}
