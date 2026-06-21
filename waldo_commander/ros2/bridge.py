"""ROS 2 bridge: singleton rclpy node with /joint_states publisher.

All rclpy imports are guarded so this module is safe to import when
ROS 2 is not installed — callers check ROS2_AVAILABLE before use.
"""

from __future__ import annotations

import logging
import math as _math
import threading

logger = logging.getLogger(__name__)

try:
    import rclpy
    from rclpy.node import Node as _RosNodeBase
    from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
    from sensor_msgs.msg import JointState

    ROS2_AVAILABLE = True
except ImportError:
    rclpy = None  # type: ignore[assignment]
    _RosNodeBase = object  # type: ignore[assignment,misc]
    JointState = None  # type: ignore[assignment]
    QoSProfile = None  # type: ignore[assignment]
    ReliabilityPolicy = None  # type: ignore[assignment]
    DurabilityPolicy = None  # type: ignore[assignment]
    HistoryPolicy = None  # type: ignore[assignment]
    ROS2_AVAILABLE = False

_JOINT_NAMES = ["L1", "L2", "L3", "L4", "L5", "L6"]

# BEST_EFFORT matches rsp's QoS override (set by parol6_moveit rsp.launch.py):
#   qos_overrides./joint_states.subscription.reliability = best_effort
# Using RELIABLE (the rclpy shorthand default) causes silent delivery failure
# in Fast-DDS Jazzy on loopback when the subscriber is BEST_EFFORT.
_JS_QOS: "QoSProfile | None" = None


def _to_rviz_angles(angles: list[float]) -> list[float]:
    """Convert Waldo IK angles to RViz/parol6.urdf display convention.

    Waldo uses calibrated PAROL6.urdf (all joints +Z axis).
    RViz uses parol6.urdf (L3-L6 on -Z axis, different joint origins).
    This mapping is derived from URDF comparison + visual verification.

    Args:
        angles: [L1..L6] in radians, Waldo convention
    Returns:
        [L1..L6] in radians, RViz/parol6.urdf convention
    """
    return [
        -angles[0],                        # L1: flip
        (angles[1] + _math.pi / 2),        # L2: π/2 offset (Waldo home=-π/2, RViz home=0)
        -(angles[2] - _math.pi),           # L3: flip + π offset
        -angles[3] + _math.pi,             # L4: flip + π offset
        angles[4],                         # L5: unchanged
        -angles[5],                        # L6: flip
    ]


class WaldoROS2Bridge(_RosNodeBase):  # type: ignore[misc]
    """Singleton rclpy node that publishes /joint_states for RViz.

    Use ``get_instance()`` — never instantiate directly.
    The spin loop runs in a daemon thread so it never blocks Waldo's asyncio loop.
    """

    _instance: "WaldoROS2Bridge | None" = None
    _spin_thread: "threading.Thread | None" = None

    def __init__(self) -> None:
        if ROS2_AVAILABLE:
            global _JS_QOS
            super().__init__("waldo_ros2_bridge")
            _JS_QOS = QoSProfile(
                depth=10,
                reliability=ReliabilityPolicy.BEST_EFFORT,
                durability=DurabilityPolicy.VOLATILE,
                history=HistoryPolicy.KEEP_LAST,
            )
            self._last_angles: list[float] | None = None
            self._js_pub = self.create_publisher(JointState, "/joint_states", _JS_QOS)
            self._pub_timer = self.create_timer(0.1, self._timer_publish_cb)

    @classmethod
    def get_instance(cls) -> "WaldoROS2Bridge":
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

    def _timer_publish_cb(self) -> None:
        if self._last_angles is None:
            return
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "world"
        msg.name = _JOINT_NAMES
        msg.position = _to_rviz_angles(self._last_angles)
        self._js_pub.publish(msg)

    def publish_joint_states(self, angles_rad: list[float]) -> None:
        """Publish joint angles to /joint_states for RViz display.

        Args:
            angles_rad: Joint angles in radians, ordered [L1..L6].
        """
        self._last_angles = list(angles_rad)
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "world"
        msg.name = _JOINT_NAMES
        msg.position = _to_rviz_angles(angles_rad)
        self._js_pub.publish(msg)
        logger.debug("[JS] angles_rad=%s", [round(a, 3) for a in angles_rad])

    def update_angles(self, angles_rad: list[float]) -> None:
        """Update angles for next timer publish without immediate publish.

        Called from Waldo's status loop (~20Hz). The _timer_publish_cb at
        10Hz picks up the new values and publishes to /joint_states.

        Args:
            angles_rad: Current joint angles in radians [L1..L6],
                        copied from robot_state.angles.rad.
        """
        self._last_angles = list(angles_rad)
