import signaller
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
    def create(self):
        """
        The creation function.  
        """
        pygame.draw.rect(self.action_surface, 
                         (212,212,212), 
                         self.rect)
        pygame.draw.rect(self.action_surface, 
                         (0,0,0), 
                         self.rect, 2)
        pygame.draw.line(self.action_surface, 
                         (255,255,255), 
                         (self.rect[0], self.rect[1]), 
                         (self.rect[0] + self.rect[2], self.rect[1]))
        pygame.draw.line(self.action_surface, 
                         (255,255,255), 
                         (self.rect[0], self.rect[1]), 
                         (self.rect[0], self.rect[1] + self.rect[3]))
        
        self.button_labels = ["mercury","venus","earth","mars","jupiter","saturn","uranus","neptune"]

        self.buttons = {}
        for i, button_label in enumerate(self.button_labels):
            b=button.button(
                button_label, 
                self.action_surface,
                topleft = (self.rect[0] + 5, self.rect[1] + 5 + i * 30),
                fixed_size = (self.rect[2] - 10, 
                              25))
            self.buttons[button_label] = b
            signaller.connect(b,"signal__clicked",lambda: self.planet_jump(b.label()))

    def planet_jump(self,planet_name):
        print "planet_jump_window::planet_jump(",planet_name,")"
        planet = self.solar_system_object_link.planets[planet_name] 
        self.solar_system_object_link.current_planet = planet
        planet.load_for_drawing()
        self.solar_system_object_link.display_mode = "planetary"
        surface = planet.draw_entire_planet(planet.eastern_inclination,planet.northern_inclination,planet.projection_scaling)
        self.action_surface.blit(surface,(0,0))
        pygame.display.flip()
            
    """
    The planet jump window. Can be toggled from commandbox. When visible it can be used as shortcut to planet view
    for the different planets
    """
    def __init__(self,solar_system_object,action_surface):
        self.solar_system_object_link = solar_system_object
        self.rect = pygame.Rect(500,50,100,250)
        self.action_surface = action_surface
        
        
        
            
    

    
    def receive_click(self,event):
        offset = event.pos[1] - self.rect[1]
        index = (offset - 5) // 30
        if 0 <= index < len(self.button_labels):
            selection = self.buttons[self.button_labels[index]].activate(event.pos)
            if selection in self.solar_system_object_link.planets.keys():
                return self.solar_system_object_link.planets[selection]
            else:
                if self.solar_system_object_link.message_printing["debugging"]:
                    print_dict = {"text":"DEBUGGING: The planet jump function asked to go to a non-recognised planet","type":"debugging"}
                    self.solar_system_object_link.messages.append(print_dict)


