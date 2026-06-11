# Product Requirements Document
# Waldo Commander — ROS 2 XYZ Target Integration

**Version:** 1.0  
**Status:** Draft  
**Project type:** Feature addition (non-destructive)

---

## 1. Latar belakang

Waldo Commander adalah web GUI berbasis NiceGUI (Python) untuk mengontrol robot arm PAROL6. GUI sudah berjalan baik dengan fitur 3D viewer, jog controls, program editor, I/O panel, dan simulator mode.

Project ini menambahkan integrasi ROS 2 melalui pendekatan **WebSocket/REST Bridge** (Opsi 2) — yaitu menambahkan endpoint baru di Waldo Server dan tab baru di panel kiri GUI, tanpa mengubah fitur yang sudah ada.

---

## 2. Tujuan

Menambahkan fitur input koordinat target X, Y, Z melalui GUI Waldo Commander, yang kemudian:
1. Dikirim ke ROS 2 untuk komputasi inverse kinematics via MoveIt 2
2. Divalidasi keamanannya (workspace limit + IK reachability)
3. Ditampilkan preview di 3D viewer Waldo sebelum eksekusi
4. Menampilkan indikator visual hijau (aman) atau merah (tidak aman / out of range)
5. Dieksekusi ke robot / simulator jika pengguna mengkonfirmasi

---

## 3. Scope

### 3.1 In scope
- Penambahan tab baru **"ROS 2"** di panel kiri Waldo Commander (sejajar Program, I/O, Settings)
- Penambahan endpoint backend: `POST /api/ros/preview`, `POST /api/ros/execute`, `GET /api/ros/status`, `POST /api/rviz/launch`, `POST /api/rviz/close`
- Modul baru `ros2_bridge.py` (rclpy node, IK service client, safety checker)
- Tombol **"Launch RViz"** dan **"Close RViz"** di dalam tab ROS 2
- Safety validation: workspace bounding box + IK success check dari MoveIt 2
- Preview joint angles dari hasil IK ditampilkan di 3D viewer Waldo yang sudah ada
- Badge status: hijau (pose aman) / merah (pose tidak aman atau IK gagal)
- Tab Gripper : Pneumatic tetap ada dan tidak diubah

### 3.2 Out of scope
- Perubahan apapun pada tab Jog, Program, I/O, Settings
- Perubahan pada 3D viewer engine Waldo
- Perubahan pada waldoctl backend atau PAROL6 driver
- Implementasi ulang kinematics (menggunakan MoveIt 2 yang sudah ada)
- UI redesign atau perubahan tema/warna existing Waldo
- Fitur trajectory recording via ROS 2

---

## 4. Pengguna dan use case

**Pengguna utama:** Operator robot yang sudah familiar dengan Waldo Commander.

### Use case UC-01: Preview koordinat target
```
Sebagai operator,
Saya ingin memasukkan koordinat X, Y, Z target,
Agar saya bisa melihat apakah pose tersebut aman dan dapat dicapai robot
sebelum robot benar-benar bergerak.
```

### Use case UC-02: Eksekusi gerakan
```
Sebagai operator,
Setelah melihat preview pose yang valid (hijau),
Saya ingin menekan tombol Eksekusi
Agar robot bergerak ke koordinat target tersebut.
```

### Use case UC-03: Penolakan pose tidak aman
```
Sebagai operator,
Ketika saya memasukkan koordinat di luar jangkauan robot,
Saya ingin mendapat indikator merah beserta pesan alasan
Agar robot tidak mencoba bergerak ke posisi yang berbahaya.
```

### Use case UC-04: Launch RViz untuk monitoring
```
Sebagai operator,
Saya ingin membuka RViz langsung dari GUI
Tanpa harus membuka terminal terpisah,
Agar saya dapat memonitor data ROS 2 secara visual.
```

---

## 5. Functional requirements

### FR-01: Tab ROS 2
- Tab baru bernama **"ROS 2"** ditambahkan di panel kiri Waldo Commander
- Tab muncul di posisi setelah tab I/O (atau di akhir urutan tab yang ada)
- Tab ini berdiri sendiri dan tidak bergantung pada konfigurasi tool/backend Waldo
- Tab yang sudah ada (Program, I/O, Gripper, Settings) tidak berubah sama sekali

### FR-02: Form input koordinat
- Tiga input field numerik: **X**, **Y**, **Z** (satuan: meter, step: 0.001)
- Nilai default: X=0.3, Y=0.0, Z=0.4 (posisi aman tengah workspace)
- Tombol **"Preview"** — mengirim request ke bridge, menunggu respons
- Input harus menolak nilai non-numerik

### FR-03: Safety validation
- Validasi dilakukan di `ros2_bridge.py`, bukan di frontend
- Dua lapisan validasi:
  1. **Workspace bounding box** — koordinat harus dalam batas aman yang dikonfigurasi
  2. **IK reachability** — MoveIt 2 harus berhasil menemukan solusi joint angles
- Jika salah satu gagal, status = error + alasan ditampilkan

### FR-04: Indikator status visual
- Badge **hijau** + teks "Pose dapat dicapai" jika validasi sukses
- Badge **merah** + teks alasan kegagalan jika validasi gagal
- Status badge hanya muncul setelah tombol Preview ditekan
- Status di-reset ketika nilai input X/Y/Z diubah

### FR-05: Preview di 3D viewer
- Jika status hijau, joint angles hasil IK dikirim ke 3D viewer Waldo yang sudah ada
- 3D viewer menampilkan pose target (bukan eksekusi — hanya preview visual)
- Menggunakan mekanisme update viewer yang sudah ada di Waldo, tidak membuat renderer baru

### FR-06: Eksekusi
- Tombol **"Eksekusi"** hanya aktif (enabled) ketika status badge = hijau
- Saat diklik, mengirim perintah gerakan ke robot/simulator via Waldo backend
- Setelah eksekusi dikirim, tombol Eksekusi kembali disabled hingga Preview dijalankan ulang

### FR-07: Tombol RViz
- Tombol **"Launch RViz"** — membuka proses RViz sebagai window terpisah
- Jika RViz sudah berjalan, tombol berubah menjadi **"Close RViz"**
- Jika RViz ditutup dari luar (user close window), status tombol kembali ke "Launch RViz"
- Jika ROS 2 tidak tersedia, tombol menampilkan pesan error yang jelas

---

## 6. Non-functional requirements

### NFR-01: Non-destructive
- **Zero perubahan** pada file-file existing Waldo Commander yang sudah berjalan
- Semua kode baru berada dalam file/modul baru yang terpisah
- Integrasi ke Waldo dilakukan hanya dengan menambahkan import dan satu baris registrasi tab

### NFR-02: Graceful degradation
- Jika ROS 2 tidak terinstall atau tidak berjalan: tab ROS 2 tetap muncul di GUI, namun menampilkan pesan "ROS 2 tidak tersedia" yang jelas — Waldo tetap berfungsi normal
- Jika MoveIt 2 tidak berjalan: tombol Preview menampilkan error, tidak crash

### NFR-03: Response time
- Tombol Preview harus memberikan feedback loading (spinner atau disabled state) segera saat diklik
- Response dari IK service diharapkan < 3 detik untuk pose normal

### NFR-04: Konsistensi visual
- Tab ROS 2 mengikuti style dark theme Waldo Commander yang sudah ada
- Tidak mengimpor library CSS atau font baru
- Komponen UI menggunakan NiceGUI components yang sama dengan yang dipakai Waldo

---

## 7. Arsitektur teknis

### 7.1 Komponen baru yang dibuat

```
waldo_commander/
├── ros2/                          ← folder baru, semua kode ROS 2
│   ├── __init__.py
│   ├── bridge.py                  ← rclpy node, IK client, safety checker
│   ├── config.py                  ← workspace limits, parameter konfigurasi
│   └── rviz_launcher.py           ← subprocess management untuk RViz
└── ui/
    └── panels/
        └── ros2_panel.py          ← NiceGUI tab content untuk tab ROS 2
```

### 7.2 Endpoint baru di Waldo Server

| Method | Endpoint | Fungsi |
|--------|----------|--------|
| POST | `/api/ros/preview` | Jalankan IK + safety check, kembalikan joint angles + status |
| POST | `/api/ros/execute` | Kirim perintah eksekusi ke robot via Waldo backend |
| GET | `/api/ros/status` | Cek apakah ROS 2 bridge aktif |
| POST | `/api/rviz/launch` | Buka proses RViz |
| POST | `/api/rviz/close` | Tutup proses RViz |
| GET | `/api/rviz/status` | Cek apakah RViz sedang berjalan |

### 7.3 Integrasi ke Waldo

Satu-satunya modifikasi ke kode Waldo yang sudah ada adalah **menambahkan satu import dan satu pemanggilan fungsi** di file yang mendaftarkan tab panel (akan diidentifikasi saat implementasi). Tidak ada perubahan logika existing.

---

## 8. Konfigurasi workspace

Workspace bounding box robot dikonfigurasi di `ros2/config.py` dan dapat disesuaikan tanpa mengubah kode:

```
WORKSPACE_LIMITS = {
    "x": (-0.6, 0.6),   # meter
    "y": (-0.6, 0.6),   # meter  
    "z": (0.0, 0.9),    # meter (tidak boleh di bawah meja)
}
```

---

## 9. Definisi selesai (Definition of Done)

- [ ] Tab "ROS 2" muncul di panel kiri Waldo tanpa error
- [ ] Input X/Y/Z menerima nilai numerik dengan benar
- [ ] Tombol Preview memanggil ROS 2 IK dan menampilkan status hijau/merah
- [ ] Pose aman ditampilkan di 3D viewer Waldo
- [ ] Tombol Eksekusi hanya aktif saat status hijau
- [ ] Eksekusi berhasil menggerakkan robot/simulator
- [ ] Tombol Launch/Close RViz berfungsi
- [ ] Semua tab dan fitur Waldo yang sudah ada tetap berfungsi normal
- [ ] Jika ROS 2 tidak aktif, Waldo tetap bisa dijalankan tanpa error

---

## 10. Risiko dan mitigasi

| Risiko | Kemungkinan | Mitigasi |
|--------|-------------|----------|
| rclpy blocking asyncio Waldo | Tinggi | Jalankan ROS 2 spin di thread terpisah |
| RViz tidak terbuka (env ROS 2 belum di-source) | Sedang | Tambahkan PATH ROS 2 eksplisit di subprocess, tampilkan pesan error jelas |
| MoveIt 2 belum berjalan saat Preview diklik | Sedang | Try/except pada service call, tampilkan error di badge |
| Perubahan tidak sengaja mempengaruhi tab lain | Rendah | Semua kode baru di modul terpisah, review diff sebelum commit |
