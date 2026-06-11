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


def test_simthread_logs_unhandled_exception(caplog):
    thread = SimThread(ExplodingSolarSystem())

    with caplog.at_level(logging.ERROR), pytest.raises(RuntimeError, match="sim boom"):
        thread.run()

    assert "Unhandled exception in simulation thread" in caplog.text
    assert "sim boom" in caplog.text
