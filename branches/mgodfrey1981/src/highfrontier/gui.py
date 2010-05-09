import button
import company_window
import trade_window
import base_window
import overlay_window
import planet_jump_window
import file_window
import tech_window
import base_population_info
import base_list_of_companies
import base_list_of_firms
import base_and_firm_market_window
import base_build_menu
import company_ownership_info
import company_financial_info
import company_list_of_firms
import firm_trade_partners_info
import firm_process_info
import construct_base_menu
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
import message_bar

class gui():
    def solarSystem(self):
        return global_variables.solar_system
    """
    This class holds all the top-level gui stuff, such as functions to distribute clicks and the commandbox buttons on the right side and such
    """
    def __init__(self,right_side_surface, message_surface, action_surface, solar_system_object):
        """
        Here the commandbox is started initialized. In addition all the other GUI elements is started up, to keep it at one place
        """
        
        
        # defining 
        command_box_left = right_side_surface.get_offset()[0]
        command_width = right_side_surface.get_size()[0]
        infobox_top = 0
        command_top = 70
        subcommand_top = 470
        
        
        self.action_rect = pygame.Rect(0,0, action_surface.get_size()[0], action_surface.get_size()[1])
        self.infobox_rect = pygame.Rect(command_box_left, infobox_top, command_width, command_top)
        self.command_rect =  pygame.Rect(command_box_left, command_top, command_width, subcommand_top-command_top)
        self.subcommand_rect = pygame.Rect(command_box_left, subcommand_top, command_width, global_variables.window_size[1] -subcommand_top)

        self.action_surface = action_surface
        self.infobox_surface = right_side_surface.subsurface(pygame.Rect(0, infobox_top, command_width, command_top))
        self.command_surface =  right_side_surface.subsurface(pygame.Rect(0, command_top, command_width, subcommand_top-command_top))
        self.subcommand_surface = right_side_surface.subsurface(pygame.Rect(0, subcommand_top, command_width, global_variables.window_size[1] -subcommand_top))


        
        
        self.active_window = None
        
        self.all_windows = {}
        
        self.all_windows["Messages"] = message_bar.message_bar(solar_system_object, action_surface, message_surface)
        self.all_windows["Company menu"] = company_window.company_window(solar_system_object, action_surface)
        self.all_windows["Trade menu"] = trade_window.trade_window(solar_system_object, action_surface)
        self.all_windows["Base overview"] = base_window.base_window(solar_system_object, action_surface)
        self.all_windows["Map overlays"] = overlay_window.overlay_window(solar_system_object, action_surface)
        self.all_windows["Planet shortcuts"] = planet_jump_window.planet_jump_window(solar_system_object, action_surface)
        self.all_windows["File menu"] = file_window.file_window(solar_system_object, action_surface)
        self.all_windows["Technology"] = tech_window.tech_window(solar_system_object, action_surface)
        
        self.all_windows["base_population_info"] = base_population_info.base_population_info(solar_system_object, action_surface)
        self.all_windows["base_list_of_companies"] = base_list_of_companies.base_list_of_companies(solar_system_object, action_surface)
        self.all_windows["base_list_of_firms"] = base_list_of_firms.base_list_of_firms(solar_system_object, action_surface)
        self.all_windows["base_and_firm_market_window"] = base_and_firm_market_window.base_and_firm_market_window(action_surface)
        self.all_windows["base_build_menu"] = base_build_menu.base_build_menu(action_surface)
        self.all_windows["company_ownership_info"] = company_ownership_info.company_ownership_info(solar_system_object, action_surface)
        self.all_windows["company_financial_info"] = company_financial_info.company_financial_info(solar_system_object, action_surface)
        self.all_windows["company_list_of_firms"] = company_list_of_firms.company_list_of_firms(solar_system_object, action_surface)
        self.all_windows["firm_trade_partners_info"] = firm_trade_partners_info.firm_trade_partners_info(solar_system_object, action_surface)
        self.all_windows["firm_process_info"] = firm_process_info.firm_process_info(solar_system_object, action_surface)
        self.all_windows["firm_process_info"] = firm_process_info.firm_process_info(solar_system_object, action_surface)
        self.all_windows["construct_base_menu"] = construct_base_menu.construct_base_menu(solar_system_object, action_surface)
        
        self.create_infobox()
        self.create_commandbox()
        self.create_subcommandbox()

        
        
    
    def receive_click(self,event):
        """
        Function that distributes clicks where necessary
        """

        #Checking where the click is located
        if self.command_rect.collidepoint(event.pos) == 1:
            for button in self.command_buttons.values():
                if button.rect.collidepoint((event.pos[0] - global_variables.window_size[0] + self.command_rect[2], event.pos[1] - self.command_rect[1])) == 1:
                    button.activate(None)
                    return 

        if self.subcommand_rect.collidepoint(event.pos) == 1:
            for button in self.subcommand_buttons.values():
                if button.rect.collidepoint((event.pos[0] - global_variables.window_size[0] + self.subcommand_rect[2], event.pos[1] - self.subcommand_rect[1])) == 1:
                    button.activate(None)
                    return 


        elif self.action_rect.collidepoint(event.pos) == 1:
            if self.active_window is not None:
                if self.active_window.rect.collidepoint(event.pos) == 1:
                    return_value = self.active_window.receive_click(event)
                    if return_value is not None:
                        if return_value == "clear":
                            self.clear_screen()
                        elif return_value == "population transfer":
                            self.solarSystem().display_mode = "planetary"
                            self.solarSystem().build_base_mode = True
                            self.solarSystem().building_base = self.solarSystem().current_planet.current_base
                            print_dict = {"text":"DEBUGGING: unknown display mode passed to infobox","type":"debugging"}
                            self.solarSystem().messages.append(print_dict)
                            pygame.mouse.set_cursor(*pygame.cursors.diamond)
                            print_dict = {"text":"Select destination for population transfer: new or existing base","type":"general gameplay info"}
                            self.clear_screen()
                            self.active_window = None
                            pygame.display.flip()
                        else:
                            raise Exception("Receive click got this, return value: " + str(return_value))
                    return

        self.click_in_action_window(event)

        
        #updating the infobox in any case
        self.create_infobox()
        self.all_windows["Messages"].create()
        pygame.display.flip()


        

    def clear_screen(self):
        """
        Function that takes care of clearing screen, by drawing whatever planet or solar system or base window that is supposed
        to be on it, thus overwriting what gui-box might be there
        """
        self.active_window = None
        sol = self.solarSystem()
        if sol.display_mode == "solar_system":
            self.action_surface.blit(sol.draw_solar_system(zoom_level=sol.solar_system_zoom,date_variable=sol.current_date,center_object=sol.current_planet.planet_name),(0,0))
        elif sol.display_mode == "planetary":
            self.action_surface.blit(sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling),(0,0))                        
        elif sol.display_mode == "base":
            if sol.current_planet.current_base is not None:
                self.going_to_base_mode_event(sol.current_planet.current_base)
        elif sol.display_mode == "firm":
            if sol.firm_selected is not None:
                self.going_to_firm_window_event(sol.firm_selected)
        elif sol.display_mode == "company":
            if sol.company_selected is not None:
                self.going_to_company_window_event(sol.company_selected)
        elif sol.display_mode in ["techtree"]:
            pass
        else:
            raise Exception("error. The mode: " + sol.display_mode +" is unknown")
        
        self.create_subcommandbox()
        pygame.display.flip()



    def zoom_in(self,event):
        self.clear_screen()
        sol = self.solarSystem()
        if sol.display_mode == "solar_system":
            sol.solar_system_zoom = sol.solar_system_zoom * 2
            surface = sol.draw_solar_system(zoom_level=sol.solar_system_zoom,date_variable=sol.current_date,center_object=sol.current_planet.planet_name)
            if surface == "planetary_mode":
                sol.solar_system_zoom = sol.solar_system_zoom / 2
                sol.display_mode = "planetary"
                sol.current_planet.load_for_drawing()
                surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
        elif sol.display_mode == "planetary":
            if sol.current_planet.projection_scaling < 720:
                sol.current_planet.projection_scaling = sol.current_planet.projection_scaling * 2
                surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)                        
            else:
                if sol.current_planet.current_base is not None: #if a base is selected on this planet, we'll zoom in on it
                    sol.display_mode = "base"
                    self.going_to_base_mode_event(sol.current_planet.current_base)
                    return
                else:
                    return
        elif sol.display_mode in ["base","firm","company"]:
            return
        elif sol.display_mode in ["techtree"]:
            surface = sol.technology_tree.zoom("in")
        else:
            raise Exception("error. The mode: " + sol.display_mode +" is unknown")
            

        self.action_surface.blit(surface,(0,0))
        pygame.display.flip()

    
        
    def zoom_out(self,event):
        self.clear_screen()
        sol = self.solarSystem()
        if sol.display_mode == "solar_system":
            if sol.solar_system_zoom >= 2:
                sol.solar_system_zoom = sol.solar_system_zoom / 2
                surface = sol.draw_solar_system(zoom_level=sol.solar_system_zoom,date_variable=sol.current_date,center_object=sol.current_planet.planet_name)
            else:
                return
        
        elif sol.display_mode == "planetary":
            if sol.current_planet.projection_scaling >= 90:
                sol.current_planet.projection_scaling = sol.current_planet.projection_scaling / 2
                surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
            else:
                sol.solar_system_zoom = 300000000 / max(sol.current_planet.planet_diameter_km, 2000) 
                sol.current_planet.unload_from_drawing()
                sol.display_mode = "solar_system" 
                surface = sol.draw_solar_system(zoom_level=sol.solar_system_zoom,date_variable=datetime.date(2102,1,22),center_object=sol.current_planet.planet_name)

        elif sol.display_mode in ["firm","company","base"]:
            surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
            sol.display_mode = "planetary"
            self.create_subcommandbox()
        elif sol.display_mode in ["techtree"]:
            surface = sol.technology_tree.zoom("out")
            
        else:
            raise Exception("error. The mode: " + sol.display_mode +" is unknown")
            return
        
        self.action_surface.blit(surface,(0,0))
        pygame.display.flip()
                

    
    def click_in_action_window(self,event):
        sol = self.solarSystem()
        position = event.pos
        button = event.button
        click_spot = pygame.Rect(position[0]-3,position[1]-3,6,6)
        if sol.display_mode == "solar_system":
            
            collision_test_result = click_spot.collidedict(sol.areas_of_interest)
            
            if collision_test_result != None:
                sol.current_planet = sol.planets[collision_test_result[1]]
                surface = sol.draw_solar_system(zoom_level=sol.solar_system_zoom,date_variable=sol.current_date,center_object=sol.current_planet.planet_name)
                if surface == "planetary_mode":
                    manager.emit("going_to_planetary_mode_event",sol.current_planet)
                    sol.solar_system_zoom = 200000000 / sol.current_planet.planet_diameter_km  
                    sol.display_mode = "planetary"
                    sol.current_planet.load_for_drawing()
                    surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
                self.action_surface.blit(surface,(0,0))
                pygame.display.flip()
        
        elif sol.display_mode == "planetary":
        
            if sol.build_base_mode: #if we are in the special build base mode, there should be a base creation instead.
                sphere_coordinates = sol.current_planet.check_base_position(position)
                
                if sphere_coordinates[0:19] == "transfer population" or isinstance(sphere_coordinates, tuple) or sphere_coordinates == "space base": #if the selection was correctly verified by check_base_position we send it back to the GUI for further processing
                    sol.build_base_mode = False
                    pygame.mouse.set_cursor(*pygame.cursors.arrow)
                    self.all_windows["construct_base_menu"].new_base_ask_for_name(sphere_coordinates)
                    self.active_window = self.all_windows["construct_base_menu"]
                return
            
            else: #if we are not in build_base_mode we work as normally
                areas_of_interest = sol.current_planet.areas_of_interest[(sol.current_planet.northern_inclination,sol.current_planet.eastern_inclination,sol.current_planet.projection_scaling)]
                collision_test_result = click_spot.collidedict(areas_of_interest)
                if collision_test_result != None:
                    current_base = sol.current_planet.bases[collision_test_result[1]]
                    #print "current_base " + str(current_base)
                    sol.current_planet.current_base = current_base
                    if button == 1:
                        surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
                    if button == 3:
                        self.going_to_base_mode_event(current_base)
                        
                        return
                else:
                    return

            self.action_surface.blit(surface,(0,0))
            pygame.display.flip()

        
        elif sol.display_mode in ["techtree"]:
            surface = sol.technology_tree.receive_click(event)
            self.action_surface.blit(surface,(0,0))
            pygame.display.flip()
        
        elif sol.display_mode in ["company","firm","base"]:
            pass            
        else:
            raise Exception("error. The mode: " + sol.display_mode +" is unknown")                

            
            
            
    
    def go_left(self,event):
        self.clear_screen()
        sol = self.solarSystem()
        if sol.display_mode == "planetary":
            sol.current_planet.eastern_inclination = sol.current_planet.eastern_inclination - 30
            if sol.current_planet.eastern_inclination <= -180:
                sol.current_planet.eastern_inclination = sol.current_planet.eastern_inclination + 360
            surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
        elif sol.display_mode == "techtree":
            surface = sol.technology_tree.move("left")
        else:
            return
        
        self.action_surface.blit(surface,(0,0))
        pygame.display.flip()
        
    def go_right(self,event):
        self.clear_screen()
        sol = self.solarSystem()
        if sol.display_mode == "planetary":
            sol.current_planet.eastern_inclination = sol.current_planet.eastern_inclination + 30
            if sol.current_planet.eastern_inclination > 180:
                sol.current_planet.eastern_inclination = sol.current_planet.eastern_inclination - 360
            
            surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
        elif sol.display_mode == "techtree":
            surface = sol.technology_tree.move("right")
        else:
            return
        self.action_surface.blit(surface,(0,0))
        pygame.display.flip()

        
    def go_down(self,event):
        self.clear_screen()
        sol = self.solarSystem()
        if sol.display_mode == "planetary":
            if sol.current_planet.northern_inclination > -90:
                sol.current_planet.northern_inclination = sol.current_planet.northern_inclination - 30
                surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
            else:
                return
        elif sol.display_mode == "techtree":
            surface = sol.technology_tree.move("down")
        else:
            return
        self.action_surface.blit(surface,(0,0))
        pygame.display.flip()


    
    def go_up(self,event):
        self.clear_screen()
        sol = self.solarSystem()
        if sol.display_mode == "planetary":
            if sol.current_planet.northern_inclination < 90:
                sol.current_planet.northern_inclination = sol.current_planet.northern_inclination + 30
                surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
            else:
                return
        elif sol.display_mode == "techtree":
            surface = sol.technology_tree.move("up")
        else:
            return
        self.action_surface.blit(surface,(0,0))
        pygame.display.flip()


        
    

#            print "error. The mode: " + sol.display_mode +" does not accept a/z input"


        


    def going_to_company_window_event(self,company_selected):
        sol = self.solarSystem()
#        company_selected = event.data
#        mode_before_change = sol.display_mode
        sol.display_mode = "company"
        surface = company_selected.draw_company_window()
        self.action_surface.blit(surface,(0,0))
        pygame.display.flip()

    def going_to_firm_window_event(self,firm_selected):
        sol = self.solarSystem()
        sol.display_mode = "firm"
        surface = firm_selected.draw_firm_window()
        self.action_surface.blit(surface,(0,0))
        pygame.display.flip()
        
    def going_to_base_mode_event(self,base_selected):
        sol = self.solarSystem()
#        mode_before_change = sol.display_mode
        sol.current_planet.current_base = base_selected
        sol.current_planet = base_selected.home_planet
        sol.display_mode = "base"
        surface = base_selected.draw_base_window()
        self.create_subcommandbox()
        self.action_surface.blit(surface,(0,0))
        pygame.display.flip()
















        
#


    def create_infobox(self):
        self.infobox_surface.fill((150,150,150))
        
        # creating the date string
        date_string = str(self.solarSystem().current_date)
        rendered_date_string = global_variables.standard_font.render(date_string,True,(0,0,0))
        self.infobox_surface.blit(rendered_date_string, (10,10))

        # creating the env string
        if self.solarSystem().display_mode == "solar_system":
            env_string = "Solar system -" + string.capitalize(self.solarSystem().current_planet.planet_name)
        elif self.solarSystem().display_mode == "planetary":
            if self.solarSystem().current_planet.current_base == None:
                env_string = self.solarSystem().current_planet.planet_name
            else:
                env_string = self.solarSystem().current_planet.planet_name + " - " + self.solarSystem().current_planet.current_base.name 
        elif self.solarSystem().display_mode == "company" and self.solarSystem().company_selected is not None:
            env_string = self.solarSystem().company_selected.name
        elif self.solarSystem().display_mode == "firm" and self.solarSystem().firm_selected is not None:
            env_string = self.solarSystem().firm_selected.name
        elif self.solarSystem().display_mode == "base" and self.solarSystem().current_planet.current_base is not None:
            env_string = self.solarSystem().current_planet.current_base.name
        elif self.solarSystem().display_mode == "techtree":
            env_string = "technology tree"
        else:
            env_string = ""
            if self.solarSystem().message_printing["debugging"]:
                print_dict = {"text":"DEBUGGING: unknown display mode passed to infobox","type":"debugging"}
                self.solarSystem().messages.append(print_dict)
        rendered_env_string = global_variables.standard_font.render(env_string,True,(0,0,0))
        self.infobox_surface.blit(rendered_env_string, (10,30))

        
        #creating the capital string
        if self.solarSystem().current_player is not None:
            capital_string = str(primitives.nicefy_numbers(int(self.solarSystem().current_player.capital))) + " $"
            rendered_capital_string = global_variables.standard_font.render(capital_string,True,(0,0,0))
            self.infobox_surface.blit(rendered_capital_string, (10,50))
        
        
    
    def commandbox_button_activate(self,label, function_parameter):
        """
        Function that decides what to do if a commandbox button is pressed
        """
        if label == "Technology":
            if self.solarSystem().display_mode == "techtree":
                self.solarSystem().display_mode = self.all_windows["Technology"].display_mode_before
                self.clear_screen()
                return
            else:
                self.all_windows["Technology"].display_mode_before = self.solarSystem().display_mode
                
            
        
        self.clear_screen()
        self.active_window = self.all_windows[label]
        self.all_windows[function_parameter].create()
        
    
    def create_commandbox(self):    
        """
        Creates the right-side menu command box
        """
        self.command_surface.fill((150,150,150))
#        pygame.draw.rect(self.command_surface, (150,150,150), self.command_rect)
        
        labels = ["Map overlays","Planet shortcuts","Company menu","Base overview","Technology","Trade menu","File menu"]
        self.command_buttons = {}
        for i, label in enumerate(labels):
            self.command_buttons[label] = button.button(label, 
                                                                self.command_surface,
                                                                self.commandbox_button_activate, 
                                                                function_parameter = label, 
                                                                fixed_size = (self.command_rect[2]-20,35), topleft = (10, i * 40 + 10))

    
    
    def subcommandbox_button_activate(self, nicelabel, label):
        """
        Activates the right-side menu lower subcommand box. This is specific for the navigation window context
        such as for example base information and such
        """
        self.all_windows[label].create()
        self.active_window = self.all_windows[label]

    def create_subcommandbox(self):    
        """
        Creates the right-side menu lower subcommand box. This is specific for the navigation window context
        such as for example base information and such
        """
        self.subcommand_surface.fill((150,150,150))
        self.subcommand_buttons = {}
#        pygame.draw.rect(self.subcommand_surface, (150,150,150), self.subcommand_rect)

        if self.solarSystem().display_mode == "base":
            self.buttonlinks = ["base_population_info","base_list_of_companies","base_list_of_firms","base_and_firm_market_window","base_build_menu"]
            self.buttonnicenames = ["Population","Companies","Firms","Market","Build"]
        elif self.solarSystem().display_mode == "firm":
            self.buttonlinks = ["firm_process_info","base_and_firm_market_window","firm_trade_partners_info"]
            self.buttonnicenames = ["Production","Market","Trade partners"]
        elif self.solarSystem().display_mode == "company":
            self.buttonlinks = ["company_ownership_info","company_financial_info","company_list_of_firms"]
            self.buttonnicenames = ["Ownership info","Financial info","Owned firms"]

        else:
            
            pygame.display.flip()
            return
        
        self.subcommand_buttons = {}
        for i, label in enumerate(self.buttonlinks):
            self.subcommand_buttons[label] = button.button(self.buttonnicenames[i], self.subcommand_surface,
                                                                self.subcommandbox_button_activate, function_parameter = label, 
                                                                fixed_size = (self.subcommand_surface.get_width()-20,35), 
                                                                topleft = (10, i * 40 + 10))
        
        pygame.display.flip()

