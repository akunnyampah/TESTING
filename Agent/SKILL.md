# SKILL.md — Panduan Teknis Implementasi
# Waldo Commander ROS 2 Integration

Dokumen ini berisi pola-pola teknis spesifik yang harus diikuti
saat mengimplementasikan integrasi ROS 2 ke Waldo Commander.

---

## Stack teknis project ini

| Komponen | Teknologi | Versi minimum |
|----------|-----------|---------------|
| GUI framework | NiceGUI | sesuai Waldo existing |
| Python | CPython | 3.12+ |
| ROS 2 | Humble / Iron / Jazzy | Humble (22.04) |
| Motion planning | MoveIt 2 | sesuai distro ROS 2 |
| Robot backend | waldoctl + PAROL6 | existing |

---

## Pola 1: Menambahkan tab baru di NiceGUI

Cara yang benar menambahkan tab baru ke panel yang sudah ada di NiceGUI.
Jangan membuat `ui.tabs` baru — cari instance yang sudah ada dan tambahkan ke sana.

```python
# Di ros2_panel.py — mendefinisikan konten tab
from nicegui import ui

def create_ros2_tab_content():
    """Konten yang dirender di dalam tab ROS 2."""
    with ui.column().classes('w-full gap-2 p-2'):
        # Header
        ui.label('Target koordinat ROS 2').classes('text-sm text-gray-400 uppercase tracking-wide')
        
        # Input fields
        with ui.column().classes('gap-1 w-full'):
            x_input = ui.number('X (meter)', value=0.3, step=0.001, format='%.3f').classes('w-full')
            y_input = ui.number('Y (meter)', value=0.0, step=0.001, format='%.3f').classes('w-full')
            z_input = ui.number('Z (meter)', value=0.4, step=0.001, format='%.3f').classes('w-full')
        
        # Status badge (tersembunyi awalnya)
        status_badge = ui.label('').classes('hidden')
        
        # Tombol-tombol
        preview_btn = ui.button('Preview gerakan', on_click=lambda: handle_preview())
        execute_btn = ui.button('Eksekusi robot', on_click=lambda: handle_execute()).props('disabled')
        
        ui.separator()
        
        launch_btn = ui.button('Launch RViz', on_click=lambda: handle_rviz_toggle())

    return {
        'x': x_input, 'y': y_input, 'z': z_input,
        'status': status_badge,
        'preview_btn': preview_btn,
        'execute_btn': execute_btn,
        'launch_btn': launch_btn,
    }
```

---

## Pola 2: rclpy dengan asyncio (WAJIB diikuti)

rclpy blocking — selalu jalankan di thread daemon terpisah.
Gunakan `Future` untuk komunikasi antar thread.

```python
# bridge.py

import threading
import rclpy
from rclpy.node import Node
from concurrent.futures import Future as ThreadFuture

class WaldoROS2Bridge(Node):
    _instance = None
    _spin_thread = None

    def __init__(self):
        super().__init__('waldo_ros2_bridge')
        self._ik_client = self.create_client(
            GetPositionIK, '/compute_ik'
        )
        self._logger = self.get_logger()

    @classmethod
    def get_instance(cls):
        """Singleton — satu node untuk seluruh lifecycle Waldo."""
        if cls._instance is None:
            rclpy.init()
            cls._instance = cls()
            cls._spin_thread = threading.Thread(
                target=rclpy.spin,
                args=(cls._instance,),
                daemon=True   # daemon=True wajib agar tidak memblokir shutdown Waldo
            )
            cls._spin_thread.start()
        return cls._instance

    def compute_ik_sync(self, x: float, y: float, z: float) -> dict:
        """
        Panggil IK service secara synchronous (aman dipanggil dari thread apapun).
        Gunakan ini dari endpoint aiohttp via run_in_executor.
        """
        if not self._ik_client.wait_for_service(timeout_sec=2.0):
            return {'success': False, 'reason': 'MoveIt 2 IK service tidak tersedia'}

        req = GetPositionIK.Request()
        req.ik_request.group_name = 'arm'
        req.ik_request.pose_stamped.header.frame_id = 'base_link'
        req.ik_request.pose_stamped.pose.position.x = x
        req.ik_request.pose_stamped.pose.position.y = y
        req.ik_request.pose_stamped.pose.position.z = z
        req.ik_request.pose_stamped.pose.orientation.w = 1.0  # orientasi default

        future = self._ik_client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)

        if future.result() is None:
            return {'success': False, 'reason': 'IK service timeout'}

        result = future.result()
        if result.error_code.val == 1:  # MoveItErrorCodes.SUCCESS
            angles_deg = [
                math.degrees(a)
                for a in result.solution.joint_state.position
            ]
            return {
                'success': True,
                'joint_angles_deg': angles_deg,
                'joint_angles_rad': list(result.solution.joint_state.position),
            }
        else:
            return {
                'success': False,
                'reason': f'IK gagal (error code: {result.error_code.val})'
            }
```

---

## Pola 3: Endpoint aiohttp yang aman untuk asyncio

Karena Waldo memakai asyncio, endpoint harus menggunakan `run_in_executor`
agar panggilan blocking ke ROS 2 tidak memblokir event loop.

```python
# Di file route handler baru

import asyncio
from aiohttp import web

async def handle_ros_preview(request):
    try:
        data = await request.json()
        x, y, z = float(data['x']), float(data['y']), float(data['z'])
    except (KeyError, ValueError, TypeError):
        return web.json_response(
            {'status': 'error', 'reason': 'Input X, Y, Z tidak valid'},
            status=400
        )

    # Validasi workspace dulu (cepat, tidak perlu thread)
    from .ros2.config import check_workspace
    workspace_ok, workspace_reason = check_workspace(x, y, z)
    if not workspace_ok:
        return web.json_response({
            'status': 'error',
            'reason': workspace_reason
        })

    # IK adalah blocking — jalankan di thread pool
    loop = asyncio.get_event_loop()
    try:
        bridge = WaldoROS2Bridge.get_instance()
        ik_result = await loop.run_in_executor(
            None,
            bridge.compute_ik_sync, x, y, z
        )
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'reason': f'ROS 2 bridge error: {str(e)}'
        }, status=500)

    if ik_result['success']:
        return web.json_response({
            'status': 'ok',
            'joint_angles_deg': ik_result['joint_angles_deg'],
        })
    else:
        return web.json_response({
            'status': 'error',
            'reason': ik_result['reason']
        })
```

---

## Pola 4: RViz subprocess management

```python
# rviz_launcher.py

import subprocess
import os
import shutil

_rviz_process = None

def launch_rviz(rviz_config_path: str = None) -> dict:
    global _rviz_process

    # Cek apakah sudah berjalan
    if _rviz_process and _rviz_process.poll() is None:
        return {'status': 'already_running', 'pid': _rviz_process.pid}

    # Cek RViz tersedia
    if not shutil.which('rviz2'):
        # Coba dengan full path ROS 2
        ros_distro = os.environ.get('ROS_DISTRO', 'humble')
        rviz2_path = f'/opt/ros/{ros_distro}/bin/rviz2'
        if not os.path.exists(rviz2_path):
            return {
                'status': 'error',
                'reason': f'rviz2 tidak ditemukan. Pastikan ROS 2 sudah di-source.'
            }
        cmd = [rviz2_path]
    else:
        cmd = ['rviz2']

    # Tambahkan config file jika ada
    if rviz_config_path and os.path.exists(rviz_config_path):
        cmd.extend(['-d', rviz_config_path])

    # Inherit environment agar ROS 2 domain ID dan settings ikut
    env = os.environ.copy()
    ros_distro = env.get('ROS_DISTRO', 'humble')
    ros_setup = f'/opt/ros/{ros_distro}/setup.bash'

    try:
        _rviz_process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return {'status': 'launched', 'pid': _rviz_process.pid}
    except Exception as e:
        return {'status': 'error', 'reason': str(e)}


def close_rviz() -> dict:
    global _rviz_process
    if _rviz_process and _rviz_process.poll() is None:
        _rviz_process.terminate()
        return {'status': 'closed'}
    return {'status': 'not_running'}


def get_rviz_status() -> dict:
    running = _rviz_process is not None and _rviz_process.poll() is None
    return {'running': running}
```

---

## Pola 5: Safety check workspace

```python
# config.py

from dataclasses import dataclass
from typing import Tuple

# Sesuaikan nilai ini dengan robot PAROL6 yang digunakan
WORKSPACE_LIMITS = {
    'x': (-0.55, 0.55),   # meter
    'y': (-0.55, 0.55),   # meter
    'z': (0.02, 0.85),    # meter — batas bawah 2cm di atas base
}

def check_workspace(x: float, y: float, z: float) -> Tuple[bool, str]:
    """
    Returns (is_safe, reason_if_not_safe).
    Reason kosong string jika aman.
    """
    limits = WORKSPACE_LIMITS

    if not (limits['x'][0] <= x <= limits['x'][1]):
        return False, f'X={x:.3f} di luar batas ({limits["x"][0]} s.d. {limits["x"][1]} m)'
    if not (limits['y'][0] <= y <= limits['y'][1]):
        return False, f'Y={y:.3f} di luar batas ({limits["y"][0]} s.d. {limits["y"][1]} m)'
    if not (limits['z'][0] <= z <= limits['z'][1]):
        return False, f'Z={z:.3f} di luar batas ({limits["z"][0]} s.d. {limits["z"][1]} m)'

    return True, ''
```

---

## Pola 6: Update 3D viewer Waldo dengan joint angles

Jangan buat viewer baru. Cari dan gunakan mekanisme update yang sudah ada.
Saat explore kode Waldo, identifikasi fungsi/method yang dipanggil saat jog
untuk update pose di viewer — itulah yang harus dipakai.

Polanya kemungkinan seperti ini (sesuaikan dengan kode actual Waldo):
```python
# Setelah mendapat joint_angles_deg dari IK result:
# Cari di kode Waldo cara memanggil teleport atau update viewer
# Kemungkinan sesuatu seperti:
#   app_state.robot_client.teleport(joint_angles_deg)
# atau:
#   viewer.set_joint_angles(joint_angles_deg)
# IDENTIFIKASI ini dulu sebelum coding
```

---

## Checklist sebelum submit kode

- [ ] Semua import ROS 2 dibungkus try/except dengan fallback `ROS2_AVAILABLE = False`
- [ ] rclpy.spin() berjalan di daemon thread, bukan di event loop
- [ ] Semua panggilan blocking menggunakan `run_in_executor`
- [ ] Tidak ada file existing yang diubah selain satu titik integrasi tab
- [ ] Tombol Eksekusi disabled by default, hanya aktif saat status hijau
- [ ] Workspace limits dikonfigurasi di `config.py`, bukan hardcoded di bridge
- [ ] Setiap endpoint mengembalikan error yang jelas jika ROS 2 tidak tersedia
- [ ] Tidak ada `print()` — gunakan `logging` atau NiceGUI `ui.notify`
