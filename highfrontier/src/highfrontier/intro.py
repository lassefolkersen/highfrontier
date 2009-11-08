



from pygame.locals import *
import pygame
import solarsystem
import planet
import global_variables
import os
import sys
import datetime
import gui_components
import main
import time
import primitives



class Intro_gui():
    """
    The class that holds everything on introduction, starting with the introduction sequence
    """
    
    def __init__(self):
        self.stepsize = 50
        self.company_capital = None
        self.company_name = None
        self.save_game_to_load = None
        self.run_background_spin = True
        self.gui_rect = pygame.Rect(global_variables.window_size[0] / 2 - 90,global_variables.window_size[1] / 3, 180,180)
        self.text_receiver = None
        pygame.init()
        if global_variables.fullscreen:
            self.window = pygame.display.set_mode(global_variables.window_size,FULLSCREEN) 
        else:
            self.window = pygame.display.set_mode(global_variables.window_size)
        icon = pygame.image.load(os.path.join("images","window_icon.png"))
        pygame.display.set_icon(icon) 

        if global_variables.fullscreen:
            pygame.time.delay(1000)

        self.initialize_intro_sequence()
        
        self.intro_sequence()

        self.create_intro_gui()
        

        i = 0
        while True:
            
            if self.run_background_spin:
                pygame.time.delay(self.stepsize)
                self.background_sequence(i)
                i = i + 1
                if i >= self.steps_loop:
                    i = 0
            events = pygame.event.get()
            for event in events: 
                if event.type == QUIT: 
                    sys.exit(0)
                if event.type == 5: #mouse down event
                    self.receive_click(event)

                if event.type == 2: #key down event
                    if self.text_receiver is not None:
                        self.text_receiver.receive_text(event)



    def receive_click(self, event):
        if self.gui_rect.collidepoint(event.pos) == 1:
            for button in self.buttons.values():
                if button.rect.collidepoint(event.pos) == 1:
                    if isinstance(button, gui_components.fast_list):
                        button.receive_click(event)
                    elif isinstance(button, gui_components.radiobuttons):
                        
                        button.activate(event.pos)
                    else:
                        button.activate(event)
                

    def triplify_number(self,number):
        if len(str(number)) == 1:
            number = "00" + str(number)
        elif len(str(number)) == 2:
            number = "0" + str(number)
        elif len(str(number)) == 3:
            number = str(number)
        else:
            raise Exception("Bad number: " + str(number))
        return number


    def set_eccentricity(self,solar_system_instance, new_eccentricity):
        """
        Function that forces the eccentricity of all planets in a solar system to another value
        """
        if new_eccentricity >= 1:
            raise Exception("Too high eccentricity")
        for planet_instance in solar_system_instance.planets.values():
            if ["original eccentricity"] not in planet_instance.planet_data.keys():
                eccentricity = planet_instance.planet_data["eccentricity"]
                if planet_instance.name != "sun":
                    planet_instance.planet_data["original eccentricity"] = eccentricity
            planet_instance.planet_data["eccentricity"] = new_eccentricity

    def initialize_intro_sequence(self):
        """
        Function that checks if all pictures needed are present for the intro sequence
        """

        self.steps_system = 74
        self.steps_both = 9
        self.steps_planet = 51

        
        all_ok = True
        for i in range(self.steps_system + self.steps_both + self.steps_planet):
            path = os.path.join("intro","intro_file_" + str(self.triplify_number(i)) + ".jpg")
            if not os.access(path,os.R_OK):
                all_ok = False
                
        
        
        if not all_ok:
            print "WARNING: Some files were missing from the intro directory. It will be recreated. This will take time."
            self.sol = solarsystem.solarsystem(global_variables.start_date)
            
            
            
            #The part where only the solar system is visible
            for i in range(self.steps_system):
                eccentricity = 1 - (((i+1) / float(500)) ** 2)
                zoom = (1.2 ** (i+1)) / 100
                print "at i = " + str(i) + " eccentricity: " + str(eccentricity) + " zoom: " + str(zoom)
                
                self.set_eccentricity(self.sol,eccentricity)
                surface = self.sol.draw_solar_system(zoom_level=zoom,date_variable=self.sol.current_date,center_object="earth")
                pickle_final_name_and_path = os.path.join("intro","intro_file_" + str(self.triplify_number(i)) + ".jpg")
                pygame.image.save(surface,pickle_final_name_and_path)
            
            
            
            #The part where both the planet and system is visible
            earth = self.sol.planets["earth"]
            for i in range(self.steps_both):
                northern_inclination = -40 + (i+1) / 2 
                eastern_inclination = (i+1) * 5 - 50
                projection_scaling = 3 + (i+1) * 4
                if eastern_inclination >= 180:
                    eastern_inclination = eastern_inclination - 360

                eccentricity = 1 - ((((i+1) + self.steps_system) / float(500)) ** 2)
                zoom = (1.2 ** ((i+1) + self.steps_system)) / 100

                self.set_eccentricity(sol,eccentricity)
                
                surface = self.sol.draw_solar_system(zoom_level=zoom,date_variable=self.sol.current_date,center_object="earth")
                surface.blit(pygame.Surface((projection_scaling*4,projection_scaling*4)),(global_variables.window_size[0] / 2 - projection_scaling*2, global_variables.window_size[1] / 2 - projection_scaling*2))
                
                
                print " at i " + str(i) + " north is " + str(northern_inclination) + " and east is " + str(eastern_inclination) + " and scaling is " + str(projection_scaling)
                projections = earth.plane_to_sphere_total(eastern_inclination,northern_inclination,projection_scaling)
                planet_surface = earth.draw_image(eastern_inclination,northern_inclination,projection_scaling, fast_rendering=False, plane_to_sphere=projections)
                surface.blit(planet_surface, (global_variables.window_size[0] / 2 - projection_scaling/2, global_variables.window_size[1] / 2 - projection_scaling/2))
                pickle_final_name_and_path = os.path.join("intro","intro_file_" + str(self.triplify_number(i+self.steps_system)) + ".jpg")
                pygame.image.save(surface,pickle_final_name_and_path)
                
            
            #The part where only on the planet is visible
            for i in range(self.steps_planet):
                northern_inclination = -30 + (i+1) / 2
                eastern_inclination = (i+1) * 5
                projection_scaling = 43 + (i+1) * 6
                if eastern_inclination >= 180:
                    eastern_inclination = eastern_inclination - 360
                print " at i " + str(i) + " north is " + str(northern_inclination) + " and east is " + str(eastern_inclination) + " and scaling is " + str(projection_scaling)
                projections = earth.plane_to_sphere_total(eastern_inclination,northern_inclination,projection_scaling)
                planet_surface = earth.draw_image(eastern_inclination,northern_inclination,projection_scaling, fast_rendering=False, plane_to_sphere=projections)
                surface = pygame.Surface(global_variables.window_size)
                surface.blit(planet_surface, (global_variables.window_size[0] / 2 - projection_scaling/2, global_variables.window_size[1] / 2 - projection_scaling/2))
                pickle_final_name_and_path = os.path.join("intro","intro_file_" + str(self.triplify_number(i+self.steps_system+self.steps_both)) + ".jpg")
                pygame.image.save(surface,pickle_final_name_and_path)

                
        
        
        #checking the loop picture files
        northern_inclination_start = -30 + (self.steps_planet+1) / 2
        eastern_inclination_start = (self.steps_planet+1) * 5
        projection_scaling_start = 43 + (self.steps_planet+1) * 6

        self.steps_loop = 360 / 5 #because we tilt 5 each step
        
        
        all_ok = True
        for i in range(self.steps_loop):
            path = os.path.join("intro","loop_file_" + str(self.triplify_number(i)) + ".jpg")
            if not os.access(path,os.R_OK):
                all_ok = False
                
        if not all_ok:
            try:    self.sol
            except:
                self.sol = solarsystem.solarsystem(global_variables.start_date)
            else:
                pass
            earth = self.sol.planets["earth"]
            for i in range(self.steps_loop):
                eastern_inclination = eastern_inclination_start + i * 5
                northern_inclination = northern_inclination_start
                projection_scaling = projection_scaling_start
    
                if eastern_inclination >= 180:
                    eastern_inclination = eastern_inclination - 360
                print " at i " + str(i) + " north is " + str(northern_inclination) + " and east is " + str(eastern_inclination) + " and scaling is " + str(projection_scaling)
                projections = earth.plane_to_sphere_total(eastern_inclination,northern_inclination,projection_scaling)
                planet_surface = earth.draw_image(eastern_inclination,northern_inclination,projection_scaling, fast_rendering=False, plane_to_sphere=projections)
                surface = pygame.Surface(global_variables.window_size)
                surface.blit(planet_surface, (global_variables.window_size[0] / 2 - projection_scaling/2, global_variables.window_size[1] / 2 - projection_scaling/2))
                pickle_final_name_and_path = os.path.join("intro","loop_file_" + str(self.triplify_number(i)) + ".jpg")
                pygame.image.save(surface,pickle_final_name_and_path)

                
    
    def intro_sequence(self):
        """
        This function will run the intro sequence by checking for the presence of aptly named pictures in /intro folder.
     
        """
        #Runing the simulation
        skip_intro = False
        for i in range(self.steps_system + self.steps_both + self.steps_planet):
            events = pygame.event.get()
            for event in events:
                if event.type in [2,5]: #key or mouse down event
                    skip_intro = True
            if not skip_intro:
                path = os.path.join("intro","intro_file_" + str(self.triplify_number(i)) + ".jpg")
                surface = pygame.image.load(path)
                self.window.blit(surface, (0,0))
                pygame.display.flip()
#                self.mainscreen.set_picture(surface)
#                self.renderer.update()
                pygame.time.delay(self.stepsize)

        
        
        

    def background_sequence(self,i):
        """
        Function that spins the earth in the background of the intro_gui
        i is in the range of self.steps_loop
        """
        #starting positions from intro_sequence
        #Runing the simulation
        path = os.path.join("intro","loop_file_" + str(self.triplify_number(i)) + ".jpg")
        surface = pygame.image.load(path)
        
        
        left_rect = pygame.Rect(0,0,self.gui_rect[0],global_variables.window_size[1])
        right_rect = pygame.Rect(self.gui_rect[0] + self.gui_rect[2],0,global_variables.window_size[0]-self.gui_rect[0]-self.gui_rect[2],global_variables.window_size[1])
        top_rect = pygame.Rect(0,0,global_variables.window_size[0],self.gui_rect[1])
        bottom_rect = pygame.Rect(0,self.gui_rect[1] + self.gui_rect[3],global_variables.window_size[0],global_variables.window_size[1]-self.gui_rect[3] - top_rect[3])
        for rect in [left_rect,right_rect,top_rect,bottom_rect]:
            self.window.set_clip(rect)
            self.window.blit(surface, (0,0))
        self.window.set_clip(None)

        
        
        pygame.display.flip()
        pygame.time.delay(self.stepsize)
        
                
                
            


#    def select_game_to_load_callback(self):
#        self.exit()
#        
#        self.load_window = gui_components.fast_list(self.renderer)
#        
#        self.load_window.receive_data(os.listdir("savegames"))
#        self.load_window.topleft = (global_variables.window_size[0] / 2 - self.load_window.list_size[0] / 2, 100) 
#        self.load_window.create_fast_list()
#
#        
#        ok_button = Button("Ok")
#        ok_button.connect_signal(SIG_CLICKED,self.effectuate_load_callback)
#        cancel_button = Button("Cancel")
#        cancel_button.connect_signal(SIG_CLICKED,self.create_intro_gui)
#
#        
#        self.load_button = HFrame()
#        self.load_button.set_children([ok_button,cancel_button])
#        self.load_button.topleft = (global_variables.window_size[0] / 2 - self.load_button.size[0] / 2, self.load_window.topleft[1] + self.load_window.list_size[1] + 50)
#        self.renderer.add_widget(self.load_button)

    def effectuate_load_callback(self):
        load_file_name = self.load_window.selected
        if load_file_name is not None:
            main.start_loop(load_previous_game = os.path.join("savegames",load_file_name))
            
            #self.solar_system_object_link.load_solar_system(load_file_name)

    def load_callback(self, label, function_parameter):
        self.gui_rect = pygame.Rect(global_variables.window_size[0] / 2 - 150,global_variables.window_size[1] / 3 - 50, 300,300)
        pygame.draw.rect(self.window, (212,212,212), self.gui_rect)
        
        
        load_window = gui_components.fast_list(self.window, os.listdir("savegames"), rect = pygame.Rect(self.gui_rect[0], self.gui_rect[1], self.gui_rect[2], self.gui_rect[3] - 50))

        
        self.buttons = {}
        
        self.buttons["load_window"] = load_window
        self.buttons["ok"] = gui_components.button("ok", 
                              self.window, 
                              self.load_game, 
                              function_parameter = load_window, 
                              topleft = (self.gui_rect[0] + self.gui_rect[2] - 100,self.gui_rect[1] + self.gui_rect[3] - 40), 
                              fixed_size = None)

        self.buttons["cancel"] = gui_components.button("cancel", 
                              self.window, 
                              self.create_intro_gui, 
                              function_parameter = None, 
                              topleft = (self.gui_rect[0] + self.gui_rect[2] - 65,self.gui_rect[1] + self.gui_rect[3] - 40), 
                              fixed_size = None)

    def load_game(self, label, load_window):
        main.start_loop(load_previous_game = os.path.join("savegames",load_window.selected_name))
    
    def game_settings_callback(self, label, function_parameter):
        pass
    
    
    def quit_callback(self, label, function_parameter):
        sys.exit(0)

    

    
    def create_intro_gui(self, label = None, function_parameter = None):
        """
        The GUI part of starting up the game
        """
        #reset gui_rect in case it was altered
        self.gui_rect = pygame.Rect(global_variables.window_size[0] / 2 - 90,global_variables.window_size[1] / 3, 180,180)
        self.text_receiver = None
        pygame.draw.rect(self.window, (212,212,212), self.gui_rect)

        pygame.draw.line(self.window, (255,255,255), (self.gui_rect[0], self.gui_rect[1]), (self.gui_rect[0] + self.gui_rect[2], self.gui_rect[1]),2)        
        pygame.draw.line(self.window, (255,255,255), (self.gui_rect[0], self.gui_rect[1]), (self.gui_rect[0], self.gui_rect[1] + self.gui_rect[3]),2)

        
        button_names= ["New game","Load game","Game settings","Quit game"]
        button_functions = [self.ask_company_type,self.load_callback,self.game_settings_callback,self.quit_callback]
        
        self.buttons = {}
        
        for i, button_name in enumerate(button_names):
            self.buttons[button_name] = gui_components.button(button_name, 
                                  self.window, 
                                  button_functions[i], 
                                  function_parameter = None, 
                                  topleft = (self.gui_rect[0] + 25,self.gui_rect[1] + i * 35 + 25), 
                                  fixed_size = (130,30))
                                  
        


    def ask_company_type(self,label,function_parameter):
        pygame.draw.rect(self.window, (212,212,212), self.gui_rect)
        
        title = global_variables.standard_font.render("Type of company:",True,(0,0,0))
        self.window.blit(title, (self.gui_rect[0] + 10, self.gui_rect[1] + 10))
        

        def dummy_function_for_radiobuttons(label, function_parameter):
            pass
        self.buttons = {}
        self.buttons["type_selector"] = gui_components.radiobuttons(
                                    ["Private company","Country"],
                                    surface = self.window, 
                                    function = dummy_function_for_radiobuttons,
                                    function_parameter = None, 
                                    topleft = (self.gui_rect[0] + 10, self.gui_rect[1] + 40), 
                                    selected = None)
        self.buttons["ok"] = gui_components.button("ok", 
                              self.window, 
                              self.decide_company_type, 
                              function_parameter = None, 
                              topleft = (self.gui_rect[0] + self.gui_rect[2] - 100,self.gui_rect[1] + self.gui_rect[3] - 40), 
                              fixed_size = None)
        self.buttons["cancel"] = gui_components.button("cancel", 
                              self.window, 
                              self.create_intro_gui, 
                              function_parameter = None, 
                              topleft = (self.gui_rect[0] + self.gui_rect[2] - 65,self.gui_rect[1] + self.gui_rect[3] - 40), 
                              fixed_size = None)




    def decide_company_type(self, label, function_parameter):
        #creating list of current countries
        data_file_name = os.path.join("data","base_data","earth.txt")
        if os.access(data_file_name,os.R_OK):
            read_base_database = primitives.import_datasheet(data_file_name)
        else:
            raise Exception("The intro script couldn't access:" + str(data_file_name))
        self.countries = []
        for entry in read_base_database.values():
            if entry["country"] not in self.countries:
                self.countries.append(entry["country"])
        self.countries.sort()

        
        if self.buttons["type_selector"].selected == "Private company":
            self.ask_company_name(None,None)
            self.is_country = False
        elif self.buttons["type_selector"].selected == "Country":
            self.ask_country_name(None,None)
            self.is_country = True
        else:
            raise Exception("unknown company type selected: ",self.buttons["type_selector"].selected)




    
    def ask_country_name(self,label,function_parameter):
        self.gui_rect = pygame.Rect(global_variables.window_size[0] / 2 - 150,global_variables.window_size[1] / 3 - 50, 300,300)
        pygame.draw.rect(self.window, (212,212,212), self.gui_rect)

        country_window = gui_components.fast_list(self.window, self.countries, rect = pygame.Rect(self.gui_rect[0], self.gui_rect[1], self.gui_rect[2], self.gui_rect[3] - 50))
        
        self.buttons = {}
        self.buttons["country_window"] = country_window
        self.buttons["ok"] = gui_components.button("ok", 
                              self.window, 
                              self.ask_company_capital, 
                              function_parameter = None, 
                              topleft = (self.gui_rect[0] + self.gui_rect[2] - 100,self.gui_rect[1] + self.gui_rect[3] - 40), 
                              fixed_size = None)

        self.buttons["cancel"] = gui_components.button("cancel", 
                              self.window, 
                              self.create_intro_gui, 
                              function_parameter = None, 
                              topleft = (self.gui_rect[0] + self.gui_rect[2] - 65,self.gui_rect[1] + self.gui_rect[3] - 40), 
                              fixed_size = None)

    

    def ask_company_name(self,label, function_parameter, give_warning = False):
        

        pygame.draw.rect(self.window, (212,212,212), self.gui_rect)
        
        title = global_variables.standard_font.render("Name of company:",True,(0,0,0))
        self.window.blit(title, (self.gui_rect[0] + 10, self.gui_rect[1] + 10))

        self.text_receiver = gui_components.entry(self.window, 
                             (self.gui_rect[0] + 10, self.gui_rect[1] + 45), 
                             self.gui_rect[2] - 20, 
                             global_variables.max_letters_in_company_names)
        

        self.buttons = {}
        self.buttons["ok"] = gui_components.button("ok", 
                              self.window, 
                              self.ask_company_capital, 
                              function_parameter = None, 
                              topleft = (self.gui_rect[0] + self.gui_rect[2] - 100,self.gui_rect[1] + self.gui_rect[3] - 40), 
                              fixed_size = None)

        self.buttons["cancel"] = gui_components.button("cancel", 
                              self.window, 
                              self.create_intro_gui, 
                              function_parameter = None, 
                              topleft = (self.gui_rect[0] + self.gui_rect[2] - 65,self.gui_rect[1] + self.gui_rect[3] - 40), 
                              fixed_size = None)

        if give_warning:
            warning_label = global_variables.standard_font_small.render("No double space, no blanks",True,(0,0,0))
            self.window.blit(warning_label, (self.gui_rect[0] + 10, self.gui_rect[1] + 90))
            pygame.display.flip()
        
        
    
    def ask_company_capital(self, label, function_parameter, give_warning = False):
        if "country_window" in self.buttons and self.is_country:
            company_name = self.buttons["country_window"].selected
            
        elif self.text_receiver is not None and not self.is_country:
            company_name = self.text_receiver.text
        else:
            raise Exception("Could not figure out whether country or private company was selected")
            
        
        all_ok = True
        if not (0 < len(company_name) <= global_variables.max_letters_in_company_names):
            all_ok = False
            
        if company_name.find("  ") != -1: #somewhere it is used that there are two double spaces, so we can't allow that in a companyname
            all_ok = False
        
        if company_name in self.countries and not self.is_country:
            all_ok = False
        
        if all_ok:
            pygame.draw.rect(self.window, (212,212,212), self.gui_rect)
            
            title = global_variables.standard_font.render("Starting capital:",True,(0,0,0))
            self.window.blit(title, (self.gui_rect[0] + 10, self.gui_rect[1] + 10))
    
            self.text_receiver = gui_components.entry(self.window, 
                                 (self.gui_rect[0] + 10, self.gui_rect[1] + 45), 
                                 self.gui_rect[2] - 20, 
                                 global_variables.max_letters_in_company_names,
                                 starting_text = "10000000")
            
    
            self.buttons = {}
            self.buttons["ok"] = gui_components.button("ok", 
                                  self.window, 
                                  self.start_new_game, 
                                  function_parameter = None, 
                                  topleft = (self.gui_rect[0] + self.gui_rect[2] - 100,self.gui_rect[1] + self.gui_rect[3] - 40), 
                                  fixed_size = None)
    
            self.buttons["cancel"] = gui_components.button("cancel", 
                                  self.window, 
                                  self.create_intro_gui, 
                                  function_parameter = None, 
                                  topleft = (self.gui_rect[0] + self.gui_rect[2] - 65,self.gui_rect[1] + self.gui_rect[3] - 40), 
                                  fixed_size = None)

            
            
            self.company_name = company_name
            
            if give_warning:
                warning_label = global_variables.standard_font_small.render("Starting capital must be an",True,(0,0,0))
                self.window.blit(warning_label, (self.gui_rect[0] + 10, self.gui_rect[1] + 90))
                warning_label2 = global_variables.standard_font_small.render("integer above zero",True,(0,0,0))
                self.window.blit(warning_label2, (self.gui_rect[0] + 10, self.gui_rect[1] + 100))

                pygame.display.flip()
        else:
            self.ask_company_name(None, None, give_warning=True)
            





    def start_new_game(self, label, function_parameter):
        company_capital = self.text_receiver.text
        
        
        all_ok = True
        try:    int(company_capital)
        except: all_ok = False
        else:   pass
        
        
        if all_ok:
            if 0 >= int(company_capital):
                all_ok = False
        
        if all_ok:
            self.company_capital = int(company_capital)
            main.start_loop(company_name = str(self.company_name), company_capital = self.company_capital, load_previous_game = None)#os.path.join("pickledmiscellanous","A_small_test_game"))
            

            
        else:
            self.ask_company_capital(None, None, give_warning=True)

            
intro_gui = Intro_gui()