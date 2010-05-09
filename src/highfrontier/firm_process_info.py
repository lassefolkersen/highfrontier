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

class firm_process_info():
    def solarSystem(self):
        return global_variables.solar_system
    """
    Subview of the firm view. Shows a list of the resources of interest for the firm. Both the stock and the production rate is shown.
    """

    def __init__(self,solar_system_object,action_surface):
        self.rect = pygame.Rect(50,50,700,500)
        self.action_surface = action_surface
        

        
    def receive_click(self,event):
        self.fast_list.receive_click(event)
            


    def create(self):
        """
        The creation function.  
        """
        
        firm_selected = self.solarSystem().firm_selected
        
        
        if firm_selected is not None:
            
            if firm_selected.isMerchant():
                process_and_stock_dict = {}
                for direction_name in ["destination","origin"]:
                    if direction_name == "destination":
                        base = firm_selected.to_location
                    else:
                        base = firm_selected.from_location
                    
                    direction = "in " + base.name
                    for resource in [firm_selected.resource, firm_selected.transport_type]:
                         process_and_stock_dict[resource + " at " + direction_name] = {}
                         process_and_stock_dict[resource + " at " + direction_name]["direction"] = direction
                         if direction_name == "destination":
                             process_and_stock_dict[resource + " at " + direction_name]["current stock"] = firm_selected.to_stock_dict[resource]
                         else:
                             process_and_stock_dict[resource + " at " + direction_name]["current stock"] = firm_selected.from_stock_dict[resource]
                         process_and_stock_dict[resource + " at " + direction_name]["rate"] = "NA"
                 
            else:
                process_and_stock_dict = {}
                for direction in ["input","output"]:
                    for resource in firm_selected.input_output_dict[direction]:
                         process_and_stock_dict[resource] = {}
                         process_and_stock_dict[resource]["direction"] = direction
                         process_and_stock_dict[resource]["current stock"] = firm_selected.stock_dict[resource]
                         process_and_stock_dict[resource]["rate"] = firm_selected.input_output_dict[direction][resource]
        
            self.fast_list = gui_components.fast_list(self.action_surface, process_and_stock_dict, rect = self.rect,column_order = ["rownames","direction","rate","current stock"])
        
            














