"""Unit tests for lock_machine() across all platform branches."""

from __future__ import annotations

import subprocess
from unittest.mock import call, patch

import pytest

from sleeptimer import actions

_CGSESSION = (
    "/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession"
)


# ── 1. Windows ────────────────────────────────────────────────────────────────

def test_lock_machine_windows():
    with patch("sys.platform", "win32"), patch("subprocess.run") as mock_run:
        actions.lock_machine()
    mock_run.assert_called_once_with(
        ["rundll32.exe", "user32.dll,LockWorkStation"], check=True
    )


# ── 2. macOS — CGSession present ──────────────────────────────────────────────

def test_lock_machine_macos():
    with patch("sys.platform", "darwin"), patch("subprocess.run") as mock_run:
        actions.lock_machine()
    mock_run.assert_called_once_with([_CGSESSION, "-suspend"], check=True)


# ── 3. macOS — CGSession missing ──────────────────────────────────────────────

def test_lock_machine_macos_missing_cgsession():
    with patch("sys.platform", "darwin"), patch(
        "subprocess.run", side_effect=FileNotFoundError
    ):
        with pytest.raises(RuntimeError, match="CGSession not found"):
            actions.lock_machine()


# ── 4. Linux — first command succeeds ────────────────────────────────────────

def test_lock_machine_linux_first_succeeds():
    with patch("sys.platform", "linux"), patch("subprocess.run") as mock_run:
        actions.lock_machine()
    mock_run.assert_called_once_with(["loginctl", "lock-session"], check=True)


# ── 5. Linux — first fails, second succeeds ──────────────────────────────────

def test_lock_machine_linux_fallback():
    responses = [FileNotFoundError, None]

    def _run(cmd, **_kw):
        effect = responses.pop(0)
        if effect is not None:
            raise effect()

    with patch("sys.platform", "linux"), patch("subprocess.run", side_effect=_run) as mock_run:
        actions.lock_machine()

    assert mock_run.call_count == 2
    assert mock_run.call_args_list[0] == call(["loginctl", "lock-session"], check=True)
    assert mock_run.call_args_list[1] == call(["xdg-screensaver", "lock"], check=True)


# ── 6. Linux — all three commands fail ───────────────────────────────────────

def test_lock_machine_linux_all_fail():
    with patch("sys.platform", "linux"), patch(
        "subprocess.run", side_effect=FileNotFoundError
    ):
        with pytest.raises(RuntimeError, match="no supported lock command"):
            actions.lock_machine()


# ── 7. Unknown platform ───────────────────────────────────────────────────────

def test_lock_machine_unknown_platform():
    with patch("sys.platform", "freebsd12"):
        with pytest.raises(NotImplementedError):
            actions.lock_machine()
