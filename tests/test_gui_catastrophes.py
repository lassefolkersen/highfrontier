import types

import pygame

import gui
from display import Display


class _FakeEarth:
    def __init__(self, bases):
        self.bases = bases
        self.explosions = []

    def explode(self, size, strength, bases_chosen, action_surface):
        self.explosions.append((size, strength, bases_chosen, action_surface))


def _window_with_earth(earth):
    pygame.init()
    pygame.display.set_mode((1, 1))
    window = gui.file_window.__new__(gui.file_window)
    window.action_surface = pygame.Surface((100, 100))
    window.solar_system_object_link = types.SimpleNamespace(
        display_mode=Display.PLANETARY,
        planets={"earth": earth},
        messages=[],
    )
    return window


def test_nuclear_war_skips_missing_configured_targets_without_crashing():
    earth = _FakeEarth({"stockholm": object()})
    window = _window_with_earth(earth)

    window.nuclear_war(None, None)

    assert len(earth.explosions) == 1
    assert list(earth.explosions[0][2]) == ["stockholm"]
    assert any("glasgow" in message["text"] for message in window.solar_system_object_link.messages)


def test_nuclear_war_reports_if_no_configured_targets_exist():
    earth = _FakeEarth({})
    window = _window_with_earth(earth)

    window.nuclear_war(None, None)

    assert earth.explosions == []
    assert any("not available" in message["text"] for message in window.solar_system_object_link.messages)
