import signaller
import math
import global_variables
import pygame
import primitives

import time
import random

class radiobuttons():
    def activate(self, pos):
        selected_pos = (pos[1] - self.topLeft()[1]) // self.textHeight()
        self.setSelected(self.labels()[selected_pos])
        self.update_radiobuttons()
        signaller.emit(self,"signal__change",self.selected())
    def __init__(self,labels,surface, topleft = (0,0), selected = None):
        self.setTextHeight(15)
        self.setTopLeft(topleft)
        self.setLabels(labels)
        self.setSurface(surface)
        if selected is None:
            self.setSelected(self.labels()[0])
        else:
            if selected in self.labels():
                self.setSelected(selected)
            else:
                raise Exception("The pre-selected radiobutton " + str(selected) + " was not found in labels")
        self.setRect(pygame.Rect(self.topLeft()[0],
                                 self.topLeft()[1],
                                 20,
                                 len(labels)*self.textHeight()))
        self.draw()
    def setRect(self,r):
        self._rect=r
        return
    def rect(self):
        return self._rect
    def setTextHeight(self,h):
        self._textHeight=h
        return
    def textHeight(self):
        return self._textHeight

    def draw(self):
        for i, label in enumerate(self.labels()):
            rendered_label = global_variables.standard_font.render(label,True,(0,0,0))
            self.surface().blit(rendered_label,(self.topLeft()[0] + 20, self.topLeft()[1] + self.textHeight() * i))
        self.update_radiobuttons()


    
    def update_radiobuttons(self):    
        for i, label in enumerate(self.labels()):
            pygame.draw.circle(self.surface(),(255,255,255),(self.topLeft()[0] + 10,self.topLeft()[1] + self.textHeight() // 2 + self.textHeight()*i),6)
            pygame.draw.circle(self.surface(),(0,0,0),(self.topLeft()[0] + 10,self.topLeft()[1] + self.textHeight() // 2 + self.textHeight()*i),6, 1)
            if label == self.selected():
                pygame.draw.circle(self.surface(),(0,0,0),(self.topLeft()[0] + 10,self.topLeft()[1] + self.textHeight() // 2 + self.textHeight()*i),4)
        
        pygame.display.flip()

    def setTopLeft(self,t):
        self._topLeft=t
        return
    def topLeft(self):
        return self._topLeft
    def setLabels(self,l):
        self._labels=l
        return
    def labels(self):
        return self._labels
    def setSurface(self,s):
        self._surface=s
        return
    def surface(self):
        return self._surface
    def setSelected(self,l):
        self._selected=l
        return
    def selected(self):
        return self._selected
