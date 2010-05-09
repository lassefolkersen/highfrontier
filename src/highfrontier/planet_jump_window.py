import button
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

class planet_jump_window():
    def solarSystem(self):
        return global_variables.solar_system
    """
    The planet jump window. Can be toggled from commandbox. When visible it can be used as shortcut to planet view
    for the different planets
    """
    def __init__(self,solar_system_object,action_surface):
        self.rect = pygame.Rect(500,50,100,250)
        self.action_surface = action_surface
        
        
        
    def planet_jump(self,planet_name,function_parameter):
        planet = self.solarSystem().planets[planet_name] 
        self.solarSystem().current_planet = planet
        planet.load_for_drawing()
        self.solarSystem().display_mode = "planetary"
        surface = planet.draw_entire_planet(planet.eastern_inclination,planet.northern_inclination,planet.projection_scaling)
        self.action_surface.blit(surface,(0,0))
        pygame.display.flip()
            
    

    
    def receive_click(self,event):
        offset = event.pos[1] - self.rect[1]
        index = (offset - 5) // 30
        if 0 <= index < len(self.button_labels):
            selection = self.buttons[self.button_labels[index]].activate(event.pos)
            if selection in self.solarSystem().planets.keys():
                return self.solarSystem().planets[selection]
            else:
                if self.solarSystem().message_printing["debugging"]:
                    print_dict = {"text":"DEBUGGING: The planet jump function asked to go to a non-recognised planet","type":"debugging"}
                    self.solarSystem().messages.append(print_dict)


    def create(self):
        """
        The creation function.  
        """
        pygame.draw.rect(self.action_surface, (212,212,212), self.rect)
        pygame.draw.rect(self.action_surface, (0,0,0), self.rect, 2)
        pygame.draw.line(self.action_surface, (255,255,255), (self.rect[0], self.rect[1]), (self.rect[0] + self.rect[2], self.rect[1]))
        pygame.draw.line(self.action_surface, (255,255,255), (self.rect[0], self.rect[1]), (self.rect[0], self.rect[1] + self.rect[3]))
        
        self.button_labels = ["mercury","venus","earth","mars","jupiter","saturn","uranus","neptune"]

        self.buttons = {}
        for i, button_label in enumerate(self.button_labels):
            self.buttons[button_label] = button.button(button_label, self.action_surface, self.planet_jump, topleft = (self.rect[0] + 5, self.rect[1] + 5 + i * 30),fixed_size = (self.rect[2] - 10, 25))
