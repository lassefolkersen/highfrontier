import random

import pytest

import company as company_module
import global_variables
from solarsystem import solarsystem


def test_initial_bootstrap_firms_do_not_exceed_their_home_city_population():
    random.seed(12345)
    sol = solarsystem(global_variables.start_date, de_novo_initialization=True)

    oversize_firms = []
    for company_instance in sol.companies.values():
        for firm_instance in company_instance.owned_firms.values():
            if getattr(firm_instance, "technology_name", None) == "Base":
                continue
            location = getattr(firm_instance, "location", None)
            if location is None or not hasattr(location, "population"):
                continue
            if firm_instance.size > location.population:
                oversize_firms.append(
                    (company_instance.name, firm_instance.name, firm_instance.size, location.population)
                )

    assert oversize_firms == []


def test_company_database_integer_genes_stay_within_1_to_100():
    random.seed(12345)
    sol = solarsystem(global_variables.start_date, de_novo_initialization=True)

    out_of_bounds = []
    for company_instance in sol.companies.values():
        for gene_name, gene_value in company_instance.company_database.items():
            if isinstance(gene_value, int):
                if not 1 <= gene_value <= 100:
                    out_of_bounds.append((company_instance.name, gene_name, gene_value))

    assert out_of_bounds == []


def test_model_company_database_rejects_integer_genes_outside_1_to_100():
    company_instance = company_module.company.__new__(company_module.company)

    with pytest.raises(ValueError, match="desired_gini_coefficent"):
        company_instance.calculate_company_database(
            {"desired_gini_coefficent": 101}, standard_deviation=0
        )


def test_strategy_selector_maps_company_genes_to_one_based_strategy_keys():
    strategies = {1: "low", 2: "medium", 3: "high"}

    assert company_module.select_strategy(strategies, 1) == "low"
    assert company_module.select_strategy(strategies, 33) == "low"
    assert company_module.select_strategy(strategies, 34) == "medium"
    assert company_module.select_strategy(strategies, 66) == "medium"
    assert company_module.select_strategy(strategies, 67) == "high"
    assert company_module.select_strategy(strategies, 100) == "high"
