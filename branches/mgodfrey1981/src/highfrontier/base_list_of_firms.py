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

class base_list_of_firms():
    def solarSystem(self):
        return global_variables.solar_system
    """
    Subview of the base view. Shows a list of all firms operating in the base. Shortcut button to zoom in on one of these firms.
    """

    def __init__(self,solar_system_object,action_surface):
        self.rect = pygame.Rect(50,50,700,500)
        self.action_surface = action_surface
        

        
    

        

    def create(self):
        """
        The creation function.  
        """
        list_of_firms_in_base = []
        for company_instance in self.solarSystem().companies.values():
            for firm_instance in company_instance.owned_firms.values():
                if not firm_instance.isMerchant():
                    if firm_instance.location == self.solarSystem().current_planet.current_base:
                        list_of_firms_in_base.append(firm_instance)
                else:
                    if firm_instance.from_location == self.solarSystem().current_planet.current_base or firm_instance.to_location == self.solarSystem().current_planet.current_base:
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
            for stock_item in firm_instance.stock_dict.values():
                stock_amount = stock_amount + stock_item
            firm_data[firm_instance.name]["stock size"] = stock_amount
        
        self.fast_list = gui_components.fast_list(self.action_surface, 
                                                  firm_data, 
                                                  rect = self.rect,
                                                  column_order = ["rownames","owner","stock size","last profit"]
                                                  )
        
    
    def receive_click(self,event):
        self.fast_list.receive_click(event)
        if event.button == 3:
            firm_selected = self.links[self.fast_list.selected_name]
            if firm_selected.isBase():
                return "clear"
            else:
                self.solarSystem().display_mode = "firm"
                self.solarSystem().firm_selected = firm_selected
                return "clear"
