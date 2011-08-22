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

class company_window():
    """
    The company overview window. Can be toggled from commandbox. Shows all companies in the solarsystem, along with some info
    about them. Can be used as shortcut to the company of interest.
    """
    def __init__(self,solar_system_object,action_surface):
        self.solar_system_object_link = solar_system_object
        self.rect = pygame.Rect(50,50,700,500)
        self.action_surface = action_surface
        
 
    def create(self):
        """
        The creation function. 
        """
        
        company_data = {}
        for company_name in self.solar_system_object_link.companies:
            company_instance = self.solar_system_object_link.companies[company_name]
            capital = company_instance.capital
            no_of_firms = len(company_instance.owned_firms)
            no_of_cities = len(company_instance.home_cities)
            data_here = {"capital":capital,"owned firms":no_of_firms,"home cities":no_of_cities}
            if len(company_name)> global_variables.max_letters_in_company_names:
                if self.solar_system_object_link.message_printing["debugging"]:
                    print_dict = {"text":"DEBUGGING: Shortened " + str(company_name) + " to " + str(company_name[0:30]),"type":"debugging"}
                    self.solar_system_object_link.messages.append(print_dict)
                company_name = company_name[0:global_variables.max_letters_in_company_names]
            company_data[company_name] = data_here
        
        column_order = ["rownames","capital","owned firms","home cities"]
        
        self.fast_list = fast_list.fast_list(self.action_surface, company_data, rect = self.rect, column_order = column_order)

                

    def receive_click(self,event):
        self.fast_list.receive_click(event)
        if event.button == 3:

            if self.fast_list.selected_name in self.solar_system_object_link.companies.keys():
                selected_company = self.solar_system_object_link.companies[self.fast_list.selected_name]
                self.solar_system_object_link.display_mode = "company"
                self.solar_system_object_link.company_selected = selected_company
                return "clear"

            else:
                print_dict = {"text":"DEBUGGING:  " + str(self.fast_list.selected_name) + " was not found in company database","type":"debugging"}
                self.solar_system_object_link.messages.append(print_dict)
                











