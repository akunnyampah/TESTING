"""ROS 2 integration module for Waldo Commander.

All public symbols degrade gracefully when rclpy is not installed.
"""

from .bridge import ROS2_AVAILABLE, WaldoROS2Bridge
from .config import WORKSPACE_LIMITS, check_workspace
from .rviz_launcher import close_rviz, get_rviz_status, launch_rviz

__all__ = [
    "ROS2_AVAILABLE",
    "WaldoROS2Bridge",
    "WORKSPACE_LIMITS",
    "check_workspace",
    "launch_rviz",
    "close_rviz",
    "get_rviz_status",
]
