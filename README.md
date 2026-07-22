# Waldo Commander

Antarmuka web untuk mengendalikan lengan robot, saat ini diuji dengan robot [PAROL6](https://github.com/PCrnjak/PAROL6-Desktop-robot-arm).

- **Berbasis browser.** Robot dapat dikendalikan dari perangkat apa pun dalam jaringan tanpa harus terhubung langsung ke arm.
- **Program Python.** Tulis program robot menggunakan Python, termasuk loop, perhitungan matematika, dan library tambahan. Editor bawaan menyediakan auto-complete, output langsung, dan debugging per langkah.
- **Simulasi 3D.** Pratinjau jalur gerak, cek keterjangkauan pose, dan geser timeline tanpa harus memakai robot fisik.
- **Rekam gerakan manual.** Kendalikan robot secara langsung dan rekam gerakannya menjadi kode Python.
- **Backend fleksibel.** Logika khusus robot berada di balik layer abstraksi [waldoctl](https://github.com/Jepson2k/waldoctl). Robot lain dapat diintegrasikan dengan menerapkan interface yang sama.

## Mulai Cepat

```bash
git clone https://github.com/Jepson2k/Waldo-Commander.git
cd Waldo-Commander
pip install -e ".[parol6]"
waldo-commander
```

Buka URL yang muncul di terminal. Jika robot belum terhubung, aplikasi akan otomatis berjalan dalam mode simulator sehingga fitur dapat dicoba terlebih dahulu.

Untuk koneksi hardware, setup platform, dan konfigurasi, lihat dokumentasi [Getting Started](https://jepson2k.github.io/Waldo-Commander/getting-started/).

## Tautan

- [Dokumentasi](https://jepson2k.github.io/Waldo-Commander/)
- [waldoctl](https://github.com/Jepson2k/waldoctl) — layer abstraksi backend robot
- [Hardware PAROL6](https://github.com/PCrnjak/PAROL6-Desktop-robot-arm)

## Keselamatan

- Software ini tidak memberikan jaminan keselamatan dan tidak menanggung tanggung jawab atas penggunaan robot.
- Pengguna bertanggung jawab penuh atas pengoperasian robot.
- Mode simulator tidak akurat secara fisika dan tidak menjamin hasil yang sama pada hardware asli.
- E-STOP digital bukan pengganti tombol emergency stop fisik.
- Perhitungan kinematika yang salah dapat menyebabkan gerakan robot yang tiba-tiba.
- Jaga jarak aman dari semua bagian robot yang bergerak saat sistem beroperasi.
