# TASKPLAN_HELP_UPDATE_2.md — Help Panel Update Phase 2
# Last updated: 2026-07-06

## Status keseluruhan
[PHASE 4 of 4] / [COMPLETE]

## Konteks
Pembaruan lanjutan Help panel Waldo Commander berdasarkan review:
1. Quick Start — step 5 diganti, konten lebih rinci, gambar menggantikan video
2. Safety — hapus semua video placeholder, siapkan image placeholder
3. Setup folder asset dan path file untuk gambar/video

## Keputusan desain
- Bahasa: Indonesia sepenuhnya
- Gambar: static file PNG/JPG dari folder ~/Documents/help_assets/images/
- Video: tetap ada di Quick Start step 1 (Tentang Robot) dan step 6 (Cara Buka Help)
- Safety: tidak ada video placeholder — hanya image placeholder
- Quick Start step 2/3/4: tidak ada video placeholder — hanya image placeholder

## File yang akan disentuh
- waldo_commander/components/help_menu.py  ← semua perubahan konten
- TIDAK ada file lain yang disentuh

---

## Phase 1 — Setup folder asset dan naming convention

- [x] TASK-H2-01 — Buat folder struktur di ~/Documents/help_assets/:
        mkdir -p ~/Documents/help_assets/images
        mkdir -p ~/Documents/help_assets/videos

        Buat file README.md di ~/Documents/help_assets/ yang menjelaskan:
        - Naming convention file gambar
        - Naming convention file video
        - Cara menambahkan file ke GUI

- [x] TASK-H2-02 — Identifikasi semua nama file yang diperlukan:
        Quick Start images:
          qs_fk_vs_ik.png         — diagram FK vs IK (step 2)
          qs_dh_params.png        — ilustrasi parameter DH (step 3)
          qs_matriks_transform.png — matriks transformasi homogen (step 4)
          qs_iterasi_ik.png        — visualisasi iterasi IK (step 4)

        Quick Start videos:
          qs_tentang_robot.mp4    — video step 1 (Tentang Robot)
          qs_cara_buka_help.mp4   — video step 5 (Cara Buka Help) — opsional

        Safety images:
          safety_area_kerja.png   — persiapan area kerja (section A)
          safety_mode_robot.png   — perbedaan mode (section B)
          safety_jog_manual.png   — jog aman (section C)
          safety_estop.png        — E-STOP (section D)
          safety_recording.png    — recording aman (section E)
          safety_ik_fk.png        — IK/FK aman (section F)

- [x] TASK-H2-03 — Buat image placeholder helper yang membaca dari folder:
        Fungsi _build_image_placeholder(filename, caption) yang:
        - Cek apakah file ada di ~/Documents/help_assets/images/filename
        - Jika ADA: tampilkan gambar dengan ui.image()
        - Jika TIDAK ADA: tampilkan kotak abu-abu placeholder dengan:
            ui.card().classes("bg-gray-800 rounded-lg p-4 text-center my-2"):
                ui.icon("image", size="md").classes("text-gray-500")
                ui.label("🖼 Gambar akan ditambahkan").classes("text-gray-400 text-sm")
                ui.label(caption).classes("text-gray-500 text-xs italic")
                ui.label(f"File: {filename}").classes("text-gray-600 text-xs")

        Show diff. Wait for approval before applying.

- [x] TASK-H2-04 — Konfirmasi folder dan naming convention ke user
        Tunjukkan folder structure dan semua nama file yang akan digunakan.
        User bisa langsung menaruh file ke folder tersebut kapan saja.

---

## Phase 2 — Update Quick Start content

### Step 1: Tentang Robot Ini
- [x] TASK-H2-05 — Perluas konten step 1 agar lebih rinci untuk orang awam:
        Tambahkan penjelasan:
        - Apa itu robot arm 6 DOF (dengan analogi sederhana)
        - Mengapa 6 DOF (derajat kebebasan) — analogi lengan manusia
        - Stepper motor vs servo motor — perbedaan sederhana
        - Apa yang bisa dan tidak bisa dilakukan robot ini
        Video placeholder tetap ada (qs_tentang_robot.mp4)
        Show diff. Wait for approval.

### Step 2: Konsep Dasar FK vs IK
- [x] TASK-H2-06 — Ganti video placeholder → image placeholder:
        Remove: _build_video_placeholder("Demo FK vs IK...")
        Add: _build_image_placeholder("qs_fk_vs_ik.png",
             "Diagram perbandingan FK (kiri) dan IK (kanan)")

        Perluas konten teks:
        - Penjelasan lebih mendalam tentang FK (langkah demi langkah)
        - Penjelasan lebih mendalam tentang IK (mengapa lebih sulit)
        - Contoh konkret: "Jika J1=90°, J2=-90°, J3=180°... maka end-effector ada di..."
        - Mengapa IK bisa punya banyak solusi (analogi siku atas/bawah)
        Show diff. Wait for approval.

### Step 3: Parameter DH
- [x] TASK-H2-07 — Hapus video placeholder, tambah image placeholder:
        Remove: _build_video_placeholder("Tab DH Parameter realtime...")
        Add: _build_image_placeholder("qs_dh_params.png",
             "Ilustrasi parameter a, α, d, θ pada satu sendi")

        Perluas konten teks:
        - Penjelasan a, α, d, θ dengan analogi lebih mudah dipahami
        - Mengapa perlu 4 parameter (bukan 3 atau 6)
        - Cara membaca tabel DH — contoh dengan J1 robot ini
        - Catatan Modified DH vs Standard DH (untuk yang pakai buku)
        Show diff. Wait for approval.

### Step 4: Cara FK dan IK Dihitung
- [x] TASK-H2-08 — Hapus video placeholder, tambah 2 image placeholder:
        Remove: _build_video_placeholder("Visualisasi iterasi IK...")
        Add: _build_image_placeholder("qs_matriks_transform.png",
             "Struktur matriks transformasi homogen 4×4")
             _build_image_placeholder("qs_iterasi_ik.png",
             "Alur iterasi IK: tebak → FK → error → koreksi → ulang")

        Perluas konten teks FK:
        - Penjelasan matriks 4×4 lebih ramah orang awam
          (bagian rotasi 3×3 = "arah", bagian translasi = "posisi")
        - Contoh angka sederhana perkalian matriks

        Perluas konten teks IK:
        - Penjelasan Jacobian dengan analogi mudah
          ("Jacobian seperti peta: kalau sendi X bergerak 1°,
           end-effector pindah sejauh berapa mm ke arah mana?")
        - Kenapa iteratif (tidak bisa langsung)
        - Apa artinya "konvergen" dan "tidak konvergen"
        Show diff. Wait for approval.

### Step 5: Cara Membuka Panduan Kembali
- [x] TASK-H2-09 — GANTI step "Alur Sistem" dengan step baru:
        Judul: "Cara Membuka Panduan Kembali"
        Konten:
        - Icon ? di panel kiri bawah → klik untuk buka Help kapan saja
        - Penjelasan 4 tab yang tersedia:
            Keybindings: shortcut keyboard yang tersedia
            Quick Start: panduan dasar yang sedang dibaca ini
            Fitur GUI: penjelasan detail setiap fitur
            Safety: panduan keselamatan operasi robot
        - Tips: baca Safety sebelum mengoperasikan robot fisik
        - Tidak ada video, tidak ada image placeholder
        - Tombol Finish di step ini (step terakhir)
        Show diff. Wait for approval.

---

## Phase 3 — Update Safety tab

- [x] TASK-H2-10 — Hapus semua video placeholder di Safety:
        Remove _build_video_placeholder() dari semua 6 section Safety
        (Section A hingga F)
        Show diff. Wait for approval.

- [x] TASK-H2-11 — Tambah image placeholder di setiap Safety section:
        Section A: _build_image_placeholder("safety_area_kerja.png",
                   "Contoh area kerja yang aman")
        Section B: _build_image_placeholder("safety_mode_robot.png",
                   "Perbedaan tampilan mode Simulator dan Robot")
        Section C: _build_image_placeholder("safety_jog_manual.png",
                   "Indikator batas gerak sendi saat jog")
        Section D: _build_image_placeholder("safety_estop.png",
                   "Lokasi tombol E-STOP di GUI")
        Section E: _build_image_placeholder("safety_recording.png",
                   "Alur recording yang aman")
        Section F: _build_image_placeholder("safety_ik_fk.png",
                   "Badge IK dan warning FK")
        Show diff. Wait for approval.

---

## Phase 4 — Final verification

- [x] TASK-H2-12 — Verifikasi folder asset:
        ls ~/Documents/help_assets/images/
        ls ~/Documents/help_assets/videos/
        cat ~/Documents/help_assets/README.md

- [x] TASK-H2-13 — Verifikasi semua changes di Help dialog:
        [ ] Quick Start step 1: konten lebih rinci, video placeholder ada
        [ ] Quick Start step 2: image placeholder, konten diperluas
        [ ] Quick Start step 3: image placeholder, konten diperluas
        [ ] Quick Start step 4: 2 image placeholder, konten diperluas
        [ ] Quick Start step 5: "Cara Buka Help" (bukan Alur Sistem)
        [ ] Safety: tidak ada video placeholder, ada image placeholder
        [ ] Image placeholder menampilkan file jika ada, placeholder jika tidak
        [ ] Syntax OK, clean startup

- [x] TASK-H2-14 — Test image loading:
        Taruh satu file test (test.png) di ~/Documents/help_assets/images/
        Verifikasi bahwa gambar tampil menggantikan placeholder
        Hapus test.png → placeholder kembali

- [x] TASK-H2-15 — Update TASKPLAN.md utama

---

## Naming convention (untuk README)
| File | Digunakan di | Keterangan |
|------|-------------|------------|
| qs_fk_vs_ik.png | Quick Start step 2 | Diagram FK vs IK |
| qs_dh_params.png | Quick Start step 3 | Ilustrasi parameter DH |
| qs_matriks_transform.png | Quick Start step 4 | Matriks 4×4 |
| qs_iterasi_ik.png | Quick Start step 4 | Alur iterasi IK |
| qs_tentang_robot.mp4 | Quick Start step 1 | Video robot intro |
| safety_area_kerja.png | Safety section A | Area kerja aman |
| safety_mode_robot.png | Safety section B | Mode simulator vs robot |
| safety_jog_manual.png | Safety section C | Batas gerak jog |
| safety_estop.png | Safety section D | Lokasi E-STOP |
| safety_recording.png | Safety section E | Alur recording aman |
| safety_ik_fk.png | Safety section F | Badge IK dan warning FK |

### Fitur GUI (videos)
| File | Digunakan di | Keterangan |
|------|-------------|------------|
| fitur_mode_robot.mp4 | Fitur GUI: Mode Robot/Simulator | Toggle mode Robot vs Simulator |
| fitur_joint_jog.mp4 | Fitur GUI: Joint Jog | Demo Joint Jog — gerak tiap sendi |
| fitur_cartesian_jog.mp4 | Fitur GUI: Cartesian Jog | Demo Cartesian Jog — gerak dalam koordinat |
| fitur_jog_settings.mp4 | Fitur GUI: Jog Settings | Pengaturan speed, accel, step |
| fitur_program_editor.mp4 | Fitur GUI: Program/Editor | Membuat dan menjalankan program |
| fitur_io.mp4 | Fitur GUI: I/O | Kontrol I/O — relay dan sensor |
| fitur_ik.mp4 | Fitur GUI: IK | Demo IK — input koordinat, lihat sudut hasil |
| fitur_fk.mp4 | Fitur GUI: FK | Demo FK — input sudut, lihat koordinat hasil |
| fitur_dh_params.mp4 | Fitur GUI: DH Parameters | Tab DH Parameter — θ realtime |
| fitur_ros2_rviz.mp4 | Fitur GUI: ROS 2/RViz | RViz mirror — robot bergerak di GUI dan RViz |
| fitur_koneksi_robot.mp4 | Fitur GUI: Koneksi Robot | Langkah koneksi robot real — cek port, switch mode, verifikasi |

---

## Log perubahan
| Tanggal | Perubahan | Catatan |
|---------|-----------|---------|
| 2026-07-06 | File dibuat | Help update phase 2 |
| 2026-07-06 | TASKPLAN_HELP_UPDATE_2 complete | Quick Start 5 steps diperluas (orang awam) |
| 2026-07-06 | TASKPLAN_HELP_UPDATE_2 complete | Safety tab: video → image placeholder |
| 2026-07-06 | TASKPLAN_HELP_UPDATE_2 complete | assets/help/ folder di repo untuk gambar & video |
| 2026-07-06 | TASKPLAN_HELP_UPDATE_2 complete | _build_image_placeholder() + _build_video_placeholder() upgrade |
