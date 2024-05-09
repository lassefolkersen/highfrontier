import primitives
import logging
from pathlib import Path

import pygame, sys,os
from pygame.locals import *
#from ocempgui.widgets from PIL import ImageLabel
from PIL import Image, ImageChops, ImageOps, ImageFile,ImageFilter,ImageEnhance
import math
import subprocess
import time
import os
import global_variables
import company
import random

from pyproj import Transformer
import numpy as np



logger = logging.getLogger(__name__)



class planet:
    """
    The class that holds all methods of the planets
    And instance of class planet also holds all the base instances within.
    """

    def __init__(self,planet_name,solar_system_object_link,planet_data):
        planet_file_name = planet_name + ".jpg"
        self.solar_system_object_link = solar_system_object_link
        self.planet_data = planet_data
        self.planet_diameter_km = planet_data["diameter_km"]
        self.planet_type = planet_data["type"]
        self.current_base = None
        self.planet_name = planet_name
        self.name = planet_name
        self.surface_file_name = os.path.join("images","planet",planet_file_name)
        self.projection_scaling=45
        self.eastern_inclination = 0
        self.northern_inclination = 0
        self.gravity_at_surface = planet_data["gravity_at_surface"]
        self.surface_area = 4 * math.pi * ((planet_data["diameter_km"]*0.5) ** 2)

        self.logger = logging.getLogger(f"{__name__}.{planet_name}")

        self.athmospheric_surface_pressure_pa = self.planet_data["athmospheric_carbondioxide"]
        self.athmospheric_nitrogen = self.planet_data["athmospheric_carbondioxide"]
        self.athmospheric_carbondioxide = self.planet_data["athmospheric_carbondioxide"]
        self.athmospheric_oxygen = self.planet_data["athmospheric_oxygen"]
        self.athmospheric_helium = self.planet_data["athmospheric_helium"]
        self.athmospheric_hydrogen = self.planet_data["athmospheric_hydrogen"]





        self.areas_of_interest = {}
        self.base_positions = {}
        self.space_stations = {}
        self.pre_drawn_surfaces = {}
        self.pre_drawn_action_layers = {}
        self.resource_maps = {}
        self.planet_display_mode = "visible light"
        if self.name == "earth":
            self.water_level = 1
        else:
            self.water_level = 0
        self.bases = self.read_pre_base_file(planet_name)
        for base in list(self.bases.values()):
            base.calculate_trade_routes(self)

        self.co2_emissions = 0
        self.high_grade_greenhouse_gas_emissions = 0
        self.radioactive_emissions = 0





    def change_gas_in_atmosphere(self,gas,ton):
        """
        Function to manipulate partial gas pressure of the atmosphere of the planet.
        Takes the gas type, and an amount of gas in tons (can be negative). It then updates the partial pressure to reflect
        the change. The main use of the function is that takes into account the environment to which the gas is added.
        If a million tonnes of CO2 is added to a small dense planet it has a much larger effect on partial pressure than
        if the same amount is added to a large low gravity planet planet.

        The assumptions behind the calculations is simply that the higher the surface gravity the more partial pressure per ton of gas
        (because it will be drawn towards the surface), and also the larger the surface area of the planet the smaller the partial pressure
        per ton of gas (because it has more room to fill). Numbers are currently fitted to the fact that wikipedia ("Carbon dioxide in
        the Earth's atmosphere") states that there is today 3 terratonnes of CO2 in the atmosphere as of 2008. With a simple additive
        model is assumed. There is of course plenty of space for improvement in this model.
        """

        #according to wikipedia ("Carbon dioxide in the Earth's atmosphere") there is today 3 terratonnes of CO2 in the atmosphere
        ton_carbondioxide_on_earth_2008 = 3000000000000
        pascal_carbondioxide_on_earth_2008 = 384.94
        #we use this to calculate the ton_per_pascal factor (and do the rough assumption that it is the same for other gases)
        ton_per_pa_on_earth = ton_carbondioxide_on_earth_2008 / pascal_carbondioxide_on_earth_2008

        #we then take surface area and gravity of the planet in account and calculate a useful factor
        surface_area_ratio = self.solar_system_object_link.planets["earth"].surface_area / self.surface_area
        gravity_at_surface_ratio = self.solar_system_object_link.planets["earth"].gravity_at_surface / self.gravity_at_surface

        ton_per_pa_here = ton_per_pa_on_earth * gravity_at_surface_ratio / surface_area_ratio


        ton_per_pa_here = ton_per_pa_here / (global_variables.gas_change_multiplier * 100000) # for fine tuning in global variables. The number is to try to keep 100.0 a standard value.

        if str("athmospheric_" + gas) in list(self.planet_data.keys()):
            before = getattr(self, "athmospheric_" + gas)
            setattr(self, "athmospheric_" + gas, before + (ton / ton_per_pa_here))
            print_dict = {"text":"added " + str(ton) + " " + str(gas) + " to " + self.name + " which made the partial pressure change from " + str((before)) + " to " + str(getattr(self, "athmospheric_" + gas)),"type":"climate"}
            self.solar_system_object_link.messages.append(print_dict)
        else:
            raise Exception(self.name + " did not have a " + str("athmospheric_" + gas) + " entry in the athmospheric_ - only " + str(list(self.planet_data.keys())))






    def check_gas_in_atmosphere(self):
        """
        Checks if the water level of the planet should be raised
        At the moment this is a very simple implementation where it is only the carbondioxide level
        that plays in, but room for expansion of this model is open.
        """
        difference_from_original = self.athmospheric_carbondioxide - self.planet_data["athmospheric_carbondioxide"]
        if self.water_level * 10 + 10 < difference_from_original:
             before = self.water_level
             self.change_water_level(self.water_level + 0.5)
             print_dict = {"text":"The waters are rising on" + self.name + "!","type":"general gameplay info"}
             self.solar_system_object_link.messages.append(print_dict)



    def read_pre_base_file(self,planet_name):
        data_file_name = os.path.join("data","base_data",str(str(planet_name) + ".txt"))



        if os.access(data_file_name,os.R_OK):
            read_base_database = primitives.import_datasheet(data_file_name)
            base_database = {}

            #a placeholder "company to give the new bases. Since no companies are initialized yet, this is necessary
            class Placeholder():
                pass
            placeholder = Placeholder()
            placeholder.solar_system_object_link = self.solar_system_object_link

            for base_name in read_base_database:

                base_instance = company.base(self.solar_system_object_link,base_name,self,read_base_database[base_name],placeholder)

                base_database[base_name] = base_instance
            self.bases = base_database

        else: #ie. if no pre-designed bases are found
            base_database = {}
        return base_database






    def calculate_distance(self,position_a,position_b):
        """
        Takes two sphere_positions as tuples or two list of sphere_positions as tuples and return the distance
        between the two in kilometers based on the diameter_km entry in planet_data
        """
        if len(position_a) != len(position_b):
            if self.solar_system_object_link.message_printing["debugging"]:
                print_dict = {"text":"WARNING: The two lists given in calculate_distance() are not the same length","type":"debugging"}
                self.solar_system_object_link.messages.append(print_dict)


        result = []
        if isinstance(position_a,tuple):
            position_a = [position_a]
        if isinstance(position_b,tuple):
            position_b = [position_b]

        for i in range(len(position_a)):
            single_position_a = position_a[i]
            single_position_b = position_b[i]



            long_1 = math.radians(single_position_a[0])
            lat_1 = math.radians(single_position_a[1])
            long_2 = math.radians(single_position_b[0])
            lat_2 = math.radians(single_position_b[1])

#            probably not necessary
#            if long_1 > 2 * math.pi: long_1 = long_1 - 2 * math.pi
#            if long_1 < 0: long_1 = long_1 + 2 * math.pi
#            if long_2 > 2 * math.pi: long_2 = long_2 - 2 * math.pi
#            if long_2 < 0: long_2 = long_2 + 2 * math.pi

            dlong = long_2 - long_1
            dlat = lat_2 - lat_1
            a = (math.sin(dlat / 2))**2 + math.cos(lat_1) * math.cos(lat_2) * (math.sin(dlong / 2))**2
            c = 2 * math.asin(min(1, math.sqrt(a)))
            dist = self.planet_diameter_km * ( c / (2 * math.pi))
            result.append(dist)
        return result


    def calculate_all_distances(self):
        """
        Function that calculates all distances from all pixels, for use in assigning resource areas
        The pixel grid is the (90,45) used in the resource overlay map. The function will return a
        dictionary with keys being tuples of all 90 x 45 pixels. The value of each is another dictionary
        with keys being 1n,2n,3n,4n(distances in degrees, n = step_size variable) and values being the pixel-tuples
        within these distances.
        """

        step_size = 1
        steps = 9

        distance_matrix = {}

        planet_circumference = self.planet_diameter_km * math.pi
        x1 = 0
        for y1 in range(45):
            distance_matrix[(x1,y1)] = {}
            for i in range(0,step_size * steps,step_size):
                distance_matrix[(x1,y1)][i] = []

            for x2 in range(90):
                for y2 in range(45):

                    distance_km = self.calculate_distance(((x1*4)-180,(y1*4)-90),((x2*4)-180,(y2*4)-90))
                    distance_degrees = (360 * distance_km[0]) / planet_circumference
                    degree_rounding = int(distance_degrees / step_size) * step_size
                    if degree_rounding in list(distance_matrix[(x1,y1)].keys()):
                        distance_matrix[(x1,y1)][degree_rounding].append((x2,y2))

        distance_data = {"distance_matrix":distance_matrix,"step_size":step_size,"steps":steps}


        return distance_data



    def check_environmental_safety(self):
        """
        Function that will check if humans can live on the surface without housing.

        Returns ""Breathable atmosphere", "Survivable atmosphere", or "Lethal atmosphere"

        "Breathable atmosphere" is earth like
        "Survivable atmosphere" is not nice, but with simple assist devices it is possible (type breathing masks from Red Mars, Green Mars, Blue Mars)

        FIXME add temperature at some point
        """

        answer = "Breathable atmosphere"

        if self.planet_data["athmospheric_surface_pressure_pa"] < 500000:
            answer = "Survivable atmosphere"
            if self.planet_data["athmospheric_surface_pressure_pa"] < 300000:
                answer = "Lethal atmosphere"

        if self.planet_data["athmospheric_oxygen"] < 200000:
            answer = "Survivable atmosphere"
            if self.planet_data["athmospheric_oxygen"] < 150000:
                answer = "Lethal atmosphere"


        if self.planet_data["athmospheric_carbondioxide"] > 3840:
            answer = "Survivable atmosphere"
            if self.planet_data["athmospheric_carbondioxide"] > 38400:
                answer = "Lethal atmosphere"

        return answer




    @property
    def image(self):
        """
        Function that loads the picture of a planet and saves it in the instance.
        This function could probably be made much better, since some of the map_dim etc.
        are irelevant. Finally there could be a "unload" function or something.
        """
        if not hasattr(self, "_image"):
            self._load_for_drawing()
        return self._image

    def _load_for_drawing(self):
        if os.access(self.surface_file_name,os.R_OK):
            image = Image.open(self.surface_file_name)
        else:
            image = Image.open(os.path.join("images","planet","placeholder.jpg"))

        self.projection_dim = (self.projection_scaling,self.projection_scaling)

        size = image.size
        if((size[0]/size[1])!=2):
            logger.warning("The map file is not twice as wide as it is high !")
            image = image.resize((size[0], size[0]/2))

        if image.size[0] < 1800:
            image = image.resize((1800,900))

        if (self.water_level != 0 and self.name != "earth") or (self.water_level != 1 and self.name == "earth"):
            self.change_water_level(self.water_level)

        self._image = image





    def unload_from_drawing(self):
        """
        Unload the picture of a planet from memory.
        """

        if hasattr(self, "_image"):
            del self._image


        try: self.heat_bar
        except AttributeError:
            pass
        else:
            del self.heat_bar

        self.pre_drawn_action_layers = {}



    def calculate_topography(self):
        """
        Function that checks if a topography picture exists in the /images/planet/topo
        If not it "calculates" the topography based on the physical picture
        This is of course only an approximation to make it look realistic
        In all cases the output is that self.topo_image will contain a topographical image
        where red is lowest and yellow is highest.
        """
        #check if this has already been loaded
        try: self.topo_image
        except AttributeError:
            #test if a pre-calculated topo-file exists
            topo_file_name_and_path = os.path.join("images","planet","topo",str(self.planet_name + ".png"))
            if os.access(topo_file_name_and_path,os.R_OK):
                self.topo_image = Image.open(topo_file_name_and_path)
                #print "topo file does not exist for " + str(self.planet_name) + " - all ok"
            else:
                #print "topo file does not exist for " + str(self.planet_name)

                #see if a regular image has already been loaded
                if self.planet_type != "gasplanet":

                    regular_image = self.image

                    regular_image = ImageOps.grayscale(regular_image)
                    topo_image = ImageOps.posterize(regular_image, 5)
                    topo_image = ImageOps.colorize(topo_image,"red","yellow")
                    topo_image = topo_image.resize((720,360))

                    #topo_image.save("test.png") #for testing purposes
                    self.topo_image = topo_image
                else: #planet is a gasplanet
                    self.topo_image = Image.new("RGB",(720,360),(255,0,0))


        else:
            #print "self.topo_image does exists - all ok"
            pass


    def change_water_level(self,new_water_level):
        """
        Function to redraw the wet_area image for a planet, after the water level of that planet has been changed
        It checks if the topographical map has been loaded, and loads it if not it then computes the layout of
        the different topological levels. The function also checks if bases are getting flooded and removes them if necessary.

        The function saves a self.action_layer which is an "L" mode image that can receive region specific information. Currently this
        values are defined:
        191 - 220 are for newly flooded areas, 221 being for the lowest
        221 - 250 are for half-wet flooded areas, 221 being for the lowest. Only one number in this range should therefore exist
        255 is for dry areas
        0 is for earth oceans

        They can be translated with the convert_to_rgba
        """
        #testing if self.topo exists
        try: self.topo_image
        except AttributeError:
            self.calculate_topography()

        topo_image = self.topo_image

        #converting to BW
        topo_image_bw = ImageOps.grayscale(topo_image)
        assert topo_image_bw.mode == "L"



        # makes a dictionary with the topology level as key and a tuble of color-span for which this topology holds as the value
        colors_in_topo = topo_image_bw.getcolors()
#        print "colors_in_topo: " + str(colors_in_topo) #[(153835, 76), (30, 77), (42
        table_of_topology = {0:(0,0)}


        #we would like all planets to have max 30 levels of topology - the sum of all color[0] equals the number of pixels in the image
        pixels_in_image = topo_image_bw.size[0] * topo_image_bw.size[1]
        pixels_each_level = pixels_in_image / 30
#        print "pixels_each_level: " + str(pixels_each_level)
        sum_of_pixels = 0
        i = 1
        for color in colors_in_topo:
            sum_of_pixels = sum_of_pixels + color[0]

            if sum_of_pixels > pixels_each_level:
                topology_color_range = (table_of_topology[i-1][1],color[1])
                table_of_topology[i] = topology_color_range
                i = i + 1
                sum_of_pixels = 0
        del table_of_topology[0]
#        print "table_of_topology: " + str(table_of_topology) #{1: (0, 76), 2: (76, 90), 3: (90, 113), 4: (113, 127), 5: (127, 137), 6: (137, 141)}
#        print "the planet " + self.planet_name+ " has " + str(len(table_of_topology)) +" levels of topology"

        if new_water_level > len(table_of_topology):
            new_water_level = len(table_of_topology)
            if self.solar_system_object_link.message_printing["debugging"]:
                print_dict = {"text":"The planet " + str(self.planet_name) + " has reached its max water level of " + str(len(table_of_topology)),"type":"debugging"}
                self.solar_system_object_link.messages.append(print_dict)




        table_of_colors = []
        for i in range(256):
            topology_level_here = None
            for topology_level in table_of_topology:
                if table_of_topology[topology_level][0] < i <= table_of_topology[topology_level][1]:
                    topology_level_here = topology_level
                    break

            if topology_level_here is None:
                new_color = 255
            elif topology_level_here == 1 and self.planet_name == "earth":
                new_color = 0
            elif topology_level_here <= new_water_level:
                new_color = 190 + topology_level_here

            elif topology_level_here - 0.5 == new_water_level:
                new_color = 220 + topology_level_here
            else:
                new_color = 255

            table_of_colors.append(new_color)

        self.action_layer = topo_image_bw.point(table_of_colors)
        self.pre_drawn_action_layers = {}





        #determines how the bases on the planet fare in the surge. Bases under water are removed.
        bases_to_remove = []
        for base in self.bases:
            if self.bases[base].terrain_type != "Space":
                position_x_degrees = self.bases[base].position_coordinate[0]
                position_y_degrees = self.bases[base].position_coordinate[1]


                position_x_pixel = int(((position_x_degrees + 180.0 ) / 360.0) * self.action_layer.size[0])
                position_y_pixel = int(self.action_layer.size[1] - ((position_y_degrees + 90.0 ) / 180.0) * self.action_layer.size[1])
                pixel_color = self.action_layer.getpixel((position_x_pixel,position_y_pixel))
                if 190 < pixel_color <= 220 or pixel_color == 0:
                    self.bases[base].is_on_dry_land = "no"
                    bases_to_remove.append(base)
                elif 220 < pixel_color <= 250:
                    self.bases[base].is_on_dry_land = "almost"
                else:
                    self.bases[base].is_on_dry_land = "yes"
        for base in bases_to_remove:
            self.kill_a_base(base)

        if new_water_level != self.water_level:
            self.water_level = new_water_level








    def convert_to_rgba(self,image):
        """
        Function that takes a image with information about the surface and converts it to an RGBA type image ready for drawing

        Read the change_water_level documentation for more info on the different value codes.
        """

        water_colors = {
                        1:(16,40,44),
                        2:(18,44,50),
                        3:(19,49,54),
                        4:(20,51,56),
                        5:(22,58,61),
                        6:(25,63,69),
                        7:(28,66,72),
                        8:(30,70,76),
                        9:(33,73,79),
                        10:(33,83,82),
                        11:(36,86,85),
                        12:(37,84,90),
                        13:(40,87,93),
                        14:(39,88,94),
                        15:(40,90,97),
                        16:(41,93,99),
                        17:(42,95,102),
                        18:(43,98,105),
                        19:(44,100,107),
                        20:(45,102,110),
                        21:(46,104,112),
                        22:(47,107,115),
                        23:(48,110,117),
                        24:(49,112,120),
                        25:(50,114,123),
                        26:(51,117,125),
                        27:(52,119,128),
                        28:(53,121,131),
                        29:(54,121,131),
                        30:(53,121,131)}

        assert image.mode == "L"
        table_of_colors = []

        for band in range(4):
            for i in range(256):
                if band < 3:
                    if 190 < i <= 220:
                        RGB_color = water_colors[i - 190]
                        new_color = RGB_color[band]
                    elif 220 < i <= 250:
                        RGB_color = water_colors[i - 220]
                        new_color = RGB_color[band]
                    else:
                        new_color = 0
                else:
                    if 190 < i <= 220:
                        new_color = 255
                    elif 220 < i <= 250:
                        new_color = 255/2
                    else:
                        new_color = 0


                table_of_colors.append(new_color)
        new_image = image.point(table_of_colors,"RGBA")
        return new_image



    def sphere_to_plane_total(
        self,
        sphere_coordinates: list[tuple[float, float]] | np.ndarray,
        eastern_inclination: float,
        northern_inclination: float,
        projection_scaling: float,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Function to translate a list of single sphere_coordinates into projection coordinates with only one
        query to the proj program. Takes a list of tuples with sphere_coordinates.
        This is much faster than the old sphere_to_plane()

        General notes on maps:
                Three map coordinate types:
        Sphere... nothing is ever rendered like this. It is a tuple with (range(-180,180),range(-90,90),
        which corresponds to degrees. The first longitude / x / east-west, the second is latitude / y / north_south.

        Map.... the source map. It has map_coordinates that correspond to the size of the map (range(0, width(map))
        , range(0,height(map))). The map_coordinates are directly translatable to sphere_coordinates and are of course
        (east/west,north/south)

        Projection.... the main rendition of the planet projection. It has projection_coordinates (range(0,1*scale),range(0,1*scale))
        which corresponds to the location on the screen (top left is (0,0), further east is (1,0), and further
        south is (0,1). Pixels outside of the globe-projection are black. An important concept is the rotation
        which is the amount of turning the planet has seen relative to the 0 N, 0 W position. This is
        given as rotation_coordinates (range(-180,180),range(-90,90))


        The idea is to draw the projection by taking each pixel in the rendition, looking up its translation
        to sphere_coordinates and then paint the corresponding projection_coordinate.

        """
        if not sphere_coordinates:
            return [], []

        if isinstance(sphere_coordinates, tuple):
            sphere_coordinates = [sphere_coordinates]

        if projection_scaling <= global_variables.flat_earth_scaling_start: #for the round world projection

            arr = np.array(sphere_coordinates)
            x_sphere = arr[:,0]
            y_sphere = arr[:,1]


            startup_string = f"+proj=ortho +ellps=sphere +lon_0={eastern_inclination} +lat_0={northern_inclination}"

            transformer = Transformer.from_pipeline(startup_string)

            x, y = transformer.transform(x_sphere,y_sphere)

            half_scale = projection_scaling * 0.5

            x_proj = ( x / 6370997 ) * half_scale + half_scale  #where 6370997 is the constant of the proj program
            y_proj = -( y / 6370997 ) * half_scale + half_scale


        else: #planar map projection

            x_proj = []
            y_proj = []

            window_size = global_variables.window_size
            west_border = self.flat_image_borders["west_border"]
            east_border = self.flat_image_borders["east_border"]
            south_border = self.flat_image_borders["south_border"]
            north_border = self.flat_image_borders["north_border"]
            east_west_span = float(east_border - west_border) #114
            north_south_span = float(north_border - south_border)
#            sphere_hit_locations = []
            for sphere_coordinate in sphere_coordinates:
                if (west_border < sphere_coordinate[0] < east_border) and (south_border < sphere_coordinate[1] < north_border):
                    x_proj_position = (( sphere_coordinate[0] - west_border) / east_west_span ) * window_size[0]
                    y_proj_position = window_size[1] - ((( sphere_coordinate[1] - south_border ) / north_south_span ) * window_size[1])

                    x_proj.append(x_proj_position)
                    y_proj.append(y_proj_position)
                else:
                    x_proj.append(np.nan)
                    y_proj.append(np.nan)

            x_proj = np.array(x_proj)
            y_proj = np.array(y_proj)


        return x_proj, y_proj







    def plane_to_sphere_total(
        self,
        eastern_inclination: float,
        northern_inclination: float,
        projection_scaling: float,
        given_coordinates: np.ndarray | tuple,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        The function that calculates the relation of all the points on the projection to their sphere coordinates
        It returns a dictionary of all projection coordinates and their corresponding sphere coordinates
        This  way is probably faster than many single queries to the proj command
        Optional variables:
            given_coordinates - if given as tuple or a list of tuples this will limit the algorithm to give only these as sphere_coordinates
        """

        if len(given_coordinates) == 0:
            return [], []

        if isinstance(given_coordinates, tuple):
            given_coordinates = [given_coordinates]

        #new_image_string=""
        if projection_scaling <= global_variables.flat_earth_scaling_start: #for the round world projection

            startup_string = f"+proj=ortho +ellps=sphere +lat_0={-northern_inclination} +lon_0={eastern_inclination}"

            arr = np.array(given_coordinates)

            # Coordinates scale from 0 to projection_scaling
            x = arr[:,0]
            y = arr[:,1]

            x_proj = (x/projection_scaling - 0.5) * 2 * 6370997
            y_proj = (0.5 - y/projection_scaling) * 2 * 6370997


            #running pyproj
            transformer = Transformer.from_pipeline(startup_string)

            xxs, yys = transformer.transform(x_proj,y_proj, direction='INVERSE')


            plane_to_sphere = xxs, yys

        else: #for the flat world projection

            plane_to_sphere_x, plane_to_sphere_y = [], []

            if isinstance(given_coordinates,list) or isinstance(given_coordinates,tuple):
                if isinstance(given_coordinates,tuple):
                    given_coordinates = [given_coordinates]


                window_size = global_variables.window_size
                west_border = self.flat_image_borders["west_border"]
                east_border = self.flat_image_borders["east_border"]
                south_border = self.flat_image_borders["south_border"]
                north_border = self.flat_image_borders["north_border"]
                east_west_span = east_border - west_border
                north_south_span = north_border - south_border

                for proj_position in given_coordinates:
                    x_sphere_position = (float(proj_position[0]) / float(window_size[0]) ) * east_west_span + west_border
                    y_sphere_position = ((float(window_size[1]) - float(proj_position[1])) / window_size[1] ) * north_south_span + south_border
                    plane_to_sphere_x.append((x_sphere_position))
                    plane_to_sphere_y.append((y_sphere_position))

            else:
                raise Exception("Major error in plane_to_sphere_total - the coordinates given does not make sense")

        return plane_to_sphere







    def calculate_resource_map(self,resource_type):
        """
        Function that checks if a resource picture exists in the /images/planet/nonrenewable materials map/"resource_type"
        If not it "calculates" the topography based random parameters
        In all cases the output is that self.resource_maps will contain a resource image of size (90,45)
        where red is lowest and yellow is highest.
        """
        #try to find the proper non-renewable resource map
        try: self.resource_maps[resource_type]
        except:
            resource_file_name_and_path = os.path.join("images","planet","nonrenewable materials map",resource_type,str(self.planet_name + ".png"))
            if os.access(resource_file_name_and_path,os.R_OK):
                resource_map_image = Image.open(resource_file_name_and_path)
                #print "resource file " + str(resource_type) + " does exist for " + str(self.planet_name) + " - all ok"
            else:
                #print "resource file " + str(resource_type) + " does not exist for " + str(self.planet_name) + " - creating a random"

                resource_map_image = Image.new("L",(90,45))
                lut = []

                x_offset = random.random()
                x_skewing = random.random()
                x_band_clearness = random.random()*0.8
                y_offset = random.random()
                y_skewing = random.random()
                y_band_clearness = random.random() * 0.8
                resource_type_in_database = "ground_" + str(resource_type)
                try: self.planet_data[resource_type_in_database]
                except:
                    resource_level = 1
                    print("The resource_level for " + str(resource_type_in_database) + " was not found in planet_database so the background value was set to 1")
                else:
                    resource_level = self.planet_data[resource_type_in_database]
                #print (x_offset,x_skewing,x_band_clearness,y_offset,y_skewing,y_band_clearness)
                if self.planet_type != "gasplanet":
                    for y in range(0,45):
                        for x in range(0,90):
                            pixel = (random.randint(0,255) + math.sin((x / 90.0)* 2 * math.pi + x_offset*90 + y_skewing*(y/7.0))*100 * x_band_clearness + math.sin((y / 90.0)* 2 * math.pi + y_offset*90 + x_skewing*(y/7.0))*100 * y_band_clearness) * resource_level
                            lut.append(pixel)
                else:
                    for y in range(0,45):
                        for x in range(0,90):
                            pixel = 0
                            lut.append(pixel)

                resource_map_image.putdata(lut)

                enhancer = ImageEnhance.Sharpness(resource_map_image)
                resource_map_image = enhancer.enhance(0)

                #making the correct colors
                lut = []
                for i in range(256):
                    lut.extend([255, i, 0])
                resource_map_image.putpalette(lut)

                resource_map_image = resource_map_image.convert("RGB")

                #print "saving calculated map"
                #resource_map_image.save("testingresourcemap.png")

            self.resource_maps[resource_type] = resource_map_image
        else:
            pass
            #The self.resource_maps[resource_type]  does already exist


    def draw_overlay_map(self,eastern_inclination,northern_inclination,projection_scaling,resource_type):
        """
        Function that gives a surface with a given overlay
        The type can be topographical or the name of non-renewable resource used
        It will first check if the map in question already exists, and if not it will generate it
        The topographical needs to be special, because it is calculated from the looks of the actual surface.
        Also this map is size (720,360) because it needs to be somewhat fine-grained for water-rising purposes
        The non-renewable resource is calculated entire at random if it does not exists. It is only a (90,45)
        size map so it shouldn't be too much to have a lot of them in memory.
        The output is a pysurface for use with other plotting mechanisms.
        The resolution of the surface will be automatically decreased as proper for the displaytype (topo/resource)
        """
        #image_string = image.tostring()
        if resource_type == "topographical":
            #retrieve the topographical map.
            self.calculate_topography()
            overlay_image = self.topo_image

        else:
            self.calculate_resource_map(resource_type)
            overlay_image = self.resource_maps[resource_type].copy()

            if self.current_base is not None:
                overlay_image = self.current_base.draw_mining_area(self,overlay_image)

        overlay_image = overlay_image.convert("RGB")
        surface = self.draw_image(eastern_inclination, northern_inclination,projection_scaling,fast_rendering=True,image=overlay_image)

        return surface



    def draw_image(
        self,
        eastern_inclination: float,
        northern_inclination: float,
        projection_scaling: float,
        fast_rendering=False,
        image=None,
    ) -> pygame.Surface:
        """
        Function that gives the actual surface for use with pysurface, of a planet the zoom/rotation parameters.
        Optional arguments
            fast_rendering    boolean, False per default. If set to true the projection scaling will be halved for spherical
                    projections and the surface will be doubled before returning. This gives much faster calculation
                    times

            image   an image can be fed to the function (such as for example a topographical map) and then this
                    will be projected instead. If not the function will use the self.image (fixme delete and self.image_string)

            plane_to_sphere    The output from plane_to_sphere_total() given for special renditions. If not given it will load from the standard
                                calculations (ie. all lat/long's divisible by 30)

        """
        if image != None:
            check_memory = False
        else:
            image = self.image
            check_memory = True

        mode = image.mode
        if mode == "RGBA":
            color_len = 4
        else:
            color_len = 3

        image_array = np.array(image)

        projection_scaling = int(projection_scaling)
        if projection_scaling <= global_variables.flat_earth_scaling_start:
            # When we don't need a very high resolution, we can use the fast rendering
            resize_after_fast_rendering = False
            if fast_rendering and projection_scaling > 45:
                projection_scaling = int(projection_scaling / 2)
                resize_after_fast_rendering = True

            plane_to_sphere = None
            # Here we could implement caching of the mapping

            if plane_to_sphere is None:
                # Caclulate it if it is not given

                coord_x, coord_y = np.meshgrid(range(projection_scaling), range(projection_scaling))

                # Calculate the sphere coordinates
                sphere_x, sphere_y = self.plane_to_sphere_total(
                    eastern_inclination,
                    northern_inclination,
                    projection_scaling,
                    np.c_[coord_x.T.flatten(), coord_y.T.flatten()],
                )

            # Create the output byte image
            output_image = np.zeros((projection_scaling * projection_scaling, color_len), dtype=np.uint8)

            # Calculate what the indices are in the image given
            mask_valid = np.isfinite(sphere_x) & np.isfinite(sphere_y)
            x_image = ((sphere_x[mask_valid] + 180) / 360 * image.size[0]).round(0).astype(int).clip(0, image.size[0] - 1)
            y_image = ((sphere_y[mask_valid] + 90) / 180 * image.size[1]).round(0).astype(int).clip(0, image.size[1] - 1)



            # Copy the values from the image to the output image
            output_image[mask_valid, :] = image_array[y_image, x_image, :]

            surface = pygame.image.frombuffer(output_image.flatten(), (projection_scaling, projection_scaling), mode)
            surface = pygame.transform.rotate(surface,90)


            if resize_after_fast_rendering:
                surface = pygame.transform.scale2x(surface)
                projection_scaling = projection_scaling * 2

            self.projection_dim =(projection_scaling,projection_scaling)
            if check_memory:
                self.pre_drawn_surfaces[(northern_inclination,eastern_inclination,projection_scaling)] = surface

        else: #ie for the flat planet projection

            if northern_inclination == 90:
                self.northern_inclination = 60
                northern_inclination = 60
            if northern_inclination == -90:
                self.northern_inclination = -60
                northern_inclination = -60

            if image.size != self.image.size: #comparing the topographic/resource map with the real-light surface map
                image = image.resize(self.image.size)

            window_size = global_variables.window_size
            image = ImageChops.offset(image,int((-eastern_inclination/ 360.0 ) * image.size[0]),0)


            #borders given in pixel_number from the left-upper corner of image (as it looks after the offset)
            west_border =  (image.size[0] / 2) - (window_size[0] / 2)
            east_border =  (image.size[0] / 2) + (window_size[0] / 2)

            max_north_center = window_size[1] / 2
            max_south_center = image.size[1] - (window_size[1] / 2)
            north_south_span = max_south_center - max_north_center
            north_border = int(max_north_center + (((northern_inclination - 60.0) / - 30.0 ))* (north_south_span / 4.0)  - (window_size[1] / 2.0))
            south_border = int(max_north_center + (((northern_inclination - 60.0) / - 30.0 ))* (north_south_span / 4.0)  + (window_size[1] / 2.0))


            #calculating the borders of the picture, for use with other interfaces
            east_west_span = east_border - west_border
            east_west_span_degrees = (east_west_span / float(image.size[0])) * 360.0
            self.flat_image_borders = {}
            self.flat_image_borders["west_border"] = int(eastern_inclination - east_west_span_degrees / 2)
            self.flat_image_borders["east_border"] = int(eastern_inclination + east_west_span_degrees /2)
            self.flat_image_borders["north_border"] = int(((north_border / float(image.size[1])) - 0.5) * - 180)
            self.flat_image_borders["south_border"] = int(((south_border / float(image.size[1])) - 0.5) * - 180)
            image = image.crop((west_border,north_border,east_border,south_border))
            image_bmp = image.convert(mode).tobytes()
            surface = pygame.image.frombuffer(image_bmp , (window_size[0],window_size[1]), mode)
            self.projection_dim =(window_size[0],window_size[1])

        return surface


    def draw_entire_planet(self,eastern_inclination,northern_inclination,projection_scaling,fast_rendering=True):
        """
        Function that gives the actual surface for use with pysurface, of a planet, when given the flat
        image-string, and the zoom/rotation parameters.
        It first checks if the planet object already contains a drawn surface, and if so it uses that.
        Otherwise the surface is saved here for next time use.
        """

        blackscreen = pygame.Surface(global_variables.window_size)
        self.projection_dim =(projection_scaling,projection_scaling)
        if self.planet_display_mode == "visible light":
            surface = self.draw_image(eastern_inclination,northern_inclination,projection_scaling,fast_rendering).copy()

        elif self.planet_display_mode == "trade network":
            surface = self.draw_image(eastern_inclination,northern_inclination,projection_scaling,fast_rendering).copy()
            self.draw_trade_network(surface, eastern_inclination, northern_inclination, projection_scaling)
        else:
            surface = self.draw_overlay_map(eastern_inclination,northern_inclination,projection_scaling,self.planet_display_mode)


        if self.planet_display_mode in ["visible light","trade network"]:
            try:    self.action_layer
            except: pass
            else:
                if (northern_inclination,eastern_inclination,projection_scaling) in self.pre_drawn_action_layers:
                    rgba_action_surface = self.pre_drawn_action_layers[(northern_inclination,eastern_inclination,projection_scaling)]
                    surface.blit(rgba_action_surface,(0,0))
                else:
                    rgba_action = self.convert_to_rgba(self.action_layer)
                    rgba_action_surface = self.draw_image(eastern_inclination, northern_inclination, projection_scaling, fast_rendering = True, image = rgba_action)
                    surface.blit(rgba_action_surface,(0,0))
                    self.pre_drawn_action_layers[(northern_inclination,eastern_inclination,projection_scaling)] = rgba_action_surface



        surface = self.draw_bases(surface,eastern_inclination,northern_inclination,projection_scaling)

        #if self.planet_name == "mars":


        blackscreen.blit(surface, ((global_variables.window_size[0]-self.projection_dim[0])/2 ,(global_variables.window_size[1]-self.projection_dim[1])/2))
        surface = blackscreen
        surface = self.draw_space_stations(surface,eastern_inclination,northern_inclination,projection_scaling)

        if self.planet_display_mode not in ["visible light","trade network"]:
            try: self.heat_bar
            except:
                self.heat_bar = pygame.image.load(os.path.join("images","heat_bar.png"))
            else:
                surface.blit(self.heat_bar,(0,global_variables.window_size[1]-320))

        return surface













    def calculate_base_positions(
        self,
        eastern_inclination: float,
        northern_inclination: float,
        projection_scaling: float,
    ):
        """
        checks if base positions have been stored already and loads them if they have
        if not, they are calculated.
        Returns a dictionary with base names as key, and the position or ["Not seen",edge_position] as values.
        """

        # Name which is kept in cache
        memory_tuple = (northern_inclination,eastern_inclination,projection_scaling)

        if memory_tuple in self.base_positions:
            # Check that the bases are all there
            if all(base in self.base_positions[memory_tuple] for base in self.bases):
                return self.base_positions[memory_tuple]

        base_positions_here = {}
        areas_of_interest_here = {}

        window_x, window_y = global_variables.window_size

        if projection_scaling <= global_variables.flat_earth_scaling_start:
            #for the round world projection
            sphere_coordinates = []
            reverse_sphere_coordinates = []
            base_names = []
            for base in self.bases:
                if self.bases[base].terrain_type == "Space": #for space stations
                    base_positions_here[base] = ["Space",None]
                else:
                    sphere_position = (self.bases[base].position_coordinate[0],self.bases[base].position_coordinate[1])
                    sphere_coordinates.append(sphere_position)

                    if sphere_position[0] < 0:
                        reverse_sphere_position = (sphere_position[0]+180,-sphere_position[1])
                    else:
                        reverse_sphere_position = (sphere_position[0]-180,-sphere_position[1])
                    reverse_sphere_coordinates.append(reverse_sphere_position)
                    base_names.append(base)

            plane_x, plane_y = self.sphere_to_plane_total(sphere_coordinates, eastern_inclination, northern_inclination, projection_scaling)
            reverse_plane_x, reverse_plane_y = self.sphere_to_plane_total(reverse_sphere_coordinates, eastern_inclination, northern_inclination, projection_scaling)

            for i in range(len(base_names)):
                x, y = plane_x[i], plane_y[i]
                if np.isfinite(x) and np.isfinite(y):
                    base_positions_here[base_names[i]] = (int(x),int(y))
                    absolute_position = (x + (window_x/2) - (projection_scaling/2), y + (window_y /2) - (projection_scaling/2))
                    areas_of_interest_here[(absolute_position[0]-1,absolute_position[1]-1,2,2)] = base_names[i]
                else:
                    #calculation the edge position for a base below the edge (for use in trade_network drawing)
                    reverse_x =  - ( int(reverse_plane_x[i]) - 0.5 * projection_scaling )
                    reverse_y =  int(reverse_plane_y[i]) - 0.5 * projection_scaling
                    angle = math.atan2(reverse_y,reverse_x)
                    edge_position = (0.5*projection_scaling * ( 1 + math.cos(angle) ), projection_scaling - 0.5 * projection_scaling *( 1 + math.sin(angle)))
                    #print str(base_names[i]) + " has an angle of: " + str(angle) + " / " + str(180*angle/math.pi) + ", a reverse_plane_position of " + str((reverse_x,reverse_y)) + " and an edge_position of " + str(edge_position)
                    base_positions_here[base_names[i]] = ["Not seen", edge_position]

        else: #if zoomed all the way in to the flat world
            window_size = global_variables.window_size
            west_border = self.flat_image_borders["west_border"]
            east_border = self.flat_image_borders["east_border"]
            south_border = self.flat_image_borders["south_border"]
            north_border = self.flat_image_borders["north_border"]
            east_west_span = east_border - west_border
            north_south_span = north_border - south_border
            for base in self.bases:
                if self.bases[base].terrain_type != "Space":
                    sphere_position = (self.bases[base].position_coordinate[0],self.bases[base].position_coordinate[1])
                    if (west_border < sphere_position[0] < east_border) and (south_border < sphere_position[1] < north_border):
                        x_proj_position = (( sphere_position[0] - west_border ) / east_west_span ) * window_x
                        y_proj_position = window_y - ((( sphere_position[1] - south_border ) / north_south_span ) * window_y)
                        base_positions_here[base] = (int(x_proj_position),int(y_proj_position))
                        areas_of_interest_here[(x_proj_position,y_proj_position,2,2)] = base
                    else:
                        #calculation the edge position for a base over the edge (for use in trade_network drawing)
                        x_proj_position = (( sphere_position[0] - west_border ) / east_west_span ) * window_x
                        y_proj_position = window_y - ((( sphere_position[1] - south_border ) / north_south_span ) * window_y)
                        #print str(base_names[i]) + " has an angle of: " + str(angle) + " / " + str(180*angle/math.pi) + ", a reverse_plane_position of " + str((reverse_x,reverse_y)) + " and an edge_position of " + str(edge_position)


                        base_positions_here[base] = ["Not seen",(int(x_proj_position),int(y_proj_position))]


        # Save the calculated positions to the memory
        self.base_positions[memory_tuple] = base_positions_here
        self.areas_of_interest[memory_tuple] = areas_of_interest_here

        return base_positions_here


    def kill_a_base(self,base_name):
        try: self.bases[base_name]
        except:
            print("the base " + str(base_name) + " is already removed")
        else:
            if self.current_base is not None:
                if self.current_base.name == base_name:
                    self.current_base = None

            dying_base = self.bases[base_name]

            for trade_route in dying_base.trade_routes:
                trade_route_instance = dying_base.trade_routes[trade_route]
                for endpoint_base in trade_route_instance["endpoint_links"]:
                    if endpoint_base != dying_base:
                        break
                del endpoint_base.trade_routes[dying_base.name]
#                print "deleted trade route entry to " + dying_base.name + " from " + endpoint_base.name


            firms_to_delete = {}
            for company_instance in list(self.solar_system_object_link.companies.values()):
                for firm_name in company_instance.owned_firms:
                    firm_instance = company_instance.owned_firms[firm_name]
                    if not isinstance(firm_instance, company.merchant):
                        if firm_instance.location == self.solar_system_object_link.current_planet.current_base:
#                            print "deleting " + firm_instance.name + " owned by " + company_instance.name + " in " + str(dying_base.name)
                            firm_instance.close_firm()
                            firms_to_delete[firm_name] = company_instance

                    else:
                        if firm_instance.from_location == self.solar_system_object_link.current_planet.current_base or firm_instance.to_location == self.solar_system_object_link.current_planet.current_base:
#                            print "deleting " + firm_instance.name + " merchant owned by " + company_instance.name + " in " + str(dying_base.name)
                            firm_instance.close_firm()
                            firms_to_delete[firm_name] = company_instance

                if dying_base.name in list(company_instance.home_cities.keys()):
                    del company_instance.home_cities[dying_base.name]
#                    print "deleted " + dying_base.name + " from " + company_instance.name + "'s list of home_cities"

            for firm_to_delete in firms_to_delete:
                del firms_to_delete[firm_to_delete].owned_firms[firm_to_delete]

            try:    dying_base.owner.owned_firms[base_name]
            except: print("Didn't find " + base_name + " in owned firms of " + str(dying_base.owner.name))
            else:
                del dying_base.owner.owned_firms[base_name]
#                print "Found and deleted " + base_name + " in owned firms of " + str(dying_base.owner.name)

            try:    self.bases[base_name]
            except: print("Didn't find " + base_name + " in bases of " + str(self.name))
            else:
                del self.bases[base_name]
#                print "Found and deleted " + base_name + " in bases of " + str(self.name)





    def check_base_position(self,projection_position):
        """
        Function that takes a projection_position from a click on the map, checks if it is not on water, in space, or
        too close to another base, means within 100 km
        and returns the sphere_coordinates
        """
        click_spot = pygame.Rect(projection_position[0]-3,projection_position[1]-3,6,6)
        collision_test_result = click_spot.collidedict(self.areas_of_interest[(self.northern_inclination,self.eastern_inclination,self.projection_scaling)])
        if collision_test_result != None:

            return "transfer population to " + collision_test_result[1]


        if self.projection_scaling <= global_variables.flat_earth_scaling_start: #for the round world projection
            transposed_projection_position = (projection_position[0] - global_variables.window_size[0]/2 + self.projection_scaling/2, projection_position[1] - global_variables.window_size[1]/2 + self.projection_scaling/2)
            sphere_coordinates = self.plane_to_sphere_total(
                self.eastern_inclination,
                self.northern_inclination,
                self.projection_scaling,
                transposed_projection_position
            )
            logger.debug(f"Sphere coordinates: {sphere_coordinates}")

        else: #planar map projection
            window_size = global_variables.window_size
            west_border = self.flat_image_borders["west_border"]
            east_border = self.flat_image_borders["east_border"]
            south_border = self.flat_image_borders["south_border"]
            north_border = self.flat_image_borders["north_border"]
            east_west_span = east_border - west_border
            north_south_span = north_border - south_border

            x_sphere_position = west_border + (float(projection_position[0]) / window_size[0]) * east_west_span
            y_sphere_position = -((((float(projection_position[1]) - window_size[1] ) /  window_size[1]) * north_south_span ) - south_border )

            if x_sphere_position > 180:
                x_sphere_position = x_sphere_position - 360
            if x_sphere_position < -180:
                x_sphere_position = x_sphere_position + 360
            sphere_coordinates = (x_sphere_position,y_sphere_position)

        if isinstance(sphere_coordinates,tuple):
                #first check if it is within the range of other bases (first take ones within the 3 degree square of the globe, then calculate round distance
                square_size_degrees = int(math.ceil(10 * (12756 / self.planet_diameter_km ))) #this is first used, to quickly sort away bases far away - the real check is truly circular. It is normalized to earth radius.
#                print "self.planet_diameter_km " + str(self.planet_diameter_km)
                radius_size = 100 #this is the circular radius within wich the bases are disqualified for being to near
                not_too_close = True
                for base_instance in list(self.bases.values()):
                    if base_instance.terrain_type != "Space":
                        if abs(base_instance.position_coordinate[0] - sphere_coordinates[0]) < square_size_degrees and abs(base_instance.position_coordinate[1] - sphere_coordinates[1]) < square_size_degrees:
                            distance = self.calculate_distance(base_instance.position_coordinate, sphere_coordinates)
                            if distance[0] < radius_size:
                                print_dict = {"text":"The new position is less than " + str(radius_size) + " km to " + base_instance.name + " it is " + str(distance[0]),"type":"general gameplay info"}
                                self.solar_system_object_link.messages.append(print_dict)
                                not_too_close = False


                if not_too_close:
                    try: self.action_layer
                    except:
                        self.change_water_level(self.water_level)
                    position_x_pixel = int(((sphere_coordinates[0] + 180.0 ) / 360.0) * self.action_layer.size[0])
                    position_y_pixel = int(self.action_layer.size[1] - ((sphere_coordinates[1] + 90.0 ) / 180.0) * self.action_layer.size[1])
                    pixel_color = self.action_layer.getpixel((position_x_pixel,position_y_pixel))
#                    print "pixel_color " + str(pixel_color)
                    if pixel_color == 255:
                        return sphere_coordinates
                    else:
                        print_dict = {"text":"Can't build a base here","type":"general gameplay info"}
                        self.solar_system_object_link.messages.append(print_dict)
                        return "Can't build a base in this terrain"

                else:
                    return "Too close to another base"
        else:
            return "space base"



    def draw_bases(self,surface,eastern_inclination,northern_inclination,projection_scaling):
        """
        Function that decorates the globe as made by draw_image, with bases. Takes a surface gives a surface
        """
        outer_circle_radius = projection_scaling/90
        if outer_circle_radius < 2:
            outer_circle_radius = 2
        inner_circle_radius = outer_circle_radius / 2

        base_positions = self.calculate_base_positions(eastern_inclination, northern_inclination, projection_scaling)
        for base in self.bases:
            if base_positions[base][0] in ["Space", "Not seen"]:
                continue
            if self.bases[base].is_on_dry_land == "almost":
                pygame.draw.circle(surface,(255,36,0),base_positions[base],outer_circle_radius)
                pygame.draw.circle(surface,(0,0,0),base_positions[base],inner_circle_radius)
            elif self.bases[base].is_on_dry_land == "no":
                pass
            else:
                pygame.draw.circle(surface,(255,255,255),base_positions[base],outer_circle_radius)
                pygame.draw.circle(surface,(0,0,0),base_positions[base],inner_circle_radius)

            if self.current_base is not None:
                if self.current_base.name == base:
                    pygame.draw.circle(surface,(255,255,255),base_positions[base],inner_circle_radius)
                #pygame.draw.circle(surface,(0,0,0),base_positions[base],int(outer_circle_radius*1.5),1)

        return surface



    def draw_trade_network(self,surface,eastern_inclination,northern_inclination,projection_scaling):
        """
        Function that decorates the globe as made by draw_image, with trade network. Takes a surface gives a surface
        """
        base_positions = self.calculate_base_positions(eastern_inclination, northern_inclination, projection_scaling)
        for base in self.bases:
            if base_positions[base][0] in ["Space", "Not seen"]:
                continue
            for other_base in self.bases[base].trade_routes:
                if other_base in list(base_positions.keys()):
                    if base_positions[other_base][0] == "Not seen":
                        pygame.draw.line(surface,(155,155,155),base_positions[base],base_positions[other_base][1])
                    elif base_positions[other_base][0] == "Space":
                        pass
                    else:
                        pygame.draw.line(surface,(155,155,155),base_positions[base],base_positions[other_base])

        return surface


    def draw_space_stations(self,surface,eastern_inclination,northern_inclination,projection_scaling):
        """
        Function that decorates the globe as made by draw_image, with satellites. Takes a surface gives a surface.

        """
        if projection_scaling <= 180:
            km_per_pixels = float(self.planet_diameter_km) / float(projection_scaling)
            transposition = (global_variables.window_size[0]/2,global_variables.window_size[1]/2)
            relative_semi_major_axis = (self.planet_diameter_km ) / km_per_pixels #space stations are found on planet diameter from center of planet (ie, on planet-radius of height)
            eccentricity = abs(abs(northern_inclination)/2 - 89.5) / 90

            relative_semi_minor_axis = ((relative_semi_major_axis ** 2) * (1 - (eccentricity **2) )) ** 0.5
            orbit = []

            for i in range(0,101):
                t = -math.pi + i * ((2 * math.pi) / 100 )
                x = relative_semi_major_axis * math.cos(t)
                y = relative_semi_minor_axis * math.sin(t)

                #transpose
                x = x + transposition[0]
                y = y + transposition[1]

                orbit.append((x,y))

            space_station_number = 0 # for assigning more or less permannent position
            for space_station_name in self.bases:
                if self.bases[space_station_name].terrain_type == "Space":
                    space_station = self.bases[space_station_name]


                    #Draw the space station itself
                    orbit_position_index = space_station_number * 77 + int(100 * eastern_inclination / 360.0)
                    space_station_number = space_station_number + 1
                    if northern_inclination < 0:
                        orbit_position_index = - orbit_position_index
                    orbit_position_index = orbit_position_index % 100


                    if not 17 < orbit_position_index < 33 or northern_inclination != 0:
                        space_station_position = orbit[orbit_position_index]
                        space_station_position = (int(space_station_position[0]), int(space_station_position[1]))
                        outer_circle_radius = 4
                        inner_circle_radius = outer_circle_radius / 2
                        pygame.draw.circle(surface,(255,255,255),space_station_position,outer_circle_radius)
                        if not space_station == self.current_base:
                            pygame.draw.circle(surface,(0,0,0),space_station_position,inner_circle_radius)
                        if projection_scaling == 90:
                            space_station_label = global_variables.standard_font.render(space_station.name,True,(255,255,255))
                            surface.blit(space_station_label,space_station_position)
                        if projection_scaling == 45:
                            space_station_label = global_variables.standard_font_small.render(space_station.name,True,(255,255,255))
                            surface.blit(space_station_label,space_station_position)

                        viewpoint = (northern_inclination,eastern_inclination,projection_scaling)
                        self.areas_of_interest[viewpoint][(space_station_position[0]-1, space_station_position[1], 2, 2)] = space_station.name

                if space_station_number > 0:
                    if northern_inclination == 0:
                        pygame.draw.lines(surface, (60,60,60), False, orbit[0:17])
                        pygame.draw.lines(surface, (60,60,60), False, orbit[33:100])
                    else:
                        pygame.draw.lines(surface, (60,60,60), False, orbit)



        return surface


    def explode(self,per_hit_intensity,number_of_hits,bases_involved,mainscreen):
        """
        Function that animates explosions, decimates bases hit by the explosions and renderes the land
        ravaged.

        Accepts the following:

        per_hit_intensity     an integer between 1 and 100. 100 is large enough to wipe out an earth size planet entirely.
        number_of_hits        an integer between 1 and 100. The number of hits.
        bases_involved        a {base_name:base} dictionary of the bases that are involved. If None the strikes are randomly assigned

        Returns a tally of total losses as a dict
        """

        hit_locations = []

        blast_surface = pygame.image.load(os.path.join("images","blast.png"))
        ratio = 0.25 *(float(per_hit_intensity) / 100.0) * (float(self.projection_scaling) / 360.0) * (self.solar_system_object_link.planets["earth"].planet_diameter_km / float(self.planet_diameter_km))
#        print "ratio " + str(ratio)
        large_blast_surface = pygame.transform.scale(blast_surface, (int(blast_surface.get_width() * ratio / 2), int(blast_surface.get_height() * ratio / 2)))
        medium_blast_surface = pygame.transform.scale(blast_surface, (int(blast_surface.get_width() * ratio / 3), int(blast_surface.get_height() * ratio / 3)))
        small_blast_surface = pygame.transform.scale(blast_surface, (int(blast_surface.get_width() * ratio / 4), int(blast_surface.get_height() * ratio / 4)))
        if bases_involved is None:
            for i in range(number_of_hits):
                latitude = (random.random() - 0.5) * 180
                longitude = (random.random() - 0.5) * 360
                hit_locations.append((longitude,latitude))
        else:
            base_positions = []

            for base_instance in list(bases_involved.values()):
                base_pos = base_instance.position_coordinate
                base_positions.append(base_pos)
                try:    edges
                except: edges = [base_pos[0],base_pos[1],base_pos[0],base_pos[1]] #ie. left, bottom, right, top edge in spherical coordiantes
                else:
                    edges[0] = min(base_pos[0], edges[0])
                    edges[1] = min(base_pos[1], edges[1])
                    edges[2] = max(base_pos[0], edges[0])
                    edges[3] = max(base_pos[1], edges[1])

            long_span = max(edges[2] - edges[0],2)
            lat_span = max(edges[3] - edges[1], 2) / 2


            for i in range(number_of_hits):
                aimed_position = random.choice(base_positions)
                longitude = random.gauss(aimed_position[0],long_span)
                latitude = random.gauss(aimed_position[1],lat_span)
                hit_locations.append((longitude,latitude))

        hit_x, hit_y = self.sphere_to_plane_total(hit_locations,self.eastern_inclination,self.northern_inclination,self.projection_scaling)

        if self.projection_scaling <= global_variables.flat_earth_scaling_start:
            # for the round world projection
            hit_x += global_variables.window_size[0] / 2 - self.projection_scaling / 2
            hit_y += global_variables.window_size[1] / 2 - self.projection_scaling / 2


        surface = mainscreen.copy()

        background = mainscreen.copy()
#        print "background.get_size(): " + str(background.get_size())


        if per_hit_intensity > 50:
            #this is earth shattering: a meteor or some ultrahightech super bomb that has yet to be discovered
            #onle one animation at a time for these

            half_w_small = small_blast_surface.get_width() / 2
            half_h_small = small_blast_surface.get_height() / 2

            for x, y in zip(hit_x, hit_y):
                proj_hit_location_transposed = (int(x - half_w_small), int(y - half_h_small))
                surface.blit(small_blast_surface,proj_hit_location_transposed)
                mainscreen.blit(surface.copy(),(1,0))
                pygame.display.flip()
#                mainscreen.blit(surface)
#                renderer.update()
                pygame.time.delay(33)
                mainscreen.blit(surface.copy(),(-2,0))
                pygame.display.flip()
#                mainscreen.set_picture(surface)
#                renderer.update()
                pygame.time.delay(33)
                mainscreen.blit(surface.copy(),(1,0))
                pygame.display.flip()
#                mainscreen.set_picture(surface)
#                renderer.update()
                pygame.time.delay(33)
                proj_hit_location_transposed = (int(x - medium_blast_surface.get_width()/2), int(y - medium_blast_surface.get_height()/2))
                mainscreen.blit(medium_blast_surface,proj_hit_location_transposed)
                pygame.display.flip()
#                mainscreen.set_picture(surface)
#                renderer.update()
                pygame.time.delay(100)
                proj_hit_location_transposed = (int(x - large_blast_surface.get_width()/2), int(y - large_blast_surface.get_height()/2))
                mainscreen.blit(large_blast_surface,proj_hit_location_transposed)
                pygame.display.flip()
#                mainscreen.set_picture(surface)
#                renderer.update()
                pygame.time.delay(100)
                surface = background.copy()
                mainscreen.blit(surface,(0,0))
                pygame.display.flip()
#                renderer.update()






        else:
            print("puff")


#
#        surface = self.draw_entire_planet(self.eastern_inclination,self.northern_inclination,self.projection_scaling)
#
#
#        delay_time = 300 / len(sphere_hit_locations)
#
#        for i, sphere_hit_location in enumerate(sphere_hit_locations):
#            if isinstance(sphere_hit_location, tuple):
#                size_of_blast = random.choice(["small","medium","large"])
#                if size_of_blast == "small":
#                    sphere_hit_location_transposed = (int(sphere_hit_location[0] - small_blast_surface.get_width()/2), int(sphere_hit_location[1] - small_blast_surface.get_height()/2))
#                    surface.blit(small_blast_surface,sphere_hit_location_transposed)
#                elif size_of_blast == "medium":
#                    sphere_hit_location_transposed = (int(sphere_hit_location[0] - medium_blast_surface.get_width()/2), int(sphere_hit_location[1] - medium_blast_surface.get_height()/2))
#                    surface.blit(medium_blast_surface,sphere_hit_location_transposed)
#                elif size_of_blast == "large":
#                    sphere_hit_location_transposed = (int(sphere_hit_location[0] - large_blast_surface.get_width()/2), int(sphere_hit_location[1] - large_blast_surface.get_height()/2))
#                    surface.blit(large_blast_surface,sphere_hit_location_transposed)
#                else:
#                    raise Exception("Weird")
#
#                mainscreen.set_picture(surface)
#                renderer.update()
#                pygame.time.delay(delay_time)
#
#
