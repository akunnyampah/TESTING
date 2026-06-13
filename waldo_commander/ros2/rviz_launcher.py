"""RViz subprocess management.

No rclpy dependency — pure subprocess. Safe to import at all times.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess

logger = logging.getLogger(__name__)

_rviz_process: subprocess.Popen | None = None


def launch_rviz(rviz_config_path: str | None = None) -> dict:
    """Start an RViz window in a subprocess.

    Returns a dict with ``status`` key:
      "launched"       — started successfully
      "already_running" — process was already running
      "error"          — failed; see ``reason`` key
    """
    global _rviz_process

    if _rviz_process is not None and _rviz_process.poll() is None:
        return {"status": "already_running", "pid": _rviz_process.pid}

    rviz2_bin = shutil.which("rviz2")
    if rviz2_bin is None:
        ros_distro = os.environ.get("ROS_DISTRO", "humble")
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
    if rviz_config_path and os.path.exists(rviz_config_path):
        cmd.extend(["-d", rviz_config_path])

    env = os.environ.copy()
    ros_distro = env.get("ROS_DISTRO", "humble")
    # Ensure ROS 2 setup is sourced in subprocess environment
    ros_setup = f"/opt/ros/{ros_distro}/setup.bash"
    if os.path.exists(ros_setup) and "AMENT_PREFIX_PATH" not in env:
        logger.warning(
            "ROS 2 setup not sourced in parent env; rviz2 may fail. "
            "Source %s before launching Waldo Commander.",
            ros_setup,
        )

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
    """Terminate the RViz subprocess if running.

    Returns ``{"status": "closed"}`` or ``{"status": "not_running"}``.
    """
    global _rviz_process
    if _rviz_process is not None and _rviz_process.poll() is None:
        _rviz_process.terminate()
        logger.info("RViz (PID %d) terminated", _rviz_process.pid)
        return {"status": "closed"}
    return {"status": "not_running"}


def get_rviz_status() -> dict:
    """Return ``{"running": bool}`` reflecting current RViz subprocess state."""
    running = _rviz_process is not None and _rviz_process.poll() is None
    return {"running": running}
