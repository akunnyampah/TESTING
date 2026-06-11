# CLAUDE.md — Waldo Commander ROS 2 Integration

Dokumen ini adalah instruksi wajib untuk Claude Code saat bekerja di project ini.
Baca seluruh dokumen ini sebelum menulis satu baris kode pun.

---

## Konteks project

Kamu sedang menambahkan fitur integrasi ROS 2 ke Waldo Commander — sebuah web GUI Python
berbasis **NiceGUI** untuk mengontrol robot arm PAROL6.

Repo asli: https://github.com/Jepson2k/Waldo-Commander

**Yang kamu kerjakan hanya fitur tambahan. Seluruh kode Waldo yang sudah ada
harus tetap berfungsi persis seperti sebelumnya.**

---

## Aturan absolut — jangan dilanggar

### 1. NON-DESTRUCTIVE FIRST
- **Jangan mengubah file Waldo yang sudah ada**, kecuali satu tempat integrasi
  yang sudah didefinisikan di PRD (menambahkan import + satu baris registrasi tab).
- Jika ragu apakah sebuah perubahan akan merusak sesuatu — jangan lakukan.
  Tanyakan atau cari cara lain yang tidak menyentuh kode existing.
- Sebelum mengedit file apapun yang sudah ada, baca isinya dulu secara menyeluruh.

### 2. MODULAR — semua kode baru di folder terpisah
Semua kode baru harus berada di:
```
waldo_commander/ros2/          ← logika ROS 2 dan bridge
waldo_commander/ui/panels/ros2_panel.py   ← NiceGUI UI tab
```
Jangan menyebarkan kode baru ke file-file yang sudah ada di luar dua lokasi ini.

### 3. GRACEFUL DEGRADATION wajib
Setiap fungsi yang menyentuh ROS 2 harus dibungkus try/except.
Jika ROS 2 tidak tersedia, Waldo harus tetap berjalan normal — hanya tab ROS 2
yang menampilkan pesan "ROS 2 tidak tersedia".

Contoh pola wajib:
```python
try:
    import rclpy
    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False
```

### 4. JANGAN MENGUBAH UI YANG SUDAH ADA
- Tidak mengubah layout, warna, font, atau komponen NiceGUI yang sudah ada
- Tidak menghapus atau memindahkan elemen UI existing
- Tab baru mengikuti style dark theme yang sudah ada — tidak mengimpor CSS baru
- Jika perlu referensi style, lihat cara komponen dibuat di file panel lain yang sudah ada

### 5. THREAD SAFETY untuk rclpy
rclpy bersifat blocking. Waldo menggunakan asyncio. Wajib jalankan
ROS 2 spin di thread daemon terpisah:
```python
import threading
spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
spin_thread.start()
```
Jangan pernah memanggil `rclpy.spin()` langsung di event loop asyncio.

---

## Cara kerja Waldo Commander (pahami ini dulu)

- Framework UI: **NiceGUI** (Python) — bukan HTML/JS murni
- Server: **aiohttp** atau framework async Python yang sudah ada di Waldo
- Backend robot: abstraksi **waldoctl** — jangan disentuh
- Tab panel kiri dibuat dengan NiceGUI `ui.tabs` / `ui.tab_panel`
- 3D viewer adalah komponen custom Waldo — untuk update pose, gunakan
  mekanisme yang sudah ada, jangan buat viewer baru

---

## Alur kerja yang diharapkan

Sebelum menulis kode apapun:
1. Baca `PRD.md` — pahami scope dan requirements
2. Baca `BrandGuidelines.md` — pahami aturan visual
3. Explore struktur folder `waldo_commander/` untuk memahami pola yang ada
4. Identifikasi file registrasi tab yang perlu ditambah satu baris import
5. Buat plan implementasi, konfirmasi dengan user sebelum mulai coding

Urutan implementasi yang benar:
1. `waldo_commander/ros2/config.py` — konfigurasi workspace limits
2. `waldo_commander/ros2/bridge.py` — ROS 2 node dan logika IK
3. `waldo_commander/ros2/rviz_launcher.py` — subprocess RViz
4. `waldo_commander/ros2/__init__.py` — exports
5. Endpoint baru di server Waldo (file yang tepat didentifikasi saat explore)
6. `waldo_commander/ui/panels/ros2_panel.py` — NiceGUI tab content
7. Satu baris registrasi tab di file existing yang tepat
8. Testing: pastikan semua tab lama masih berfungsi

---

## Referensi file penting di repo Waldo

Sebelum coding, explore dan pahami file-file ini:
- `waldo_commander/ui/` — struktur panel dan tab existing
- `waldo_commander/server.py` atau setara — tempat mendaftarkan route
- `pyproject.toml` — dependencies yang sudah ada
- `CLAUDE.md` di repo asli Waldo — ada instruksi dari maintainer asli

---

## Cara melaporkan blocker

Jika menemukan situasi di mana satu-satunya cara mengimplementasikan fitur
adalah dengan mengubah file existing secara signifikan, **jangan langsung lakukan**.
Laporkan temuannya ke user dengan:
1. File mana yang perlu diubah
2. Perubahan apa yang diperlukan
3. Risiko yang mungkin timbul
4. Alternatif yang lebih aman jika ada

---

## Hal-hal yang tidak boleh dilakukan

- `pip install` library baru tanpa konfirmasi user
- Mengubah `pyproject.toml` dependencies tanpa konfirmasi
- Menghapus atau mengganti nama file yang sudah ada
- Mengubah konfigurasi waldoctl atau PAROL6 backend
- Membuat 3D viewer baru atau mengganti renderer yang sudah ada
- Mengubah routing/URL yang sudah ada di Waldo server
- Menambahkan middleware atau interceptor ke server Waldo
