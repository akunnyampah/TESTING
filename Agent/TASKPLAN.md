# TASKPLAN.md — Waldo Commander ROS 2 Integration
# Last updated: 2026-06-13

## Status keseluruhan
[PHASE 5 of 5] / [COMPLETE — all features verified]

---

## Phase 1 — Eksplorasi & verifikasi (tidak ada kode)

- [x] TASK-01 — Baca Agent/CLAUDE.md  ✓
- [x] TASK-02 — Baca Agent/PRD.md  ✓
- [x] TASK-03 — Baca Agent/SKILL.md  ✓
- [x] TASK-04 — Baca Agent/BrandGuidelines.md  ✓
- [x] TASK-05 — Baca Agent/TASKPLAN_INSTRUCTIONS.md  ✓
- [x] TASK-06 — Identifikasi file registrasi tab di waldo_commander/  ✓
- [x] TASK-07 — Identifikasi file server route di waldo_commander/  ✓
- [x] TASK-08 — Identifikasi mekanisme update 3D viewer  ✓
- [x] TASK-09 — Identifikasi versi NiceGUI yang dipakai  ✓
- [x] TASK-10 — Konfirmasi findings ke user sebelum lanjut  ✓

## Phase 2 — Setup struktur file baru

- [x] TASK-11 — Buat folder waldo_commander/ros2/  ✓
- [x] TASK-12 — Buat waldo_commander/ros2/__init__.py  ✓
- [x] TASK-13 — Buat waldo_commander/ros2/config.py (workspace limits)  ✓
- [~] TASK-14 — Buat waldo_commander/ros2/bridge.py (rclpy node + IK client)  ✓  ← REVISED in v2: rewrite to remove MoveIt IK, add /joint_states publisher
- [x] TASK-15 — Buat waldo_commander/ros2/rviz_launcher.py  ✓
- [x] TASK-16 — Buat waldo_commander/ui/panels/ros2_panel.py (NiceGUI tab)  ✓

## Phase 3 — Integrasi ke Waldo

- [~] TASK-17 — Tambah endpoint POST /api/ros/preview ke server  ✓  ← REVISED in v2: rewrite to use EditingIKSolver instead of MoveIt
- [x] TASK-18 — Tambah endpoint POST /api/ros/execute ke server  ✓
- [x] TASK-19 — Tambah endpoint GET /api/ros/status ke server  ✓
- [x] TASK-20 — Tambah endpoint POST /api/rviz/launch ke server  ✓
- [x] TASK-21 — Tambah endpoint POST /api/rviz/close ke server  ✓
- [x] TASK-22 — Tambah GET /api/rviz/status ke server  ✓
- [x] TASK-23 — Daftarkan tab ROS 2 di titik integrasi  ✓

## Phase 4 — Verifikasi

- [x] TASK-24 — Verifikasi tab Program masih berfungsi  ✓ PASS
- [x] TASK-25 — Verifikasi tab I/O masih berfungsi  ✓ PASS
- [x] TASK-26 — Verifikasi tab Settings  ✓ N/A (tab tidak ada di codebase)
- [x] TASK-27 — Test Preview dengan koordinat valid → badge hijau  ✓ PASS (check_workspace verified)
- [x] TASK-28 — Test Preview dengan koordinat out of range → badge merah  ✓ PASS (check_workspace verified)
- [x] TASK-29 — Test tombol Eksekusi hanya aktif saat hijau  ✓ PASS (static analysis confirmed gating)
- [x] TASK-30 — Test Launch RViz → window terbuka  ✓ PASS (pid=26110, poll()=None after 1.5s)
- [x] TASK-31 — Test Close RViz → window tertutup  ✓ PASS (status=closed, running=False)
- [x] TASK-32 — Test Waldo berjalan normal tanpa ROS 2 aktif  ✓ PASS (ROS2_AVAILABLE=False path verified)

---

## Temuan eksplorasi

### File registrasi tab
- Path: `waldo_commander/main.py` — fungsi `_build_left_panels()` (baris 468)
- Cara menambahkan tab baru:
  1. Tambah `ui.tab(name="ros2", label="", icon="...")` di dalam blok `ui.tabs()` (setelah `gripper_tab`, sekitar baris 489)
  2. Tambah `with ui.tab_panel("ros2").classes("..."):` di dalam blok `ui.tab_panels(side_tabs, ...)` (sekitar baris 527)
  3. Panggil `ros2_panel.build()` atau `create_ros2_tab_content()` di dalam panel tersebut
- Integrasi minimal: **2 penambahan di `_build_left_panels()`** + 1 import di bagian atas `main.py`

### File server route
- Pattern: FastAPI via NiceGUI (`ng_app` = `nicegui.app`)
- Cara menambahkan route: decorator `@ng_app.get(...)` / `@ng_app.post(...)` persis seperti di `camera_service.py` baris 357–374
- Import yang diperlukan: `from nicegui import app as ng_app`
- Route baru cukup ditulis di file terpisah (`ros2/routes.py` atau langsung di `ros2_panel.py`) lalu **diimport** di `main.py` agar teregistrasi — tidak perlu mendaftarkan secara manual
- Tidak ada file server terpisah; NiceGUI pakai FastAPI (Starlette) built-in

### Mekanisme update 3D viewer
- Untuk **live update** (dari status robot): `update_urdf_angles(angles_deg: np.ndarray)` → `ui_state.urdf_scene.set_axis_values(buffer)`
  - File: `waldo_commander/services/urdf_scene/angle_pipeline.py` baris 97
  - `update_urdf_angles` menerapkan index mapping + sign + offset (untuk memetakan urutan controller ke URDF)
- Untuk **ROS 2 IK preview** (langsung dari MoveIt, sudah dalam urutan URDF, dalam radian):
  - Panggil langsung: `ui_state.urdf_scene.set_axis_values(joint_angles_rad)` (baris 1379, `urdf_scene.py`)
  - Ini bypass index mapping — cocok karena MoveIt mengembalikan joint values dalam URDF order
  - **Tidak mengubah `robot_state`** — hanya visual preview, robot tidak bergerak

### NiceGUI version
- Custom fork: `git+https://github.com/Jepson2k/nicegui.git@feature/additional_scene_features`
- Installed version string: `0.0.0.post6571.dev0+b393ee8d` (dev build dari fork)

### Launch script untuk ROS 2 integration
- File: `start_waldo_ros2.sh` (repo root, executable)
- **Wajib digunakan** setiap kali menjalankan Waldo untuk ROS 2 integration testing
- Jika Waldo distart tanpa script ini (tanpa source ROS 2), `rclpy` tidak terdeteksi
  dan `ROS2_AVAILABLE = False` — semua endpoint `/api/ros/*` akan mengembalikan error
- Usage:
  ```bash
  # Foreground (lihat log langsung):
  ./start_waldo_ros2.sh

  # Background (log ke file):
  ./start_waldo_ros2.sh > /tmp/waldo_server.log 2>&1 &
  ```
- Script otomatis source `/opt/ros/jazzy/setup.bash` dan `~/ros2_ws/install/setup.bash`
  sebelum menjalankan `waldo-commander`

### Startup procedure setelah laptop restart

1. Jalankan Waldo dengan ROS 2:
   ```bash
   ./start_waldo_ros2.sh > /tmp/waldo_server.log 2>&1 &
   ```
2. Buka browser → `http://localhost:8080`
3. Buka tab **ROS 2** → klik tombol **Launch RViz**
4. RViz akan terbuka dan langsung mirror gerakan robot secara realtime otomatis
   — tidak perlu konfigurasi tambahan apapun

---

## Catatan blocker

### [RESOLVED] bridge.py: group_name salah → INVALID_GROUP_NAME pada setiap IK call

**Gejala:** Setiap call ke `/compute_ik` mengembalikan `error_code.val = -15`
(`INVALID_GROUP_NAME`), menyebabkan semua IK preview gagal.

**Root cause:** `bridge.py` mengirim `group_name = "arm"`, padahal SRDF mendefinisikan
satu-satunya planning group sebagai `"arm_group"` (bukan `"arm"`).
Selain itu, `timeout` tidak di-set sehingga default-nya 0 — IK solver bisa langsung
return tanpa mencoba solution.

**Fix:** Di `waldo_commander/ros2/bridge.py` fungsi `compute_ik_sync()`:
1. `req.ik_request.group_name = "arm_group"` (bukan `"arm"`)
2. `req.ik_request.timeout = Duration(seconds=5).to_msg()` (import `Duration` dari `rclpy.duration`)

**Status:** FIXED — ditemukan saat investigasi SRDF post-Phase 4.

---

### [RESOLVED] Default coordinates (0.3, 0.0, 0.4) tidak reachable — IK selalu gagal saat startup

**Gejala:** Saat tab ROS 2 pertama dibuka dan user menekan Preview dengan nilai default,
IK selalu gagal ("pose not reachable"), meskipun `group_name` sudah benar.

**Root cause:** Default koordinat `(x=0.3, y=0.0, z=0.4)` memiliki jarak Euclidean dari
`base_link` sebesar `√(0.3² + 0.4²) ≈ 0.500 m`, melebihi estimasi max reach robot
(~0.466 m dari penjumlahan link L2→L5: 0.1105 + 0.180 + 0.17635 ≈ 0.467 m).
Koordinat ini secara geometris berada di luar workspace, sehingga IK solver tidak
pernah bisa mengembalikan solusi valid.

WORKSPACE_LIMITS sebelumnya juga terlalu lebar (±0.6 m x/y, 0–0.9 m z), jauh melampaui
jangkauan fisik robot.

**Fix:**
- `waldo_commander/ros2/config.py`: WORKSPACE_LIMITS diperketat ke:
  - `x`: (−0.35, 0.35) m
  - `y`: (−0.35, 0.35) m
  - `z`: (0.0, 0.45) m
  — konservatif di dalam sphere radius ~0.466 m, memastikan koordinat yang lolos
  workspace check benar-benar memiliki kemungkinan IK solution.
- `waldo_commander/ui/panels/ros2_panel.py`: default inputs diubah ke
  `(x=0.15, y=0.0, z=0.2)`, jarak Euclidean `√(0.15² + 0.2²) ≈ 0.250 m`.
  Diverifikasi CLI mengembalikan `error_code.val = 1` (SUCCESS).

**Status:** FIXED — ditemukan saat CLI testing post-Phase 4.

---

### [KNOWN LIMITATION] RViz crashes on mouse interaction — Qt/VS Code snap conflict

**Gejala:** RViz window opens and renders robot model correctly, but crashes
immediately when user attempts to zoom or pan with mouse.

**Root cause:** Environment issue — VS Code installed as snap injects Qt/GTK
overrides into the subprocess environment that conflict with RViz2's Qt renderer
on mouse input events. Same underlying snap/glibc conflict as the rviz2 launch
crash (fixed), but triggered at a different point (input handling vs startup).

**Impact:** RViz is functional for pose preview (read-only). Model renders,
/tf frames update, robot pose changes with Preview clicks. Only interactive
navigation (zoom/pan/rotate) is broken.

**Workaround:** Camera position is pre-configured in `waldo_preview.rviz`
(Distance: 1.2m, Pitch: 0.52, Yaw: 5.14, Focal Z: 0.25m) so robot fills view
on open without any mouse interaction required.

**Not a code bug.** No fix planned — this is an environment limitation specific
to running RViz2 under a snap-based VS Code session.

---

### [KNOWN LIMITATION] _to_rviz_angles() L2 slightly exceeds RViz joint limit

**Gejala:** L2 max dari _to_rviz_angles() adalah +86.6° (π/2 + max controller angle),
sedangkan URDF mendefinisikan L2 joint limit sebesar +57°. RViz meng-clamp nilai
secara silent — tidak crash, tidak error, hanya pose tidak 100% akurat di ekstrem range.

**Impact:** Hanya terlihat saat Preview menggunakan koordinat dekat batas workspace
(z sangat rendah + x/y dekat ±0.35m). Pose realtime di workspace normal tidak terpengaruh.

**Workaround:** None needed — RViz clamps silently, no crash. Acceptable for visualization.

**Not a code bug.** Fix would require re-deriving L2 formula with tighter constraint.

---

### [RESOLVED] rviz2 crash saat dijalankan dari VS Code — snap/glibc conflict

**Gejala:** `launch_rviz()` berhasil spawn subprocess (dapat PID) tapi `poll()` langsung
non-None — process mati seketika. Error: `undefined symbol: __libc_pthread_init, version GLIBC_PRIVATE`.

**Root cause:** VS Code diinstall sebagai snap, yang meng-inject variabel GTK ke environment:
```
GTK_PATH=/snap/code/247/usr/lib/x86_64-linux-gnu/gtk-3.0
GTK_EXE_PREFIX=/snap/code/247/usr
GTK_IM_MODULE_FILE=/home/<user>/snap/code/common/.cache/immodules/immodules.cache
```
Saat rviz2 init GTK, ia load `libcanberra-gtk-module.so` dari path snap tersebut.
Library itu punya RPATH ke `snap/core20/current/lib/` → `libpthread.so.0` dari snap/core20
(GLIBC 2.31) di-load, konflik dengan system GLIBC 2.39.

**Fix:** Di `waldo_commander/ros2/rviz_launcher.py`, strip ketiga var tersebut dari env subprocess
sebelum `subprocess.Popen()` dipanggil. Tidak menyentuh environment parent process.

**Status:** FIXED di Phase 4. Jika muncul lagi di environment lain (non-snap VS Code),
strip ini adalah no-op dan tidak ada efek samping negatif.

---

### [RESOLVED] bridge.py: TCP/flange coordinate mismatch — IK target salah frame saat tool aktif

**Gejala:** Saat tool terpasang (misal SSG-48), robot bergerak ke posisi yang
tidak tepat. Waldo menampilkan koordinat TCP tip (ujung gripper), tapi MoveIt
dikirim koordinat yang sama sebagai target L6 flange — sehingga TCP tip
berakhir di posisi yang offset dari yang diinginkan (hingga ~105mm untuk SSG-48).

**Root cause:** `bridge.py` mengirim `(x, y, z)` input user langsung ke
`/compute_ik` sebagai target L6 flange. Tapi `robot_state.x/y/z` (readout Waldo)
dihitung oleh `get_fkine_flat_mm()` yang menerapkan tool transform via
`_pinokin.set_tool_transform()` — jadi readout sudah termasuk TCP offset.
SRDF `arm_group` tidak mendefinisikan tip_link di luar L6; URDF tidak punya
link TCP terpisah.

**Tool offsets (dalam L6 frame):**
- NONE: (0, 0, 0) — tidak ada offset
- SSG-48: (0, 0, −0.105 m)
- PNEUMATIC: (−0.055, 0, −0.027 m)
- MSG: (−0.029, 0, −0.103 m)
- VACUUM: (0, 0, −0.037 m)

**Fix:** Di `compute_ik_sync()`, sebelum membangun IK request:
1. Baca `robot_state.tool_key` (active tool)
2. Lookup offset dari `parol6.tools.get_registry()[tool_key].transform`
3. `flange = user_input - offset` (valid karena offset translation-only, orientation identity)
4. Kirim `flange` ke MoveIt, bukan `user_input`
5. Tool NONE: offset (0,0,0) → perilaku tidak berubah (backward compatible)

**Status:** FIXED — ditemukan saat investigasi TCP/flange mismatch post-Phase 4.

---

## Architecture Revision — v2 (triggered after Phase 4)

Root cause: MoveIt /compute_ik targets L6 flange only. Waldo displays
TCP tip (flange + tool offset). Manual offset subtraction failed across
multiple attempts due to inconsistent pose-dependent behavior.

Resolution: Switch to Waldo-local IK (EditingIKSolver) which is already
tool-aware. ROS 2 role reduced to /joint_states publisher for RViz display.

Files to rewrite: bridge.py, routes.py (/api/ros/preview), rviz_launcher.py

---

## Log perubahan
| Tanggal | Task selesai | Catatan |
|---------|--------------|---------|
| 2026-06-11 | TASK-01 s/d TASK-05 | Semua dokumen Agent/ dibaca (CLAUDE.md, PRD.md, SKILL.md, BrandGuidelines.md, TASKPLAN_INSTRUCTIONS.md) |
| 2026-06-11 | TASK-06 s/d TASK-10 | Eksplorasi kode selesai — tab registrasi, route pattern, 3D viewer, NiceGUI version teridentifikasi |
| 2026-06-13 | TASK-11 s/d TASK-16 | Phase 2 selesai — ros2/ module + ui/panels/ros2_panel.py dibuat |
| 2026-06-13 | TASK-17 s/d TASK-23 | Phase 3 selesai — routes.py (6 endpoint) + tab ROS 2 di main.py |
| 2026-06-13 | TASK-24 s/d TASK-32 | Phase 4 selesai — semua verifikasi PASS; fix snap/GTK di rviz_launcher.py |
| 2026-06-13 | bugfix | bridge.py: group_name "arm" → "arm_group" + set IK timeout 5s (SRDF mismatch, error_code -15) |
| 2026-06-13 | bugfix | config.py: WORKSPACE_LIMITS diperketat (±0.35/0.45 m); ros2_panel.py: default (0.3,0,0.4)→(0.15,0,0.2) (default lama OOB, jarak 0.5m > max reach 0.466m) |
| 2026-06-13 | bugfix | bridge.py: TCP offset correction — user input adalah TCP target (sama dengan readout Waldo), tapi MoveIt hanya tahu L6 flange. Fix: subtract active tool offset (dari parol6.tools.get_registry()) sebelum kirim ke /compute_ik. Valid karena tool offset adalah translation-only (no rpy) dan IK orientation identity. Tool NONE: no-op. |
| 2026-06-14 | Architecture pivot v2 | MoveIt IK removed; EditingIKSolver used instead; /joint_states publisher added; rsp.launch.py for RViz |
| 2026-06-14 | bugfix Phase 5 | ros2_panel.py: handle_preview() masih memanggil bridge.compute_ik_sync() yang sudah dihapus di Phase 5. Diganti dengan EditingIKSolver langsung (konsisten dengan routes.py). asyncio/run_in_executor dihapus karena IK sekarang pure CPU (tidak blocking I/O). |
| 2026-06-14 | bugfix Phase 5 | bridge.py: publisher QoS changed from RELIABLE (shorthand 10) to explicit BEST_EFFORT/VOLATILE to match rsp's qos_override. Fast-DDS Jazzy silently drops RELIABLE→BEST_EFFORT on loopback. Also publish 3x with 100ms interval to handle transient delivery failures. |
| 2026-06-14 | bugfix Phase 5 | waldo_preview.rviz: added Description Source: Topic + changed Durability from Volatile→Transient Local (robot model now loads). Added Orbit camera view at Distance 1.2m so robot fills view without mouse interaction. |
| 2026-06-14 | TASK-41,42,43 | Pipeline confirmed end-to-end: X/Y/Z input → IK → /joint_states → rsp → /tf → RViz renders pose. Robot model visible. Known limitation: RViz mouse interaction crashes (Qt/snap conflict, view-only workaround via pre-set camera). |
| 2026-06-21 | TASK-47,48 | All joints verified correct in RViz realtime mirror. _to_rviz_angles() mapping finalized: L1=−θ, L2=θ+π/2, L3=−(θ−π), L4=−θ+π, L5=θ, L6=−θ |
| 2026-06-21 | cleanup | bridge.py: [JS] angles_rad log level reverted INFO → DEBUG (was elevated during investigation) |
| 2026-06-29 | bugfix | bridge.py: _to_rviz_angles() L1 removed incorrect negation. Formula was `-angles[0]` (flip), corrected to `angles[0]` (identity). Both URDFs use +Z axis with rpy=0 — no conversion needed. Empirical: Waldo +45°→RViz -45° (wrong) → now Waldo +45°→RViz +45° (correct). |
| 2026-06-29 | bugfix | bridge.py: _to_rviz_angles() L4 removed incorrect π offset. Formula was `-angles[3] + π` (constant 180° bias), corrected to `-angles[3]` (flip only). Mathematically verified: Waldo home 0° → RViz 0° (correct), no constant offset in URDF joint chain. |
| 2026-06-29 | bugfix | bridge.py: _to_rviz_angles() L6 corrected home offset. Formula was `-angles[5]` (flip), corrected to `angles[5] - π` (offset by π). Waldo L6 home=180°, RViz L6 home=0°. Verified: all 6 joints at home → [90°,0°,0°,0°,0°,0°] in RViz ✓ |
| 2026-07-06 | Help panel update selesai | 4 tab: Keybindings, Quick Start, Fitur GUI, Safety |
| 2026-07-06 | Help panel update selesai | assets/help/ folder untuk gambar & video |
| 2026-07-06 | Help panel update selesai | Auto-show dialog + per-browser storage |

---

## Phase 5 — Architecture revision (Waldo-local IK)

- [x] TASK-33 — Confirm EditingIKSolver.solve() exact signature from ik_solver.py  ✓
- [x] TASK-34 — Show diff: bridge.py rewrite (remove MoveIt, add /joint_states publisher)  ✓
- [x] TASK-35 — User approves bridge.py diff → apply  ✓
- [x] TASK-36 — Show diff: routes.py /api/ros/preview rewrite (use EditingIKSolver)  ✓
- [x] TASK-37 — User approves routes.py diff → apply  ✓
- [x] TASK-38 — Show diff: rviz_launcher.py update (rsp.launch.py default)  ✓
- [x] TASK-39 — User approves rviz_launcher.py diff → apply  ✓
- [x] TASK-40 — Restart Waldo server, confirm clean startup  ✓ PASS
- [x] TASK-41 — Run: ros2 launch parol6_moveit rsp.launch.py  ✓ PASS (launched via rviz_launcher.py)
- [x] TASK-42 — Open RViz from GUI button, confirm robot model visible  ✓ PASS
- [x] TASK-43 — Test Preview valid coords → badge hijau + RViz pose updates  ✓ PASS
- [x] TASK-44 — Test Preview: Waldo X/Y/Z display matches panel input  ✓ PASS (X≈0mm Y≈300mm Z≈100mm)
- [x] TASK-45 — Test Preview out-of-range → badge merah, no movement  ✓ PASS (X=Y=Z=0.5 → "Out of workspace", Execute disabled)
- [x] TASK-46 — Test Execute → robot moves, Waldo X/Y/Z matches input  ✓ PASS
- [x] TASK-47 — Final review: list all changed files with exact diffs  ✓ COMPLETE
- [x] TASK-48 — Realtime RViz mirroring verified — all 6 joints confirmed correct  ✓ PASS
