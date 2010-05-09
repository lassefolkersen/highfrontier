import radiobuttons
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

class overlay_window():
    def solarSystem(self):
        return global_variables.solar_system
    """
    The overlay control window. Can be toggled from commandbox. When visible it can be used to control which visual overlays
    that can be seen in planet mode (topographical maps, resource maps etc)
    """
    def __init__(self,solar_system_object,action_surface):
        self.rect = pygame.Rect(500,50,200,250)
        self.action_surface = action_surface
        
    def overlay_set(self,type_of_overlay, function_parameter):
        sol = self.solarSystem()
        sol.current_planet.planet_display_mode = type_of_overlay
        surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
        self.action_surface.blit(surface,(0,0))
        self.create()
        pygame.display.flip()

#    def (self,button_name,function_parameter):
#        print "emitted display overlay with " + str(button_name)


    def receive_click(self,event):
        self.radiobuttons.activate(event.pos)


        
    def create(self):
        """
        The creation function. Doesn't return anything. 
        """
        
        pygame.draw.rect(self.action_surface, (212,212,212), self.rect)
        pygame.draw.rect(self.action_surface, (0,0,0), self.rect, 2)
        pygame.draw.line(self.action_surface, (255,255,255), (self.rect[0], self.rect[1]), (self.rect[0] + self.rect[2], self.rect[1]))
        pygame.draw.line(self.action_surface, (255,255,255), (self.rect[0], self.rect[1]), (self.rect[0], self.rect[1] + self.rect[3]))
        
        labels = ["visible light","trade network","topographical"] + self.solarSystem().mineral_resources

        self.radiobuttons = radiobuttons.radiobuttons(
                                                        labels, 
                                                        self.action_surface, 
                                                        self.overlay_set, 
                                                        function_parameter = None, 
                                                        topleft = (self.rect[0] + 10 , self.rect[1] + 10), 
                                                        selected = self.solarSystem().current_planet.planet_display_mode)
