import math
import global_variables
import pygame
import primitives

import time
import random

class entry():
    """
    Box that accepts text
    """
    def __init__(self, surface, topleft, width, max_letters, starting_text = "", restrict_input_to = " QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890"):
        self.surface = surface
        self.topleft = topleft
        self.width = width
        self.height = 30
        self.max_letters = max_letters
        self.text = starting_text
        self.restrict_input_to = restrict_input_to
        self.rect = pygame.Rect(self.topleft[0],self.topleft[1],self.width,self.height)
        self.active = True
        self.draw()


    def receive_text(self,event):
        if self.active:
#            print event
            if event.str == "\x08":
                self.text = self.text[0:(len(self.text)-1)]
                self.draw()
#            elif event.key == 13:
#                print "enter"
#                return "enter"
            else:
                if self.restrict_input_to is not None:
                    if event.str not in self.restrict_input_to:
                        return
                if len(self.text) < self.max_letters:
                    self.text = self.text + event.str
                    self.draw()

    def activate(self,position):
        self.active = True


    def draw(self):
        pygame.draw.rect(self.surface,(255,255,255),self.rect)
        pygame.draw.rect(self.surface,(0,0,0),self.rect,1)
        pygame.draw.line(self.surface,(0,0,0),(self.topleft[0], self.topleft[1] + 1), (self.topleft[0]  + self.width - 1, self.topleft[1] + 1),2) #black horizontal
        pygame.draw.line(self.surface,(0,0,0),(self.topleft[0] + 1, self.topleft[1]), (self.topleft[0] + 1, self.topleft[1] + self.height - 1),2) #black vertical


        rendered_text = global_variables.standard_font.render(self.text,True,(0,0,0))
        self.surface.blit(rendered_text,(self.topleft[0] + 5, self.topleft[1] + 6))
        pygame.display.flip()






