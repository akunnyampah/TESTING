"""Workspace configuration and safety limits for ROS 2 integration."""

from typing import Tuple

# Workspace limits derived from PAROL6 workspace hull STL
# (~/.waldo-commander/workspace_hull.stl, generated 2026-06-13)
# Values are 95th-percentile hull extents — excludes near-singular
# configurations at workspace boundary.
# Z min = 0.0 kept for table clearance safety.
# Full hull extents: X(-0.369,+0.446) Y(-0.446,+0.446) Z(-0.122,+0.533)
WORKSPACE_LIMITS: dict[str, tuple[float, float]] = {
    "x": (-0.34, 0.43),  # meters
    "y": (-0.43, 0.43),  # meters
    "z": (0.0, 0.53),    # meters — floor of 0.0 kept for table clearance
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
