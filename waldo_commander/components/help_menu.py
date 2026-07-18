"""Help menu component with keybindings and quick start tutorial."""

import os

from nicegui import app as ng_app, ui

from waldo_commander.services.keybindings import keybindings_manager


class HelpMenu:
    """Help dialog with vertical tabs for keybindings and quick start tutorial."""

    FIRST_VISIT_KEY = "parol_first_visit_shown"
    SAFETY_ACKNOWLEDGED_KEY = "parol_safety_acknowledged"

    def __init__(self) -> None:
        self._dialog: ui.dialog | None = None
        self._stepper: ui.stepper | None = None
        self._keybindings_container: ui.element | None = None
        self._safety_accepted: ui.checkbox | None = None

    def show_help_dialog(self) -> None:
        """Show the main help dialog with vertical tabs."""
        if self._dialog:
            self._dialog.delete()
            self._dialog = None

        self._dialog = ui.dialog().classes("help-dialog").mark("help-dialog")

        with self._dialog:
            with ui.card().classes("overlay-card help-dialog-card p-0 overflow-hidden"):
                with ui.row().classes("gap-0"):
                    # Left side: vertical tabs
                    with ui.column().classes("help-tabs-column shrink-0"):
                        with (
                            ui.tabs()
                            .props("vertical dense")
                            .classes("help-vertical-tabs") as tabs
                        ):
                            keybindings_tab = (
                                ui.tab(name="keybindings", label="", icon="keyboard")
                                .classes("help-tab")
                                .tooltip("Keybindings")
                                .mark("tab-keybindings")
                            )
                            quickstart_tab = (
                                ui.tab(name="quickstart", label="", icon="school")
                                .classes("help-tab")
                                .tooltip("Quick Start")
                                .mark("tab-quickstart")
                            )
                            fitur_gui_tab = (
                                ui.tab(name="fitur_gui", label="", icon="widgets")
                                .classes("help-tab")
                                .tooltip("Fitur GUI")
                                .mark("tab-fitur-gui")
                            )
                            safety_tab = (
                                ui.tab(
                                    name="safety",
                                    label="",
                                    icon="health_and_safety",
                                )
                                .classes("help-tab")
                                .tooltip("Safety")
                                .mark("tab-safety")
                            )

                    # Right side: content
                    with ui.column().classes("flex-1 gap-0 overflow-hidden"):
                        # Header with close button
                        with (
                            ui.row()
                            .classes("w-full items-center px-4 py-2 shrink-0")
                            .style("border-bottom: 1px solid rgba(255,255,255,0.1);")
                        ):
                            ui.label("Help").classes("text-lg font-medium")
                            ui.space()
                            with (
                                ui.link(
                                    "",
                                    "https://jepson2k.github.io/Waldo-Commander/",
                                    new_tab=True,
                                )
                                .classes("text-gray-400")
                                .tooltip("View tutorials online")
                            ):
                                ui.icon("open_in_new", size="sm")
                            ui.button(icon="close", on_click=self._dialog.close).props(
                                "flat round dense color=white"
                            )

                        # Tab panels with vertical animation (matching vertical tabs)
                        with (
                            ui.tab_panels(tabs, value=quickstart_tab)
                            .classes("w-full overflow-hidden")
                            .style("min-width: 720px; min-height: 700px;")
                            .props(
                                "animated transition-prev=slide-up transition-next=slide-down"
                            )
                        ):
                            with (
                                ui.tab_panel(keybindings_tab)
                                .classes("p-0")
                                .style("width: 720px; height: 700px; max-height: 85vh;")
                            ):
                                with ui.scroll_area().classes("w-full h-full"):
                                    self._build_keybindings_content()

                            with (
                                ui.tab_panel(quickstart_tab)
                                .classes("p-0")
                                .style("width: 720px; height: 700px; max-height: 85vh;")
                            ):
                                self._build_quickstart_stepper()

                            with (
                                ui.tab_panel(fitur_gui_tab)
                                .classes("p-0")
                                .style("width: 720px; height: 700px; max-height: 85vh;")
                            ):
                                self._build_fitur_gui_content()

                            with (
                                ui.tab_panel(safety_tab)
                                .classes("p-0")
                                .style("width: 720px; height: 700px; max-height: 85vh;")
                            ):
                                self._build_safety_content()

        self._dialog.open()

    def _build_keybindings_content(self) -> None:
        """Build the keybindings table content."""
        categories = keybindings_manager.get_all_bindings()

        with ui.column().classes("w-full p-4 gap-4").mark("keybindings-content"):
            if not categories:
                ui.label("No keybindings registered").classes("text-gray-500")
                return

            # Sort categories for consistent display
            category_order = [
                "Robot Control",
                "Playback",
                "Recording",
                "Cartesian Jog",
                "Speed Control",
            ]
            sorted_categories = sorted(
                categories.items(),
                key=lambda x: (
                    category_order.index(x[0]) if x[0] in category_order else 999,
                    x[0],
                ),
            )

            for category, bindings in sorted_categories:
                with ui.column().classes("w-full gap-1"):
                    ui.label(category).classes("text-sm font-medium text-gray-400")

                    # Build rows with key parts as list for template rendering
                    rows = []
                    for i, binding in enumerate(bindings):
                        key_parts = []
                        if binding.requires_ctrl:
                            key_parts.append("Ctrl")
                        if binding.requires_alt:
                            key_parts.append("Alt")
                        if binding.requires_shift:
                            key_parts.append("Shift")
                        key_parts.append(binding.display)

                        rows.append(
                            {
                                "id": f"{category}-{i}",
                                "keys": key_parts,
                                "description": binding.description,
                            }
                        )

                    columns = [
                        {
                            "name": "keys",
                            "label": "Key",
                            "field": "keys",
                            "align": "left",
                        },
                        {
                            "name": "description",
                            "label": "Description",
                            "field": "description",
                            "align": "left",
                        },
                    ]

                    table = (
                        ui.table(columns=columns, rows=rows, row_key="id")
                        .props("flat dense hide-header hide-pagination")
                        .classes("keybindings-table")
                    )

                    # Custom slot to render keys as keyboard icons
                    table.add_slot(
                        "body-cell-keys",
                        """
                        <q-td :props="props" class="keys-cell">
                            <span class="kbd-group">
                                <template v-for="(key, idx) in props.value" :key="idx">
                                    <span class="kbd-key">{{ key }}</span>
                                    <span v-if="idx < props.value.length - 1" class="kbd-plus">+</span>
                                </template>
                            </span>
                        </q-td>
                    """,
                    )

    def _build_video_placeholder(
        self, description: str, filename: str | None = None
    ) -> None:
        """Render the video at assets/help/videos/{filename} if present, else a placeholder card."""
        if filename:
            video_path = os.path.join(
                os.path.dirname(__file__), "../../assets/help/videos", filename
            )
            if os.path.exists(video_path):
                ui.video(video_path).classes("w-full rounded-lg my-2").props(
                    'preload="metadata"'
                ).style("max-height: 360px;")
                return

        with ui.card().classes("bg-gray-800 rounded-lg p-4 text-center my-2"):
            ui.icon("videocam_off", size="md").classes("text-gray-500")
            ui.label("📹 Video akan ditambahkan").classes("text-gray-400 text-sm")
            ui.label(description).classes("text-gray-500 text-xs italic")

    def _build_image_placeholder(self, filename: str, caption: str) -> None:
        """Render the image at assets/help/images/{filename} if present, else a placeholder card."""
        image_path = os.path.join(
            os.path.dirname(__file__), "../../assets/help/images", filename
        )
        if os.path.exists(image_path):
            ui.image(image_path).classes("w-full rounded-lg my-2")
        else:
            with ui.card().classes("bg-gray-800 rounded-lg p-4 text-center my-2"):
                ui.icon("image", size="md").classes("text-gray-500")
                ui.label("🖼 Gambar akan ditambahkan").classes("text-gray-400 text-sm")
                ui.label(caption).classes("text-gray-500 text-xs italic")
                ui.label(f"📁 File: images/{filename}").classes(
                    "text-gray-600 text-xs font-mono"
                )

    def _build_dh_reference_table(self) -> None:
        """Render the robot's actual DH parameters, sourced from the DH tab panel."""
        from waldo_commander.ui.panels.dh_tab_panel import _DH_LIMITS_DEG, _DH_PARAMS

        columns = [
            {"name": "joint", "label": "Joint", "field": "joint", "align": "left"},
            {"name": "a", "label": "a (mm)", "field": "a", "align": "right"},
            {"name": "alpha", "label": "α (°)", "field": "alpha", "align": "right"},
            {"name": "d", "label": "d (mm)", "field": "d", "align": "right"},
            {"name": "range", "label": "Range θ (°)", "field": "range", "align": "right"},
        ]
        rows = [
            {
                "joint": joint,
                "a": f"{a:.2f}",
                "alpha": f"{alpha:.1f}",
                "d": f"{d:.2f}",
                "range": f"[{lo:.1f}, {hi:.1f}]",
            }
            for (joint, a, alpha, d, _note), (lo, hi) in zip(_DH_PARAMS, _DH_LIMITS_DEG)
        ]
        ui.table(columns=columns, rows=rows, row_key="joint").props(
            "flat dense hide-pagination"
        ).classes("w-full my-2")

    def _build_fitur_gui_content(self) -> None:
        """Build the Fitur GUI tab: accordion of GUI features."""
        features = [
            {
                "title": "Mode Robot / Simulator",
                "description": """
                    Tombol toggle di toolbar (ikon robot).

                    - **Simulator:** aman untuk latihan, tidak gerakkan hardware.
                    - **Robot:** terhubung ke hardware fisik via serial/USB.

                    Saat pertama buka: selalu mulai di mode Simulator.
                """,
                "video_desc": "Toggle mode Robot vs Simulator",
                "video_filename": "fitur_mode_robot.mp4",
            },
            {
                "title": "Joint Jog",
                "description": """
                    Menggerakkan tiap sendi secara individual.

                    - Klik dan tahan tombol +/- untuk gerakkan sendi.
                    - Satu sendi bergerak dalam satu waktu.

                    **Cocok untuk:** eksplorasi batas gerak, set posisi awal.
                """,
                "video_desc": "Demo Joint Jog — gerak tiap sendi",
                "video_filename": "fitur_joint_jog.mp4",
            },
            {
                "title": "Cartesian Jog",
                "description": """
                    Menggerakkan end-effector dalam koordinat dunia (X/Y/Z/Rx/Ry/Rz).

                    - Robot otomatis hitung sudut sendi yang diperlukan (IK real-time).
                    - Bisa terhenti jika ada sendi mencapai danger zone.
                """,
                "video_desc": "Demo Cartesian Jog — gerak dalam koordinat",
                "video_filename": "fitur_cartesian_jog.mp4",
            },
            {
                "title": "Jog Settings",
                "description": """
                    - **Speed:** kontrol kecepatan jog (level 1-10).
                    - **Accel:** kontrol akselerasi jog (level 1-10).
                    - **Step:** ukuran langkah saat klik singkat (mm/°).
                """,
                "video_desc": "Pengaturan speed, accel, step",
                "video_filename": "fitur_jog_settings.mp4",
            },
            {
                "title": "Program / Editor",
                "description": """
                    Editor Python untuk membuat program gerakan robot.

                    **Fungsi-fungsi yang tersedia:**

                    **Gerakan:**

                    - `rbt.move_j([j1,j2,j3,j4,j5,j6], speed=0.5, accel=0.5)` — gerak ke konfigurasi joint (derajat). Contoh: `rbt.move_j([90,-90,180,0,0,180], speed=0.5, accel=0.5)`
                    - `rbt.move_l([x,y,z,rx,ry,rz], speed=0.5, accel=0.5)` — gerak lurus ke koordinat Cartesian (mm+derajat). Contoh: `rbt.move_l([0,300,200,90,0,90], speed=0.3, accel=0.3)`
                    - `rbt.home()` — prosedur homing via limit switch. ⚠ Hanya gunakan saat area aman.
                    - `rbt.stop()` — hentikan semua gerakan seketika.

                    **Kecepatan dan Akselerasi:**

                    - `rbt.speed(0.5)` — set kecepatan global (0.0–1.0). Nilai 1.0=maksimum, 0.1=sangat lambat.
                    - `rbt.accel(0.5)` — set akselerasi global (0.0–1.0).

                    **Timing:**

                    - `rbt.sleep(detik)` — tunggu N detik sebelum perintah berikutnya. Contoh: `rbt.sleep(1.5)`

                    **Digital I/O:**

                    - `rbt.write_io(port, state)` — set output digital. Contoh: `rbt.write_io(1, True)` → nyalakan DO1
                    - `rbt.read_io(port)` — baca input digital. Contoh: `nilai = rbt.read_io(1)` → baca DI1

                    **Status:**

                    - `rbt.status()` — dapatkan status robot (posisi, sudut, mode, dll)

                    **Fitur Editor:**

                    - Record: rekam gerakan jog → otomatis jadi kode Python
                    - Run: jalankan program di simulator atau hardware
                    - New Tab: buat tab program baru
                    - Save/Load: simpan dan muat program dari file

                    **Contoh program:**
                    ```python
                    rbt.move_j([90,-90,180,0,0,180], speed=0.5, accel=0.5)
                    rbt.sleep(1.0)
                    rbt.move_l([0,300,200,90,0,90], speed=0.3, accel=0.3)
                    rbt.sleep(0.5)
                    rbt.move_j([90,-90,180,0,0,180], speed=0.5, accel=0.5)
                    ```
                """,
                "video_desc": "Membuat dan menjalankan program",
                "video_filename": "fitur_program_editor.mp4",
            },
            {
                "title": "I/O",
                "description": """
                    - Kontrol digital output (DO1, DO2) — nyala/mati relay/solenoid.
                    - Monitor digital input (DI1, DI2) — baca sensor/switch.
                """,
                "video_desc": "Kontrol I/O — relay dan sensor",
                "video_filename": "fitur_io.mp4",
            },
            {
                "title": "Inverse Kinematics (IK)",
                "description": """
                    - **Input:** koordinat target X/Y/Z + orientasi Rx/Ry/Rz (dalam mm/°).
                    - **Preview:** cek apakah pose bisa dicapai → lihat sudut J1-J6 hasil.
                    - **Execute:** gerakkan robot ke pose tersebut.

                    Badge hijau = pose reachable, merah = tidak bisa dicapai.
                """,
                "video_desc": "Demo IK — input koordinat, lihat sudut hasil",
                "video_filename": "fitur_ik.mp4",
            },
            {
                "title": "Forward Kinematics (FK)",
                "description": """
                    - **Input:** sudut joint Base/Shoulder/Elbow/Wrist1/Wrist2/Wrist3 (°).
                    - **Calculate:** hitung posisi end-effector → tampilkan X/Y/Z/Rx/Ry/Rz.
                    - **Execute:** gerakkan robot ke konfigurasi joint tersebut.

                    Warning oranye jika sudut di luar batas — Execute terkunci.
                """,
                "video_desc": "Demo FK — input sudut, lihat koordinat hasil",
                "video_filename": "fitur_fk.mp4",
            },
            {
                "title": "DH Parameters",
                "description": """
                    Menampilkan tabel DH aktual robot secara realtime.

                    - θ (sudut joint) terupdate setiap 100ms saat robot bergerak.
                    - Baris highlight kuning = joint sedang bergerak.

                    **Berguna untuk:** verifikasi manual, pembelajaran kinematika.
                """,
                "video_desc": "Tab DH Parameter — θ realtime",
                "video_filename": "fitur_dh_params.mp4",
            },
            {
                "title": "ROS 2 — Launch RViz",
                "description": """
                    - **Tombol Launch RViz:** buka visualisasi 3D robot di RViz.
                    - RViz mirror semua gerakan robot secara realtime.

                    **Berguna untuk:** monitoring pose dari sudut pandang berbeda.
                """,
                "video_desc": "RViz mirror — robot bergerak di GUI dan RViz",
                "video_filename": "fitur_ros2_rviz.mp4",
            },
            {
                "title": "Mengkoneksikan dengan Robot Real",
                "description": """
                    Panduan menghubungkan GUI ke hardware robot PAROL6 via USB/serial.

                    **Persiapan Hardware:**

                    - Pastikan robot terhubung ke komputer via kabel USB
                    - Power supply robot sudah ON (24V)
                    - Kabel USB dari PAROL Control Board ke komputer terpasang

                    **Cek Koneksi di Linux:**
                    Buka terminal dan jalankan: `ls /dev/ttyACM*`

                    Jika muncul `/dev/ttyACM0` → robot terdeteksi.

                    Jika tidak muncul:

                    - Coba cabut dan pasang kembali kabel USB
                    - Cek dengan: `lsusb`
                    - Tambah akses port serial: `sudo usermod -a -G dialout $USER` (perlu logout/login ulang)

                    **Cara Switch ke Mode Robot di GUI:**

                    1. Pastikan `/dev/ttyACM0` terdeteksi
                    2. Klik tombol robot (ikon robot) di toolbar atas
                    3. Status berubah: SIMULATOR → ROBOT
                    4. Indikator koneksi di pojok kanan atas berubah hijau

                    **Baud Rate dan Port:**

                    - Port default: `/dev/ttyACM0`
                    - Baud rate dikonfigurasi otomatis — tidak perlu setting manual

                    **Jika Koneksi Gagal:**

                    - Cek proses yang memakai port: `fuser /dev/ttyACM0`
                    - Restart Waldo Commander setelah robot dinyalakan
                    - Pastikan robot selesai booting sebelum switch mode

                    ⚠ Selalu baca tab Safety sebelum mengoperasikan robot fisik!
                """,
                "video_desc": "Langkah koneksi robot real — cek port, switch mode, verifikasi",
                "video_filename": "fitur_koneksi_robot.mp4",
            },
        ]

        with ui.scroll_area().classes("w-full h-full"):
            with ui.column().classes("w-full p-4 gap-2").mark("fitur-gui-content"):
                ui.label(
                    "Panduan lengkap fitur-fitur yang tersedia di Waldo Commander GUI."
                ).classes("text-sm text-gray-400 mb-2")

                for feature in features:
                    with ui.expansion(feature["title"]).classes("w-full"):
                        ui.markdown(feature["description"], sanitize=False).classes(
                            "text-md text-gray-300"
                        )
                        self._build_video_placeholder(
                            feature["video_desc"], feature.get("video_filename")
                        )

    def _build_safety_content(self) -> None:
        """Build the Safety tab: warning banner + 6 sections of safety guidance."""
        sections = [
            {
                "title": "Sebelum Mulai",
                "points": [
                    ("Pastikan area kerja robot bebas dari halangan.", False),
                    (
                        "Jangan letakkan tangan/benda di jangkauan robot saat beroperasi.",
                        True,
                    ),
                    ("Selalu mulai di mode Simulator sebelum coba di Robot asli.", False),
                    ("Kenali tombol Emergency Stop (E-STOP) sebelum mulai.", True),
                    (
                        "Jangan paksa gerakkan lengan robot secara manual saat power ON.",
                        True,
                    ),
                ],
                "image": (
                    "safety_area_kerja.png",
                    "Contoh area kerja yang aman sebelum mengoperasikan robot",
                ),
            },
            {
                "title": "Mode Robot vs Simulator",
                "points": [
                    (
                        "Simulator: pergerakan hanya di layar, aman untuk belajar dan debug.",
                        False,
                    ),
                    (
                        "Robot asli: motor bergerak, ada risiko tabrakan dan kerusakan.",
                        False,
                    ),
                    (
                        "Selalu verifikasi program di Simulator sebelum jalankan di Robot.",
                        False,
                    ),
                    (
                        "Jangan switch ke mode Robot saat lengan dalam posisi tidak aman.",
                        True,
                    ),
                ],
                "image": (
                    "safety_mode_robot.png",
                    "Perbedaan tampilan mode Simulator (kiri) dan Robot (kanan)",
                ),
            },
            {
                "title": "Saat Jog Manual",
                "points": [
                    (
                        "Perhatikan batas gerak setiap sendi — jangan paksakan melewati limit.",
                        True,
                    ),
                    (
                        "Cartesian Jog bisa terhenti tiba-tiba saat sendi mendekati danger zone.",
                        False,
                    ),
                    (
                        "Gerakkan perlahan terutama saat mendekati objek atau batas workspace.",
                        False,
                    ),
                    (
                        "Lepaskan tombol segera jika gerakan tidak sesuai ekspektasi.",
                        False,
                    ),
                ],
                "image": (
                    "safety_jog_manual.png",
                    "Indikator batas gerak sendi saat melakukan jog manual",
                ),
            },
            {
                "title": "Emergency Stop (E-STOP)",
                "points": [
                    (
                        "Tombol E-STOP (merah) menghentikan semua gerakan seketika.",
                        True,
                    ),
                    ("Gunakan segera jika robot bergerak tidak terduga.", False),
                    (
                        "Setelah E-STOP: jangan langsung resume — periksa posisi robot dulu.",
                        True,
                    ),
                    (
                        "Robot harus di-home ulang setelah E-STOP pada beberapa kondisi.",
                        True,
                    ),
                ],
                "image": (
                    "safety_estop.png",
                    "Lokasi tombol E-STOP (merah) di panel kontrol GUI",
                ),
            },
            {
                "title": "Recording dan Program",
                "points": [
                    ("Pastikan robot dalam posisi aman sebelum mulai recording.", False),
                    ("Periksa hasil rekaman di editor sebelum dijalankan.", False),
                    ("Jalankan program baru di Simulator terlebih dahulu.", False),
                    (
                        "Kecepatan default (0.5) disarankan untuk program baru — "
                        "jangan langsung set ke 1.0 tanpa verifikasi.",
                        True,
                    ),
                ],
                "image": (
                    "safety_recording.png",
                    "Alur recording yang aman: record → cek editor → run simulator → run robot",
                ),
            },
            {
                "title": "Saat Pakai IK / FK",
                "points": [
                    (
                        "IK: badge merah berarti pose tidak reachable — jangan paksa Execute.",
                        True,
                    ),
                    (
                        "FK: warning oranye berarti sudut di luar batas — Execute dikunci otomatis.",
                        True,
                    ),
                    (
                        "Setelah IK/FK Execute: tunggu robot berhenti sebelum input baru.",
                        False,
                    ),
                    ("Preview selalu sebelum Execute — jangan skip langkah ini.", True),
                ],
                "image": (
                    "safety_ik_fk.png",
                    "Badge hijau IK (reachable) dan warning oranye FK (over limit)",
                ),
            },
        ]

        with ui.scroll_area().classes("w-full h-full"):
            with ui.column().classes("w-full p-4 gap-2").mark("safety-content"):
                with ui.row().classes(
                    "items-center gap-2 bg-amber-900/30 border-l-4 border-amber-500 "
                    "rounded p-3 mb-2 w-full"
                ):
                    ui.icon("warning", size="md").classes("text-amber-500")
                    ui.label(
                        "Baca panduan keselamatan sebelum mengoperasikan robot fisik"
                    ).classes("text-sm font-medium text-amber-200")

                for section in sections:
                    with (
                        ui.expansion(section["title"])
                        .classes("w-full")
                        .style("border-left: 4px solid #f59e0b;")
                    ):
                        for text, critical in section["points"]:
                            if critical:
                                with ui.card().classes(
                                    "bg-amber-900/20 border-l-4 border-amber-500 p-3 rounded my-1"
                                ):
                                    ui.label(text).classes("text-sm text-amber-100")
                            else:
                                with ui.row().classes("items-start gap-2 px-1"):
                                    ui.icon("circle", size="6px").classes(
                                        "text-gray-500 mt-2 shrink-0"
                                    )
                                    ui.label(text).classes("text-sm text-gray-300")

                        image_filename, image_caption = section["image"]
                        self._build_image_placeholder(image_filename, image_caption)

    def _build_quickstart_stepper(self, include_safety_step: bool = False) -> None:
        """Build quick start stepper with tutorial videos.

        Args:
            include_safety_step: If True, prepend a safety acknowledgment step.
                                 Used for first-time visit dialog only.
        """
        # Step descriptions are markdown transcribed from
        # Draft_untuk_dimasukan_ke_user_guide.docx.
        steps = [
            {
                "title": "Tentang Robot Ini",
                "description": """
                    **Apa itu Robot Arm 6 DOF?**

                    Robot ini adalah lengan mekanik yang bisa bergerak bebas di ruang 3D, seperti lengan manusia — tapi dikendalikan oleh komputer. "6 DOF" berarti 6 Degrees of Freedom (6 derajat kebebasan): robot punya 6 sendi yang masing-masing bisa berputar sendiri-sendiri.

                    Analogi mudah: bayangkan lengan Anda —

                    - **Sendi 1 (Base/Pinggang):** memutar seluruh lengan kiri-kanan
                    - **Sendi 2 (Shoulder/Bahu):** mengangkat lengan atas naik-turun
                    - **Sendi 3 (Elbow/Siku):** menekuk lengan bawah
                    - **Sendi 4 (Wrist 1):** memutar pergelangan tangan kiri-kanan
                    - **Sendi 5 (Wrist 2):** menekuk pergelangan tangan naik-turun
                    - **Sendi 6 (Wrist 3):** memutar ujung tangan (seperti memutar obeng)

                    Dengan 6 sendi ini, ujung robot (end-effector) bisa menjangkau hampir semua posisi dan orientasi dalam area kerjanya.

                    **Mengapa Motor Stepper?**

                    Robot ini menggunakan motor stepper — berbeda dengan motor biasa yang berputar terus, motor stepper bergerak dalam langkah-langkah kecil yang presisi (seperti jarum jam yang "tik-tik"). Keuntungan: posisi bisa dikontrol sangat akurat tanpa sensor tambahan. Kekurangan: tidak sekuat motor servo industri, tapi cukup untuk pembelajaran.

                    **Dua Mode Operasi:**

                    - **SIMULATOR — aman untuk belajar:** semua gerakan hanya tampil di layar 3D, tidak ada hardware yang bergerak. Cocok untuk belajar pemrograman dan uji coba gerakan baru.
                    - **ROBOT ASLI — terhubung ke hardware:** motor benar-benar bergerak, perlu berhati-hati — baca panduan Safety dulu. Cocok untuk demonstrasi nyata dan uji gerakan yang sudah diverifikasi.

                    **Apa yang Bisa Dilakukan?**

                    - ✓ Gerak manual per-sendi (Joint Jog)
                    - ✓ Gerak berdasarkan koordinat (Cartesian Jog)
                    - ✓ Hitung dan visualisasi FK/IK
                    - ✓ Rekam gerakan jadi program otomatis
                    - ✓ Jalankan program Python untuk urutan gerakan
                    - ✓ Kontrol I/O (relay, sensor)
                    - ✓ Monitor posisi real-time di RViz (via ROS 2)
                """,
                "video_desc": "Video pengenalan robot dan cara kerjanya secara umum",
                "video_filename": "qs_tentang_robot.mp4",
            },
            {
                "title": "Konsep Dasar FK vs IK",
                "description": """
                    **Forward Kinematics (FK) — Dari Sudut ke Posisi:**

                    FK menjawab pertanyaan: "Jika semua sendi berada di sudut tertentu, end-effector ada di mana?"

                    Prosesnya selalu maju — dari sendi ke posisi:

                    1. Kita tahu: J1=90°, J2=-90°, J3=180°, J4=0°, J5=0°, J6=180°
                    2. Komputer hitung: perkalian 6 matriks transformasi
                    3. Hasil: posisi (X, Y, Z) dan orientasi (Rx, Ry, Rz) end-effector

                    Sifat FK:

                    -✓ Selalu ada jawaban (tidak bisa gagal)
                    -✓ Jawaban selalu satu (tidak ambigu)
                    -✓ Perhitungan cepat dan sederhana

                    **Inverse Kinematics (IK) — Dari Posisi ke Sudut:**

                    IK menjawab kebalikannya: "Sudut sendi berapa agar end-effector sampai di posisi (X, Y, Z) yang kita inginkan?"

                    Prosesnya terbalik — dari posisi ke sendi:

                    1. Kita inginkan: end-effector di X=0, Y=300mm, Z=279mm
                    2. Komputer cari: kombinasi sudut J1...J6 yang menghasilkan posisi itu
                    3. Hasil: bisa berhasil (pose reachable) atau gagal (tidak terjangkau)

                    Sifat IK:

                    -✗ Bisa tidak ada solusi (target di luar jangkauan)
                    -✗ Bisa banyak solusi (siku atas vs siku bawah — sama-sama benar)
                    -✓ Lebih intuitif untuk pengguna (input koordinat, bukan sudut)

                    **Mengapa IK Lebih Sulit?**

                    Bayangkan Anda ingin menyentuh ujung meja dengan jari telunjuk:

                    - Anda bisa melakukannya dengan siku di atas ATAU siku di bawah
                    - Keduanya valid — dua solusi berbeda untuk target yang sama
                    - Komputer harus memilih salah satu (biasanya yang paling dekat dengan posisi sendi saat ini)

                    Untuk robot 6 DOF, bisa ada 16 konfigurasi berbeda yang mencapai titik yang sama — IK harus memilih yang paling aman dan efisien.
                """,
                "images": [
                    (
                        "qs_fk_vs_ik.png",
                        "Diagram perbandingan FK (kiri: sudut→posisi) dan IK (kanan: posisi→sudut)",
                    ),
                ],
            },
            {
                "title": "Parameter Denavit-Hartenberg (DH)",
                "description": """
                    **Apa itu Parameter DH?**

                    DH adalah cara standar untuk "mendeskripsikan" geometri robot — bagaimana setiap link (batang) dan sendi (joint) tersusun di ruang 3D. Diciptakan oleh Jacques Denavit dan Richard Hartenberg pada 1955, dan masih dipakai di seluruh dunia hingga sekarang.

                    Analoginya: bayangkan Anda ingin menjelaskan jalan dari rumah ke kampus kepada orang yang belum pernah ke sana. Anda bisa bilang: "Jalan lurus 500m, belok kiri 90°, jalan 200m, belok kanan 45°..." DH parameter melakukan hal yang sama untuk setiap sendi robot — mendefinisikan "berapa jauh" dan "berapa putar" dari satu sendi ke sendi berikutnya.

                    **4 Parameter per Sendi:**

                    - **a (Link Length — panjang link):** jarak dari sumbu sendi ini ke sumbu sendi berikutnya, diukur sepanjang sumbu X. Analogi: panjang tulang lengan Anda.
                    - **α (Link Twist — puntiran link):** sudut antara sumbu Z sendi ini dan sumbu Z sendi berikutnya, diukur mengelilingi sumbu X. Analogi: seberapa "miring" sumbu putar antar sendi.
                    - **d (Link Offset — jarak offset):** jarak sepanjang sumbu Z dari satu sendi ke sendi berikutnya. Analogi: ketebalan/panjang sambungan antar tulang.
                    - **θ (Joint Angle — sudut sendi):** sudut rotasi mengelilingi sumbu Z — INI yang berubah saat robot bergerak! a, α, d selalu tetap (geometri robot tidak berubah), θ berubah setiap kali sendi bergerak.

                    **Perhatian Penting:**

                    Robot ini menggunakan **Modified DH (Craig's Convention)** — bukan Standard DH yang ada di banyak buku robotika. Jika Anda menghitung manual dari buku Standard DH, angkanya TIDAK akan cocok. Ini normal, bukan kesalahan!

                    Parameter DH aktual robot ini:
                """,
                "extra": "dh_table",
                "description_after": """
                    Catatan J4: nilai a dan d negatif adalah hasil sah dari konvensi geometri DH — bukan kesalahan input.

                    **Cara Membaca Tabel:**

                    Contoh J1 (Base): a=0mm, α=0°, d=110.5mm, θ=variabel [-123°, +123°]. Artinya: Base tidak punya panjang link (a=0), tidak ada puntiran (α=0), tapi punya offset tinggi 110.5mm dari lantai ke pusat sendi pertama.
                """,
                "images": [
                    (
                        "qs_dh_params.png",
                        "Ilustrasi parameter a, α, d, θ pada satu sendi robot",
                    ),
                ],
            },
            {
                "title": "Cara FK dan IK Dihitung",
                "description": """
                    **BAGIAN 1 — Forward Kinematics: Perkalian Matriks**

                    Setiap sendi direpresentasikan sebagai matriks 4×4. Matriks ini menggabungkan ROTASI dan TRANSLASI dalam satu operasi. Disebut "matriks transformasi homogen" — terdengar rumit, tapi idenya sederhana:

                    ```
                    [  R  R  R  | tx ]
                    [  R  R  R  | ty ]   ← R = rotasi (3×3), t = translasi (posisi)
                    [  R  R  R  | tz ]
                    [  0  0  0  |  1 ]
                    ```

                    Bagian R (3×3) di kiri atas = "ke arah mana end-effector menghadap". Bagian t (kolom kanan) = "end-effector ada di koordinat X,Y,Z berapa".

                    Untuk mendapat posisi end-effector dari Base:

                    **T_total = T₁ × T₂ × T₃ × T₄ × T₅ × T₆**

                    Setiap T dihitung dari parameter DH sendi tersebut. Hasilnya T_total langsung memberikan posisi dan orientasi end-effector.

                    Inilah yang dilakukan tab Forward Kinematics di GUI — Anda masukkan 6 sudut, komputer kalikan 6 matriks, hasilnya langsung tampil sebagai X, Y, Z, Rx, Ry, Rz.
                """,
                "mid_images": [
                    (
                        "qs_matriks_transform.png",
                        "Struktur matriks transformasi homogen 4×4 dan cara membacanya",
                    ),
                ],
                "description_after": """
                    **BAGIAN 2 — Inverse Kinematics: Pendekatan Iteratif**

                    **Mengapa tidak bisa langsung (closed-form)?**

                    Untuk robot sederhana (3 DOF), ada rumus langsung untuk IK. Untuk robot 6 DOF dengan geometri kompleks seperti ini, rumus langsungnya sangat panjang dan rentan singularitas. Robot ini menggunakan pendekatan numerik-iteratif via Pinocchio.

                    **Alur iterasi IK (langkah demi langkah):**

                    1. TEBAKAN AWAL: mulai dari sudut sendi saat ini
                    2. HITUNG FK: dari tebakan → dapat posisi sementara end-effector
                    3. HITUNG ERROR: bandingkan posisi sementara dengan target (seberapa jauh dan ke arah mana masih meleset?)
                    4. GUNAKAN JACOBIAN: matriks yang memetakan "kalau sendi X berubah 1°, end-effector pindah sejauh berapa ke arah mana?" Jacobian dipakai untuk memperkirakan koreksi sudut yang diperlukan
                    5. KOREKSI: tambahkan koreksi ke sudut saat ini
                    6. ULANGI dari langkah 2 sampai error cukup kecil (konvergen) atau batas iterasi tercapai (tidak konvergen = tidak reachable)

                    **Apa itu Jacobian?**

                    Analogi mudah: bayangkan Anda mengendarai mobil di malam hari. Anda tidak tahu peta lengkap, tapi Anda tahu: "Kalau saya belok kanan, saya mendekat ke tujuan". Jacobian adalah "peta lokal" itu — setiap iterasi dihitung ulang karena peta berubah seiring posisi robot berubah.

                    **Konvergen vs Tidak Konvergen:**

                    - **KONVERGEN (badge hijau):** iterasi berhasil menemukan sudut yang pas → error mengecil setiap iterasi → berhenti saat error < threshold
                    - **TIDAK KONVERGEN (badge merah):** target tidak bisa dicapai → error tidak mengecil → batas iterasi tercapai → pose not reachable
                """,
                "images": [
                    (
                        "qs_iterasi_ik.png",
                        "Alur iterasi IK: tebak awal → FK → error → Jacobian → koreksi → ulang",
                    ),
                ],
            },
            {
                "title": "Cara Membuka Panduan Kembali",
                "description": """
                    Panduan ini bisa dibuka kapan saja selama menggunakan GUI.

                    **Cara membuka Help:**

                    1. Lihat panel ikon di sisi KIRI layar
                    2. Klik ikon tanda tanya (?) di bagian BAWAH panel
                    3. Dialog Help akan terbuka

                    **4 Tab yang tersedia di Help:**

                    **📋 Keybindings**
                    Daftar lengkap shortcut keyboard yang tersedia di GUI. Berguna saat ingin menggunakan keyboard untuk kontrol cepat.

                    **🚀 Quick Start (panduan ini)**
                    Penjelasan dasar konsep FK, IK, parameter DH, dan cara perhitungannya. Cocok dibaca sebelum mulai praktik.

                    **🔧 Fitur GUI**
                    Penjelasan detail setiap fitur yang ada di GUI — Joint Jog, Cartesian Jog, IK/FK panel, DH Parameters, Program Editor, I/O, dan ROS 2/RViz. Buka tab ini jika bingung cara menggunakan fitur tertentu.

                    **⚠ Safety**
                    Panduan keselamatan operasi robot. WAJIB dibaca sebelum mengoperasikan robot fisik (mode Robot).

                    **Tips:**

                    - → Selalu mulai di mode Simulator sebelum coba di Robot asli
                    - → Baca tab Safety minimal sekali sebelum menyentuh hardware
                    - → Tab DH Parameters di GUI menampilkan θ realtime saat robot bergerak
                    - → Jika ragu dengan suatu fitur, buka tab Fitur GUI di Help ini
                """,
            },
        ]

        with ui.scroll_area().classes("w-full h-full tutorial-scroll"):
            with (
                ui.stepper()
                .props("vertical header-nav flat active-color=white done-color=grey-5")
                .classes("p-0")
                .style("width: 700px;") as self._stepper
            ):
                # Safety step (only shown on first visit)
                if include_safety_step:
                    with ui.step("Safety Notice").classes("gap-2").mark("safety-step"):
                        with ui.row().classes("items-center gap-2 mb-2"):
                            ui.icon("warning", size="md").classes("text-amber-500")
                            ui.label("Please read before continuing").classes(
                                "text-lg font-medium"
                            )

                        with ui.column().classes("gap-2 ml-1"):
                            warnings = [
                                "This software provides no safety guarantees and assumes no liability",
                                "User accepts full responsibility for robot operation",
                                "Simulator mode is not physics-accurate and does not guarantee repeatability on real hardware",
                                "The digital E-STOP is not a substitute for the hardware emergency stop",
                                "Incorrect kinematics calculations could result in sudden robotic movements",
                                "Keep clear of all moving parts during operation",
                            ]
                            for warning in warnings:
                                with ui.row().classes("items-start gap-2"):
                                    ui.icon("circle", size="6px").classes(
                                        "text-amber-500 mt-2 shrink-0"
                                    )
                                    ui.label(warning).classes("text-sm")

                        with ui.stepper_navigation().classes("mt-4"):
                            self._safety_accepted = ui.checkbox(
                                "I have read and accept responsibility"
                            ).classes("mr-4")
                            next_btn = ui.button(
                                "Continue", on_click=self._stepper.next
                            ).props("color=primary")
                            next_btn.bind_enabled_from(self._safety_accepted, "value")

                            # Store acknowledgment when checkbox is checked
                            def on_accept(e):
                                if e.args:
                                    ng_app.storage.general[
                                        self.SAFETY_ACKNOWLEDGED_KEY
                                    ] = True

                            self._safety_accepted.on("update:model-value", on_accept)

                for i, step in enumerate(steps):
                    with ui.step(step["title"]).classes("gap-2"):
                        # sanitize=False is safe here: the content is a
                        # hardcoded literal that includes inline formatting
                        # (bold, tables, arrows) that DOMPurify would strip.
                        ui.markdown(step["description"], sanitize=False).classes(
                            "text-md text-gray-300"
                        )

                        if step.get("extra") == "dh_table":
                            self._build_dh_reference_table()

                        for image_filename, image_caption in step.get(
                            "mid_images", []
                        ):
                            self._build_image_placeholder(image_filename, image_caption)

                        if "description_after" in step:
                            ui.markdown(
                                step["description_after"], sanitize=False
                            ).classes("text-md text-gray-300")

                        if "video_desc" in step:
                            self._build_video_placeholder(
                                step["video_desc"], step.get("video_filename")
                            )

                        for image_filename, image_caption in step.get("images", []):
                            self._build_image_placeholder(image_filename, image_caption)

                        with ui.stepper_navigation():
                            if i < len(steps) - 1:
                                ui.button("Next", on_click=self._stepper.next).props(
                                    "color=primary"
                                )
                            else:
                                ui.button("Finish", on_click=self._on_finish).props(
                                    "color=primary"
                                )
                            if i > 0:
                                ui.button(
                                    "Back", on_click=self._stepper.previous
                                ).props("flat")

    def _on_finish(self) -> None:
        """Handle finish button click - close dialog without suppressing future appearances."""
        if self._dialog:
            self._dialog.close()

    def check_first_visit(self) -> None:
        """Check if this is the first visit and show tutorial dialog if so."""
        if not ng_app.storage.user.get(self.FIRST_VISIT_KEY, False):
            self.show_dialog()

    def show_dialog(self) -> None:
        """Show the first-time tutorial dialog (alias for backwards compatibility)."""
        self.create_first_time_dialog().open()

    def create_first_time_dialog(self) -> ui.dialog:
        """Create and return the first-time tutorial dialog."""
        # Persistent dialog - can't be dismissed by clicking outside
        self._dialog = ui.dialog().props("persistent")

        # Check if safety was already acknowledged in a previous session
        safety_already_acknowledged = ng_app.storage.general.get(
            self.SAFETY_ACKNOWLEDGED_KEY, False
        )

        with self._dialog:
            with ui.card().classes("overlay-card tutorial-dialog-card"):
                with ui.column().classes("w-full h-full gap-0"):
                    # Header
                    ui.label("Selamat Datang di GUI Robot!").classes("text-xl font-bold")

                    ui.label(
                        "Mari kenali fitur-fitur yang tersedia di antarmuka ini."
                    ).classes("text-sm text-gray-400 mb-3 shrink-0")

                    # Quick start stepper (with safety step only if not already acknowledged)
                    self._build_quickstart_stepper(
                        include_safety_step=not safety_already_acknowledged
                    )

                    # Footer - hidden until safety is acknowledged (or always visible if already acknowledged)
                    footer = (
                        ui.row()
                        .classes("w-full items-center pt-3 shrink-0")
                        .style("border-top: 1px solid rgba(255,255,255,0.1);")
                    )
                    if self._safety_accepted and not safety_already_acknowledged:
                        footer.bind_visibility_from(self._safety_accepted, "value")

                    with footer:
                        dont_show = ui.checkbox("Don't show this again")
                        dont_show.on(
                            "update:model-value",
                            lambda e: self._save_dont_show_pref(e.args),
                        )
                        ui.space()
                        ui.button("Skip Tour", on_click=self._dialog.close).props(
                            "flat"
                        )

        return self._dialog

    def _save_dont_show_pref(self, value: bool) -> None:
        """Save don't show again preference to server storage."""
        if value:
            ng_app.storage.user[self.FIRST_VISIT_KEY] = True


# Singleton
help_menu = HelpMenu()
