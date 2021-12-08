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

class company_list_of_firms():
    """
    Subview of the company view. Shows a list of all firms owned by the company. A shortcut button allows quick zoom to the firm page of these firms.
    """

    def __init__(self,solar_system_object,action_surface):
        self.solar_system_object_link = solar_system_object
        self.rect = pygame.Rect(50,50,700,500)
        self.action_surface = action_surface



    def create(self):
        """
        The creation function.
        """
        company_selected = self.solar_system_object_link.company_selected
        if company_selected is None:
            raise Exception("A list of firms was requested, but no company was selected")

        firm_data = {}
        for firm_instance in list(company_selected.owned_firms.values()):
            firm_data[firm_instance.name] = {}
            try: firm_instance.last_profit
            except:
                firm_data[firm_instance.name]["last profit"] = "NA"
            else:
                firm_data[firm_instance.name]["last profit"] = firm_instance.last_profit

            firm_data[firm_instance.name]["location"] = firm_instance.location.name

            stock_amount = 0
            for stock_item in list(firm_instance.stock_dict.values()):
                stock_amount = stock_amount + stock_item
            firm_data[firm_instance.name]["stock size"] = stock_amount
        self.fast_list = fast_list.fast_list(self.action_surface, firm_data, rect = self.rect)


    def receive_click(self,event):
        self.fast_list.receive_click(event)
        if event.button == 3:
            firm_selected = None
            for firm in list(self.solar_system_object_link.company_selected.owned_firms.values()):
                if firm.name == self.fast_list.selected_name:
                    firm_selected = firm
            if firm_selected is None:
                if self.solar_system_object_link.message_printing["debugging"]:
                    print_dict = {"text":"POSSIBLE DEBUGGING: - the firm asked for was of None type","type":"debugging"}
                    self.solar_system_object_link.messages.append(print_dict)

            else:
                if isinstance(firm_selected, company.base):
                    self.solar_system_object_link.display_mode = "base"
                    self.solar_system_object_link.current_planet.current_base = firm_selected

                else:
                    self.solar_system_object_link.display_mode = "firm"
                    self.solar_system_object_link.firm_selected = firm_selected
                return "clear"



