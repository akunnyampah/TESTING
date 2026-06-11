# TASKPLAN_INSTRUCTIONS.md
# Instruksi Pembuatan dan Pemeliharaan Task Plan

Baca dokumen ini sebagai bagian dari setup awal.
Kamu WAJIB membuat dan memperbarui file `Agent/TASKPLAN.md` sepanjang project berlangsung.

---

## Apa yang harus kamu buat

Setelah membaca semua dokumen di folder `Agent/` dan mengeksplorasi
struktur folder `waldo_commander/`, buat file `Agent/TASKPLAN.md`
dengan format yang didefinisikan di bawah.

---

## Format TASKPLAN.md

```markdown
# TASKPLAN.md — Waldo Commander ROS 2 Integration
# Last updated: [tanggal dan waktu setiap kali diperbarui]

## Status keseluruhan
[PHASE 1 of 4] / [IN PROGRESS] / [BLOCKED: alasan]

---

## Phase 1 — Eksplorasi & verifikasi (tidak ada kode)

- [ ] TASK-01 — Baca Agent/CLAUDE.md
- [ ] TASK-02 — Baca Agent/PRD.md
- [ ] TASK-03 — Baca Agent/SKILL.md
- [ ] TASK-04 — Baca Agent/BrandGuidelines.md
- [ ] TASK-05 — Identifikasi file registrasi tab di waldo_commander/
- [ ] TASK-06 — Identifikasi file server route di waldo_commander/
- [ ] TASK-07 — Identifikasi mekanisme update 3D viewer
- [ ] TASK-08 — Identifikasi versi NiceGUI yang dipakai
- [ ] TASK-09 — Konfirmasi findings ke user sebelum lanjut

## Phase 2 — Setup struktur file baru

- [ ] TASK-10 — Buat folder waldo_commander/ros2/
- [ ] TASK-11 — Buat waldo_commander/ros2/__init__.py
- [ ] TASK-12 — Buat waldo_commander/ros2/config.py (workspace limits)
- [ ] TASK-13 — Buat waldo_commander/ros2/bridge.py (rclpy node + IK client)
- [ ] TASK-14 — Buat waldo_commander/ros2/rviz_launcher.py
- [ ] TASK-15 — Buat waldo_commander/ui/panels/ros2_panel.py (NiceGUI tab)

## Phase 3 — Integrasi ke Waldo

- [ ] TASK-16 — Tambah endpoint POST /api/ros/preview ke server
- [ ] TASK-17 — Tambah endpoint POST /api/ros/execute ke server
- [ ] TASK-18 — Tambah endpoint GET /api/ros/status ke server
- [ ] TASK-19 — Tambah endpoint POST /api/rviz/launch ke server
- [ ] TASK-20 — Tambah endpoint POST /api/rviz/close ke server
- [ ] TASK-21 — Tambah GET /api/rviz/status ke server
- [ ] TASK-22 — Daftarkan tab ROS 2 di titik integrasi (1 baris)

## Phase 4 — Verifikasi

- [ ] TASK-23 — Verifikasi tab Program masih berfungsi
- [ ] TASK-24 — Verifikasi tab I/O masih berfungsi
- [ ] TASK-25 — Verifikasi tab Settings masih berfungsi
- [ ] TASK-26 — Test Preview dengan koordinat valid → badge hijau
- [ ] TASK-27 — Test Preview dengan koordinat out of range → badge merah
- [ ] TASK-28 — Test tombol Eksekusi hanya aktif saat hijau
- [ ] TASK-29 — Test Launch RViz → window terbuka
- [ ] TASK-30 — Test Close RViz → window tertutup
- [ ] TASK-31 — Test Waldo berjalan normal tanpa ROS 2 aktif

---

## Temuan eksplorasi
[Diisi setelah Phase 1 selesai]

### File registrasi tab
- Path: [...]
- Cara menambahkan tab baru: [...]

### File server route
- Path: [...]
- Pattern yang digunakan: [...]

### Mekanisme update 3D viewer
- Method/function: [...]
- Cara memanggilnya: [...]

### NiceGUI version
- Versi: [...]

---

## Catatan blocker
[Kosong jika tidak ada blocker]

---

## Log perubahan
| Tanggal | Task selesai | Catatan |
|---------|--------------|---------|
| [date] | TASK-01 s/d TASK-04 | Semua dokumen Agent/ dibaca |
```

---

## Aturan pembaruan TASKPLAN.md

### Kapan harus diperbarui
- Setiap kali satu task selesai: ubah `- [ ]` menjadi `- [x]`
- Setiap kali menemukan blocker: catat di bagian "Catatan blocker"
- Setiap kali mengisi temuan eksplorasi: isi bagian "Temuan eksplorasi"
- Setiap sesi kerja baru: perbarui "Last updated" di baris kedua
- Setiap kali ada perubahan phase: perbarui "Status keseluruhan"

### Format task selesai
```
- [x] TASK-01 — Baca Agent/CLAUDE.md  ✓
```

### Format task blocked
```
- [!] TASK-13 — Buat bridge.py  ← BLOCKED: rclpy import error, lihat Catatan Blocker
```

### Format task in progress
```
- [~] TASK-16 — Tambah endpoint /api/ros/preview  ← sedang dikerjakan
```

---

## Aturan tambahan

1. **Jangan hapus task yang sudah selesai** — biarkan tetap ada dengan tanda `[x]`
   agar progress bisa dilacak secara penuh.

2. **Jika menemukan task baru** yang tidak ada di daftar (karena hasil eksplorasi),
   tambahkan dengan format `TASK-XX` di phase yang sesuai dan beri catatan
   mengapa task ini perlu ditambahkan.

3. **Setiap awal sesi baru**, baca `Agent/TASKPLAN.md` terlebih dahulu untuk
   mengetahui posisi progress saat ini sebelum melakukan apapun.

4. **Laporkan ke user** setiap kali satu phase selesai penuh, bukan setiap task.
   Kecuali ada blocker — blocker dilaporkan segera.
