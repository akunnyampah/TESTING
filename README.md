# Robot Arm 6 DOF GUI

Antarmuka berbasis browser untuk mengendalikan robot arm 6 DOF (PAROL6) dengan motor stepper, dilengkapi panel Kinematika (IK & FK), editor program, integrasi ROS 2, dan panduan pembelajaran interaktif.

---

## Fitur Utama

- **Joint Jog & Cartesian Jog** — kendali manual per-sendi atau berbasis koordinat
- **Inverse Kinematics (IK)** — input koordinat XYZ + orientasi, robot menghitung sudut sendi
- **Forward Kinematics (FK)** — input sudut sendi, robot menghitung posisi end-effector
- **DH Parameter** — tampilan parameter Denavit-Hartenberg secara realtime + tab eksperimen dengan stick diagram 3D
- **Editor Program** — tulis dan jalankan program Python untuk urutan gerakan otomatis
- **Rekam Gerakan** — rekam gerakan jog langsung menjadi kode Python
- **ROS 2 + RViz** — visualisasi 3D robot secara realtime via ROS 2 Jazzy
- **Panduan Interaktif** — tab Help dengan Quick Start, Fitur GUI, Safety, dan Keybindings

---

## Persyaratan Sistem

| Komponen | Versi |
|---|---|
| Sistem Operasi | Ubuntu 22.04 / 24.04 |
| Python | 3.12 |
| ROS 2 | Jazzy Jalisco |
| NiceGUI | ≥ 2.x |

---

## Instalasi

### 1. Clone repositori

```bash
git clone https://github.com/akunnyampah/TESTING.git
cd TESTING
git checkout sidang-Sesudah-UI-di-perbarui
```

### 2. Buat virtual environment

```bash
python3.12 -m venv waldo_env
source waldo_env/bin/activate
```

### 3. Install dependensi Python

```bash
pip install -e ".[dev]"
```

### 4. Setup ROS 2 workspace

```bash
# Source ROS 2
source /opt/ros/jazzy/setup.bash

# Build workspace
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

### 5. Install dependensi tambahan (opsional, untuk DH Eksperimen)

```bash
pip install matplotlib numpy
```

---

## Menjalankan Program

### Mode Simulator (tanpa hardware)

```bash
cd /path/to/repo
source waldo_env/bin/activate
python -m waldo_commander
```

Buka browser dan akses: **http://localhost:8080**

### Mode Robot Real (dengan hardware)

```bash
# Pastikan robot terhubung via USB dan terdeteksi
ls /dev/ttyACM*   # harus muncul /dev/ttyACM0

# Jalankan GUI
source waldo_env/bin/activate
python -m waldo_commander
```

Di GUI, klik tombol **robot** di toolbar untuk switch ke mode Robot.

### Dengan ROS 2 + RViz

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
source waldo_env/bin/activate
python -m waldo_commander
```

Di GUI, buka tab **ROS 2** → klik **Launch RViz** untuk membuka visualisasi 3D.

---

## Struktur Folder

```
├── waldo_commander/
│   ├── components/         # Komponen UI (Jog, Readout, Help, dll)
│   ├── ui/panels/          # Panel IK/FK, DH Parameter, ROS 2
│   ├── ros2/               # Integrasi ROS 2 (bridge, launcher)
│   ├── services/           # Kinematika (Pinocchio), path visualizer
│   └── common/             # Tema, konfigurasi
├── assets/
│   └── help/
│       ├── images/         # Gambar untuk panduan Help
│       └── videos/         # Video untuk panduan Help
├── Agent/                  # Dokumentasi pengembangan
└── README.md
```

---

## Menambahkan Gambar/Video ke Panduan

Letakkan file di folder yang sesuai tanpa perlu mengubah kode:

| Folder | Format | Digunakan di |
|---|---|---|
| `assets/help/images/` | PNG / JPG | Tab Quick Start & Safety |
| `assets/help/videos/` | MP4 | Tab Quick Start & Fitur GUI |

Lihat `assets/help/README.md` untuk daftar lengkap nama file yang diperlukan.

---

## Koneksi Hardware

Robot terhubung via USB (serial). Cek koneksi dengan:

```bash
ls /dev/ttyACM*
```

Jika perangkat tidak terdeteksi:

```bash
# Tambahkan user ke grup dialout
sudo usermod -a -G dialout $USER
# Logout dan login ulang, kemudian coba lagi
```

---

## Lisensi

Proyek ini dikembangkan untuk keperluan pendidikan.