"""RViz subprocess management.

No rclpy dependency — pure subprocess. Safe to import at all times.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import time

logger = logging.getLogger(__name__)

_rviz_process: subprocess.Popen | None = None
_rsp_process: subprocess.Popen | None = None

_DEFAULT_RVIZ_CONFIG = os.path.expanduser(
    "~/ros2_ws/src/parol6_moveit/config/waldo_preview.rviz"
)


def _clean_env() -> dict:
    """Return os.environ copy with VS Code snap GTK overrides stripped."""
    env = os.environ.copy()
    # Strip VS Code snap GTK overrides — they cause rviz2 to load libcanberra-gtk-module.so
    # from /snap/code, which has a RPATH to snap/core20's libpthread (GLIBC 2.31) that
    # conflicts with the system GLIBC 2.39, producing: undefined symbol __libc_pthread_init.
    for _var in ("GTK_PATH", "GTK_EXE_PREFIX", "GTK_IM_MODULE_FILE"):
        env.pop(_var, None)
    # Inherit X11/display vars if Waldo started in a context that lacks them
    # (e.g. VS Code integrated terminal strips DISPLAY, XDG_RUNTIME_DIR).
    for _var in ("DISPLAY", "XDG_RUNTIME_DIR", "XDG_SESSION_TYPE",
                 "XDG_CURRENT_DESKTOP", "GDK_BACKEND"):
        if _var not in env and _var in os.environ:
            env[_var] = os.environ[_var]
    # Only set a DISPLAY fallback if none was found — do not force QT_QPA_PLATFORM,
    # let Qt auto-detect the backend from the session type instead.
    env.setdefault("DISPLAY", ":1")
    return env


def launch_rviz(rviz_config_path: str | None = None) -> dict:
    """Start robot_state_publisher and an RViz window as subprocesses.

    robot_state_publisher (rsp.launch.py) is started first so that RViz
    receives /tf when it opens. Both processes are tracked and terminated
    together by close_rviz().

    Returns a dict with ``status`` key:
      "launched"        — started successfully
      "already_running" — process was already running
      "error"           — failed; see ``reason`` key
    """
    global _rviz_process, _rsp_process

    if _rviz_process is not None and _rviz_process.poll() is None:
        return {"status": "already_running", "pid": _rviz_process.pid}

    env = _clean_env()
    ros_distro = env.get("ROS_DISTRO", "humble")

    if os.path.exists(f"/opt/ros/{ros_distro}/setup.bash") and "AMENT_PREFIX_PATH" not in env:
        logger.warning(
            "ROS 2 setup not sourced in parent env; rviz2 may fail. "
            "Source /opt/ros/%s/setup.bash before launching Waldo Commander.",
            ros_distro,
        )

    # Kill any stale robot_state_publisher before spawning a fresh one.
    # Prevents duplicate rsp instances accumulating across RViz crash/relaunch cycles.
    subprocess.run(["pkill", "-9", "-f", "robot_state_publisher"], capture_output=True)
    time.sleep(0.5)
    ros2_bin = shutil.which("ros2") or f"/opt/ros/{ros_distro}/bin/ros2"
    if os.path.exists(ros2_bin):
        try:
            _rsp_process = subprocess.Popen(
                [ros2_bin, "launch", "parol6_moveit", "rsp.launch.py"],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.info("robot_state_publisher launched with PID %d", _rsp_process.pid)
        except Exception as exc:
            logger.warning("Failed to launch rsp.launch.py (RViz may show no model): %s", exc)
    else:
        logger.warning("ros2 binary not found; skipping rsp.launch.py")

    # Start rviz2
    rviz2_bin = shutil.which("rviz2")
    if rviz2_bin is None:
        candidate = f"/opt/ros/{ros_distro}/bin/rviz2"
        if os.path.exists(candidate):
            rviz2_bin = candidate
        else:
            return {
                "status": "error",
                "reason": (
                    f"rviz2 not found. Source ROS 2 or set ROS_DISTRO "
                    f"(checked {candidate})."
                ),
            }

    cmd = [rviz2_bin]
    if rviz_config_path is None and os.path.exists(_DEFAULT_RVIZ_CONFIG):
        rviz_config_path = _DEFAULT_RVIZ_CONFIG
        logger.info("Using default RViz config: %s", rviz_config_path)
    if rviz_config_path and os.path.exists(rviz_config_path):
        cmd.extend(["-d", rviz_config_path])

    try:
        _rviz_process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logger.info("RViz launched with PID %d", _rviz_process.pid)
        return {"status": "launched", "pid": _rviz_process.pid}
    except Exception as exc:
        logger.error("Failed to launch rviz2: %s", exc)
        return {"status": "error", "reason": str(exc)}


def close_rviz() -> dict:
    """Terminate RViz and robot_state_publisher subprocesses if running.

    Returns ``{"status": "closed"}`` or ``{"status": "not_running"}``.
    """
    global _rviz_process, _rsp_process
    was_running = False
    if _rviz_process is not None and _rviz_process.poll() is None:
        _rviz_process.terminate()
        logger.info("RViz (PID %d) terminated", _rviz_process.pid)
        was_running = True
    if _rsp_process is not None and _rsp_process.poll() is None:
        _rsp_process.terminate()
        logger.info("robot_state_publisher (PID %d) terminated", _rsp_process.pid)
    # Fallback: kill any rsp that survived terminate() or was spawned outside this module
    subprocess.run(["pkill", "-9", "-f", "robot_state_publisher"], capture_output=True)
    return {"status": "closed"} if was_running else {"status": "not_running"}


def get_rviz_status() -> dict:
    """Return ``{"running": bool}`` reflecting current RViz subprocess state."""
    running = _rviz_process is not None and _rviz_process.poll() is None
    return {"running": running}
