from enum import Enum


class Direction(Enum):
    """Direction one can move the displays."""
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"

class Display(Enum):
    """Possible displais of the user."""
    SOLAR_SYSTEM = "solar_system"
    PLANETARY = "planetary"
    BASE = "base"
    FIRM = "firm"
    COMPANY = "company"
    TECHTREE = "techtree"


def raise_not_implemented_display(display: Display):
    """Raise a not implemented error for the given display."""
    raise NotImplementedError(f"Display {display} is not implemented.")
