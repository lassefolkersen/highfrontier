from . import fast_list
from . import merchant
import os
from . import global_variables
import sys
import string
import pygame
import datetime
import math
from . import company
from . import primitives
import random
import time


class company_financial_info():
    """
    Subview of the company view. Shows a graph of the capital of the company as it has been over the past years. 
    """


    def __init__(self,solar_system_object,action_surface):
        self.solar_system_object_link = solar_system_object
        self.rect = pygame.Rect(50,50,700,500)
        self.action_surface = action_surface
        self.frame_size = 80



    def create(self):
        """
        The creation function.  
        """
        
        company_selected = self.solar_system_object_link.company_selected
        company_accounting = company_selected.company_accounting

        blank_surface = pygame.Surface((self.rect[2], self.rect[3]))
        blank_surface.fill((150,150,150))
#        pygame.draw.rect(self.action_surface, (0,0,0), self.rect, 2)
        pygame.draw.line(blank_surface, (255,255,255), (0, 0), (self.rect[2], 0))
        pygame.draw.line(blank_surface, (255,255,255), (0, 0), (0, self.rect[3]))
        pygame.draw.line(blank_surface, (0,0,0), (self.rect[2], 0), (self.rect[2], self.rect[3]))
        pygame.draw.line(blank_surface, (0,0,0), (0, self.rect[3]), (self.rect[2], self.rect[3]))
  
        
        if len(company_selected.company_accounting) == 0:
            no_history_label = global_variables.standard_font.render("No history for " + company_selected.name,True,(0,0,0))
            blank_surface.blit(no_history_label,(20,20))
        else:
            start_date = company_accounting[0]["date"]
            end_date = company_accounting[len(company_accounting)-1]["date"]
            relative_numeric_start_date = (start_date - self.solar_system_object_link.start_date).days
            relative_numeric_end_date = (end_date - self.solar_system_object_link.start_date).days
            
            dates = []
            capital = []
            for account_report in company_accounting:
                dates.append((account_report["date"] - self.solar_system_object_link.start_date).days)
                capital.append(account_report["capital"])
                
            xlim = (min(dates),max(dates))
            ylim = (0,max(capital))
            if ylim[0] == ylim[1]:
                ylim = (ylim[0]-1,ylim[1]+1)
            if xlim[0] == xlim[1]:
                xlim = (xlim[0]-1,xlim[1]+1)
            
            
            blank_surface = primitives.make_linear_y_axis(blank_surface, self.frame_size, ylim, solar_system_object_link=self.solar_system_object_link, unit = "capital")
            blank_surface = primitives.make_linear_x_axis(blank_surface,self.frame_size,xlim, solar_system_object_link=self.solar_system_object_link, unit="date")
#            print "(self.graph_rect[2]-self.frame_size*2): " + str((self.graph_rect[2]-self.frame_size*2))
            for i in range(1,len(capital)):
                x1_position = int(self.frame_size + ((self.rect[2]-self.frame_size*2) * (dates[i-1] - xlim[0])) / (xlim[1]-xlim[0]))
                y1_position = int(self.rect[3] - (self.frame_size + ( (self.rect[3]-self.frame_size*2) * (capital[i-1] - ylim[0]) / (ylim[1]-ylim[0]) )))
                x2_position = int(self.frame_size + ((self.rect[2]-self.frame_size*2) * (dates[i] - xlim[0])) / (xlim[1]-xlim[0]))
                y2_position = int(self.rect[3] - (self.frame_size + ( (self.rect[3]-self.frame_size*2) * (capital[i] - ylim[0]) / (ylim[1]-ylim[0]) )))
#                print "From (" + str(x1_position) + "," + str(y1_position) + ") to (" + str(x2_position) + "," +str(y2_position) + ") - the date was: " + str(dates[i]) + " and the capital was " + str(capital[i])
                
                pygame.draw.line(blank_surface,(0,0,0),(x1_position,y1_position),(x2_position,y2_position))
        
        
        self.action_surface.blit(blank_surface,(self.rect[0],self.rect[1]))
        pygame.display.flip()



    def receive_click(self,event):
        if self.solar_system_object_link.message_printing["debugging"]:
            print_dict = {"text":"Nothing should happen now in company_financial_info","type":"debugging"} 
            self.solar_system_object_link.messages.append(print_dict)

