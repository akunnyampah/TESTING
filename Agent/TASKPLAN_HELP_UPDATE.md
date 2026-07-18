# TASKPLAN_HELP_UPDATE.md — Help Panel Update
# Last updated: 2026-07-06

Dilanjutkan di TASKPLAN_HELP_UPDATE_2.md untuk konten lebih rinci

## Status keseluruhan
[COMPLETE — dilanjutkan di phase 2]

## Konteks
Update tab Help di Waldo Commander:
1. Fix layout Keybindings (terlalu kecil)
2. Update Quick Start dengan konten dari Draft_untuk_dimasukan_ke_user_guide.docx
3. Tambah tab baru "Fitur GUI" dari Draft_penjelasan_fitur_GUI.odt
4. Tambah tab baru "Safety" dari Draft_Safety.odt

Urutan tab Help: Keybindings | Quick Start | Fitur GUI | Safety
Styling: card/accordion/highlight — rapi, bukan teks mentah
Video placeholder: buat layout kosong siap diisi video nanti

## Non-destructive rules (MANDATORY)
- Hanya menyentuh file Help panel dan file terkait Help
- Show diff before every change, wait for approval
- Jangan ubah logika/fungsi lain yang sudah berjalan

## File yang akan disentuh
- waldo_commander/components/help_menu.py  ← semua perubahan Help
- waldo_commander/common/theme.py          ← CSS jika perlu (sizing)
- Tidak ada file lain yang disentuh

---

## Phase 1 — Investigasi (tidak ada kode)

- [ ] TASK-H01 — Temukan file help panel yang ada sekarang:
        grep -rn "help\|Help\|keybinding\|Keybinding" \
        waldo_commander/ --include="*.py" | grep -v ".pyc" | head -20

- [ ] TASK-H02 — Tampilkan struktur tab Help saat ini (full file content)

- [ ] TASK-H03 — Identifikasi masalah layout Keybindings:
        Mengapa terlalu kecil? Apakah ada fixed width/height?
        Apa yang perlu diubah agar pas dengan isinya?

- [ ] TASK-H04 — Identifikasi cara menambah tab baru di Help panel:
        Apakah pakai ui.tabs() yang sama? Atau struktur berbeda?

- [ ] TASK-H05 — Konfirmasi findings ke user sebelum lanjut

---

## Phase 2 — Fix Keybindings layout

- [ ] TASK-H06 — Show diff: perbaiki layout Keybindings agar pas dengan isinya
        (remove fixed width/height, tambah scroll jika perlu,
        pastikan tabel/list keybinding tidak terpotong)
- [ ] TASK-H07 — User approves diff
- [ ] TASK-H08 — Apply fix Keybindings
- [ ] TASK-H09 — Verifikasi: Keybindings tab tampil penuh tidak terpotong

---

## Phase 3 — Update Quick Start

- [ ] TASK-H10 — Buat konten Quick Start dari Draft_untuk_dimasukan_ke_user_guide.docx:
        Konten mencakup:
        - Tentang Robot Ini (intro, fungsi, mode operasi)
        - Konsep Dasar FK vs IK (dengan analogi)
        - Parameter DH (tabel a/α/d/θ actual robot)
        - Matriks Transformasi Homogen
        - Cara FK dihitung
        - Cara IK dihitung (iteratif/numerik via Pinocchio)
        - Tabel DH aktual robot
        - Alur sistem GUI → ROS 2 → RViz
        Styling: section card per topik, tabel untuk DH params,
        highlight untuk poin penting

- [ ] TASK-H11 — Show full Quick Start implementation, wait for approval
- [ ] TASK-H12 — Apply Quick Start update
- [ ] TASK-H13 — Verifikasi: semua section tampil, tabel DH benar

---

## Phase 4 — Tambah tab Fitur GUI

- [ ] TASK-H14 — Buat konten tab "Fitur GUI" dari Draft_penjelasan_fitur_GUI.odt:
        Konten mencakup 9 fitur:
        0. Robot/Simulator Toggle
        1. Joint Jog
        2. Cartesian Jog
        3. Jog Settings
        4. Program/Editor
        5. I/O
        6. Inverse Kinematics (IK)
        7. Forward Kinematics (FK)
        8. DH Parameters
        9. ROS 2 — Launch RViz
        Styling: accordion per fitur (expand/collapse),
        video placeholder berupa kotak abu-abu dengan teks
        "📹 Video akan ditambahkan" untuk setiap 🎥 marker

- [ ] TASK-H15 — Show full Fitur GUI implementation, wait for approval
- [ ] TASK-H16 — Apply tab Fitur GUI
- [ ] TASK-H17 — Verifikasi: semua 9 fitur tampil, accordion berfungsi,
        video placeholder terlihat

---

## Phase 5 — Tambah tab Safety

- [ ] TASK-H18 — Buat konten tab "Safety" dari Draft_Safety.odt:
        Konten mencakup 6 section:
        A. Sebelum Mulai
        B. Robot vs Simulator
        C. Saat Jog Manual
        D. E-STOP
        E. Recording / Program
        F. Saat Pakai IK / FK
        Styling: card per section, warning color (amber/red)
        untuk poin kritis, video placeholder sama seperti Fitur GUI

- [ ] TASK-H19 — Show full Safety implementation, wait for approval
- [ ] TASK-H20 — Apply tab Safety
- [ ] TASK-H21 — Verifikasi: semua 6 section tampil dengan styling warning

---

## Phase 6 — Modifikasi first_time_dialog (auto-show sudah ada)

Note: first_time_dialog sudah ada di help_menu.py dengan mekanisme
"Don't show again" via app.storage.general[FIRST_VISIT_KEY].
Phase 6 mengubah storage ke app.storage.user (per-browser-session)
dan memperluas konten dialog dengan Fitur GUI + Safety.

REVISED: Use app.storage.user instead of app.storage.browser.
Reason: app.storage.browser requires storage_secret in ui.run()
AND is read-only after HTTP response — silent write failure.
app.storage.user is per-browser-session (same per-device behavior),
writable anytime, recommended by NiceGUI for this exact pattern.

Two changes needed:
1. Add storage_secret to ui.run() in main.py (required for
   app.storage.user too)
2. Change FIRST_VISIT_KEY storage from app.storage.general
   to app.storage.user in help_menu.py

Investigation found: create_first_time_dialog() already exists
with "Don't show again" backed by app.storage.general[FIRST_VISIT_KEY].

Approach: modify first_time_dialog to include Fitur GUI and Safety
content — same stepper or tab structure, reuse existing mechanism.

- [ ] TASK-H23 — Show full create_first_time_dialog() implementation:
        grep -n "create_first_time_dialog\|FIRST_VISIT_KEY\|first_visit\|first_time" \
        waldo_commander/components/help_menu.py | head -20
        Show full function content.

- [ ] TASK-H24 — Decide: should first_time_dialog show the same
        content as the new Help tabs (Fitur GUI + Safety), or
        should it remain as a separate onboarding flow?
        Show current first_time_dialog content to user for decision.

- [ ] TASK-H25 — Show diff: add Fitur GUI and Safety to
        first_time_dialog (reuse existing "don't show again" mechanism)
        Wait for approval.

- [ ] TASK-H26 — Apply changes to first_time_dialog

- [ ] TASK-H27 — Change storage from app.storage.general to
        app.storage.user for FIRST_VISIT_KEY:
        1. Add storage_secret to ui.run() in main.py
        2. Change FIRST_VISIT_KEY reads/writes in help_menu.py
           to app.storage.user
        Show diff. Wait for approval. Apply.

- [ ] TASK-H28 — Verify:
        [ ] Fresh browser session: first_time_dialog muncul otomatis
        [ ] Centang "don't show again" → refresh → tidak muncul
        [ ] Browser/session lain: muncul lagi (per-browser-session storage)

---

## Phase 7 — Final verification

- [ ] TASK-H29 — Full regression test:
        [ ] Tab Keybindings: layout pas, tidak terpotong
        [ ] Tab Quick Start: semua section tampil, tabel DH benar
        [ ] Tab Fitur GUI: 9 fitur dengan accordion + video placeholder
        [ ] Tab Safety: 6 section dengan warning styling
        [ ] Urutan tab: Keybindings | Quick Start | Fitur GUI | Safety
        [ ] Tab lain di Waldo tidak terpengaruh
        [ ] Fresh session: Help tab auto-open
        [ ] After "don't show": default tab opens instead
        [ ] Checkbox visible di semua tab Help

- [ ] TASK-H30 — Update TASKPLAN.md utama dengan summary perubahan

---

## Catatan konten

### Video placeholder format
Setiap 🎥 marker di draft diganti dengan:
  ui.card().classes("bg-gray-800 rounded p-4 text-center"):
      ui.icon("videocam", size="lg").classes("text-gray-500")
      ui.label("Video akan ditambahkan").classes("text-gray-400 text-sm")
      ui.label("[deskripsi video]").classes("text-gray-500 text-xs")

### Styling guide
- Section header: text-base font-semibold dengan border-b
- Konten: text-sm dengan line-height cukup
- Tabel: border, alternating row color
- Warning/poin kritis: bg-amber-900/20 border-l-4 border-amber-500
- Accordion: ui.expansion() per fitur/section

---

## Log perubahan
| Tanggal | Perubahan | Catatan |
|---------|-----------|---------|
| 2026-07-06 | File dibuat | Help panel update — 4 tab |
| 2026-07-06 | Tambah Phase 6 | Auto-show Help + don't show again checkbox |
