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

class base_list_of_companies():
    """
    Subview of the base view. Shows a list of all companies operating in the base. Shortcut button to zoom in on one of these companies.
    """

    def __init__(self,solar_system_object,action_surface):
        self.solar_system_object_link = solar_system_object
        self.rect = pygame.Rect(50,50,700,500)
        self.action_surface = action_surface


    def receive_click(self,event):
        self.fast_list.receive_click(event)
        if event.button == 3:

            if self.fast_list.selected_name in list(self.solar_system_object_link.companies.keys()):
                selected_company = self.solar_system_object_link.companies[self.fast_list.selected_name]
                self.solar_system_object_link.display_mode = "company"
                self.solar_system_object_link.company_selected = selected_company
                return "clear"

            else:
                if self.solar_system_object_link.message_printing["debugging"]:
                    print_dict = {"text":"DEBUGGING:  " + str(self.fast_list.selected_name) + " was not found in company database","type":"debugging"}
                    self.solar_system_object_link.messages.append(print_dict)




    def create(self):
        """
        The creation function.
        """

        company_data = {}
        for company_instance in list(self.solar_system_object_link.companies.values()):
            if self.solar_system_object_link.current_planet.current_base.name in list(company_instance.home_cities.keys()):
                company_data[company_instance.name] = {}
                company_data[company_instance.name]["capital"] = company_instance.capital

                owned_firms_here = 0
                for firm_instance in list(company_instance.owned_firms.values()):
                    if firm_instance.location == self.solar_system_object_link.current_planet.current_base:
                         owned_firms_here = owned_firms_here + 1

                company_data[company_instance.name]["local firms"] = owned_firms_here


        self.fast_list = fast_list.fast_list(self.action_surface, company_data, rect = self.rect)


