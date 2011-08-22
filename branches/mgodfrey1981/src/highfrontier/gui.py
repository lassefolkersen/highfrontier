import signaller
import button
import construct_base_menu
import firm_process_info
import firm_trade_partners_info
import company_list_of_firms
import company_financial_info
import company_ownership_info
import base_build_menu
import base_and_firm_market_window
import base_list_of_firms
import base_list_of_companies
import base_population_info
import file_window
import company_window
import trade_window
import base_window
import tech_window
import planet_jump_window
import overlay_window
import navigation_window
import message_bar
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


class gui():
    def slot__clickFirmTradePartners(self):
        w=self.firmTradePartnersInfo()
        w.create()
        self.active_window=w
        return
    def slot__clickFirmProduction(self):
        w=self.firmProcessInfo()
        w.create()
        self.active_window=w
        return
    def receive_text(self,event):
        if "text_receiver" in dir(self.active_window):
            if self.active_window.text_receiver is not None:
                self.active_window.text_receiver.receive_text(event)
                return True
    def slot__showTechnologyWindow(self):
        w=self.techWindow()
        w.create()
        self.active_window=w
        return
    def techWindow(self):
        try:
            b=self._techWindow
        except AttributeError:
            self._techWindow=tech_window.tech_window(self.sol(), 
                                                     self.actionSurface())
        return self._techWindow
    def fileWindow(self):
        try:
            b=self._fileWindow
        except AttributeError:
            self._fileWindow = file_window.file_window(self.sol(), 
                                                       self.actionSurface())
        return self._fileWindow
    def receive_click(self,event):
        """
        Function that distributes clicks where necessary
        """
        #Checking where the click is located
        if self.command_rect.collidepoint(event.pos) == 1:
            for button in self.command_buttons.values():
                if button.rect().collidepoint((event.pos[0] - global_variables.window_size[0] + self.command_rect[2], 
                                               event.pos[1] - self.command_rect[1])) == 1:
                    button.activate(None)
                    return 
        if self.subcommand_rect.collidepoint(event.pos) == 1:
            self.subcommand_rect_clicked(event)
            return 
        elif self.action_rect.collidepoint(event.pos) == 1:
            if self.active_window is not None:
                if self.active_window.rect.collidepoint(event.pos) == 1:
                    return_value = self.active_window.receive_click(event)
                    if return_value is not None:
                        if return_value == "clear":
                            self.clear_screen()
                        elif return_value == "population transfer":
                            self.sol().display_mode = "planetary"
                            self.sol().build_base_mode = True
                            self.sol().building_base = self.sol().current_planet.current_base
                            print_dict = {"text":"DEBUGGING: unknown display mode passed to infobox","type":"debugging"}
                            self.sol().messages.append(print_dict)
                            pygame.mouse.set_cursor(*pygame.cursors.diamond)
                            print_dict = {"text":"Select destination for population transfer: new or existing base",
                                          "type":"general gameplay info"}
                            self.clear_screen()
                            self.active_window = None
                            pygame.display.flip()
                        else:
                            raise Exception("Receive click got this, return value: " + str(return_value))
                    return
        self.click_in_action_window(event)

        
        #updating the infobox in any case
        self.create_infobox()
        self.messageBar().create()
        pygame.display.flip()
    """
    This class holds all the top-level gui stuff, 
    such as functions to distribute clicks 
    and the commandbox buttons on the right side and such
    """
    def __init__(self,right_side_surface, message_surface, action_surface, solar_system_object):
        self.setActionSurface(action_surface)
        self.setMessageSurface(message_surface)
        """
        Here the commandbox is started initialized. 
        In addition all the other GUI elements is started up, 
        to keep it at one place
        """
        # defining 
        command_box_left = right_side_surface.get_offset()[0]
        command_width = right_side_surface.get_size()[0]
        infobox_top = 0
        command_top = 70
        subcommand_top = 470
        self.action_rect = pygame.Rect(0,
                                       0, 
                                       self.actionSurface().get_size()[0], 
                                       self.actionSurface().get_size()[1])
        self.infobox_rect = pygame.Rect(command_box_left, 
                                        infobox_top, 
                                        command_width, 
                                        command_top)
        self.command_rect =  pygame.Rect(command_box_left, 
                                         command_top, 
                                         command_width, 
                                         subcommand_top-command_top)
        self.subcommand_rect = pygame.Rect(command_box_left, 
                                           subcommand_top, 
                                           command_width, 
                                           global_variables.window_size[1] -subcommand_top)
        self.setActionSurface(action_surface)
        self.infobox_surface = right_side_surface.subsurface(pygame.Rect(0, 
                                                                         infobox_top, 
                                                                         command_width, 
                                                                         command_top))
        self.command_surface =  right_side_surface.subsurface(pygame.Rect(0, 
                                                                          command_top, 
                                                                          command_width, 
                                                                          subcommand_top-command_top))
        self.subcommand_surface = right_side_surface.subsurface(pygame.Rect(0, 
                                                                            subcommand_top, 
                                                                            command_width, 
                                                                            global_variables.window_size[1] -subcommand_top))
        self.setSol(solar_system_object)
        self.active_window = None
        self.create_infobox()
        self.create_commandbox()
        self.create_subcommandbox()

    def slot__showBaseOverviewWindow(self):
        w=self.baseWindow()
        w.create()
        self.active_window=w
        return
    def baseWindow(self):
        """ creates a base window if none exists """
        try:
            b=self._baseWindow
        except AttributeError:
            self._baseWindow=base_window.base_window(self.sol(), 
                                                     self.actionSurface())
        return self._baseWindow
    def slot__showPlanetShortcutsWindow(self):
        w=self.planetJumpWindow()
        w.create()
        self.active_window=w
        return
    def planetJumpWindow(self):
        try:
            b=self._planetJumpWindow
        except AttributeError:
            self._planetJumpWindow=planet_jump_window.planet_jump_window(self.sol(), 
                                                                         self.actionSurface())
        return self._planetJumpWindow
    def slot__showMapOverlayWindow(self):
        w=self.mapOverlayWindow()
        signaller.connect(w,"signal__change",lambda overlay: self.slot__setMapOverlay(overlay))
        w.create()
        self.active_window=w
        return
    def click_in_action_window(self,event):
        sol = self.sol()
        position = event.pos
        button = event.button
        click_spot = pygame.Rect(position[0]-3,position[1]-3,6,6)
        if sol.display_mode == "solar_system":
            
            collision_test_result = click_spot.collidedict(sol.areas_of_interest)
            
            if collision_test_result != None:
                sol.current_planet = sol.planets[collision_test_result[1]]
                surface = sol.draw_solar_system(zoom_level=sol.solar_system_zoom,
                                                date_variable=sol.current_date,
                                                center_object=sol.current_planet.planet_name)
                if surface == "planetary_mode":
                    manager.emit("going_to_planetary_mode_event",sol.current_planet)
                    sol.solar_system_zoom = 200000000 / sol.current_planet.planet_diameter_km  
                    sol.display_mode = "planetary"
                    sol.current_planet.load_for_drawing()
                    surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,
                                                                    sol.current_planet.northern_inclination,
                                                                    sol.current_planet.projection_scaling)
                self.actionSurface().blit(surface,(0,0))
                pygame.display.flip()
        elif sol.display_mode == "planetary":
            if sol.build_base_mode: #if we are in the special build base mode, there should be a base creation instead.
                sphere_coordinates = sol.current_planet.check_base_position(position)
                if (sphere_coordinates[0:19] == "transfer population" or isinstance(sphere_coordinates, tuple) 
                    or sphere_coordinates == "space base"): 
                    """if the selection was correctly verified by check_base_position we send it back to the GUI 
                    for further processing"""
                    sol.build_base_mode = False
                    pygame.mouse.set_cursor(*pygame.cursors.arrow)
                    self.all_windows["construct_base_menu"].new_base_ask_for_name(sphere_coordinates)
                    self.active_window = self.all_windows["construct_base_menu"]
                return
            else: #if we are not in build_base_mode we work as normally
                areas_of_interest = sol.current_planet.areas_of_interest[(sol.current_planet.northern_inclination,
                                                                          sol.current_planet.eastern_inclination,
                                                                          sol.current_planet.projection_scaling)]
                collision_test_result = click_spot.collidedict(areas_of_interest)
                if collision_test_result != None:
                    current_base = sol.current_planet.bases[collision_test_result[1]]
                    sol.current_planet.current_base = current_base
                    if button == 1:
                        surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,
                                                                        sol.current_planet.northern_inclination,
                                                                        sol.current_planet.projection_scaling)
                    if button == 3:
                        self.going_to_base_mode_event(current_base)
                        return
                else:
                    return
            self.actionSurface().blit(surface,(0,0))
            pygame.display.flip()
        elif sol.display_mode in ["techtree"]:
            surface = sol.technology_tree.receive_click(event)
            self.actionSurface().blit(surface,(0,0))
            pygame.display.flip()
        elif sol.display_mode in ["company","firm","base"]:
            pass            
        else:
            raise Exception("error. The mode: " + sol.display_mode +" is unknown")                
    def mapOverlayWindow(self):
        try:
            b=self._mapOverlayWindow
        except AttributeError:
            self._mapOverlayWindow=overlay_window.overlay_window(self.sol(), 
                                                                 self.actionSurface())
        return self._mapOverlayWindow
    def create_commandbox(self):    
        """
        Creates the right-side menu command box
        """
        self.command_surface.fill((150,150,150))
        self.command_buttons = {}
        """ Map overlays """
        i=0
        surface=self.command_surface
        size=(self.command_rect[2]-20,35)
        topleft=(10,i*40+10)
        b=button.button("Map overlays",surface,fixed_size=size,topleft=topleft)
        signaller.connect(b,"signal__clicked",lambda: self.slot__showMapOverlayWindow())
        self.command_buttons[b.label()]=b
        """ Planet shortcuts """
        i=i+1
        topleft=(10,i*40+10)
        b=button.button("Planet shortcuts",surface,fixed_size=size,topleft=topleft)
        signaller.connect(b,"signal__clicked",lambda: self.slot__showPlanetShortcutsWindow())
        self.command_buttons[b.label()]=b
        """ Base overview """
        i=i+1
        topleft=(10,i*40+10)
        b=button.button("Base overview",surface,fixed_size=size,topleft=topleft)
        signaller.connect(b,"signal__clicked",lambda: self.slot__showBaseOverviewWindow())
        self.command_buttons[b.label()]=b
        """ Technology """
        i=i+1
        topleft=(10,i*40+10)
        b=button.button("Technology",surface,fixed_size=size,topleft=topleft)
        signaller.connect(b,"signal__clicked",lambda: self.slot__showTechnologyWindow())
        self.command_buttons[b.label()]=b
        """ File menu """
        i=i+1
        topleft=(10,i*40+10)
        b=button.button("File menu",surface,fixed_size=size,topleft=topleft)
        signaller.connect(b,"signal__clicked",lambda: self.slot__showFileWindow())
        self.command_buttons[b.label()]=b
        """ Trade Menu """
        i=i+1
        topleft=(10,i*40+10)
        b=button.button("Trade menu",surface,fixed_size=size,topleft=topleft)
        signaller.connect(b,"signal__clicked",lambda: self.slot__showTradeWindow())
        self.command_buttons[b.label()]=b
        """ Company menu """
        i=i+1
        topleft=(10,i*40+10)
        b=button.button("Company menu",surface,fixed_size=size,topleft=topleft)
        signaller.connect(b,"signal__clicked",lambda: self.slot__showCompanyWindow())
        self.command_buttons[b.label()]=b
    def clear_screen(self):
        """
        Function that takes care of clearing screen, 
        by drawing whatever planet or solar system or base window that is supposed
        to be on it, thus overwriting what gui-box might be there
        """
        self.active_window = None
        sol = self.sol()
        if sol.display_mode == "solar_system":
            self.actionSurface().blit(sol.draw_solar_system(zoom_level=sol.solar_system_zoom,
                                                           date_variable=sol.current_date,
                                                           center_object=sol.current_planet.planet_name),
                                     (0,0))
        elif sol.display_mode == "planetary":
            self.actionSurface().blit(sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,
                                                                           sol.current_planet.northern_inclination,
                                                                           sol.current_planet.projection_scaling),
                                     (0,0))                        
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
        sol = self.sol()
        if sol.display_mode == "solar_system":
            sol.solar_system_zoom = sol.solar_system_zoom * 2
            surface = sol.draw_solar_system(zoom_level=sol.solar_system_zoom,
                                            date_variable=sol.current_date,
                                            center_object=sol.current_planet.planet_name)
            if surface == "planetary_mode":
                sol.solar_system_zoom = sol.solar_system_zoom / 2
                sol.display_mode = "planetary"
                sol.current_planet.load_for_drawing()
                surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,
                                                                sol.current_planet.northern_inclination,
                                                                sol.current_planet.projection_scaling)
        elif sol.display_mode == "planetary":
            if sol.current_planet.projection_scaling < 720:
                sol.current_planet.projection_scaling = sol.current_planet.projection_scaling * 2
                surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,
                                                                sol.current_planet.northern_inclination,
                                                                sol.current_planet.projection_scaling)
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
        self.actionSurface().blit(surface,(0,0))
        pygame.display.flip()
    def zoom_out(self,event):
        self.clear_screen()
        sol = self.sol()
        if sol.display_mode == "solar_system":
            if sol.solar_system_zoom >= 2:
                sol.solar_system_zoom = sol.solar_system_zoom / 2
                surface = sol.draw_solar_system(zoom_level=sol.solar_system_zoom,
                                                date_variable=sol.current_date,
                                                center_object=sol.current_planet.planet_name)
            else:
                return
        elif sol.display_mode == "planetary":
            if sol.current_planet.projection_scaling >= 90:
                sol.current_planet.projection_scaling = sol.current_planet.projection_scaling / 2
                surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,
                                                                sol.current_planet.northern_inclination,
                                                                sol.current_planet.projection_scaling)
            else:
                sol.solar_system_zoom = 300000000 / max(sol.current_planet.planet_diameter_km, 2000) 
                sol.current_planet.unload_from_drawing()
                sol.display_mode = "solar_system" 
                surface = sol.draw_solar_system(zoom_level=sol.solar_system_zoom,
                                                date_variable=datetime.date(2102,1,22),
                                                center_object=sol.current_planet.planet_name)
        elif sol.display_mode in ["firm","company","base"]:
            surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,
                                                            sol.current_planet.northern_inclination,
                                                            sol.current_planet.projection_scaling)
            sol.display_mode = "planetary"
            self.create_subcommandbox()
        elif sol.display_mode in ["techtree"]:
            surface = sol.technology_tree.zoom("out")
        else:
            raise Exception("error. The mode: " + sol.display_mode +" is unknown")
            return
        self.actionSurface().blit(surface,(0,0))
        pygame.display.flip()
    def go_left(self,event):
        self.clear_screen()
        sol = self.sol()
        if sol.display_mode == "planetary":
            sol.current_planet.eastern_inclination = sol.current_planet.eastern_inclination - 30
            if sol.current_planet.eastern_inclination <= -180:
                sol.current_planet.eastern_inclination = sol.current_planet.eastern_inclination + 360
            surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,
                                                            sol.current_planet.northern_inclination,
                                                            sol.current_planet.projection_scaling)
        elif sol.display_mode == "techtree":
            surface = sol.technology_tree.move("left")
        else:
            return
        self.actionSurface().blit(surface,(0,0))
        pygame.display.flip()
    def go_right(self,event):
        self.clear_screen()
        sol = self.sol()
        if sol.display_mode == "planetary":
            sol.current_planet.eastern_inclination = sol.current_planet.eastern_inclination + 30
            if sol.current_planet.eastern_inclination > 180:
                sol.current_planet.eastern_inclination = sol.current_planet.eastern_inclination - 360
            surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,
                                                            sol.current_planet.northern_inclination,
                                                            sol.current_planet.projection_scaling)
        elif sol.display_mode == "techtree":
            surface = sol.technology_tree.move("right")
        else:
            return
        self.actionSurface().blit(surface,(0,0))
        pygame.display.flip()
    def go_down(self,event):
        self.clear_screen()
        sol = self.sol()
        if sol.display_mode == "planetary":
            if sol.current_planet.northern_inclination > -90:
                sol.current_planet.northern_inclination = sol.current_planet.northern_inclination - 30
                surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,
                                                                sol.current_planet.northern_inclination,
                                                                sol.current_planet.projection_scaling)
            else:
                return
        elif sol.display_mode == "techtree":
            surface = sol.technology_tree.move("down")
        else:
            return
        self.actionSurface().blit(surface,(0,0))
        pygame.display.flip()
    def go_up(self,event):
        self.clear_screen()
        sol = self.sol()
        if sol.display_mode == "planetary":
            if sol.current_planet.northern_inclination < 90:
                sol.current_planet.northern_inclination = sol.current_planet.northern_inclination + 30
                surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,
                                                                sol.current_planet.northern_inclination,
                                                                sol.current_planet.projection_scaling)
            else:
                return
        elif sol.display_mode == "techtree":
            surface = sol.technology_tree.move("up")
        else:
            return
        self.actionSurface().blit(surface,(0,0))
        pygame.display.flip()

    def going_to_company_window_event(self,company_selected):
        sol = self.sol()
#        company_selected = event.data
#        mode_before_change = sol.display_mode
        sol.display_mode = "company"
        surface = company_selected.draw_company_window()
        self.actionSurface().blit(surface,(0,0))
        pygame.display.flip()

    def going_to_firm_window_event(self,firm_selected):
        sol = self.sol()
        sol.display_mode = "firm"
        surface = firm_selected.draw_firm_window()
        self.actionSurface().blit(surface,(0,0))
        pygame.display.flip()
        
    def going_to_base_mode_event(self,base_selected):
        sol = self.sol()
#        mode_before_change = sol.display_mode
        sol.current_planet.current_base = base_selected
        sol.current_planet = base_selected.home_planet
        sol.display_mode = "base"
        surface = base_selected.draw_base_window()
        self.create_subcommandbox()
        self.actionSurface().blit(surface,(0,0))
        pygame.display.flip()

    def create_infobox(self):
        self.infobox_surface.fill((150,150,150))
        
        # creating the date string
        date_string = str(self.sol().current_date)
        rendered_date_string = global_variables.standard_font.render(date_string,True,(0,0,0))
        self.infobox_surface.blit(rendered_date_string, (10,10))

        # creating the env string
        if self.sol().display_mode == "solar_system":
            env_string = "Solar system -" + string.capitalize(self.sol().current_planet.planet_name)
        elif self.sol().display_mode == "planetary":
            if self.sol().current_planet.current_base == None:
                env_string = self.sol().current_planet.planet_name
            else:
                env_string = self.sol().current_planet.planet_name + " - " + self.sol().current_planet.current_base.name 
        elif self.sol().display_mode == "company" and self.sol().company_selected is not None:
            env_string = self.sol().company_selected.name
        elif self.sol().display_mode == "firm" and self.sol().firm_selected is not None:
            env_string = self.sol().firm_selected.name
        elif self.sol().display_mode == "base" and self.sol().current_planet.current_base is not None:
            env_string = self.sol().current_planet.current_base.name
        elif self.sol().display_mode == "techtree":
            env_string = "technology tree"
        else:
            env_string = ""
            if self.sol().message_printing["debugging"]:
                print_dict = {"text":"DEBUGGING: unknown display mode passed to infobox","type":"debugging"}
                self.sol().messages.append(print_dict)
        rendered_env_string = global_variables.standard_font.render(env_string,True,(0,0,0))
        self.infobox_surface.blit(rendered_env_string, (10,30))
        #creating the capital string
        if self.sol().current_player is not None:
            capital_string = str(primitives.nicefy_numbers(int(self.sol().current_player.capital)))+" $"
            rendered_capital_string = global_variables.standard_font.render(capital_string,True,(0,0,0))
            self.infobox_surface.blit(rendered_capital_string, (10,50))
    def sol(self):
        return self._sol
    def setSol(self,s):
        self._sol=s
        return
    def actionSurface(self):
        return self._action_surface
    def setActionSurface(self,s):
        self._action_surface=s
        return
    def messageSurface(self):
        return self._message_surface
    def setMessageSurface(self,s):
        self._message_surface=s
        return
    def messageBar(self):
        """ inits the message bar once, 
        and returns the one attached to this object """
        try:
            b=self._message_bar
        except AttributeError:
            self._message_bar=message_bar.message_bar(self.sol(),
                                                      self.actionSurface(),
                                                      self.messageSurface())
        return self._message_bar
    def commandbox_button_activate(self,label, function_parameter):
        """
        Function that decides what to do if a commandbox button is pressed
        """
        if label == "Technology":
            if self.sol().display_mode == "techtree":
                self.sol().display_mode = self.all_windows["Technology"].display_mode_before
                self.clear_screen()
                return
            else:
                self.all_windows["Technology"].display_mode_before = self.sol().display_mode
        self.clear_screen()
        self.active_window = self.all_windows[label]
        self.all_windows[function_parameter].create()
    def baseListOfCompanies(self):
        try:
            b=self._baseListOfCompanies
        except AttributeError:
            self._baseListOfCompanies=base_list_of_companies.base_list_of_companies(self.sol(), 
                                                                                    self.actionSurface())
        return self._baseListOfCompanies
    def baseListOfFirms(self):
        try:
            b=self._baseListOfFirms
        except AttributeError:
            self._baseListOfFirms = base_list_of_firms.base_list_of_firms(self.sol(), 
                                                                          self.actionSurface())
        return self._baseListOfFirms
    def baseAndFirmMarketWindow(self):
        try:
            b=self._baseAndFirmMarketWindow
        except AttributeError:
            self._baseAndFirmMarketWindow=base_and_firm_market_window.base_and_firm_market_window(self.sol(), 
                                                                                                  self.actionSurface())
        return self._baseAndFirmMarketWindow
    def baseBuildMenu(self):
        try:
            b=self._baseBuildMenu
        except AttributeError:
            self._baseBuildMenu=base_build_menu.base_build_menu(self.sol(), 
                                                                self.actionSurface())
        return self._baseBuildMenu
    def companyOwnershipInfo(self):
        try:
            b=self._companyOwnershipInfo
        except AttributeError:
            self._companyOwnershipInfo = company_ownership_info.company_ownership_info(self.sol(), 
                                                                                       self.actionSurface())
        return self._companyOwnershipInfo
    def companyFinancialInfo(self):
        try:
            b=self._companyFinancialInfo
        except AttributeError:
            self._companyFinancialInfo=company_financial_info.company_financial_info(self.sol(), 
                                                                                     self.actionSurface())
        return self._companyFinancialInfo
    def companyListOfFirms(self):
        try:
            b=self._companyListOfFirms
        except AttributeError:
            self._companyListOfFirms = company_list_of_firms.company_list_of_firms(self.sol(), 
                                                                                   self.actionSurface())
        return self._companyListOfFirms
    def firmTradePartnersInfo(self):
        try:
            b=self._firmTradePartnersInfo
        except AttributeError:
            self._firmTradePartnersInfo=firm_trade_partners_info.firm_trade_partners_info(self.sol(), 
                                                                                          self.actionSurface())
        return self._firmTradePartnersInfo
    def firmProcessInfo(self):
        try:
            b=self._firmProcessInfo
        except AttributeError:
            self._firmProcessInfo=firm_process_info.firm_process_info(self.sol(), 
                                                                      self.actionSurface())
        return self._firmProcessInfo
    def constructBaseMenu(self):
        try:
            b=self._constructBaseMenu
        except AttributeError:
            self._constructBaseMenu=construct_base_menu.construct_base_menu(self.sol(), 
                                                                            self.actionSurface())
        return self._constructBaseMenu
    def slot__clickBasePopulation(self):
        w=self.basePopulationInfo()
        w.create()
        self.active_window=w
        return
    def slot__clickBaseCompanies(self):
        w=self.baseListOfCompanies()
        w.create()
        self.active_window=w
        return
    def slot__clickBaseFirms(self):
        w=self.baseListOfFirms()
        w.create()
        self.active_window=w
        return
    def slot__clickBaseMarket(self):
        w=self.baseAndFirmMarketWindow()
        w.create()
        self.active_window=w
        return
    def slot__clickBaseBuild(self):
        w=self.baseBuildMenu()
        w.create()
        self.active_window=w
        return
    def slot__clickFirmMarket(self):
        w=self.baseAndFirmMarketWindow()
        w.create()
        self.active_window=w
        return
    def createFirmSubcommandbox(self):
        self.buttonlinks = ["firm_process_info","base_and_firm_market_window","firm_trade_partners_info"]
        self.buttonnicenames = ["production","market","trade partners"]
        i=0
        b=button.button("production", 
                        self.subcommand_surface,
                        fixed_size = (self.subcommand_surface.get_width()-20,
                                      35), 
                        topleft = (10, i * 40 + 10))
        self.subcommand_buttons["production"] = b
        signaller.connect(b,"signal__clicked",self.slot__clickFirmProduction)
        i=i+1
        b=button.button("market", 
                        self.subcommand_surface,
                        fixed_size = (self.subcommand_surface.get_width()-20,
                                      35), 
                        topleft = (10, i * 40 + 10))
        self.subcommand_buttons["market"] = b
        signaller.connect(b,"signal__clicked",self.slot__clickFirmMarket)
        i=i+1
        b=button.button("trade partners", 
                        self.subcommand_surface,
                        fixed_size = (self.subcommand_surface.get_width()-20,
                                      35), 
                        topleft = (10, i * 40 + 10))
        self.subcommand_buttons["trade partners"] = b
        signaller.connect(b,"signal__clicked",self.slot__clickFirmTradePartners)
        return
    def createBaseSubcommandbox(self):
        self.buttonlinks = ["base_population_info","base_list_of_companies","base_list_of_firms",
                            "base_and_firm_market_window","base_build_menu"]
        self.buttonnicenames = ["population","companies","firms","market","build"]
        i=0
        b=button.button("population", 
                        self.subcommand_surface,
                        fixed_size = (self.subcommand_surface.get_width()-20,
                                      35), 
                        topleft = (10, i * 40 + 10))
        self.subcommand_buttons["population"] = b
        signaller.connect(b,"signal__clicked",self.slot__clickBasePopulation)
        i=i+1
        b=button.button("companies", 
                        self.subcommand_surface,
                        fixed_size = (self.subcommand_surface.get_width()-20,
                                      35), 
                        topleft = (10, i * 40 + 10))
        self.subcommand_buttons["companies"] = b
        signaller.connect(b,"signal__clicked",self.slot__clickBaseCompanies)
        i=i+1
        b=button.button("firms", 
                        self.subcommand_surface,
                        fixed_size = (self.subcommand_surface.get_width()-20,
                                      35), 
                        topleft = (10, i * 40 + 10))
        self.subcommand_buttons["firms"] = b
        signaller.connect(b,"signal__clicked",self.slot__clickBaseFirms)
        i=i+1
        b=button.button("market", 
                        self.subcommand_surface,
                        fixed_size = (self.subcommand_surface.get_width()-20,
                                      35), 
                        topleft = (10, i * 40 + 10))
        self.subcommand_buttons["market"] = b
        signaller.connect(b,"signal__clicked",self.slot__clickBaseMarket)
        i=i+1
        b=button.button("build", 
                        self.subcommand_surface,
                        fixed_size = (self.subcommand_surface.get_width()-20,
                                      35), 
                        topleft = (10, i * 40 + 10))
        self.subcommand_buttons["build"] = b
        signaller.connect(b,"signal__clicked",self.slot__clickBaseBuild)
        return
    def slot__clickCompanyOwnershipInfo(self):
        w=self.companyOwnershipInfo()
        w.create()
        self.active_window=w
        return
    def slot__clickCompanyFinancialInfo(self):
        w=self.companyFinancialInfo()
        w.create()
        self.active_window=w
        return
    def slot__clickCompanyOwnedFirms(self):
        w=self.companyListOfFirms()
        w.create()
        self.active_window=w
        return
    def createCompanySubcommandbox(self):
        self.buttonlinks = ["company_ownership_info","company_financial_info","company_list_of_firms"]
        self.buttonnicenames = ["ownership info","financial info","owned firms"]
        i=0
        b=button.button("ownership info", 
                        self.subcommand_surface,
                        fixed_size = (self.subcommand_surface.get_width()-20,
                                      35), 
                        topleft = (10, i * 40 + 10))
        self.subcommand_buttons["ownership_info"] = b
        signaller.connect(b,"signal__clicked",self.slot__clickCompanyOwnershipInfo)
        i=i+1
        b=button.button("financial info", 
                        self.subcommand_surface,
                        fixed_size = (self.subcommand_surface.get_width()-20,
                                      35), 
                        topleft = (10, i * 40 + 10))
        self.subcommand_buttons["financial info"] = b
        signaller.connect(b,"signal__clicked",self.slot__clickCompanyFinancialInfo)
        i=i+1
        b=button.button("owned firms", 
                        self.subcommand_surface,
                        fixed_size = (self.subcommand_surface.get_width()-20,
                                      35), 
                        topleft = (10, i * 40 + 10))
        self.subcommand_buttons["owned firms"] = b
        signaller.connect(b,"signal__clicked",self.slot__clickCompanyOwnedFirms)
        return
    def create_subcommandbox(self):    
        """
        creates the right-side menu lower subcommand box. this is specific for the navigation window context
        such as for example base information and such
        """
        self.subcommand_surface.fill((150,150,150))
        self.subcommand_buttons = {}
        if self.sol().display_mode == "base":
            self.createBaseSubcommandbox()
        elif self.sol().display_mode == "firm":
            self.createFirmSubcommandbox()
        elif self.sol().display_mode == "company":
            self.createCompanySubcommandbox()
        else:
            pygame.display.flip()
            return
        pygame.display.flip()
    def basePopulationInfo(self):
        try:
            b=self._basePopulationInfo
        except AttributeError:
            self._basePopulationInfo=base_population_info.base_population_info(self.sol(), 
                                                                               self.actionSurface())
        return self._basePopulationInfo
    def subcommand_rect_clicked(self,event):
        print 'gui::subcommand_rect_clicked()'
        for button in self.subcommand_buttons.values():
            if button.rect().collidepoint((event.pos[0] - global_variables.window_size[0] + self.subcommand_rect[2], 
                                           event.pos[1] - self.subcommand_rect[1])) == 1:
                button.activate(None)
    def slot__showTradeWindow(self):
        w=self.tradeMenu()
        w.create()
        self.active_window=w
        return
    def tradeMenu(self):
        try:
            b=self._tradeMenu
        except AttributeError:
            self._tradeMenu=trade_window.trade_window(self.sol(), 
                                                      self.actionSurface())
        return self._tradeMenu
    def slot__showFileWindow(self):
        w=self.fileWindow()
        w.create()
        self.active_window=w
        return
    def slot__showCompanyWindow(self):
        w=self.companyWindow()
        w.create()
        self.active_window=w
        return
    def companyWindow(self):
        try:
            b=self._companyWindow
            pass
        except AttributeError:
            self._companyWindow=company_window.company_window(self.sol(), 
                                                              self.actionSurface())
        return self._companyWindow
