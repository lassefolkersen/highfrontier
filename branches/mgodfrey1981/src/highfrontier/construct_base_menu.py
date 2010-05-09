import merchant
import os
import global_variables
import sys
import string
import pygame
import datetime
import math
import company
import primitives
import gui_components
import random
import time

class construct_base_menu():
    """
    The functions in which new bases can be build
    """
    def __init__(self,solar_system_object,action_surface):
        self.solar_system_object_link = solar_system_object
        self.rect = pygame.Rect(150,150,300,400)
        self.action_surface = action_surface
        self.text_receiver = None




    def receive_click(self,event):
        if self.ok_button.rect.collidepoint(event.pos) == 1:
            return self.ok_button.activate(None)
        if self.cancel_button.rect.collidepoint(event.pos) == 1:
            return self.cancel_button.activate(None)
        if self.population_bar.rect.collidepoint(event.pos) == 1:
            self.population_bar.activate(event.pos)



    def exit(self, label, function_parameter):
        return "clear"
        
            
    def new_base_ask_for_name(self,sphere_coordinates, give_length_warning = False):
        """
        Function that prompts the user for a name of the new base
        Optional argument give_length_warning includes a label that specifies max " + str(global_variables.max_letters_in_company_names) + " characters
        """
        
        #first we calculate the distance
        building_base = self.solar_system_object_link.building_base
        
        if self.solar_system_object_link.current_player != building_base.owner:
            print_dict = {"text":"Could not transfer population from " + str(building_base.name) + " because it is not owned by you.","type":"general gameplay info"}
            self.solar_system_object_link.messages.append(print_dict)
            pygame.mouse.set_cursor(*pygame.cursors.arrow)
            return
        
        if sphere_coordinates[0:19] == "transfer population":
            if sphere_coordinates[23:] in self.solar_system_object_link.current_planet.bases.keys():
                destination_base = self.solar_system_object_link.current_planet.bases[sphere_coordinates[23:]]
                sphere_coordinates = destination_base.position_coordinate
                if self.solar_system_object_link.current_player != destination_base.owner:
                    print_dict = {"text":"Could not transfer population to " + str(destination_base.name) + " because it is not owned by you.","type":"general gameplay info"}
                    self.solar_system_object_link.messages.append(print_dict)
                    self.solar_system_object_link.build_base_mode = True 
                    pygame.mouse.set_cursor(*pygame.cursors.diamond)
                    return

            else:
                raise Exception("The destination base " + str(sphere_coordinates[23:]) + "was not found in base dict of " + str(self.solar_system_object_link.current_planet.name))
        else:
            destination_base = None

        if sphere_coordinates == (None, None): #
            sphere_coordinates = "space base"
            
        gravitational_constant = 40
        if building_base.home_planet == self.solar_system_object_link.current_planet: #intraplanetary 
            if building_base.terrain_type != "Space" and sphere_coordinates != "space base": #ground based
                transport_type = "ground transport"
                distance = int(building_base.home_planet.calculate_distance(sphere_coordinates, building_base.position_coordinate)[0]) / 100 
            else: #space based intraplanetary
                if building_base.terrain_type != "Space" and sphere_coordinates == "space base": #ground to space building - mostly depends on escape velocity
                    transport_type = "space transport"
                    distance = (self.solar_system_object_link.current_planet.gravity_at_surface * gravitational_constant) ** 2
                else: #space-to-ground or space-to-space (cheap)
                    transport_type = "space transport"
                    distance = 10.0
        else: #inter-planetary -- one fixed part and one part ground escape velocity
            transport_type = "space transport"
            distance = 100.0

            #adding an extra for travels between far-away planets
            endpoint_distances = []
            for endpoint in [building_base.home_planet, self.solar_system_object_link.current_planet]: 
                while endpoint.planet_data["satellite_of"] != "sun":
                    endpoint = self.solar_system_object_link.planets[endpoint.planet_data["satellite_of"]]
                endpoint_distances.append(endpoint.planet_data["semi_major_axis"])
            distance = distance + int(abs(endpoint_distances[0] - endpoint_distances[1]) ** 0.5) / 50

            if building_base.terrain_type != "Space":
                distance = distance + int((building_base.home_planet.gravity_at_surface*gravitational_constant) ** 2)
                distance = distance * 2 #because it is generally more difficult to have to launch from surface of planet

#        print "distance is " + str(distance) + " using " + transport_type
        self.pricing = {
                        "steel_cost_per_person" : 0.51 + distance / 100,
                        "power_cost_per_person" : 0.5 + distance / 100,
                        "transport_cost_per_person" : distance,
                        "electronics_cost_per_person" : 0.01 + distance / 2000,
                        "transport_type":transport_type,
                        "distance":distance
        }
        
        pygame.draw.rect(self.action_surface, (212,212,212), self.rect)
        pygame.draw.rect(self.action_surface, (0,0,0), self.rect, 2)
        pygame.draw.line(self.action_surface, (255,255,255), (self.rect[0], self.rect[1]), (self.rect[0] + self.rect[2], self.rect[1]))
        pygame.draw.line(self.action_surface, (255,255,255), (self.rect[0], self.rect[1]), (self.rect[0], self.rect[1] + self.rect[3]))

        
        if destination_base is not None:
            location_description = "Transfering population to " + destination_base.name
        else:
            if sphere_coordinates == "space base":
                location_description = "Building a base in orbit around " + self.solar_system_object_link.current_planet.name
            else:
                location_description = "Building a base at (" + str(round(sphere_coordinates[0]))+ "," + str(round(sphere_coordinates[1])) + ") on "+ self.solar_system_object_link.current_planet.name
        
        description = global_variables.standard_font.render(location_description,True,(0,0,0))
        self.action_surface.blit(description, (self.rect[0] + 20, self.rect[1]  + 20))
        
        
        if destination_base is None:
            description = global_variables.standard_font.render("Enter name",True,(0,0,0))
            self.action_surface.blit(description, (self.rect[0] + 20, self.rect[1]  + 40))
            
            if give_length_warning:
                warning = global_variables.standard_font.render("Name must be unique",True,(0,0,0))
                self.action_surface.blit(warning, (self.rect[0] + 20, self.rect[1] + 50))
                
                
            self.text_receiver = gui_components.entry(self.action_surface, 
                                 topleft = (self.rect[0] + self.rect[2]/2 - 100, self.rect[1] + 70), 
                                 width = 200, 
                                 max_letters = global_variables.max_letters_in_company_names)
            self.text_receiver.active = True
        else:
            assert self.text_receiver == None

        description = global_variables.standard_font.render("Population to transfer:",True,(0,0,0))
        self.action_surface.blit(description, (self.rect[0] + 20, self.rect[1]  + 120))
        
        
        price_rect = pygame.Rect(self.rect[0] + 10, self.rect[1] + 210, self.rect[2] - 20, 80)

        def population_execute(label,price_rect):
            pygame.draw.rect(self.action_surface,(212,212,212),price_rect)
            
            text = primitives.nicefy_numbers(int(self.population_bar.position)) + " people" 
            rendered_text = global_variables.standard_font.render(text,True,(0,0,0))
            self.action_surface.blit(rendered_text, (price_rect[0], price_rect[1]))
            
            text = primitives.nicefy_numbers(int(self.population_bar.position * self.pricing["steel_cost_per_person"])) + " steel" 
            rendered_text = global_variables.standard_font.render(text,True,(0,0,0))
            self.action_surface.blit(rendered_text, (price_rect[0], price_rect[1] + 15))
            
            text = primitives.nicefy_numbers(int(self.population_bar.position * self.pricing ["power_cost_per_person"])) + " power" 
            rendered_text = global_variables.standard_font.render(text,True,(0,0,0))
            self.action_surface.blit(rendered_text, (price_rect[0], price_rect[1] + 30))
            
            text = primitives.nicefy_numbers(int(self.population_bar.position * self.pricing["transport_cost_per_person"])) + " " + transport_type 
            rendered_text = global_variables.standard_font.render(text,True,(0,0,0))
            self.action_surface.blit(rendered_text, (price_rect[0], price_rect[1] + 45))
            
            text = primitives.nicefy_numbers(int(self.population_bar.position * self.pricing ["electronics_cost_per_person"])) + " electronics" 
            rendered_text = global_variables.standard_font.render(text,True,(0,0,0))
            self.action_surface.blit(rendered_text, (price_rect[0], price_rect[1] + 60))

            pygame.display.update(price_rect)



        max_size = min(10000,building_base.population)
        min_size = min(max_size/2, 100)
        self.population_bar = gui_components.hscrollbar(
                                                        self.action_surface,
                                                        population_execute, 
                                                        (self.rect[0] + 10, self.rect[1] + 140), 
                                                        self.rect[2]-20, 
                                                        (min_size,max_size), 
                                                        start_position = 100,
                                                        function_parameter=price_rect)
        
        description = global_variables.standard_font.render("Price of transfer:",True,(0,0,0))
        self.action_surface.blit(description, (self.rect[0] + 20, self.rect[1]  + 170))
        description = global_variables.standard_font.render("Calculated on a cost-distance of " + str(int(distance)),True,(0,0,0))
        self.action_surface.blit(description, (self.rect[0] + 20, self.rect[1]  + 185))

        
        population_execute(None,price_rect)

        if destination_base is None:
            self.ok_button = gui_components.button("ok", 
                                                    self.action_surface,
                                                    self.new_base_build, 
                                                    function_parameter = sphere_coordinates, 
                                                    fixed_size = (100,35), 
                                                    topleft = (self.rect[0] + self.rect[2] - 110, self.rect[1] + self.rect[3] - 40))
        else:
            self.ok_button = gui_components.button("ok", 
                                                    self.action_surface,
                                                    self.new_base_build, 
                                                    function_parameter = destination_base, 
                                                    fixed_size = (100,35), 
                                                    topleft = (self.rect[0] + self.rect[2] - 110, self.rect[1] + self.rect[3] - 40))

        
        self.cancel_button = gui_components.button("cancel", 
                                                self.action_surface,
                                                self.exit, function_parameter = None, 
                                                fixed_size = (100,35), 
                                                topleft = (self.rect[0] + self.rect[2] - 220, self.rect[1] + self.rect[3] - 40))

    def new_base_build(self,label,function_parameter):
        
        if self.text_receiver is not None:
            destination_base = None
            name = self.text_receiver.text
            construction_name = name + " construction"
            sphere_coordinates = function_parameter
            if sphere_coordinates == "space base":
                location_description = " in space"
            else:
                location_description = " at (" + str(round(sphere_coordinates[0]))+ "," + str(round(sphere_coordinates[1])) + ")"

        else:
            destination_base = function_parameter
            name = destination_base.name
            construction_name = name + " transfer"
            sphere_coordinates = destination_base.position_coordinate
            location_description = ""
        
        
        size = self.population_bar.position 

        #test if name is unique
        unique = True
        if destination_base is None:
            for planet_instance in self.solar_system_object_link.planets.values():
                if name in planet_instance.bases.keys():
                    unique = False
        
        if 0 < len(name) <= global_variables.max_letters_in_company_names and unique:
            

            home_planet = self.solar_system_object_link.current_planet
            owner = self.solar_system_object_link.current_player
            building_base = self.solar_system_object_link.building_base
            self.solar_system_object_link.building_base = None
            
            
            if sphere_coordinates == "space base":
                northern_loc = None
                eastern_loc = None
            else:
                northern_loc = sphere_coordinates[1]
                eastern_loc = sphere_coordinates[0]
            
            
            input_output_dict = {"input":{
                                          "steel":int(self.pricing["steel_cost_per_person"] * size),
                                          "power":int(self.pricing["power_cost_per_person"] * size),
                                          self.pricing["transport_type"]:int(self.pricing["transport_cost_per_person"] * size),
                                          "electronics":int(self.pricing["electronics_cost_per_person"] * size)
                                          },
                                      "output":{},
                                      "timeframe":30,
                                      "byproducts":{}
            }
            

            base_to_be_build_data = {
                         "destination_base":destination_base,
                         "northern_loc":northern_loc,
                         "eastern_loc":eastern_loc,
                         "population":size,
                         "country":self.solar_system_object_link.current_player.name,
                         "GDP_per_capita_in_dollars":building_base.gdp_per_capita_in_dollars,
                         "home_planet":home_planet,
                         "owner":owner,
                         "name":name,
                         "distance_to_origin":self.pricing["distance"],
                         "transport_type_to_origin":self.pricing["transport_type"]
                         }
            
            
            base_construction = company.base_construction(
                                                          solar_system_object = self.solar_system_object_link, 
                                                          input_output_dict = input_output_dict, 
                                                          location = building_base, 
                                                          name = construction_name, 
                                                          home_planet = building_base.home_planet, 
                                                          base_to_be_build_data = base_to_be_build_data, 
                                                          owner = owner,
                                                          size = size)
            
            
            owner.owned_firms[construction_name] = base_construction


            print_dict = {"text":"The preparation of " + construction_name + location_description + " has started in " + str(building_base.name),"type":"general gameplay info"}
            self.solar_system_object_link.messages.append(print_dict)

            #clear up everything to make space
            self.solar_system_object_link.display_mode = "planetary"
            return "clear"
            
        else:
            print_dict = {"text":"the selected name " + str(name) + " was too long. Has to be less than " + str(global_variables.max_letters_in_company_names) + " characters","type":"general gameplay info"}
            self.solar_system_object_link.messages.append(print_dict)

            self.new_base_ask_for_name(sphere_coordinates,give_length_warning=True)

