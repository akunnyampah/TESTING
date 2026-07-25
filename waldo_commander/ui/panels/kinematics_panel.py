"""Kinematics panel (IK / FK) for Waldo Commander.

Always-visible panel rendered above the Jog panel at bottom-right.
Call ``KinematicsPanel().build()`` inside a positioning wrapper —
the card itself carries no absolute positioning.
"""

from __future__ import annotations

import logging
import math

import numpy as np
from nicegui import ui

from waldo_commander.ros2.config import check_workspace

logger = logging.getLogger(__name__)

_DH_LIMITS_DEG = [
    (-123.0,  123.0),   # J1
    (-145.0,   -3.4),   # J2
    ( 107.9,  287.9),   # J3
    (-105.5,  105.5),   # J4
    ( -90.0,   90.0),   # J5
    (   0.0,  360.0),   # J6
]


class KinematicsPanel:
    """IK/FK panel displayed above the Jog panel."""

    def build(self) -> dict:
        """Render the kinematics card. Returns UI element refs for testing."""
        _last_ik: dict = {}
        _fk_last_angles: list[float] = []
        _fk_last_pose: list[float] = []

        with ui.card().classes("overlay-card gap-1"):
            with ui.tabs().props("dense").classes("kin-tabs") as kin_tabs:
                ik_tab = ui.tab("Inverse Kinematics").mark("tab-ik")
                fk_tab = ui.tab("Forward Kinematics").mark("tab-fk")
            kin_tabs.value = ik_tab

            with ui.tab_panels(kin_tabs, value=ik_tab).classes("kin-panels w-full"):
                # ── IK tab ────────────────────────────────────────────────
                with ui.tab_panel(ik_tab).classes("gap-1"):
                    with ui.row().classes("gap-2 w-full"):
                        with ui.column().classes("gap-1 flex-1"):
                            ui.label("Position").classes(
                                "text-xs text-gray-400 uppercase tracking-wide"
                            )
                            x_input = (
                                ui.number("X (mm)", value=0.0, step=1.0, format="%.1f")
                                .classes("w-full")
                                .mark("ik-x-input")
                            )
                            y_input = (
                                ui.number("Y (mm)", value=263.8, step=1.0, format="%.1f")
                                .classes("w-full")
                                .mark("ik-y-input")
                            )
                            z_input = (
                                ui.number("Z (mm)", value=279.0, step=1.0, format="%.1f")
                                .classes("w-full")
                                .mark("ik-z-input")
                            )

                        with ui.column().classes("gap-1 flex-1"):
                            ui.label("Orientation").classes(
                                "text-xs text-gray-400 uppercase tracking-wide"
                            )
                            rx_input = (
                                ui.number("Rx (°)", value=90.0, step=1.0, format="%.1f")
                                .classes("w-full")
                                .mark("ik-rx-input")
                            )
                            ry_input = (
                                ui.number("Ry (°)", value=0.0, step=1.0, format="%.1f")
                                .classes("w-full")
                                .mark("ik-ry-input")
                            )
                            rz_input = (
                                ui.number("Rz (°)", value=90.0, step=1.0, format="%.1f")
                                .classes("w-full")
                                .mark("ik-rz-input")
                            )

                    status_label = (
                        ui.label("").classes("text-sm hidden").mark("ik-status")
                    )

                    ui.label("Resulting Joint Angles").classes(
                        "text-xs text-gray-400 uppercase tracking-wide"
                    )
                    with ui.row().classes("gap-2 w-full"):
                        with ui.column().classes("gap-0 flex-1"):
                            ik_out_j1 = ui.label("J1: —").classes("text-sm").mark("ik-out-j1")
                            ik_out_j2 = ui.label("J2: —").classes("text-sm").mark("ik-out-j2")
                            ik_out_j3 = ui.label("J3: —").classes("text-sm").mark("ik-out-j3")
                        with ui.column().classes("gap-0 flex-1"):
                            ik_out_j4 = ui.label("J4: —").classes("text-sm").mark("ik-out-j4")
                            ik_out_j5 = ui.label("J5: —").classes("text-sm").mark("ik-out-j5")
                            ik_out_j6 = ui.label("J6: —").classes("text-sm").mark("ik-out-j6")

                    with ui.row().classes("gap-2 w-full"):
                        preview_btn = ui.button("Calculate").mark("ik-preview-btn")
                        execute_btn = (
                            ui.button("Execute")
                            .props("disabled")
                            .mark("ik-execute-btn")
                        )

                # ── FK tab ────────────────────────────────────────────────
                with ui.tab_panel(fk_tab).classes("gap-1"):
                    ui.label("Joint Angles").classes(
                        "text-xs text-gray-400 uppercase tracking-wide"
                    )
                    with ui.grid(columns=2).classes("w-full gap-x-4 gap-y-1"):
                        fk_j1 = (
                            ui.number("Base (°)", value=90.0, step=1.0, format="%.1f")
                            .classes("w-full").mark("fk-j1-input")
                        )
                        fk_j4 = (
                            ui.number("Wrist 1 (°)", value=0.0, step=1.0, format="%.1f")
                            .classes("w-full").mark("fk-j4-input")
                        )
                        fk_j2 = (
                            ui.number("Shoulder (°)", value=-90.0, step=1.0, format="%.1f")
                            .classes("w-full").mark("fk-j2-input")
                        )
                        fk_j5 = (
                            ui.number("Wrist 2 (°)", value=0.0, step=1.0, format="%.1f")
                            .classes("w-full").mark("fk-j5-input")
                        )
                        fk_j3 = (
                            ui.number("Elbow (°)", value=180.0, step=1.0, format="%.1f")
                            .classes("w-full").mark("fk-j3-input")
                        )
                        fk_j6 = (
                            ui.number("Wrist 3 (°)", value=180.0, step=1.0, format="%.1f")
                            .classes("w-full").mark("fk-j6-input")
                        )

                    ui.label("End Effector Pose").classes(
                        "text-xs text-gray-400 uppercase tracking-wide"
                    )
                    with ui.row().classes("w-full justify-between"):
                        fk_out_x  = ui.label("X:  —").classes("text-sm").mark("fk-out-x")
                        fk_out_y  = ui.label("Y:  —").classes("text-sm").mark("fk-out-y")
                        fk_out_z  = ui.label("Z:  —").classes("text-sm").mark("fk-out-z")
                    with ui.row().classes("w-full justify-between"):
                        fk_out_rx = ui.label("Rx: —").classes("text-sm").mark("fk-out-rx")
                        fk_out_ry = ui.label("Ry: —").classes("text-sm").mark("fk-out-ry")
                        fk_out_rz = ui.label("Rz: —").classes("text-sm").mark("fk-out-rz")

                    fk_warn_label = (
                        ui.label("").classes("text-xs text-orange hidden").mark("fk-warn")
                    )
                    with ui.row().classes("gap-2 w-full"):
                        fk_calc_btn = ui.button("Calculate").mark("fk-calc-btn")
                        fk_execute_btn = (
                            ui.button("Execute")
                            .props("disabled")
                            .mark("fk-execute-btn")
                        )

        # ── Helpers ───────────────────────────────────────────────────────

        def _set_status(success: bool | None, message: str) -> None:
            status_label.set_text(message)
            status_label.classes(remove="hidden text-positive text-negative text-grey")
            if success is True:
                status_label.classes(add="text-positive")
            elif success is False:
                status_label.classes(add="text-negative")
            else:
                status_label.classes(add="text-grey")

        def _reset_ik_joint_outputs() -> None:
            for i, lbl in enumerate(
                [ik_out_j1, ik_out_j2, ik_out_j3, ik_out_j4, ik_out_j5, ik_out_j6]
            ):
                lbl.set_text(f"J{i+1}: —")

        def _reset_status() -> None:
            status_label.classes(add="hidden")
            status_label.set_text("")
            execute_btn.props("disabled")
            _last_ik.clear()
            _reset_ik_joint_outputs()

        def _update_viewer(joint_angles_rad: list[float]) -> None:
            from waldo_commander.state import ui_state  # avoid circular import

            if ui_state.urdf_scene is None:
                return
            try:
                buf = np.array(joint_angles_rad, dtype=np.float64)
                ui_state.urdf_scene.set_axis_values(buf)
            except Exception as exc:
                logger.warning("3D viewer update failed: %s", exc)

        def _fk_reset_outputs() -> None:
            for lbl, txt in [
                (fk_out_x, "X:  —"), (fk_out_y, "Y:  —"), (fk_out_z, "Z:  —"),
                (fk_out_rx, "Rx: —"), (fk_out_ry, "Ry: —"), (fk_out_rz, "Rz: —"),
            ]:
                lbl.set_text(txt)
            fk_warn_label.classes(add="hidden")
            fk_warn_label.set_text("")
            fk_execute_btn.props("disabled")
            _fk_last_angles.clear()
            _fk_last_pose.clear()

        async def handle_fk_calculate() -> None:
            fk_inputs = [fk_j1, fk_j2, fk_j3, fk_j4, fk_j5, fk_j6]
            angles_deg = [
                (inp.value if inp.value is not None else 0.0) for inp in fk_inputs
            ]
            warnings = []
            for i, (deg, (lo, hi)) in enumerate(zip(angles_deg, _DH_LIMITS_DEG), start=1):
                if not (lo <= deg <= hi):
                    warnings.append(f"J{i}={deg:.1f}° outside [{lo:.1f}, {hi:.1f}]")
            if warnings:
                fk_warn_label.set_text("⚠ " + "; ".join(warnings))
                fk_warn_label.classes(remove="hidden")
                fk_execute_btn.props("disabled")
            else:
                fk_warn_label.classes(add="hidden")
                fk_warn_label.set_text("")

            angles_rad = [math.radians(d) for d in angles_deg]
            try:
                from waldo_commander.services.urdf_scene.ik_solver import EditingIKSolver
                from waldo_commander.state import ui_state
                solver = EditingIKSolver(robot=ui_state.active_robot)
                pose = solver.forward_kinematics(angles_rad)
            except Exception as exc:
                logger.warning("FK solver error: %s", exc)
                _fk_reset_outputs()
                fk_warn_label.set_text(f"FK error: {exc}")
                fk_warn_label.classes(remove="hidden")
                return

            fk_out_x.set_text(f"X:  {pose[0] * 1000:.1f} mm")
            fk_out_y.set_text(f"Y:  {pose[1] * 1000:.1f} mm")
            fk_out_z.set_text(f"Z:  {pose[2] * 1000:.1f} mm")
            fk_out_rx.set_text(f"Rx: {math.degrees(pose[3]):.1f}°")
            fk_out_ry.set_text(f"Ry: {math.degrees(pose[4]):.1f}°")
            fk_out_rz.set_text(f"Rz: {math.degrees(pose[5]):.1f}°")
            _update_viewer(angles_rad)
            _fk_last_angles.clear()
            _fk_last_angles.extend(angles_deg)
            _fk_last_pose.clear()
            _fk_last_pose.extend([
                pose[0] * 1000,
                pose[1] * 1000,
                pose[2] * 1000,
                math.degrees(pose[3]),
                math.degrees(pose[4]),
                math.degrees(pose[5]),
            ])
            if not warnings:
                fk_execute_btn.props(remove="disabled")

        async def handle_fk_execute() -> None:
            if not _fk_last_pose:
                ui.notify("Run Calculate first.", type="warning")
                return
            from waldo_commander.state import ui_state
            fk_execute_btn.props("disabled")
            try:
                await ui_state.control_panel.client.move_l(
                    _fk_last_pose, speed=0.5, accel=0.5
                )
                ui.notify("Execute sent.", type="positive")
            except Exception as exc:
                logger.warning("FK Execute failed: %s", exc)
                ui.notify(f"Execute failed: {exc}", type="negative")
            _fk_last_pose.clear()
            _fk_last_angles.clear()

        # ── Event handlers ────────────────────────────────────────────────

        async def handle_preview() -> None:
            x = (x_input.value if x_input.value is not None else 0.0) / 1000.0
            y = (y_input.value if y_input.value is not None else 0.0) / 1000.0
            z = (z_input.value if z_input.value is not None else 0.0) / 1000.0

            ok, reason = check_workspace(x, y, z)
            if not ok:
                _set_status(False, reason)
                execute_btn.props("disabled")
                _last_ik.clear()
                _reset_ik_joint_outputs()
                return

            rx_rad = math.radians(rx_input.value if rx_input.value is not None else 0.0)
            ry_rad = math.radians(ry_input.value if ry_input.value is not None else 0.0)
            rz_rad = math.radians(rz_input.value if rz_input.value is not None else 0.0)

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
                    target_orientation=np.array([rx_rad, ry_rad, rz_rad]),
                )
            except Exception as exc:
                logger.warning("IK solver error: %s", exc)
                _set_status(False, "IK solver error")
                execute_btn.props("disabled")
                _last_ik.clear()
                _reset_ik_joint_outputs()
                return
            finally:
                preview_btn.props(remove="disabled")

            if ik is None or not ik.success:
                _last_ik.clear()
                _set_status(False, "Pose not reachable")
                execute_btn.props("disabled")
                _reset_ik_joint_outputs()
                return

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
            for i, lbl in enumerate(
                [ik_out_j1, ik_out_j2, ik_out_j3, ik_out_j4, ik_out_j5, ik_out_j6]
            ):
                lbl.set_text(f"J{i+1}: {result['joint_angles_deg'][i]:.1f}°")

        async def handle_execute() -> None:
            if not _last_ik.get("success"):
                ui.notify("Run Preview first to validate the pose.", type="warning")
                return

            from waldo_commander.state import ui_state  # avoid circular import

            angles_deg: list[float] = _last_ik["joint_angles_deg"]
            execute_btn.props("disabled")
            try:
                await ui_state.control_panel.client.move_j(angles_deg, speed=0.5, accel=0.5)
                ui.notify("Execute sent.", type="positive")
            except Exception as exc:
                logger.warning("Execute failed: %s", exc)
                ui.notify(f"Execute failed: {exc}", type="negative")
            _last_ik.clear()

        # ── Event wiring ──────────────────────────────────────────────────

        for inp in (x_input, y_input, z_input, rx_input, ry_input, rz_input):
            inp.on("update:model-value", lambda _: _reset_status())

        preview_btn.on("click", handle_preview)
        execute_btn.on("click", handle_execute)
        kin_tabs.on("update:model-value", lambda _: _reset_status())

        for fk_inp in (fk_j1, fk_j2, fk_j3, fk_j4, fk_j5, fk_j6):
            fk_inp.on("update:model-value", lambda _: _fk_reset_outputs())
        fk_calc_btn.on("click", handle_fk_calculate)
        fk_execute_btn.on("click", handle_fk_execute)

        return {
            "kin_tabs": kin_tabs,
            "ik_tab": ik_tab,
            "fk_tab": fk_tab,
            "x": x_input,
            "y": y_input,
            "z": z_input,
            "rx": rx_input,
            "ry": ry_input,
            "rz": rz_input,
            "status": status_label,
            "preview_btn": preview_btn,
            "execute_btn": execute_btn,
            "ik_out_j1": ik_out_j1, "ik_out_j2": ik_out_j2, "ik_out_j3": ik_out_j3,
            "ik_out_j4": ik_out_j4, "ik_out_j5": ik_out_j5, "ik_out_j6": ik_out_j6,
            "fk_j1": fk_j1, "fk_j2": fk_j2, "fk_j3": fk_j3,
            "fk_j4": fk_j4, "fk_j5": fk_j5, "fk_j6": fk_j6,
            "fk_calc_btn": fk_calc_btn,
            "fk_execute_btn": fk_execute_btn,
            "fk_out_x": fk_out_x,   "fk_out_y": fk_out_y,   "fk_out_z": fk_out_z,
            "fk_out_rx": fk_out_rx,  "fk_out_ry": fk_out_ry,  "fk_out_rz": fk_out_rz,
            "fk_warn": fk_warn_label,
        }
