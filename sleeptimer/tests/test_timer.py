"""Unit tests for CountdownTimer."""

import pytest
from sleeptimer.timer import CountdownTimer


# ── 1. tick() decrements remaining by 1 per call when running ─────────────
def test_tick_decrements_when_running():
    t = CountdownTimer(minutes=1)
    t.start()
    t.tick()
    assert t.remaining == 59


# ── 2. tick() does NOT decrement when paused ──────────────────────────────
def test_tick_no_decrement_when_paused():
    t = CountdownTimer(minutes=1)
    # timer is paused by default (not started)
    t.tick()
    assert t.remaining == 60


# ── 3. on_expire fires exactly once at 0 ──────────────────────────────────
def test_on_expire_fires_exactly_once():
    calls = []
    t = CountdownTimer(minutes=0, on_expire=lambda: calls.append(1))
    t.start()
    # remaining is already 0; one tick should fire expiry
    t.tick()
    # further ticks must NOT fire again
    t.tick()
    t.tick()
    assert len(calls) == 1


# ── 4. add_minutes with negative result clamps remaining to 0 ─────────────
def test_add_minutes_clamps_to_zero():
    t = CountdownTimer(minutes=1)
    t.add_minutes(-999)
    assert t.remaining == 0


# ── 5. add_minutes on an expired timer re-enables countdown ───────────────
def test_add_minutes_re_enables_expired_timer():
    t = CountdownTimer(minutes=0, on_expire=lambda: None)
    t.start()
    t.tick()  # expires here
    assert t.is_expired

    t.add_minutes(1)
    assert not t.is_expired
    assert t.remaining == 60


# ── 6. reset() restores remaining and clears expired flag ─────────────────
def test_reset_restores_state():
    t = CountdownTimer(minutes=5)
    t.start()
    for _ in range(30):
        t.tick()

    t.reset(minutes=10)
    assert t.remaining == 600
    assert not t.is_running
    assert not t.is_expired


# ── 7. display property returns correct MM:SS string ──────────────────────
def test_display_format():
    t = CountdownTimer(minutes=20)
    assert t.display == "20:00"

    t.start()
    t.tick()
    assert t.display == "19:59"

    t2 = CountdownTimer(minutes=0)
    assert t2.display == "00:00"
