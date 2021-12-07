import math
from . import global_variables
import pygame
from . import primitives

import time
import random

class hscrollbar():
    def setRect(self,r):
        self._rect=r
        return
    def rect(self):
        return self._rect
    def __init__(self,surface, function, topleft, length_of_bar_in_pixel, range_of_values, range_seen = None, start_position = 0, function_parameter=None):
        """
        Draws a scroll bar
        
        length_of_bar_in_pixel       An integer with the length of the bar in pixels
        range_of_values              A tuple giving the values at each end of the bar
        range_seen                   Optional integer giving how much of the range_of_values is seen at a given time (eg. the number
                                        of entries in a scrolled list visible). Default to None, which is equal to a square
                                        slider (for time-settings etc).
        
        
        """ 
        if not isinstance(length_of_bar_in_pixel, int):
            raise Exception("length_of_bar_in_pixel must be an integer")

        if not isinstance(range_of_values, tuple):
            raise Exception("range_of_values must be a tuple")

        if len(range_of_values) != 2:
            raise Exception("range_of_values must be a tuple of length 2")
        
        if range_of_values[1] < range_of_values[0]:
            raise Exception("the first entry in range_of_values must be smaller than the second: " + str(range_of_values))
        
        if range_of_values[0] < 0 or range_of_values[1] < 0:
            raise Exception("range_of_values cannot contain negative entries: " + str(range_of_values))
        
        if not (isinstance(range_of_values[0], int) or isinstance(range_of_values[0], int)): 
            raise Exception("range_of_values[0] must be an integer. It was " + str(range_of_values[0]))
        
        if not (isinstance(range_of_values[1], int) or isinstance(range_of_values[1], int)):
            raise Exception("range_of_values[1] must be an integer. It was " + str(range_of_values[1]))
        
        if start_position < range_of_values[0] or start_position > range_of_values[1]:
            raise Exception("start position must be within the range_of_values. It was " + str(start_position) + " and range_of_values were: " + str(range_of_values))
        
        if range_of_values[1] - range_of_values[0] <= 0:
            self.unmovable = True
        else:
            self.unmovable = False
        
        if range_seen is not None:
            if not isinstance(range_seen, int):
                raise Exception("if given, range_seen must be an integer")

            if range_seen <= 0:
                raise Exception("if given, range_seen must be above zero")
        
            if range_seen > (range_of_values[1] - range_of_values[0]):
                self.unmovable = True
        



        #        
        self.surface = surface
        self.topleft = topleft
        self.length_of_bar_in_pixel = length_of_bar_in_pixel
        self.range_of_values = range_of_values
        self.range_seen = range_seen
        self.width = 20
        self.function = function
        self.function_parameter = function_parameter
        self.position = start_position
        
        self.setRect(pygame.Rect(self.topleft[0],self.topleft[1],self.length_of_bar_in_pixel,self.width))

        
        self.draw()
        

    def calculate_extent_of_slider(self):
        """
        Function that calculates at what points (in pixels) the slider should be based on the self.position, self.range_of_values,
        self.step_size and self.length_of_bar_in_pixels.
        Returns a length-two tuple with the start and end in pixel measured from topleft
        """
        if not self.unmovable:
            if self.range_seen is None:  
                #the simple case with a square slider. First calculate the operating-space (ie. all except end-arrows and space for the actual slider
                operational_length = self.length_of_bar_in_pixel - 3 * self.width
                #the fraction of the operational space at which the start of the slider is (as given in self.position)
                percentage_position = float(self.position - self.range_of_values[0]) / float(self.range_of_values[1] - self.range_of_values[0])
                
                start_of_slider = int(percentage_position * operational_length) + self.width
                
                return (start_of_slider, start_of_slider + self.width)
                
                
            else: #for scrolledlist etc.  
                #the more complicated case with a variable length slider. First calculate the operating-space (ie. all except end-arrows and space for the actual slider
                operational_length_without_slider = self.length_of_bar_in_pixel - 2 * self.width
                percentage_taken_by_slider = float(self.range_seen) / float(self.range_of_values[1] - self.range_of_values[0])
                length_of_slider = int(operational_length_without_slider * percentage_taken_by_slider)
                operational_length = operational_length_without_slider - length_of_slider
                #the fraction of the operational space at which the start of the slider is (as given in self.position)
                percentage_position = float(self.position - self.range_of_values[0]) / float(self.range_of_values[1] - self.range_of_values[0])
                start_of_slider = int(percentage_position * operational_length) + self.width
                return (start_of_slider, start_of_slider + length_of_slider)
        else: #if unmovable
            return (self.width, self.length_of_bar_in_pixel - self.width)
        
        
    
    def draw(self):
        #draw frame
        r=self.rect()
        pygame.draw.rect(self.surface,(212,212,212),r)
        pygame.draw.rect(self.surface,(0,0,0),r,1)
        
        #draw slider
        extent_of_slider = self.calculate_extent_of_slider()
        pygame.draw.line(self.surface,(255,255,255),(self.topleft[0] + extent_of_slider[0], self.topleft[1] + 2), (self.topleft[0] + extent_of_slider[0], self.topleft[1] + self.width - 2),2) #vertical white
        pygame.draw.line(self.surface,(255,255,255),(self.topleft[0] + extent_of_slider[0], self.topleft[1] + 2), (self.topleft[0]+ extent_of_slider[1] - 2, self.topleft[1] + 2),2) #horizontal white
        pygame.draw.line(self.surface,(0,0,0),(self.topleft[0] + extent_of_slider[1] - 2, self.topleft[1] + 2), (self.topleft[0] + extent_of_slider[1] - 2, self.topleft[1] + self.width - 2),2) #vertical black
        pygame.draw.line(self.surface,(0,0,0),(self.topleft[0] + extent_of_slider[0], self.topleft[1] + self.width - 2), (self.topleft[0] + extent_of_slider[1] - 2, self.topleft[1] + self.width - 2),2) #horizontal black
        
        
        #draw left-arrow
        pygame.draw.line(self.surface,(255,255,255),(self.topleft[0] + 2, self.topleft[1] + 2), (self.topleft[0] + 2, self.topleft[1] + self.width - 2),2) #vertical white
        pygame.draw.line(self.surface,(255,255,255),(self.topleft[0] + 2, self.topleft[1] + 2), (self.topleft[0] + self.width - 2, self.topleft[1] + 2),2) #horizontal white
        pygame.draw.line(self.surface,(0,0,0),(self.topleft[0] + self.width - 2, self.topleft[1] + 2), (self.topleft[0] + self.width - 2, self.topleft[1] + self.width - 2),2) #vertical black
        pygame.draw.line(self.surface,(0,0,0),(self.topleft[0] + 2, self.topleft[1] + self.width - 2), (self.topleft[0] + self.width - 2, self.topleft[1] + self.width - 2),2) #horizontal black
        pygame.draw.polygon(self.surface, (0,0,0), [ (self.topleft[0] + 6, self.topleft[1] + self.width/2), (self.topleft[0] + 12, self.topleft[1] + 5), (self.topleft[0] + 12, self.topleft[1] - 5 + self.width)])
        
        
        #draw right-arrow
        pygame.draw.line(self.surface,(255,255,255),(self.topleft[0] + self.length_of_bar_in_pixel - self.width + 2, self.topleft[1] + 2), (self.topleft[0] - 2 + self.length_of_bar_in_pixel, self.topleft[1] + 2),2) #horizontal white
        pygame.draw.line(self.surface,(255,255,255),(self.topleft[0] + self.length_of_bar_in_pixel + 2 - self.width, self.topleft[1] + 2), (self.topleft[0] + self.length_of_bar_in_pixel + 2 - self.width, self.topleft[1] - 2 + self.width),2) #vertical white
        pygame.draw.line(self.surface,(0,0,0),(self.topleft[0] + self.length_of_bar_in_pixel - self.width + 2, self.topleft[1] - 2 + self.width), (self.topleft[0] - 2 + self.length_of_bar_in_pixel, self.topleft[1] - 2 + self.width),2) #horizontal black
        pygame.draw.line(self.surface,(0,0,0),(self.topleft[0] + self.length_of_bar_in_pixel - 2, self.topleft[1] + 2), (self.topleft[0] + self.length_of_bar_in_pixel - 2, self.topleft[1] - 2 + self.width),2) #vertical black
        pygame.draw.polygon(self.surface, (0,0,0), [ (self.topleft[0] + self.length_of_bar_in_pixel - 6, self.topleft[1] + self.width/2), (self.topleft[0] + self.length_of_bar_in_pixel - 12, self.topleft[1] + 5), (self.topleft[0] + self.length_of_bar_in_pixel - 12, self.topleft[1] - 5 + self.width)])
        
        pygame.display.flip()
        

    def activate(self, pos):
        """
        Will distribute a click according to if it is on the slider or on the arrows. For now, no mouse-down sliding of sliders :-(
        """
        if not self.unmovable:

            if pos[0] - self.topleft[0] < self.width: #up-arrow
                if self.range_seen is None:
                    if self.position > self.range_of_values[0]:
                        self.position = self.position - 1
                else:
                    if self.position - self.range_seen > self.range_of_values[0]:
                        self.position = self.position - self.range_seen
                    else:
                        self.position = self.range_of_values[0]
                
            elif pos[0] - self.topleft[0] > self.length_of_bar_in_pixel - self.width: #down-arrow
                if self.range_seen is None:
                    if self.position < self.range_of_values[1]:
                        self.position = self.position + 1
                else:
                    if self.position + self.range_seen < self.range_of_values[1]:
                        self.position = self.position + self.range_seen
                    else:
                        self.position = self.range_of_values[1]
            else:
                operational_space = self.length_of_bar_in_pixel - 2 * self.width
                percentage_pos = (pos[0] - self.topleft[0] - self.width) / float(operational_space)
                self.position = int((self.range_of_values[1] - self.range_of_values[0]) * percentage_pos) + self.range_of_values[0]
            
            self.draw()
            self.function(self.position,self.function_parameter)
            
            





