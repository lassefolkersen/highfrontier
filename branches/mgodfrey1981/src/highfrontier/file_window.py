import entry
import button
import fast_list
import togglebutton
import vscrollbar
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

class file_window():
    def solarSystem(self):
        return global_variables.solar_system
    """
    The file window. Can be toggled from commandbox. Quitting, saving, loading, settings and all the usual stuff you'd
    expect to find such a place.
    """
    def __init__(self,solar_system_object,action_surface):
        self.rect = pygame.Rect(50,50,400,500)
        self.action_surface = action_surface
        self.text_receiver = None 
        self.distribute_click_to_subwindow = None
        
        
        self.button_structure = {
                           "File menu":{
                                   "Save game":self.select_save_name,
                                   "Load game":self.select_game_to_load,
                                   "New game":self.new_game,
                                   "Automation settings":self.automation_settings,
                                   "Message settings":self.message_settings,
                                   "Quit game":"Quit game",
                                   "Game speed":self.game_speed_settings,
                                   "Catastrophes":"Catastrophe window"},
                           "Quit game":{
                                        "Ok":self.quit,
                                        "Cancel":"File menu",
                                        "Save first":self.select_save_name
                                    },
                           "Catastrophe window":{
                                                 "Global warming":self.raise_waters,
                                                 "Global cooling":self.lower_waters,
                                                 "Meteor strike":"Catastrophe window",
                                                 "Nuclear war":self.nuclear_war,
                                                 "Lunar explosion":self.nuclear_war,
                                                 "Skynet uprising":"Catastrophe window"
                                                 }
                           
                           }




    def create(self):
        """
        The creation function.  
        """
        self.button_instances_now = {}
        self.button_list_now = []
        self.distribute_click_to_subwindow = None
        self.position = "File menu"
        self.text_receiver = None
        self.draw()

    def draw(self):
        self.button_instances_now = {}
        pygame.draw.rect(self.action_surface, (150,150,150), self.rect)
        
        self.button_list_now = self.button_structure[self.position].keys()
        self.button_list_now.sort()
        
        for i, button_name in enumerate(self.button_list_now):
            if isinstance(self.button_structure[self.position][button_name], str): # has a submenu
                self.button_instances_now[button_name] = button.button(button_name,
                                                    self.action_surface,
                                                    self.go_to_submenu,
                                                    function_parameter = self.button_structure[self.position][button_name],
                                                    fixed_size = (self.rect[2] - 20, 35),
                                                    topleft = (10 + self.rect[0], i * 40 + 10 + self.rect[1])
                                                    )
            else: # has a subfunction
                self.button_instances_now[button_name] = button.button(button_name,
                                                    self.action_surface,
                                                    self.button_structure[self.position][button_name],
                                                    function_parameter = None,
                                                    fixed_size = (self.rect[2] - 20, 35),
                                                    topleft = (10 + self.rect[0], i * 40 + 10 + self.rect[1])
                                                    )
            
            
        pygame.display.flip()


    def go_to_submenu(self, label, function_parameter):
        """
        Function that accepts activations from buttons that leads to submenus
        """
        self.position = function_parameter
        self.draw()

    
    def receive_click(self,event):
        if self.distribute_click_to_subwindow is None:
            if isinstance(event.pos[1],int):
                index = (event.pos[1] - self.rect[1] - 10) / 40
                if index >= 0 and index < len(self.button_list_now):
                    button_pressed = self.button_list_now[index]
                    if button_pressed != "Empty space":
                        self.button_instances_now[button_pressed].activate(event.pos)
        else:
            self.distribute_click_to_subwindow.receive_click(event)
            if event.button == 3:
                if self.position == "Load menu":
                    self.solarSystem().load_solar_system(os.path.join("savegames",self.distribute_click_to_subwindow.selected))
    



    def quit(self,label,function_parameter):
        sys.exit(0)


    
            

    def select_save_name(self,label, function_parameter):
        """
        Prompts the player to input the name of the savegame file
        """
        
        pygame.draw.rect(self.action_surface, (150,150,150), self.rect)
        description = global_variables.standard_font.render("Enter savegame name:",True,(0,0,0))
        self.action_surface.blit(description, (10 + self.rect[0], 10 + self.rect[1]))
        
        self.button_list_now = ["Empty space","Name box","Ok"]
        self.button_instances_now = {}
        self.button_instances_now["Name box"] = entry.entry(self.action_surface, 
                             topleft = (10 + self.rect[0], 10 + 40 + self.rect[1]), 
                             width = self.rect[2] - 20, 
                             max_letters = global_variables.max_letters_in_company_names)

        self.text_receiver = self.button_instances_now["Name box"]
        self.button_instances_now["Name box"].active = True 
        
        self.button_instances_now["Ok"] = button.button(
                                    "Ok",
                                    self.action_surface,
                                    self.effectuate_save,
                                    function_parameter = None,
                                    fixed_size = (self.rect[2] - 20, 35),
                                    topleft = (10 + self.rect[0], 80 + 10 + self.rect[1])
                                    )
        pygame.display.flip() 
        
        
    def effectuate_save(self,label,function_parameter):
        save_game_name = self.button_instances_now["Name box"].text
        self.solarSystem().save_solar_system(os.path.join("savegames",save_game_name))
        self.create()
        

    def select_game_to_load(self, label, function_parameter):
        self.position = "Load menu"
        load_window = fast_list.fast_list(self.action_surface, os.listdir("savegames"), rect = self.rect)
        self.distribute_click_to_subwindow = load_window
                                                    

#    def effectuate_load(self):

        

    def new_game(self, label, function_parameter):
        raise Exception("should start new game, but this has not been implemented yet FIXME")







    def automation_settings(self,label,function_parameter):
        """
        The window that is shown when asking for automation_settings.
        First destroys the previous file window
        """
        
        
        
        if self.solarSystem().current_player is None:
            if self.solarSystem().message_printing["debugging"]:
                print_dict = {"text":"DEBUGGING: Game is in simulation mode so no changes can be made","type":"debugging"}
                self.solarSystem().messages.append(print_dict)
        else:
            pygame.draw.rect(self.action_surface, (150,150,150), self.rect)
            
            self.button_instances_now = {}
            self.button_list_now = []

            button_names = self.solarSystem().current_player.automation_dict.keys()

            for i, button_name in enumerate(button_names):
                self.button_list_now.append(button_name)
                
                self.button_instances_now[button_name] = togglebutton.togglebutton(button_name,
                                                          self.action_surface,
                                                          self.change_automation,
                                                          function_parameter = button_name,
                                                          fixed_size = (self.rect[2] - 20, 35),
                                                          topleft = (10 + self.rect[0], i * 40 + 10 + self.rect[1]),
                                                          pressed = self.solarSystem().current_player.automation_dict[button_name]
                                                    )
            
            
            self.button_list_now.append("Decision variables")
            self.button_instances_now["Decision variables"] = button.button(
                                                                           "Decision variables",
                   self.action_surface,
                   self.decision_variables,
                   function_parameter = None,
                   fixed_size = (self.rect[2] - 20, 35),
                   topleft = (10 + self.rect[0], (i + 1) * 40 + 10 + self.rect[1]),
                   )
            
            
            

    def change_automation(self,label,function_parameter):
        """
        Function that will effectuate the change of automation status
        """
        if self.solarSystem().current_player is None:
            raise Exception("No player selected")
        if function_parameter not in self.solarSystem().current_player.automation_dict.keys():
            raise Exception("The automation_type " + str(function_parameter) + " was not found in the automation_dict")
        previous_setting = self.solarSystem().current_player.automation_dict[function_parameter]
        self.solarSystem().current_player.automation_dict[function_parameter] = not previous_setting

        print_dict = {"text":"For " + self.solarSystem().current_player.name + " the " + str(function_parameter) + " was changed from " + str(previous_setting) + " to " + str(not previous_setting),"type":"general company info"}
        self.solarSystem().messages.append(print_dict)
#        self.manager.emit("update_infobox", None)
        
        

    def decision_variables(self,label,function_parameter):
        """
        The window that is shown when asking for decision_variables.
        """

        if self.solarSystem().current_player is None:
            if self.solarSystem().message_printing["debugging"]:
                print_dict = {"text":"DEBUGGING: Game is in simulation mode so no changes can be made","type":"debugging"}
                self.solarSystem().messages.append(print_dict)
        else:
            pygame.draw.rect(self.action_surface, (150,150,150), self.rect)
            decision_variables_window = fast_list.fast_list(self.action_surface, 
                                                                 self.solarSystem().current_player.company_database.keys(),
                                                                 rect = self.rect)

            self.distribute_click_to_subwindow = decision_variables_window                                            

            
        


    def check_and_save_decision_variables(self):
        """
        Function that checks that all variables in the entry boxes of the automation settings are integers between 1-100,
        and saves them if this is correct
        """
        
#        table = self.window
        all_passed_check = True
        for column_offset in [0,2]:
            for row_index in range(0,self.window.rows - 1): #don't count the last row with buttons
                if self.window.grid[(row_index, column_offset)] is not None:
                    name = self.window.grid[(row_index, column_offset)].text
                    value = self.window.grid[(row_index, column_offset + 1)].text
                    try:    int(value)
                    except: 
                        print_dict = {"text":"The value " + str(value) + " at " + str(name) + " is not integer","type":"general gameplay info"}
                        self.solarSystem().messages.append(print_dict)
                        self.manager.emit("update_infobox", None)
                        all_passed_check = False
                        break
                    else:   
                        pass
                    
                    value_as_int = int(value)
                    
                    if 1 <= value_as_int <= 100:
                        pass
                    else:
                        print_dict = {"text":"The value " + str(value) + " at " + str(name) + " is not between 1 and 100","type":"general gameplay info"}
                        self.solarSystem().messages.append(print_dict)
                        self.manager.emit("update_infobox", None)
                        all_passed_check = False
                        break
 
        if all_passed_check:
            print_dict = {"text":"The decision matrix has been updated for " + self.solarSystem().current_player.name,"type":"general gameplay info"}
            self.solarSystem().messages.append(print_dict)
            self.manager.emit("update_infobox", None)
            for column_offset in [0,2]:
                for row_index in range(0,self.window.rows - 1): #don't include rows with buttons
                    if self.window.grid[(row_index, column_offset)] is not None:
                        name = self.window.grid[(row_index, column_offset)].text
                        value = self.window.grid[(row_index, column_offset + 1)].text
                        value_as_int = int(value)
                        
                        self.solarSystem().current_player.company_database[name] = value_as_int
            
            self.exit(True)
            


    def message_settings(self, label, function_parameter):
        """
        Function that decides what messages should be shown
        """
        pygame.draw.rect(self.action_surface, (150,150,150), self.rect)

        button_names = self.solarSystem().message_printing.keys()

        self.button_instances_now = {}
        self.button_list_now = []

        for i, button_name in enumerate(button_names):
            self.button_list_now.append(button_name)
            
            self.button_instances_now[button_name] = togglebutton.togglebutton(button_name,
                                                      self.action_surface,
                                                      self.change_message_setting,
                                                      function_parameter = button_name,
                                                      fixed_size = (self.rect[2] - 20, 35),
                                                      topleft = (10 + self.rect[0], i * 40 + 10 + self.rect[1]),
                                                      pressed = self.solarSystem().message_printing[button_name]
                                                )


    def change_message_setting(self, label, function_parameter):                        
        """
        Function that will effectuate the change of message settings
        """
        if function_parameter not in self.solarSystem().message_printing.keys():
            raise Exception("The message type " + str(function_parameter) + " was not found in the message_printing dict")
        previous_setting = self.solarSystem().message_printing[function_parameter]
        self.solarSystem().message_printing[function_parameter] = not previous_setting

        print_dict = {"text":"The show-settings for " + str(function_parameter) + " was changed from " + str(previous_setting) + " to " + str(not previous_setting),"type":"general gameplay info"}
        self.solarSystem().messages.append(print_dict)
#        self.manager.emit("update_infobox", None)
                        
    
        

    

        
    def game_speed_settings(self, label, function_parameter):
        """
        The window that is shown when asking for time delay settings
        Time delay settings is defined as a value between 0 and 100 with 100 being the fastest.
        It translates into the self.solarSystem().step_delay_time
        which is a value between 0 (perform game-iteration at every loop-iteration) and infinity (but then the game will stop)
        a loop-iteration is the time it takes to react to clicks etc + 15 milliseconds (but check value pygame.time.delay in main 
        document to be sure). A game-iteration is all the movement of planets, thinking of companies etc.
        
        We here define the range of self.solarSystem().step_delay_time as given in step_delay_time_range. This is certainly up to testing.
        In any case it means that the lowest value of step_delay_time_range equals time delays settings of 100 (max speed) and the highest
        value of step_delay_time_range equals time delay settings of 0 (slowest speed)
        """
        pygame.draw.rect(self.action_surface, (150,150,150), self.rect)

        delay_range = (10,500)

        old_game_speed = self.solarSystem().step_delay_time

        button_names = self.solarSystem().message_printing.keys()
        
        
        fastest = global_variables.standard_font.render("Fastest",True,(0,0,0))
        self.action_surface.blit(fastest, (self.rect[0] + 50, self.rect[1] + 40))

        slowest = global_variables.standard_font.render("Slowest",True,(0,0,0))
        self.action_surface.blit(slowest, (self.rect[0] + 50, self.rect[1] + self.rect[3]-  50))
        
        
        def execute(label, function_parameter):
            game_speed = self.distribute_click_to_subwindow.position / 30
            self.solarSystem().step_delay_time = self.distribute_click_to_subwindow.position
        
        self.distribute_click_to_subwindow = vscrollbar.vscrollbar (self.action_surface,
                                                execute,
                                                topleft = (self.rect[0] + 10, self.rect[1] + 30),
                                                length_of_bar_in_pixel = self.rect[3] - 60,
                                                range_of_values = delay_range,
                                                start_position = old_game_speed
                                                )

#    def catastrophe_window(self, label, function_parameter):
#        """
#        The window that is shown when asking for catastrophes
#        """
#        
#        button_names = ["Global warming","Global cooling","Meteor strike","Nuclear war","Lunar explosion","Skynet uprising"]
#        button_functions = [self.raise_waters,self.lower_waters,self.exit,self.nuclear_war,self.exit,self.exit]
#        
#        for i, button_name in enumerate(button_names):
#            temp_button = Button(button_name)
#            temp_button.connect_signal(SIG_CLICKED,button_functions[i])
#            max_width = max(max_width,temp_button.width)
#            list_of_children.append(temp_button)
#        
#        for button in list_of_children:
#            button.set_minimum_size(max_width,button.size[1])
#        
#        ok_button = Button("Ok")
#        ok_button.connect_signal(SIG_CLICKED,self.exit,True)
#        
#        self.window.set_children(list_of_children + [Label(""), ok_button])
#
#        self.renderer.add_widget(self.window)

    def raise_waters(self,label,function_parameter):
        """
        Function to raise waters
        """
        sol = self.solarSystem()

        if sol.display_mode == "planetary":
            sol.current_planet.change_water_level(sol.current_planet.water_level + 0.5)
            surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
        else:
            return
        self.action_surface.blit(surface,(0,0))
        pygame.display.flip()


    def lower_waters(self,label,function_parameter):
        sol = self.solarSystem()

        if sol.display_mode == "planetary":
            sol.current_planet.change_water_level(sol.current_planet.water_level - 0.5)                        
            surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
        else:
            return
        self.action_surface.blit(surface,(0,0))
        pygame.display.flip()


    def nuclear_war(self,label,function_parameter):
        sol = self.solarSystem()
        if sol.display_mode == "planetary":
            earth = sol.planets["earth"]
            base_names_chosen = ["stockholm","glasgow","bremen","rotterdam","stuttgart","genoa"]
            bases_chosen = {}
            for base_name_chosen in base_names_chosen:
                bases_chosen[base_name_chosen] = earth.bases[base_name_chosen]
            earth.explode(56,10,bases_chosen,self.action_surface)
        else:
            return

        

    def quit_dialog(self):
        """
        The window that is shown when quittting.
        """
        def _result (result, dialog):
            if result == DLGRESULT_OK:
                sys.exit(0)
            elif result == DLGRESULT_CANCEL:
                dialog.destroy ()
            elif result == DLGRESULT_USER:
                dialog.destroy ()
        buttons = [Button ("#OK"), Button ("#Cancel"), Button ("#Save first")]
        results = [DLGRESULT_OK, DLGRESULT_CANCEL, DLGRESULT_USER]
        dialog = GenericDialog ("Generic dialog", buttons, results)
        lbl = Label ("Do you really want to quit?")
        dialog.content.add_child (lbl)
        dialog.connect_signal (SIG_DIALOGRESPONSE, _result, dialog)
        dialog.topleft = 30, 30
        dialog.depth = 1
        return dialog
