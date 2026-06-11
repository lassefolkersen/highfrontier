import random
from types import SimpleNamespace

import pytest

import company
import global_variables
from market_decisions import market_decisions
from solarsystem import solarsystem


SNAPSHOT_SEED = 20260611


def _initialized_solar_system(seed=SNAPSHOT_SEED):
    random.seed(seed)
    return solarsystem(global_variables.start_date, de_novo_initialization=True)


def test_full_initialization_snapshot_is_deterministic_for_fixed_seed():
    sol = _initialized_solar_system()

    total_bases = sum(len(planet.bases) for planet in sol.planets.values())
    total_firms = sum(len(owner.owned_firms) for owner in sol.companies.values())
    total_trade_routes = (
        sum(len(base.trade_routes) for planet in sol.planets.values() for base in planet.bases.values())
        // 2
    )
    base_counts_by_planet = {
        planet_name: len(planet.bases)
        for planet_name, planet in sol.planets.items()
        if planet.bases
    }

    assert len(sol.planets) == 193
    assert total_bases == 255
    assert len(sol.companies) == 500
    assert total_firms == 7755
    assert total_trade_routes == 808
    assert base_counts_by_planet == {"earth": 255}
    assert len(sol.trade_resources) == 19
    assert len(sol.mineral_resources) == 5
    assert len(sol.technology_tree.vertex_dict) == 149


def test_new_solar_system_starts_with_zeroed_telemetry_keys():
    sol = _initialized_solar_system()

    assert sol.telemetry == {
        "stockouts": 0,
        "zero_stock_bases": 0,
        "transactions": 0,
        "firm_starts": 0,
        "firm_closes": 0,
        "bankruptcies": 0,
    }


def test_telemetry_counts_post_initialization_firm_starts():
    sol = _initialized_solar_system()
    owner = next(iter(sol.companies.values()))
    location = next(iter(owner.home_cities.values()))

    owner.change_firm_size(location, 1, "research", name="telemetry research start")

    assert sol.telemetry["firm_starts"] == 1


def test_telemetry_counts_market_transactions():
    sol = _initialized_solar_system()
    location = next(base for planet in sol.planets.values() for base in planet.bases.values())
    seller_owner, buyer_owner = list(sol.companies.values())[:2]
    seller = company.firm(
        sol,
        location,
        {"input": {}, "output": {}, "timeframe": 30, "byproducts": {}},
        seller_owner,
        "telemetry seller",
        "common knowledge",
    )
    buyer = company.firm(
        sol,
        location,
        {"input": {}, "output": {}, "timeframe": 30, "byproducts": {}},
        buyer_owner,
        "telemetry buyer",
        "common knowledge",
    )
    seller.stock_dict["food"] = 3
    buyer_owner.capital = 1000
    location.market["buy_offers"]["food"] = [
        {
            "resource": "food",
            "price": 5.0,
            "quantity": 3,
            "buyer": buyer,
            "date": sol.current_date,
            "name": buyer.name,
        }
    ]

    seller.make_market_bid(
        location.market,
        {
            "resource": "food",
            "price": 4.0,
            "quantity": 3,
            "seller": seller,
            "date": sol.current_date,
            "name": seller.name,
        },
    )

    assert sol.telemetry["transactions"] == 1


@pytest.mark.xfail(strict=True, reason="Known bug: intercity trade profit margin uses sellprice - buyprice instead of buyprice - sellprice")
def test_intercity_trade_starts_merchant_when_destination_price_exceeds_source_price():
    sol = _initialized_solar_system()
    owner = next(iter(sol.companies.values()))
    seller_base = next(base for planet in sol.planets.values() for base in planet.bases.values() if base.trade_routes)
    buyer_base = next(iter(seller_base.trade_routes.values()))["endpoint_links"][0]
    if buyer_base is seller_base:
        buyer_base = next(iter(seller_base.trade_routes.values()))["endpoint_links"][1]

    owner.home_cities = {seller_base.name: seller_base, buyer_base.name: buyer_base}
    owner.company_database["tendency_to_start_trade_routes"] = 100
    seller_base.market["sell_offers"]["food"] = [{"resource": "food", "price": 10.0, "quantity": 100}]
    buyer_base.market["buy_offers"]["food"] = [{"resource": "food", "price": 100.0, "quantity": 100}]
    seller_base.market["sell_offers"]["ground transport"] = [{"resource": "ground transport", "price": 0.0, "quantity": 100}]
    buyer_base.market["sell_offers"]["ground transport"] = [{"resource": "ground transport", "price": 0.0, "quantity": 100}]

    merchants_before = [firm for firm in owner.owned_firms.values() if isinstance(firm, company.merchant)]
    global_variables.market_decisions.evaluate_intercity_trade_market_01(owner)
    merchants_after = [firm for firm in owner.owned_firms.values() if isinstance(firm, company.merchant)]

    assert len(merchants_after) == len(merchants_before) + 1


@pytest.mark.xfail(strict=True, reason="Known bug: desired_research percentage is compared directly to a 0..1 research ratio")
def test_research_firms_do_not_start_when_current_ratio_already_exceeds_desired_percent():
    decisions = market_decisions()
    subject = company.company.__new__(company.company)
    research_firm = company.research.__new__(company.research)
    research_firm.size = 50
    ordinary_firm = SimpleNamespace(size=50)
    started = []

    subject.owned_firms = {"research": research_firm, "ordinary": ordinary_firm}
    subject.company_database = {"desired_research": 40}
    subject.home_cities = {"test city": object()}

    def record_start(location, size, technology_name, name=None):
        started.append((location, size, technology_name, name))

    subject.change_firm_size = record_start

    decisions.start_research_firms_01(subject)

    assert started == []
