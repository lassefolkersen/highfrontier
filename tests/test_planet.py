import pytest
from planet import planet
from company import company
from solarsystem import solarsystem
import global_variables


def test_solar_system_initialization():
    sol = solarsystem(global_variables.start_date, de_novo_initialization = True)

    # Assertion statements
    assert sol.display_mode == Display.PLANETARY  # Check if the display mode is set to planetary
    assert sol.effectuate_migration == global_variables.effectuate_migration  # Check if migration effectuation is set correctly
    assert sol.effectuate_growth == global_variables.effectuate_growth  # Check if growth effectuation is set correctly
    assert sol.current_player is None  # Check if the current player is set to None initially
    assert sol.start_date == global_variables.start_date  # Check if the start date is set correctly
    assert sol.current_date == sol.start_date  # Check if the current date is set to the start date initially
    assert sol.step_delay_time == global_variables.step_delay_time  # Check if the step delay time is set correctly
    assert sol.technology_research_cost == global_variables.technology_research_cost  # Check if the technology research cost is set correctly
    assert sol.bitterness_of_world == (None, None)  # Check if the bitterness of the world is initialized correctly
    assert sol.build_base_mode is False  # Check if the build base mode is set to False initially
    assert sol.building_base is None  # Check if the building base is set to None initially
    assert len(sol.messages) == 0  # Check if the messages list is empty initially
    assert sol.window_size == global_variables.window_size  # Check if the window size is set correctly
    assert sol.universe_creation_date == datetime.date(1969, 7, 16)  # Check if the universe creation date is set correctly
    assert sol.solar_system_zoom == 20480  # Check if the solar system zoom is set correctly
    assert len(sol.areas_of_interest) == 0  # Check if the areas of interest dictionary is empty initially
    assert sol.company_selected is None  # Check if the company selected is set to None initially
    assert sol.firm_selected is None  # Check if the firm selected is set to None initially
    assert sol.go_to_planetary_mode is False  # Check if the go to planetary mode is set to False initially
    assert len(sol.planets) > 0  # Check if there are planets initialized
    assert isinstance(sol.technology_tree, technology.Tree)  # Check if the technology tree is initialized correctly
    assert len(sol.companies) > 0  # Check if there are companies initialized
    assert sol.current_planet == sol.planets["sun"]  # Check if the current planet is set correctly initially
