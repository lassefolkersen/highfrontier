import importlib
import sys
import types


def test_importing_intro_does_not_start_intro_gui(monkeypatch):
    class GameStartedAtImport(RuntimeError):
        pass

    class ExplodingGame:
        def __init__(self):
            raise GameStartedAtImport("intro constructed Game during import")

    pygame_stub = types.ModuleType("pygame")
    pygame_locals_stub = types.ModuleType("pygame.locals")
    setattr(pygame_stub, "Surface", object)
    setattr(pygame_stub, "locals", pygame_locals_stub)
    monkeypatch.setitem(sys.modules, "pygame", pygame_stub)
    monkeypatch.setitem(sys.modules, "pygame.locals", pygame_locals_stub)
    monkeypatch.setitem(sys.modules, "solarsystem", types.ModuleType("solarsystem"))
    monkeypatch.setitem(sys.modules, "planet", types.ModuleType("planet"))
    monkeypatch.setitem(sys.modules, "global_variables", types.ModuleType("global_variables"))
    monkeypatch.setitem(sys.modules, "gui_components", types.ModuleType("gui_components"))
    monkeypatch.setitem(sys.modules, "primitives", types.ModuleType("primitives"))
    main_stub = types.ModuleType("main")
    setattr(main_stub, "Game", ExplodingGame)
    monkeypatch.setitem(sys.modules, "main", main_stub)
    sys.modules.pop("intro", None)

    importlib.import_module("intro")
