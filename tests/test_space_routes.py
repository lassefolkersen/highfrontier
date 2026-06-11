import random

import company
import global_variables
from solarsystem import solarsystem


def _make_space_base(sol):
    earth = sol.planets["earth"]
    ground_base = next(iter(earth.bases.values()))
    base_data = {
        "eastern_loc": None,
        "northern_loc": None,
        "GDP_per_capita_in_dollars": ground_base.gdp_per_capita_in_dollars,
        "population": 100,
        "country": ground_base.original_country,
    }
    space_base = company.base(sol, "test orbit", earth, base_data, ground_base.owner)
    earth.bases[space_base.base_name] = space_base
    return earth, ground_base, space_base


def test_space_base_has_space_terrain_and_no_mining():
    sol = solarsystem(global_variables.start_date, de_novo_initialization=True)
    earth, _, space_base = _make_space_base(sol)

    assert space_base.terrain_type == "Space"
    assert space_base.get_mining_opportunities(earth, "iron") == 0
    assert space_base.get_mining_opportunities(earth, "food") == 0


def test_space_trade_route_is_reciprocal_and_keeps_legacy_keys_with_metadata():
    random.seed(12345)
    sol = solarsystem(global_variables.start_date, de_novo_initialization=True)
    _, _, space_base = _make_space_base(sol)

    space_base.calculate_trade_routes(space_base.home_planet)
    [(ground_name, route)] = list(space_base.trade_routes.items())
    ground_route = space_base.home_planet.bases[ground_name].trade_routes[space_base.base_name]

    assert ground_route is route
    assert {"distance", "transport_type", "endpoints", "endpoint_links"} <= set(route)
    assert route["metadata"]["schema_version"] == 1
    assert route["metadata"]["route_class"] == "surface-orbit"
