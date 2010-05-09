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

class tech_window():
    """
    Class for the tech tree. Most of the actual algorithms are in techtree.py - this is just a shell for holding
    the notify system in the same structure as other GUI elements
    """
    def __init__(self,solar_system_object, action_surface):
        self.solar_system_object_link = solar_system_object
        self.action_surface = action_surface
        self.display_mode_before = "planetary"
        self.rect = pygame.Rect(0,0,0,0)
        

    def create(self):
        sol = self.solar_system_object_link
        sol.display_mode = "techtree"
        surface = sol.technology_tree.plot_total_tree(sol.technology_tree.vertex_dict,sol.technology_tree.zoomlevel,center = sol.technology_tree.center)
        self.action_surface.blit(surface,(0,0))
        pygame.display.flip()
        
    def receive_click(self,event):
        if self.solar_system_object_link.message_printing["debugging"]:
            print_dict = {"text":"DEBUGGING: tech window received a direct click. This should not be possible","type":"debugging"}
            self.solar_system_object_link.messages.append(print_dict)
