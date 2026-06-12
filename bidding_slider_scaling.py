"""Pure slider scaling helpers for bidding and firm-size UI controls.

The pygame scrollbars expose integer positions. These helpers keep the
nonlinear UX mapping outside the GUI so it can be tested without opening a
window or relying on pygame state.
"""

import math


SLIDER_MIN = 0
SLIDER_MAX = 1000
SLIDER_LOW_ANCHOR = 333
SLIDER_HIGH_ANCHOR = 667
EDGE_EXPONENT = 2.5
FIRM_SIZE_CAPITAL_DIVISOR = 10_000
FIRM_SIZE_MIN_MAX = 50


def _clamp(value, lower, upper):
    return max(lower, min(upper, value))


def _valid_positive(value):
    try:
        return value is not None and float(value) > 0
    except (TypeError, ValueError):
        return False


def _linear_from_slider(position, maximum):
    maximum = max(float(maximum or 0), 0.0)
    position = _clamp(float(position), SLIDER_MIN, SLIDER_MAX)
    return position / float(SLIDER_MAX) * maximum


def _linear_to_slider(value, maximum):
    maximum = max(float(maximum or 0), 0.0)
    if maximum <= 0:
        return SLIDER_MIN
    return int(round(_clamp(float(value), 0.0, maximum) / maximum * SLIDER_MAX))


def _low_edge_value(position, anchor_value):
    """0..LOW_ANCHOR -> 0..anchor, with finer changes near the anchor."""
    position = _clamp(float(position), SLIDER_MIN, SLIDER_LOW_ANCHOR)
    anchor_value = max(float(anchor_value), 0.0)
    if anchor_value <= 0:
        return 0.0
    u = position / float(SLIDER_LOW_ANCHOR)
    return anchor_value * (1.0 - math.pow(1.0 - u, EDGE_EXPONENT))


def _low_edge_position(value, anchor_value):
    anchor_value = max(float(anchor_value), 0.0)
    if anchor_value <= 0:
        return SLIDER_MIN
    ratio = _clamp(float(value), 0.0, anchor_value) / anchor_value
    return SLIDER_LOW_ANCHOR * (1.0 - math.pow(1.0 - ratio, 1.0 / EDGE_EXPONENT))


def _high_edge_value(position, anchor_value, maximum_value):
    """HIGH_ANCHOR..MAX -> anchor..maximum, with finer changes near anchor."""
    anchor_value = max(float(anchor_value), 0.0)
    maximum_value = max(float(maximum_value), anchor_value)
    if maximum_value <= anchor_value:
        return anchor_value
    position = _clamp(float(position), SLIDER_HIGH_ANCHOR, SLIDER_MAX)
    u = (position - SLIDER_HIGH_ANCHOR) / float(SLIDER_MAX - SLIDER_HIGH_ANCHOR)
    return anchor_value + (maximum_value - anchor_value) * math.pow(u, EDGE_EXPONENT)


def _high_edge_position(value, anchor_value, maximum_value):
    anchor_value = max(float(anchor_value), 0.0)
    maximum_value = max(float(maximum_value), anchor_value)
    if maximum_value <= anchor_value:
        return SLIDER_HIGH_ANCHOR
    ratio = (float(value) - anchor_value) / (maximum_value - anchor_value)
    ratio = _clamp(ratio, 0.0, 1.0)
    return SLIDER_HIGH_ANCHOR + (SLIDER_MAX - SLIDER_HIGH_ANCHOR) * math.pow(ratio, 1.0 / EDGE_EXPONENT)


def firm_size_slider_max(capital, population_limited_max=None, minimum=FIRM_SIZE_MIN_MAX):
    """Return a conservative max firm size for the creation slider.

    Firm creation itself does not currently debit capital, so this is a UI
    range heuristic rather than a hard affordability check. The default
    10,000,000 starting capital maps to roughly the old large range of 1,000;
    larger companies get a larger range; very small companies still get a
    usable range; and an existing population-derived max is respected when it
    is larger.
    """
    try:
        capital_based = int(float(capital) / FIRM_SIZE_CAPITAL_DIVISOR)
    except (TypeError, ValueError):
        capital_based = 0

    candidates = [int(minimum), capital_based]
    if population_limited_max is not None:
        try:
            candidates.append(int(population_limited_max))
        except (TypeError, ValueError):
            pass
    return max(1, max(candidates))


def firm_size_from_slider(position, max_size, min_size=1):
    """Map top-to-bottom vertical slider position to logarithmic firm size."""
    max_size = max(int(max_size), int(min_size))
    min_size = max(1, int(min_size))
    position = _clamp(float(position), SLIDER_MIN, SLIDER_MAX)
    if max_size <= min_size:
        return min_size
    ratio = position / float(SLIDER_MAX)
    value = min_size * math.pow(float(max_size) / float(min_size), ratio)
    return int(_clamp(round(value), min_size, max_size))


def firm_size_to_slider(size, max_size, min_size=1):
    max_size = max(int(max_size), int(min_size))
    min_size = max(1, int(min_size))
    size = _clamp(float(size), min_size, max_size)
    if max_size <= min_size:
        return SLIDER_MIN
    ratio = math.log(size / float(min_size)) / math.log(float(max_size) / float(min_size))
    return int(round(_clamp(ratio, 0.0, 1.0) * SLIDER_MAX))


def _usable_price_anchors(highest_buy_offer, lowest_sell_offer):
    if not (_valid_positive(highest_buy_offer) and _valid_positive(lowest_sell_offer)):
        return None
    low_anchor_value = float(highest_buy_offer)
    high_anchor_value = float(lowest_sell_offer)
    if high_anchor_value <= low_anchor_value:
        # Crossed/odd markets violate the nominal labels. Preserve a monotonic
        # usable control by widening the 2/3 anchor just above the 1/3 value.
        high_anchor_value = low_anchor_value + max(1.0, low_anchor_value * 0.05)
    return low_anchor_value, high_anchor_value


def market_price_from_slider(position, highest_buy_offer=None, lowest_sell_offer=None, fallback_max=0):
    anchors = _usable_price_anchors(highest_buy_offer, lowest_sell_offer)
    if anchors is None:
        return int(round(_linear_from_slider(position, fallback_max)))

    low_anchor_value, high_anchor_value = anchors
    position = _clamp(float(position), SLIDER_MIN, SLIDER_MAX)
    if position <= SLIDER_LOW_ANCHOR:
        value = _low_edge_value(position, low_anchor_value)
    elif position <= SLIDER_HIGH_ANCHOR:
        ratio = (position - SLIDER_LOW_ANCHOR) / float(SLIDER_HIGH_ANCHOR - SLIDER_LOW_ANCHOR)
        value = low_anchor_value + (high_anchor_value - low_anchor_value) * ratio
    else:
        upper = max(high_anchor_value * 100.0, high_anchor_value + float(fallback_max or 0) * 10.0, high_anchor_value + 1.0)
        value = _high_edge_value(position, high_anchor_value, upper)
    return int(round(max(0.0, value)))


def market_price_to_slider(price, highest_buy_offer=None, lowest_sell_offer=None, fallback_max=0):
    anchors = _usable_price_anchors(highest_buy_offer, lowest_sell_offer)
    if anchors is None:
        return _linear_to_slider(price, fallback_max)

    low_anchor_value, high_anchor_value = anchors
    price = max(float(price), 0.0)
    if price <= low_anchor_value:
        position = _low_edge_position(price, low_anchor_value)
    elif price <= high_anchor_value:
        ratio = (price - low_anchor_value) / (high_anchor_value - low_anchor_value)
        position = SLIDER_LOW_ANCHOR + ratio * (SLIDER_HIGH_ANCHOR - SLIDER_LOW_ANCHOR)
    else:
        upper = max(high_anchor_value * 100.0, high_anchor_value + float(fallback_max or 0) * 10.0, high_anchor_value + 1.0)
        position = _high_edge_position(price, high_anchor_value, upper)
    return int(round(_clamp(position, SLIDER_MIN, SLIDER_MAX)))


def quantity_anchor_for_direction(input_output_dict, direction, resource):
    if not input_output_dict:
        return None
    if direction == "buy":
        section = "input"
    elif direction == "sell":
        section = "output"
    else:
        return None
    try:
        value = input_output_dict.get(section, {}).get(resource)
    except AttributeError:
        return None
    if not _valid_positive(value):
        return None
    return float(value)


def quantity_from_slider(position, anchor_quantity=None, fallback_max=0):
    if not _valid_positive(anchor_quantity):
        return int(round(_linear_from_slider(position, fallback_max)))

    anchor = float(anchor_quantity)
    high_anchor_quantity = anchor * 10.0
    maximum_quantity = anchor * 100.0
    position = _clamp(float(position), SLIDER_MIN, SLIDER_MAX)
    if position <= SLIDER_LOW_ANCHOR:
        value = _low_edge_value(position, anchor)
    elif position <= SLIDER_HIGH_ANCHOR:
        ratio = (position - SLIDER_LOW_ANCHOR) / float(SLIDER_HIGH_ANCHOR - SLIDER_LOW_ANCHOR)
        value = anchor + (high_anchor_quantity - anchor) * ratio
    else:
        value = _high_edge_value(position, high_anchor_quantity, maximum_quantity)
    return int(round(max(0.0, value)))


def quantity_to_slider(quantity, anchor_quantity=None, fallback_max=0):
    if not _valid_positive(anchor_quantity):
        return _linear_to_slider(quantity, fallback_max)

    anchor = float(anchor_quantity)
    high_anchor_quantity = anchor * 10.0
    maximum_quantity = anchor * 100.0
    quantity = max(float(quantity), 0.0)
    if quantity <= anchor:
        position = _low_edge_position(quantity, anchor)
    elif quantity <= high_anchor_quantity:
        ratio = (quantity - anchor) / (high_anchor_quantity - anchor)
        position = SLIDER_LOW_ANCHOR + ratio * (SLIDER_HIGH_ANCHOR - SLIDER_LOW_ANCHOR)
    else:
        position = _high_edge_position(quantity, high_anchor_quantity, maximum_quantity)
    return int(round(_clamp(position, SLIDER_MIN, SLIDER_MAX)))
