"""ROS 2 tab panel for Waldo Commander.

Call ``create_ros2_tab_content()`` inside a ``ui.tab_panel`` context.
Returns a dict of UI element references for testing.
"""

from __future__ import annotations

import logging
import math

import numpy as np
from nicegui import ui

from waldo_commander.ros2.config import check_workspace
from waldo_commander.ros2.rviz_launcher import close_rviz, get_rviz_status, launch_rviz

try:
    from waldo_commander.ros2.bridge import ROS2_AVAILABLE, WaldoROS2Bridge
except ImportError:
    ROS2_AVAILABLE = False
    WaldoROS2Bridge = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


def create_ros2_tab_content() -> dict:
    """Render the ROS 2 tab and return a dict of UI element references."""

    _last_ik: dict = {}  # stores the most recent successful IK result

    with ui.column().classes("w-full gap-3 p-3"):

        # ── Target Coordinate ─────────────────────────────────────────
        ui.label("Target Coordinate").classes(
            "text-xs text-gray-400 uppercase tracking-wide"
        )
        with ui.column().classes("gap-1 w-full"):
            x_input = (
                ui.number("X (mm)", value=0.0, step=1.0, format="%.1f")
                .classes("w-full")
                .mark("ros2-x-input")
            )
            y_input = (
                ui.number("Y (mm)", value=300.0, step=1.0, format="%.1f")
                .classes("w-full")
                .mark("ros2-y-input")
            )
            z_input = (
                ui.number("Z (mm)", value=100.0, step=1.0, format="%.1f")
                .classes("w-full")
                .mark("ros2-z-input")
            )

        # Status badge — hidden until Preview is clicked
        status_label = ui.label("").classes("text-sm hidden").mark("ros2-status")

        # Action buttons
        with ui.row().classes("gap-2 w-full"):
            preview_btn = ui.button("Preview").mark("ros2-preview-btn")
            execute_btn = (
                ui.button("Execute").props("disabled").mark("ros2-execute-btn")
            )

        ui.separator()

        # ── RViz ──────────────────────────────────────────────────────
        ui.label("RViz").classes("text-xs text-gray-400 uppercase tracking-wide")
        rviz_btn = ui.button("Launch RViz").mark("ros2-rviz-btn")

    # ── Helpers ───────────────────────────────────────────────────────

    def _set_status(success: bool | None, message: str) -> None:
        """Update the status badge. success=None means loading/grey."""
        status_label.set_text(message)
        status_label.classes(remove="hidden text-positive text-negative text-grey")
        if success is True:
            status_label.classes(add="text-positive")
        elif success is False:
            status_label.classes(add="text-negative")
        else:
            status_label.classes(add="text-grey")

    def _reset_status() -> None:
        status_label.classes(add="hidden")
        status_label.set_text("")
        execute_btn.props("disabled")
        _last_ik.clear()

    def _update_viewer(joint_angles_rad: list[float]) -> None:
        """Send IK joint angles to the 3D viewer — visual preview only, no robot movement."""
        from waldo_commander.state import ui_state  # avoid circular import at module level

        if ui_state.urdf_scene is None:
            return
        try:
            buf = np.array(joint_angles_rad, dtype=np.float64)
            ui_state.urdf_scene.set_axis_values(buf)
        except Exception as exc:
            logger.warning("3D viewer update failed: %s", exc)

    # ── Event handlers ────────────────────────────────────────────────

    async def handle_preview() -> None:
        if not ROS2_AVAILABLE:
            _set_status(False, "ROS 2 unavailable")
            execute_btn.props("disabled")
            return

        x = (x_input.value if x_input.value is not None else 0.0) / 1000.0
        y = (y_input.value if y_input.value is not None else 0.0) / 1000.0
        z = (z_input.value if z_input.value is not None else 0.0) / 1000.0

        # Workspace bounding-box check (fast, no thread needed)
        ok, reason = check_workspace(x, y, z)
        if not ok:
            _set_status(False, reason)
            execute_btn.props("disabled")
            _last_ik.clear()
            return

        _set_status(None, "Computing...")
        preview_btn.props("disabled")
        try:
            from waldo_commander.services.urdf_scene.ik_solver import EditingIKSolver
            from waldo_commander.state import robot_state, ui_state

            solver = EditingIKSolver(robot=ui_state.active_robot)
            ik = solver.solve(
                target_pos=np.array([x, y, z]),
                current_angles=robot_state.angles.rad,
                throttle=False,
                target_orientation=None,
            )
        except Exception as exc:
            logger.warning("ROS 2 bridge error during preview: %s", exc)
            _set_status(False, "IK solver error")
            execute_btn.props("disabled")
            _last_ik.clear()
            return
        finally:
            preview_btn.props(remove="disabled")

        if ik is None or not ik.success:
            _last_ik.clear()
            _set_status(False, "IK failed — pose not reachable")
            execute_btn.props("disabled")
            return

        try:
            WaldoROS2Bridge.get_instance().publish_joint_states(ik.angles)
        except Exception as exc:
            logger.warning("ROS 2 publish failed (preview still valid): %s", exc)

        result = {
            "success": True,
            "joint_angles_rad": ik.angles,
            "joint_angles_deg": [math.degrees(a) for a in ik.angles],
        }
        _last_ik.clear()
        _last_ik.update(result)
        _set_status(True, "Pose reachable")
        execute_btn.props(remove="disabled")
        _update_viewer(result["joint_angles_rad"])

    async def handle_execute() -> None:
        if not _last_ik.get("success"):
            ui.notify("Run Preview first to validate the pose.", type="warning")
            return

        from waldo_commander.state import ui_state  # avoid circular import

        angles_deg: list[float] = _last_ik["joint_angles_deg"]
        execute_btn.props("disabled")
        try:
            await ui_state.control_panel.client.teleport(angles_deg)
            ui.notify("Execute sent.", type="positive")
        except Exception as exc:
            logger.warning("Execute failed: %s", exc)
            ui.notify(f"Execute failed: {exc}", type="negative")
        _last_ik.clear()

    async def handle_rviz() -> None:
        status = get_rviz_status()
        if status["running"]:
            result = close_rviz()
            if result["status"] == "closed":
                rviz_btn.set_text("Launch RViz")
                ui.notify("RViz closed.", type="positive")
            else:
                ui.notify("RViz was not running.", type="warning")
        else:
            if not ROS2_AVAILABLE:
                ui.notify("ROS 2 unavailable — cannot launch RViz.", type="negative")
                return
            result = launch_rviz()
            if result["status"] in ("launched", "already_running"):
                rviz_btn.set_text("Close RViz")
                ui.notify("RViz launched.", type="positive")
            else:
                ui.notify(
                    result.get("reason", "Failed to launch RViz."), type="negative"
                )

    # Wire input-change reset
    x_input.on("update:model-value", lambda _: _reset_status())
    y_input.on("update:model-value", lambda _: _reset_status())
    z_input.on("update:model-value", lambda _: _reset_status())

    # Wire button handlers
    preview_btn.on("click", handle_preview)
    execute_btn.on("click", handle_execute)
    rviz_btn.on("click", handle_rviz)

    return {
        "x": x_input,
        "y": y_input,
        "z": z_input,
        "status": status_label,
        "preview_btn": preview_btn,
        "execute_btn": execute_btn,
        "rviz_btn": rviz_btn,
    }
