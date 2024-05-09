from datetime import datetime
import math
import pygame
from pygame.locals import *
import time
import os, sys
from display import Direction, Display
import planet
import company
import solarsystem
import datetime
import primitives
import global_variables
import gui
import random
import importlib



class Game:
    def __init__(self):
        print("init Game")
        return
    def start_loop(self,companyName = None, companyCapital = None, loadPreviousGame = None):
        """
        companyName          string of a company that will play as current player. If none, the game will run in simulation mode
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
            sol = solarsystem.solarsystem(global_variables.start_date, de_novo_initialization = False)
            sol.load_solar_system(loadPreviousGame)
        else:
            sol = solarsystem.solarsystem(global_variables.start_date, de_novo_initialization = True)
        #initialize current player company
        if companyName is not None:
            if sol.current_player is not None:
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
            if companyName in list(sol.companies.keys()):
                sol.current_player = sol.companies[companyName]
                sol.current_player.automation_dict = automation_dict
                sol.current_player.automation_dict["Demand bidding (initiate buying bids)"] = True
                sol.current_player.automation_dict["Supply bidding (initiate selling bids)"] = True
                sol.current_player.capital = companyCapital
            else:
                model_companyName = random.choice(list(sol.companies.keys()))
                model_company = sol.companies[model_companyName]
                new_company = company.company(sol,model_company.company_database,deviation=5,companyName=companyName,capital=companyCapital)
                sol.companies[companyName] = new_company
                new_company.automation_dict = automation_dict
                sol.current_player = new_company


        #divide the surface in action and non-action
        action_rect = pygame.Rect(0,0,global_variables.window_size[0] - 150, global_variables.window_size[1] - 100)
        right_side_rect = pygame.Rect(global_variables.window_size[0] - 150, 0, 150, global_variables.window_size[1])
        message_rect = pygame.Rect(10,global_variables.window_size[1] - 100, global_variables.window_size[0] - 170, 100)
        action_surface = window.subsurface(action_rect)
        right_side_surface = window.subsurface(right_side_rect)
        message_surface = window.subsurface(message_rect)
        #switch to determine planetary mode or solarsystem mode from beginning
        mode_before_change = sol.display_mode
        if sol.display_mode == Display.SOLAR_SYSTEM:
            surface = sol.draw_solar_system(zoom_level=sol.solar_system_zoom,date_variable=sol.current_date,center_object=sol.current_planet.planet_name)
        if sol.display_mode == Display.PLANETARY:
            sol.current_planet = sol.planets["earth"]
            surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
        action_surface.blit(surface,(0,0))
        pygame.display.flip()
        #Initialising the GUI
        gui_instance = gui.gui(right_side_surface, message_surface, action_surface, sol)
        #getting psyco if available
        try:
            import psyco
            psyco.log()
            psyco.profile()
        except ImportError:
            pass
        i = 0
        sol.launchThread()
        while True:
            events = pygame.event.get()
            for event in events:
                direction_to_move = None
                match event.type:
                    case pygame.QUIT:
                        sys.exit(0)
                    case pygame.MOUSEBUTTONDOWN:
                        gui_instance.receive_click(event)
                        pygame.display.flip()
                    case pygame.KEYDOWN:
                        if "text_receiver" in dir(gui_instance.active_window):
                            if gui_instance.active_window.text_receiver is not None:
                                gui_instance.active_window.text_receiver.receive_text(event)
                                break
                        match event.key:

                            case  pygame.K_PAGEUP:
                                gui_instance.zoom()
                            case  pygame.K_PAGEDOWN:
                                gui_instance.zoom(out=True)
                            case  pygame.K_LEFT | pygame.K_a:
                                direction_to_move = Direction.LEFT
                            case  pygame.K_RIGHT| pygame.K_d:
                                direction_to_move = Direction.RIGHT
                            case  pygame.K_UP | pygame.K_w:
                                direction_to_move = Direction.UP
                            case  pygame.K_DOWN | pygame.K_s:
                                direction_to_move = Direction.DOWN
                        pygame.display.flip()
                    case pygame.MOUSEWHEEL:
                        if event.y > 0:
                            gui_instance.zoom()
                        if event.y < 0:
                            gui_instance.zoom(out=True)
                        if event.x > 0:
                            direction_to_move = Direction.RIGHT
                        if event.x < 0:
                            direction_to_move = Direction.LEFT

                if direction_to_move is not None:
                    gui_instance.go_any_direction(direction_to_move)


            i = 0
            gui_instance.create_infobox()
            gui_instance.all_windows["Messages"].create()
            #in solar system the display needs updating all the time. However we need to protect whatever active window is shown:
            if sol.display_mode == Display.SOLAR_SYSTEM:
                surface = sol.draw_solar_system(zoom_level=sol.solar_system_zoom,date_variable=sol.current_date,center_object=sol.current_planet.planet_name)
                if gui_instance.active_window is not None:
                    left_rect = pygame.Rect(0,0,gui_instance.active_window.rect[0],global_variables.window_size[1])
                    right_rect = pygame.Rect(gui_instance.active_window.rect[0] + gui_instance.active_window.rect[2],0,global_variables.window_size[0]-gui_instance.active_window.rect[0]-gui_instance.active_window.rect[2],global_variables.window_size[1])
                    top_rect = pygame.Rect(0,0,global_variables.window_size[0],gui_instance.active_window.rect[1])
                    bottom_rect = pygame.Rect(0,gui_instance.active_window.rect[1] + gui_instance.active_window.rect[3],global_variables.window_size[0],global_variables.window_size[1]-gui_instance.active_window.rect[3] - top_rect[3])
                    for rect in [left_rect,right_rect,top_rect,bottom_rect]:
                        action_surface.set_clip(rect)
                        action_surface.blit(surface,(0,0))
                    action_surface.set_clip(None)
                else:
                    action_surface.blit(surface,(0,0))
            pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.start_loop(companyName = "asdf",
                        companyCapital =  1000000,
                        loadPreviousGame = None)
