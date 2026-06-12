import datetime
import logging

import pytest

from SimThread import SimThread


class ExplodingSolarSystem:
    def __init__(self):
        self.current_date = datetime.date(2026, 1, 1)
        self.companies = {}

    def evaluate_each_game_step(self):
        raise RuntimeError("sim boom")


class _FakeCompany:
    def __init__(self):
        self.evaluated = 0

    def evaluate_self(self):
        self.evaluated += 1


class _SteppingSolarSystem:
    def __init__(self):
        self.current_date = datetime.date(2026, 1, 1)
        self.companies = {"company": _FakeCompany()}
        self.step_delay_time = 250
        self.evaluated = 0

    def evaluate_each_game_step(self):
        self.evaluated += 1


def test_simthread_run_one_step_advances_date_and_evaluates_world_and_companies():
    sol = _SteppingSolarSystem()
    thread = SimThread(sol)

    thread.run_one_step()

    assert sol.current_date == datetime.date(2026, 1, 31)
    assert sol.evaluated == 1
    assert sol.companies["company"].evaluated == 1


def test_simthread_sleep_between_steps_uses_sol_step_delay_time_milliseconds(monkeypatch):
    sol = _SteppingSolarSystem()
    sol.step_delay_time = 250
    thread = SimThread(sol)
    sleep_calls = []

    monkeypatch.setattr("SimThread.time.sleep", sleep_calls.append)

    thread.sleep_between_steps()

    assert sleep_calls == [0.25]


def test_simthread_logs_unhandled_exception(caplog):
    thread = SimThread(ExplodingSolarSystem())

    with caplog.at_level(logging.ERROR), pytest.raises(RuntimeError, match="sim boom"):
        thread.run()

    assert "Unhandled exception in simulation thread" in caplog.text
    assert "sim boom" in caplog.text
