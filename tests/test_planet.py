import os
import pytest
from planet import planet
from company import company
from solarsystem import solarsystem
import global_variables
from planet import planet


# Fixture to set up a solar system for testing
@pytest.fixture
def solar_system():
    return solarsystem(global_variables.start_date, de_novo_initialization=True)


# Test initialization of Earth
def test_earth_initialization(solar_system):
    solar_system.initialize_planets()
    Earth = solar_system.planets["earth"]
    # Test inclination_degrees
    assert Earth.planet_data["inclination_degrees"] == 0
    assert isinstance(Earth.planet_data["inclination_degrees"], float)

    # Test athmospheric_oxygen
    assert Earth.planet_data["athmospheric_oxygen"] == 212223.5
    assert isinstance(Earth.planet_data["athmospheric_oxygen"], float)

    # Test satellite_order
    assert Earth.planet_data["satellite_order"] == 3
    assert isinstance(Earth.planet_data["satellite_order"], int)

    # Test eccentricity
    assert Earth.planet_data["eccentricity"] == 0.017
    assert isinstance(Earth.planet_data["eccentricity"], float)

    # Add more tests as needed

# Test initialization of Mars
def test_mars_initialization(solar_system):
    solar_system.initialize_planets()
    Mars = solar_system.planets["mars"]
    # Test inclination_degrees
    assert Mars.planet_data["inclination_degrees"] == 5.650
    assert isinstance(Mars.planet_data["inclination_degrees"], float)

    # Test athmospheric_oxygen
    assert Mars.planet_data["athmospheric_oxygen"] == 1.6
    assert isinstance(Mars.planet_data["athmospheric_oxygen"], float)

    # Test satellite_order
    assert Mars.planet_data["satellite_order"] == 4
    assert isinstance(Mars.planet_data["satellite_order"], int)

    # Test eccentricity
    assert Mars.planet_data["eccentricity"] == 0.093
    assert isinstance(Mars.planet_data["eccentricity"], float)

    # Add more tests as needed

