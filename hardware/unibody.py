"""Continuous exterior volumes for C.04. Concept surfaces, not production CAD."""
import trimesh as tm
from geometry import loft


def revise(ctx):
    parts = ctx['PARTS']
    rounded, diff, cyl, box = [ctx[k] for k in ('rounded', 'diff', 'cyl', 'box')]
    get = lambda name: next(p for p in parts if p['n'] == name)
    union = lambda meshes: tm.boolean.union(meshes, engine='manifold')

    # A single upper skin flows from the keyboard deck into the drive enclosure.
    # Its front begins behind the keys; the belt and bearing reserves stay intact.
    outer = loft([(35,160,124,13),(39,160,122,13),
                  (43,159.5,118,13.5),(49,158,108,14),
                  (58,155,92,14),(67,152,80,14),
                  (71,150,76,14),(72.5,147,73,13)], center=(0,120,0), n=16)
    inner = loft([(32,154,118,10),(37,154,116,10),
                  (41,153.5,112,10.5),(47,152,102,11),
                  (56,149,86,11),(65,146,74,11),
                  (69.5,142,68,10)], center=(0,120,0), n=16)
    cover = diff(outer, inner, cyl(23,80,(0,118,60)))
    deck = rounded(160,182,4,13,1,(0,91,37.5),n=16)
    # Open the deck below the drive and below each mechanical switch.
    holes = [rounded(150,114,12,10,.5,(0,120,38),n=12)]
    for row in range(2):
        for col in range(3):
            holes.append(box((14.5,14.5,12),(-36+23*col,16+23*row,38)))
    deck = diff(deck, *holes)
    base = get('Base / 160 x 182 mm')
    base['mesh'] = union([base['mesh'],get('Fundo')['mesh'],deck,cover])
    base['m'], base['r'] = .22, .45
    remove = {'Fundo','Deck traseiro','Deck do teclado','Drive cover · removable'}

    # The tray becomes the floor of the head, with a continuous rounded skirt.
    # Keep its 16 mm cable opening and the original upper shell apertures.
    # Use the original shell's axial bevel and corner construction, extending
    # its bottom by 10 mm. This matches the upper sidewalls without a ledge.
    lower_outer = rounded(120,146,118,16,6,(0,119,151),axis='y',n=8)
    lower_inner = rounded(114,140,124,13,4,(0,114,151),axis='y',n=8)
    lower = diff(lower_outer,lower_inner,cyl(8,20,(0,118,79)),
                 box((300,300,300),(0,119,254.05)))
    shell = get('Carcaça do monitor')
    upper = diff(shell['mesh'],box((300,300,210),(0,119,-1)))
    shell['mesh'] = union([upper,lower])
    remove.update({'Rotating head tray','Head tray attachment rim · proposed'})
    parts[:] = [p for p in parts if p['n'] not in remove]
    ctx['unibody_spec'] = verify(base['mesh'],shell['mesh'])


def verify(base, head):
    result = {}
    for name, mesh in [('base',base),('head_with_platform',head)]:
        bodies = [m for m in mesh.split(only_watertight=False) if abs(m.volume) > .0001]
        assert mesh.is_watertight and len(bodies) == 1, name
        result[name] = {'watertight':bool(mesh.is_watertight),'connected_solids':len(bodies)}
    gap = float(head.bounds[0,2]-base.bounds[1,2])
    assert gap > 0
    result['exterior_vertical_clearance_all_yaw_mm'] = round(gap,3)
    result['scope'] = 'Continuous exterior skins and yaw separation only; service access, print tolerances and internal fits remain preliminary.'
    return result
