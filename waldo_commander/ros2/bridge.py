"""ROS 2 bridge: singleton rclpy node with MoveIt 2 IK client.

All rclpy imports are guarded so this module is safe to import when
ROS 2 is not installed — callers check ROS2_AVAILABLE before use.
"""

from __future__ import annotations

import logging
import math
import threading

logger = logging.getLogger(__name__)

try:
    import rclpy
    from moveit_msgs.srv import GetPositionIK
    from rclpy.node import Node as _RosNodeBase

    ROS2_AVAILABLE = True
except ImportError:
    rclpy = None  # type: ignore[assignment]
    GetPositionIK = None  # type: ignore[assignment]
    _RosNodeBase = object  # type: ignore[assignment,misc]
    ROS2_AVAILABLE = False


class WaldoROS2Bridge(_RosNodeBase):  # type: ignore[misc]
    """Singleton rclpy node that holds the MoveIt 2 IK service client.

    Use ``get_instance()`` — never instantiate directly.
    The spin loop runs in a daemon thread so it never blocks Waldo's asyncio loop.
    """

    _instance: WaldoROS2Bridge | None = None
    _spin_thread: threading.Thread | None = None

    def __init__(self) -> None:
        if ROS2_AVAILABLE:
            super().__init__("waldo_ros2_bridge")
            self._ik_client = self.create_client(GetPositionIK, "/compute_ik")

    @classmethod
    def get_instance(cls) -> WaldoROS2Bridge:
        """Return the singleton bridge, initialising rclpy on first call.

        Raises RuntimeError if ROS 2 is not installed.
        """
        if not ROS2_AVAILABLE:
            raise RuntimeError("ROS 2 unavailable")
        if cls._instance is None:
            rclpy.init()
            cls._instance = cls()
            cls._spin_thread = threading.Thread(
                target=rclpy.spin,
                args=(cls._instance,),
                daemon=True,  # daemon=True: shutdown does not block on this thread
            )
            cls._spin_thread.start()
            logger.info("WaldoROS2Bridge initialised and spin thread started")
        return cls._instance

    def compute_ik_sync(self, x: float, y: float, z: float) -> dict:
        """Compute IK for a Cartesian target synchronously.

        Safe to call from any thread via ``asyncio.run_in_executor``.
        Returns a dict with keys:
          success (bool), joint_angles_rad (list), joint_angles_deg (list)
          — or — success=False, reason (str) on failure.
        """
        if not self._ik_client.wait_for_service(timeout_sec=2.0):
            return {"success": False, "reason": "MoveIt 2 service not running"}

        req = GetPositionIK.Request()
        req.ik_request.group_name = "arm"
        req.ik_request.pose_stamped.header.frame_id = "base_link"
        req.ik_request.pose_stamped.pose.position.x = x
        req.ik_request.pose_stamped.pose.position.y = y
        req.ik_request.pose_stamped.pose.position.z = z
        req.ik_request.pose_stamped.pose.orientation.w = 1.0  # upright orientation

        future = self._ik_client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)

        if future.result() is None:
            return {"success": False, "reason": "IK failed — pose not reachable"}

        result = future.result()
        if result.error_code.val == 1:  # MoveItErrorCodes.SUCCESS
            angles_rad = list(result.solution.joint_state.position)
            angles_deg = [math.degrees(a) for a in angles_rad]
            return {
                "success": True,
                "joint_angles_rad": angles_rad,
                "joint_angles_deg": angles_deg,
            }

        return {"success": False, "reason": "IK failed — pose not reachable"}
