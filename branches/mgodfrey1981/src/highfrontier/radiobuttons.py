import math
import global_variables
import pygame
import primitives

import time
import random

class radiobuttons():
    def __init__(self,labels,surface, function,function_parameter = None, topleft = (0,0), selected = None):
        self.textheight = 15
        self.topleft = topleft
        self.labels = labels
        self.surface = surface
        self.function = function
        self.function_parameter = function_parameter
        if selected is None:
            self.selected = self.labels[0]
        else:
            if selected in self.labels:
                self.selected = selected
            else:
                raise Exception("The pre-selected radiobutton " + str(selected) + " was not found in labels")

        self.rect = pygame.Rect(self.topleft[0],self.topleft[1],20,len(labels)*self.textheight)
        
        self.draw()

    def activate(self, pos):
        selected_pos = (pos[1] - self.topleft[1]) // self.textheight
        self.selected = self.labels[selected_pos]
        self.update_radiobuttons()
        self.function(self.selected,self.function_parameter)
        
        
        

    def draw(self):
        for i, label in enumerate(self.labels):
            rendered_label = global_variables.standard_font.render(label,True,(0,0,0))
            self.surface.blit(rendered_label,(self.topleft[0] + 20, self.topleft[1] + self.textheight * i))
        self.update_radiobuttons()


    
    def update_radiobuttons(self):    
        for i, label in enumerate(self.labels):
            pygame.draw.circle(self.surface,(255,255,255),(self.topleft[0] + 10,self.topleft[1] + self.textheight // 2 + self.textheight*i),6)
            pygame.draw.circle(self.surface,(0,0,0),(self.topleft[0] + 10,self.topleft[1] + self.textheight // 2 + self.textheight*i),6, 1)
            if label == self.selected:
                pygame.draw.circle(self.surface,(0,0,0),(self.topleft[0] + 10,self.topleft[1] + self.textheight // 2 + self.textheight*i),4)
        
        pygame.display.flip()
                          





