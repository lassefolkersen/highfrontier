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

class company_ownership_info():
    """
    Subview of the company view. Shows miscellanous information about a company, such as decision parameters, capital and number of firms.
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
        company_selected = self.solar_system_object_link.company_selected
        if company_selected is not None:
            company_ownership_dict = {}

            for company_database_variable in company_selected.company_database:
                company_database_variable_name_here = company_database_variable
                if len(company_database_variable_name_here) > global_variables.max_letters_in_company_names:
                    company_database_variable_name_here = company_database_variable_name_here[0:global_variables.max_letters_in_company_names]
                company_ownership_dict["parameter: " + company_database_variable_name_here] = {"info":str(company_selected.company_database[company_database_variable])}

            company_ownership_dict["capital"] = {"info":company_selected.capital}

            company_ownership_dict["home cities, number of"] = {"info":str(len(company_selected.home_cities))}
            if 0 < len(company_selected.home_cities) < 4:
                list_value = str(list(company_selected.home_cities.keys()))
                list_value = list_value.rstrip("]")
                list_value = list_value.lstrip("[")
                company_ownership_dict["home cities"] = {"info":list_value}

            company_ownership_dict["last_firm_evaluation"] = {"info":str(company_selected.last_firm_evaluation)}
            company_ownership_dict["last_market_evaluation"] = {"info":str(company_selected.last_market_evaluation)}
            company_ownership_dict["last_demand_evaluation"] = {"info":str(company_selected.last_demand_evaluation)}
            company_ownership_dict["last_supply_evaluation"] = {"info":str(company_selected.last_supply_evaluation)}

            company_ownership_dict["research"] = {"info":str(company_selected.research)}

            company_ownership_dict["firms owned, number of"] = {"info":str(len(company_selected.owned_firms))}

            self.fast_list = fast_list.fast_list(self.action_surface, company_ownership_dict, rect = self.rect)
        else:
            if self.solar_system_object_link.message_printing["debugging"]:
                print_dict = {"text":"DEBUGGING: Company selected was None","type":"debugging"}
                self.solar_system_object_link.messages.append(print_dict)







