import datetime

import company


class _FakeSolarSystem:
    def __init__(self):
        self.start_date = datetime.date(2026, 1, 1)
        self.current_date = self.start_date
        self.trade_resources = {}
        self.mineral_resources = []
        self.message_printing = {"debugging": False}
        self.messages = []
        self.current_player = None


class _FakeLocation:
    def __init__(self, home_planet):
        self.home_planet = home_planet
        self.mining_performed = {}


class _FakePlanet:
    name = "test planet"

    def __init__(self, atmospheric_keys=()):
        self.planet_data = {key: 0 for key in atmospheric_keys}
        self.gas_changes = []

    def change_gas_in_atmosphere(self, gas, ton):
        if f"athmospheric_{gas}" not in self.planet_data:
            raise AssertionError(f"non-atmospheric byproduct should not be treated as gas: {gas}")
        self.gas_changes.append((gas, ton))


def _production_firm(byproducts, planet):
    sol = _FakeSolarSystem()
    firm = company.firm.__new__(company.firm)
    firm.name = "test producer"
    firm.owner = object()
    firm.solar_system_object_link = sol
    firm.location = _FakeLocation(planet)
    firm.last_consumption_date = sol.start_date
    firm.stock_dict = {}
    firm.input_output_dict = {
        "input": {},
        "output": {},
        "timeframe": 30,
        "byproducts": byproducts,
    }
    return firm, sol


def test_non_atmospheric_byproduct_does_not_crash_production():
    firm, sol = _production_firm({"radioactive waste": 10}, _FakePlanet())

    firm.execute_stock_change(sol.start_date + datetime.timedelta(days=60))

    assert firm.last_consumption_date == sol.start_date + datetime.timedelta(days=60)


def test_atmospheric_byproduct_still_changes_planet_atmosphere():
    planet = _FakePlanet(["athmospheric_carbondioxide"])
    firm, sol = _production_firm({"carbondioxide": 10}, planet)

    firm.execute_stock_change(sol.start_date + datetime.timedelta(days=60))

    assert planet.gas_changes == [("carbondioxide", 20)]
