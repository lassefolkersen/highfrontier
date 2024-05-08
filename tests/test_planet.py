import os
import pytest
import pygame
from PIL import Image, ImageChops, ImageOps, ImageFile,ImageFilter,ImageEnhance
from planet import planet
from company import company
from solarsystem import solarsystem
import global_variables
from planet import planet


# Fixture to set up a solar system for testing
@pytest.fixture
def solar_system():
    solar_system = solarsystem(global_variables.start_date, de_novo_initialization=True)
    solar_system.initialize_planets()
    return solar_system


# Test initialization of Earth
def test_earth_initialization(solar_system):
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
    Earth = solar_system.planets["earth"]

    # Before change
    initial_pressure = Earth.planet_data["athmospheric_carbondioxide"]

    # Change the atmosphere
    Earth.change_gas_in_atmosphere("carbondioxide", 10000)  # Add many tons of CO2

    # Check it worked
    assert getattr(Earth, "athmospheric_" + "carbondioxide") == 397.77133333333336





# Test check_gas_in_atmosphere method for raising waters
def test_check_gas_in_atmosphere(solar_system):
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
    Earth = solar_system.planets["earth"]
    
    # Check environmental safety of Earth
    safety = Earth.check_environmental_safety()
    
    # Check if safety assessment is correct
    assert safety == "Breathable atmosphere"  # Earth has a breathable atmosphere by default



def test_pickle_all_projections_existing_files(solar_system, tmpdir):
    tmp_dir = tmpdir.mkdir("pickledsurfaces")
    planet_instance = solar_system.planets["earth"]
    
    # Create mock pre-drawn images in the temporary directory
    for projection_scaling in (45, 90, 180, 360):
        for eastern_inclination in (-150, -120, -90, -60, -30, 0, 30, 60, 90, 120, 150, 180):
            for northern_inclination in (-90, -60, -30, 0, 30, 60, 90):
                pickle_file_name = f"{planet_instance.planet_name}_{projection_scaling}_zoom_{northern_inclination}_NS_{eastern_inclination}_EW.jpg"
                open(os.path.join(tmp_dir, pickle_file_name), "w").close()  # Create empty file

    # Call the function
    planet_instance.pickle_all_projections()

    # Assertions: Check if pre-drawn surfaces are correctly loaded into pre_drawn_surfaces
    for projection_scaling in (45, 90, 180, 360):
        for eastern_inclination in (-150, -120, -90, -60, -30, 0, 30, 60, 90, 120, 150, 180):
            for northern_inclination in (-90, -60, -30, 0, 30, 60, 90):
                assert (northern_inclination, eastern_inclination, projection_scaling) in planet_instance.pre_drawn_surfaces
                assert isinstance(planet_instance.pre_drawn_surfaces[(northern_inclination, eastern_inclination, projection_scaling)], pygame.Surface)




def test_load_for_drawing(solar_system, tmpdir):
    # Pick an example planet, like Earth
    planet_instance = solar_system.planets["earth"]

    # Call the function
    planet_instance.load_for_drawing()

    # Assertions
    assert hasattr(planet_instance, "image")  # Check if the image attribute exists
    assert isinstance(planet_instance.image, Image.Image)  # Check if the image is an instance of PIL Image

    # Check if the placeholder image is loaded when the actual image file is missing
    if not os.path.exists(planet_instance.surface_file_name):
        assert planet_instance.image.size == (1800, 900)  # Check if the image is resized to (1800, 900)

    # Call the unload_from_drawing function
    planet_instance.unload_from_drawing()

    # Assertions for unloading
    assert not hasattr(planet_instance, "image")  # Check if the image attribute is removed
    assert not hasattr(planet_instance, "heat_bar")  # Check if the heat_bar attribute is removed
    assert planet_instance.pre_drawn_action_layers == {}  # Check if the pre_drawn_action_layers attribute is empty



def test_calculate_topography(solar_system):
    planet_instance = solar_system.planets["jupiter"] #can also do earth or mars, just checking the gasplanet setup here

    # Call the calculate_topography function
    planet_instance.calculate_topography()

    # Assertions
    assert hasattr(planet_instance, "topo_image")  # Check if the topo_image attribute exists
    assert isinstance(planet_instance.topo_image, Image.Image)  # Check if the topo_image is an instance of PIL Image

    # Check if the topo_image is created correctly
    topo_file_name_and_path = os.path.join("images", "planet", "topo", str(planet_instance.planet_name + ".png"))
    if os.path.exists(topo_file_name_and_path):
        assert planet_instance.topo_image.size == (720, 360)  # Check if the topo_image is resized to (720, 360)
        # Add more assertions to check the content or characteristics of the topo_image if needed
    else:
        assert planet_instance.planet_type == "gasplanet" 
        assert planet_instance.topo_image.size == (720, 360)  # Check if the topo_image size matches the default gas planet size




def test_change_water_level(solar_system):
    # Pick an example planet, like Earth
    planet_instance = solar_system.planets["earth"]

    # Set a new water level
    new_water_level = 5

    # Call the change_water_level function
    planet_instance.change_water_level(new_water_level)

    # Assertions
    assert planet_instance.water_level == new_water_level  # Check if the water level is updated correctly

    # Check if the action_layer attribute is created
    assert hasattr(planet_instance, "action_layer")

    # Check if the bases on the planet are affected correctly
    for base in planet_instance.bases.values():
        if base.terrain_type != "Space":
            position_x_degrees = base.position_coordinate[0]
            position_y_degrees = base.position_coordinate[1]

            position_x_pixel = int(((position_x_degrees + 180.0) / 360.0) * planet_instance.action_layer.size[0])
            position_y_pixel = int(planet_instance.action_layer.size[1] - ((position_y_degrees + 90.0) / 180.0) * planet_instance.action_layer.size[1])
            pixel_color = planet_instance.action_layer.getpixel((position_x_pixel, position_y_pixel))

            if 190 < pixel_color <= 220 or pixel_color == 0:
                assert base.is_on_dry_land == "no"  # Check if the base is considered under water
            elif 220 < pixel_color <= 250:
                assert base.is_on_dry_land == "almost"  # Check if the base is considered almost under water
            else:
                assert base.is_on_dry_land == "yes"  # Check if the base is considered on dry land



def test_convert_to_rgba(solar_system, tmpdir):
    # Pick an example planet, like Earth
    planet_instance = solar_system.planets["earth"]

    # Load a sample image for testing
    test_image_path = os.path.join("images", "planet", "moon.jpg")
    test_image = Image.open(test_image_path)

    # Convert the test image to grayscale
    test_image_bw = ImageOps.grayscale(test_image)

    # Call the convert_to_rgba function
    rgba_image = planet_instance.convert_to_rgba(test_image_bw)

    # Assertions
    assert rgba_image.mode == "RGBA"  # Check if the output image mode is RGBA

    # Check if the size of the output image is the same as the input image
    assert rgba_image.size == test_image_bw.size

    # Check if other RGBA values are calculated correctly
    for i in range(1, 191):
        assert rgba_image.getpixel((i, 0)) == (0, 0, 0, 0)  # Assuming image width is 1080
    for i in range(251, 256):
        assert rgba_image.getpixel((i, 0)) == (0, 0, 0, 0)  # Assuming image width is 1080




def test_sphere_to_plane_total(solar_system, tmpdir):
    # Pick an example planet, like Earth
    planet_instance = solar_system.planets["earth"]

    # Define sample sphere coordinates
    sphere_coordinates = [(0, 0), (45, 45), (90, 90)]

    # Define projection parameters
    eastern_inclination = 0
    northern_inclination = 0
    projection_scaling = 360

    # Call the sphere_to_plane_total function
    projection_coordinates = planet_instance.sphere_to_plane_total(sphere_coordinates, eastern_inclination, northern_inclination, projection_scaling)

    # Assertions
    assert len(projection_coordinates) == len(sphere_coordinates)  # Check if the number of projection coordinates matches the number of sphere coordinates

    # Print out the projection coordinates for examination
    print("Projection Coordinates:")
    for i, coord in enumerate(projection_coordinates):
        print(f"Sphere Coordinate {i+1}: {sphere_coordinates[i]} -> Projection Coordinate: {coord}")



def test_plane_to_sphere_total(solar_system, tmpdir):
    # Pick an example planet, like Earth
    planet_instance = solar_system.planets["earth"]

    # Define projection parameters
    eastern_inclination = 0
    northern_inclination = 0
    projection_scaling = 360

    # Define sample projection coordinates
    sample_coordinates = [(0, 0), (180, 180), (360, 360)]

    # Call the plane_to_sphere_total function
    result = planet_instance.plane_to_sphere_total(eastern_inclination, northern_inclination, projection_scaling, given_coordinates=sample_coordinates)

    # Print out the result for examination
    print("Result:")
    for coord, sphere_coord in result.items():
        print(f"Projection Coordinate: {coord} -> Sphere Coordinate: {sphere_coord}")




def test_calculate_resource_map_existing(solar_system, tmpdir):
    # Create a temporary directory to mimic the file system
    temp_dir = tmpdir.mkdir('images')
    planet_instance = solar_system.planets["earth"]

    # Create a sample resource map file
    resource_type = 'iron'
    planet_name = 'earth'
    resource_file_name = f"{resource_type}_{planet_name}.png"
    resource_file_path = temp_dir.join(resource_file_name)
    with open(resource_file_path, 'w') as f:
        f.write("Sample resource map content")

    # Assign the resource map directory to the planet instance
    planet_instance.resource_maps = {}

    # Call the calculate_resource_map method
    planet_instance.calculate_resource_map(resource_type)

    # Assert that the resource map is loaded
    assert resource_type in planet_instance.resource_maps
    assert planet_instance.resource_maps[resource_type].size == (90, 45)
    assert planet_instance.resource_maps[resource_type].mode == 'RGB'




def test_calculate_base_positions_existing(solar_system, tmpdir):
    # Create a temporary directory to mimic the file system
    temp_dir = tmpdir.mkdir('images')

    # Get an instance of the planet (e.g., Earth)
    planet_instance = solar_system.planets["earth"]

    # Call the calculate_base_positions method with the same parameters
    eastern_inclination = 0
    northern_inclination = 0
    projection_scaling = 360
    base_positions = planet_instance.calculate_base_positions(eastern_inclination, northern_inclination, projection_scaling)

    # Assert that the existing base positions are returned
    assert base_positions == planet_instance.base_positions[(northern_inclination, eastern_inclination, projection_scaling)]
    assert base_positions['phoenix'] == ['Not seen', (36.372838167606794, 71.50466192517058)]
    assert base_positions['moscow'] == (241, 21)
