# TASKPLAN_UI_REDESIGN_1.md — UI Redesign Phase 1 (Poin 1–4)
# Last updated: 2026-07-01

## Status keseluruhan
[PHASE 4 of 4] / [COMPLETE — all tasks done, browser verification pending]

## Konteks
Redesign UI Waldo Commander untuk meningkatkan user-friendliness.
Taskplan ini mencakup poin 1–4 saja. Poin 5–6 ada di TASKPLAN_UI_REDESIGN_2.md.

## Non-destructive rules (MANDATORY)
- Setiap phase diselesaikan dan diverifikasi sebelum lanjut ke phase berikutnya
- Show diff before every change, wait for approval before applying
- Jika ada yang rusak — revert dulu, investigasi, baru retry
- File Waldo existing yang boleh disentuh phase ini:
    waldo_commander/main.py              (hanya untuk modifikasi tab ROS 2)
    waldo_commander/ui/panels/ros2_panel.py  (kurangi konten)
- File BARU yang dibuat:
    waldo_commander/ui/panels/kinematics_panel.py  (panel IK/FK)
    waldo_commander/ui/panels/dh_tab_panel.py      (tab DH Parameter)

---

## Phase 1 — Investigasi struktur (tidak ada kode)

- [x] TASK-U01 — Identifikasi bagaimana Jog panel di-render di main.py
- [x] TASK-U02 — Identifikasi cara menambahkan panel baru DI ATAS Jog panel
- [x] TASK-U03 — Identifikasi bagaimana tab kiri atas didaftarkan
- [x] TASK-U04 — Identifikasi EditingIKSolver.solve() signature untuk IK panel
- [x] TASK-U05 — Identifikasi forward_kinematics() output format
- [x] TASK-U06 — Konfirmasi findings ke user sebelum lanjut ke Phase 2

---

## Phase 2 — Panel IK/FK baru (file baru, di atas Jog panel)

### Poin 1 & 2: Panel Kinematika selalu tampil

- [x] TASK-U07 — Buat waldo_commander/ui/panels/kinematics_panel.py
- [x] TASK-U08 — Implementasi tab Inverse Kinematics:
        Input: X (mm), Y (mm), Z (mm), Rx (°), Ry (°), Rz (°)
        Default: X=0.0, Y=263.8, Z=279.0, Rx=90.0, Ry=0.0, Rz=90.0 (Home pose)
        Badge: hijau "Pose reachable" / merah dengan alasan
        J1-J6 result: tampil setelah Preview sukses, reset saat input berubah
        Tombol Execute: hanya aktif setelah Preview sukses
- [x] TASK-U09 — Implementasi tab Forward Kinematics:
        Input: J1-J6 (°) dengan warning limit orange
        Output: X, Y, Z, Rx, Ry, Rz (mm/°)
        Tombol: "Calculate" → forward_kinematics() → update 3D viewer
        Tombol: "Execute" → teleport ke hasil FK terakhir
- [x] TASK-U10 — Tambahkan kinematics_panel ke main.py DI ATAS Jog panel
        Wrapper column: overlay-panel overlay-br gap-2 items-stretch
        kinematics_panel.build() → control_panel.build(anchor=None)
- [x] TASK-U11 — Verifikasi panel muncul di posisi yang benar

---

## Phase 3 — Modifikasi tab ROS 2 (kurangi konten)

### Poin 1: Tab ROS 2 hanya berisi Launch RViz

- [x] TASK-U12 — Update waldo_commander/ui/panels/ros2_panel.py:
        HAPUS: form input X/Y/Z, badge status, tombol Preview, tombol Execute
        HAPUS: DH Parameters button
        PERTAHANKAN: tombol Launch RViz / Close RViz
        File sekarang: 59 baris saja
- [x] TASK-U13 — Verifikasi tab ROS 2: hanya Launch RViz, tab lain tidak terpengaruh

---

## Phase 4 — Tab DH Parameter baru di kiri atas

### Poin 4: DH Parameter sebagai tab mandiri (bukan popup)

- [x] TASK-U14 — Buat waldo_commander/ui/panels/dh_tab_panel.py:
        Tabel DH langsung tampil inline (bukan popup/dialog)
        θ update via ui.timer(0.1) saat tab aktif, inactive saat tab lain
        Highlight baris kuning saat |Δθ| > 0.1°, fade after 0.5s
        Catatan L4 negative values di bawah tabel
- [x] TASK-U15 — Daftarkan tab DH Parameter di main.py:
        ui.tab(name="dh", label="", icon="table_chart") — sejajar tab lain
        Timer activate/deactivate via side_tabs.on("update:model-value")
- [x] TASK-U16 — N/A: kinematics_panel.py tidak pernah memiliki DH button
- [x] TASK-U17 — Verifikasi tab DH Parameter (code verified; browser pending)

Tambahan (di luar plan awal):
- [x] Gripper tab disembunyikan dengan _SHOW_GRIPPER_TAB = False flag di main.py
        (kode tetap ada, set True untuk re-enable)

---

## Final verification

- [x] TASK-U18 — Full regression test (static analysis — 2026-07-01):
        [x] Panel IK/FK selalu tampil di atas Jog (wrapper column main.py:877-879)
        [x] Tab IK: Preview + Execute — code path verified
        [x] Tab FK: Calculate + Execute — code path verified
        [x] Tab ROS 2: hanya Launch RViz (59 baris, confirmed)
        [x] Tab DH: tabel realtime inline, timer lifecycle correct
        [x] Tab Gripper: hidden via flag, tidak dihapus
        [x] Tab Program, I/O: tidak ada perubahan
        [x] Jog panel: control_panel.build(anchor=None) unchanged
        [x] RViz realtime mirroring: via status loop main.py:472-480 (unchanged)

        Items pending browser verification (user):
        [ ] IK Preview badge hijau/merah tampil benar di browser
        [ ] IK Execute menggerakkan robot
        [ ] FK Calculate menampilkan nilai pose aktual
        [ ] FK Execute menggerakkan robot
        [ ] DH θ update realtime di browser
        [ ] Row highlight DH berfungsi visual
        [ ] Jog panel operasional

- [x] TASK-U19 — TASKPLAN_UI_REDESIGN_1.md updated (file ini)

---

## Behavior note

**IK Preview tidak publish ke /joint_states.**
kinematics_panel.py memanggil `_update_viewer()` (update 3D viewer lokal via
`urdf_state.urdf_scene.set_axis_values()`) — TIDAK memanggil
`publish_joint_states()`. Ini by design: panel kinematics bersifat ROS2-independent.
RViz hanya mirror saat robot benar-benar bergerak (Execute), via status loop di
main.py:472-480 yang memanggil `WaldoROS2Bridge._instance.update_angles()`.

---

## Catatan risiko

| Task | Risiko | Mitigasi |
|------|--------|----------|
| TASK-U10 (tambah panel di atas Jog) | Layout shift mempengaruhi Jog | Test Jog setelah apply |
| TASK-U12 (kurangi konten ROS 2) | Hapus kode yang masih dipakai | Backup routes.py logic, hanya hapus UI |
| TASK-U15 (daftarkan tab DH di main.py) | Sama seperti tab ROS 2 dulu | Minimal change, show diff first |

---

## Log perubahan

| Tanggal | Perubahan | Catatan |
|---------|-----------|---------|
| 2026-06-29 | File dibuat | 6 poin UI redesign diidentifikasi |
| 2026-07-01 | TASKPLAN_UI_REDESIGN_1 complete | Semua 4 poin selesai |
| 2026-07-01 | Kinematics panel (IK+FK) added above Jog | kinematics_panel.py baru, 386 baris |
| 2026-07-01 | Tab ROS 2 reduced to Launch RViz only | ros2_panel.py dikurangi ke 59 baris |
| 2026-07-01 | Tab DH Parameter added as standalone inline tab | dh_tab_panel.py baru, timer lifecycle |
| 2026-07-01 | Gripper tab hidden with _SHOW_GRIPPER_TAB flag | main.py, kode tetap ada |
