import math
from . import global_variables
import pygame
from . import primitives

import time
import random

class togglebutton():
    """
    Class that defines ToggleButtons. Takes the name of the button, the surface that it should be drawn on, a function to execute on pressing
    and optionally a position. Size will be determined by length of label.  
    """
    def __init__(self,label, surface, function, function_parameter = None, topleft = (0,0), fixed_size = None, pressed = False):
        self.padding = 10
        self.topleft = topleft
        self.label = label
        self.pressed = pressed
        self.surface = surface
        self.function = function
        self.function_parameter = function_parameter
        self.rendered_label = global_variables.standard_font.render(self.label,True,(0,0,0))
        if fixed_size is None:
            labelsize = self.rendered_label.get_size()
            self.rect = pygame.Rect(self.topleft[0],self.topleft[1],labelsize[0] + 2 * self.padding,labelsize[1] + 2 * self.padding)
        else:
            self.rect = pygame.Rect(self.topleft[0],self.topleft[1],fixed_size[0],fixed_size[1])
        
        if self.pressed:
            self.draw_pressed()
            
        else:
            self.draw_unpressed()
            

    
    def activate(self, pos):
        if self.pressed:
            self.draw_unpressed()
            self.pressed = False
            
        else:
            self.draw_pressed()
            self.pressed = True
            
            
        self.function(self.pressed, self.function_parameter)
        
    def draw_unpressed(self):
        pygame.draw.rect(self.surface,(212,212,212),self.rect)
        pygame.draw.rect(self.surface,(0,0,0),self.rect,1)
        pygame.draw.line(self.surface,(255,255,255),self.topleft,(self.topleft[0],self.topleft[1]+self.rect[3]))
        pygame.draw.line(self.surface,(255,255,255),self.topleft,(self.topleft[0]+self.rect[2],self.topleft[1]))
        self.surface.blit(self.rendered_label,(self.topleft[0] + self.padding, self.topleft[1] + self.padding))
        pygame.display.flip()

    def draw_pressed(self):
        pygame.draw.rect(self.surface,(212,212,212),self.rect)
        pygame.draw.rect(self.surface,(0,0,0),self.rect,1)
        pygame.draw.rect(self.surface,(112,112,112),pygame.Rect(self.topleft[0],self.topleft[1],self.rect[2],self.rect[3]))
        pygame.draw.line(self.surface,(0,0,0),(self.topleft[0]+1,self.topleft[1]),(self.topleft[0]+1,self.topleft[1]+self.rect[3]-2)) #vertical
        pygame.draw.line(self.surface,(0,0,0),(self.topleft[0],self.topleft[1]+1),(self.topleft[0]+self.rect[2]+ - 2,self.topleft[1]+1),1) #horizontal

        self.surface.blit(self.rendered_label,(self.topleft[0] + self.padding, self.topleft[1] + self.padding))
        pygame.display.flip()
        


