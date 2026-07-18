# TASKPLAN_DH_EXPERIMENT.md — DH Parameter Experiment Tab
# Last updated: 2026-07-06

## Status keseluruhan
[PHASE 1 of 4] / [NOT STARTED]

## Deskripsi fitur
Tab baru "Eksperimen" di dalam panel DH Parameter (sejajar tab "Realtime").
User bisa mengubah semua 4 variabel DH (a, α, d, θ) per joint secara bebas,
lalu klik "Plot" untuk menampilkan stick diagram 2D (top view + side view)
di matplotlib window terpisah. Ada tombol Reset untuk kembali ke nilai
default robot asli.

## Tujuan pembelajaran
Menunjukkan bahwa mengubah parameter DH menghasilkan bentuk kinematika
yang berbeda — membantu mahasiswa memahami hubungan antara parameter
geometri robot dan bentuk/jangkauan lengan robot.

## Keputusan desain
- Lokasi: sub-tab "Eksperimen" di dalam dh_tab_panel.py
- Output: matplotlib window terpisah (bukan embedded di browser)
- Plot: 2D top view (XY) + 2D side view (XZ) berdampingan
- Variabel: semua 4 (a, α, d, θ) bisa diubah bebas
- Nilai awal: default robot asli (_DH_PARAMS dari dh_tab_panel.py)
- θ awal: nilai default (tidak sync dengan posisi robot saat ini)
- Reset: tombol reset ke nilai default robot asli per-row
- matplotlib: perlu dicek ketersediaannya di waldo_env

## File yang akan disentuh
- waldo_commander/ui/panels/dh_tab_panel.py  ← tambah sub-tab Eksperimen
- TIDAK ada file lain yang disentuh

---

## Phase 1 — Investigasi

- [ ] TASK-DH-01 — Cek matplotlib di waldo_env:
        waldo_env/bin/python -m pip show matplotlib 2>/dev/null || \
        waldo_env/bin/python -c "import matplotlib; print(matplotlib.__version__)"
        → jika tidak ada: install dengan
        waldo_env/bin/pip install matplotlib --quiet

- [ ] TASK-DH-02 — Cek apakah matplotlib bisa membuka window dari
        NiceGUI subprocess context (headless issue):
        waldo_env/bin/python -c "
        import matplotlib
        matplotlib.use('TkAgg')  # atau 'Qt5Agg'
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.plot([1,2,3])
        plt.show(block=False)
        print('OK')
        plt.close()
        "
        → jika error: coba backend lain (Agg, TkAgg, Qt5Agg, wxAgg)
        → catat backend yang berhasil

- [ ] TASK-DH-03 — Show current dh_tab_panel.py full structure:
        cat waldo_commander/ui/panels/dh_tab_panel.py
        → identify: how create_dh_tab_content() is structured,
          what _DH_PARAMS and _DH_LIMITS_DEG contain,
          how the Realtime tab is currently built

- [ ] TASK-DH-04 — Plan FK calculation from custom DH parameters:
        The stick diagram needs joint frame positions.
        For each joint i, compute T_0_i = T_1 × T_2 × ... × T_i
        where T_i is the Modified DH transformation matrix:

        T_i = Rot_x(α_{i-1}) × Trans_x(a_{i-1}) × Rot_z(θ_i) × Trans_z(d_i)

        Extract origin of each frame (column 4 of T_0_i) → XYZ positions
        Plot these positions as connected lines (stick diagram)

        Confirm: does numpy come with waldo_env?
        waldo_env/bin/python -c "import numpy; print(numpy.__version__)"

- [ ] TASK-DH-05 — Konfirmasi findings ke user sebelum lanjut

---

## Phase 2 — Implementasi sub-tab struktur

- [ ] TASK-DH-06 — Restructure dh_tab_panel.py:
        Wrap existing Realtime content inside sub-tab structure:

        ui.tabs() with two tabs:
          tab1: "Realtime" (existing content, unchanged)
          tab2: "Eksperimen" (new content)

        Show diff — Realtime content must remain 100% identical.
        Wait for approval.

- [ ] TASK-DH-07 — User approves → Apply restructure
- [ ] TASK-DH-08 — Verify: Realtime tab still works, θ still updates,
        highlight still works, new Eksperimen tab visible

---

## Phase 3 — Implementasi tab Eksperimen

- [ ] TASK-DH-09 — Implement input grid in Eksperimen tab:
        Layout: table-like grid dengan header row + 6 joint rows

        Header: Joint | a (mm) | α (°) | d (mm) | θ (°)

        Per joint (6 rows):
          - Label: J1/J2/.../J6 (atau Base/Shoulder/Elbow/W1/W2/W3)
          - ui.number input untuk a, α, d, θ
          - Default values dari _DH_PARAMS (a, α, d)
            dan _DH_PARAMS home angles untuk θ
          - Step: a/d=1mm, α/θ=1°
          - Format: 2 desimal

        Buttons row di bawah grid:
          [Reset ke Default] [Plot Stick Diagram]

        Warning label di atas grid:
          "⚠ Mode Eksperimen: nilai ini tidak mencerminkan robot asli"

        Show diff. Wait for approval.

- [ ] TASK-DH-10 — User approves → Apply input grid
- [ ] TASK-DH-11 — Implement _compute_fk_positions() helper:
        Pure function (no UI), takes 6×4 DH params array,
        returns list of 7 XYZ positions (base + 6 joint frames)
        using Modified DH matrix multiplication via numpy.

        def _compute_fk_positions(dh_params: list[dict]) -> list[tuple]:
            # dh_params: list of {a, alpha_deg, d, theta_deg}
            # returns: [(x0,y0,z0), (x1,y1,z1), ..., (x6,y6,z6)]
            # position 0 = base frame origin

        Show implementation. Wait for approval.

- [ ] TASK-DH-12 — User approves → Apply _compute_fk_positions()
- [ ] TASK-DH-13 — Implement _plot_stick_diagram() helper:
        Opens matplotlib window with two subplots side by side:

        Left plot — Top View (XY plane):
          Title: "Top View (XY)"
          xlabel: "X (mm)", ylabel: "Y (mm)"
          Plot: connected line through all 7 positions (x,y)
          Mark joints: dots at each position
          Mark base: square marker at position 0
          Mark end-effector: star marker at position 6
          Aspect ratio: equal
          Grid: on

        Right plot — Side View (XZ plane):
          Title: "Side View (XZ)"
          xlabel: "X (mm)", ylabel: "Z (mm)"
          Same markers as left plot
          Aspect ratio: equal
          Grid: on

        Figure title: "Stick Diagram — DH Parameter Eksperimen"

        plt.show(block=False) — non-blocking so GUI stays responsive

        Show implementation. Wait for approval.

- [ ] TASK-DH-14 — User approves → Apply _plot_stick_diagram()
- [ ] TASK-DH-15 — Wire buttons:
        Reset button: restore all inputs to _DH_PARAMS defaults
        Plot button:
          1. Read all input values
          2. Call _compute_fk_positions()
          3. Call _plot_stick_diagram()
          4. Show ui.notify("Plot ditampilkan di window terpisah")

        Show diff for button wiring. Wait for approval.

- [ ] TASK-DH-16 — User approves → Apply button wiring
- [ ] TASK-DH-17 — Full test:
        [ ] Tab Eksperimen terbuka dengan grid input
        [ ] Semua nilai default sudah terisi dari _DH_PARAMS
        [ ] Ubah nilai a J1 → klik Plot → window matplotlib muncul
        [ ] Top view dan side view tampil berdampingan
        [ ] Reset → semua nilai kembali ke default
        [ ] Tab Realtime masih berfungsi normal (θ update, highlight)

---

## Phase 4 — Final verification

- [ ] TASK-DH-18 — Regression test:
        [ ] Tab DH di panel kiri masih berfungsi
        [ ] Sub-tab Realtime: θ update realtime, highlight kuning
        [ ] Sub-tab Eksperimen: input grid, plot, reset semua bekerja
        [ ] Kinematics panel (IK/FK) tidak terpengaruh
        [ ] Semua tab lain tidak terpengaruh

- [ ] TASK-DH-19 — Update TASKPLAN.md utama dengan summary

---

## Catatan teknis

### Modified DH transformation matrix
T_i = Rot_x(α) · Trans_x(a) · Rot_z(θ) · Trans_z(d)

Dalam bentuk matriks 4×4:
[cos θ,        -sin θ,        0,       a         ]
[sin θ cos α,   cos θ cos α,  -sin α,  -d sin α  ]
[sin θ sin α,   cos θ sin α,   cos α,   d cos α  ]
[0,             0,             0,       1         ]

### matplotlib backend
Dicek di TASK-DH-02. Backend yang berhasil dicatat di sini setelah investigasi.

### Default θ values untuk Eksperimen
Home position: [90, -90, 180, 0, 0, 180] derajat (J1-J6)

---

## Log perubahan
| Tanggal | Perubahan | Catatan |
|---------|-----------|---------|
| 2026-07-06 | File dibuat | DH Experiment tab — matplotlib stick diagram |
