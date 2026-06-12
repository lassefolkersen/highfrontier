import pytest

from bidding_slider_scaling import (
    SLIDER_HIGH_ANCHOR,
    SLIDER_LOW_ANCHOR,
    SLIDER_MAX,
    firm_size_from_slider,
    firm_size_slider_max,
    firm_size_to_slider,
    market_price_from_slider,
    market_price_to_slider,
    quantity_anchor_for_direction,
    quantity_from_slider,
    quantity_to_slider,
)


def test_firm_size_slider_uses_log_mapping_with_small_top_and_large_bottom():
    max_size = 1000

    assert firm_size_from_slider(0, max_size) == 1
    assert firm_size_from_slider(SLIDER_MAX, max_size) == max_size
    assert 25 <= firm_size_from_slider(SLIDER_MAX // 2, max_size) <= 45
    assert firm_size_from_slider(10, max_size) - firm_size_from_slider(0, max_size) <= 1
    assert firm_size_from_slider(SLIDER_MAX, max_size) - firm_size_from_slider(SLIDER_MAX - 10, max_size) > 50


def test_firm_size_slider_max_scales_with_capital_but_has_floor_and_population_context():
    assert firm_size_slider_max(capital=1000, population_limited_max=1) >= 50
    assert 900 <= firm_size_slider_max(capital=10_000_000, population_limited_max=200) <= 1200
    assert firm_size_slider_max(capital=100_000_000, population_limited_max=200) > firm_size_slider_max(
        capital=10_000_000,
        population_limited_max=200,
    )
    assert firm_size_slider_max(capital=10_000, population_limited_max=500) >= 500


def test_firm_size_inverse_round_trips_representative_values():
    for size in (1, 5, 25, 100, 1000):
        slider_position = firm_size_to_slider(size, 1000)
        assert abs(firm_size_from_slider(slider_position, 1000) - size) <= max(1, int(size * 0.03))


def test_market_price_mapping_anchors_linear_middle_and_nonlinear_edges():
    highest_buy = 30
    lowest_sell = 90

    assert market_price_from_slider(SLIDER_LOW_ANCHOR, highest_buy, lowest_sell, fallback_max=180) == highest_buy
    assert market_price_from_slider(SLIDER_HIGH_ANCHOR, highest_buy, lowest_sell, fallback_max=180) == lowest_sell
    assert market_price_from_slider((SLIDER_LOW_ANCHOR + SLIDER_HIGH_ANCHOR) // 2, highest_buy, lowest_sell, fallback_max=180) == pytest.approx(60, abs=1)
    assert market_price_from_slider(0, highest_buy, lowest_sell, fallback_max=180) == 0
    assert market_price_from_slider(SLIDER_MAX, highest_buy, lowest_sell, fallback_max=180) >= lowest_sell * 50

    near_buy_step = market_price_from_slider(SLIDER_LOW_ANCHOR, highest_buy, lowest_sell, fallback_max=180) - market_price_from_slider(SLIDER_LOW_ANCHOR - 10, highest_buy, lowest_sell, fallback_max=180)
    near_zero_step = market_price_from_slider(10, highest_buy, lowest_sell, fallback_max=180) - market_price_from_slider(0, highest_buy, lowest_sell, fallback_max=180)
    assert near_zero_step > near_buy_step


def test_market_price_mapping_falls_back_without_both_anchors_and_handles_crossed_market():
    assert market_price_from_slider(SLIDER_MAX // 2, None, 90, fallback_max=200) == 100
    assert market_price_from_slider(SLIDER_MAX // 2, 30, None, fallback_max=200) == 100

    crossed_values = [market_price_from_slider(pos, 100, 50, fallback_max=200) for pos in range(0, SLIDER_MAX + 1, 50)]
    assert crossed_values == sorted(crossed_values)
    assert crossed_values[SLIDER_LOW_ANCHOR // 50] <= crossed_values[SLIDER_HIGH_ANCHOR // 50]


def test_market_price_inverse_round_trips_representative_values():
    highest_buy = 30
    lowest_sell = 90
    for price in (0, 10, 30, 60, 90, 900):
        slider_position = market_price_to_slider(price, highest_buy, lowest_sell, fallback_max=180)
        assert market_price_from_slider(slider_position, highest_buy, lowest_sell, fallback_max=180) == pytest.approx(price, rel=0.05, abs=2)


def test_quantity_mapping_anchors_supply_time_units_and_nonlinear_edges():
    assert quantity_from_slider(SLIDER_LOW_ANCHOR, 17, fallback_max=850) == 17
    assert quantity_from_slider(SLIDER_HIGH_ANCHOR, 17, fallback_max=850) == 170
    assert quantity_from_slider(SLIDER_LOW_ANCHOR, 123, fallback_max=6150) == 123
    assert quantity_from_slider(SLIDER_HIGH_ANCHOR, 123, fallback_max=6150) == 1230
    assert quantity_from_slider(0, 17, fallback_max=850) == 0
    assert quantity_from_slider(SLIDER_MAX, 17, fallback_max=850) >= 1700

    near_anchor_step = quantity_from_slider(SLIDER_LOW_ANCHOR, 17, fallback_max=850) - quantity_from_slider(SLIDER_LOW_ANCHOR - 10, 17, fallback_max=850)
    near_zero_step = quantity_from_slider(10, 17, fallback_max=850) - quantity_from_slider(0, 17, fallback_max=850)
    assert near_zero_step > near_anchor_step


def test_quantity_mapping_falls_back_when_selected_resource_has_no_supply_anchor():
    assert quantity_from_slider(SLIDER_MAX // 2, None, fallback_max=800) == 400


def test_quantity_inverse_round_trips_representative_values():
    for quantity in (0, 5, 17, 90, 170, 1700):
        slider_position = quantity_to_slider(quantity, 17, fallback_max=850)
        assert quantity_from_slider(slider_position, 17, fallback_max=850) == pytest.approx(quantity, rel=0.05, abs=2)


def test_quantity_anchor_for_direction_uses_inputs_for_buy_and_outputs_for_sell():
    process = {
        "input": {"labor": 17},
        "output": {"education": 123},
    }

    assert quantity_anchor_for_direction(process, "buy", "labor") == 17
    assert quantity_anchor_for_direction(process, "sell", "education") == 123
    assert quantity_anchor_for_direction(process, "buy", "education") is None
    assert quantity_anchor_for_direction(process, "sell", "labor") is None
