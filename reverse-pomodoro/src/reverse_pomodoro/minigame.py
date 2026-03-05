"""Dodge mini-game widget for Reverse Pomodoro break sessions."""

import random

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

_COLS = 9
_ROWS = 10
_CELL = 30
_TICK_MS = 400

_COLOR_BG = QColor("#1a1a2e")
_COLOR_PLAYER = QColor("#00b4d8")
_COLOR_OBSTACLE = QColor("#ff6b35")
_COLOR_TEXT = QColor("#e0e0e0")


class DodgeGame(QWidget):
    """Grid-based dodge mini-game: move the player left/right to avoid falling obstacles."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(_COLS * _CELL, _ROWS * _CELL + 30)
        self.setFocusPolicy(Qt.StrongFocus)

        self._player_col: int = _COLS // 2
        self._obstacles: list[tuple[int, int]] = []  # (row, col)
        self._score: int = 0
        self._game_over: bool = False

        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(_TICK_MS)
        self._tick_timer.timeout.connect(self._tick)

        self._restart_timer = QTimer(self)
        self._restart_timer.setSingleShot(True)
        self._restart_timer.timeout.connect(self._reset)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        self._reset()
        self._tick_timer.start()

    def stop(self) -> None:
        self._tick_timer.stop()
        self._restart_timer.stop()

    def move_left(self) -> None:
        if not self._game_over and self._player_col > 0:
            self._player_col -= 1
            self.update()

    def move_right(self) -> None:
        if not self._game_over and self._player_col < _COLS - 1:
            self._player_col += 1
            self.update()

    # ------------------------------------------------------------------
    # Internal logic
    # ------------------------------------------------------------------

    def _reset(self) -> None:
        self._player_col = _COLS // 2
        self._obstacles = []
        self._score = 0
        self._game_over = False
        self.update()

    def _tick(self) -> None:
        # Move existing obstacles down by one row
        next_obstacles = []
        for row, col in self._obstacles:
            new_row = row + 1
            if new_row < _ROWS - 1:
                next_obstacles.append((new_row, col))
            elif new_row == _ROWS - 1:
                # Obstacle reached player row — check collision
                if col == self._player_col:
                    next_obstacles.append((new_row, col))
                    self._obstacles = next_obstacles
                    self._end_round()
                    return
                else:
                    # Passed safely → score
                    self._score += 1
            # else: obstacle fell off bottom, discard

        # Spawn a new obstacle at the top (random column)
        if random.random() < 0.7:  # 70% chance each tick
            next_obstacles.append((0, random.randint(0, _COLS - 1)))

        self._obstacles = next_obstacles
        self.update()

    def _end_round(self) -> None:
        self._game_over = True
        self._tick_timer.stop()
        self.update()
        self._restart_timer.start(2000)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        # Background
        painter.fillRect(self.rect(), _COLOR_BG)

        if self._game_over:
            painter.setPen(_COLOR_TEXT)
            font = painter.font()
            font.setPointSize(14)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(
                self.rect(),
                Qt.AlignCenter,
                f"💥 Dodged: {self._score}\nRestarting…",
            )
            return

        # Draw player
        px = self._player_col * _CELL
        py = (_ROWS - 1) * _CELL
        painter.fillRect(px + 4, py + 4, _CELL - 8, _CELL - 8, _COLOR_PLAYER)

        # Draw player glyph
        painter.setPen(_COLOR_BG)
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(px, py, _CELL, _CELL, Qt.AlignCenter, "▲")

        # Draw obstacles
        painter.setPen(Qt.NoPen)
        for row, col in self._obstacles:
            ox = col * _CELL
            oy = row * _CELL
            painter.fillRect(ox + 4, oy + 4, _CELL - 8, _CELL - 8, _COLOR_OBSTACLE)

        # Score label at bottom
        painter.setPen(_COLOR_TEXT)
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)
        painter.drawText(
            0, _ROWS * _CELL, _COLS * _CELL, 30,
            Qt.AlignCenter,
            f"Dodged: {self._score}  |  ← → to move",
        )
