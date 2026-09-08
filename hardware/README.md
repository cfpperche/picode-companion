# PiCode Companion — C.04 mechanical visualization

This revision improves the interior and keeps the rounded cyberpunk enclosure, top speaker and four left-side acoustic ports. Units are millimetres. It is **not released for manufacturing**.

## C.04 rotating head

See [ROTATING_HEAD.md](ROTATING_HEAD.md) for the yaw mechanism, component BOM,
power and control changes, load assumptions, assembly and validation limits.
The original C.03 head moves intact on a bearing-supported tray. The base now
measures 160 mm wide; the overall neutral height is 224 mm.

## C.03 interior retained

- ReSpeaker simplified disc replaced with 580 native-scale solids tessellated from the manufacturer's STEP, including the optional XIAO in that file. Materials are illustrative. The variant has not been frozen for purchasing.
- Separate inter-board connector reserves replace the solid block between CM5 and carrier.
- Removable compute cradle with deck supports, camera edge saddle, display retaining clips and microphone edge clips. These are proposed mounts, not verified production parts.
- Flat tapered CSI ribbon, USB audio route and speaker pair routed from the audio board. Connector engagement, routing lengths and bend radii are not validated.
- Generic top speaker now has a conical diaphragm, basket, surround, magnet and gasket inside a separate chamber. The commercial driver is still unselected.
- Viewer can isolate a selected subsystem; interior mode makes the acoustic chamber and screen transparent.

## Evidence and limits

`components.json` records the source, fidelity and unresolved dimensions of each module. Only the ReSpeaker uses imported supplier CAD in this revision. Camera, display, CM5/carrier, sensors and cooling are simplified packing geometry. Do not infer a verified connector layout or mounting pattern from these approximations.

The supplier [ReSpeaker STEP](https://files.seeedstudio.com/wiki/respeaker_xvf3800_usb/3d/respeaker_mic_array_xvf3800_1_with-xiao-0820.stp) and [2D drawing](https://files.seeedstudio.com/wiki/respeaker_xvf3800_usb/respeaker_xvf3800_2d_mechanical_drawing.pdf) differ in revision details. Confirm the purchased variant and optical acoustic-port registration. The STEP is tessellated at 0.15 mm linear deflection, without scaling; electronics meshes are visualization assets, not printable components.

`verificacao.json` contains computed group bounds, non-watertight mesh names and the top-joint boolean check. The shell/grille union remains one connected watertight solid with no positive-volume overlap. This verifies the nominal top joint only. It does not establish complete collision freedom, print tolerances, acoustic performance or cooling.

## Rebuild

Python dependencies: numpy, trimesh, manifold3d, shapely, mapbox_earcut, matplotlib.

```sh
python hardware/prepare_supplier.py  # first build; requires cadquery-ocp
python hardware/build_model.py
cp hardware/meshes.b64 public/assets/companion-c04.b64
python scripts/build_locales.py
```

The first command downloads and verifies the pinned supplier STEP, so network access is required once. The prepared intermediate is intentionally excluded from Git.

The generator reads `respeaker-native.json.gz.b64`, a compressed intermediate made from the supplier STEP. It outputs the viewer mesh, a GLB in metres with Y up, and geometry verification. Regenerating that intermediate additionally needs cadquery-ocp 8.0.1.0.0:

```sh
python hardware/import_step.py supplier.stp native.json
```

Compress the resulting JSON with gzip and base64 to `respeaker-native.json.gz.b64`. `respeaker-transform.json` gives the rigid placement in the enclosure. Supplier geometry remains subject to its owner's terms; no new license is asserted for it.

## Proposed assembly order

1. Assemble and verify the CM5/carrier stack on the bench. Confirm underside connectors against the actual board.
2. Attach the compute cradle to the rotating tray; confirm connector access and board clearance before fixing the stack.
3. Fit display and camera in their edge supports, then connect CSI and display cables while the front is accessible.
4. Fit the complete microphone board to the left side and check every inlet against its sealing duct.
5. Fit speaker and gasket to the acoustic baffle; connect the amplified output from the audio board.
6. Follow the C.04 rotating-head assembly steps before routing the flex harness and closing the covers.

Before producing functional STL: resolve the carrier geometry, select the speaker/cooling/light modules, validate all supports and fasteners, perform full interference checks, and test acoustic isolation and temperature on the assembled prototype.

## Continuous exterior

`unibody.py` runs after the interior and rotation revisions. It replaces stacked base surfaces with one continuous skin and integrates the head tray into the rounded head shell. See `ROTATING_HEAD.md` and the `unibody` section of `verificacao.json` for verification and limits.

## Centered display and printed front

`front_panel.py` centers the unchanged 84 × 84 mm LCD glass on the head's
120 × 146 mm front (x=0, z=151 mm). Its 72.53 mm active area remains at native
scale. A 76 × 76 mm opening leaves 22 mm lateral margins and 35 mm upper/lower
margins, filled by a front panel integrated with the printed shell. The camera
and sensor openings remain functional. The camera and its cradle move 3 mm up,
the sensors move 6 mm up, and the LCD and its supports move 6 mm up. The CSI
route's upper end follows the camera. The old full-face black bezel is removed;
the accent light now outlines only the display. The lower front is closed.

The build verifies LCD dimensions/centering, one connected watertight head shell,
and zero positive-volume interference between the moved display and camera
assemblies. This does not release print-ready CAD or validate all internal parts.
