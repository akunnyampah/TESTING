# TASKPLAN_UI_REDESIGN_2.md — UI Redesign Phase 2 (Poin 5–6)
# Last updated: 2026-07-01

## Status keseluruhan
[PHASE 1 of 4] / [IN PROGRESS — starting header changes]

## Konteks
Redesign UI Waldo Commander — poin 5 dan 6.
Menyentuh file Waldo existing yang sensitif (main.py, control.py, theme.py).
Dikerjakan TERPISAH dan SETELAH poin 1–4 selesai dan stabil.

## Non-destructive rules (MANDATORY)
- Show diff before EVERY change, wait for approval before applying
- Jika ada yang rusak — git checkout file tersebut, investigasi dulu
- Perubahan sekecil mungkin — jangan refactor, hanya ubah yang diperlukan
- Test setelah SETIAP perubahan sebelum lanjut ke task berikutnya

---

## Phase 0 — Layout expansion (new point from user)

- [x] TASK-V00A — Investigate current width of:
        1. Left panel (tabs: Program, I/O, ROS 2, DH) — current width
        2. Kinematics panel (IK/FK) — current width
        3. Jog panel (Joint Jog/Cartesian Jog) — current width (400px confirmed)
        Find: what controls their width, what is the available space
        now that 3D viewer only occupies bottom-left 50vw × 50vh

- [x] TASK-V00B — Program + DH tabs: per-tab inline style approach
        main.py: ui.tab_panel("program") → width: calc(50vw - 70px); height: calc(50vh - 24px)
        main.py: ui.tab_panel("dh") → width: calc(50vw - 70px)
        I/O dan ROS 2 tabs tidak disentuh — tetap compact

- [x] TASK-V00C — Readout + Kinematics+Jog wrapper width set
        readout.py:239: overlay card → width: calc(50vw - 24px)
        main.py:879: overlay-br wrapper column → width: calc(50vw - 24px)
        control.py:1546: Jog tab_panels → width: 100% (was 400px)

- [x] TASK-V00D — Layout balanced, no gaps
        Per-tab approach: global container tidak disentuh, tidak ada regresi I/O/ROS2

- [x] TASK-V00E — Verified by user: panels sejajar, no overlap

---

## Phase 1 — Investigasi (tidak ada kode)

- [ ] TASK-V01 — Identifikasi lokasi teks "PAROL6" di header/status bar kanan atas:
        grep -rn "PAROL6\|parol6" waldo_commander/main.py
        grep -rn "PAROL6\|parol6" waldo_commander/ui/ --include="*.py"
        Catat: file dan line number yang menampilkan nama di header

- [ ] TASK-V02 — Identifikasi lokasi X/Y/Z/Rx/Ry/Rz display di header kanan atas:
        Cari bagian yang merender angka koordinat di pojok kanan atas
        Catat: ukuran font saat ini, classes yang digunakan

- [ ] TASK-V03 — Identifikasi lokasi Digital I/O display di header:
        Cari DI1, DI2, DO1, DO2 di kode
        Catat: bagaimana digital input/output dirender

- [ ] TASK-V04 — Identifikasi struktur tombol Jog (Joint + Cartesian):
        Cari kode yang merender tombol +/- untuk setiap joint
        Catat: ukuran current (classes Tailwind yang dipakai)

- [ ] TASK-V05 — Konfirmasi findings sebelum lanjut

---

## Phase 2 — Poin 5: Header kanan atas

### 5a: Ukuran font X/Y/Z seragam

- [ ] TASK-V06 — Identifikasi perbedaan ukuran font antar X, Y, Z, Rx, Ry, Rz
        (mungkin X/Y/Z lebih besar dari Rx/Ry/Rz atau sebaliknya)
- [ ] TASK-V07 — Show diff: samakan ukuran font semua 6 nilai
        (show diff → wait for approval → apply)
- [ ] TASK-V08 — Verifikasi: semua 6 nilai tampil dengan ukuran sama

### 5b: Sembunyikan Digital Input, hanya tampilkan DO1 dan DO2

- [ ] TASK-V09 — Show diff: sembunyikan DI1, DI2, pertahankan DO1, DO2
        (show diff → wait for approval → apply)
- [ ] TASK-V10 — Verifikasi: header hanya menampilkan DO1 dan DO2

### 5c: Ubah "PAROL6" → "ROBOT" di header

- [ ] TASK-V11 — Show diff: ganti teks di lokasi yang ditemukan TASK-V01
        Hanya di header/status bar kanan atas — tidak di tempat lain
        (show diff → wait for approval → apply)
- [ ] TASK-V12 — Verifikasi: header menampilkan "ROBOT" bukan "PAROL6"
        Pastikan tidak ada tempat lain yang ikut berubah

---

## Phase 3 — Poin 6: Perbesar tombol Jog

- [ ] TASK-V13 — Analisis: berapa ukuran yang tepat?
        Bandingkan ukuran current dengan target
        Proposal: naikkan padding dan font size satu level Tailwind
        (misal: dari py-1 px-2 text-sm → py-2 px-3 text-base)

- [ ] TASK-V14 — Show diff untuk tombol Joint Jog
        (show diff → wait for approval → apply)

- [ ] TASK-V15 — Verifikasi Joint Jog: tombol lebih besar, masih berfungsi

- [ ] TASK-V16 — Show diff untuk tombol Cartesian Jog
        (show diff → wait for approval → apply)

- [ ] TASK-V17 — Verifikasi Cartesian Jog: tombol lebih besar, masih berfungsi

---

## Final verification

- [ ] TASK-V18 — Full regression test:
        [ ] Layout Phase 0: semua panel expanded, tidak overlap
        [ ] Header X/Y/Z/Rx/Ry/Rz: semua ukuran sama
        [ ] Header I/O: hanya DO1 dan DO2 tampil
        [ ] Header nama: "ROBOT" (bukan "PAROL6")
        [ ] Joint Jog: tombol lebih besar, semua fungsi normal
        [ ] Cartesian Jog: tombol lebih besar, semua fungsi normal
        [ ] Recording masih berfungsi (jog tombol yang diperbesar)
        [ ] Semua fitur dari TASKPLAN_UI_REDESIGN_1 masih berfungsi

- [ ] TASK-V19 — Update TASKPLAN.md utama dengan summary perubahan

---

## Catatan risiko

| Task | Risiko | Mitigasi |
|------|--------|----------|
| TASK-V00B (expand left panel) | Panel overflow atau overlap 3D viewer | Measure space first (TASK-V00A), test after apply |
| TASK-V00C (expand right panels) | Fixed-width panels tidak responsive | Check Jog panel min-width constraint (400px) |
| TASK-V11 (ganti PAROL6) | Nama mungkin dipakai di logika backend, bukan hanya display | Grep dulu, ubah hanya di UI layer |
| TASK-V14/V16 (perbesar Jog) | Tombol lebih besar bisa menggeser layout Jog panel | Test layout di fullscreen setelah apply |
| TASK-V09 (sembunyikan DI) | DI mungkin terkait dengan logika lain | Hanya sembunyikan di UI, jangan hapus logika |

---

## Log perubahan
| Tanggal | Perubahan | Catatan |
|---------|-----------|---------|
| 2026-06-29 | File dibuat | Poin 5-6 UI redesign, dikerjakan setelah poin 1-4 |
| 2026-07-01 | Phase 0 ditambahkan | Layout expansion — prerequisite sebelum Phase 1-3 |
| 2026-07-01 | Phase numbering diupdate | Old Phase 1→2, Phase 2→3, Phase 3→4 |
| 2026-07-01 | Phase 0 complete — layout expansion | 3D viewer: 50vw × 50vh bottom-left |
| | | Program/DH tabs: calc(50vw - 70px) width (main.py per-tab) |
| | | Readout/Kinematics/Jog wrapper: calc(50vw - 24px) width |
| | | Jog panel: 400px → 100% width (control.py:1546) |
