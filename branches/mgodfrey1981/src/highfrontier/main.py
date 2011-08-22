from datetime import datetime
import pygame
from pygame.locals import *
import time
import os, sys
import planet
import company
import solarsystem
import datetime
import primitives
import global_variables
import gui
import random
reload(sys)
if hasattr(sys,"setdefaultencoding"):
    sys.setdefaultencoding("latin-1")

class Game:
    def handleEvent(self,event):
        """handle a single event"""
        if event.type == QUIT: 
            sys.exit(0)
        if event.type == 5: #mouse down event
            self.gui().receive_click(event)
            pygame.display.flip()
        if event.type == 2: #key down event
            if(self.gui().receive_text(event)):
                return True # consume event if there's a textbox
            if event.key == 280: #pgup
                self.gui().zoom_in(event)
            if event.key == 281: #pgdown
                self.gui().zoom_out(event)
            if event.key == 276: #left
                self.gui().go_left(event)
            if event.key == 275: #right
                self.gui().go_right(event)
            if event.key == 273: #up
                self.gui().go_up(event)
            if event.key == 274: #down
                self.gui().go_down(event)
            pygame.display.flip()
        return
    def start_loop(self,companyName = None, companyCapital = None, loadPreviousGame = None):
        """
        companyName          string of a company that will play as current player. If none, 
        the game will run in simulation mode
                             
        companyCapital       int with the starting capital of the newly started company.

        loadPreviousGame    filename of a save game that can be loaded
        """
        #initilizing screen stuff
        window_size = global_variables.window_size
        pygame.init()
        if global_variables.fullscreen:
            window = pygame.display.set_mode(window_size,FULLSCREEN) 
        else:
            window = pygame.display.set_mode(window_size)
        icon = pygame.image.load(os.path.join("images","window_icon.png"))
        pygame.display.set_icon(icon) 
        pygame.mouse.set_cursor(*pygame.cursors.arrow)
        #initializing the world - depends on if a previous game should be loaded
        if loadPreviousGame is not None:
            self.setSol(solarsystem.solarsystem(global_variables.start_date, de_novo_initialization = False))
            self.sol().load_solar_system(loadPreviousGame)
        else:
            self.setSol(solarsystem.solarsystem(global_variables.start_date, de_novo_initialization = True))
        #initialize current player company
        if companyName is not None:
            if self.sol().current_player is not None:
                raise Exception("The loaded solar system already had a current player")
            automation_dict = {
                "Demand bidding (initiate buying bids)":False,
                "Supply bidding (initiate selling bids)":False,
                "Asset market (buy bases and firms)":False,
                "Commodities market (start commodity producing firms)":False,
                "Tech market (buy and sell technology)":False,
                "Transport market (start up merchant firms)":False,
                "Evaluate firms (close problematic firms)":False,
                "Start research firms":False,
                "Pick research (pick research automatically)":False,
                "Expand area of operation (search for new home cities)":False
                }
            if companyName in self.sol().companies.keys():
                self.sol().current_player = self.sol().companies[companyName]
                self.sol().current_player.automation_dict = automation_dict
                self.sol().current_player.automation_dict["Demand bidding (initiate buying bids)"] = True
                self.sol().current_player.automation_dict["Supply bidding (initiate selling bids)"] = True
                self.sol().current_player.capital = companyCapital
            else:
                model_companyName = random.choice(self.sol().companies.keys())
                model_company = self.sol().companies[model_companyName]
                new_company = company.company(self.sol(),
                                              model_company.company_database,
                                              deviation=5,
                                              companyName=companyName,
                                              capital=companyCapital)
                self.sol().companies[companyName] = new_company
                new_company.automation_dict = automation_dict
                self.sol().current_player = new_company
        #loading planets that are often used:
        print "loading earth"
        self.sol().planets["earth"].pickle_all_projections()
        print "finished loading"
        #divide the surface in action and non-action
        action_rect = pygame.Rect(0,0,global_variables.window_size[0] - 150, global_variables.window_size[1] - 100)
        right_side_rect = pygame.Rect(global_variables.window_size[0] - 150, 0, 150, global_variables.window_size[1])
        message_rect = pygame.Rect(10,global_variables.window_size[1] - 100, global_variables.window_size[0] - 170, 100)
        action_surface = window.subsurface(action_rect)
        right_side_surface = window.subsurface(right_side_rect)
        message_surface = window.subsurface(message_rect)
        #switch to determine planetary mode or solarsystem mode from beginning
        mode_before_change = self.sol().display_mode 
        if self.sol().display_mode == "solar_system":
            surface = self.sol().draw_solar_system(zoom_level=self.sol().solar_system_zoom,
                                                   date_variable=self.sol().current_date,
                                                   center_object=self.sol().current_planet.planet_name)
        if self.sol().display_mode == "planetary":
            self.sol().current_planet = self.sol().planets["earth"]
            surface = self.sol().current_planet.draw_entire_planet(self.sol().current_planet.eastern_inclination,
                                                                   self.sol().current_planet.northern_inclination,
                                                                   self.sol().current_planet.projection_scaling)
        action_surface.blit(surface,(0,0))
        pygame.display.flip()
        #Initialising the GUI
        self.setGui(gui.gui(right_side_surface, message_surface, action_surface, self.sol()))
        #getting psyco if available
        try:
            import psyco
            psyco.log()
            psyco.profile()
        except ImportError:
            pass
        i = 0
        self.sol().launchThread()
        self.eventLoop()
    def gui(self):
        return self._guiInstance
    def setGui(self,g):
        self._guiInstance=g
        return
    def __init__(self):
        print "init Game"
        return
    def sol(self):
        return self._solar_system
    def setSol(self,s):
        self._solar_system=s
        return
    def updateGui(self):
        self.gui().create_infobox()
        self.gui().messageBar().create()
        if self.sol().display_mode == "solar_system":
            zoomLevel=self.sol().solar_system_zoom
            dateVariable=self.sol().current_date
            centerObject=self.sol().current_planet.planet_name
            surface = self.sol().draw_solar_system(zoom_level=zoomLevel,
                                                   date_variable=dateVariable,
                                                   center_object=centerObject)
            if self.gui().active_window is not None:
                window_w=global_variables.window_size[0]
                active_x=self.gui().active_window.rect[0]
                active_h=self.gui().active_window.rect[2]
                x=0
                y=0
                w=active_x
                h=global_variables.window_size[1]
                left_rect = pygame.Rect(x,y,w,h)
                x=active_x + active_h
                y=0
                w=window_w-active_x-active_h
                h=global_variables.window_size[1]
                right_rect = pygame.Rect(x,y,w,h)
                x=0
                y=0
                w=window_w
                h=self.gui().active_window.rect[1]
                top_rect = pygame.Rect(x,y,w,h)
                x=0
                y=self.gui().active_window.rect[1] + self.gui().active_window.rect[3]
                w=window_w
                h=global_variables.window_size[1]-self.gui().active_window.rect[3] - top_rect[3]
                bottom_rect = pygame.Rect(x,y,w,h)
                for rect in [left_rect,right_rect,top_rect,bottom_rect]:
                    action_surface.set_clip(rect)
                    action_surface.blit(surface,(0,0))
                action_surface.set_clip(None)
            else:
                action_surface.blit(surface,(0,0))
        pygame.display.flip()
    def eventLoop(self):
        """the main loop of the game"""
        while True:
            events = pygame.event.get()
            for event in events: 
                if(self.handleEvent(event)):
                    break
            i = 0
            self.updateGui()
        return
