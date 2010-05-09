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
    def solarSystem(self):
        return global_variables.solar_system
    """
    Class for the tech tree. Most of the actual algorithms are in techtree.py - this is just a shell for holding
    the notify system in the same structure as other GUI elements
    """
    def __init__(self,solar_system_object, action_surface):
        self.action_surface = action_surface
        self.display_mode_before = "planetary"
        self.rect = pygame.Rect(0,0,0,0)
        

    def create(self):
        sol = self.solarSystem()
        sol.display_mode = "techtree"
        surface = sol.technology_tree.plot_total_tree(sol.technology_tree.vertex_dict,sol.technology_tree.zoomlevel,center = sol.technology_tree.center)
        self.action_surface.blit(surface,(0,0))
        pygame.display.flip()
        
    def receive_click(self,event):
        if self.solarSystem().message_printing["debugging"]:
            print_dict = {"text":"DEBUGGING: tech window received a direct click. This should not be possible","type":"debugging"}
            self.solarSystem().messages.append(print_dict)
