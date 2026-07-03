"""DH Parameter tab panel for Waldo Commander.

Renders inline (no dialog) inside a tab panel.
Call ``create_dh_tab_content()`` inside a ``ui.tab_panel`` context.
Returns the ``ui.timer`` so the caller can activate/deactivate it
based on tab visibility.
"""

from __future__ import annotations

import math
import time

from nicegui import ui

_DH_PARAMS = [
    ("J1",   0.00,    0.0,   110.50, ""),
    ("J2",  23.42,  -90.0,     0.00, ""),
    ("J3", 180.00,  180.0,     0.00, ""),
    ("J4", -43.50,   90.0,  -176.35, "negative a,d: geometrically valid"),
    ("J5",   0.00,  -90.0,     0.00, ""),
    ("J6",   0.00,   90.0,   -37.00, ""),
]

_DH_LIMITS_DEG = [
    (-123.0,  123.0),
    (-145.0,   -3.4),
    ( 107.9,  287.9),
    (-105.5,  105.5),
    ( -90.0,   90.0),
    (   0.0,  360.0),
]


def create_dh_tab_content() -> ui.timer:
    """Render DH parameter table inline. Returns inactive timer."""
    from waldo_commander.state import robot_state

    theta_labels: list = []
    row_elements: list = []
    last_angles: list[float | None] = [None] * 6
    last_change_times: list[float] = [0.0] * 6

    ui.label(
        "Modified DH (Craig's convention) | θ = joint variable (realtime)"
    ).classes("text-xs text-gray-400 mb-1")

    with ui.row().classes("w-full gap-0 items-center border-b border-gray-600 pb-1"):
        ui.label("Joint").classes("w-10 text-xs text-gray-400 font-bold")
        ui.label("a (mm)").classes("w-[90px] text-xs text-gray-400 font-bold text-right")
        ui.label("α (°)").classes("w-[70px] text-xs text-gray-400 font-bold text-right")
        ui.label("d (mm)").classes("w-[90px] text-xs text-gray-400 font-bold text-right")
        ui.label("θ (°)").classes("flex-1 text-xs text-gray-400 font-bold text-right")

    for i, (joint, a, alpha, d, _note) in enumerate(_DH_PARAMS):
        lo, hi = _DH_LIMITS_DEG[i]
        row_el = ui.row().classes("w-full gap-0 items-center rounded py-0.5 px-1")
        with row_el:
            ui.label(joint).classes("w-10 text-sm font-mono")
            ui.label(f"{a:.2f}").classes("w-[90px] text-sm font-mono text-right")
            ui.label(f"{alpha:.1f}").classes("w-[70px] text-sm font-mono text-right")
            ui.label(f"{d:.2f}").classes("w-[90px] text-sm font-mono text-right")
            with ui.column().classes("flex-1 gap-0 items-end"):
                t_lbl = (
                    ui.label("—")
                    .classes("text-sm font-mono")
                    .mark(f"dh-theta-{i}")
                )
                ui.label(f"[{lo:.1f}°, {hi:.1f}°]").classes("text-xs text-gray-500")
        theta_labels.append(t_lbl)
        row_elements.append(row_el)

    ui.separator().classes("my-1")
    ui.label(
        "L4 negative a/d values are geometrically correct — result of α=90° "
        "mapping Y-offset to −d in DH convention"
    ).classes("text-xs text-gray-500 italic")

    def update_fn() -> None:
        now = time.monotonic()
        try:
            angles_rad = robot_state.angles.rad
        except Exception:
            return
        for i, t_lbl in enumerate(theta_labels):
            if i >= len(angles_rad):
                break
            deg = math.degrees(angles_rad[i])
            t_lbl.set_text(f"{deg:.1f}°")
            prev = last_angles[i]
            if prev is not None and abs(deg - prev) > 0.1:
                row_elements[i].classes(remove="bg-transparent")
                row_elements[i].classes(add="bg-warning")
                last_change_times[i] = now
            elif last_change_times[i] > 0 and now - last_change_times[i] > 0.5:
                row_elements[i].classes(remove="bg-warning")
                last_change_times[i] = 0.0
            last_angles[i] = deg

    return ui.timer(0.1, update_fn, active=False)
