import pytest
import os
import datetime
import pickle
from PIL import Image
from planet import planet
from company import company
from solarsystem import solarsystem
import global_variables
from savegame import PAYLOAD_TYPE, SAVE_FORMAT, SAVE_VERSION, SaveFormatError


def test_solar_system_initialization():
    sol = solarsystem(global_variables.start_date, de_novo_initialization = True)

    # Assertion statements
    assert hasattr(sol, '__dict__')
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
    assert sol.solar_system_zoom == 20480  # Check if the solar system zoom is set correctly
    assert len(sol.areas_of_interest) == 0  # Check if the areas of interest dictionary is empty initially
    assert sol.company_selected is None  # Check if the company selected is set to None initially
    assert sol.firm_selected is None  # Check if the firm selected is set to None initially
    assert sol.go_to_planetary_mode is False  # Check if the go to planetary mode is set to False initially
    assert len(sol.planets) > 0  # Check if there are planets initialized
    assert len(sol.companies) > 0  # Check if there are companies initialized
    assert sol.current_planet == sol.planets["sun"]  # Check if the current planet is set correctly initially


def test_save_and_load_solar_system(tmpdir):
    def compare_attributes(obj1, obj2, level=0, max_depth=10):
        if level >= max_depth:
            return True  # Exit recursion if maximum depth is reached
    
        if obj1 is None and obj2 is None:
            return True
    
        if isinstance(obj1, (int, float, str, bool, tuple, type(None), datetime.date, list)):
            return obj1 == obj2
    
        if isinstance(obj1, dict):
            for key in obj1:
                if key not in obj2:
                    print(f"Key '{key}' is missing in the second dictionary.")
                    return False
                if not isinstance(obj1[key], (int, float, str, bool, tuple, type(None), datetime.date, list)):
                    continue
                if not compare_attributes(obj1[key], obj2[key], level + 1, max_depth):
                    print(f"Values for key '{key}' are different:")
                    print(f"Value 1: {obj1[key]}")
                    print(f"Value 2: {obj2[key]}")
                    return False
            return True

        if hasattr(obj1, '__dict__'):
            for attr in obj1.__dict__:
                if 'display' in attr.lower():
                    continue  # Skip attributes containing 'display'
                if not compare_attributes(getattr(obj1, attr), getattr(obj2, attr), level + 1, max_depth):
                    attr_value1 = getattr(obj1, attr)
                    attr_value2 = getattr(obj2, attr)
                    attr_class1 = obj1.__class__.__name__
                    attr_class2 = obj2.__class__.__name__
                    attr_type1 = type(attr_value1).__name__
                    attr_type2 = type(attr_value2).__name__
                    print(f"Difference found in attribute '{attr}':")
                    print(f"Class: {attr_class1} and {attr_class2}")
                    print(f"Type: {attr_type1} and {attr_type2}")
                    print(f"Value 1: {attr_value1}")
                    print(f"Value 2: {attr_value2}")
                    return False
            return True
    
        return False  # Default case: objects are not comparable
    

    # Define the start date string
    start_date_str = "2024-05-01"

    # Parse the start date string into a datetime.date object
    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()

    # Create a temporary directory to save the file
    save_dir = tmpdir.mkdir("save_files")
    save_file_path = os.path.join(save_dir, "test_save_file.pkl")

    # Create a new solar system instance and initialize planets
    old_solar_system = solarsystem(start_date=start_date)
    old_solar_system.initialize_planets()

    # Save the solar system settings
    old_solar_system.save_solar_system(save_file_path)

    # Create a new solar system instance and load the saved settings
    new_solar_system = solarsystem(start_date=start_date)
    new_solar_system.load_solar_system(save_file_path)

    # Assertions
    assert os.path.exists(save_file_path)

    # Compare attributes of old and new solar system instances
    assert compare_attributes(old_solar_system, new_solar_system, max_depth=10), "Attributes of old and new solar system instances are not the same"


def test_save_and_load_solar_system_with_loaded_planet_images(tmpdir):
    """Saving should survive planet PIL images/resource maps loaded in memory.

    Planet drawing lazily loads images that cannot be pickled directly.  This
    regression test exercises the conversion/restoration path that ordinary
    bare save/load tests miss.
    """
    save_file_path = os.path.join(tmpdir.mkdir("save_files"), "image_save_file.pkl")

    old_solar_system = solarsystem(start_date=global_variables.start_date)
    old_solar_system.initialize_planets()
    earth = old_solar_system.planets["earth"]
    earth.calculate_topography()
    earth.calculate_resource_map("iron")

    original_topo_size = earth.topo_image.size
    original_resource_size = earth.resource_maps["iron"].size

    old_solar_system.save_solar_system(save_file_path)

    assert isinstance(earth.topo_image, Image.Image)
    assert isinstance(earth.resource_maps["iron"], Image.Image)
    assert earth.topo_image.size == original_topo_size
    assert earth.resource_maps["iron"].size == original_resource_size

    new_solar_system = solarsystem(start_date=global_variables.start_date)
    new_solar_system.load_solar_system(save_file_path)
    loaded_earth = new_solar_system.planets["earth"]

    assert isinstance(loaded_earth.topo_image, Image.Image)
    assert isinstance(loaded_earth.resource_maps["iron"], Image.Image)
    assert loaded_earth.topo_image.size == original_topo_size
    assert loaded_earth.resource_maps["iron"].size == original_resource_size
    assert loaded_earth.solar_system_object_link is new_solar_system


def test_load_legacy_raw_pickle_with_loaded_planet_images(tmpdir):
    """Raw legacy pickles may contain PIL Images instead of serialized dicts."""
    save_file_path = os.path.join(tmpdir.mkdir("save_files"), "legacy_raw.pkl")

    old_solar_system = solarsystem(start_date=global_variables.start_date)
    old_solar_system.initialize_planets()
    earth = old_solar_system.planets["earth"]
    earth.calculate_topography()
    earth.calculate_resource_map("iron")
    original_topo_size = earth.topo_image.size
    original_resource_size = earth.resource_maps["iron"].size

    import pickle

    with open(save_file_path, "wb") as save_file:
        pickle.dump(old_solar_system, save_file)

    new_solar_system = solarsystem(start_date=global_variables.start_date)
    new_solar_system.load_solar_system(save_file_path)
    loaded_earth = new_solar_system.planets["earth"]

    assert isinstance(loaded_earth.topo_image, Image.Image)
    assert isinstance(loaded_earth.resource_maps["iron"], Image.Image)
    assert loaded_earth.topo_image.size == original_topo_size
    assert loaded_earth.resource_maps["iron"].size == original_resource_size
    assert loaded_earth.solar_system_object_link is new_solar_system


def test_save_restores_loaded_planet_images_when_pickle_fails(tmpdir):
    """A failed save must not leave live planet images in serialized dict form."""
    save_file_path = os.path.join(tmpdir.mkdir("save_files"), "failed_save.pkl")

    old_solar_system = solarsystem(start_date=global_variables.start_date)
    old_solar_system.initialize_planets()
    earth = old_solar_system.planets["earth"]
    earth.calculate_topography()
    earth.calculate_resource_map("iron")
    setattr(old_solar_system, "unpickleable_for_test", lambda: None)

    old_solar_system.save_solar_system(save_file_path)

    assert isinstance(earth.topo_image, Image.Image)
    assert isinstance(earth.resource_maps["iron"], Image.Image)
    assert not os.path.exists(save_file_path + ".tmp")


def test_new_solar_system_saves_use_versioned_wrapper(tmpdir):
    save_file_path = os.path.join(tmpdir.mkdir("save_files"), "wrapped.pkl")
    old_solar_system = solarsystem(start_date=global_variables.start_date)
    old_solar_system.initialize_planets()

    old_solar_system.save_solar_system(save_file_path)

    with open(save_file_path, "rb") as save_file:
        saved_object = pickle.load(save_file)
    assert saved_object["format"] == SAVE_FORMAT
    assert saved_object["version"] == SAVE_VERSION
    assert saved_object["payload_type"] == PAYLOAD_TYPE
    assert isinstance(saved_object["created_at"], str)
    assert isinstance(saved_object["payload"], solarsystem)


def test_versioned_wrapper_loads_solar_system(tmpdir):
    save_file_path = os.path.join(tmpdir.mkdir("save_files"), "wrapped.pkl")
    old_solar_system = solarsystem(start_date=global_variables.start_date)
    old_solar_system.initialize_planets()
    old_solar_system.current_date = global_variables.start_date + datetime.timedelta(days=42)
    old_solar_system.save_solar_system(save_file_path)

    new_solar_system = solarsystem(start_date=global_variables.start_date)
    new_solar_system.load_solar_system(save_file_path)

    assert new_solar_system.current_date == old_solar_system.current_date
    assert new_solar_system.planets["earth"].solar_system_object_link is new_solar_system


def test_unsupported_wrapper_version_fails_without_mutating_current_system(tmpdir):
    save_file_path = os.path.join(tmpdir.mkdir("save_files"), "unsupported.pkl")
    payload = solarsystem(start_date=global_variables.start_date)
    payload.initialize_planets()
    with open(save_file_path, "wb") as save_file:
        pickle.dump(
            {
                "format": SAVE_FORMAT,
                "version": SAVE_VERSION + 1,
                "created_at": "2026-06-11T12:00:00+00:00",
                "payload_type": PAYLOAD_TYPE,
                "payload": payload,
            },
            save_file,
        )

    current_system = solarsystem(start_date=global_variables.start_date)
    current_system.initialize_planets()
    sentinel = object()
    current_system.mutation_sentinel_for_test = sentinel

    with pytest.raises(SaveFormatError, match="Unsupported savegame version"):
        current_system.load_solar_system(save_file_path)

    assert current_system.mutation_sentinel_for_test is sentinel


@pytest.mark.parametrize(
    ("contents", "message"),
    [
        (b"", "empty"),
        (b"not a pickle", "could not be unpickled"),
    ],
)
def test_corrupt_or_empty_save_fails_without_mutating_current_system(tmpdir, contents, message):
    save_file_path = os.path.join(tmpdir.mkdir("save_files"), "bad.pkl")
    with open(save_file_path, "wb") as save_file:
        save_file.write(contents)

    current_system = solarsystem(start_date=global_variables.start_date)
    current_system.initialize_planets()
    sentinel = object()
    current_system.mutation_sentinel_for_test = sentinel

    with pytest.raises(SaveFormatError, match=message):
        current_system.load_solar_system(save_file_path)

    assert current_system.mutation_sentinel_for_test is sentinel


def test_invalid_payload_fails_without_mutating_current_system(tmpdir):
    save_file_path = os.path.join(tmpdir.mkdir("save_files"), "invalid.pkl")
    with open(save_file_path, "wb") as save_file:
        pickle.dump(
            {
                "format": SAVE_FORMAT,
                "version": SAVE_VERSION,
                "created_at": "2026-06-11T12:00:00+00:00",
                "payload_type": "wrong-payload",
                "payload": object(),
            },
            save_file,
        )

    current_system = solarsystem(start_date=global_variables.start_date)
    current_system.initialize_planets()
    sentinel = object()
    current_system.mutation_sentinel_for_test = sentinel

    with pytest.raises(SaveFormatError, match="Unsupported savegame payload type"):
        current_system.load_solar_system(save_file_path)

    assert current_system.mutation_sentinel_for_test is sentinel


