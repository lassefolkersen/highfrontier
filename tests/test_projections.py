import pytest

from planet import planet as planet_class
from solarsystem import solarsystem

import global_variables

import numpy as np


# Fixture to set up a solar system for testing
@pytest.fixture
def planet() -> planet_class:
    solar_system = solarsystem(global_variables.start_date, de_novo_initialization=True)
    solar_system.initialize_planets()
    return solar_system.planets["earth"]


def test_projection_on_earth(planet: planet_class):


    projected_coordinates = planet.sphere_to_plane_total(
        sphere_coordinates=[(0, 0), (180, 0), (-180, 90), (90, 45), (90, 0)],
        eastern_inclination=0,
        northern_inclination=0,
        projection_scaling=1,
    )

    # Center of the sphere (Equator, Prime Meridian)
    assert projected_coordinates[0] == (0.5, 0.5)
    # Equator, 180 degrees East, is not seen on the map so gives non-finite values
    assert all(~np.isfinite(projected_coordinates[1]))
    # North Pole
    assert projected_coordinates[2] == (0.5, 0)

    # 45 degrees North, 90 degrees East
    assert all(np.isfinite(projected_coordinates[3]))

    # 0 degrees North, 90 degrees East
    assert projected_coordinates[4] == (1, 0.5)

def test_projection_shifted(planet: planet_class):


    projected_coordinates = planet.sphere_to_plane_total(
        sphere_coordinates=[(0, 0), (180, 0), (-180, 90), (90, 45), (90, 0)],
        eastern_inclination=90,
        northern_inclination=45,
        projection_scaling=1,
    )

    # Center of the sphere (Equator, Prime Meridian) is seen
    assert all(np.isfinite(projected_coordinates[0]))
    # Equator, 180 degrees East, is  seen on the map so gives non-finite values
    assert projected_coordinates[1] == (1, 0.5)
    # North Pole
    assert all(np.isfinite(projected_coordinates[2]))

    # 45 degrees North, 90 degrees East is the center now
    assert projected_coordinates[3] == (0.5, 0.5)

    # 0 degrees North, 90 degrees East
    assert all(np.isfinite(projected_coordinates[4]))


def test_inverted_projection(planet: planet_class):

    xxs, yys = planet.plane_to_sphere_total(
        eastern_inclination=0,
        northern_inclination=0,
        projection_scaling=1,
        given_coordinates=[(0.5, 0.5), (1, 0.5), (0.5, 0), (0.5, 0.5), (1, 0.75)]
    )
    # Convert to list of tuples
    planet_coordinates = [(x, y) for x, y in zip(xxs, yys)]

    # Center of the sphere (Equator, Prime Meridian)
    assert planet_coordinates[0] == (0, 0)

    # Equator, 180 degrees East
    assert planet_coordinates[1] == (90, 0)

    # North Pole
    assert planet_coordinates[2][1] ==  90

    # Center of the sphere (Equator, Prime Meridian)
    assert planet_coordinates[3] == (0, 0)

    # This is not a valid coordinate
    assert all(~np.isfinite(planet_coordinates[4]))
