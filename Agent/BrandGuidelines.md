# Brand & UI Guidelines
# Waldo Commander ROS 2 Integration

Dokumen ini mendefinisikan aturan visual untuk fitur ROS 2 yang ditambahkan.
Tujuan utama: **fitur baru harus terasa seperti bagian asli Waldo Commander**,
bukan seperti plugin yang ditempel dari luar.

---

## Prinsip utama

**"Invisible addition"** — jika seseorang melihat tab ROS 2 tanpa tahu ia
adalah fitur tambahan, ia harus mengira tab itu memang bagian asli Waldo.

Ini berarti:
- Ikuti semua pola visual yang sudah ada di tab lain (I/O, Program)
- Jangan menambahkan elemen dekoratif yang tidak ada di tempat lain
- Gunakan komponen NiceGUI yang sama persis
- Jangan mengimpor CSS tambahan

---

## Tema dan warna

Waldo Commander menggunakan **dark theme** (background gelap).
Seluruh fitur baru harus ikut dark theme ini.

### Warna yang sudah ada di Waldo (reference, jangan hardcode)

Gunakan Tailwind classes yang sama dengan yang dipakai di panel lain Waldo:

| Elemen | Class yang dipakai di Waldo |
|--------|----------------------------|
| Background panel | `bg-dark` / `bg-[#1e1e1e]` atau sesuai existing |
| Text utama | `text-white` |
| Text sekunder / label | `text-gray-400` |
| Border pemisah | `border-gray-700` |
| Input field | sesuai komponen `ui.number` / `ui.input` default |

### Warna semantik untuk fitur ROS 2

Dua warna baru yang diperbolehkan, hanya untuk badge status:

| Status | Warna | NiceGUI class |
|--------|-------|---------------|
| Pose aman | Hijau | `text-positive` atau `bg-positive` (NiceGUI semantic) |
| Pose tidak aman | Merah | `text-negative` atau `bg-negative` (NiceGUI semantic) |
| Loading / proses | Abu-abu | `text-grey` |

Gunakan NiceGUI semantic color names (`positive`, `negative`, `warning`)
bukan hex hardcoded — agar otomatis mengikuti tema.

---

## Tipografi

Ikuti tipografi yang sudah ada di Waldo:

- **Label section** (judul grup): uppercase, tracking-wide, text-gray-400, text-xs
  ```python
  ui.label('Target koordinat').classes('text-xs text-gray-400 uppercase tracking-wide')
  ```

- **Label input**: default NiceGUI label pada `ui.number` / `ui.input`

- **Teks status badge**: text-sm, menggunakan warna semantik
  ```python
  ui.label('Pose dapat dicapai').classes('text-sm text-positive')
  ```

- Jangan menggunakan font-weight bold berlebihan — ikuti yang sudah ada

---

## Layout dan spacing

### Struktur konten tab

Setiap tab di Waldo menggunakan `ui.column` dengan gap dan padding yang konsisten.
Lihat tab I/O atau tab Program sebagai referensi spacing.

Pola umum yang aman:
```python
with ui.column().classes('w-full gap-3 p-3'):
    # Grup 1: input
    with ui.column().classes('gap-1 w-full'):
        ...
    
    ui.separator()  # pemisah antar grup
    
    # Grup 2: tombol aksi
    with ui.column().classes('gap-1 w-full'):
        ...
    
    ui.separator()
    
    # Grup 3: utilitas (RViz)
    with ui.column().classes('gap-1 w-full'):
        ...
```

### Tombol

Gunakan pola tombol yang sama dengan yang ada di tab lain Waldo.
Jika tab I/O atau Program menggunakan `ui.button` dengan props tertentu,
ikuti pola yang sama.

Tombol Eksekusi harus secara visual berbeda dari Preview untuk
menghindari klik tidak sengaja — gunakan warna atau styling
yang sudah ada di Waldo untuk aksi "destructive" atau "final".

---

## Komponen UI yang diperbolehkan

Hanya komponen NiceGUI yang sudah digunakan di Waldo:

| Kebutuhan | Komponen |
|-----------|----------|
| Input angka X/Y/Z | `ui.number` |
| Tombol | `ui.button` |
| Label teks / status | `ui.label` |
| Pemisah | `ui.separator` |
| Container | `ui.column`, `ui.row` |
| Notifikasi sementara | `ui.notify` |

**Tidak diperbolehkan** menambahkan:
- `ui.dialog` / modal baru (kecuali Waldo sudah punya polanya)
- Chart atau grafik
- Custom HTML/CSS via `ui.html` atau `ui.add_css`
- Icon library tambahan
- Tooltip yang berlebihan

---

## Pesan dan teks

### Bahasa
Ikuti bahasa yang digunakan di Waldo Commander (English) untuk konsistensi,
atau pilih satu bahasa dan konsisten. Jangan campur Indonesia dan English
dalam satu label/tombol.

Rekomendasi: gunakan English agar konsisten dengan Waldo existing.

### Label tombol

| Aksi | Label |
|------|-------|
| Kirim request IK | `Preview` |
| Konfirmasi gerakan | `Execute` |
| Buka RViz | `Launch RViz` |
| Tutup RViz | `Close RViz` |

### Pesan status badge

| Kondisi | Pesan |
|---------|-------|
| IK sukses + workspace valid | `Pose reachable` |
| Workspace violation | `Out of workspace: X=... exceeds limit` |
| IK gagal | `IK failed — pose not reachable` |
| ROS 2 tidak tersedia | `ROS 2 unavailable` |
| MoveIt 2 tidak tersedia | `MoveIt 2 service not running` |
| Sedang proses | `Computing...` |

### Pesan error

Error harus informatif, bukan generic:
- ✓ `IK failed — pose not reachable by robot`
- ✓ `Z=0.950 exceeds workspace limit (max: 0.850 m)`
- ✗ `Error occurred`
- ✗ `Something went wrong`

---

## Hal yang tidak boleh dilakukan (UI)

- Jangan menambahkan animasi atau transisi yang tidak ada di Waldo
- Jangan mengubah ukuran panel sidebar
- Jangan menambahkan scrollbar kecuali konten memang overflow
- Jangan menggunakan warna merah/hijau terang yang mencolok —
  gunakan semantic color NiceGUI yang sudah mengikuti tema
- Jangan menambahkan splash screen atau loading overlay
- Jangan mengubah header/toolbar Waldo
- Jangan menambahkan floating button atau elemen fixed-position
