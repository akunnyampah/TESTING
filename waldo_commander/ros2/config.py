"""Workspace configuration and safety limits for ROS 2 integration."""

from typing import Tuple

# Bounding box workspace for PAROL6 — adjust to match physical setup
WORKSPACE_LIMITS: dict[str, tuple[float, float]] = {
    "x": (-0.35, 0.35),  # meters
    "y": (-0.35, 0.35),  # meters
    "z": (0.0, 0.45),    # meters — floor of 0.0 prevents sub-table targets
}


def check_workspace(x: float, y: float, z: float) -> Tuple[bool, str]:
    """Return (is_safe, reason) for the given Cartesian target.

    Reason is an empty string when the target is within limits.
    """
    lim = WORKSPACE_LIMITS

    if not (lim["x"][0] <= x <= lim["x"][1]):
        return (
            False,
            f"Out of workspace: X={x:.3f} exceeds limit "
            f"({lim['x'][0]:.3f} to {lim['x'][1]:.3f} m)",
        )
    if not (lim["y"][0] <= y <= lim["y"][1]):
        return (
            False,
            f"Out of workspace: Y={y:.3f} exceeds limit "
            f"({lim['y'][0]:.3f} to {lim['y'][1]:.3f} m)",
        )
    if not (lim["z"][0] <= z <= lim["z"][1]):
        return (
            False,
            f"Out of workspace: Z={z:.3f} exceeds limit "
            f"({lim['z'][0]:.3f} to {lim['z'][1]:.3f} m)",
        )

    return True, ""
