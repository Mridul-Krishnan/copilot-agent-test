"""Headless unit tests for DodgeGame mini-game widget.

Run with: QT_QPA_PLATFORM=offscreen uv run pytest tests/test_minigame.py
"""

import os
import sys

import pytest


@pytest.fixture(scope="session", autouse=True)
def offscreen_qt():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="session")
def qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


@pytest.fixture
def game(qapp):
    from reverse_pomodoro.minigame import DodgeGame
    g = DodgeGame()
    yield g
    g.stop()


# ------------------------------------------------------------------
# Initial state
# ------------------------------------------------------------------

def test_initial_state(game):
    from reverse_pomodoro.minigame import _COLS
    assert game._player_col == _COLS // 2
    assert game._score == 0
    assert game._obstacles == []
    assert game._game_over is False


# ------------------------------------------------------------------
# Boundary movement
# ------------------------------------------------------------------

def test_move_left_boundary(game):
    game._player_col = 0
    game.move_left()
    assert game._player_col == 0


def test_move_right_boundary(game):
    from reverse_pomodoro.minigame import _COLS
    game._player_col = _COLS - 1
    game.move_right()
    assert game._player_col == _COLS - 1


def test_move_left_decrements(game):
    game._player_col = 4
    game.move_left()
    assert game._player_col == 3


def test_move_right_increments(game):
    game._player_col = 4
    game.move_right()
    assert game._player_col == 5


# ------------------------------------------------------------------
# Tick logic
# ------------------------------------------------------------------

def test_tick_advances_obstacles(game):
    game._obstacles = [(0, 3)]
    game._player_col = 0  # won't collide
    game._tick()
    rows = [r for r, c in game._obstacles if c == 3]
    assert 1 in rows


def test_tick_score_increments(game):
    from reverse_pomodoro.minigame import _ROWS
    game._player_col = 0
    game._obstacles = [(_ROWS - 2, 5)]  # col differs from player
    game._score = 0
    game._tick()
    assert game._score == 1


def test_tick_collision(game):
    from reverse_pomodoro.minigame import _ROWS
    game._player_col = 4
    game._obstacles = [(_ROWS - 2, 4)]  # same col → collision next tick
    game._tick()
    assert game._game_over is True
    assert not game._tick_timer.isActive()


# ------------------------------------------------------------------
# start / stop
# ------------------------------------------------------------------

def test_stop_halts_timers(game):
    game.start()
    assert game._tick_timer.isActive()
    game.stop()
    assert not game._tick_timer.isActive()
    assert not game._restart_timer.isActive()


def test_start_resets_state(game):
    # Put game into dirty state
    game._score = 99
    game._game_over = True
    game._obstacles = [(0, 0)]
    game.start()
    assert game._score == 0
    assert game._game_over is False
    assert game._tick_timer.isActive()
    game.stop()


# ------------------------------------------------------------------
# set_colors
# ------------------------------------------------------------------

def test_set_colors_updates_attributes(game):
    from PySide6.QtGui import QColor

    game.set_colors("#aabbcc", "#112233", "#445566", "#778899")

    assert game._color_bg == QColor("#aabbcc")
    assert game._color_player == QColor("#112233")
    assert game._color_obstacle == QColor("#445566")
    assert game._color_text == QColor("#778899")
