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

class navigation_window():
    """
    The navigation window. Is controlled by a togglebutton in the commandbox. When visible it can be used for zooming and rotating.
    """
    def __init__(self,solar_system_object,action_surface):
        self.solar_system_object_link = solar_system_object
        self.rect = pygame.Rect(500,50,190,170)
        self.action_surface = action_surface



    def zoom_in(self,label,function_parameter):
        return "zoom_in"

    def zoom_out(self,label,function_parameter):
        return "zoom_out"

    def rotate_west(self,label,function_parameter):
        return "go_west"

    def rotate_east(self,label,function_parameter):
        return "go_east"

    def rotate_south(self,label,function_parameter):
        return "go_south"

    def rotate_north(self,label,function_parameter):
        return "go_north"


    def receive_click(self,event):
        if pygame.Rect(self.rect[0] + 70, self.rect[1] + 10, 50, 30).collidepoint(event.pos) == 1:
            return self.button_north.activate(event.pos)
        if pygame.Rect(self.rect[0] + 20, self.rect[1] + 40, 50, 30).collidepoint(event.pos) == 1:
            return self.button_west.activate(event.pos)
        if pygame.Rect(self.rect[0] + 70, self.rect[1] + 70, 50, 30).collidepoint(event.pos) == 1:
            return self.button_south.activate(event.pos)
        if pygame.Rect(self.rect[0] + 120, self.rect[1] + 40, 50, 30).collidepoint(event.pos) == 1:
            return self.button_east.activate(event.pos)


        if pygame.Rect(self.rect[0] + 10, self.rect[1] + 120, 80, 30).collidepoint(event.pos) == 1:
            return self.button_zoom_in.activate(event.pos)
        if pygame.Rect(self.rect[0] + 100, self.rect[1] + 120, 80, 30).collidepoint(event.pos) == 1:
            return self.button_zoom_out.activate(event.pos)



    def create(self):
        """
        The creation function.
        """

        pygame.draw.rect(self.action_surface, (212,212,212), self.rect)
        pygame.draw.rect(self.action_surface, (0,0,0), self.rect, 2)
        pygame.draw.line(self.action_surface, (255,255,255), (self.rect[0], self.rect[1]), (self.rect[0] + self.rect[2], self.rect[1]))
        pygame.draw.line(self.action_surface, (255,255,255), (self.rect[0], self.rect[1]), (self.rect[0], self.rect[1] + self.rect[3]))

        self.button_north = button.button("N", self.action_surface, self.rotate_north, topleft = (self.rect[0] + 70, self.rect[1] + 10),fixed_size = (50,30))
        self.button_west = button.button("W", self.action_surface, self.rotate_west, topleft = (self.rect[0] + 20, self.rect[1] + 40),fixed_size = (50,30))
        self.button_south = button.button("S", self.action_surface, self.rotate_south, topleft = (self.rect[0] + 70, self.rect[1] + 70),fixed_size = (50,30))
        self.button_east = button.button("E", self.action_surface, self.rotate_east, topleft = (self.rect[0] + 120, self.rect[1] + 40),fixed_size = (50,30))

        self.button_zoom_in = button.button("Zoom in", self.action_surface, self.zoom_in, topleft = (self.rect[0] + 10, self.rect[1] + 120),fixed_size = (80,30))
        self.button_zoom_out = button.button("Zoom out", self.action_surface, self.zoom_out, topleft = (self.rect[0] + 100, self.rect[1] + 120),fixed_size = (80,30))



