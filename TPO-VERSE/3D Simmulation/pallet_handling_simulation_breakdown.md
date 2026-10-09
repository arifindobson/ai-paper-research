# Pallet Handling Simulation (revC, PR99) — Breakdown & Reusable Requirements

**Source file:** `Pallet_Handling_Simulation_revC_PR99_5365.html` (28.8 MB, single self-contained file)
**Served in app as:** page `pallet-handling-simulation` → `public/decks/warehouse/pallet_handling_simulation.html` (iframe)
**Purpose of this doc:** reverse-engineered spec of how the simulation is built, so a new scenario
(another packing line, another DC cell, a different vendor's machines) can be briefed and built the
same way. Everything below was read from the file itself (embedded glTF models + the bundled
app script); nothing is guessed except where marked **(inferred)**.

---

## 1. What it simulates

A **discrete-event, real-time 3D digital twin of a pallet-handling cell** with two product lines
feeding trucks:

1. AMR delivers freshly produced carton loads (on plastic pallets) to the cell.
2. **Pallet changer** pushes the load from the plastic pallet onto a wooden pallet.
3. AMR carries the wooden-pallet load to **Line 1** (tall loads) or **Line 2** (short loads).
4. **Helix 3 Evo** stretch-wrapper wraps the load.
5. Line 1 only: **PR99 4-way strapper** straps it (press carriage + sword + turntable).
6. Load waits at the line exit; a **forklift** picks it up and drives to a truck bay.
7. Empty plastic pallets are collected, **stacked 10-high**, and an AMR removes each stack.

It compares **two layout options** (switchable at runtime), each its own 3D model:

| Option | Difference |
| --- | --- |
| 1 · compact | No buffer after strapping — one pallet position at each line exit. |
| 2 · buffer | Extra 1 500 mm buffer conveyor at the west end of each line — two pallet positions after strapping. |

Output is a KPI panel (throughput/h, lead time, station utilisation, blocked time, forklift
utilisation) used to decide which option and how many forklifts (1 or 2) are needed.

---

## 2. File anatomy

| Lines | Content | Size |
| --- | --- | --- |
| 1–68 | HTML head + CSS (dark theme, fixed panes) | small |
| 69–98 | DOM: `<canvas id="c">`, left `#panel` (controls), right `#kpi` (live KPIs), `#loading`, `#tags` overlay | small |
| 69 | Inline PNG logos (base64) | ~41 KB |
| 100 | `<script id="glb1" type="application/octet-stream">` — **Option 1 model**, gzip + base64 | ~14.0 MB |
| 101 | `<script id="glb2" …>` — **Option 2 model**, gzip + base64 | ~14.0 MB |
| 102 | `window.TEX = { carton, decal }` — two PNG data URIs (carton logo, trailer logo decal) | ~99 KB |
| 103–end | One bundled IIFE: **three.js** (module build, GLTFLoader, OrbitControls, PMREM) + **the simulation app** (last ~27 KB, minified) | ~0.4 MB |

**Loading pipeline:** `atob` → `DecompressionStream("gzip")` → `GLTFLoader.parse` → scene is built
lazily per option (only Option 1 on load; Option 2 parsed the first time it is selected).
Needs a modern Chromium browser (DecompressionStream). Single file = works offline, no CDN calls.

**Reuse note:** the 28 MB is ~97 % model payload. For new scenarios, ship models as separate
`.glb` files (Draco/meshopt compressed) and load by URL instead of embedding — a single-file
export is only worth it for e-mail hand-off.

---

## 3. Rendering stack

- **three.js** (WebGL), `OrbitControls` (damping 0.08, `maxPolarAngle` just under 90°, zoom 1.5 – 140 m).
- Camera: perspective FOV 40°, near 0.2, far 400.
- Tone mapping ACES-style, exposure 0.85. Background `#0b1626`-family navy.
- **Lighting:** one warm directional "sun" (colour `0xFFF3E2`-ish, intensity 1.9) with a 4096² shadow map
  (frustum ±32 × ±34 m, bias −4e-4), a weak hemisphere fill (0.3), and an **image-based environment
  generated procedurally** (a small room of emissive boxes run through PMREM; intensity 0.55) — no HDRI file.
- Shadows: cast by everything except stretch film, trailer decal and floor; received by everything except film.
- Pixel ratio capped at 2.

### Coordinate convention (important when authoring models)

The sim logic is 2-D `(x, y)` on the floor; helper `jt(x, y, h=0)` maps to three.js
`Vector3(x, h, -y)`. i.e. **sim +y = world −Z**, height = world Y, units = **metres**.
glTF was exported from Blender (Khronos I/O 4.3), Y-up.

Key constants (sim space): production-line Y rows `L1 = -0.58`, `L2 = -5.75`, pallet-changer
lane A `Y = 4.12`, lane B `Y = 6.18`; load carry height above floor `0.29 m`; AMR deck lift
`0.29 → 0.36 m`; forklift fork lift `0.29 → 0.42 m`; plastic pallet thickness `0.16 m`.

---

## 4. 3D asset catalogue

Both models: glTF 2.0, ~24.7 MB uncompressed each (≈14 MB gz), **~492 k triangles**, 569–600 nodes,
~350 meshes, ~137 materials, **0 animations, 0 skins** (all motion is code-driven, see §6), 2 embedded
PNG textures. Floor plane spans roughly X −17…19 m, sim-Y −17.7…33.6 m.

### 4.1 Scene graph (root nodes, Option 1 positions in glTF space)

| Node | Role | Notes |
| --- | --- | --- |
| `Helix3Evo_Root` (L1) / `L2_Helix3Evo_Root` | Stretch wrapper ×2 | 8 child groups: `ClampCutSealUnit`, `Conveyors`, `ElectricalCabinet`, `Frame`, `L1_StrapTT_Panel`, `LightBarriers`, `RotatingArm_PIVOT`, `SafetyFence`. **Animated parts: `RotatingArm_PIVOT`, `FilmCarriage_Z`** (L2 prefixed `L2_`). |
| `L1_/L2_UShapeConveyor` | Line conveyor (single mesh) | Rotated quaternion `[0.5,-0.5,0.5,0.5]` (Blender → Y-up fix). |
| `L1_/L2_AMR_Q3-600D` | AMR template (single mesh) | Hidden; cloned for the 3 live AMRs. |
| `PalletChanger_Root` | Pallet-changer cell | ~300 child nodes (86 rollers, 60 sprockets, 32 adjusters, pallets, frames, pusher, dispenser, stacker). **Animated: `PC_Pallet changer - pusher`.** Option 2 adds a west buffer conveyor + `PC_WestBufferPallet_1…10`. |
| `PCF_SafetyFence`, `PCF_ControlPanel` | Cell fence (7 parts incl. light-curtain posts, interlock) and control cabinet | Static. |
| `PR99_Frame`, `PR99_PressCarriage`, `PR99_Sword` | 4-way strapper | **Animated: `PR99_PressCarriage` (Y), `PR99_Sword` (Y)**; turntable = `ConveyorStrapping_Turntable` (rotates). |
| `L1_Load_1…7`, `L2_Load_1…6` | Load stand-ins per conveyor slot | Each = `*_Cartons` + `*_Pallet` (+ `*_StretchFilm`, `*_Straps` depending on stage). **Hidden at runtime** — used only as geometry templates / placeholders. |
| `Wall_*` (14 meshes), `Gate_*`, `Wall_Columns`, `TruckBay_Markings` | Building shell, sliding gate, floor markings | Group `walls`. |
| `PalletStack_R1_C1…C9` | 9 static stacks of plastic pallets in a row at X = −13 | Spacing 1.4 m. |
| `Truck_1/2/3_Head`, `_Trailer` | 3 truck bays | Scale 25.4 (model authored in inches), spaced 5 m on Z (13.1 / 18.1 / 23.1). Trailer child carries logo decal. |
| `AMR_Transport_1` | AMR carrying a 10-stack of plastic pallets | 10 pallet meshes + platform. Template for the stack-removal AMR. |
| `Forklift_Inside`, `Forklift_Outside` | Forklift + load variants | Children: `_Truck` (the vehicle), `_Cartons`, `_Pallet`, `_Straps`, `_StretchFilm`. `Forklift_Outside_Truck` is the template used for the live forklifts. |
| `Floor` | Epoxy floor | Group `floor`, no shadow cast. |

### 4.2 Authoring conventions the code relies on (copy these for new models)

1. **Name-based lookup.** The app finds objects by node name (spaces → `_`). Renaming a node breaks the
   sim silently. Names it requires: `PC_WoodPallet_1`, `PC_New Pallet Gopal`, `L1_Load_1_Cartons`,
   `L1_AMR_Q3-600D`, `Forklift_Outside_Truck`, `RotatingArm_PIVOT`, `L2_RotatingArm_PIVOT`,
   `FilmCarriage_Z`, `L2_FilmCarriage_Z`, `ConveyorStrapping_Turntable`,
   `PC_Pallet changer - pusher`, `PR99_PressCarriage`, `PR99_Sword`.
2. **Layer grouping via node `extras.grp`** (inherited by child meshes): `pc` (318 nodes), `line1`, `line2`,
   `fence`, `loads`, `walls`, `forklifts`, `buffer`, `trucks`, `floor`. The "Show / Hide" checkboxes toggle these.
   Only `walls, fence, line1, line2, pc, buffer, trucks` are exposed in the UI.
3. **Pivot = animation axis.** Rotating/sliding parts must have their origin at the pivot point and sit
   under their own node; the code stores each part's *rest* position/quaternion/world-position
   (`userData.base`) on load and animates relative to it.
4. **Templates are hidden and cloned.** Anything matching `L1_Load_*, L2_Load_*, Forklift_*, L1/L2_AMR,
   PC_Q3D*, AMR_Transport, PC_Cartons, PC_New_Pallet_Gopal, PC_WoodPallet_13/14/Buffer, PC_BufferStack_*`
   is hidden after load; the sim creates its own clones with the pivot re-based to *bottom-centre* of the
   bounding box (`or()` helper), so movers can be positioned by their footprint on the floor.
5. **Materials are keyed by name** and re-skinned at load (see §4.3). Unnamed Blender colour materials
   (`"0,128,255"`, `"202,209,238"` …) are kept as exported.
6. **Carton height is parametric:** the template carton is scaled in Y to the requested load height
   (`scale.y = (H − 0.155) / templateHeight`), so one mesh covers every load height.

### 4.3 Material overrides (code-applied)

| Material name | Override |
| --- | --- |
| `PalletWood` | brown `(0.42,0.27,0.13)`, roughness 0.75, no map |
| `ENV_FloorEpoxyGrey` | dark grey, roughness 0.45 |
| `Wall_WhitePlaster` | off-white, roughness 0.92 |
| `StretchFilm` | transparent, opacity 0.28, roughness 0.15, no depth write, double-sided |
| `CartonBrown_Logo` | white base + `TEX.carton` map, roughness 0.85 |
| `Trailer_LogoDecal` | `TEX.decal` map, transparent, no depth write |

Vendor-prefixed material families to preserve for brand colour: `HX_*` (Helix), `PR99_*` (strapper),
`TT_*` (turntable), `CV_*` (conveyor), `AMR_*`, `Gate_*`, `PalletPaint_Pink`, `StrapPP_Black`.

Procedural (non-model) meshes created at run-time: wrapping-film "sleeve" (translucent box
1.24 × 1 × 1.04 m, scaled up in Y while wrapping) and strap loops (thin black boxes, §6.4).

---

## 5. Simulation engine

### 5.1 Time model

- **Fixed timestep `dt = 0.05 s`** of simulated time; the render loop accumulates `realDelta × speed`
  and steps the engine as many times as needed (cap 2000 steps/frame to avoid spirals; real delta
  clamped to 0.1 s).
- Speed buttons: 1×, 2×, 5× (default), 10×, 30×. Pause/Play, Restart (re-seeds and rebuilds state).
- **Deterministic:** own LCG PRNG (`seed = 7`, `x·16807 mod 2³¹−1`) reset on every Restart, so runs of
  Option 1 vs Option 2 with the same parameters are directly comparable.
- Headless hook: `window.__sim.run(seconds)` fast-forwards without rendering; `__sim.S` exposes state,
  `__sim.P` the parameter object, `__sim.showOption(n)` switches layout. **Useful for batch KPI runs / tests.**

### 5.2 Building blocks

| Primitive | What it is |
| --- | --- |
| **Tween** `(duration, update(0..1), done)` | Timed animation of a machine; all machine cycles are tweens, advanced by `dt`. |
| **Lane** `(name, y, slots[])` | A straight conveyor = ordered **slots**, each `{x, proc, occ, res}` (`occ` = load present, `res` = reserved by an incoming mover). `proc` names the process executed when a load *arrives* in that slot. |
| **Load** `{kind, H, tall, born, ready, moving, cart, …}` | `kind` ∈ `product` (cartons on plastic pallet), `wood` (wooden pallet, empty or loaded), `plastic`, `stack`. `born` timestamp gives lead time. |
| **Agent** (AMR / forklift) | Command queue executed in order: `path(points, reverse)`, `lift(up, secs)`, `wait(secs)`, `call(fn)`. Moves with speed from the parameter table; turning in place at 1.6 rad/s before driving; can carry one load (`pickUp`/`drop` re-parent the load). |
| **Station state** | `busy` (cycle running), `blocked` (finished load can't advance because next slot occupied/reserved), `idle` — time in each is integrated for the KPI bars. |

**Lane advance rule** (every tick, scanning from the exit backwards): a load that is `ready` and
not `moving` advances to the next slot if it is free and unreserved, taking `distance / conv` seconds
(conveyor speed `conv = 0.25 m/s`); on arrival it triggers that slot's `proc`.

### 5.3 Lane definitions (slot x-positions in metres, `proc`)

Option 1:

- **L1:** 2.9 · 1.0 · **−1.595 `wrap`** · −3.8 · **−5.2 `strap`** · **−6.71 `pick`**
- **L2:** 2.9 · 1.0 · **−1.595 `wrap`** · −4.55 · **−6.71 `pick`**
- **A (changer lane A):** **−4.93 `disp`** · −3.28 · **−1.76 `hold`** · −0.23 · 1.27 · **2.895 `amr`**
- **B (changer lane B):** 2.865 · 1.24 · −0.26 · **−1.76 `hold`** · **−3.26 `stack`** · **−4.905 `amr`**

Option 2 adds one extra slot at the exit of L1 (`−8.22 pick`, `−6.71` becomes plain), L2 likewise,
and shifts lane A's dispenser to `−6.43` (one more slot).

Slot `proc` meanings: `wrap`, `strap`, `pick` (waits for forklift), `amr` (waits for AMR),
`hold` (waits at a fixed position), `disp` (pallet dispenser output), `stack` (stacker).

### 5.4 Process logic (per machine)

| Process | Trigger | Behaviour | Duration param |
| --- | --- | --- | --- |
| **Production arrival** | Timer | `nextArrival = arrival × (0.8 + 0.4·rand)`; increments a `prodQueue` counter. | `arrival` 80 s |
| **Inbound AMR** | `prodQueue > 0`, lane B slot 0 free | Spawns a `product` load: with prob. `tall`% height **1.55–1.85 m** (→ Line 1) else **1.05–1.40 m** (→ Line 2). AMR picks it up, drives to B slot 0, lifts down, returns to start (9.5, 6.18). | AMR speed |
| **Pallet dispenser** | Lane A slot 0 empty | Produces an empty **wooden pallet** after a delay. | `disp` 15 s |
| **Pallet changer** | Product at B slot 3 (`hold`) **and** empty wood pallet at A `hold` | Pusher advances (0 → 55 % of cycle), the carton stack slides across (`4.12 ↔ 6.18` lanes) onto the wood pallet, pusher returns; the empty plastic pallet continues down lane B. Counts `changed`. | `pc` 30 s |
| **Pallet stacker** | Empty plastic pallet arrives at B `stack` slot | Lifts it onto the growing pile (each +0.16 m); at **10** a `stack` load is emitted and logged. | `stack` 8 s |
| **Stack AMR** | `stack` load at B exit | Drives out through the gate (−6.6, 9.06 → 9.5, 9.06), drops/removes it, waits 30 s, returns. | AMR speed |
| **Transfer AMR** | Loaded wood pallet at A exit and target line slot 0 free | Chooses **L1 if `tall` else L2**, reserves both ends, lifts, drives via x = 4.7, lowers onto the line. | AMR speed |
| **Helix wrap** | Load reaches `wrap` slot | See §6.2. | `wrap` 75 s |
| **PR99 strap** | Load reaches L1 `strap` slot | See §6.4. | `strap` 55 s |
| **Forklift dispatch** | Load at a line's last slot (`pick`), not claimed; forklift idle and not "away" | Picks the **longest-waiting** load across both lines; drives lane-side approach → forks in → lift 2 s → reverse out → to truck bay (Forklift 1 → X = −13 / Forklift 2 → X = −18) → lift down 2 s → load removed ("loaded on truck"), lead time recorded → returns home. Then goes **away** for `fork × 2 × rand` s (random "busy elsewhere" time, mean = `fork`). | `fork` 45 s, `fl` speed |

Forklift home positions: F1 (−10.6, −3.2), F2 (−10.6, 2.8). Forklift 2 only exists when `forks = 2`
(applies on Restart).

### 5.5 Initial state

On start/restart: one loaded wooden pallet with cartons is pre-placed in slot 1 of **each** line
(L1 height 1.7 m tall, L2 1.3 m), the AMRs and forklifts sit at home, and `nextArrival = 2 s`.

---

## 6. Asset movement catalogue (what moves, how, and how fast)

All values are tweakable; "param" = key in the live parameter table (§7).

### 6.1 Conveyor load transport
- Linear interpolation of the load's group position from slot *a* to slot *b* at `conv` m/s.
- Loads ride at height `0.29 m`, Y-rotation 0 (except during strapping).

### 6.2 Helix 3 Evo wrapper (×2)
- **Rotating arm** (`RotatingArm_PIVOT`): rotates about Y at `rpm` (default **18 rpm**) for the whole
  `wrap` cycle: `angle = progress × wrapSeconds × 2π × rpm / 60`.
- **Film carriage** (`FilmCarriage_Z`): rises 0 → full load height in the first 60 % of the cycle, then
  descends to ~15 % of travel at cycle end (`≈ H − 1 m` stroke).
- **Film sleeve** (procedural translucent box) grows in Y with the carriage so the film visibly "builds" up.
- On completion: `wrapped = true`, `ready = true`, KPI `wrapped++`.

### 6.3 Pallet changer pusher
- `PC_Pallet changer - pusher` translates along the lane axis by `(6.18 − 4.12) m` using a triangle wave
  (out 0–55 %, back 55–100 %). The carton stack translates in lock-step in the first 55 %, then is
  re-parented onto the wooden pallet at the 55 % mark.

### 6.4 PR99 4-way strapper (L1)
A scripted **keyframe sequence** (weights → fractions of the strap cycle) repeated for both axes
(0° then 90°): `rotate turntable (w1)` → `press carriage down (pz→1, w0.8)` → `sword up (sy→1, w0.9)`
→ `sword down (sy→0, w0.9)` **+ spawn 2 strap loops** (at ±0.34 m) → `press carriage up (pz→0, w0.6)`
→ final `turntable back to 0° (w1)`.
- Press carriage travels from its rest height to `0.29 + load H + 0.01 m`; sword travels **2.05 m** in Y.
- Turntable (`ConveyorStrapping_Turntable`) and the load rotate together about Y (0 → 90° → 0).
- Strap loops: black `StrapPP` boxes (0.02 m wide, 0.008 m thick) forming a closed rectangle
  around the load at heights 0.11 m and `H + 0.012 m`; the X-axis pair is at ±0.34 m, the Z pair at ±0.3.
- Fallback (no press/sword in model): simple turntable rotation 33–50 %, hold, return, with 4 strap loops.

### 6.5 AMR (Q3-600D style)
- **Differential-drive kinematics:** rotate in place at **1.6 rad/s** until heading within 0.02 rad
  of the target, then drive straight at `amr` m/s (default 1.0). `reverse` flag drives backwards
  (heading + π) — used to back out of cell entrances.
- Lift: linear height change **0.29 ↔ 0.36 m** over 2.5 s while carrying.
- Waypoints are hand-authored polylines (e.g. via x = 4.7 corridor, gate corridor y = 9.06).
- Three instances: inbound (start 9.5, 6.18), transfer (4.7, 1.8), stack removal (2, 9.06).

### 6.6 Forklifts
- Same agent engine: rotate at 1.6 rad/s, drive at `fl` m/s (default **1.8**), fork lift **0.29 ↔ 0.42 m**
  over 2 s, reverse out of the load and truck.
- Waypoint route = approach at lane X − 2.4 m → forks in → reverse → gate X → truck Y → reverse out → home.
- Utilisation = `busyT / simTime`; "away" time is random per cycle (see §5.4).

### 6.7 Camera
- 8 preset views (name, camera position, look-at), flown to with a **1.1 s ease-in-out cubic** lerp
  (cancelled if the user grabs the controls): *Overview, Top view, Pallet changer, Dispenser and stacker,
  Wrapping lines, Strapping and turntable, Exit and forklift, Truck loading*.
- **Follow a pallet:** chases the newest product / loaded wood load, smoothing factor 0.12 per frame,
  keeping a 9 m offset.

---

## 7. Parameter table (UI sliders → `P` object)

| Key | Label | Default | Range (step) | Unit |
| --- | --- | --- | --- | --- |
| `arrival` | Product arrival interval | 80 | 40–180 (5) | s |
| `tall` | Loads above 1.5 m (to strapping) | 50 | 0–100 (5) | % |
| `wrap` | Wrapping cycle, Helix 3 Evo | 75 | 40–150 (5) | s |
| `rpm` | Helix arm speed | 18 | 6–40 (1) | rpm |
| `strap` | 4-way strapping cycle | 55 | 30–120 (5) | s |
| `pc` | Pallet changer push cycle | 30 | 15–90 (5) | s |
| `forks` | Forklifts (restart to apply) | 2 | 1–2 (1) | – |
| `fork` | Forklift busy elsewhere (mean) | 45 | 0–240 (5) | s |
| `fl` | Forklift speed | 1.8 | 1–3 (0.1) | m/s |
| `amr` | AMR speed | 1 | 0.5–1.5 (0.1) | m/s |
| *(no slider)* `disp` | Pallet dispenser cycle | 15 | – | s |
| *(no slider)* `stack` | Pallet stack cycle | 8 | – | s |
| *(no slider)* `conv` | Conveyor speed | 0.25 | – | m/s |

The UI states these are **concept assumptions** — replace with measured machine cycle times for any
real study. New values apply to the next cycle; Restart to compare options from the same start.

---

## 8. KPIs & UI

**Live KPI pane:** sim clock `HH:MM:SS`, products arrived, pallets changed, loads wrapped, loads
strapped (L1), loaded on trucks, **throughput** (/h; shown after 15 min, rolling 60-min window once
past 1 h), **average lead time** (min, last 200 loads, `born → loaded on truck`), waiting at
production (queue), stacks removed, loads waiting for forklift L1 / L2, forklift utilisation.
**Station cards** (pallet changer, Helix L1, Strapper L1, Helix L2, Stacker): state dot
(busy green / idle amber / blocked red) + busy/blocked % bar. **Event log:** last 7 events.
Refreshed 4×/second.

**Control pane:** layout option switch, play/pause, restart, speed, 8 camera presets, follow-pallet,
station-tag overlay toggle, parameter sliders, layer toggles. **Station tags** are HTML labels
projected from 3D anchor points each frame (state-coloured left border). Panels collapse via ☰;
responsive below 760 px.

---

## 9. Template for a new scenario (requirements checklist)

To brief a new simulation in this style, a requester (or a modeller) should supply:

### 9.1 Layout & assets
- [ ] Floor footprint (m), walls/gates, origin and axis orientation (Y-up, metres, sim +y = −Z).
- [ ] One glTF per layout option, **Draco/meshopt compressed**, target **< 150 k tris** per option
      (this one is ~490 k and 14 MB gz per option — heavy on laptops).
- [ ] Every machine as a named node group with `extras.grp` layer tag.
- [ ] Every **moving part** as its own node, **origin on the pivot/axis**, with a documented rest pose
      and travel (angle or distance) — see §6 for how each is specified.
- [ ] Load/vehicle **templates** (carton, pallet, AMR, forklift, truck) as hidden nodes, origin
      anywhere (re-based at load).
- [ ] Material names for anything the code must re-skin (film, wood, floor, decals).
- [ ] Textures (logos) as separate small PNGs.

### 9.2 Process model
- [ ] Ordered list of **stations** with: position (x on lane, lane y), cycle time (fixed or distribution),
      capacity, and what it blocks on (next slot full? other machine busy?).
- [ ] **Lane/slot map** (§5.3 format) incl. which slot triggers which process.
- [ ] **Routing rules** (e.g. tall → Line 1, else Line 2; longest-waiting-first forklift pick).
- [ ] **Mover specs** (§6.5/6.6): speed, turn rate, lift heights/time, waypoint polylines, home
      positions, "busy elsewhere" behaviour.
- [ ] **Arrival process:** mean interval + jitter, product mix (% tall), batch rules.
- [ ] **Initial state** and **seed** (for fair option comparison).

### 9.3 Outputs
- [ ] KPI list with exact definitions (window, units, what counts as "blocked").
- [ ] Parameters exposed as sliders with min / max / step / default.
- [ ] Camera presets (name + position + target) per area of interest.
- [ ] Acceptance targets (e.g. required throughput/h, max forklift utilisation) for the decision.

---

## 10. Known limitations / improvement ideas for the next scenario

- All movers follow **fixed hand-written waypoints**; no path-finding or collision avoidance between
  AMRs/forklifts (conflicts are avoided only by slot reservation). New layouts need new waypoints.
- Machine state is **boolean busy/idle** — no breakdowns, changeovers, shift calendars or operators.
- Single stochastic stream (arrivals + forklift away time share one RNG); no warm-up period or
  multi-replication statistics — add before quoting throughput numbers externally.
- Names-as-API between model and code is brittle; consider a JSON **scenario manifest** (stations,
  lanes, pivots, params) next to each `.glb` so code and model can't drift.
- Embedded 28 MB single file: split model/code, lazy-load options, compress with Draco/meshopt,
  decimate (492 k tris), and serve gzip/brotli.
- No Supabase / auth dependency — it is a static asset; in ParaTech it is exposed via the
  `pallet-handling-simulation` page (iframe, `/decks/warehouse/`). It is therefore **not** access-controlled
  at the file level (same as other `public/decks/` pages).
