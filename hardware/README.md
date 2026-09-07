# PiCode Companion — C.03 mechanical visualization

This revision improves the interior and keeps the rounded cyberpunk enclosure, top speaker and four left-side acoustic ports. Units are millimetres. It is **not released for manufacturing**.

## What changed

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
cp hardware/meshes.b64 public/assets/companion-c03.b64
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
2. Attach the compute cradle to the rear deck; confirm connector access and board clearance before fixing the stack.
3. Fit display and camera in their edge supports, then connect CSI and display cables while the front is accessible.
4. Fit the complete microphone board to the left side and check every inlet against its sealing duct.
5. Fit speaker and gasket to the acoustic baffle; connect the amplified output from the audio board.
6. Route and secure cables, then close the body and install the recessed top grille.

Before producing functional STL: resolve the carrier geometry, select the speaker/cooling/light modules, validate all supports and fasteners, perform full interference checks, and test acoustic isolation and temperature on the assembled prototype.
