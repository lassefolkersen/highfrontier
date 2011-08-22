import pygame
from pygame.locals import *
import widget

pygame.init()
s=pygame.display.set_mode((640,480))
w=widget.widget(None,(0,0))
w.setSize((640,480))
w.show()
v=widget.widget(w,(32,24))
v.setSize((100,100))
v.setColor((255,255,255))
w.show()

qc=False
while(not qc):
    events=pygame.event.get()
    for event in events:
        if(event.type==QUIT):
            qc=True
        if(event.type in [MOUSEMOTION,MOUSEBUTTONUP,MOUSEBUTTONDOWN]):
            p=event.pos
            r=w.screenRect()
            if(r.collidepoint(p)):
                w.mouseEvent(event)
        if(event.type in [KEYDOWN,KEYUP]):
            """ only one toplevel widget """
            w.keyboardEvent(event)
    w.draw(s)
    pygame.display.flip()
