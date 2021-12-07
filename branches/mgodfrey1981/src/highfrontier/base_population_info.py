from . import fast_list
from . import merchant
import os
from . import global_variables
import sys
import string
import pygame
import datetime
import math
from . import company
from . import primitives
import random
import time


class base_population_info():
    """
    Subview of the base view. Shows miscellanous information about a base, such as stock, trade routes and population.
    """

    def __init__(self,solar_system_object,action_surface):
        self.solar_system_object_link = solar_system_object
        self.rect = pygame.Rect(50,50,700,500)
        self.action_surface = action_surface
        
    def receive_click(self,event):
        self.fast_list.receive_click(event)

    def create(self):
        """
        The creation function.  
        """
        base_selected = self.solar_system_object_link.current_planet.current_base
        if base_selected is not None:
            base_population_dict= {}
            base_population_dict["Owner"] = {"info":base_selected.owner.name}
            base_population_dict["GDP per capita"] = {"info":base_selected.gdp_per_capita_in_dollars}
            base_population_dict["Position: east"] = {"info":str(base_selected.position_coordinate[0])}
            base_population_dict["Position: north"] = {"info":str(base_selected.position_coordinate[1])}
            base_population_dict["Population"] = {"info":base_selected.population}
            base_population_dict["Bitternes"] = {"info":base_selected.bitternes_of_base}
            base_population_dict["Wages"] = {"info":base_selected.wages}
            
            for resource in base_selected.mining_opportunities:
                 base_population_dict["Mining: " + resource] = {"info":base_selected.mining_opportunities[resource]}
            
            for resource in base_selected.stock_dict:
                 base_population_dict["Stock: " + resource] = {"info":base_selected.stock_dict[resource]}

            for resource in base_selected.input_output_dict["input"]:
                 base_population_dict["Input: " + resource] = {"info":base_selected.input_output_dict["input"][resource]}

            
            base_population_dict["Trade routes, number of"] = {"info":str(len(base_selected.trade_routes))}
            if 0 < len(base_selected.trade_routes) < 6:
                trade_route_list = ""
                for trade_route in list(base_selected.trade_routes.keys()):
                    trade_route_list = trade_route_list + trade_route + ", "
                trade_route_list = trade_route_list.rstrip(", ")
                base_population_dict["Trade routes"] = {"info":trade_route_list}
            

            self.fast_list = fast_list.fast_list(self.action_surface, base_population_dict, rect = self.rect, column_order = ["rownames","info"])
        else:
            if self.solar_system_object_link.message_printing["debugging"]:
                print_dict = {"text":"DEBUGGING: Base selected was None","type":"debugging"} 
                self.solar_system_object_link.messages.append(print_dict)

            




