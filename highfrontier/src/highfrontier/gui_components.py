import math
#from ocempgui.widgets.Constants import *
#from ocempgui.object import BaseObject
#from ocempgui.widgets import *
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
            if event.unicode == "\x08":
                self.text = self.text[0:(len(self.text)-1)]
                self.draw()
#            elif event.key == 13:
#                print "enter"
#                return "enter"
            else:
                if self.restrict_input_to is not None:
                    if event.unicode not in self.restrict_input_to:
                        return 
                if len(self.text) < self.max_letters:
                    self.text = self.text + event.unicode
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
        
        
        




class vscrollbar():
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
            raise Exception("the first entry in range_of_values must be smaller than the second")
        
        if range_of_values[0] < 0 or range_of_values[1] < 0:
            raise Exception("range_of_values cannot contain negative entries")
        
        if not isinstance(range_of_values[0], int): 
            raise Exception("range_of_values[0] must be an integer")
        
        if not isinstance(range_of_values[1], int):
            raise Exception("range_of_values[0] must be an integer")
        
        if start_position < range_of_values[0] or start_position > range_of_values[1]:
            raise Exception("start position must be within the range_of_values")
        
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
        
        self.rect = pygame.Rect(self.topleft[0],self.topleft[1],self.width,self.length_of_bar_in_pixel)
#        print self.calculate_extent_of_slider()
        
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
        pygame.draw.rect(self.surface,(212,212,212),self.rect)
        pygame.draw.rect(self.surface,(0,0,0),self.rect,1)
        
        #draw slider
        extent_of_slider = self.calculate_extent_of_slider()
        pygame.draw.line(self.surface,(255,255,255),(self.topleft[0] + 2, self.topleft[1] + extent_of_slider[0]), (self.topleft[0] + 2, self.topleft[1] + extent_of_slider[1]),2) #vertical
        pygame.draw.line(self.surface,(255,255,255),(self.topleft[0] + 2, self.topleft[1] + extent_of_slider[0]), (self.topleft[0] + self.width - 2, self.topleft[1] + extent_of_slider[0]),2) #horizontal
        pygame.draw.line(self.surface,(0,0,0),(self.topleft[0] + self.width - 2, self.topleft[1] + extent_of_slider[0]), (self.topleft[0] + self.width - 2, self.topleft[1] + extent_of_slider[1]),2) #vertical
        pygame.draw.line(self.surface,(0,0,0),(self.topleft[0], self.topleft[1] + extent_of_slider[1]), (self.topleft[0] + self.width - 2, self.topleft[1] + extent_of_slider[1]),2) #horizontal
        
        
        #draw up-arrow
        pygame.draw.line(self.surface,(255,255,255),(self.topleft[0] + 2, self.topleft[1] + 2), (self.topleft[0] + 2, self.topleft[1] + self.width - 2),2) #vertical white
        pygame.draw.line(self.surface,(255,255,255),(self.topleft[0] + 2, self.topleft[1] + 2), (self.topleft[0] + self.width - 2, self.topleft[1] + 2),2) #horizontal white
        pygame.draw.line(self.surface,(0,0,0),(self.topleft[0] + self.width - 2, self.topleft[1] + 2), (self.topleft[0] + self.width - 2, self.topleft[1] + self.width - 2),2) #vertical black
        pygame.draw.line(self.surface,(0,0,0),(self.topleft[0] + 2, self.topleft[1] + self.width - 2), (self.topleft[0] + self.width - 2, self.topleft[1] + self.width - 2),2) #horizontal black
        pygame.draw.polygon(self.surface, (0,0,0), [ (self.topleft[0] + self.width /2, self.topleft[1] + 6), (self.topleft[0] + 5, self.topleft[1] + 12), (self.topleft[0] + self.width - 5, self.topleft[1] +12)])

        #draw down-arrow
        pygame.draw.line(self.surface,(255,255,255),(self.topleft[0] + 2, self.topleft[1] + 2 + self.length_of_bar_in_pixel - self.width), (self.topleft[0] + 2, self.topleft[1] + self.length_of_bar_in_pixel - 2),2) #vertical white
        pygame.draw.line(self.surface,(255,255,255),(self.topleft[0] + 2, self.topleft[1] + 2 + self.length_of_bar_in_pixel - self.width), (self.topleft[0] + self.width - 2, self.topleft[1] + 2 + self.length_of_bar_in_pixel - self.width),2) #horizontal white
        pygame.draw.line(self.surface,(0,0,0),(self.topleft[0] + self.width - 2, self.topleft[1] + 2 + self.length_of_bar_in_pixel - self.width), (self.topleft[0] + self.width - 2, self.topleft[1] + self.length_of_bar_in_pixel - 2),2) #vertical black
        pygame.draw.line(self.surface,(0,0,0),(self.topleft[0] + 2, self.topleft[1] + self.length_of_bar_in_pixel - 2), (self.topleft[0] + self.width - 2, self.topleft[1] + self.length_of_bar_in_pixel - 2),2) #horizontal black
        pygame.draw.polygon(self.surface, (0,0,0), [ (self.topleft[0] + self.width/2, self.topleft[1] - 6 + self.length_of_bar_in_pixel), (self.topleft[0] + 5, self.topleft[1] - 12 + self.length_of_bar_in_pixel), (self.topleft[0] + self.width - 5, self.topleft[1] - 12 + self.length_of_bar_in_pixel)])
        
        pygame.display.flip()
    
    def receive_click(self, event):
        self.activate(event.pos)

    def activate(self, pos):
        """
        Will distribute a click according to if it is on the slider or on the arrows. For now, no mouse-down sliding of sliders :-(
        """
        if not self.unmovable:
            if pos[1] - self.topleft[1] < self.width: #up-arrow
                if self.range_seen is None:
                    if self.position > self.range_of_values[0]:
                        self.position = self.position - 1
                else:
                    if self.position - self.range_seen > self.range_of_values[0]:
                        self.position = self.position - self.range_seen
                    else:
                        self.position = self.range_of_values[0]
                
            elif pos[1] - self.topleft[1] > self.length_of_bar_in_pixel - self.width: #down-arrow
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
                percentage_pos = (pos[1] - self.topleft[1] - self.width) / float(operational_space)
                self.position = int((self.range_of_values[1] - self.range_of_values[0]) * percentage_pos) + self.range_of_values[0]
            
            self.draw()
            self.function(self.position,self.function_parameter)
        
            






class hscrollbar():
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
            raise Exception("the first entry in range_of_values must be smaller than the second")
        
        if range_of_values[0] < 0 or range_of_values[1] < 0:
            raise Exception("range_of_values cannot contain negative entries")
        
        if not isinstance(range_of_values[0], int): 
            raise Exception("range_of_values[0] must be an integer")
        
        if not isinstance(range_of_values[1], int):
            raise Exception("range_of_values[0] must be an integer")
        
        if start_position < range_of_values[0] or start_position > range_of_values[1]:
            raise Exception("start position must be within the range_of_values")
        
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
        
        self.rect = pygame.Rect(self.topleft[0],self.topleft[1],self.length_of_bar_in_pixel,self.width)

        
        self.draw()
        

    def calculate_extent_of_slider(self):
        """
        Function that calculates at what points (in pixels) the slider should be based on the self.position, self.range_of_values,
        self.step_size and self.length_of_bar_in_pixels.
        Returns a length-two tuple with the start and end in pixel measured from topleft
        """
        if not unmovable:
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
        pygame.draw.rect(self.surface,(212,212,212),self.rect)
        pygame.draw.rect(self.surface,(0,0,0),self.rect,1)
        
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
        



class fast_list():
    """
    A list similar to the ScrolledList, but faster
    """
    def __init__(self, surface, tabular_data, rect, column_order = None):
        self.surface = surface
      

        self.rect = rect
        self.rect_for_main_list = pygame.Rect(self.rect[0],self.rect[1] + 20,self.rect[2]-20,self.rect[3]-20)
        self.text_height = global_variables.courier_font.size("abcdefghijklmnopqrstuvxysABCDEFGHIJKLMNOPQRSTU")[1]
        self.left_list_frame = 5 # how much the text in the list is indented
        self.top_frame_width = 5 # this is a guesstimate of how much the Frame is filling
        self.title = None #either None (in which case it can't be rendered" or else a dictionary with key "text", containing a string with the text to write, and key "entry_span" containing another dictionary with the column names as values and their length in pixels as keys
        self.original_tabular_data = tabular_data
        self.receive_data(tabular_data,column_order = column_order)
        self.selected = None
        self.selected_name = None

        self.reverse_sorting = False
        self.create_fast_list()

                
#        if self.title is not None:
#            self.render_title()

        
    def create_fast_list(self):
        """
        The creation function. Doesn't return anything, but saves self.list_frame variable and renders using the self.renderer.
        Needs to have something saved to self.data first 
        """
        

        title_surface = pygame.Surface((self.rect[2],20))
        title_surface.fill((224,218,213))
        if self.title is not None:
            rendered_titleline = global_variables.courier_font.render(self.title["text"],True,(0,0,0))
            title_surface.blit(rendered_titleline,(self.left_list_frame, 0))
        self.surface.blit(title_surface,(self.rect[0],self.rect[1]))
        
        
        #expanding rectangle to catch clicks on title
#        self.rect = pygame.Rect(self.rect[0],self.rect[1] - self.text_height, self.rect[2], self.rect[3] + self.text_height)

        self.lines_visible = int( math.floor( self.rect[3] / self.text_height) )
        
        
        
        self.vscrollbar = vscrollbar(self.surface, self.scrolling, (self.rect[0] + self.rect[2] - 20, self.rect[1]), self.rect[3], (0,len(self.data)), range_seen = self.lines_visible, start_position = 0, function_parameter=None)
        self.update_fast_list()
        pygame.display.flip()
        
    def scrolling(self,position,function_parameter):
        self.update_fast_list()
    
    def receive_click(self,event):
        if event.pos[0] > self.rect[0] + self.rect[2] - 20:
            self.vscrollbar.activate(event.pos)
            pygame.display.flip()
        else:
            if self.title is not None:
                if event.pos[1] < self.rect[1] + self.text_height:
                    print "click in title"
                    for key in self.title["entry_span"].keys():
                        if key[0] < event.pos[0] and event.pos[0] < key[1]:
                            sort_by_this_column = self.title["entry_span"][key]
#                            print self.title["entry_span"][key]
#                        try: self.original_tabular_data
#                        except: raise Exception("The fast_list was supposed to have the self.orginal_tabular_data variable, but didn't")
#                        else: 
                    if self.sorted_by_this_column == sort_by_this_column:
                        self.reverse_sorting = not self.reverse_sorting
                    else:
                        self.reverse_sorting = self.reverse_sorting
                    self.receive_data(self.original_tabular_data, sort_by = sort_by_this_column , column_order = self.original_column_order, reverse_sort = self.reverse_sorting)
                    self.update_fast_list()                    
                    pygame.display.flip()
                    return


            
            index_selected = (event.pos[1] - 20 - self.rect[1] - self.top_frame_width) / self.text_height + self.interval[0]
            
#            print "clicked at relative y_pos: " + str(event.pos[1] - self.rect[1] - self.top_frame_width) + " which is index: " + str(index_selected)
            if 0 <= index_selected and index_selected < len(self.data):
                self.selected = self.data[index_selected]
                self.selected_name = self.selected.split("  ")[0]
                self.selected_name = self.selected_name.rstrip(" ")
                self.update_fast_list()
                pygame.display.flip()
        
        
    def notify(self,event):
        try: self.list_frame
        except: pass
        else:
            try: self.vscrollbar
            except: right_border = self.topleft[0] + self.list_size[0]
            else: right_border = self.topleft[0] + self.list_size[0] - self.vscrollbar.width
            
            if self.topleft[0] < event.data.pos[0] and event.data.pos[0] < right_border:
                if self.topleft[1] < event.data.pos[1] and event.data.pos[1] < self.topleft[1] + self.list_size[1]:    
                    index_selected = (event.data.pos[1] - self.topleft[1] - self.top_frame_width) / self.text_height + self.interval[0]
                    #print "clicked at relative y_pos: " + str(event.data.pos[1] - self.topleft[1] - self.top_frame_width) + " which is index: " + str(index_selected)
                    if 0 <= index_selected and index_selected < len(self.data):
                        self.selected = self.data[index_selected]
                        self.selected_name = self.selected.split("  ")[0]
                        self.selected_name = self.selected_name.rstrip(" ")
                        self.update_fast_list()
                        #print self.selected
            
                #checking to see if the click is on the titlebar
                try: self.list_frame
                except: pass
                else:
                    top_border = int(self.topleft[1] - 2 * self.text_height)
                    bottom_border = int(self.topleft[1] - self.text_height + self.top_frame_width * 2) 
                    if top_border < event.data.pos[1] and event.data.pos[1] < bottom_border:
                        horizontal_position = event.data.pos[0] - self.topleft[0]
                        for key in self.title["entry_span"].keys():
                            if key[0] < horizontal_position and horizontal_position < key[1]:
                                sort_by_this_column = self.title["entry_span"][key]
                        try: self.original_tabular_data
                        except: raise Exception("The fast_list was supposed to have the self.orginal_tabular_data variable, but didn't")
                        else: 
                            print "self.sorted_by_this_column: " + str(self.sorted_by_this_column)
                            print "sort_by_this_column: " + str(sort_by_this_column)
                            if self.sorted_by_this_column == sort_by_this_column:
                                self.reverse_sorting = not self.reverse_sorting
                            else:
                                self.reverse_sorting = self.reverse_sorting
                                
                            
                            self.receive_data(self.original_tabular_data, sort_by = sort_by_this_column , column_order = self.original_column_order, reverse_sort = self.reverse_sorting)
                              
                            self.update_fast_list()                    
                    
                        
                    
                    
                    
                    
    
    def update_fast_list(self):
        """
        Function to update the fast list. Changes the look of the surface "self.list_surface", sets it as picture in the
        self.list_surface_label and calls renderer.update. Adds scrollbar if necessary. 
        """
        if(len(set(self.data)) != len(self.data)):
            raise Exception("The fast_list contains non-unique values!")
        pygame.draw.rect(self.surface, (234,228,223), self.rect_for_main_list)
        
        
        
        #in the case where data can fit on screen
        if self.lines_visible >= len(self.data):
            self.interval = range(0,len(self.data))
            for i in range(0,len(self.data)):
                if self.data[i] == self.selected:
                    rendered_dataline = global_variables.courier_font.render(self.data[i],True,(255,0,0))
                else:
                    rendered_dataline = global_variables.courier_font.render(self.data[i],True,(0,0,0))
                
                self.surface.blit(rendered_dataline,(self.rect_for_main_list[0] + self.left_list_frame, self.rect_for_main_list[1] + i*self.text_height + self.top_frame_width))
                pygame.display.flip()
        
        #in the case where data can't fit on screen
        else:
            
            percentage_position = float(self.vscrollbar.position) / float(self.vscrollbar.range_of_values[1] - self.vscrollbar.range_of_values[0])
            per_entry_position = int(percentage_position * (len(self.data)-self.lines_visible))
            self.interval = range(int(per_entry_position),int(per_entry_position) + self.lines_visible)
            for j, i in enumerate(self.interval):
                if self.data[i] == self.selected:
                    rendered_dataline = global_variables.courier_font.render(self.data[i],True,(255,0,0))
                else:
                    rendered_dataline = global_variables.courier_font.render(self.data[i],True,(0,0,0))
                self.surface.blit(rendered_dataline,(self.rect_for_main_list[0] + self.left_list_frame, self.rect_for_main_list[1] + j*self.text_height + self.top_frame_width))

        
        
                
        
    





#
#    def render_title(self):
#        """
#        Function that will check if the fast_list has a self.title entry, and in that case
#        render it in a separate frame just above the main list
#        """
#        title_surface = pygame.Surface((self.rect[2],self.text_height))
#        title_surface.fill((234,228,223))
#        rendered_titleline = global_variables.courier_font.render(self.title["text"],True,(0,0,0))
#        title_surface.blit(rendered_titleline,(self.left_list_frame, 0))
#        
#        self.surface.blit(title_surface,(self.rect[0],self.rect[1]-self.text_height))
#        
#        pygame.display.flip()
#
#        #expanding rectangle to catch clicks on title
#        self.rect = pygame.Rect(self.rect[0],self.rect[1] - self.text_height, self.rect[2], self.rect[3] + self.text_height)





    def receive_data(self,data,sort_by="rownames",column_order=None,reverse_sort=False):
        """
        Function that takes tabular data either of the form imported by primitives.import_datasheet (a dictionary with rows as keys and values 
        being another dictionary were colums are keys and values are data entries) or else as a simple list.
        This is then saved in self.data as a regular list, with the data in flattened and sorted form.
        The first line of the data is the title
        Optional arguments:
            sort_by    A string .If given the table will be sorted by this column name. Defaults to sorting by row-title name
            column_order     a list. If given the columns will appear in this order. Use 'rownames' to refer to the rownames. Omitted entries will not be in the list.
        """
        
        if isinstance(data,list):
            self.data = data
        elif isinstance(data,dict):
            if data == {}:
                self.data = []
                self.title = {}
                self.title["text"] = ""
                self.title["entry_span"] = {}
            else:
                #checking that the column_order is correct
                collection = []
                self.original_tabular_data = data
                self.sorted_by_this_column = sort_by
                self.original_column_order = column_order
                try: data[data.keys()[0]].keys()
                except:
                    print data
                    raise Exception("The data given to fast_list did not follow standards. It has been printed above")
                original_columns = ["rownames"] + data[data.keys()[0]].keys()
                if column_order is None:
                    column_order = original_columns 
                else:
                    for column_name in column_order:
                        if column_name not in original_columns:
                            raise Exception("Received a column_order entry that was not located in data columns")
                
                
                #determining the max number of letters in each column
                max_letters_per_column = {"rownames":0}
                for column_name in column_order:
                    max_letters_per_column[column_name] = 0
                for row in data:
                    for column_name in column_order:
                        if column_name == "rownames":
                            entry = str(row)
                        else:
                            entry = data[row][column_name]
                        if isinstance(entry,int) or isinstance(entry,long) or isinstance(entry,float):
                            entry_length = 13 
                        else:
                            entry_length = len(str(entry))
                        max_letters_per_column[column_name] = max(max_letters_per_column[column_name],entry_length)
                for column_name in column_order:
                    max_letters_per_column[column_name] = max(max_letters_per_column[column_name],len(column_name))
                for max_letters_per_column_entry in max_letters_per_column:
                    max_letters_per_column[max_letters_per_column_entry] = max_letters_per_column[max_letters_per_column_entry] + 2
                
                
                #sorting the rows according to sort_by
                if sort_by not in column_order:
                    print column_order
                    raise Exception("The sort_by variable was not found in the column_order. Remember the rownames must also be present if needed") 
                if sort_by == "rownames":
                    sorting_list = data.keys()
                    sorting_list.sort()
                else:
                    temp_dict = {}
                    
                    #from http://mail.python.org/pipermail/python-list/2002-May/146190.html - thanks xtian
                    for row in data:
                        temp_dict[row] = data[row][sort_by]
                    def sorter(x, y):
                        return cmp(x[1],y[1])
            
                    i = temp_dict.items()
                    i.sort(sorter)
                    sorting_list = []
                    for i_entry in i:
                        sorting_list.append(i_entry[0])
                
                
                if reverse_sort:
                    sorting_list.reverse()
        
        
                
                
                for rowname in sorting_list:
                    rowstring = ""
                    for column_entry in column_order:
                        if column_entry == "rownames":
                            data_point_here = rowname
                        else:
                            data_point_here = data[rowname][column_entry]
                        
                        if isinstance(data_point_here,int) or isinstance(data_point_here,long) or isinstance(data_point_here,float):
                            if isinstance(data_point_here,float):
                                if abs(data_point_here) > 1000:
                                    data_point_here = int(data_point_here)
                                else:
                                    data_point_here = "%.4g" % data_point_here
                            
                            if isinstance(data_point_here,int) or isinstance(data_point_here,long):
                                if abs(data_point_here) > 1000*1000*1000*1000*1000*3:
                                    data_point_here = "%.4g" % data_point_here
                                elif abs(data_point_here) > 1000*1000*1000*1000*3:
                                    data_point_here = str(int(data_point_here / (1000*1000*1000*1000) )) + " trillion"
                                elif abs(data_point_here) > 1000*1000*1000*3:
                                    data_point_here = str(int(data_point_here / (1000*1000*1000) )) + " billion"
                                elif abs(data_point_here) > 1000*1000*3:
                                    data_point_here = str(int(data_point_here / (1000*1000) )) + " million"
                                elif abs(data_point_here) > 1000*3:
                                    data_point_here = str(int(data_point_here / 1000)) + " thousand"
                                else:
                                    data_point_here = str(data_point_here)
                                
                            #data_point_here = "%.3g" % data_point_here
                        else:
                            data_point_here = str(data_point_here)
                            
                            
                        seperator = "                                                                "        
            
                        seperator = seperator[0:(max_letters_per_column[column_entry] - len(data_point_here))]
                            
                        rowstring = rowstring + data_point_here + seperator
                    collection.append(rowstring)
                
                
                #creating title 
                #a dictionary with key "text", containing a string with the text to write, and key "entry_span" containing another 
                #dictionary with the column names as values and their length in pixels as keys
                self.title = {}
                self.title["text"] = ""
                self.title["entry_span"] = {}
                entry_end = 5 #FIXME?
                for column_entry in column_order:
                    if column_entry == "rownames":
                        column_title = ""
                    else:
                        column_title = column_entry
                        
                    seperator = "                                                                "        
                    seperator = seperator[0:(max_letters_per_column[column_entry] - len(column_title))]
                    
                    
                    entry_start = entry_end 
                    entry_end = global_variables.courier_font.size(column_title + seperator)[0] + entry_start
                    self.title["entry_span"][(entry_start,entry_end)] = column_entry
                    
        #            
                    self.title["text"] = self.title["text"] + column_title + seperator
                
                self.data = collection
    
            
        else:
            print data
            raise Exception("The data passed to the fast_list was not recognised")
    
    
    
    
    
    
    









#import random
#from ocempgui.widgets import *
#from ocempgui.events import EventManager
#re = Renderer()
##input = ["one test line","another test line","yet another test line","even one more test line","an extremely long line that is way too long and perhaps should give a warning"]
##input_long = []
##for i in range(0,23):
##    realwords = input[random.randint(0,len(input)-1)]
##    input_long.append(realwords + " " + str(random.randint(1,10000)))  
#
#
#
#
#
#fast_list_instance = fast_list(re)
#fast_list_instance.title={}
##fast_list_instance.title["text"] = "Test1 test2 test3 test4"
##fast_list_instance.title["entry_span"] = {(5,30):"Test1",(30,70):"test2",(70,160):"test3",(160,250):"test4"}
##fast_list_instance.data = input_long
#
#
#import os
#data_file_name = os.path.join("data","economy","trade resources.txt")
#trade_resources = primitives.import_datasheet(data_file_name)
#fast_list_instance.listify_tabular_data(trade_resources)
#
##print trade_resources
#
#fast_list_instance.create_fast_list()
#fast_list_instance.render_title()
#
#
##print fast_list_instance.title
#re.create_screen (800, 600)
#re.title = "Window examples"
#re.color = (234, 228, 223)
#
#re.start ()
#

