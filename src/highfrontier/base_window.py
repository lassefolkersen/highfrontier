import fast_list
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
import random
import time

class base_window():
    """
    This window shows an overview of all bases with options for fast jumping.
    """
    def __init__(self,solar_system_object,action_surface):
        self.solar_system_object_link = solar_system_object
        self.rect = pygame.Rect(50,50,700,500)
        self.action_surface = action_surface
    def create(self):
        """
        The creation function. ' 
        """
        base_data = {}
        for planet_instance in self.solar_system_object_link.planets.values():
            for base_instance in planet_instance.bases.values():
                if base_instance.for_sale:
                    for_sale = "For sale"
                else:
                    for_sale = ""
                data_here = {"Location":planet_instance.name,"Population":base_instance.population,"For sale":for_sale}
                base_data[base_instance.name] = data_here
        column_order = ["rownames","Location","Population","For sale"]
        self.fast_list = fast_list.fast_list(self.action_surface, base_data, self.rect, column_order)
    def receive_click(self,event):
        self.fast_list.receive_click(event)
        if event.button == 3:
            base_selected = None
            for planet_instance in self.solar_system_object_link.planets.values():
                for base_instance in planet_instance.bases.values():
                    if base_instance.name == self.fast_list.selected_name:
                        base_selected = base_instance
            if base_selected is None:
                raise Exception("The base sought after (" + str(self.fast_list.selected_name) + ") was not found in the base list of the solar_system_object_link")
            self.solar_system_object_link.current_planet.current_base = base_selected
            self.solar_system_object_link.display_mode = "base"
            return "clear"
