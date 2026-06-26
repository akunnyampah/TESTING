# TASKPLAN_RECORDER_FIX.md — Motion Recorder Duplicate Fix
# Last updated: 2026-06-21

## Status keseluruhan
[PHASE 2 of 3] / [FIX C APPLIED — awaiting user test]

## Context
Three bugs in existing Waldo Commander motion_recorder.py and
control.py cause duplicate move_j/move_l entries when recording.
These are pre-existing bugs, not introduced by the ROS 2 integration.

Root causes:
- Bug 1 (control.py:1263-1268): TCP drag implicit-start fires after
  end-handler clears _tcp_drag_active → two move_l for one drag
- Bug 2 (motion_recorder.py): on_jog_start() calls on_jog_end()
  inline but does NOT cancel pending _jog_end_wait_task → old task
  records new jog at wrong time
- Bug 3 (motion_recorder.py): finally block sets
  _jog_end_wait_task = None even on cancellation → overwrites new
  task reference, causes multiple on_jog_end() calls

## Non-destructive rules (MANDATORY)
- Only touch: motion_recorder.py and control.py
- Do NOT touch: any other file
- Each fix is independent — if one fix causes issues, revert only
  that fix without affecting the others
- After EACH fix, verify existing jog recording still works before
  proceeding to next fix
- If any fix introduces new behavior change beyond the bug fix scope,
  STOP and report before continuing

---

## Phase 1 — Investigation & baseline

- [ ] TASK-R01 — Show full _wait_and_record_jog_end() in motion_recorder.py
- [ ] TASK-R02 — Show full _schedule_jog_end_wait() in motion_recorder.py
- [ ] TASK-R03 — Show full on_jog_start() in motion_recorder.py
- [ ] TASK-R04 — Show full on_jog_end() in motion_recorder.py
- [ ] TASK-R05 — Show _handle_tcp_cartesian_move() in control.py (lines ~1245-1290)
- [ ] TASK-R06 — Show _handle_tcp_cartesian_move_end() in control.py
- [ ] TASK-R07 — Confirm exact line numbers for all three bug locations
- [ ] TASK-R08 — User confirms understanding of each bug before fix

## Phase 2 — Apply fixes (one at a time, independent)

### Fix A — Bug 1: TCP implicit-start guard (control.py)
- [ ] TASK-R09  — Show diff for Bug 1 fix
- [ ] TASK-R10  — User approves diff
- [~] TASK-R11  — Apply Bug 1 fix [REVERTED]
- [ ] TASK-R12  — Test: do one TCP drag, confirm only ONE move_l recorded
- [ ] TASK-R13  — Confirm no regression: normal cartesian jog still records

### Fix B — Bug 2: Cancel pending task in on_jog_start (motion_recorder.py)
- [ ] TASK-R14  — Show diff for Bug 2 fix
- [ ] TASK-R15  — User approves diff
- [x] TASK-R16  — Apply Bug 2 fix (guard counter pattern)
- [ ] TASK-R17  — Test: rapid J1+ then J2+, confirm each recorded once
- [x] TASK-R18  — motion_start_timeout=5.0 added to wait_motion() call in
                  _wait_and_record_jog_end() (control.py:1299). Extends Phase 1
                  detection window from 1.0s to 5.0s. ABC uses **kwargs so parameter
                  passes through safely. [RESOLVED]

### Fix mouseleave — root cause: spurious jog-end during holds (control.py)
- [x] TASK-R19  — mouseleave bindings removed from joint neg (line ~1682),
                  joint pos (line ~1712), and cartesian slot (line ~1780).
                  Robot safety maintained via 0.1s stream timeout on jog_l/jog_j.
                  All jog stops now require explicit mouseup only. [RESOLVED]

### Fix C — Bug 3: finally block task reference (control.py)
- [x] TASK-R20  — Diff shown and approved. Bug 3 confirmed in
                  control.py (NOT motion_recorder.py as originally noted).
                  finally block in _wait_and_record_jog_end() ran before
                  CancelledError return, clearing _jog_end_wait_task which
                  already pointed to the NEW task. This orphaned N/2 tasks
                  per N rapid press-release cycles. Each orphaned task
                  independently awaited wait_motion then fired on_jog_end()
                  → N/2 identical duplicate move_l/move_j entries.
                  Also included motion_start_timeout=5.0 (re-applied).
- [x] TASK-R21  — Applied. Removed finally block; moved
                  self._jog_end_wait_task = None to after except blocks
                  (non-cancelled path only). Waldo restarted clean.
- [ ] TASK-R22  — Test: rapid multi-joint sequence, confirm no duplicates
- [ ] TASK-R23  — Confirm no regression: all jog types record correctly

## Kesimpulan (updated)

Root cause sebenarnya: Bug 3 di control.py — bukan di motion_recorder.py.
`finally: self._jog_end_wait_task = None` di _wait_and_record_jog_end()
berjalan sebelum `return` pada CancelledError, menghapus referensi ke task
baru yang baru saja di-create. Akibatnya N/2 orphaned tasks per siklus
rapid press-release, semua fire on_jog_end() setelah wait_motion selesai.

Fix yang diterapkan (control.py only):
- Hapus `finally:` block
- Pindahkan `self._jog_end_wait_task = None` ke path non-cancelled (setelah
  except blocks, sebelum motion_recorder.on_jog_end())
- motion_start_timeout=5.0 juga di-apply kembali

Fix A (TCP drag flag): REVERTED — menyebabkan seluruh kontrol robot mati
Fix B (guard counter): REVERTED — hanya absorbs 1 stale call, tak cukup
Fix C (mouseleave removal): REVERTED — bukan root cause
Fix C real (finally block): APPLIED — awaiting user test

---

## Phase 3 — Final verification

- [ ] TASK-R24  — Full record session test:
                  home → jog J1 → jog J2 → cartesian jog → TCP drag
                  → stop record → count lines in editor
                  → confirm no duplicates
- [ ] TASK-R25  — Test Capture Current Pose still works (not affected by fixes)
- [ ] TASK-R26  — Test I/O recording still works
- [ ] TASK-R27  — Test gripper recording still works
- [ ] TASK-R28  — Update this file: mark all tasks [x], status COMPLETE

---

## Temuan eksplorasi (diisi setelah Phase 1)

### Bug 1 exact location
- File: control.py
- Lines: ~1263-1268
- Description: [diisi setelah TASK-R05]

### Bug 2 exact location
- File: motion_recorder.py
- Lines: [diisi setelah TASK-R02/R03]
- Description: [diisi setelah TASK-R03]

### Bug 3 exact location
- File: control.py (NOT motion_recorder.py — corrected)
- Lines: 1307-1308 (original), now fixed
- Description: finally block in _wait_and_record_jog_end() ran before
  CancelledError return, wiping new task reference assigned by
  _schedule_jog_end_wait(). Fix: remove finally, add = None in
  non-cancelled path only.

---

## Catatan risiko

| Fix | Risiko | Mitigasi |
|-----|--------|----------|
| Bug 1 (TCP implicit-start) | Bisa break TCP drag recording jika guard terlalu ketat | Test TCP drag setelah fix sebelum lanjut |
| Bug 2 (cancel task) | asyncio.Task.cancel() tidak guaranteed immediate | Add check result.cancelled() if needed |
| Bug 3 (finally block) | Moving _jog_end_wait_task = None out of finally could leak task reference | Set to None only in non-cancelled path AND after on_jog_end() call |

---

## Log perubahan
| Tanggal | Perubahan | Catatan |
|---------|-----------|---------|
| 2026-06-21 | File dibuat | Tiga bug recorder duplikat diidentifikasi |
