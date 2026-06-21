"""FastAPI endpoints for ROS 2 XYZ target feature.

Imported by main.py to register routes with ng_app (NiceGUI/FastAPI).
"""
from __future__ import annotations

import logging
import math

import numpy as np

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
        from waldo_commander.services.urdf_scene.ik_solver import EditingIKSolver
        from waldo_commander.state import robot_state, ui_state

        solver = EditingIKSolver(robot=ui_state.active_robot)
        result = solver.solve(
            target_pos=np.array([body.x, body.y, body.z]),
            current_angles=robot_state.angles.rad,
            throttle=False,
            target_orientation=None,
        )
    except Exception as exc:
        logger.warning("IK solver error in /api/ros/preview: %s", exc)
        return {"success": False, "reason": str(exc)}

    if result is None:
        return {"success": False, "reason": "IK solver returned no result"}
    if not result.success:
        return {"success": False, "reason": "IK failed — pose not reachable"}

    try:
        WaldoROS2Bridge.get_instance().publish_joint_states(result.angles)
    except Exception as exc:
        logger.warning("ROS 2 publish failed (preview still valid): %s", exc)

    angles_deg = [math.degrees(a) for a in result.angles]
    return {
        "success": True,
        "joint_angles_rad": result.angles,
        "joint_angles_deg": angles_deg,
    }


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
