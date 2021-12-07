import signaller
import math
from . import global_variables
import pygame
from . import primitives

import time
import random

class button():
    def rect(self):
        size=self.renderedLabel().get_size()
        w=size[0]+2*self.padding()
        h=size[1]+2*self.padding()
        topleft=self.topLeft()
        x=topleft[0]
        y=topleft[1]
        if(not self.fixedSize() is None):
            size=self.fixedSize()
            w=size[0]
            h=size[1]
        self._rect = pygame.Rect(x,y,w,h)
        return self._rect
    def __init__(self,label="unlabeled", 
                 surface=None, 
                 topleft = (0,0), 
                 fixed_size = None):
        self.setPadding(5)
        self.setLabel(label)
        self.setSurface(surface)
        self.setTopLeft(topleft)
        self.setFixedSize(fixed_size)
        self.draw()
    def setPadding(self,p):
        self._padding=p
        return
    def padding(self):
        return self._padding
    
    def setLabel(self,l):
        self._label=l
        self._rendered_label = global_variables.standard_font.render(self._label,True,(0,0,0))
        self._labelsize=self.renderedLabel().get_size()
        return
    def label(self):
        return self._label
    def renderedLabel(self):
        return self._rendered_label
    def labelsize(self):
        return self.renderedLabel().get_size();
    """
    Class that defines buttons. Takes the name of the button, the surface that it should be drawn on, a function to execute on pressing
    and optionally a position. Size will be determined by length of label.  
    """
    def activate(self, pos):
        self.draw_pressed()
        signaller.emit(self,"signal__clicked") # dispatch the click event
        
    def draw(self):
        shape = self.rect()
        
        pygame.draw.rect(self.surface(),(212,212,212),shape)
        pygame.draw.rect(self.surface(),(0,0,0),shape,1)
        pygame.draw.line(self.surface(),(255,255,255),(shape[0], shape[1]),(shape[0],shape[1]+shape[3]))
        pygame.draw.line(self.surface(),(255,255,255),(shape[0], shape[1]),(shape[0]+shape[2],shape[1]))
        self.surface().blit(self.renderedLabel(),(shape[0] + self.padding(), shape[1] + self.padding()))
        pygame.display.flip()

    def draw_pressed(self):
        shape = self.rect()
        pygame.draw.rect(self.surface(),(112,112,112),shape)
        pygame.draw.line(self.surface(),(0,0,0),(shape[0]+1,shape[1]),(shape[0]+1,shape[1] + shape[3] - 2)) #vertical
        pygame.draw.line(self.surface(),(0,0,0),(shape[0],shape[1]+1),(shape[0]+shape[2] - 2,shape[1]+1),1) #horizontal
        self.surface().blit(self.renderedLabel(),(shape[0] + self.padding(), shape[1] + self.padding()))
        pygame.display.flip()
        time.sleep(0.05)
        self.draw()         
    def setSurface(self,s):
        self._surface=s
        return
    def surface(self):
        return self._surface
    def function(self):
        return self._function
    def setFunction(self,f):
        self._function=f
        return
    def setFunctionParameter(self,p):
        self._function_parameter=p
        return
    def functionParameter(self):
        return self._function_parameter
    def fixedSize(self):
        return self._fixed_size
    def setFixedSize(self,f=None):
        self._fixed_size=f
        return
    def setTopLeft(self,tl):
        self._topLeft=tl
        return
    def topLeft(self):
        return self._topLeft
