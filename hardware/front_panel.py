"""Center the real-size LCD inside a continuous printed front enclosure."""
import numpy as np
import trimesh as tm


def revise(ctx):
    parts = ctx['PARTS']
    rounded, diff, cyl, box = [ctx[k] for k in ('rounded','diff','cyl','box')]
    shell = next(p for p in parts if p['n'] == 'Carcaça do monitor')
    # Enclosure center: z=151, LCD's previous center: z=145. Move its complete
    # mounting assembly, preserving the actual 84 mm glass / 72.53 mm active area.
    for p in parts:
        if p['g'] == 'display' or (p['g'] == 'mounts' and tuple(p['e']) == (0,-55,2)):
            p['mesh'].apply_translation([0,0,6])
        # Restore clearance above the glass, including the camera's lower bar.
        if p['g'] in ('camera','shutterrail','shutter') or (p['g'] == 'mounts' and tuple(p['e']) == (-26,-20,43)):
            p['mesh'].apply_translation([0,0,3])
        if p['g'] == 'sensors':
            p['mesh'].apply_translation([0,0,6])
        if p['n'] == 'CSI FFC 15-to-22 pin · proposed routing':
            vertices = p['mesh'].vertices.copy()
            vertices[:,2] += 3*np.clip((vertices[:,2]-180)/14,0,1)
            p['mesh'].vertices = vertices

    # Crop the same outer solid used for the head. Its front surface follows
    # the existing bevel exactly, rather than adding an oversized flat bezel.
    outer = rounded(120,146,118,16,6,(0,119,151),axis='y',n=8)
    front = tm.boolean.intersection([outer,box((300,10,300),(0,58.25,151))],engine='manifold')
    aperture = rounded(76,76,16,3,.3,(0,60,151),axis='y',n=8)
    front = diff(front,aperture,cyl(6,16,(0,60,208),'y'),
                 rounded(12,6,16,1,.3,(41,60,207),axis='y',n=5),
                 cyl(2.2,16,(-40,60,207),'y'))
    shell['mesh'] = tm.boolean.union([shell['mesh'],front],engine='manifold')

    # Remove the old screen-sized face panel and its perimeter hardware.
    # The product label remains on the printed lower margin.
    parts[:] = [p for p in parts if p['g'] != 'bezel' or p['n'] == 'COMPANION / C-01']
    for p in parts:
        if p['n'] == 'COMPANION / C-01':
            p['mesh'].apply_translation([0,2.2,0])
            p['g'],p['e'] = 'shell',shell['e']
    trim = diff(rounded(80,80,.8,5,.2,(0,59.8,151),axis='y',n=8),
                rounded(78,78,4,4,.2,(0,59.8,151),axis='y',n=8))
    ctx['add']('LCD perimeter light',trim,ctx['CYAN'],'bezel',shell['e'],emit=.72)
    parts[-1]['j'] = 'head'

    glass = next(p['mesh'] for p in parts if p['n'] == 'LCD · vidro 84 x 84')
    active = next(p['mesh'] for p in parts if p['n'] == 'Área ativa 72.53 x 72.53')
    center = glass.bounds.mean(axis=0)
    assert np.allclose(center[[0,2]],shell['mesh'].bounds.mean(axis=0)[[0,2]],atol=.01)
    assert np.allclose(glass.extents[[0,2]],[84,84])
    assert np.allclose(active.extents[[0,2]],[72.53,72.53])
    # Check the newly moved display and its mounts against the camera assembly.
    display = [p['mesh'] for p in parts if p['g']=='display' or (p['g']=='mounts' and tuple(p['e'])==(0,-55,2))]
    camera = [p['mesh'] for p in parts if p['g']=='camera' or (p['g']=='mounts' and tuple(p['e'])==(-26,-20,43))]
    overlap = 0.0
    for a in display:
        for b in camera:
            if np.all(a.bounds[1]>b.bounds[0]) and np.all(b.bounds[1]>a.bounds[0]):
                m=tm.boolean.intersection([a,b],engine='manifold')
                overlap += abs(m.volume) if len(m.faces) else 0
    assert overlap < .01
    ctx['front_panel_spec'] = {
        'lcd_center_xz_mm':center[[0,2]].tolist(),
        'glass_size_mm':[84,84], 'active_size_mm':[72.53,72.53],
        'front_opening_mm':[76,76], 'side_margin_mm':22,
        'top_bottom_margin_mm':35, 'camera_display_overlap_mm3':overlap,
        'front_integrated_with_shell':True,
        'scope':'Visual enclosure and selected camera/display clearances; production wall thickness, fasteners and tolerances require detailed CAD.'}
