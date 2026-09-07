# C.04 — rotating head / cabeça giratória

Status: mechanical packaging and interactive motion study. The website simulates
movement; it does not drive a motor. No functional firmware, electrical schematic
or print-ready production CAD is released by this revision.

## Design decision

Keep the keyboard, rear connectors and base stationary. Rotate the complete head:
display, camera, microphones, top speaker, CM5/carrier, cooling and their mounting
cradles. The cradle supports now sit on a rotating tray, not on the fixed deck.
This keeps HDMI, CSI and USB audio connections inside one rigid assembly.

| Item | C.04 proposal |
|---|---|
| Head yaw, relative to front | −180° to +180°; 360° total travel, not unlimited turns |
| Actuator candidate | Waveshare SC09 positional serial-bus microservo |
| Transmission | Open GT2 belt, 72-tooth input / 48-tooth output; 1.5× angular travel |
| Servo operating interval | 30°–270°, centered at 150°; ±120° about center |
| Catalog servo range | 300° positional mode; leave 30° margin at both ends |
| Nominal belt | 220 mm pitch length, 2 mm pitch, 6 mm width |
| Nominal center distance | 49.4082 mm; tension adjustment and belt SKU still required |
| Structural support | Two 6805-size bearing reserves, 25 × 37 × 7 mm |
| Cable passage | 16 mm bore through the spindle; flex harness and strain relief reserves |
| Base shell | 160 × 182 mm; +32 mm width, original depth retained |
| Head lift | +40 mm; original head envelope and electronics scale retained |
| Neutral overall W × H × D | 160 × 224 × 183.95 mm, rounded to 160 × 224 × 184 in UI |
| Swept head diameter | Approximately 165.4 mm; provisionally reserve 180 mm free diameter |

The servo body uses a conservative **34 × 16 × 34 mm keep-out**. It is not a
supplier dimensional drawing. Shaft location, mounting ears and horn are
illustrative. Pulley teeth are visible but are not manufacturing GT2 profiles.
Bearings, controller, supply and cable harness are packaging reserves.

### Why this transmission

A standard positional servo advertised as 180° normally offers 180° total, not
180° each way. A continuous-rotation RC servo normally controls speed rather
than absolute position. SC09's positional range plus the 3:2 transmission
provides the requested head range without operating at the servo endpoints.

For an open belt (same rotation direction), with angles in degrees:

`head = 1.5 × (servo − 150)`

`servo = 150 + head / 1.5`

| Head | Servo |
|---:|---:|
| −180° | 30° |
| −90° | 90° |
| 0° | 150° |
| +90° | 210° |
| +180° | 270° |

Do not use modulo 360 or a shortest-path operation. +180° and −180° look alike,
but have different servo and cable states: move back through zero to get from
one to the other. An input-side flag and stop reserves illustrate an independent
travel limit; an output-only stop cannot distinguish both ends of a full turn.
Stop clearances and their attachments remain to be detailed and bench tested.

## Mechanical load and torque

The bearings and pedestal carry axial weight, overturning moments and belt load;
the servo only actuates yaw. Bearing shoulders, fits, axial retention, bridge
fasteners, belt preload and fatigue life still need engineering drawings.
The cover is removable and is not a bearing support.

The 1.5× speed/travel increase reduces torque:

`T_head = efficiency × T_servo / 1.5`

SC09 is advertised at 2.3 kg·cm at 6 V. Treat this as a peak/stall figure, **not
a continuous working torque**. Ideal head peak would be 1.53 kg·cm; an assumed
80% transmission efficiency gives roughly 1.23 kg·cm (0.120 N·m). Neither is a
validated continuous rating for this mechanism.

Example assumptions for the first bench test: 0.6 kg head, yaw inertia
0.0016 kg·m² and acceleration 60°/s² give inertial torque about 0.0017 N·m.
Cable torsion, bearing friction, belt preload and startup drag must be measured
and added. Do not size a vertical yaw axis as simply mass times head radius;
gravity mainly produces bearing loads and overturning moments.

Start with 30°/s velocity and 60°/s² acceleration limits, unloaded. A provisional
working-torque test target is below 0.025 N·m at the head, subject to measured
current and temperature. This is a design target, not a guaranteed SC09 rating.
If loaded tests fail, retain the bearing/tray architecture and use a larger
positional servo or a position-feedback multi-turn actuator with reduction;
recheck the motor mount, supply and footprint before substitution.

## Power and control changes

- Keep the existing proposed 5 V USB-C logic rail; the CM5 supply budget still
  requires measurement and selection of a suitable source.
- Add a **separate regulated 6 V motor rail**, provisionally sized for 2 A peak
  with current limiting. Do not power the servo from a GPIO or the CM5 3.3 V rail.
  The connector modeled on the rear is an indicative motor-supply inlet.
- Add a dedicated motion-controller reserve with watchdog, hardware motor-power
  enable and a compatible half-duplex TTL bus interface. A generic UART TX/RX
  connection alone is not a complete SC09 bus interface.
- Join grounds at the distribution point. Keep motor return current out of
  microphone and compute return paths; add local decoupling and bulk capacitance
  after measuring transients. Do not assume the previous supply has spare power.
- Read servo feedback before enabling torque. Verify center calibration, input
  travel bounds and the independent index. Invalid feedback, stale commands,
  overcurrent or stalls must inhibit movement and require explicit recovery.
- Do not force an automatic home move at power-up. A calibrated servo reading
  can establish position only while belt engagement is known. Following belt
  removal/slip, use supervised reindexing and verify the head center.

Firmware command proposal (not implemented):

```json
{"type":"head.move","target_deg":90,"max_speed_deg_s":30,"accel_deg_s2":60}
```

Validate finite values and range, perform ramped motion, monitor feedback and
report actual versus requested position. Communication failure must never start
a sweep. The browser uses a smooth interpolation purely for demonstration.

## Cables and assembly

Only the flexible power/control/service harness crosses the joint. High-speed
camera, display and audio links remain in the head. Route a torsion-rated harness
through the bore with sufficient free length and two strain-relief points.
The displayed twist is illustrative deformation, **not a bend-radius or fatigue
simulation**. Do not infer connector engagement from it. No slip ring is required
for bounded travel; unlimited rotation would be a separate redesign, especially
for USB and other high-speed signals.

1. Confirm the exact SC09, horn, belt, pulleys, bearings and controller drawings.
2. Print fit coupons, then check the bearing support and servo clamp without load.
3. Assemble the spindle, bearings and tray; verify axial retention and free rotation.
4. Electrically center the servo, align the head forward, install and tension the
   belt, then lock its adjustable mount. Never tension it against the servo shaft
   beyond the selected actuator's admissible radial load.
5. Transfer the head and its compute supports onto the tray; verify all attachments.
6. Install the harness, check torsion at both endpoints manually without power,
   and only then energize the actuator with current limiting.
7. Test ±30°, ±90°, ±150° and finally ±180°, with head mass and cable drag included.
8. Measure current, temperatures, sound pickup during motion, repeatability,
   collision margins and cable wear over repeated cycles before releasing parts.

## Evidence and verification scope

- [Waveshare SC09 product](https://www.waveshare.com/sc09-servo.htm): positional
  range and feedback feature confirmed in manufacturer-indexed material on
  2026-09-07. Direct page/wiki retrieval returned HTTP 403 in this session;
  purchase dimensions, continuous torque and bus registers remain unresolved.
- [Waveshare SC09 resources](https://www.waveshare.com/wiki/SC09_Servo): intended
  source for final dimensions, servo protocol and drawings before procurement.
- [Pololu continuous-rotation servo explanation](https://www.pololu.com/category/143/continuous-rotation-servos):
  supports the distinction between speed control and positional control.

`verificacao.json` records computed geometry bounds, the translated C.03 top-joint
check and an analytic 15.4 mm vertical gap between all legacy head geometry and
all base/key geometry. That gap is invariant for every yaw angle. It does not
establish complete collision freedom inside the new transmission or head.
`scripts/check_motion.cjs` checks signed-angle limits, servo mapping, rigid
rotation, fixed-base invariance and the committed geometry's joint metadata.

## Resumo em português

A C.04 acrescenta uma base giratória com curso de −180° a +180°, acionada por
microservo posicional SC09 e correia 3:2. A cabeça gira inteira sobre rolamentos;
teclado e conexões traseiras ficam fixos. A base foi alargada para 160 mm e a
cabeça elevada 40 mm. A simulação já permite testar o movimento, mas torque,
cabos, encaixes, fixações e alimentação precisam de validação física.

## Resumen en español

La C.04 incorpora una base giratoria de −180° a +180°, accionada por un microservo
posicional SC09 y correa 3:2. La cabeza gira completa sobre rodamientos; teclado y
conexiones traseras quedan fijos. La base se amplió a 160 mm y la cabeza se elevó
40 mm. La simulación permite explorar el movimiento; par, cables, ajustes,
fijaciones y alimentación todavía requieren validación física.
