"""ROS 2 tab panel for Waldo Commander.

Call ``create_ros2_tab_content()`` inside a ``ui.tab_panel`` context.
Returns a dict of UI element references for testing.
"""

from __future__ import annotations

import logging

from nicegui import ui

from waldo_commander.ros2.rviz_launcher import close_rviz, get_rviz_status, launch_rviz

try:
    from waldo_commander.ros2.bridge import ROS2_AVAILABLE
except ImportError:
    ROS2_AVAILABLE = False

logger = logging.getLogger(__name__)


def create_ros2_tab_content() -> dict:
    """Render the ROS 2 tab and return a dict of UI element references."""

    with ui.column().classes("w-full gap-3 p-3 overflow-y-auto").style(
        "max-height: calc(100vh - 80px)"
    ):
        ui.label("RViz").classes("text-xs text-gray-400 uppercase tracking-wide")
        rviz_btn = ui.button("Launch RViz").mark("ros2-rviz-btn")

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
                try:
                    from waldo_commander.state import robot_state
                    from waldo_commander.ros2.bridge import WaldoROS2Bridge
                    if ROS2_AVAILABLE:
                        WaldoROS2Bridge.get_instance().publish_joint_states(
                            list(robot_state.angles.rad)
                        )
                except Exception:
                    pass  # non-critical, RViz will get data from next status update
            else:
                ui.notify(
                    result.get("reason", "Failed to launch RViz."), type="negative"
                )

    rviz_btn.on("click", handle_rviz)

    return {
        "rviz_btn": rviz_btn,
    }
