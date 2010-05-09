import math
import global_variables
import pygame
import primitives

import time
import random

class button():
    """
    Class that defines buttons. Takes the name of the button, the surface that it should be drawn on, a function to execute on pressing
    and optionally a position. Size will be determined by length of label.  
    """
    def __init__(self,label, surface, function, function_parameter = None, topleft = (0,0), fixed_size = None):
        self.padding = 5
#        self.topleft = topleft
        self.label = label
        self.surface = surface
        self.function = function
        self.function_parameter = function_parameter
        self.rendered_label = global_variables.standard_font.render(self.label,True,(0,0,0))
#        self.size = self.rendered_label.get_size()
        if fixed_size is None:
            labelsize = self.rendered_label.get_size()
            self.rect = pygame.Rect(topleft[0],topleft[1],labelsize[0] + 2 * self.padding,labelsize[1] + 2 * self.padding)
        else:
            self.rect = pygame.Rect(topleft[0],topleft[1],fixed_size[0],fixed_size[1])


        self.draw()

    
    def activate(self, pos):
        self.draw_pressed()
        return_value = self.function(self.label, self.function_parameter)
        return return_value
        
    def draw(self):
        pygame.draw.rect(self.surface,(212,212,212),self.rect)
        pygame.draw.rect(self.surface,(0,0,0),self.rect,1)
        pygame.draw.line(self.surface,(255,255,255),(self.rect[0], self.rect[1]),(self.rect[0],self.rect[1]+self.rect[3]))
        pygame.draw.line(self.surface,(255,255,255),(self.rect[0], self.rect[1]),(self.rect[0]+self.rect[2],self.rect[1]))
        self.surface.blit(self.rendered_label,(self.rect[0] + self.padding, self.rect[1] + self.padding))
        pygame.display.flip()

    def draw_pressed(self):
#        pygame.draw.rect(self.surface,(212,212,212),self.rect)
#        pygame.draw.rect(self.surface,(0,0,0),self.rect,1)
        pygame.draw.rect(self.surface,(112,112,112),self.rect)
        pygame.draw.line(self.surface,(0,0,0),(self.rect[0]+1,self.rect[1]),(self.rect[0]+1,self.rect[1] + self.rect[3] - 2)) #vertical
        pygame.draw.line(self.surface,(0,0,0),(self.rect[0],self.rect[1]+1),(self.rect[0]+self.rect[2] - 2,self.rect[1]+1),1) #horizontal
        self.surface.blit(self.rendered_label,(self.rect[0] + self.padding, self.rect[1] + self.padding))
        pygame.display.flip()
        time.sleep(0.05)
        self.draw()         




