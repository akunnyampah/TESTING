# TASKPLAN.md — Waldo Commander ROS 2 Integration
# Last updated: 2026-06-13

## Status keseluruhan
[PHASE 3 of 4] / [COMPLETE — awaiting user confirmation to start Phase 4]

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
- [x] TASK-14 — Buat waldo_commander/ros2/bridge.py (rclpy node + IK client)  ✓
- [x] TASK-15 — Buat waldo_commander/ros2/rviz_launcher.py  ✓
- [x] TASK-16 — Buat waldo_commander/ui/panels/ros2_panel.py (NiceGUI tab)  ✓

## Phase 3 — Integrasi ke Waldo

- [x] TASK-17 — Tambah endpoint POST /api/ros/preview ke server  ✓
- [x] TASK-18 — Tambah endpoint POST /api/ros/execute ke server  ✓
- [x] TASK-19 — Tambah endpoint GET /api/ros/status ke server  ✓
- [x] TASK-20 — Tambah endpoint POST /api/rviz/launch ke server  ✓
- [x] TASK-21 — Tambah endpoint POST /api/rviz/close ke server  ✓
- [x] TASK-22 — Tambah GET /api/rviz/status ke server  ✓
- [x] TASK-23 — Daftarkan tab ROS 2 di titik integrasi  ✓

## Phase 4 — Verifikasi

- [ ] TASK-24 — Verifikasi tab Program masih berfungsi
- [ ] TASK-25 — Verifikasi tab I/O masih berfungsi
- [ ] TASK-26 — Verifikasi tab Settings masih berfungsi
- [ ] TASK-27 — Test Preview dengan koordinat valid → badge hijau
- [ ] TASK-28 — Test Preview dengan koordinat out of range → badge merah
- [ ] TASK-29 — Test tombol Eksekusi hanya aktif saat hijau
- [ ] TASK-30 — Test Launch RViz → window terbuka
- [ ] TASK-31 — Test Close RViz → window tertutup
- [ ] TASK-32 — Test Waldo berjalan normal tanpa ROS 2 aktif

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

---

## Catatan blocker
[Kosong — tidak ada blocker]

---

## Log perubahan
| Tanggal | Task selesai | Catatan |
|---------|--------------|---------|
| 2026-06-11 | TASK-01 s/d TASK-05 | Semua dokumen Agent/ dibaca (CLAUDE.md, PRD.md, SKILL.md, BrandGuidelines.md, TASKPLAN_INSTRUCTIONS.md) |
| 2026-06-11 | TASK-06 s/d TASK-10 | Eksplorasi kode selesai — tab registrasi, route pattern, 3D viewer, NiceGUI version teridentifikasi |
| 2026-06-13 | TASK-11 s/d TASK-16 | Phase 2 selesai — ros2/ module + ui/panels/ros2_panel.py dibuat |
| 2026-06-13 | TASK-17 s/d TASK-23 | Phase 3 selesai — routes.py (6 endpoint) + tab ROS 2 di main.py |
