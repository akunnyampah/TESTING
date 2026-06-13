"""FastAPI endpoints for ROS 2 XYZ target feature.

Imported by main.py to register routes with ng_app (NiceGUI/FastAPI).
"""
from __future__ import annotations

import asyncio
import logging

from nicegui import app as ng_app
from pydantic import BaseModel

from waldo_commander.ros2.config import check_workspace
from waldo_commander.ros2.rviz_launcher import close_rviz, get_rviz_status, launch_rviz

try:
    from waldo_commander.ros2.bridge import ROS2_AVAILABLE, WaldoROS2Bridge
except ImportError:
    ROS2_AVAILABLE = False
    WaldoROS2Bridge = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


class _PreviewRequest(BaseModel):
    x: float
    y: float
    z: float


class _ExecuteRequest(BaseModel):
    joint_angles_deg: list[float]


@ng_app.post("/api/ros/preview")
async def _ros_preview(body: _PreviewRequest):
    if not ROS2_AVAILABLE:
        return {"success": False, "reason": "ROS 2 unavailable"}
    ok, reason = check_workspace(body.x, body.y, body.z)
    if not ok:
        return {"success": False, "reason": reason}
    try:
        loop = asyncio.get_running_loop()
        bridge = WaldoROS2Bridge.get_instance()
        result: dict = await loop.run_in_executor(
            None, bridge.compute_ik_sync, body.x, body.y, body.z
        )
    except Exception as exc:
        logger.warning("ROS 2 bridge error in /api/ros/preview: %s", exc)
        return {"success": False, "reason": str(exc)}
    return result


@ng_app.post("/api/ros/execute")
async def _ros_execute(body: _ExecuteRequest):
    from waldo_commander.state import ui_state  # avoid circular import at module load

    try:
        await ui_state.control_panel.client.teleport(body.joint_angles_deg)
        return {"success": True}
    except Exception as exc:
        logger.warning("Execute failed in /api/ros/execute: %s", exc)
        return {"success": False, "reason": str(exc)}


@ng_app.get("/api/ros/status")
async def _ros_status():
    return {"ros2_available": ROS2_AVAILABLE}


@ng_app.post("/api/rviz/launch")
async def _rviz_launch():
    if not ROS2_AVAILABLE:
        return {"status": "error", "reason": "ROS 2 unavailable"}
    return launch_rviz()


@ng_app.post("/api/rviz/close")
async def _rviz_close():
    return close_rviz()


@ng_app.get("/api/rviz/status")
async def _rviz_status():
    return get_rviz_status()
