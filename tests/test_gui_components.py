import types

import pygame

import gui_components


def _surface():
    pygame.init()
    pygame.display.set_mode((1, 1))
    return pygame.Surface((320, 200))


def _sample_rows():
    return {
        "bravo": {"score": 2, "name": "B"},
        "alpha": {"score": 1, "name": "A"},
    }


def test_fast_list_sorts_tabular_rows_by_requested_column():
    widget = gui_components.fast_list(
        _surface(),
        _sample_rows(),
        pygame.Rect(0, 0, 260, 120),
        column_order=["rownames", "score", "name"],
        sort_by="score",
    )

    assert widget.data[0].startswith("alpha")
    assert widget.data[1].startswith("bravo")


def test_fast_list_reverse_sorts_tabular_rows_by_requested_column():
    widget = gui_components.fast_list(
        _surface(),
        _sample_rows(),
        pygame.Rect(0, 0, 260, 120),
        column_order=["rownames", "score", "name"],
        sort_by="score",
    )

    widget.receive_data(
        _sample_rows(),
        sort_by="score",
        column_order=["rownames", "score", "name"],
        reverse_sort=True,
    )

    assert widget.data[0].startswith("bravo")
    assert widget.data[1].startswith("alpha")


def test_fast_list_header_click_on_known_column_resorts_without_error():
    widget = gui_components.fast_list(
        _surface(),
        _sample_rows(),
        pygame.Rect(0, 0, 260, 120),
        column_order=["rownames", "score", "name"],
        sort_by="rownames",
    )
    assert widget.title is not None
    score_span = next(
        span
        for span, column_name in widget.title["entry_span"].items()
        if column_name == "score"
    )
    click = types.SimpleNamespace(pos=(score_span[0] + 1, widget.rect[1] + 1))

    widget.receive_click(click)

    assert widget.sorted_by_this_column == "score"
    assert widget.data[0].startswith("alpha")
