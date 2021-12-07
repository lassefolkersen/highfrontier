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

class base_list_of_firms():
    """
    Subview of the base view. Shows a list of all firms operating in the base. Shortcut button to zoom in on one of these firms.
    """

    def __init__(self,solar_system_object,action_surface):
        self.solar_system_object_link = solar_system_object
        self.rect = pygame.Rect(50,50,700,500)
        self.action_surface = action_surface
        

        
    

        

    def create(self):
        """
        The creation function.  
        """
        list_of_firms_in_base = []
        for company_instance in list(self.solar_system_object_link.companies.values()):
            for firm_instance in list(company_instance.owned_firms.values()):
                if not isinstance(firm_instance, company.merchant):
                    if firm_instance.location == self.solar_system_object_link.current_planet.current_base:
                        list_of_firms_in_base.append(firm_instance)
                else:
                    if firm_instance.from_location == self.solar_system_object_link.current_planet.current_base or firm_instance.to_location == self.solar_system_object_link.current_planet.current_base:
                        list_of_firms_in_base.append(firm_instance)
#        print list_of_firms_in_base
        firm_data = {}
        self.links = {}
        for firm_instance in list_of_firms_in_base:
            firm_data[firm_instance.name] = {}
            try: firm_instance.last_profit
            except: 
                firm_data[firm_instance.name]["last profit"] = "NA"
            else: 
                firm_data[firm_instance.name]["last profit"] = firm_instance.last_profit
            
            firm_data[firm_instance.name]["owner"] = firm_instance.owner.name
            self.links[firm_instance.name] = firm_instance
            
            stock_amount = 0
            for stock_item in list(firm_instance.stock_dict.values()):
                stock_amount = stock_amount + stock_item
            firm_data[firm_instance.name]["stock size"] = stock_amount
        
        self.fast_list = fast_list.fast_list(self.action_surface, 
                                                  firm_data, 
                                                  rect = self.rect,
                                                  column_order = ["rownames","owner","stock size","last profit"]
                                                  )
        
    
    def receive_click(self,event):
        self.fast_list.receive_click(event)
        if event.button == 3:
            firm_selected = self.links[self.fast_list.selected_name]
            if isinstance(firm_selected, company.base): #in this case we are already in the base, so we do nothing.
                return "clear"
            else:
                self.solar_system_object_link.display_mode = "firm"
                self.solar_system_object_link.firm_selected = firm_selected
                return "clear"



