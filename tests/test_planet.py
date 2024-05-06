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


# Test change_gas_in_atmosphere method
def test_change_gas_in_atmosphere(solar_system):
    solar_system.initialize_planets()
    Earth = solar_system.planets["earth"]

    # Before change
    initial_pressure = Earth.planet_data["athmospheric_carbondioxide"]

    # Change the atmosphere
    Earth.change_gas_in_atmosphere("carbondioxide", 10000)  # Add many tons of CO2

    # Check it worked
    assert getattr(Earth, "athmospheric_" + "carbondioxide") == 397.77133333333336





# Test check_gas_in_atmosphere method for raising waters
def test_check_gas_in_atmosphere(solar_system):
    solar_system.initialize_planets()
    Earth = solar_system.planets["earth"]
    
    # Set Earth's atmospheric CO2 level to be higher than the initial value
    Earth.change_gas_in_atmosphere("carbondioxide", 1000000)  # Add many tons of CO2

    # Before change
    initial_water_level = Earth.water_level

    # Check if water level should be raised
    Earth.check_gas_in_atmosphere()

    # Check if water level has changed
    assert Earth.water_level == initial_water_level + 0.5
    assert isinstance(Earth.water_level, float)


# Test read_pre_base_file method
def test_read_pre_base_file(solar_system):
    solar_system.initialize_planets()
    Earth = solar_system.planets["earth"]
    
    # Read pre-base file for Mars
    bases = Earth.read_pre_base_file("earth")
    
    # Check if bases are correctly read
    assert isinstance(bases, dict)
    assert len(bases) > 0
    assert "stockholm" in bases.keys()
    assert "new york" in bases.keys()


# Test calculate_distance method
def test_calculate_distance(solar_system):
    solar_system.initialize_planets()
    Earth = solar_system.planets["earth"]
    
    # Calculate distance between two points on Earth
    distance = Earth.calculate_distance((0, 0), (45, 45))
    
    # Check if distance is calculated correctly
    assert isinstance(distance, list)
    assert len(distance) == 1  # Only one distance calculated
    assert isinstance(distance[0], float)
    assert distance[0] > 0  # Distance should be positive


# Test check_environmental_safety method
def test_check_environmental_safety(solar_system):
    solar_system.initialize_planets()
    Earth = solar_system.planets["earth"]
    
    # Check environmental safety of Earth
    safety = Earth.check_environmental_safety()
    
    # Check if safety assessment is correct
    assert safety == "Breathable atmosphere"  # Earth has a breathable atmosphere by default

