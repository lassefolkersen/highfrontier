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

class message_bar():
    """
    Class that receives messages for the player and prints them.
    It will show the message depending on the type. Types are:
    general gameplay info
    company_generation
    and more
    
    The message bar is visible at all times in the bottom of the screen.
    """
    def __init__(self,solar_system_object,action_surface,message_surface):
        self.solar_system_object_link = solar_system_object
        self.action_surface = action_surface
        self.message_surface = message_surface

        self.messages = []
        self.max_print_length = 6 #how many lines of text to print in standard viewing of the window
        self.max_save_length = 500 #how many lines of text to save in memory
        self.max_string_length = 140#how many letters is maximally allowed to be printed in the message window
        
        self.create()
        
        


    def create(self):
        """
        Function that will update the text field
        """
        self.message_surface.fill((212,212,212))
        pygame.draw.line(self.message_surface, (255,255,255), (0, 0), (self.message_surface.get_size()[0],0),2)        
        pygame.draw.line(self.message_surface, (255,255,255), (0, 0), (0,self.message_surface.get_size()[1]),2)

        
        #first trim the message list down to the number indicated to be max
        if len(self.messages) > self.max_save_length:
            surplus = len(self.messages) - self.max_save_length
            del self.messages[0:surplus]


        messages = []
        
        range_here = range(0,len(self.solar_system_object_link.messages))
        range_here.reverse()

        for i in range_here:
            message = self.solar_system_object_link.messages[i]
            if self.solar_system_object_link.message_printing[message["type"]]:
                messages.append(message)
            if len(messages) >= self.max_print_length:
                break
        messages.reverse()
        

        i = 0
        for message in messages:
            if self.solar_system_object_link.message_printing[message["type"]]:
                if len(message["text"]) > self.max_string_length:
                    message_text = message["text"][0:self.max_string_length]
                else:
                    message_text = message["text"]
                rendered_message_string = global_variables.standard_font_small.render(message_text,True,(0,0,0))
                self.message_surface.blit(rendered_message_string, (10,10 + i * 15))
                i = i + 1
