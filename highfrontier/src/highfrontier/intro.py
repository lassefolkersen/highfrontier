



from pygame.locals import *
from ocempgui.widgets import *
from ocempgui.events import EventManager
from ocempgui.object import BaseObject
from ocempgui.widgets.Constants import *
from ocempgui.events import Signals
#import threading
import pygame
import solarsystem
import planet
import global_variables
import os
import sys
import datetime
import gui_extras
import main
import time



class Intro_gui():
    """
    The class that holds everything on introdction, starting with the introduction sequence
    """
    
    def __init__(self):
#        BaseObject.__init__(self)
        self.stepsize = 50
        self.manager = EventManager()
        self.company_capital = None
        self.company_name = None
        self.save_game_to_load = None
        self.run_background_spin = True
#        self.manager = manager
        
        pygame.init()
        
        self.renderer = Renderer ()
        self.renderer.title = "Intro"
        if global_variables.fullscreen:
            window = pygame.display.set_mode(global_variables.window_size,FULLSCREEN) 
        else:
            window = pygame.display.set_mode(global_variables.window_size)
        self.renderer.screen = pygame.display.get_surface()
        icon = pygame.image.load(os.path.join("images","window_icon.png"))
        pygame.display.set_icon(icon) 

        self.surface = pygame.Surface(global_variables.window_size)
        self.mainscreen = ImageLabel(self.surface)
        self.mainscreen.set_picture(self.surface)
        self.renderer.add_widget(self.mainscreen)
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

                self.renderer.distribute_events(*events)

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
            if not os.access(path,1):
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
            if not os.access(path,1):
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
        If all these are not found it will set out to re-create them and this can take some time.
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
                self.mainscreen.set_picture(surface)
                self.renderer.update()
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
        self.mainscreen.set_picture(surface)
        self.renderer.update()
        pygame.time.delay(self.stepsize)
        
                
                
            


    def select_game_to_load_callback(self):
        self.exit()
        
        self.load_window = gui_extras.fast_list(self.renderer)
        
        self.load_window.receive_data(os.listdir("savegames"))
        self.load_window.topleft = (global_variables.window_size[0] / 2 - self.load_window.list_size[0] / 2, 100) 
        self.load_window.create_fast_list()

        
        ok_button = Button("Ok")
        ok_button.connect_signal(SIG_CLICKED,self.effectuate_load_callback)
        cancel_button = Button("Cancel")
        cancel_button.connect_signal(SIG_CLICKED,self.create_intro_gui)

        
        self.load_button = HFrame()
        self.load_button.set_children([ok_button,cancel_button])
        self.load_button.topleft = (global_variables.window_size[0] / 2 - self.load_button.size[0] / 2, self.load_window.topleft[1] + self.load_window.list_size[1] + 50)
        self.renderer.add_widget(self.load_button)

    def effectuate_load_callback(self):
        load_file_name = self.load_window.selected
        if load_file_name is not None:
            main.start_loop(load_previous_game = os.path.join("savegames",load_file_name))
            
            #self.solar_system_object_link.load_solar_system(load_file_name)

    def load_callback(self):
        file_window = gui.file_window(None,self.renderer,None)
        file_window.select_game_to_load_callback()
    
    def game_settings_callback(self):
        pass
    
    def quit_callback(self):
        sys.exit(0)

    
    def exit(self, stop_world_spinning = True):
        """
        Function that kills all the windows hanging around
        """
        if stop_world_spinning:
            self.run_background_spin = False
        try:    self.window
        except: pass
        else:   
            self.window.destroy()
            del self.window
            
        try:    self.load_button
        except: pass
        else:
            self.load_button.destroy()
            del self.load_button
        
        try:    self.load_window
        except: pass
        else:
            self.load_window.exit()
            del self.load_window

    
    def create_intro_gui(self):
        """
        The GUI part of starting up the game
        """
        self.exit(stop_world_spinning = False)
        self.window = VFrame(Label("The High Frontier"))
        
        button_names= ["#New game","#Load game","#Game settings","#Quit game"]
        button_functions = [self.ask_company_name,self.select_game_to_load_callback,self.game_settings_callback,self.quit_callback]
        
        list_of_children = []
        max_width = 0
        for i, button_name in enumerate(button_names):
            temp_button = Button(button_name)
            temp_button.connect_signal(SIG_CLICKED,button_functions[i])
            max_width = max(max_width,temp_button.width)
            list_of_children.append(temp_button)
        
        for button in list_of_children:
            button.set_minimum_size(max_width,button.size[1])
        
        self.window.set_children(list_of_children)
        
        self.window.topleft = (global_variables.window_size[0] / 2 - self.window.size[0] /2, global_variables.window_size[1] / 2 - self.window.size[1] /2)
        
        self.renderer.add_widget(self.window)
        
    

    def ask_company_name(self,give_warning = False):
        self.exit()
        
#        starting_year = datetime.date(2010,1,1)
        
        self.window = VFrame(Label("Name of company"))
        entry_box = Entry("")
        entry_box.minsize = (300,24)
        entry_box.activate()
        
        ok_button = Button("ok")
        cancel_button = Button("cancel")
        
        ok_button.connect_signal(SIG_CLICKED, self.ask_company_capital)
        cancel_button.connect_signal(SIG_CLICKED, self.create_intro_gui)
        
        button_frame = HFrame()
        button_frame.set_children([ok_button,cancel_button])
        
        if give_warning:
            warning_label = Label("Name must be " + str(global_variables.max_letters_in_company_names) + " characters or less")
            self.window.set_children([entry_box,button_frame,warning_label])
        else:
            
            self.window.set_children([entry_box,button_frame])
        
        self.window.topleft = (global_variables.window_size[0] / 2 - self.window.size[0] /2, global_variables.window_size[1] / 2 - self.window.size[1] /2)
        
        self.renderer.add_widget(self.window)
        
        
        
        
    
    def ask_company_capital(self,give_warning = False):
        try:    self.window.children[0].text    
        except: 
            try:    self.company_name
            except: raise Exception("Did not find an important component")
            else:   company_name = self.company_name 
        else:   company_name = self.window.children[0].text
        
        self.exit()
        
        all_ok = True
        if not (0 < len(company_name) <= global_variables.max_letters_in_company_names):
            all_ok = False
            
        if company_name.find("  ") != -1: #somewhere it is used that there are two double spaces, so we can't allow that in a companyname
            all_ok = False
        
        if all_ok:
            self.company_name = company_name
            self.window = VFrame(Label("Starting capital of company"))
            entry_box = Entry("10000000")
            entry_box.minsize = (300,24)
            entry_box.activate()
            
            
            ok_button = Button("ok")
            cancel_button = Button("cancel")
            
            ok_button.connect_signal(SIG_CLICKED, self.start_new_game)
            cancel_button.connect_signal(SIG_CLICKED, self.create_intro_gui)
            
            button_frame = HFrame()
            button_frame.set_children([ok_button,cancel_button])
            
            if give_warning:
                warning_label = Label("Starting capital must be an integer above zero")
                self.window.set_children([entry_box,button_frame,warning_label])
            else:
                
                self.window.set_children([entry_box,button_frame])
            
            self.window.topleft = (global_variables.window_size[0] / 2 - self.window.size[0] /2, global_variables.window_size[1] / 2 - self.window.size[1] /2)
            
            self.renderer.add_widget(self.window)

        else:
            self.ask_company_name(give_warning=True)
            

    def start_new_game(self):
        try:    self.window.children[0].text    
        except: 
            try:    self.company_capital
            except: raise Exception("Did not find an important component")
            else:   company_capital = self.company_capital 
        else:   company_capital = self.window.children[0].text
        
        
        self.exit()
        all_ok = True
        try:    int(company_capital)
        except: all_ok = False
        else:   pass
        
        
        if all_ok:
            if 0 >= int(company_capital):
                all_ok = False
        
        if all_ok:
            self.company_capital = int(company_capital)
            #print "starting new game with " + str(self.company_name) + " and " + str(self.company_capital)
            main.start_loop(company_name = str(self.company_name), company_capital = self.company_capital, load_previous_game = os.path.join("pickledmiscellanous","A_small_test_game"))

            
            
        else:
            self.ask_company_capital(give_warning=True)

            
main.start_loop(company_name = "Player1", company_capital = 1000000, load_previous_game = None)
#intro_gui = Intro_gui()