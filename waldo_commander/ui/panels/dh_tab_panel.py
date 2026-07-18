"""DH Parameter tab panel for Waldo Commander.

Renders inline (no dialog) inside a tab panel.
Call ``create_dh_tab_content()`` inside a ``ui.tab_panel`` context.
Returns the ``ui.timer`` so the caller can activate/deactivate it
based on tab visibility.
"""

from __future__ import annotations

import logging
import math
import threading
import time

from nicegui import ui

logger = logging.getLogger(__name__)

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

_EXP_JOINT_LABELS = ["Base", "Shoulder", "Elbow", "Wrist 1", "Wrist 2", "Wrist 3"]

_EXP_THETA_DEFAULTS_DEG = [90.0, -90.0, 180.0, 0.0, 0.0, 180.0]

_plot_thread: threading.Thread | None = None


def _compute_fk_positions(
    dh_params: list[dict],
) -> list[tuple[float, float, float]]:
    """Compute joint frame origins using Modified DH (Craig's convention).

    Args:
        dh_params: list of 6 dicts with keys:
                   a (mm), alpha_deg, d (mm), theta_deg
    Returns:
        List of 7 (x, y, z) tuples in mm — base frame + 6 joint frames
        Index 0 = world/base origin, index 1-6 = joint frame origins
    """
    import numpy as np
    import math

    T = np.eye(4)
    positions = [(0.0, 0.0, 0.0)]  # base frame origin

    for p in dh_params:
        a     = p["a"]          # mm
        alpha = math.radians(p["alpha_deg"])
        d     = p["d"]          # mm
        theta = math.radians(p["theta_deg"])

        # Modified DH transformation matrix (Craig's convention)
        ct, st = math.cos(theta), math.sin(theta)
        ca, sa = math.cos(alpha), math.sin(alpha)

        Ti = np.array([
            [ ct,    -st,     0,    a   ],
            [ st*ca,  ct*ca, -sa,  -d*sa],
            [ st*sa,  ct*sa,  ca,   d*ca],
            [ 0,      0,      0,    1   ],
        ])

        T = T @ Ti
        x, y, z = T[0, 3], T[1, 3], T[2, 3]
        positions.append((float(x), float(y), float(z)))

    return positions  # 7 positions: base + J1..J6


def _plot_stick_diagram(
    positions: list[tuple[float, float, float]],
    dh_params: list[dict],
) -> threading.Thread:
    """Open matplotlib window in a separate thread to avoid uvloop conflict."""

    def _run() -> None:
        import matplotlib
        matplotlib.use("TkAgg")
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

        plt.close("all")  # close any existing figures first — safety net

        xs = [p[0] for p in positions]
        ys = [p[1] for p in positions]
        zs = [p[2] for p in positions]

        fig = plt.figure(figsize=(8, 7))
        ax = fig.add_subplot(111, projection="3d")
        fig.suptitle("Stick Diagram 3D — DH Parameter Eksperimen", fontsize=13)

        # Stick lines
        ax.plot(xs, ys, zs, "-o", color="steelblue", linewidth=2,
                markersize=6, label="Link")

        # Base marker (square)
        ax.scatter(xs[0], ys[0], zs[0], color="green", s=120,
                   marker="s", label="Base", zorder=5)

        # End-effector marker (star)
        ax.scatter(xs[-1], ys[-1], zs[-1], color="red", s=200,
                   marker="*", label="End-effector", zorder=5)

        # Joint markers (intermediate points)
        ax.scatter(xs[1:-1], ys[1:-1], zs[1:-1],
                   color="steelblue", s=60, zorder=4)

        # Labels per joint
        joint_names = ["Base", "J1", "J2", "J3", "J4", "J5", "J6"]
        for i, (x, y, z) in enumerate(zip(xs, ys, zs)):
            ax.text(x, y, z, f"  {joint_names[i]}", fontsize=7,
                    color="gray")

        ax.set_xlabel("X (mm)")
        ax.set_ylabel("Y (mm)")
        ax.set_zlabel("Z (mm)")
        ax.legend(fontsize=8)
        ax.grid(True)

        # Default viewing angle: slight elevation, rotated to show arm
        ax.view_init(elev=20, azim=45)

        plt.tight_layout()
        plt.show(block=True)  # blocking — Tkinter runs its own mainloop here

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return thread


def create_dh_tab_content() -> ui.timer:
    """Render DH parameter tab with Realtime/Eksperimen sub-tabs.

    Returns the inactive ``ui.timer`` driving the Realtime sub-tab so the
    caller can activate/deactivate it based on outer tab visibility.
    """
    from waldo_commander.state import robot_state

    theta_labels: list = []
    row_elements: list = []
    last_angles: list[float | None] = [None] * 6
    last_change_times: list[float] = [0.0] * 6

    with ui.tabs() as dh_sub_tabs:
        ui.tab(name="realtime", label="Realtime")
        ui.tab(name="eksperimen", label="Eksperimen")

    with ui.tab_panels(dh_sub_tabs, value="realtime").classes("w-full"):
        with ui.tab_panel("realtime"):
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

        with ui.tab_panel("eksperimen"):
            ui.label(
                "⚠ Mode Eksperimen: nilai ini tidak mencerminkan robot asli"
            ).classes("text-xs text-amber-400 font-medium mb-2")

            exp_inputs: list[list[ui.number]] = []

            with ui.row().classes("w-full gap-1 items-center").style(
                "display: grid; grid-template-columns: 80px repeat(4, 1fr);"
            ):
                ui.label("Joint").classes("text-xs text-gray-400 font-bold")
                ui.label("a (mm)").classes("text-xs text-gray-400 font-bold")
                ui.label("α (°)").classes("text-xs text-gray-400 font-bold")
                ui.label("d (mm)").classes("text-xs text-gray-400 font-bold")
                ui.label("θ (°)").classes("text-xs text-gray-400 font-bold")

            for i, name in enumerate(_EXP_JOINT_LABELS):
                _, a_def, alpha_def, d_def, _note = _DH_PARAMS[i]
                theta_def = _EXP_THETA_DEFAULTS_DEG[i]

                with ui.row().classes("w-full gap-1 items-center").style(
                    "display: grid; grid-template-columns: 80px repeat(4, 1fr);"
                ):
                    ui.label(name).classes("text-sm font-medium")
                    a_in = ui.number(value=a_def, format="%.2f", step=1.0).classes("w-full")
                    alpha_in = ui.number(value=alpha_def, format="%.2f", step=1.0).classes("w-full")
                    d_in = ui.number(value=d_def, format="%.2f", step=1.0).classes("w-full")
                    theta_in = ui.number(value=theta_def, format="%.2f", step=1.0).classes("w-full")

                exp_inputs.append([a_in, alpha_in, d_in, theta_in])

            def handle_reset() -> None:
                for i, row in enumerate(exp_inputs):
                    _, a_def, alpha_def, d_def, _note = _DH_PARAMS[i]
                    theta_def = _EXP_THETA_DEFAULTS_DEG[i]
                    row[0].set_value(a_def)
                    row[1].set_value(alpha_def)
                    row[2].set_value(d_def)
                    row[3].set_value(theta_def)

            def handle_plot() -> None:
                global _plot_thread
                if _plot_thread is not None and _plot_thread.is_alive():
                    ui.notify("Plot sedang terbuka", type="warning")
                    return

                # Read all 24 input values from exp_inputs[joint][a,α,d,θ]
                params = []
                for row in exp_inputs:
                    a_val     = row[0].value if row[0].value is not None else 0.0
                    alpha_val = row[1].value if row[1].value is not None else 0.0
                    d_val     = row[2].value if row[2].value is not None else 0.0
                    theta_val = row[3].value if row[3].value is not None else 0.0
                    params.append({
                        "a":         float(a_val),
                        "alpha_deg": float(alpha_val),
                        "d":         float(d_val),
                        "theta_deg": float(theta_val),
                    })

                try:
                    positions = _compute_fk_positions(params)
                    _plot_thread = _plot_stick_diagram(positions, params)
                    ui.notify("Plot ditampilkan di window terpisah", type="positive")
                except Exception as exc:
                    logger.warning("DH plot failed: %s", exc)
                    ui.notify(f"Plot gagal: {exc}", type="negative")

            with ui.row().classes("w-full gap-2 mt-2"):
                ui.button("Reset ke Default", on_click=handle_reset)
                ui.button("Plot Stick Diagram", on_click=handle_plot)

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

    timer = ui.timer(0.1, update_fn, active=False)

    def handle_sub_tab(e) -> None:
        if e.args == "realtime":
            timer.activate()
        else:
            timer.deactivate()

    dh_sub_tabs.on("update:model-value", handle_sub_tab)

    return timer
