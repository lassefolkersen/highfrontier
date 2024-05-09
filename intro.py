import os
import sys
import logging
from pathlib import Path

from pygame.locals import *
import pygame

import solarsystem
import planet
import global_variables

import gui_components
import main
import primitives


class IntroGui:
    """GUI for the introduction.

    The intro shows a annimation that starts with the solar system,
    then zooms in on the earth.
    Finally the introduction menu is shown, with in the background
    a loop showing the earth from different angles.

    """



    def __init__(self):
        self.main=main.Game()

        # Create a clock object to keep track of time
        self.fps = 30
        self.clock = pygame.time.Clock()
        self.company_capital = None
        self.company_name = None
        self.save_game_to_load = None
        self.run_background_spin = True
        self.gui_rect = pygame.Rect(global_variables.window_size[0] / 2 - 90,global_variables.window_size[1] / 3, 180,180)
        self.text_receiver = None

        # Where to save computed intro files
        self.intro_dir = Path("intro")
        self.intro_dir.mkdir(exist_ok=True)

        # Steps for the intro sequence
        self.steps_system = 74
        self.steps_both = 9
        self.steps_planet = 51
        self.steps_loop = 72

        # Logger object
        self.logger = logging.getLogger(__name__)

        pygame.init()
        if global_variables.fullscreen:
            self.window = pygame.display.set_mode(global_variables.window_size,FULLSCREEN)
        else:
            self.window = pygame.display.set_mode(global_variables.window_size)
        icon = pygame.image.load(os.path.join("images","window_icon.png"))
        pygame.display.set_icon(icon)

        if global_variables.fullscreen:
            pygame.time.delay(1000)

        self.intro_sequence()
        self.create_intro_gui()
        i = 0
        while True:
            self.clock.tick(self.fps)
            if self.run_background_spin:
                self.background_sequence(i)
                i = (i + 1) % self.steps_loop

            events = pygame.event.get()
            for event in events:
                if event.type == QUIT:
                    sys.exit(0)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.receive_click(event)

                if event.type == pygame.KEYDOWN:
                    if self.text_receiver is not None:
                        self.text_receiver.receive_text(event)


    @property
    def sol(self):
        if not hasattr(self, "_sol"):
            self._sol = solarsystem.solarsystem(global_variables.start_date)
        return self._sol

    def receive_click(self, event):
        print(event)
        if self.gui_rect.collidepoint(event.pos) == 1:
            for button in list(self.buttons.values()):
                if button.rect.collidepoint(event.pos) == 1:
                    if isinstance(button, gui_components.fast_list):
                        button.receive_click(event)
                    elif isinstance(button, gui_components.radiobuttons):

                        button.activate(event.pos)
                    else:
                        button.activate(event)

    def set_eccentricity(self,solar_system_instance, new_eccentricity):
        if new_eccentricity >= 1:
            raise Exception("Too high eccentricity")
        for planet_instance in list(solar_system_instance.planets.values()):
            if ["original eccentricity"] not in list(planet_instance.planet_data.keys()):
                eccentricity = planet_instance.planet_data["eccentricity"]
                if planet_instance.name != "sun":
                    planet_instance.planet_data["original eccentricity"] = eccentricity
            planet_instance.planet_data["eccentricity"] = new_eccentricity

    def filepath_of_intro(self, step: int, is_loop: bool):
        """Get the path to the introfile for step i."""
        f_name = f"file_{step:03d}.jpg"
        if is_loop:
            f_name = "loop_" + f_name
        else:
            f_name = "intro_" + f_name
        return self.intro_dir / f_name



    def get_surface_intro(self, step: int, is_loop: bool = True):
        """Get the surface for the intro step i."""
        filepath = self.filepath_of_intro(step, is_loop)

        if filepath.is_file():
            return pygame.image.load(filepath)
        else:
            # Generate the file if it doesn't exist
            self.logger.warning(f" {filepath} not found. It will be recreated. This will take time.")
            if is_loop:
                surface = self.generate_intro_loop_image(step)
            else:
                surface = self.generate_intro_image(step)
            pygame.image.save(surface, filepath)
            return surface


    def generate_intro_image(self, step: int) -> pygame.Surface:


        # Draw the solar system
        if step < self.steps_system + self.steps_both:
            # Parameters for the solar system
            eccentricity = 1 - (((step + 1) / 500) ** 2)
            zoom = (1.2 ** (step + 1)) / 100
            self.logger.debug(f"at {step=} {eccentricity=}  {zoom=}")

            self.set_eccentricity(self.sol,eccentricity)
            surface = self.sol.draw_solar_system(zoom_level=zoom,date_variable=self.sol.current_date,center_object="earth")
        else:
            surface = pygame.Surface(global_variables.window_size)

        if step < self.steps_system:
            # Draw only the solar system
            pass
        elif step < self.steps_system + self.steps_both:
            earth: planet.planet  = self.sol.planets["earth"]

            step_this = step - self.steps_system + 1

            northern_inclination = -40 + step_this / 2
            eastern_inclination = step_this* 5 - 50
            projection_scaling = 3 + step_this * 4
            if eastern_inclination >= 180:
                eastern_inclination = eastern_inclination - 360


            surface.blit(pygame.Surface((projection_scaling*4,projection_scaling*4)),(global_variables.window_size[0] / 2 - projection_scaling*2, global_variables.window_size[1] / 2 - projection_scaling*2))
            self.logger.debug(f" at {step=}  north is {northern_inclination} and east is {eastern_inclination} and scaling is {projection_scaling}")

            planet_surface = earth.draw_image(eastern_inclination,northern_inclination,projection_scaling, fast_rendering=False)
            surface.blit(planet_surface, (global_variables.window_size[0] / 2 - projection_scaling/2, global_variables.window_size[1] / 2 - projection_scaling/2))

        else:
            earth: planet.planet = self.sol.planets["earth"]
            step_this = step - self.steps_system - self.steps_both + 1

            # Will make the earth rotate while zooming in
            northern_inclination = -30 + step_this / 2
            eastern_inclination = step_this * 5
            projection_scaling = 43 + step_this * 6
            if eastern_inclination >= 180:
                eastern_inclination = eastern_inclination - 360

            self.logger.debug(f" at {step=}  north is {northern_inclination} and east is {eastern_inclination} and scaling is {projection_scaling}")

            planet_surface = earth.draw_image(eastern_inclination,northern_inclination,projection_scaling, fast_rendering=False,)

            surface.blit(planet_surface, (global_variables.window_size[0] / 2 - projection_scaling/2, global_variables.window_size[1] / 2 - projection_scaling/2))

        return surface

    def generate_intro_loop_image(self, step: int) -> pygame.Surface:

        northern_inclination_start = -30 + (self.steps_planet+1) / 2
        eastern_inclination_start = (self.steps_planet+1) * 5
        projection_scaling_start = 43 + (self.steps_planet+1) * 6
        self.steps_loop = int(360 / 5) #because we tilt 5 each step


        # Other wise recreate the file
        earth = self.sol.planets["earth"]
        eastern_inclination = eastern_inclination_start + step * 5
        northern_inclination = northern_inclination_start
        projection_scaling = projection_scaling_start
        if eastern_inclination >= 180:
            eastern_inclination = eastern_inclination - 360
        self.logger.debug(f" at {step=}  north is {northern_inclination} and east is {eastern_inclination} and scaling is {projection_scaling}")

        planet_surface = earth.draw_image(
            eastern_inclination,
            northern_inclination,
            projection_scaling
        )

        surface = pygame.Surface(global_variables.window_size)
        surface.blit(
            planet_surface,
            (
                global_variables.window_size[0] / 2 - projection_scaling/2,
                global_variables.window_size[1] / 2 - projection_scaling/2
            )
        )

        return surface

    def intro_sequence(self):

        for step in range(self.steps_system + self.steps_both + self.steps_planet):
            events = pygame.event.get()
            for event in events:
                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
                    return
            surface = self.get_surface_intro(step, is_loop=False)
            self.window.blit(surface, (0,0))
            pygame.display.flip()
            self.clock.tick(self.fps)

    def background_sequence(self,i):
        surface = self.get_surface_intro(i, is_loop=True)
        left_rect = pygame.Rect(0,0,self.gui_rect[0],global_variables.window_size[1])
        right_rect = pygame.Rect(self.gui_rect[0] + self.gui_rect[2],0,global_variables.window_size[0]-self.gui_rect[0]-self.gui_rect[2],global_variables.window_size[1])
        top_rect = pygame.Rect(0,0,global_variables.window_size[0],self.gui_rect[1])
        bottom_rect = pygame.Rect(0,self.gui_rect[1] + self.gui_rect[3],global_variables.window_size[0],global_variables.window_size[1]-self.gui_rect[3] - top_rect[3])
        for rect in [left_rect,right_rect,top_rect,bottom_rect]:
            self.window.set_clip(rect)
            self.window.blit(surface, (0,0))
        self.window.set_clip(None)
        pygame.display.flip()

    def effectuate_load_callback(self):
        load_file_name = self.load_window.selected
        if load_file_name is not None:
            self.main.start_loop(load_previous_game = os.path.join("savegames",load_file_name))

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
        self.main.start_loop(loadPreviousGame = os.path.join("savegames",load_window.selected_name))

    def game_settings_callback(self, label, function_parameter):
        pass

    def quit_callback(self, label, function_parameter):
        sys.exit(0)

    def create_intro_gui(self, label = None, function_parameter = None):
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
        data_file_name = os.path.join("data","base_data","earth.txt")
        if os.access(data_file_name,os.R_OK):
            read_base_database = primitives.import_datasheet(data_file_name)
        else:
            raise Exception("The intro script couldn't access:" + str(data_file_name))
        self.countries = []
        for entry in list(read_base_database.values()):
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
            if(self.company_name is not None):
                cn=str(self.company_name)
            else:
                cn=None
            self.main.start_loop(companyName = cn,
                                 companyCapital = self.company_capital,
                                 loadPreviousGame = None)
        else:
            self.ask_company_capital(None, None, give_warning=True)


introGui = IntroGui()
