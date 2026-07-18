# Help Assets — Waldo Commander GUI
# Letakkan file gambar dan video di folder ini sesuai naming convention.
# GUI akan otomatis menampilkan file jika ada, atau placeholder jika belum.

## Folder structure
  assets/help/
  ├── images/    ← file PNG/JPG untuk gambar di Help dialog
  └── videos/    ← file MP4 untuk video di Help dialog

## Naming convention — JANGAN ubah nama file ini

### Quick Start (images)
| Nama file                  | Digunakan di       | Konten yang disarankan              |
|----------------------------|--------------------|-------------------------------------|
| qs_fk_vs_ik.png            | Quick Start step 2 | Diagram perbandingan FK vs IK       |
| qs_dh_params.png           | Quick Start step 3 | Ilustrasi parameter a, α, d, θ      |
| qs_matriks_transform.png   | Quick Start step 4 | Struktur matriks transformasi 4×4   |
| qs_iterasi_ik.png          | Quick Start step 4 | Alur iterasi IK: tebak→FK→error→ulang|

### Quick Start (videos)
| Nama file                  | Digunakan di       | Konten yang disarankan              |
|----------------------------|--------------------|-------------------------------------|
| qs_tentang_robot.mp4       | Quick Start step 1 | Video pengenalan robot secara umum  |

### Safety (images)
| Nama file                  | Digunakan di       | Konten yang disarankan              |
|----------------------------|--------------------|-------------------------------------|
| safety_area_kerja.png      | Safety section A   | Contoh area kerja yang aman         |
| safety_mode_robot.png      | Safety section B   | Tampilan mode Simulator vs Robot    |
| safety_jog_manual.png      | Safety section C   | Indikator batas gerak sendi         |
| safety_estop.png           | Safety section D   | Lokasi tombol E-STOP di GUI         |
| safety_recording.png       | Safety section E   | Alur recording yang aman            |
| safety_ik_fk.png           | Safety section F   | Badge IK hijau/merah + warning FK   |

## Cara menambahkan file
1. Buat atau siapkan file gambar/video sesuai nama di tabel
2. Letakkan file di folder yang sesuai (images/ atau videos/)
3. Refresh browser — gambar akan langsung tampil menggantikan placeholder
4. Tidak perlu restart server atau ubah kode apapun

## Ukuran yang disarankan
- Gambar: lebar maksimal 680px, format PNG atau JPG
- Video: format MP4, resolusi 720p atau lebih rendah

### Fitur GUI (videos)
| Nama file                   | Digunakan di              |
|-----------------------------|---------------------------|
| fitur_mode_robot.mp4        | Fitur GUI: Mode Robot/Sim |
| fitur_joint_jog.mp4         | Fitur GUI: Joint Jog      |
| fitur_cartesian_jog.mp4     | Fitur GUI: Cartesian Jog  |
| fitur_jog_settings.mp4      | Fitur GUI: Jog Settings   |
| fitur_program_editor.mp4    | Fitur GUI: Program/Editor |
| fitur_io.mp4                | Fitur GUI: I/O            |
| fitur_ik.mp4                | Fitur GUI: IK             |
| fitur_fk.mp4                | Fitur GUI: FK             |
| fitur_dh_params.mp4         | Fitur GUI: DH Parameters  |
| fitur_ros2_rviz.mp4         | Fitur GUI: ROS 2/RViz     |
| fitur_koneksi_robot.mp4     | Fitur GUI: Koneksi Robot  |
