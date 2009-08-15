import os
from ocempgui.widgets import *
from ocempgui.widgets.Constants import *
from ocempgui.events import Signals
from ocempgui.widgets.components import ListItemCollection, TextListItem
from ocempgui.object import BaseObject
import global_variables
import sys
import string
import pygame
import datetime
import math
import company
import primitives
import gui_extras

import random
import time



class commandbox(BaseObject):
    """
    The command box is the right hand navigation bar. It is always in place.
    """
    def __init__(self,renderer,manager,solar_system_object):
        """
        Here the commandbox is started initialized. In addition all the other GUI elements is started up, to keep it at one place
        """
        
        BaseObject.__init__(self)
        
        #Starting up all GUI components
        self.all_windows = {}
        
        self.all_windows["infobox_window"] = infobox_window(solar_system_object,renderer,self)
        self.all_windows["infobox_window"].manager = manager

        self.all_windows["message_bar_window"] = message_bar(solar_system_object,renderer,self)
        self.all_windows["message_bar_window"].manager = manager

        self.all_windows["navigation_window"] = navigation_window(solar_system_object,renderer,self)
        self.all_windows["navigation_window"].manager = manager

        self.all_windows["overlay_window"] = overlay_window(solar_system_object,renderer,self)
        self.all_windows["overlay_window"].manager = manager

        self.all_windows["planet_jump_window"] = planet_jump_window(solar_system_object,renderer,self)
        self.all_windows["planet_jump_window"].manager = manager

        self.all_windows["company_window"] = company_window(solar_system_object,renderer,self)
        self.all_windows["company_window"].manager = manager
        
        self.all_windows["base_window"] = base_window(solar_system_object,renderer,self)
        self.all_windows["base_window"].manager = manager
        
        self.all_windows["tech_window"] = tech_window(solar_system_object,renderer,self)
        self.all_windows["tech_window"].manager = manager
        
        self.all_windows["trade_window"] = trade_window(solar_system_object,renderer,self)
        self.all_windows["trade_window"].manager = manager

        self.all_windows["file_window"] = file_window(solar_system_object,renderer,self)
        self.all_windows["file_window"].manager = manager

        #Non command-box windows
        #base-related
        
        #base-related
        self.all_windows["left_side_base_navigation"] = left_side_base_navigation(solar_system_object,renderer,self)
        self.all_windows["left_side_base_navigation"].manager = manager
        
        self.all_windows["base_population_info"] = base_population_info(solar_system_object,renderer,self)
        self.all_windows["base_population_info"].manager = manager

        self.all_windows["base_and_firm_market_window"] = base_and_firm_market_window(solar_system_object,renderer,self)
        self.all_windows["base_and_firm_market_window"].manager = manager
        
        self.all_windows["base_list_of_companies"] = base_list_of_companies(solar_system_object,renderer,self)
        self.all_windows["base_list_of_companies"].manager = manager

        self.all_windows["base_list_of_firms"] = base_list_of_firms(solar_system_object,renderer,self)
        self.all_windows["base_list_of_firms"].manager = manager
        
        self.all_windows["company_list_of_firms"] = company_list_of_firms(solar_system_object,renderer,self)
        self.all_windows["company_list_of_firms"].manager = manager

        self.all_windows["base_build_menu"] = base_build_menu(solar_system_object,renderer,self)
        self.all_windows["base_build_menu"].manager = manager
        
        
        
        #company-related
        self.all_windows["left_side_company_navigation"] = left_side_company_navigation(solar_system_object,renderer,self)
        self.all_windows["left_side_company_navigation"].manager = manager
        
        
        self.all_windows["company_ownership_info"] = company_ownership_info(solar_system_object,renderer,self)
        self.all_windows["company_ownership_info"].manager = manager

        
        self.all_windows["company_financial_info"] = company_financial_info(solar_system_object,renderer,self)
        self.all_windows["company_financial_info"].manager = manager
        
        #firm-related
        self.all_windows["left_side_firm_navigation"] = left_side_firm_navigation(solar_system_object,renderer,self)
        self.all_windows["left_side_firm_navigation"].manager = manager

        
        #see base_and_firm_market_window
#        self.all_windows["firm_bids_info"] = firm_bids_info(solar_system_object,renderer,self)
#        self.all_windows["firm_bids_info"].manager = manager


        self.all_windows["firm_trade_partners_info"] = firm_trade_partners_info(solar_system_object,renderer,self)
        self.all_windows["firm_trade_partners_info"].manager = manager


        self.all_windows["firm_process_info"] = firm_process_info(solar_system_object,renderer,self)
        self.all_windows["firm_process_info"].manager = manager
        
        self.create_commandbox()
        self.renderer = renderer
        
        

        
    def message_bar_toggle_callback(self):
        self.manager.emit("message_bar_toggle",self.button_message_bar.active)

    def navigation_toggle_callback(self):
        self.manager.emit("navigation_toggle",self.button_navigate.active)

    def overlay_toggle_callback(self):
        self.manager.emit("overlay_toggle",self.button_overlay.active)

    def planet_jump_toggle_callback(self):
        self.manager.emit("planet_jump_toggle",self.button_planet_jump.active)

    def company_toggle_callback(self):
        self.manager.emit("company_toggle",self.button_company.active)

    def base_toggle_callback(self):
        self.manager.emit("base_toggle",self.button_base.active)

    def tech_toggle_callback(self):
        self.manager.emit("tech_toggle",self.button_tech.active)


    def trade_toggle_callback(self):
        self.manager.emit("trade_toggle",self.button_trade.active)

    def file_toggle_callback(self):
        self.manager.emit("file_toggle",self.button_file.active)


    
    def create_commandbox(self):    
        """
        Returns the right-side menu command box
        """
        self.table = Table(3,1) 
        self.table.depth = 1
        self.table.minsize = (0,global_variables.window_size[1])

        menu_frame = VFrame()
        menu_frame.align = ALIGN_LEFT
        self.button_message_bar = ToggleButton("#Messages")
        self.button_navigate = ToggleButton("#Navigation")
        self.button_overlay = ToggleButton("#Map overlays")
        self.button_planet_jump = ToggleButton("#Planet shortcuts")
        self.button_company = ToggleButton("#Company menu")
        self.button_base = ToggleButton("#Base overview")
        self.button_tech = ToggleButton("T#echnology")
        self.button_trade = ToggleButton("#Trade menu")
        self.button_file = ToggleButton("#File menu")
        min_width = 20+max(self.button_message_bar.size[0],self.button_navigate.size[0],self.button_company.size[0],self.button_base.size[0],self.button_tech.size[0],self.button_trade.size[0],self.button_file.size[0])
        min_height = self.button_navigate.size[1]
        self.button_message_bar.set_minimum_size(min_width,min_height)
        self.button_navigate.set_minimum_size(min_width,min_height)
        self.button_overlay.set_minimum_size(min_width,min_height)
        self.button_planet_jump.set_minimum_size(min_width,min_height)
        self.button_company.set_minimum_size(min_width,min_height)
        self.button_base.set_minimum_size(min_width,min_height)
        self.button_tech.set_minimum_size(min_width,min_height)
        self.button_trade.set_minimum_size(min_width,min_height)
        self.button_file.set_minimum_size(min_width,min_height)

        self.table.topleft = (global_variables.window_size[0]-min_width,0)
        
        global_variables.action_window_size = (global_variables.window_size[0]-min_width,global_variables.window_size[1])
        
        menu_frame.add_child(self.button_message_bar,self.button_navigate,self.button_overlay,self.button_planet_jump,self.button_company,self.button_base,self.button_tech,self.button_trade,self.button_file)
        self.table.add_child(1,0,menu_frame)
        self.button_message_bar.connect_signal(Constants.SIG_CLICKED,self.message_bar_toggle_callback)
        self.button_navigate.connect_signal(Constants.SIG_CLICKED,self.navigation_toggle_callback)
        self.button_overlay.connect_signal(Constants.SIG_CLICKED,self.overlay_toggle_callback)
        self.button_planet_jump.connect_signal(Constants.SIG_CLICKED,self.planet_jump_toggle_callback)
        self.button_company.connect_signal(Constants.SIG_CLICKED,self.company_toggle_callback)
        self.button_base.connect_signal(Constants.SIG_CLICKED,self.base_toggle_callback)
        self.button_tech.connect_signal(Constants.SIG_CLICKED,self.tech_toggle_callback)
        self.button_trade.connect_signal(Constants.SIG_CLICKED,self.trade_toggle_callback)
        self.button_file.connect_signal(Constants.SIG_CLICKED,self.file_toggle_callback)
        






class infobox_window(BaseObject):
    """
    The infobox window. Always visible and shows time and location - ie "solarsystem, centered on earth",
    "Frankfurt" etc. It also shows internet-browser style backward and forward buttons.
    """
    def __init__(self,solar_system_object,renderer,commandbox):
        BaseObject.__init__(self)
        self._signals["update_infobox"] = []
        self._signals["going_to_planetary_mode_event"] = []
        self._signals["going_to_solar_system_mode_event"] = []
        self._signals["going_to_base_mode_event"] = []
        self._signals["going_to_company_window_event"] = []
        self._signals["going_to_firm_window_event"] = []
        self._signals["going_to_techtree_mode_event"] = []
        self.renderer = renderer
        self.solar_system_object_link = solar_system_object
        self.size = (400,40)
        self.topleft = (global_variables.window_size[0]/2 - self.size[0]/2,0)
        self.data = self.update_data()
        self.history = []
        self.has_been_history = []
        self.history_button_size = (30,30)
        self.current_event = Signals.Event("going_to_planetary_mode_event",self.solar_system_object_link.current_planet)
        self.protect_has_been_history = False  #Without this variable has_been_history would be deleted even when going steps forward
        self.create_infobox(self.renderer)
        
    
    def forwardbutton_callback(self):
        if len(self.has_been_history) > 0: 
            signal_to_emit = self.has_been_history.pop()
            
            self.protect_has_been_history = True
            if signal_to_emit.signal == "going_to_solar_system_mode_event":
                self.solar_system_object_link.current_planet.projection_scaling = 45
                self.solar_system_object_link.display_mode = "planetary"
                self.manager.emit("zoom_out",None)
            elif signal_to_emit.signal == "going_to_planetary_mode_event":
                self.manager.emit("center_on",signal_to_emit.data.name)
            else:
                self.manager.emit(signal_to_emit.signal,signal_to_emit.data)
            self.protect_has_been_history = False
        
        else:
            raise Exception("The forward button was pressed but it should not have been set to sensitive")

        if len(self.has_been_history) < 1:
            self.forwardbutton.sensitive = False

        
    def backbutton_callback(self):
        
        if len(self.history) > 0:
            self.has_been_history.append(self.current_event)
#            print "NEEDTOKNOW: Appended a signal to self.has_been_history " + str(self.current_event.signal) + " with data " + str(self.current_event.data)

            signal_to_emit = self.history.pop()
#            print "backward. Emitting " + str(signal_to_emit.signal) + " with data " + str(signal_to_emit.data)
#            print "The backward history is: " 
#            for i, entry in enumerate(self.history):
#                print str(i) + ": signal: " + str(entry.signal) + " - data: " + str(entry.data)
            self.protect_has_been_history = True
            if signal_to_emit.signal == "going_to_solar_system_mode_event":
                #print "going to solar system mode"
                self.solar_system_object_link.current_planet.projection_scaling = 45
                self.solar_system_object_link.display_mode = "planetary"
                self.manager.emit("zoom_out",None)
            elif signal_to_emit.signal == "going_to_planetary_mode_event":
                self.manager.emit("center_on",signal_to_emit.data.name)
            else:
                self.manager.emit(signal_to_emit.signal,signal_to_emit.data)
            self.protect_has_been_history = False
            
            try: self.forwardbutton.sensitive
            except: pass
            else:
                self.forwardbutton.sensitive = True
            
            self.history.pop()
        else:
            raise Exception("The back button was pressed but it should not have been set to sensitive")

        if len(self.history) < 1:
            try: self.backbutton.sensitive
            except: pass
            else:
                self.backbutton.sensitive = False
        
        
    def create_infobox(self,renderer):
        """
        The creation function. Doesn't return anything, but saves self.window variable and renders using the self.renderer. 
        """
        info_label = Label(self.data)
        info_label.multiline = True
        self.window = VFrame()
        self.window.set_opacity(100)
        self.window.border = BORDER_NONE
        self.window.add_child(info_label)
        self.window.topleft = self.topleft
        self.window.minsize = self.size
        self.window.depth = 1
        renderer.add_widget(self.window)
        
        
        #Drawing a button with an arrow
        blank_surface = pygame.Surface(self.history_button_size)
        blank_surface.fill((234,228,223))
        pygame.draw.line(blank_surface,(155,155,155),(5,13),(30,13))
        pygame.draw.line(blank_surface,(155,155,155),(5,16),(30,16))
        pygame.draw.line(blank_surface,(155,155,155),(0,15),(5,10))
        pygame.draw.line(blank_surface,(155,155,155),(0,15),(5,20))
        pygame.draw.line(blank_surface,(155,155,155),(5,10),(5,13))
        pygame.draw.line(blank_surface,(155,155,155),(5,20),(5,16))
        pygame.draw.line(blank_surface,(155,155,155),(30,13),(30,16))

        flipped_blank_surface = pygame.transform.flip(blank_surface,True,False)
        
        self.backbutton = ImageButton(blank_surface)
        self.forwardbutton = ImageButton(flipped_blank_surface)
        self.backbutton.set_opacity(100)
        self.forwardbutton.set_opacity(100)
        self.forwardbutton.topleft = (self.topleft[0] + self.size[0] + 5, self.topleft[1])
        self.backbutton.topleft = (self.topleft[0] - self.history_button_size[0] - 15 , self.topleft[1])
        if len(self.history) < 1:
            self.backbutton.sensitive = False
        if len(self.has_been_history) < 1:
            self.forwardbutton.sensitive = False

        
        self.backbutton.connect_signal(Constants.SIG_CLICKED,self.backbutton_callback)
        self.forwardbutton.connect_signal(Constants.SIG_CLICKED,self.forwardbutton_callback)

        self.backbutton.depth = 1
        self.forwardbutton.depth = 1

        
        self.renderer.add_widget(self.backbutton,self.forwardbutton)
        
        
    def exit(self):
        try: self.window
        except: pass
        else:
            self.window.destroy()
            del self.window
        try: self.backbutton
        except: pass
        else:
            self.backbutton.destroy()
            del self.backbutton
        try: self.forwardbutton
        except: pass
        else:
            self.forwardbutton.destroy()
            del self.forwardbutton


    def notify(self,event):
        if event.signal in ["going_to_planetary_mode_event","going_to_solar_system_mode_event","going_to_base_mode_event","going_to_company_window_event","going_to_firm_window_event","going_to_techtree_mode_event"]:
            self.history.append(self.current_event) 
            self.current_event = event
            if not self.protect_has_been_history:
                self.has_been_history = []
                try: self.forwardbutton
                except: pass
                else:
                    self.forwardbutton.sensitive = False
            while len(self.history) > global_variables.max_stepback_history_size:
                del self.history[0]
            try: self.backbutton
            except: pass
            else:
                self.backbutton.sensitive = True
        if event.signal == "update_infobox":
            try: self.window
            except:
                pass
            else:
                self.window.lock()
                self.data = self.update_data()
                info_label = Label(self.data)
                info_label.multiline = True
                self.window.set_children([info_label])
                self.window.update()
                self.window.unlock()
#        if event.signal == "infobox_toggle":
#            if not event.data:
#                try: self.window
#                except:
#                    self.create_infobox(self.renderer)
#                    #self.window.set_focus(True)
#                else:
#                    print "DEBUGGING: infobox was switched on, but already exists"
#            else:
#                self.exit()


    
    def update_data(self):
        date_string = str(self.solar_system_object_link.current_date)
        if self.solar_system_object_link.display_mode == "solar_system":
            env_string = "Solar system -" + string.capitalize(self.solar_system_object_link.current_planet.planet_name)
        elif self.solar_system_object_link.display_mode == "planetary":
            if self.solar_system_object_link.current_planet.current_base == None:
                env_string = self.solar_system_object_link.current_planet.planet_name
            else:
                env_string = self.solar_system_object_link.current_planet.planet_name + " - " + self.solar_system_object_link.current_planet.current_base.name 
        elif self.solar_system_object_link.display_mode == "planetary":
            env_string = self.solar_system_object_link.current_planet.current_base.name
        elif self.solar_system_object_link.display_mode == "company":
            env_string = self.solar_system_object_link.company_selected.name
        elif self.solar_system_object_link.display_mode == "firm":
            env_string = self.solar_system_object_link.firm_selected.name
        elif self.solar_system_object_link.display_mode == "base":
            env_string = self.solar_system_object_link.current_planet.current_base.name
        elif self.solar_system_object_link.display_mode == "techtree":
            env_string = "technology tree"
        else:
            env_string = ""
            if self.solar_system_object_link.message_printing["debugging"]:
                print_dict = {"text":"DEBUGGING: unknown display mode passed to infobox","type":"debugging"}
                self.solar_system_object_link.messages.append(print_dict)


            
            
        info_string = date_string + "\n" + env_string
        
        return info_string
    

        
        

        






class message_bar(Window):
    """
    Class that receives messages for the player and prints them.
    It will show the message depending on the type. Types are:
    general gameplay info
    company_generation
    and more
    
    
    """
    def __init__(self,solar_system_object,renderer,commandbox):
        Window.__init__(self)
        self._signals["message_bar_toggle"] = []
        self._signals["update_infobox"] = []
#        self._signals["print_message"] = []
        self.renderer = renderer
        self.solar_system_object_link = solar_system_object
        self.list_size = (global_variables.window_size[0]-170,110)
        self.topleft = (20,global_variables.window_size[1]-110)
        self.messages = []
        self.max_print_length = 8 #how many lines of text to print in standard viewing of the window
        self.max_save_length = 500 #how many lines of text to save in memory
        self.max_string_length = 140#how many letters is maximally allowed to be printed in the message window
        
        
    def create_message_bar_window(self,renderer):
        """
        The creation function. Doesn't return anything, but saves self.window variable and renders using the self.renderer. 
        """

        print_frame = VFrame()
        print_frame.set_minimum_size(self.list_size[0],self.list_size[1])
        print_frame.set_align(ALIGN_LEFT)

        self.window = Window()
        self.window.set_child(print_frame)
        self.window.topleft = self.topleft
        renderer.add_widget(self.window)
        self.update_text_field()

    def update_text_field(self):
        """
        Function that will update the text field
        """
        
        
        #first trim the message list down to the number indicated to be max
        if len(self.messages) > self.max_save_length:
            surplus = len(self.messages) - self.max_save_length
            del self.messages[0:surplus]

        
        print_frame = self.window.child
        print_frame.lock()
        messages = []
        
        range_here = range(0,len(self.solar_system_object_link.messages))
        range_here.reverse()
#        print range_here
        for i in range_here:
            message = self.solar_system_object_link.messages[i]
            if self.solar_system_object_link.message_printing[message["type"]]:
                messages.append(message)
            if len(messages) >= self.max_print_length:
                break
        messages.reverse()
        
        message_string = ""
        for message in messages:
            if self.solar_system_object_link.message_printing[message["type"]]:
                if len(message["text"]) > self.max_string_length:
                    message_text = message["text"][0:self.max_string_length]
#                    print "Shortened a length " + str(len(message["text"])) + " text"
                else:
                    message_text = message["text"]
                message_string = message_string + message_text + "\n" 
        message_string = message_string.rstrip("\n")    
        
        message_label = Label(message_string)
        message_label.set_align(ALIGN_LEFT)
        message_label.multiline = True
        
        print_frame.set_children([message_label])
#        self.print_frame.set_align(ALIGN_LEFT)
        print_frame.update()
        print_frame.unlock()

        
        

    def notify(self,event):
        if event.signal == "message_bar_toggle":
            if event.data:
                try: self.window
                except:
                    pass
                else:
                    self.window.destroy()
                    del self.window
#                    del self.print_frame
            else:
                self.create_message_bar_window(self.renderer)
                self.window.set_focus()
        if event.signal == "update_infobox":
            try:    self.window
            except: pass
            else:
                self.update_text_field()
            
        





class navigation_window(Window):
    """
    The navigation window. Is controlled by a togglebutton in the commandbox. When visible it can be used for zooming and rotating.
    """
    def __init__(self,solar_system_object,renderer,commandbox):
        Window.__init__(self)
        self._signals["going_to_planetary_mode_event"] = []
        self._signals["going_to_solar_system_mode_event"] = []
        self._signals["navigation_toggle"] = []
        self.renderer = renderer

    def zoom_in_callback(self):
        self.manager.emit("zoom_in",None)
    
    def zoom_out_callback(self):
        self.manager.emit("zoom_out",None)

    def rotate_west_callback(self):
        self.manager.emit("rotate_west",None)

    def rotate_east_callback(self):
        self.manager.emit("rotate_east",None)

    def rotate_south_callback(self):
        self.manager.emit("rotate_south",None)

    def rotate_north_callback(self):
        self.manager.emit("rotate_north",None)
    
    def create_navigation_window(self,renderer):
        """
        The creation function. Doesn't return anything, but saves self.window variable and renderes using the self.renderer. 
        """
        table2 = Table(1,2)
        frame1 = VFrame(Label("Zooming"))
        self.button_zoom_in = Button("Zoom #in")
        self.button_zoom_out = Button("Zoom #out")
        min_width = max(self.button_zoom_in.size[0],self.button_zoom_out.size[0])
        self.button_zoom_in.set_minimum_size(min_width,self.button_zoom_in.size[1])
        self.button_zoom_out.set_minimum_size(min_width,self.button_zoom_out.size[1])
        self.button_zoom_in.connect_signal(Constants.SIG_CLICKED,self.zoom_in_callback)
        self.button_zoom_out.connect_signal(Constants.SIG_CLICKED,self.zoom_out_callback)

        
        frame1.add_child(self.button_zoom_in)
        frame1.add_child(self.button_zoom_out)
        
        frame2 = VFrame(Label("Navigating"))
        navigation_table = Table(3,3)
        self.button_west = Button("#West")
        self.button_east = Button("#East")
        self.button_north = Button("#North")
        self.button_south = Button("#South")
        navigation_table.add_child(1,0,self.button_west)
        navigation_table.add_child(1,2,self.button_east)
        navigation_table.add_child(0,1,self.button_north)
        navigation_table.add_child(2,1,self.button_south)
        self.button_west.connect_signal(Constants.SIG_CLICKED,self.rotate_west_callback)
        self.button_east.connect_signal(Constants.SIG_CLICKED,self.rotate_east_callback)
        self.button_north.connect_signal(Constants.SIG_CLICKED,self.rotate_north_callback)
        self.button_south.connect_signal(Constants.SIG_CLICKED,self.rotate_south_callback)
        frame2.add_child(navigation_table)
        table2.add_child(0,0,frame1)
        table2.add_child(0,1,frame2)
        
        
        self.window = Window()
        self.window.topleft = (50,150)
        self.window.set_child(table2)
        
        if self.solar_system_object_link.display_mode != "planetary":
            self.button_west.sensitive = False
            self.button_east.sensitive = False
            self.button_north.sensitive = False
            self.button_south.sensitive = False
        renderer.add_widget(self.window)
        
    def notify(self,event):
        if event.signal == "going_to_planetary_mode_event":
            try: self.window
            except:
                pass
            else:
                self.button_west.sensitive = True
                self.button_east.sensitive = True
                self.button_north.sensitive = True
                self.button_south.sensitive = True
                #self.button_overlay.sensitive = True
                #print "state is " + str(self.button_overlay.state)
                #print STATE_TYPES[0]
                #if self.button_overlay.state == 2:
                    #self.button_overlay.activate()
                
                #print "state is " + str(self.button_overlay.state)

        if event.signal == "going_to_solar_system_mode_event":
            try: self.window
            except:
                pass
            else:
                self.button_west.sensitive = False
                self.button_east.sensitive = False
                self.button_north.sensitive = False
                self.button_south.sensitive = False
                #self.button_overlay.set_active(False)
                #self.button_overlay.sensitive = False
        if event.signal == "navigation_toggle":
            if not event.data:
                self.create_navigation_window(self.renderer)
                self.window.set_focus()
            else:
                #self.window.depth = -1
                self.window.destroy()
                del self.window



class overlay_window(Window):
    """
    The overlay control window. Can be toggled from commandbox. When visible it can be used to control which visual overlays
    that can be seen in planet mode (topographical maps, resource maps etc)
    """
    def __init__(self,solar_system_object,renderer,commandbox):
        Window.__init__(self)
        self._signals["overlay_toggle"] = []
        self._signals["going_to_solar_system_mode_event"] = []
        self.renderer = renderer
        self.solar_system_object_link = solar_system_object
        #self.create_overlay_window(renderer)
        
    def overlay_set_callback(self,button_name):
        self.manager.emit("display_overlay",button_name)
        #print "emitted display overlay with " + str(button_name)


    def notify(self,event):
        if event.signal == "overlay_toggle":
            #print "heard planet_jump_toggle for " + str(self.window) + " - the signal was: " + str(event.data)
            if event.data:
                try: self.window
                except:
                    pass
                else:
                    self.window.destroy()
                    del self.window
            else:
                self.create_overlay_window(self.renderer)
                self.window.set_focus()

        if event.signal == "going_to_solar_system_mode_event":
            try: self.window
            except:
                pass
            else:
                self.overlay_buttons["visible light"].set_active(True)
        
    def create_overlay_window(self,renderer):
        """
        The creation function. Doesn't return anything, but saves self.window variable and renderes using the self.renderer. 
        """

        overlay_frame = VFrame()
        overlay_frame.set_align(ALIGN_LEFT)
        self.overlay_buttons = {}
        buttons = ["visible light","trade network","topographical"] + self.solar_system_object_link.mineral_resources
        overlay_group = None
        button_size = []
        for i in range(0,len(buttons)):
            self.overlay_buttons[buttons[i]] = RadioButton(string.capitalize(buttons[i]),overlay_group)
            self.overlay_buttons[buttons[i]].connect_signal(Constants.SIG_TOGGLED,self.overlay_set_callback,buttons[i])
            overlay_frame.add_child(self.overlay_buttons[buttons[i]])
            if i == 0:
                overlay_group = self.overlay_buttons[buttons[i]]
                self.overlay_buttons[buttons[i]].overlay_group = self.overlay_buttons[buttons[i]]
        self.window = Window()
        self.window.set_child(overlay_frame)
        #self.window.depth = -1
        self.window.topleft = (global_variables.window_size[0]-300,150)
        #if self.solar_system_object_link.display_mode != "planetary":
            #self.window.sensitive = False
        renderer.add_widget(self.window)



class planet_jump_window(Window):
    """
    The planet jump window. Can be toggled from commandbox. When visible it can be used as shortcut to planet view
    for the different planets
    """
    def __init__(self,solar_system_object,renderer,commandbox):
        Window.__init__(self)
        self._signals["planet_jump_toggle"] = []
        self.renderer = renderer
        #self.create_planet_jump_window(renderer)
        
    def planet_jump_callback(self,button_name):
        self.manager.emit("center_on",button_name)
        #print "emitted center_on with " + str(button_name)

    
    def notify(self,event):
        if event.signal == "planet_jump_toggle":
            #print "heard planet_jump_toggle for " + str(self.window) + " - the signal was: " + str(event.data)
            if event.data:
                try: self.window
                except:
                    pass
                else:
                    self.window.destroy()
                    del self.window
            else:
                self.create_planet_jump_window(self.renderer)
                self.window.set_focus()
        

    def create_planet_jump_window(self,renderer):
        """
        The creation function. Doesn't return anything, but saves self.window variable and renderes using the self.renderer. 
        """

        planet_jump_frame = VFrame()
        self.planet_jump_buttons = {}
        buttons = ["mercury","venus","earth","mars","jupiter","saturn","uranus","neptune"]
        button_sizes = []
        button_size = []
        for i in range(0,len(buttons)):
            self.planet_jump_buttons[buttons[i]] = Button(string.capitalize(buttons[i]))
            self.planet_jump_buttons[buttons[i]].connect_signal(Constants.SIG_CLICKED,self.planet_jump_callback,buttons[i])
            button_sizes.append(self.planet_jump_buttons[buttons[i]].width)
            
        for i in range(0,len(buttons)):
            self.planet_jump_buttons[buttons[i]].set_minimum_size(max(button_sizes),self.planet_jump_buttons[buttons[i]].height)
            planet_jump_frame.add_child(self.planet_jump_buttons[buttons[i]])
            
        self.window = Window()
        #self.window.depth = -1
        self.window.topleft = (global_variables.window_size[0]-300,global_variables.window_size[1]-300)
        self.window.set_child(planet_jump_frame)
        renderer.add_widget(self.window)
        








class tech_window(BaseObject):
    """
    Class for the tech tree. Most of the actual algorithms are in techtree.py - this is just a shell for holding
    the notify system in the same structure as other GUI elements
    """
    def __init__(self,solar_system_object,renderer,commandbox):
        BaseObject.__init__(self)
        self._signals["tech_toggle"] = []
        self._signals["going_to_techtree_mode_event"] = []
        self.renderer = renderer
        self.solar_system_object_link = solar_system_object
        self.commandbox_link = commandbox
        

    def notify(self,event):
        if event.signal == "tech_toggle":
            if not event.data:
                self.manager.emit("going_to_techtree_mode_event",None)
            else:
                self.exit()
                
                
    
    def exit(self):
        if len(self.commandbox_link.all_windows["infobox_window"].history) >= 1:
            self.commandbox_link.all_windows["infobox_window"].backbutton_callback()
        else:
            #this is ugly, but it is a good protection against hypothetical situations were the history is empty
            if self.solar_system_object_link.message_printing["debugging"]:
                print_dict = {"text":"DEBUGGING: The history was empty when asking to exit the technology tree","type":"debugging"}
                self.solar_system_object_link.messages.append(print_dict)

            self.solar_system_object_link.current_planet.projection_scaling = 45
            self.solar_system_object_link.display_mode = "planetary"
            self.manager.emit("zoom_out",None)





class base_window(Window):
    def __init__(self,solar_system_object,renderer,commandbox):
        Window.__init__(self)
        self._signals["base_toggle"] = []
        self.renderer = renderer
        self.solar_system_object_link = solar_system_object
        self.list_size = (700,500)
        self.topleft = (50,50)
        self.commandbox_link = commandbox


    def jump_to_base_callback(self,data):
        base_selected = None
        for planet_instance in self.solar_system_object_link.planets.values():
            for base_instance in planet_instance.bases.values():
                if base_instance.name == self.window.selected_name:
                    base_selected = base_instance
                    
        if base_selected is None:
            raise Exception("The base sought after (" + str(self.window.selected_name) + ") was not found in the base list of the solar_system_object_link")

        self.solar_system_object_link.current_planet.current_base = base_selected
        self.exit()
        self.commandbox_link.button_base.active = False
        self.manager.emit("going_to_base_mode_event",base_selected)


    def create_base_window(self):
        """
        The creation function. Doesn't return anything, but saves self.window variable and renders using the self.renderer. 
        """
        base_data = {}
        for planet_instance in self.solar_system_object_link.planets.values():
            for base_instance in planet_instance.bases.values():
                
                if base_instance.for_sale:
                    for_sale = "For sale"
                else:
                    for_sale = ""
                
                data_here = {"Location":planet_instance.name,"Population":base_instance.population,"For sale":for_sale}

                base_data[base_instance.name] = data_here
                
        column_order = ["rownames","Location","Population","For sale"]
        
        self.window = gui_extras.fast_list(self.renderer)
        self.window.receive_data(base_data,column_order = column_order)
        self.window.topleft = self.topleft
        self.window.list_size = self.list_size
        self.window.create_fast_list()
        self.window.render_title()
        
        self.link_button = Button("Jump to base")
        self.link_button.topleft = (self.topleft[0] + self.list_size[0]/2 - self.link_button.size[0]/2,  self.topleft[1] + self.list_size[1]+50)
        self.link_button.connect_signal(Constants.SIG_CLICKED,self.jump_to_base_callback,None)
        self.renderer.add_widget(self.link_button)



    def notify(self,event):
        if event.signal == "base_toggle":
            if not event.data:
                self.create_base_window()
            else:
                self.exit()
    
    def exit(self):
        try: self.window
        except: pass
        else:
            self.window.exit()
            del self.window
        try: self.link_button
        except: pass
        else:
            self.link_button.destroy()
            del self.link_button



class trade_window(Window):
    """
    This windows shows an overview of all assets (bases and firms) and tech that is for sale, ie. all non-location specific offers.
    """
    def __init__(self,solar_system_object,renderer,commandbox):
        Window.__init__(self)
        self._signals["trade_toggle"] = []
        self.renderer = renderer
        self.commandbox_link = commandbox
        self.solar_system_object_link = solar_system_object
        self.list_size = (700,500)
        self.topleft = (50,50)

    def create_trade_window(self):
        """
        The creation function. Doesn't return anything, but saves self.window variable and renders using the self.renderer. 
        """
        asset_and_tech_data = {}
        for planet_instance in self.solar_system_object_link.planets.values():
            for base_instance in planet_instance.bases.values():
                if base_instance.for_sale:
                    
                    data_here = {"Type":"base","Best price":"for auction (pop: " + str(base_instance.population) + ")","For sale by":base_instance.owner.name,"for_sale_by_link":[base_instance.owner],"object":base_instance}

                    asset_and_tech_data[base_instance.name] = data_here
                
        for company_instance in self.solar_system_object_link.companies.values():
            pass #FIXME add firms for sale here, whenever that is implemented
        for technology in self.solar_system_object_link.technology_tree.vertex_dict.values():
            if len(technology["for_sale_by"]) > 0:
                prices = technology["for_sale_by"].values()
                prices.sort()
                best_price = prices[-1]
                
                if len(technology["for_sale_by"]) == 1:
                    for_sale_by = str(technology["for_sale_by"].keys()[0].name)
                else:
                    for_sale_by = str(len(technology["for_sale_by"])) + " companies"
                for_sale_by_link = technology["for_sale_by"].keys()
                
                data_here = {"Type":"technology","Best price":best_price,"For sale by":for_sale_by,"for_sale_by_link":for_sale_by_link,"object":technology}
                asset_and_tech_data[technology["technology_name"]] = data_here
        
        column_order = ["rownames","Type","Best price","For sale by"]
        
        self.window = gui_extras.fast_list(self.renderer)
        self.window.receive_data(asset_and_tech_data,column_order = column_order)
        self.window.topleft = self.topleft
        self.window.list_size = self.list_size
        self.window.create_fast_list()
        self.window.render_title()

        self.link_button = Button("Bid")
        self.link_button.topleft = (self.topleft[0] + self.list_size[0]/2 - self.link_button.size[0]/2,  self.topleft[1] + self.list_size[1]+50)
        self.link_button.connect_signal(Constants.SIG_CLICKED,self.chose_seller)
        self.renderer.add_widget(self.link_button)
#        self.renderer.add_widget(self.link_button)


    def chose_seller(self):
        """
        Function that allows players to choose between more than one seller
        """
        if self.window.selected_name is not None:
            bid_on = self.window.selected_name
            for_sale_by = self.window.original_tabular_data[bid_on]["for_sale_by_link"]
            sale_object = self.window.original_tabular_data[bid_on]["object"]
            type = self.window.original_tabular_data[bid_on]["Type"]
            price = self.window.original_tabular_data[bid_on]["Best price"]
            
            if type == "technology":
                current_player = self.solar_system_object_link.current_player.known_technologies
                check_result = self.solar_system_object_link.technology_tree.check_technology_bid(current_player,sale_object)
                
                if check_result != "ok":
                    print_dict = {"text":"Can not bid for " + sale_object["technology_name"] + " because it is " + check_result,"type":"general gameplay info"}
                    self.solar_system_object_link.messages.append(print_dict)
                    return None
            
            self.exit()
            if len(for_sale_by) > 1:
                if type != "technology":
                    raise Exception("A bid was made for a type: " + str(type) + " asset, with more than one seller. This should not be possible") 
                sellers_data = {}
                for seller in sale_object["for_sale_by"]:
                    price = sale_object["for_sale_by"][seller]
                    sellers_data[seller.name] = {"Price":price,"seller_link":seller}
                
                column_order = ["rownames","Price"]
                
                self.window = gui_extras.fast_list(self.renderer)
                self.window.receive_data(sellers_data,column_order = column_order)
                self.window.topleft = self.topleft
                self.window.list_size = (self.list_size[0], self.list_size[1] / 2)
                self.window.create_fast_list()
                self.window.render_title()
        
                self.link_button = Button("Bid")
                self.link_button.topleft = (self.topleft[0] + self.list_size[0]/2 - self.link_button.size[0]/2,  self.topleft[1] + self.list_size[1]+50)
                self.link_button.connect_signal(Constants.SIG_CLICKED,self.perform_bid, sale_object, None, type, None)
                self.renderer.add_widget(self.link_button)
#                self.perform_bid(sale_object, None, type, None)
                
            else:
                
                self.perform_bid(sale_object, for_sale_by[0],type, price)

                
                        
    def perform_bid(self, sale_object, seller, type, price):
        """
        Function that allows the player to bid on an asset or technology
        """
        if seller is None: #then it is because we don't know what was chosen in chose_seller and we'll extract that
            bid_on = self.window.selected_name
            seller = self.window.original_tabular_data[bid_on]["seller_link"]
        if price is None: #then it is because we don't know what was chosen in chose_seller and we'll extract that
            bid_on = self.window.selected_name
            price = self.window.original_tabular_data[bid_on]["Price"]    
        
        self.exit(reset_commandbox_button = True)
        

        current_player = self.solar_system_object_link.current_player
        if current_player.capital > price:
            if type == "technology":
                
                
                    self.solar_system_object_link.current_player.known_technologies[sale_object["technology_name"]] = sale_object
                    current_player.capital = current_player.capital - price
                    seller.capital = seller.capital + price
                    print_dict = {"text":str(sale_object["technology_name"]) + " was bought for " + str(price) + " from " + str(seller.name),"type":"general gameplay info"}
                    self.solar_system_object_link.messages.append(print_dict)
                     
                    
            elif type == "base":
                    print_dict = {"text":"base buying not implemented yet","type":"general gameplay info"}
                    self.solar_system_object_link.messages.append(print_dict)
    
            else:
                raise Exception("Unknown type: " + str(type) + " asked for in the asset sales GUI")
    
                
        else:
            print_dict = {"text":current_player.name + " has a capital of " + str(current_player.capital) + " and can't bid " + str(price),"type":"general gameplay info"}
            self.solar_system_object_link.messages.append(print_dict)
            
                
    
    

    def notify(self,event):
        if event.signal == "trade_toggle":
            if not event.data:
                self.create_trade_window()
            else:
                self.exit()
    
    def exit(self, reset_commandbox_button = False):
        try: self.window
        except: pass
        else:
            self.window.exit()
            del self.window

        try: self.link_button
        except: pass
        else:
            self.link_button.destroy()
            del self.link_button
            
        if reset_commandbox_button:
            try:    self.commandbox_link.button_trade
            except: pass
            else:
                if self.commandbox_link.button_trade.active:
                    self.commandbox_link.button_trade.active = False








class company_window(BaseObject):
    """
    The company overview window. Can be toggled from commandbox. Shows all companies in the solarsystem, along with some info
    about them. Can be used as shortcut to the company of interest.
    """
    def __init__(self,solar_system_object,renderer,commandbox):
        BaseObject.__init__(self)
        self._signals["company_toggle"] = []
        self.renderer = renderer
        self.solar_system_object_link = solar_system_object
        self.list_size = (700,500)
        self.topleft = (50,50)
        self.commandbox_link = commandbox
 
        
        
    def jump_to_company_callback(self,data):
        company_selected = None
        for company in self.solar_system_object_link.companies.values():
            if company.name == self.window.selected_name:
                company_selected = company
        if company_selected is None:
            for company in self.solar_system_object_link.companies.values():
                print company.name
            raise Exception("The company sought after (" + str(self.window.selected_name) + ") was not found in the companies list of the solar_system_object_link")
        #print "DEBUGGING: emitted going to company_window_event with " + str(company_selected) + " of name " + str(company_selected.name)
        self.solar_system_object_link.company_selected = company_selected
        self.exit()
        self.commandbox_link.button_company.active = False
        self.manager.emit("going_to_company_window_event",company_selected)
        

    def create_company_window(self):
        """
        The creation function. Doesn't return anything, but saves self.window variable and renders using the self.renderer. 
        """
        company_data = {}
        for company_name in self.solar_system_object_link.companies:
            company_instance = self.solar_system_object_link.companies[company_name]
            capital = company_instance.capital
            no_of_firms = len(company_instance.owned_firms)
            no_of_cities = len(company_instance.home_cities)
            data_here = {"capital":capital,"owned firms":no_of_firms,"home cities":no_of_cities}
            if len(company_name)> global_variables.max_letters_in_company_names:
                if self.solar_system_object_link.message_printing["debugging"]:
                    print_dict = {"text":"DEBUGGING: Shortened " + str(company_name) + " to " + str(company_name[0:30]),"type":"debugging"}
                    self.solar_system_object_link.messages.append(print_dict)
                company_name = company_name[0:global_variables.max_letters_in_company_names]
            company_data[company_name] = data_here
        
        column_order = ["rownames","capital","owned firms","home cities"]
        
        self.window = gui_extras.fast_list(self.renderer)
        self.window.receive_data(company_data,column_order = column_order)
        self.window.topleft = self.topleft
        self.window.list_size = self.list_size
        self.window.create_fast_list()
        self.window.render_title()
        
        self.link_button = Button("Jump to company")
        self.link_button.topleft = (self.topleft[0] + self.list_size[0]/2 - self.link_button.size[0]/2,  self.topleft[1] + self.list_size[1]+50)
        self.link_button.connect_signal(Constants.SIG_CLICKED,self.jump_to_company_callback,None)
        self.renderer.add_widget(self.link_button)

                

    def notify(self,event):
        if event.signal == "company_toggle":
            if not event.data:
                self.create_company_window()
            else:
                self.exit()
    
    def exit(self):
        try: self.window
        except: pass
        else:
            self.window.exit()
            del self.window

        try: self.link_button
        except: pass
        else:
            self.link_button.destroy()
            del self.link_button











class file_window(BaseObject):
    """
    The file window. Can be toggled from commandbox. Quitting, saving, loading, settings and all the usual stuff you'd
    expect to find such a place.
    """
    def __init__(self,solar_system_object,renderer,commandbox):
        BaseObject.__init__(self)
        self._signals["file_toggle"] = []
        self.renderer = renderer
        self.commandbox_link = commandbox
        self.solar_system_object_link = solar_system_object
        self.topleft = (150,350)

        
        
    def create_file_window(self,renderer):
        """
        The creation function. Doesn't return anything, but saves self.window variable and renderes using the self.renderer. 
        """
        self.exit()
        
        self.window = VFrame(Label("Settings"))
        self.window.topleft = self.topleft
        
        button_names= ["#Save game","#Load game","#New game","Catastrophes","#Game settings","#Automation settings","#Message settings","#Quit game"]
        button_functions = [self.select_save_name_callback,self.select_game_to_load_callback,self.new_game_callback,self.catastrophe_window,self.game_settings_callback,self.automation_settings_callback,self.message_settings,self.quit_callback]
        
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

        self.renderer.add_widget(self.window)



    def notify(self,event):
        if event.signal == "file_toggle":
            if not event.data:
                self.create_file_window(self.renderer)
                self.window.set_focus(True)
            else:
                self.exit()
                

    def exit(self, reset_commandbox_button = False):
        """
        Function that clears up the window. If reset_commandbox_button is True, it will also set the status of the commandbox button to
        unpressed.
        """
        try:    self.window._manager
        except: pass
        else:
            self.window.destroy()
        try:    self.window
        except: pass
        else:   del self.window
        
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
            
        try:    self.save_box
        except: pass
        else:
            self.save_box.destroy()
            del self.save_box
        
        if reset_commandbox_button:
#            print "Commandbox button is " + str(self.commandbox_link.button_file.active)
            try:    self.commandbox_link.button_file
            except: pass
            else:
                if self.commandbox_link.button_file.active:
                    self.commandbox_link.button_file.active = False
            

    def select_save_name_callback(self,give_warning = False):
        self.exit()
        
        self.save_box = VFrame(Label("Name of savegame"))
        
        entry_box = Entry()
        entry_box.minsize = (300,24)
        entry_box.activate()
        
        
        ok_button = Button("Ok")
        ok_button.connect_signal(SIG_CLICKED,self.effectuate_save_callback)
        
        cancel_button = Button("Cancel")
        cancel_button.connect_signal(SIG_CLICKED,self.exit,True)
        
        button_frame = HFrame()
        button_frame.set_children([ok_button,cancel_button])
        
        if give_warning:
            warning_label = Label("Max " + str(global_variables.max_letters_in_company_names) + " characters, only letters, underscores and numbers")
            self.save_box.set_children([entry_box,button_frame,warning_label])
        
        else:
            self.save_box.set_children([entry_box,button_frame])
        
        self.save_box.topleft = (global_variables.window_size[0] / 2 - self.save_box.size[0] / 2, 100) 
        
        self.renderer.add_widget(self.save_box)
        
        
        
#        

    def effectuate_save_callback(self):
        save_game_name = self.save_box.children[0].text
        all_ok = True
        if len(save_game_name) > global_variables.max_letters_in_company_names:
            all_ok = False
        
        for i in range(0,len(save_game_name)):
            letter = save_game_name[i]
            if not (letter.isalnum() or letter.isalpha() or letter == "_"):
                all_ok = False
                
        if all_ok:
            
            
            self.solar_system_object_link.save_solar_system(os.path.join("savegames",save_game_name))
        
            self.exit(True)
            
        else:
            self.exit()
            self.select_save_name_callback(give_warning=True)
        

    def select_game_to_load_callback(self):
        self.exit()
        
        self.load_window = gui_extras.fast_list(self.renderer)
        
        self.load_window.receive_data(os.listdir("savegames"))
        self.load_window.topleft = (global_variables.window_size[0] / 2 - self.load_window.list_size[0] / 2, 100) 
        self.load_window.create_fast_list()

        self.load_button = Button("Load")
        self.load_button.connect_signal(SIG_CLICKED,self.effectuate_load_callback)
        self.load_button.topleft = (global_variables.window_size[0] / 2 - self.load_button.size[0] / 2, self.load_window.topleft[1] + self.load_window.list_size[1] + 50)
        self.renderer.add_widget(self.load_button)

    def effectuate_load_callback(self):
        load_file_name = self.load_window.selected
        if load_file_name is not None:
            self.exit(reset_commandbox_button = True)
            self.solar_system_object_link.load_solar_system(os.path.join("savegames",load_file_name))
    
        

    def new_game_callback(self):
        self.manager.emit("new_game",None)

    def game_settings_callback(self):
        """
        The window that is shown when asking for game_settings.
        First destroys the previous file window
        """
        self.exit()
        
        self.window = VFrame(Label("Game settings"))
        self.window.topleft = self.topleft
        
        button_names= ["#Game speed","#Difficulty","#Catastrophes"]
        button_functions = [self.time_delay_dialog,self.exit,self.catastrophe_window]
        
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

        self.renderer.add_widget(self.window)






    def automation_settings_callback(self):
        """
        The window that is shown when asking for automation_settings.
        First destroys the previous file window
        """
        self.exit()
        if self.solar_system_object_link.current_player is None:
            if self.solar_system_object_link.message_printing["debugging"]:
                print_dict = {"text":"DEBUGGING: Game is in simulation mode so no changes can be made","type":"debugging"}
                self.solar_system_object_link.messages.append(print_dict)
        else:
            button_names = self.solar_system_object_link.current_player.automation_dict.keys()
            self.window = VFrame(Label("Game settings"))
            self.window.topleft = self.topleft
            
            button_functions = [self.change_automation]
            
            list_of_children = []
            max_width = 0
            for i, button_name in enumerate(button_names):
                temp_button = ToggleButton(button_name)
                if self.solar_system_object_link.current_player.automation_dict[button_name]:
                    temp_button.active = True
                temp_button.connect_signal(SIG_TOGGLED,self.change_automation,button_name)
                max_width = max(max_width,temp_button.width)
                list_of_children.append(temp_button)
            
            for button in list_of_children:
                button.set_minimum_size(max_width,button.size[1])
            
            decision_variables_button = Button("Decision variables")
            decision_variables_button.connect_signal(SIG_CLICKED,self.decision_variables_callback)
            
            self.window.set_children(list_of_children + [Label(""), decision_variables_button])
    
    
    
            self.renderer.add_widget(self.window)


    def change_automation(self,automation_type):
        """
        Function that will effectuate the change of automation status
        """
        if self.solar_system_object_link.current_player is None:
            raise Exception("No player selected")
        if automation_type not in self.solar_system_object_link.current_player.automation_dict.keys():
            raise Exception("The automation_type " + str(automation_type) + " was not found in the automation_dict")
        previous_setting = self.solar_system_object_link.current_player.automation_dict[automation_type]
        self.solar_system_object_link.current_player.automation_dict[automation_type] = not previous_setting

        print_dict = {"text":"For " + self.solar_system_object_link.current_player.name + " the " + str(automation_type) + " was changed from " + str(previous_setting) + " to " + str(not previous_setting),"type":"general company info"}
        self.solar_system_object_link.messages.append(print_dict)
        self.manager.emit("update_infobox", None)
        
        

    def decision_variables_callback(self):
        """
        The window that is shown when asking for decision_variables.
        First destroys the previous file window
        """
        self.exit()
        if self.solar_system_object_link.current_player is None:
            if self.solar_system_object_link.message_printing["debugging"]:
                print_dict = {"text":"DEBUGGING: Game is in simulation mode so no changes can be made","type":"debugging"}
                self.solar_system_object_link.messages.append(print_dict)
        else:
            button_names = self.solar_system_object_link.current_player.company_database.keys()
            
            list_of_children = []
            max_width = 0
            for i, button_name in enumerate(button_names):
                if isinstance(self.solar_system_object_link.current_player.company_database[button_names[i]], int):
                    temp_label = Label(button_name)
                    max_width = max(max_width,temp_label.width)
                    list_of_children.append(temp_label)

            self.window = Table(len(list_of_children)/2+2,4)
            self.window.set_column_align(0,ALIGN_LEFT)
            self.window.set_column_align(2,ALIGN_LEFT)
            self.window.topleft = (50,50)


            for i, label in enumerate(list_of_children):
                
                label.set_minimum_size(max_width,label.size[1])
                if i > len(list_of_children)/2:
                    column = 2
                    row = i - len(list_of_children)/2 - 1 
                else:
                    column = 0
                    row = i
                self.window.add_child(row, 0 + column,label)
                value = self.solar_system_object_link.current_player.company_database[label.text]
                entry_box = Entry(text=str(value))
                self.window.add_child(row, 1 + column,entry_box)
                
            cancel_button = Button("Cancel")
            cancel_button.connect_signal(SIG_CLICKED,self.exit,True)
            
            ok_button = Button("Ok")
            ok_button.connect_signal(SIG_CLICKED,self.check_and_save_decision_variables)
            
            self.window.add_child(len(list_of_children)/2+1,3,cancel_button)
            self.window.add_child(len(list_of_children)/2+1,2,ok_button)
#            hframe.set_children([ok_button,cancel_button]) 

#            self.window = VFrame(Label("Automation settings"))
             
#            self.window.set_children([table,hframe])
    
            self.renderer.add_widget(self.window)
        


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
                        self.solar_system_object_link.messages.append(print_dict)
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
                        self.solar_system_object_link.messages.append(print_dict)
                        self.manager.emit("update_infobox", None)
                        all_passed_check = False
                        break
 
        if all_passed_check:
            print_dict = {"text":"The decision matrix has been updated for " + self.solar_system_object_link.current_player.name,"type":"general gameplay info"}
            self.solar_system_object_link.messages.append(print_dict)
            self.manager.emit("update_infobox", None)
            for column_offset in [0,2]:
                for row_index in range(0,self.window.rows - 1): #don't include rows with buttons
                    if self.window.grid[(row_index, column_offset)] is not None:
                        name = self.window.grid[(row_index, column_offset)].text
                        value = self.window.grid[(row_index, column_offset + 1)].text
                        value_as_int = int(value)
                        
                        self.solar_system_object_link.current_player.company_database[name] = value_as_int
            
            self.exit(True)
            


    def message_settings(self):
        """
        Function that decides what messages should be shown
        """
        self.exit()
        button_names = self.solar_system_object_link.message_printing.keys()
        self.window = VFrame(Label("Message settings"))
        self.window.topleft = self.topleft
        
        button_functions = [self.change_message_setting]
        
        list_of_children = []
        max_width = 0
        for i, button_name in enumerate(button_names):
            temp_button = ToggleButton(button_name)
            if self.solar_system_object_link.message_printing[button_name]:
                temp_button.active = True
            temp_button.connect_signal(SIG_TOGGLED,self.change_message_setting,button_name)
            max_width = max(max_width,temp_button.width)
            list_of_children.append(temp_button)
        
        for button in list_of_children:
            button.set_minimum_size(max_width,button.size[1])
        
        ok_button = Button("Ok")
        ok_button.connect_signal(SIG_CLICKED,self.exit,True)
        
        self.window.set_children(list_of_children + [Label(""), ok_button])

        self.renderer.add_widget(self.window)

    def change_message_setting(self, message_type):                        
        """
        Function that will effectuate the change of message settings
        """
        if message_type not in self.solar_system_object_link.message_printing.keys():
            raise Exception("The message type " + str(message_type) + " was not found in the message_printing dict")
        previous_setting = self.solar_system_object_link.message_printing[message_type]
        self.solar_system_object_link.message_printing[message_type] = not previous_setting

        print_dict = {"text":"The show-settings for " + str(message_type) + " was changed from " + str(previous_setting) + " to " + str(not previous_setting),"type":"general gameplay info"}
        self.solar_system_object_link.messages.append(print_dict)
        self.manager.emit("update_infobox", None)
                        
    
    def quit_callback(self):
        self.renderer.add_widget(self.quit_dialog())
        

    

#    def game_settings_dialog(self):
        
    def time_delay_dialog(self):
        """
        The window that is shown when asking for time delay settings
        Time delay settings is defined as a value between 0 and 100 with 100 being the fastest.
        It translates into the self.solar_system_object_link.step_delay_time
        which is a value between 0 (perform game-iteration at every loop-iteration) and infinity (but then the game will stop)
        a loop-iteration is the time it takes to react to clicks etc + 15 milliseconds (but check value pygame.time.delay in main 
        document to be sure). A game-iteration is all the movement of planets, thinking of companies etc.
        
        We here define the range of self.solar_system_object_link.step_delay_time as given in step_delay_time_range. This is certainly up to testing.
        In any case it means that the lowest value of step_delay_time_range equals time delays settings of 100 (max speed) and the highest
        value of step_delay_time_range equals time delay settings of 0 (slowest speed)
        """
        delay_range = (10,500)
        
        #seemingly complicated, but basically it just converts the old step_delay time to game speed (0-100) 
        old_game_speed = int(100 - ((float(self.solar_system_object_link.step_delay_time - delay_range[0]) / float(delay_range[1] - delay_range[0]) ) * 100))
        
        
        #print old_game_speed
        
        dialog = DialogWindow ("Time Settings")
        label = Label("Slow...                                           ...Fast")
        hscrollbar = HScrollBar (300, 3300)
        hscrollbar.set_step(30)
        hscrollbar.value = old_game_speed * 30

        def execute():
            game_speed = hscrollbar.value / 30
            #seemingly complicated, but basically it just converts the game speed (0-100) to the specified delay range
            self.solar_system_object_link.step_delay_time = int( ((100 - game_speed) / 100) * (delay_range[1] - delay_range[0]) + delay_range[0]) 
            dialog.destroy()
        
        #vscrollbar.connect_signal(SIG_VALCHANGED, self.scrolling)
        ok_button = Button("#Ok")
        ok_button.connect_signal(SIG_CLICKED,execute)
        cancel_button = Button("#Cancel")
        cancel_button.connect_signal(SIG_CLICKED,dialog.destroy)
        
        
        
        frame1 = VFrame()
        frame2 = HFrame()
        frame2.set_children([ok_button,cancel_button])
        frame1.set_children([label,hscrollbar,frame2])
        dialog.set_child(frame1)

        dialog.topleft = (200, 200)
        self.renderer.add_widget(dialog)

    def catastrophe_window(self):
        """
        The window that is shown when asking for catastrophes
        """
        self.exit()
        
        self.window = VFrame(Label("Catastrophe settings"))
        self.window.topleft = self.topleft
        
        button_names = ["Global warming","Global cooling","Meteor strike","Nuclear war","Lunar explosion","Skynet uprising"]
        button_functions = [self.raise_waters,self.lower_waters,self.exit,self.nuclear_war,self.exit,self.exit]
        
        list_of_children = []
        max_width = 0
        for i, button_name in enumerate(button_names):
            temp_button = Button(button_name)
            temp_button.connect_signal(SIG_CLICKED,button_functions[i])
            max_width = max(max_width,temp_button.width)
            list_of_children.append(temp_button)
        
        for button in list_of_children:
            button.set_minimum_size(max_width,button.size[1])
        
        ok_button = Button("Ok")
        ok_button.connect_signal(SIG_CLICKED,self.exit,True)
        
        self.window.set_children(list_of_children + [Label(""), ok_button])

        self.renderer.add_widget(self.window)

    def raise_waters(self):
        """
        Function to raise waters
        """
        
        self.manager.emit("raise_waters",None)
        self.manager.emit("update_infobox",None)
        
    def lower_waters(self):
        """
        Function to lower waters
        """
        self.manager.emit("lower_waters",None)
        self.manager.emit("update_infobox",None)

    def nuclear_war(self):
        """
        Function to lower waters
        """
        self.manager.emit("start nuclear war",None)



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
    
















        




class left_side_base_navigation(BaseObject):
    """
    The buttons on the left side which are only seen when in base mode. They are used to navigate between the subviews available
    for each base.
    """
    def __init__(self,solar_system_object,renderer,commandbox):
        BaseObject.__init__(self)
        self._signals["going_to_planetary_mode_event"] = []
        self._signals["going_to_solar_system_mode_event"] = []
        self._signals["going_to_base_mode_event"] = []
        self._signals["going_to_company_window_event"] = []
        self._signals["going_to_firm_window_event"] = []
        self._signals["going_to_techtree_mode_event"] = []
        self.renderer = renderer
        self.solar_system_object_link = solar_system_object
        self.topleft_pos = (0,0)
        self.area_size = (global_variables.window_size[0]*0.2 , global_variables.window_size[1])
        self.button_size = (130, 50)
        self.buttonlinks = ["base_population","base_list_of_companies","base_list_of_firms","market","base_build_menu"]
        self.buttonnicenames = ["Population","Companies","Firms","Market","Build"]
        self.basewindow_selected = None
        
    def notify(self,event):
        if event.signal == "going_to_base_mode_event":
            self.create_left_side_base_navigation()
        if event.signal in ["going_to_solar_system_mode_event","going_to_planetary_mode_event","going_to_company_window_event","going_to_firm_window_event","going_to_techtree_mode_event"]:
            self.exit()
        if event.signal == "going_to_firm_window_event":
            if isinstance(event.data,company.base):
                print "DEBUGGING: keeping the lefthandbasebecause we are going to another base"
            else:
                self.exit()

        
        
    def base_window_type_set_callback(self,button_name):
        self.basewindow_selected = button_name
        self.manager.emit("change_base_window_type",self.basewindow_selected)
        #print "emitted " + str(button_name)

    def exit(self):
        try: self.frames
        except: pass
        else:
            iteration_list = self.frames.keys()
            for frame_name in iteration_list:
                self.frames[frame_name].destroy()
                del self.frames[frame_name]
            del self.frames
        try: self.buttons
        except: pass
        else:
            iteration_list = self.buttons.keys()
            for button_name in iteration_list:
                del self.buttons[button_name]
             

    def create_left_side_base_navigation(self):
        """
        The creation function. Doesn't return anything, but saves self.window variable and renderes using the self.renderer. 
        """

        try: self.frames
        except:
            self.buttons = {}
            self.frames = {}
            base_navigation_group = None
            vertical_slice = self.area_size[1] / len(self.buttonlinks)
            for i in range(0,len(self.buttonlinks)):
                y_pos = int( (i + 0.5) * vertical_slice ) - (self.button_size[1] / 2)
                x_pos = (self.area_size[0] / 2 ) - (self.button_size[0] / 2)
                
                self.frames[self.buttonlinks[i]] = VFrame()
                self.frames[self.buttonlinks[i]].topleft = (x_pos,y_pos)
                self.buttons[self.buttonlinks[i]] = RadioButton(self.buttonnicenames[i],base_navigation_group)
                self.buttons[self.buttonlinks[i]].connect_signal(Constants.SIG_TOGGLED,self.base_window_type_set_callback,self.buttonlinks[i])
                self.buttons[self.buttonlinks[i]].minsize = self.button_size
                self.frames[self.buttonlinks[i]].add_child(self.buttons[self.buttonlinks[i]])
                self.renderer.add_widget(self.frames[self.buttonlinks[i]])
                if i == 0:
                    base_navigation_group = self.buttons[self.buttonlinks[i]]
                    self.buttons[self.buttonlinks[i]].base_navigation_group = self.buttons[self.buttonlinks[i]]
            if self.basewindow_selected is not None:
                self.buttons[self.basewindow_selected].set_active(True)
                self.manager.emit("change_base_window_type",self.basewindow_selected)
            #print "DEBGGING: emitted: " + str(self.basewindow_selected)
        else: 
            print "DEBUGGING: warning a create_left_side_base_navigation call was made when frames already existed"
            




class base_population_info(BaseObject):
    """
    Subview of the base view. Shows miscellanous information about a base, such as stock, trade routes and population.
    """

    def __init__(self,solar_system_object,renderer,commandbox):
        BaseObject.__init__(self)
        self._signals["going_to_planetary_mode_event"] = []
        self._signals["going_to_solar_system_mode_event"] = []
        self._signals["going_to_base_mode_event"] = []
        self._signals["going_to_company_window_event"] = []
        self._signals["going_to_firm_window_event"] = []
        self._signals["change_base_window_type"] = []
        self._signals["going_to_techtree_mode_event"] = []
        self.renderer = renderer
        self.solar_system_object_link = solar_system_object
        self.list_size = (650,450)
        self.topleft = (200, 100)



     
    def exit(self):
        try: self.window
        except: pass
        else: 
            self.window.exit()
            del self.window
        
    
    def notify(self,event):
        if event.signal == "change_base_window_type":
            if event.data == "base_population":
                self.create_base_population_info()
            else:
                self.exit()
        if event.signal in ["going_to_solar_system_mode_event","going_to_planetary_mode_event","going_to_company_window_event","going_to_firm_window_event","going_to_techtree_mode_event"]:
            self.exit()
        


    def create_base_population_info(self):
        """
        The creation function. Doesn't return anything, but saves self.window variable and renderes using the self.renderer. 
        """
        try: self.window
        except:
            base_selected = self.solar_system_object_link.current_planet.current_base
            if base_selected is not None:

                #print dir(base_selected)
                #print base_selected.accounting
                #print base_selected.input_output_dict
                #print base_selected.mining_opportunities
                #print base_selected.stock_dict
                #print base_selected.trade_routes
                base_population_dict= {}
                
                base_population_dict["Owner"] = {"info":base_selected.owner.name}
                base_population_dict["GDP per capita"] = {"info":base_selected.gdp_per_capita_in_dollars}
                base_population_dict["Position: east"] = {"info":str(base_selected.position_coordinate[0])}
                base_population_dict["Position: north"] = {"info":str(base_selected.position_coordinate[1])}
                base_population_dict["Population"] = {"info":base_selected.population}
                base_population_dict["Bitternes"] = {"info":base_selected.bitternes_of_base}
                base_population_dict["Wages"] = {"info":base_selected.wages}
                
                for resource in base_selected.mining_opportunities:
                     base_population_dict["Mining: " + resource] = {"info":base_selected.mining_opportunities[resource]["sum_of_resources"]}
                
                for resource in base_selected.stock_dict:
                     base_population_dict["Stock: " + resource] = {"info":base_selected.stock_dict[resource]}

                for resource in base_selected.input_output_dict["input"]:
                     base_population_dict["Input: " + resource] = {"info":base_selected.input_output_dict["input"][resource]}

                
                base_population_dict["Trade routes, number of"] = {"info":str(len(base_selected.trade_routes))}
                if 0 < len(base_selected.trade_routes) < 4:
                    list_value = str(base_selected.trade_routes.keys())
                    list_value = list_value.rstrip("]")
                    list_value = list_value.lstrip("[")
                    base_population_dict["Trade routes"] = {"info":list_value}
                

                
                self.window = gui_extras.fast_list(self.renderer)
                self.window.receive_data(base_population_dict,column_order = ["rownames","info"],sort_by="rownames")
                self.window.topleft = self.topleft
                self.window.list_size = self.list_size
                self.window.create_fast_list()
                self.window.render_title()
    #        
            else:
                print "DEBUGGING: Base selected was None"
        else:
            print "DEBUGGING: tried to paint a base_population_info, but this already existed"





class base_list_of_companies(BaseObject):
    """
    Subview of the base view. Shows a list of all companies operating in the base. Shortcut button to zoom in on one of these companies.
    """

    def __init__(self,solar_system_object,renderer,commandbox):
        BaseObject.__init__(self)
        self._signals["going_to_planetary_mode_event"] = []
        self._signals["going_to_solar_system_mode_event"] = []
        self._signals["going_to_base_mode_event"] = []
        self._signals["going_to_company_window_event"] = []
        self._signals["going_to_firm_window_event"] = []
        self._signals["change_base_window_type"] = []
        self._signals["going_to_techtree_mode_event"] = []

        self.renderer = renderer
        self.solar_system_object_link = solar_system_object
        self.topleft = (250,100)
        self.list_size = (600,400)
        self.frame_size = 40



#    def change_selection_callback(self):
#        try: self.window
#        except:
#            print "DEBUGGING: the change_selection_callback was made when the self.window did not exist"
#            print dir(self)
#        else:
#            if self.window.selection in self.solar_system_object_link.companies.keys():
#                selected_company = self.solar_system_object_link.companies[self.window.selection]
#                self.solar_system_object_link.company_selected = selected_company
#            else:
#                print self.solar_system_object_link.companies.keys()
#                print "self.window.selection: " + str(self.window.selection)
#                raise Exception("Did not find the selected company in the list of companies")
        
            #self.manager.emit("focus_on_company",selected_company)
        
    
    def go_to_company_window_event_callback(self):
        company_selected = None
        for company in self.solar_system_object_link.companies.values():
            if company.name == self.window.selected_name:
                company_selected = company
        if company_selected is None:
            for company in self.solar_system_object_link.companies.values():
                print company.name
            raise Exception("The company sought after (" + str(self.window.selected_name) + ") was not found in the companies list of the solar_system_object_link")
        print "DEBUGGING: emitted going to company_window_event with " + str(company_selected) + " of name " + str(company_selected.name)
        self.solar_system_object_link.company_selected = company_selected
        self.manager.emit("going_to_company_window_event",company_selected)
        

    def create_base_list_of_companies_window(self):
        """
        The creation function. Doesn't return anything, but saves self.window variable and renderes using the self.renderer. 
        """

        try: self.window
        except:
            company_data = {}
            for company_instance in self.solar_system_object_link.companies.values():
                if self.solar_system_object_link.current_planet.current_base.name in company_instance.home_cities.keys():
                    company_data[company_instance.name] = {}
                    company_data[company_instance.name]["capital"] = company_instance.capital
                    
                    owned_firms_here = 0
                    for firm_instance in company_instance.owned_firms.values():
                        if firm_instance.location == self.solar_system_object_link.current_planet.current_base:
                             owned_firms_here = owned_firms_here + 1
                             
                    company_data[company_instance.name]["local firms"] = owned_firms_here
            
            
            
            
            
            
            self.window = gui_extras.fast_list(self.renderer)
            self.window.receive_data(company_data)
            
            
            self.window.topleft = self.topleft
            self.window.list_size = self.list_size
            self.window.create_fast_list()
            self.window.render_title()
            
            self.go_to_company_window_button = Button("Company page")
            self.go_to_company_window_button.connect_signal(Constants.SIG_CLICKED,self.go_to_company_window_event_callback)
            self.go_to_company_window_button_frame = VFrame()
            self.go_to_company_window_button_frame.topleft = (self.window.topleft[0]+(self.list_size[0]/2)-self.go_to_company_window_button.size[0]/2,self.window.topleft[1] + self.list_size[1]+50)
            self.go_to_company_window_button_frame.add_child(self.go_to_company_window_button)
            self.renderer.add_widget(self.go_to_company_window_button_frame)
        else: print "DEBUGGING: warning a create_base_list_of_companies_window call was made when self.windows already existed"
        
        
    def exit(self):
        try: self.window
        except: pass
        else: 
            self.window.exit()
            del self.window
        try: self.go_to_company_window_button_frame
        except: pass#print "DEBUGGING: Did not find self.go_to_company_window_button" 
        else:
            self.go_to_company_window_button_frame.destroy()
            del self.go_to_company_window_button_frame
            del self.go_to_company_window_button
        
    
    def notify(self,event):
        if event.signal == "change_base_window_type":
            if event.data == "base_list_of_companies":
                self.create_base_list_of_companies_window()
            else:
                self.exit()
        if event.signal in ["going_to_solar_system_mode_event","going_to_planetary_mode_event","going_to_company_window_event","going_to_firm_window_event","going_to_techtree_mode_event"]:
            self.exit()
        


class base_list_of_firms(BaseObject):
    """
    Subview of the base view. Shows a list of all firms operating in the base. Shortcut button to zoom in on one of these firms.
    """

    def __init__(self,solar_system_object,renderer,commandbox):
        BaseObject.__init__(self)
        self._signals["going_to_planetary_mode_event"] = []
        self._signals["going_to_solar_system_mode_event"] = []
        self._signals["going_to_base_mode_event"] = []
        self._signals["going_to_company_window_event"] = []
        self._signals["going_to_firm_window_event"] = []
        self._signals["change_base_window_type"] = []
        self._signals["going_to_techtree_mode_event"] = []

        self.renderer = renderer
        self.solar_system_object_link = solar_system_object
        self.topleft = (250,100)
        self.list_size = (600,400)
        self.frame_size = 40

        
    
    def go_to_firm_window_event_callback(self):
        firm_selected = None
        for company_instance in self.solar_system_object_link.companies.values():
            for firm in company_instance.owned_firms.values():
                if firm.name == self.window.selected_name:
                    firm_selected = firm
        if firm_selected is None:
            print "POSSIBLE DEBUGGING: - the firm asked for was of None type"
        else:
            #print "DEBUGGING: the class is: " + str(firm.__class__)
            if isinstance(firm,company.base):
                self.manager.emit("going_to_base_mode_event",firm_selected)
            else:
                self.manager.emit("going_to_firm_window_event",firm_selected)

        

    def create_base_list_of_firms_window(self):
        """
        The creation function. Doesn't return anything, but saves self.window variable and renderes using the self.renderer. 
        """
        try: self.window
        except:
            list_of_firms_in_base = []
            for company_instance in self.solar_system_object_link.companies.values():
                for firm_instance in company_instance.owned_firms.values():
                    if not isinstance(firm_instance, company.merchant):
                        if firm_instance.location == self.solar_system_object_link.current_planet.current_base:
                            list_of_firms_in_base.append(firm_instance)
                    else:
                        if firm_instance.from_location == self.solar_system_object_link.current_planet.current_base or firm_instance.to_location == self.solar_system_object_link.current_planet.current_base:
                            list_of_firms_in_base.append(firm_instance)
    #        print list_of_firms_in_base
            firm_data = {}
            for firm_instance in list_of_firms_in_base:
                firm_data[firm_instance.name] = {}
                try: firm_instance.last_profit
                except: 
                    firm_data[firm_instance.name]["last profit"] = "NA"
                else: 
                    firm_data[firm_instance.name]["last profit"] = firm_instance.last_profit
                
                firm_data[firm_instance.name]["owner"] = firm_instance.owner.name
                
                stock_amount = 0
                for stock_item in firm_instance.stock_dict.values():
                    stock_amount = stock_amount + stock_item
                firm_data[firm_instance.name]["stock size"] = stock_amount
            
            self.window = gui_extras.fast_list(self.renderer)
            self.window.topleft = self.topleft
            self.window.list_size = self.list_size
            
            self.window.receive_data(firm_data) 
            
            self.window.create_fast_list()
            self.window.render_title()
            self.go_to_firm_window_button = Button("Firm page")
            self.go_to_firm_window_button.connect_signal(Constants.SIG_CLICKED,self.go_to_firm_window_event_callback)
            self.go_to_firm_window_button_frame = VFrame()
            self.go_to_firm_window_button_frame.topleft = (self.window.topleft[0]+(self.list_size[0]/2)-self.go_to_firm_window_button.size[0]/2,self.window.topleft[1] + self.list_size[1]+50)
            self.go_to_firm_window_button_frame.add_child(self.go_to_firm_window_button)
            self.renderer.add_widget(self.go_to_firm_window_button_frame)
        else: print "DEBUGGING: warning a base_list_of_firms call was made when self.windows already existed"

        
        
    def exit(self):
        try: self.window
        except: pass
        else: 
            self.window.exit()
            del self.window
        try: self.go_to_firm_window_button_frame
        except: pass 
        else:
            self.go_to_firm_window_button_frame.destroy()
            del self.go_to_firm_window_button_frame
            del self.go_to_firm_window_button
        
    
    def notify(self,event):
        if event.signal == "change_base_window_type":
            if event.data == "base_list_of_firms":
                self.create_base_list_of_firms_window()
            else:
                self.exit()
        if event.signal in ["going_to_solar_system_mode_event","going_to_planetary_mode_event","going_to_company_window_event","going_to_firm_window_event","going_to_techtree_mode_event"]:
            self.exit()
        



class base_and_firm_market_window(BaseObject):
    """
    Subview of the base view and also of the firm view. Shows information about the market in the base. For a chosen resource this can be either
    a history of what transactions has been made, or an overview of the bids currently in effect.
    
    This is also the interface where manual bids can be made
    """

    def __init__(self,solar_system_object,renderer,commandbox):
        BaseObject.__init__(self)
        self._signals["going_to_planetary_mode_event"] = []
        self._signals["going_to_solar_system_mode_event"] = []
        self._signals["going_to_base_mode_event"] = []
        self._signals["going_to_company_window_event"] = []
        self._signals["going_to_firm_window_event"] = []
        self._signals["change_base_window_type"] = []
        self._signals["change_firm_window_type"] = []
        self._signals["going_to_techtree_mode_event"] = []
        self._signals[SIG_CLICKED] = []
        self.renderer = renderer
        self.renderer.get_managers()[0].add_object(self, 5)
        self.solar_system_object_link = solar_system_object
        self.resource_selected = self.solar_system_object_link.trade_resources.keys()[0]
        self.graph_size = (400,400)
        self.topleft_everything = (300, 50)
        self.frame_size = 40
        self.blank_area_in_middle_height = 30 #the middle area in the market bid mode
        self.graph_selected = "history"
        self.positional_database = {"bidding_mode":{},"non_bidding_mode":{}} #can be filled with information about clicks that the graphs receive
        self.highlighted_transactions = []
        self.bidding_mode = False #if click on the map should result in bidding


    def trade_resource_set_callback(self,button_name):
        self.resource_selected = button_name
        self.update_data()

    def graph_mode_callback(self,button_name):
        self.graph_selected = button_name
        self.update_data()    


    def market_selection_callback(self,base_selected_for_merchant):
        self.base_selected_for_merchant = base_selected_for_merchant
        self.update_data()
        
    def place_bid_callback(self):
        self.bidding_mode = self.bid_button.active

    
    def create_base_and_firm_market_window(self,renderer):
        """
        The creation function. Doesn't return anything, but saves and renders using the self.renderer. 
        """

        try: self.resource_selection_frame
        except: pass
        else:   self.exit()

        
        #first making a list of the resources that should be displayed
        self.resource_selection_frame = VFrame(Label("Select resource"))
        self.resource_selection_frame.set_align(ALIGN_LEFT)
        if self.solar_system_object_link.display_mode == "base":
            resource_button_names = self.solar_system_object_link.trade_resources.keys()
        elif self.solar_system_object_link.display_mode == "firm":
            firm_selected = self.solar_system_object_link.firm_selected
            if isinstance(firm_selected, company.merchant):
                resource_button_names = [firm_selected.resource, firm_selected.transport_type]
            else:
                resource_button_names = []
                for put in ["input","output"]:
                    for resource in firm_selected.input_output_dict[put]:
                        resource_button_names.append(resource)
        else:
            raise Exception("The display mode " + str(self.solar_system_object_link.display_mode) + " is not supposed to show market data")

        if self.resource_selected not in resource_button_names:
            self.resource_selected = resource_button_names[0]
        #for each resource to be displayed we make a radio button
        market_resource_group = None
        button_size = []
        self.resource_buttons = {}
        for i, button in enumerate(resource_button_names):
            self.resource_buttons[button] = RadioButton(string.capitalize(button),market_resource_group)
            self.resource_buttons[button].connect_signal(Constants.SIG_TOGGLED,self.trade_resource_set_callback,button)
            self.resource_selection_frame.add_child(self.resource_buttons[button])
            if i == 0:
                market_resource_group = self.resource_buttons[button]
                self.resource_buttons[button].market_resource_group = self.resource_buttons[button]
        self.resource_buttons[self.resource_selected].set_active("True")
        self.resource_selection_frame.topleft = self.topleft_everything
        self.renderer.add_widget(self.resource_selection_frame)

        #Ready a box that selects which of the two graph types we are looking at
        self.graph_selection_frame = VFrame(Label("Select graph"))
        self.graph_selection_frame.set_align(ALIGN_LEFT)
        graph_button_names = ["history","market bids"]
        market_graph_type_group = None
        button_size = []
        self.graph_buttons = {}
        for i, button in enumerate(graph_button_names):
            self.graph_buttons[button] = RadioButton(string.capitalize(button),market_graph_type_group)
            self.graph_buttons[button].connect_signal(Constants.SIG_TOGGLED,self.graph_mode_callback,button)
            self.graph_selection_frame.add_child(self.graph_buttons[button])
            if i == 0:
                market_graph_type_group = self.graph_buttons[button]
                self.graph_buttons[button].market_graph_type_group = self.graph_buttons[button]
        self.graph_buttons[self.graph_selected].set_active(True)
        self.graph_selection_frame.topleft = (self.topleft_everything[0],self.topleft_everything[1]+ self.resource_selection_frame.size[1] + 15)
        self.graph_selection_frame.set_minimum_size(self.resource_selection_frame.size[0],1)
        self.renderer.add_widget(self.graph_selection_frame)
        
        #in case it is a merchant selected we have to also pick the markets looked upon.
        if self.solar_system_object_link.display_mode == "firm":
            firm_selected = self.solar_system_object_link.firm_selected
            if isinstance(firm_selected, company.merchant):
                self.market_selection_frame = VFrame(Label("Select market"))
                self.market_selection_frame.set_align(ALIGN_LEFT)
                
                from_location_button = RadioButton("From: " + firm_selected.from_location.name, None)
                to_location_button = RadioButton("To: " + firm_selected.to_location.name, from_location_button)
                from_location_button.active = True
                from_location_button.connect_signal(Constants.SIG_TOGGLED,self.market_selection_callback,firm_selected.from_location)
                to_location_button.connect_signal(Constants.SIG_TOGGLED,self.market_selection_callback,firm_selected.to_location)
                self.market_selection_frame.topleft = (self.topleft_everything[0],self.graph_selection_frame.topleft[1]+ self.graph_selection_frame.size[1] + 15)
                self.market_selection_frame.set_minimum_size(self.resource_selection_frame.size[0],1)
                self.market_selection_frame.set_children([from_location_button,to_location_button])
                self.base_selected_for_merchant = firm_selected.from_location
                self.renderer.add_widget(self.market_selection_frame)
                
            else:
                try:    self.base_selected_for_merchant
                except: pass
                else:
                    del self.base_selected_for_merchant
        elif self.solar_system_object_link.display_mode == "base":
            firm_selected = self.solar_system_object_link.current_planet.current_base 
        else:
            raise Exception("Unknown display_mode: " + str(global_variabes.display_mode))
                    
        #Add an update button that allows for updates to be done
        self.update_button = Button("#Update")
        self.update_button.connect_signal(Constants.SIG_CLICKED,self.update_data)
        self.update_button.set_minimum_size(self.resource_selection_frame.size[0],1)
        try:    self.market_selection_frame.size
        except: self.update_button.topleft = (self.topleft_everything[0],self.graph_selection_frame.topleft[1]+ self.graph_selection_frame.size[1] + 15)
        else:   self.update_button.topleft = (self.topleft_everything[0],self.market_selection_frame.topleft[1]+ self.market_selection_frame.size[1] + 15)   
        self.renderer.add_widget(self.update_button)
        
        #Finally, in case the firm selected is owned by the player, we add a "make market bid button"
        
        if firm_selected.name in self.solar_system_object_link.current_player.owned_firms.keys():
            self.bid_button = ToggleButton("Make market bid")
            self.bid_button.connect_signal(Constants.SIG_TOGGLED,self.place_bid_callback)
            self.bid_button.set_minimum_size(self.resource_selection_frame.size[0],1)
            self.bid_button.topleft = (self.topleft_everything[0],self.update_button.topleft[1]+ self.update_button.size[1] + 15)
            self.renderer.add_widget(self.bid_button)
            self.bidding_mode = self.bid_button.active
        else:
            self.bidding_mode = False
            
        self.update_data()
            
        
    def update_data(self):
        """
        Function to update the data in the market analysis window. Its most important function is that it calls the relevant
        analysis function (market bids or market history) depending on the self.graph_selected variable.
        """
        #can not exist without the selection frames
        try:    self.resource_selection_frame
        except: 
            create_base_and_firm_market_window(self.renderer)
            print "DEBUGGING: update_data() was called without create_base_and_firm_market_window" 
        else:
            pass
        
        self.highlighted_transactions = []
        if self.graph_selected == "market bids":
            surface = self.update_data_market_bids()
        elif self.graph_selected == "history":
            surface = self.update_data_history()
        else:
            raise Exception("Unknown graph type " + self.graph_selected)

        if not isinstance(surface,pygame.Surface):
            print self.graph_selected
            print surface
            print self.update_data_history()
            print self.update_data_market_bids()
            raise Exception("The surface returned in the market window was not recognised")

        try: self.graph_surface_label
        except: 
            self.graph_surface_label = ImageLabel(surface)
            self.graph_frame = VFrame(Label("Market overview"))
            self.graph_frame.topleft = (self.topleft_everything[0] + 150,self.topleft_everything[1])
            self.graph_frame.add_child(self.graph_surface_label)
            self.renderer.add_widget(self.graph_frame)
        else:
            #print "remember to change labels. Right now it is " + str(self.graph_frame.label)
            self.graph_surface_label.set_picture(surface)
            self.renderer.update()


    def update_data_market_bids(self):
        """
        Function that draws a stock-market style surface with all the sell and buy bids that currently exists for a given resource
        """
        if self.solar_system_object_link.current_planet.current_base is None:
            raise Exception("A market bid window was requested at a time when the selected base was None")
        else:
            resource = self.resource_selected
            
            
            #first determining which market to look at. If in base mode it is obvious which. In firm for non-merchants it is home city, and for merchant it should be selectable
            if self.solar_system_object_link.display_mode == "base":
                market = self.solar_system_object_link.current_planet.current_base.market
            elif self.solar_system_object_link.display_mode == "firm":
                firm_selected = self.solar_system_object_link.firm_selected
                if isinstance(firm_selected, company.merchant):
                    market = self.base_selected_for_merchant.market
                else:
                    market = firm_selected.location.market
            else:
                raise Exception("The display mode " + str(self.solar_system_object_link.display_mode) + " is not supposed to show market data")

            #painting the basic market_analysis surface
            market_analysis_surface = pygame.Surface(self.graph_size)
            market_analysis_surface.fill((234,228,223))
            pygame.draw.line(market_analysis_surface,(50,50,50),(0,self.graph_size[1]*0.5+7),(self.graph_size[1],self.graph_size[1]*0.5+7),3)
            pygame.draw.line(market_analysis_surface,(50,50,50),(0,self.graph_size[1]*0.5-7),(self.graph_size[1],self.graph_size[1]*0.5-7),3)
            
            #making lists of quantitites, prices and providers
            quantities = []
            prices = []
            provider = []
            for offer_type in ["sell_offers","buy_offers"]:
                offers = market[offer_type][resource]
                for offer in offers:
                    quantities.append(offer["quantity"])
                    prices.append(offer["price"])
                    if "seller" in offer.keys():
                        provider.append(offer["seller"])
                    elif "buyer" in offer.keys():
                        provider.append(offer["buyer"])
                    else:
                        raise Exception("An offer was found in which there was neither seller nor buyer")
            
            
            if len(prices)==0:
                market_price_label = global_variables.standard_font.render("No " + resource + " on market",True,(0,0,0))
                market_analysis_surface.blit(market_price_label,(0,self.graph_size[1]*0.5-4))
            else:
                #calculating max price and market price. Adding these as labels if relevant.
                max_price = max(prices)
                min_price = min(prices)
                max_quantity = max(quantities)
                sell = global_variables.standard_font.render("Max sell price: " + "%.5g" % max_price,True,(0,0,0))
                buy = global_variables.standard_font.render("Min buy price: " + "%.5g" % min_price,True,(0,0,0))
                if len(market["buy_offers"][resource]) == 0:
                    market_price = market["sell_offers"][resource][0]["price"]
                    market_price_description = "Only sell offers. Lowest is: " + "%.5g" % market["sell_offers"][resource][0]["price"]
                    market_analysis_surface.blit(sell,(0,0))
                elif len(market["sell_offers"][resource]) == 0:
                    market_price = market["buy_offers"][resource][0]["price"]
                    market_price_description = "Only buy offers. Highest is: " + "%.5g" % market["buy_offers"][resource][0]["price"]
                    market_analysis_surface.blit(buy,(0,self.graph_size[1]-15))

                else:
                    market_price_description = "Highest buy offer: " + "%.5g" % market["buy_offers"][resource][0]["price"] + ". Lowest sell offer: " + "%.5g" % market["sell_offers"][resource][0]["price"] 
                    market_price = (market["sell_offers"][resource][0]["price"] + market["buy_offers"][resource][0]["price"]) * 0.5
                    market_analysis_surface.blit(sell,(0,0))
                    market_analysis_surface.blit(buy,(0,self.graph_size[1]-15))
                market_price_label = global_variables.standard_font.render(market_price_description,True,(0,0,0))
                market_analysis_surface.blit(market_price_label,(self.graph_size[0]/100,self.graph_size[1]*0.5-4))
                
                if market_analysis_surface is None:
                    raise Exception("After plotting the mean price on the market_analysis_surface it suddenly became None")

                
                #calculating the span of the y_axis and the x_axis. The y_axis is special because it needs to be same scale on
                #both sellers and buyers side, even if one is entirely empty. That's the reason for the 'sell_offers_have_higher_span'
                if max_price - market_price > market_price - min_price:
                    sell_offers_have_higher_span = True
                    ylim = (- max_price + 2 * market_price, max_price) 
                else:    
                    sell_offers_have_higher_span = False
                    ylim = (min_price,market_price * 2 - min_price)

                
                xlim = (0,max_quantity)
                if ylim[0] == ylim[1]:
                    ylim = (ylim[0]-1,ylim[1]+1)
                y_position_here = self.frame_size
                self.positional_database = {"bidding_mode":{},"non_bidding_mode":{}}
                self.positional_database["bidding_mode"]["price"] = ylim
                self.positional_database["bidding_mode"]["quantity"] = xlim
                
                #plotting all data points. The reason it is divided by _next, _here, and _before is that it is faster to make a positional database that way
                # ie. to delineate where a click reacts to what. In sparse plots it is okay with plenty of imprecision, but if there are many bids the precision in clicking is of course
                #required to be higher
                for i in range(0,len(prices)):
                    
                    plotting_area_height = self.graph_size[1] - self.frame_size * 2 - self.blank_area_in_middle_height
                    y_position_before = y_position_here
                    if i == 0:
                        y_position_here = (self.graph_size[1] - self.frame_size) - (((prices[i] - ylim[0]) / ( ylim[1] - ylim[0])) * plotting_area_height )
                    else:
                        y_position_here = y_position_next
                    
                    if i == len(prices)-1:
                        y_position_next = self.graph_size[1] - self.frame_size
                    else:
                        y_position_next = (self.graph_size[1] - self.frame_size) - (((prices[i+1] - ylim[0]) / ( ylim[1] - ylim[0])) * plotting_area_height )
                    
                    x_length = int((self.graph_size[1]) * math.log10(quantities[i]) / math.log10(xlim[1]) ) 
                    
                    if ((prices[i] - ylim[0]) / ( ylim[1] - ylim[0])) > 0.5: #ie if this is a sell offer
                        y_position_here = y_position_here - self.blank_area_in_middle_height
                    pygame.draw.line(market_analysis_surface,(50,50,50),(0,y_position_here),(x_length,y_position_here))
                    
                    #making positional database for linking clicking on the graph
                    max_width_of_selection_area = 10
                    top_border_length = min((y_position_here - y_position_before)/2,max_width_of_selection_area)
                    bottom_border_length = min((y_position_next - y_position_here)/2,max_width_of_selection_area)
                    top_border = y_position_here - top_border_length + self.topleft_everything[1] + 21 #the 21 is empirical. I think it is the frame height
                    height = top_border_length + bottom_border_length
                    if height == 0: height = 1
                    left_border = self.topleft_everything[0] + 150 + 7 #the seven is empirical (i think it is the frame)
                    width = x_length
                    #debugging_info = "exact y_pos: " + str(y_position_here + self.topleft_everything[1] + 21) + " top border: +" + str(top_border_length) + " bottom border: -" + str(bottom_border_length) 
                    self.positional_database["non_bidding_mode"][(left_border,top_border,width,height)] = {"linkto":provider[i],"text":provider[i].name + ": " + "%.5g" % prices[i],"figure":((0,y_position_here),(x_length,y_position_here))}
                
                
                #making x-axis scale
                x_axis_vertical_position_percent_of_frame = 0.9 # in percent of lower frame where 1 is at top of frame
                x_axis_vertical_position = self.graph_size[1]-int(self.frame_size*x_axis_vertical_position_percent_of_frame)
                pygame.draw.line(market_analysis_surface,(0,0,0),(0,x_axis_vertical_position),(self.graph_size[0],x_axis_vertical_position),3)
                pygame.draw.line(market_analysis_surface,(0,0,0),(0,self.graph_size[1] - x_axis_vertical_position),(self.graph_size[0],self.graph_size[1] - x_axis_vertical_position),3)
                pygame.draw.line(market_analysis_surface,(0,0,0),(0,x_axis_vertical_position),(0,self.graph_size[1] - x_axis_vertical_position),3)
                pygame.draw.line(market_analysis_surface,(0,0,0),(self.graph_size[0],x_axis_vertical_position),(self.graph_size[0],self.graph_size[1] - x_axis_vertical_position),3)
                max_x_axis_mark = 10 ** math.floor(math.log10(max_quantity)) #the value of the maximal x-axis mark. If eg. max_quantity is 1021, the max_x_axis_mark is 10^4
                if (max_quantity / max_x_axis_mark) < 6: # because then there is no room for the "units" marker
                    max_x_axis_mark = max_x_axis_mark / 10
                max_x_axis_mark_pos = int((self.graph_size[1]) * math.log10(max_x_axis_mark) / math.log10(xlim[1]) )
                mark_height = self.graph_size[1] / 50
                for i in range(0,10): #iterating "downwards" so to speak, because the x_mark_line will give the lineage of 10fold lower marks
                    x_mark_here = int(max_x_axis_mark / (10**i))
                    if x_mark_here < 10: #we stop the show at 10
                        break
                    x_pos_here = int((self.graph_size[1]) * math.log10(x_mark_here) / math.log10(xlim[1]) )
                    pygame.draw.line(market_analysis_surface,(0,0,0),(x_pos_here,x_axis_vertical_position + mark_height/2),(x_pos_here,x_axis_vertical_position - mark_height/2))
                    x_mark_label_text = "10^"+str(int(math.log10(x_mark_here)))
                    if i == 0:
                        x_mark_label_text = x_mark_label_text + " units"  
                    x_mark_label = global_variables.standard_font.render(x_mark_label_text,True,(0,0,0))
                    market_analysis_surface.blit(x_mark_label,(x_pos_here-self.graph_size[0]/100,x_axis_vertical_position + (mark_height)))
                    if market_analysis_surface is None:
                        raise Exception("At the end of the market_analysis_surface section, the surface had become None")
                
        return market_analysis_surface
                
        

            


    def update_data_history(self):
        history_surface = pygame.Surface(self.graph_size)
        history_surface.fill((234,228,223))
        resource = self.resource_selected
        
        #determining which market to look at. If in base mode it is obvious which. In firm for non-merchants it is home city, and for merchant it should be selectable
        if self.solar_system_object_link.display_mode == "base":
            market = self.solar_system_object_link.current_planet.current_base.market
        elif self.solar_system_object_link.display_mode == "firm":
            firm_selected = self.solar_system_object_link.firm_selected
            if isinstance(firm_selected, company.merchant):
                market = self.base_selected_for_merchant.market
            else:
                market = firm_selected.location.market
        else:
            raise Exception("The display mode " + str(self.solar_system_object_link.display_mode) + " is not supposed to show market data")

        if len(market["transactions"][resource])==0:
            no_history_label = global_variables.standard_font.render("No " + resource + " sold on market",True,(0,0,0))
            history_surface.blit(no_history_label,(0,self.graph_size[1]*0.5-4))
        else:
            start_date = market["transactions"][resource][0]["date"]
            end_date = market["transactions"][resource][-1]["date"]
            relative_numeric_start_date = (start_date - self.solar_system_object_link.start_date).days
            relative_numeric_end_date = (end_date - self.solar_system_object_link.start_date).days
            xlim = (relative_numeric_start_date,relative_numeric_end_date)
            dates = []
            price = []
            quantity = []
            seller = []
            buyer = []
            for transaction in market["transactions"][resource]:
                dates.append((transaction["date"] - self.solar_system_object_link.start_date).days)
                price.append(transaction["price"])
                quantity.append(transaction["quantity"])
                seller.append(transaction["seller"])
                buyer.append(transaction["buyer"])
            ylim = (0,max(price))
            if ylim[0] == ylim[1]:
                ylim = (ylim[0]-1,ylim[1]+1)
            if xlim[0] == xlim[1]:
                xlim = (xlim[0]-1,xlim[1]+1)
            
            history_surface = primitives.make_linear_y_axis(history_surface, self.frame_size, ylim, self.solar_system_object_link, unit ="price")
            history_surface = primitives.make_linear_x_axis(history_surface, self.frame_size, xlim, solar_system_object_link = self.solar_system_object_link, unit = "date")
            
            
            self.positional_database = {"bidding_mode":{},"non_bidding_mode":{}}
            self.positional_database["bidding_mode"]["price"] = ylim
            
            for i in range(0,len(price)):
                x_position = int(self.frame_size + ((self.graph_size[0]-self.frame_size*2) * (dates[i] - xlim[0])) / (xlim[1]-xlim[0]))
                y_position = int(self.graph_size[1] - (self.frame_size + ( (self.graph_size[1]-self.frame_size*2) * (price[i] - ylim[0]) / (ylim[1]-ylim[0]) )))
                try: dot_size = int(math.log10(quantity[i]))
                except:
                    print "DEBUGGING WARNING: quantity in a depicted transaction was " + str(quantity[i]) + " and this made the log function crash. You should probably look into the market functions and investigate why some bids are 0 or negative"
                    print "all quantities: " + str(quantity)
                    dot_size = 1
                pygame.draw.circle(history_surface,(0,0,0),(x_position,y_position),dot_size)
                
                
                left_border = x_position + self.topleft_everything[0] + 150 - dot_size + 7 
                top_border = y_position + self.topleft_everything[1] + 21 - dot_size #the 21 is empirical. I think it is the frame height
                if seller[i] is not None and buyer[i] is not None: #can happen with the empty startup transactions
                    self.positional_database["non_bidding_mode"][(left_border,top_border,2*dot_size,2*dot_size)] = {"linkto":seller[i],"text":str(seller[i].name) + " to " + str(buyer[i].name) + ": 10^" + str(dot_size) + "units","figure":((dot_size),(x_position,y_position)),"debug":left_border- dot_size}

            if len(price) != len(quantity) or len(price) != len(dates):
                raise Exception("DEBUGGING WARNING: There is a problem with unequal length in the markethistoryplotter")
                    
        return(history_surface)



    def make_manual_bid(self,price,quantity):
        """
        Function that will effectuate the bid, depending on the resource chosen
        """
        resource = self.resource_selected

        if self.solar_system_object_link.display_mode == "base":
            firm_selected = self.solar_system_object_link.current_planet.current_base
        elif self.solar_system_object_link.display_mode == "firm":
            firm_selected = self.solar_system_object_link.firm_selected
        else:
            raise Exception("The display mode " + str(self.solar_system_object_link.display_mode) + " is not supposed to show market data")

        
        
        self.exit()
        self.bid_window = Table(6,3)
        self.bid_window.topleft = (self.topleft_everything[0] + 100, self.topleft_everything[1] + 100)
        
        #row 0: price
        self.bid_window.add_child(0, 0, Label("Price"))
        self.bid_window.add_child(0, 1, Entry(price))
        self.bid_window.add_child(0, 2, Label("Capital: " + str(firm_selected.owner.capital)))
        
        #row 1: quantity
        self.bid_window.add_child(1, 0, Label("Quantity"))
        self.bid_window.add_child(1, 1, Entry(quantity))
        
        if isinstance(firm_selected, company.merchant):
            if self.base_selected_for_merchant == firm_selected.from_location:
                stock = firm_selected.from_stock_dict[resource]
            elif self.base_selected_for_merchant == firm_selected.to_location:
                stock = firm_selected.to_stock_dict[resource]
            else:
                raise Exception("The self.base_selected_for_merchant " + str(self.base_selected_for_merchant.name) + " was neither in the from or the to_location of " + str(firm_selected.name))
            self.bid_window.add_child(1, 2, Label("Stock: " + str(stock)))
        else:
            self.bid_window.add_child(1, 2, Label("Stock: " + str(firm_selected.stock_dict[resource])))
        
        #row 2: direction info
        self.bid_window.add_child(2, 0, Label("Direction"))
        sell_button = RadioButton("Sell", None)
        buy_button = RadioButton("Buy", sell_button)
        if isinstance(firm_selected, company.merchant): 
            if self.base_selected_for_merchant == firm_selected.from_location:
                buy_button.active = True 
            else:
                sell_button.active = True
        elif resource in firm_selected.input_output_dict["input"]:
            buy_button.active = True
        elif resource in firm_selected.input_output_dict["output"]:
            sell_button.active = True
        else:
            raise Exception("Oddly the resource " + str(resource) + " was neither found in the input or output of " + str(firm_selected.name)) 
        self.bid_window.add_child(2, 1, buy_button)
        self.bid_window.add_child(2, 2, sell_button)
        
        #row 3: show location
        self.bid_window.add_child(3, 0, Label("Location"))
        if isinstance(firm_selected, company.merchant): 
            from_button = RadioButton(firm_selected.from_location.name, None)
            to_button = RadioButton(firm_selected.to_location.name, from_button)
            if self.base_selected_for_merchant == firm_selected.from_location:
                from_button.active = True 
            else:
                to_button.active = True
            self.bid_window.add_child(3, 1, from_button)
            self.bid_window.add_child(3, 2, to_button)
        
        else:
            self.bid_window.add_child(3, 1, Label(firm_selected.location.name))
            
        
        #row 4: show which resource was chosen
        self.bid_window.add_child(4, 0, Label("Resource"))
        if isinstance(firm_selected, company.merchant): 
            resource_button = RadioButton(firm_selected.resource, None)
            transport_button = RadioButton(firm_selected.transport_type, resource_button)
            if resource == firm_selected.resource:
                resource_button.active = True
            else:
                transport_button.active = True
            self.bid_window.add_child(4, 1, resource_button)
            self.bid_window.add_child(4, 2, transport_button)
            
        else:
            self.bid_window.add_child(4, 1, Label(resource))
        
        #row 5: effectuate buttons
        ok_button = Button("Ok")
        ok_button.connect_signal(SIG_CLICKED,self.effectuate_market_bid)
        self.bid_window.add_child(5, 0, ok_button)

        cancel_button = Button("Cancel")
        def cancel_here():
            self.exit()
            self.create_base_and_firm_market_window(self.renderer)
        cancel_button.connect_signal(SIG_CLICKED,cancel_here)
        self.bid_window.add_child(5, 1, cancel_button)
        self.renderer.add_widget(self.bid_window)        
        


    def effectuate_market_bid(self):
        """
        Function that will check if the given numbers are ok, and if so effectuate the market bid
        """
        
        all_ok = True
        if self.solar_system_object_link.display_mode == "base":
            firm_selected = self.solar_system_object_link.current_planet.current_base
        elif self.solar_system_object_link.display_mode == "firm":
            firm_selected = self.solar_system_object_link.firm_selected
        else:
            raise Exception("The display mode " + str(self.solar_system_object_link.display_mode) + " is not supposed to show market data")
        price = self.bid_window.grid[(0,1)].text
        quantity = self.bid_window.grid[(1,1)].text
        
        #determining direction
        if self.bid_window.grid[(2,1)].active:
            direction = "buy"
        elif self.bid_window.grid[(2,2)].active:
            direction = "sell"
        else:
            all_ok = False
            if self.solar_system_object_link.message_printing["debugging"]:
                print_dict = {"text":"DEBUGGING: no direction was selected","type":"debugging"}
                self.solar_system_object_link.messages.append(print_dict)
                self.manager.emit("update_infobox", None)

        
        #determining market
        if isinstance(firm_selected, company.merchant): 
            if self.bid_window.grid[(3,1)].active:
                market = firm_selected.from_location.market
            elif self.bid_window.grid[(3,2)].active:
                market = firm_selected.to_location.market
            else:
                all_ok = False
                if self.solar_system_object_link.message_printing["debugging"]:
                    print_dict = {"text":"DEBUGGING: no market was selected","type":"debugging"}
                    self.solar_system_object_link.messages.append(print_dict)
                    self.manager.emit("update_infobox", None)
        else:
            market = firm_selected.location.market

        
        #determining resource
        if isinstance(firm_selected, company.merchant):
            if self.bid_window.grid[(4,1)].active:
                resource = firm_selected.resource
            elif self.bid_window.grid[(4,2)].active:
                resource = firm_selected.transport_type
            else:
                all_ok = False
                if self.solar_system_object_link.message_printing["debugging"]:
                    print_dict = {"text":"DEBUGGING: no resource was selected","type":"debugging"}
                    self.solar_system_object_link.messages.append(print_dict)
                    self.manager.emit("update_infobox", None)
            
        else:
            resource = self.bid_window.grid[(4,1)].text
        
        
        
        
        if direction not in ["sell","buy"]:
            if self.solar_system_object_link.message_printing["debugging"]:
                print_dict = {"text":"The direction " + str(direction) + " was not recognized. Must be sell or buy","type":"debugging"}
                self.solar_system_object_link.messages.append(print_dict)
                self.manager.emit("update_infobox", None)
            all_ok = False

        try:    float(price)
        except:
            print_dict = {"text":"The price " + str(price) + " could not be converted into a decimal number. Please use another.","type":"general gameplay info"}
            self.solar_system_object_link.messages.append(print_dict)
            self.manager.emit("update_infobox", None)
            all_ok = False
        else:
            pass
        
        
        try:    int(quantity)
        except:
            print_dict = {"text":"The quantity " + str(quantity) + " could not be converted into an integer number. Please use another.","type":"general gameplay info"}
            self.solar_system_object_link.messages.append(print_dict)
            self.manager.emit("update_infobox", None)
            all_ok = False
        else:
            pass
        
#        if isinstance(firm_selected, company.merchant): #then we need to see see if it buys in the from location or to location
        
        if all_ok:
            self.exit()
            if direction == "buy":
                own_offer = {"resource":resource,"price":float(price),"buyer":firm_selected,"name":firm_selected.name,"quantity":int(quantity),"date":self.solar_system_object_link.current_date}
            elif direction == "sell":
                own_offer = {"resource":resource,"price":float(price),"seller":firm_selected,"name":firm_selected.name,"quantity":int(quantity),"date":self.solar_system_object_link.current_date}
            
            firm_selected.make_market_bid(market,own_offer)
            print_dict = {"text":firm_selected.name + " succesfully made a " + str(direction) + " bid for " + str(quantity) + " units of " + str(resource) + " at price " + str(price),"type":"general gameplay info"}
            self.solar_system_object_link.messages.append(print_dict)
            self.manager.emit("update_infobox", None)
            self.create_base_and_firm_market_window(self.renderer)


                    

    def exit(self):
        try: self.resource_selection_frame
        except: pass
        else:
            self.resource_selection_frame.destroy()
            del self.resource_selection_frame
            del self.resource_buttons
        try: self.graph_selection_frame
        except: pass
        else:
            self.graph_selection_frame.destroy()
            del self.graph_selection_frame
            del self.graph_buttons
        
        try: self.graph_frame
        except:
            pass
        else:
            self.graph_frame.destroy()
            del self.graph_frame
            del self.graph_surface_label
        
        try:    self.market_selection_frame
        except:
            pass
        else:
            self.market_selection_frame.destroy()
            del self.market_selection_frame
        
        try:    self.update_button
        except:
            pass
        else:
            self.update_button.destroy()
            del self.update_button
        
        try: self.bid_button
        except: pass
        else: 
            try:    self.bid_button._manager
            except: pass
            else:
                self.bid_button.destroy()
            del self.bid_button
            
        try:    self.bid_window
        except: pass
        else:
            self.bid_window.destroy()
            del self.bid_window

        
    def react_to_click(self,position):
        """
        Function that will take the position of a mouse click and check if any market-window variables (either history or market bids)
        are present at that position. If so, it will highlight these with further info on first click and provide a link on second click
        """ 
        
        if self.bidding_mode: #if the graphs accept bids we start the bidding sections up
            if self.graph_selected == "market bids":
                top_of_plot = self.topleft_everything[1] + self.frame_size  + 21
                self.blank_area_in_middle_height
                y_position =  position[1] - top_of_plot
                if y_position > (self.graph_size[1] - 2 * self.frame_size) / 2 + self.blank_area_in_middle_height/2:
                    y_position = y_position - self.blank_area_in_middle_height #more than half - correct and move on
                elif y_position > (self.graph_size[1] - 2 * self.frame_size) / 2 - self.blank_area_in_middle_height/2:
                    return None #Hit half - don't continue
                height_of_plot = self.graph_size[1] - 2 * self.frame_size - self.blank_area_in_middle_height 
                y_relative_position = 1.0 - (y_position / float(height_of_plot))
            else:
                y_relative_position =  ((self.graph_size[1] - self.frame_size) - (position[1] - self.topleft_everything[1] - 21)) / float(self.graph_size[1] - self.frame_size)

            x_relative_position =  (position[0] - self.topleft_everything[0] - 150) / float(self.graph_size[0])
            if 0 < x_relative_position < 1:
                if 0 < y_relative_position < 1:
                    if "price" in self.positional_database["bidding_mode"].keys():
                        min_price = self.positional_database["bidding_mode"]["price"][0]
                        max_price = self.positional_database["bidding_mode"]["price"][1]
                        price = y_relative_position * (max_price - min_price) + min_price
                        if price < 0:
                            print "Changed price from " + str(price) + " to 0"
                            price = 0
                            
                        price = str(price)
                    else:
                        price = ""
                        
                    if "quantity" in self.positional_database["bidding_mode"].keys():
                        max_qt = self.positional_database["bidding_mode"]["quantity"][1]
                        try:    math.log10(max_qt)
                        except: 
                            print "DEBUGGING: no good selection of log10 max_qt"
                            quantity = ""
                        else:
                            quantity = str(int(10 ** (math.log10(max_qt) * x_relative_position)))  
                    else:
                        quantity = ""
                
#                    print "click at " + str((x_relative_position,y_relative_position)) + " gives price: " + str(price) + " and qt: " + str(quantity)
                    self.make_manual_bid(price,quantity)
                        
                        
            
                
        
        else:  #if the graphs do not accept bids we only display some information
            click_spot = pygame.Rect(position[0]-1,position[1]-1,2,2)
            click_spot_result = click_spot.collidedict(self.positional_database["non_bidding_mode"])
            if click_spot_result is not None:
                try: self.graph_surface_label
                except: pass
                else:
                    if click_spot_result[1] in self.highlighted_transactions:
                        if not isinstance(click_spot_result[1]["linkto"],company.base): #if it was a base there would be no point, since it would already in zoom
                            self.manager.emit("going_to_firm_window_event",click_spot_result[1]["linkto"])
                    else:
                        self.highlighted_transactions.append(click_spot_result[1])
                        surface = self.graph_surface_label.picture
                        
                        text_size = global_variables.standard_font.size(click_spot_result[1]["text"]) 
                        text = global_variables.standard_font.render(click_spot_result[1]["text"],True,(0,0,0))
                        
                        text_position = (click_spot_result[1]["figure"][1][0]-text_size[0],click_spot_result[1]["figure"][1][1])
                        
                        if text_position[0] < self.frame_size:
                            text_position = (self.frame_size,text_position[1])
                            #print "corrected text position a little" 
                        
                        surface.blit(text,text_position)
                        
                        if self.graph_selected == "market bids":
                            pygame.draw.line(surface,(100,100,255),click_spot_result[1]["figure"][0],click_spot_result[1]["figure"][1])
                        elif self.graph_selected == "history":
                            pygame.draw.circle(surface,(100,100,255),click_spot_result[1]["figure"][1],click_spot_result[1]["figure"][0])
                            #print click_spot_result[1]["debug"]
                        else:
                            raise Exception("Unknown graph type " + self.graph_selected)
    
                        self.graph_surface_label.set_picture(surface)
                        self.renderer.update()


    def notify(self,event):
        if event.signal == 5:
            
            try: self.graph_frame
            except: pass
            else:
                self.react_to_click(event.data.pos)
        if event.signal in ["change_base_window_type","change_firm_window_type"]:
            if event.data == "market":
                self.create_base_and_firm_market_window(self.renderer)
            else:
                self.exit()
        if event.signal in ["going_to_solar_system_mode_event","going_to_planetary_mode_event","going_to_company_window_event","going_to_firm_window_event","going_to_techtree_mode_event"]:
            self.exit()



class base_build_menu(BaseObject):
    """
    Subview of the base view. Shows all options regarding building firms and other bases from the current base.
    
    The first list is derived from the list of currently known technologies + options to build research, merchants and new bases.
    
    The actions from choosing a commodity producer from the known technologies is to create that firm in the current city. Likewise, more
    or less, for research firms. Choosing merchant brings up question boxes about where the destination and what resource should be traded.
    Choosing new base building brings zooms out to base position mode.
    
    
    """

    def __init__(self,solar_system_object,renderer,commandbox):
        BaseObject.__init__(self)
        self._signals["going_to_planetary_mode_event"] = []
        self._signals["going_to_solar_system_mode_event"] = []
        self._signals["going_to_base_mode_event"] = []
        self._signals["going_to_company_window_event"] = []
        self._signals["going_to_firm_window_event"] = []
        self._signals["change_base_window_type"] = []
        self._signals["going_to_techtree_mode_event"] = []

        self.renderer = renderer
        self.solar_system_object_link = solar_system_object
        self.topleft = (250,100)
        self.list_size = (600,400)
        self.frame_size = 40
        
#        self.size_requested = 1 #variable for the selection of commodity firm size - reset at each new round

    def create_base_build_menu_window(self):
        """
        The creation function. Doesn't return anything, but saves self.window variable and renderes using the self.renderer. 
        """

        try: self.window
        except:
            buildoption_data = {}
            for technology_name in self.solar_system_object_link.current_player.known_technologies:
                if technology_name != "common knowledge":
                    technology = self.solar_system_object_link.current_player.known_technologies[technology_name]
                
                    buildoption_data[technology_name] = {}
                    
                    
                    #nicefying input output
                    nice_input_output_line = ""
                    for put in ["input","output"]:
                        if put == "output":
                            nice_input_output_line = nice_input_output_line + "-> "
                        for resource in technology["input_output_dict"][put].keys():
                            value = technology["input_output_dict"][put][resource]
                            nice_input_output_line = nice_input_output_line + resource + ": " + str(value) + " "
                            
                    buildoption_data[technology_name]["input and output"] = str(nice_input_output_line)
                    
        

            buildoption_data["research"] = {}
            buildoption_data["research"]["input and output"] = "labor: 1 -> research points"

            buildoption_data["merchant"] = {}
            buildoption_data["merchant"]["input and output"] = "transport: 1 -> movement of goods"

            buildoption_data["new base"] = {}
            buildoption_data["new base"]["input and output"] = "population: 100 steel: 100 labor: 100 -> new base"
            
            self.window = gui_extras.fast_list(self.renderer)
            self.window.receive_data(buildoption_data)
            
            
            self.window.topleft = self.topleft
            self.window.list_size = self.list_size
            self.window.create_fast_list()
            self.window.render_title()
            
            self.select_this_button = Button("Select")
            self.select_this_button.connect_signal(Constants.SIG_CLICKED,self.select_button_callback)
            self.select_this_button_frame = VFrame()
            self.select_this_button_frame.topleft = (self.window.topleft[0]+(self.list_size[0]/2)-self.select_this_button.size[0]/2,self.window.topleft[1] + self.list_size[1]+50)
            self.select_this_button_frame.add_child(self.select_this_button)
            self.renderer.add_widget(self.select_this_button_frame)
        else: print "DEBUGGING: warning a create_base_list_of_companies_window call was made when self.windows already existed"



    def select_button_callback(self):
        """
        distributes the select button click to either a size selection, base destination or merchant destination prompt
        """
        try: self.window.selected_name
        except: print "DEBUGGING: select something first"
        else:
            #resetting variables, to avoid using old data
            try:    self.size_requested #variable for the selection of commodity firm size - reset at each new round
            except: pass
            else:   del self.size_requested
            
            #Being over-cautious with the naming asking box. In case it should somehow linger around, it should be removed now
            try:    self.entry_box 
            except: pass
            else:   
                try:    self.entry_box._manager
                except: pass
                else:   
                    self.entry_box.destroy()
                    print "DEBUGGING: self.entry_box was lingering around, but was caught and destroyed in the try loop"
                del self.entry_box

            if self.window.selected_name == "merchant":
                self.merchant_pick_destination()
            elif self.window.selected_name == "new base":
                self.new_base_pick_location()
            else:
                self.commodity_size_selection()




    def new_base_pick_location(self):
        """
        Function that initiates the process that allows the player to pick location of a new base
        """
#            #clear up everything to make space
#            self.exit()
        
        self.manager.emit("center_on",self.solar_system_object_link.current_planet.name)

        self.base_build_frame = VFrame()
        base_build_label = Label("Choose position of new base")
        self.base_build_frame.set_children([base_build_label])
        self.base_build_frame.topleft = (global_variables.window_size[0]/2 - self.base_build_frame.size[0]/2, 100) 
        self.renderer.add_widget(self.base_build_frame)
        
        self.solar_system_object_link.build_base_mode = True
        





    def new_base_ask_for_name(self,sphere_coordinates,give_length_warning = False):
        """
        Function that prompts the user for a name of the new base
        
        Optional argument give_length_warning includes a label that specifies max " + str(global_variables.max_letters_in_company_names) + " characters
        """
#        self.position_requested = sphere_coordinates #saving position in case we need to retype the name
#        self.manager.emit("center_on",self.solar_system_object_link.current_planet.current_base)
        try:    self.base_build_frame
        except: pass
        else:
            self.base_build_frame.destroy()
            del self.base_build_frame

        
        self.manager.emit("going_to_base_mode_event",self.solar_system_object_link.current_planet.current_base)
#        self.exit()
        self.basewindow_selected = "base_build_menu"
        self.exit()
#        time.sleep(2)
        
        
        self.dialog = VFrame(Label("Choose name for base"))
        self.dialog.set_minimum_size(400,150)
        self.dialog.topleft = (300, 250)
        
        top_label = Label("Base built on " + self.solar_system_object_link.current_planet.name + " at coordinates " + str(  ( int(sphere_coordinates[0]),int(sphere_coordinates[1]) )  ) )
    
        self.entry_box = Entry("")
        self.entry_box.minsize = (300,24)

        ok_button = Button("#Ok")
        ok_button.connect_signal(SIG_CLICKED,self.new_base_build,sphere_coordinates)
        cancel_button = Button("#Cancel")
        cancel_button.connect_signal(SIG_CLICKED,self.dialog.destroy)
        
        if give_length_warning:
            warning_label = Label("Name must be unique and between 1 and " + str(global_variables.max_letters_in_company_names) + " characters")
        
        frame2 = HFrame()
        frame2.set_children([ok_button,cancel_button])
        
        if give_length_warning:
            self.dialog.set_children([top_label,self.entry_box,frame2,warning_label])
        else:
            self.dialog.set_children([top_label,self.entry_box,frame2])
        
        self.renderer.add_widget(self.dialog)


    def new_base_build(self,sphere_coordinates):
        name = self.entry_box.text
        
        #test if name is unique
        unique = True
        for planet_instance in self.solar_system_object_link.planets.values():
            if name in planet_instance.bases.keys():
                unique = False
        
        if 0 < len(name) <= global_variables.max_letters_in_company_names and unique:
            
#            (self,base_name,home_planet,base_data,owner,manager)
            home_planet = self.solar_system_object_link.current_planet
            building_base = self.solar_system_object_link.current_planet.current_base
            base_data = {
                         "northern_loc":sphere_coordinates[1],
                         "eastern_loc":sphere_coordinates[0],
                         "population":100,
                         "country":self.solar_system_object_link.current_player.name,
                         "GDP_per_capita_in_dollars":building_base.gdp_per_capita_in_dollars
                         }
            owner = self.solar_system_object_link.current_player
            
            new_base = company.base(self.solar_system_object_link,name,home_planet,base_data,owner)
            owner.home_cities[name] = new_base
            
            #making the trade route from the founding base
            distance = home_planet.calculate_distance(sphere_coordinates, building_base.position_coordinate)
            transport_type = "ground transport"
            endpoints = [new_base.base_name,building_base.base_name] #try to remove this if you get the opportunity FIXME
            endpoint_links = [new_base,building_base]
            trade_route = {"distance":distance[0],"transport_type":transport_type,"endpoints":endpoints,"endpoint_links":endpoint_links} #converting distance from list to float (has to be list see planet
            new_base.trade_routes[building_base.base_name] = trade_route
            building_base.trade_routes[new_base.base_name] = trade_route
            
            home_planet.bases[name] = new_base
            
            owner.owned_firms[name] = new_base


            print_dict = {"text":"Building a base named " + str(name) + " at " + str(sphere_coordinates),"type":"general gameplay info"}
            self.solar_system_object_link.messages.append(print_dict)

            #clear up everything to make space
            self.exit()
            
        else:
            print_dict = {"text":"the selected name " + str(name) + " was too long. Has to be less than " + str(global_variables.max_letters_in_company_names) + " characters","type":"general gameplay info"}
            self.solar_system_object_link.messages.append(print_dict)

            self.exit()
            self.new_base_ask_for_name(sphere_coordinates,give_length_warning=True)

  
    def merchant_pick_destination(self):
        """
        Function to ask what destination the merchant should trade with
        """
        #clear up everything to make space
        self.exit()
        
            
        destination_data = {}
        location = self.solar_system_object_link.current_planet.current_base
        for destination_name in location.trade_routes:
            destination = location.trade_routes[destination_name]
            
            destination_data[destination_name] = {}
            destination_data[destination_name]["distance"] = destination["distance"]
            destination_data[destination_name]["type"] = destination["transport_type"]
            
        self.window = gui_extras.fast_list(self.renderer)
        self.window.receive_data(destination_data)
        
        
        self.window.topleft = self.topleft
        self.window.list_size = self.list_size
        self.window.create_fast_list()
        self.window.render_title()
        
        self.select_this_button = Button("Select")
        self.select_this_button.connect_signal(Constants.SIG_CLICKED,self.merchant_pick_resource)
        self.select_this_button_frame = VFrame()
        self.select_this_button_frame.topleft = (self.window.topleft[0]+(self.list_size[0]/2)-self.select_this_button.size[0]/2,self.window.topleft[1] + self.list_size[1]+50)
        self.select_this_button_frame.add_child(self.select_this_button)
        self.renderer.add_widget(self.select_this_button_frame)
        
            
        
    def merchant_pick_resource(self):
        """
        Function to ask what resource the merchant should trade in
        """
        try: self.window.selected_name
        except: 
            print_dict = {"text":"Select something first","type":"general gameplay info"}
            self.solar_system_object_link.messages.append(print_dict)
        else:
            from_location = self.solar_system_object_link.current_planet.current_base
            trade_route_selected_name = self.window.selected_name
            trade_route_selected = from_location.trade_routes[trade_route_selected_name]
            
            #clear up everything to make space
            del self.window.selected_name
            self.exit()
        
            #prepare direct links to the other endpoint location
            for endpoint in trade_route_selected["endpoint_links"]:
                if endpoint != from_location:
                    to_location = endpoint
            
            #prepare resource data
            resource_data = {}
            for resource in self.solar_system_object_link.trade_resources.keys():
                if self.solar_system_object_link.trade_resources[resource]["transportable"]:
                    resource_data[resource] = {}
                    
                    quantity_offered_here = 0
                    prices = []
                    for sell_offer in from_location.market["sell_offers"][resource]:
                        quantity_offered_here = quantity_offered_here + sell_offer["quantity"]
                        prices.append(sell_offer["price"])
                    if len(prices) == 0:
                        cheapest_sell_price = None
                    else:
                        cheapest_sell_price = min(prices)
                        
                    if len(to_location.market["buy_offers"][resource]) > 0:
                        best_buy_price = to_location.market["buy_offers"][resource][0]["price"]
                    else:
                        best_buy_price = None
                    
                    resource_data[resource]["Qt on market here"] = quantity_offered_here
                    resource_data[resource]["Best sell price"] = cheapest_sell_price
                    resource_data[resource]["Best buy price"] = best_buy_price
                
                
            self.window = gui_extras.fast_list(self.renderer)
            self.window.receive_data(resource_data)
            
            
            self.window.topleft = self.topleft
            self.window.list_size = self.list_size
            self.window.create_fast_list()
            self.window.render_title()
            
            self.select_this_button = Button("Select")
            self.select_this_button.connect_signal(Constants.SIG_CLICKED,self.merchant_pick_name,to_location,trade_route_selected)
            self.select_this_button_frame = VFrame()
            self.select_this_button_frame.topleft = (self.window.topleft[0]+(self.list_size[0]/2)-self.select_this_button.size[0]/2,self.window.topleft[1] + self.list_size[1]+50)
            self.select_this_button_frame.add_child(self.select_this_button)
            self.renderer.add_widget(self.select_this_button_frame)



    def merchant_pick_name(self,to_location,trade_route_selected,give_length_warning=False):
        """
        Function to get the name of the merchant
        to_location                 The destination location as a base object
        trade_route_selected        The trade route as given by the from_location (ie. current base selected)
        Optionally:
        give_length_warning         If true, this will specify the max text size as part of the title.
        """
        try: self.window.selected_name
        except: 
            print_dict = {"text":"the selected name " + str(name) + " was too long. Has to be less than " + str(global_variables.max_letters_in_company_names) + " characters","type":"general gameplay info"}
            self.solar_system_object_link.messages.append(print_dict)

        else:
            resource = self.window.selected_name
            from_location = self.solar_system_object_link.current_planet.current_base

            #check that this does not already exist
            from_location = self.solar_system_object_link.current_planet.current_base
            exists = False
            for firm_instance in self.solar_system_object_link.current_player.owned_firms.values():
                if isinstance(firm_instance, company.merchant):
                    if firm_instance.from_location == from_location:
                        if firm_instance.to_location == to_location:
                            if firm_instance.resource == resource:
                                exists = True
            if exists:
                print_dict = {"text":"A merchant from " + str(from_location.name) + " to " + str(to_location.name) + " trading " + str(resource) + " does already exist","type":"general gameplay info"}
                self.solar_system_object_link.messages.append(print_dict)

                
            else:
                #clear up everything to make space
                del self.window.selected_name
                self.exit()

                self.dialog = VFrame(Label("Choose name for merchant"))
                self.dialog.set_minimum_size(400,150)
                self.dialog.topleft = (300, 250)
                
                top_label = Label(resource + " from " + from_location.name + " to " + to_location.name)
            
                self.entry_box = Entry("")
                self.entry_box.minsize = (300,24)

                ok_button = Button("#Ok")
                ok_button.connect_signal(SIG_CLICKED,self.merchant_build,to_location,trade_route_selected,resource)
                cancel_button = Button("#Cancel")
                cancel_button.connect_signal(SIG_CLICKED,self.dialog.destroy)
                
                if give_length_warning:
                    warning_label = Label("Name must be unique and between 1 and " + str(global_variables.max_letters_in_company_names) + " characters")
                
                frame2 = HFrame()
                frame2.set_children([ok_button,cancel_button])
                
                if give_length_warning:
                    self.dialog.set_children([top_label,self.entry_box,frame2,warning_label])
                else:
                    self.dialog.set_children([top_label,self.entry_box,frame2])
                
                self.renderer.add_widget(self.dialog)

        
        
        
        
    def merchant_build(self,to_location,trade_route_selected,resource):
        """
        Function to build the merchant
        """ 
        name = self.entry_box.text

        #test if name is unique
        unique = True
        for company_instance in self.solar_system_object_link.companies.values():
            if name in company_instance.owned_firms.keys():
                unique = False
        
        if 0 < len(name) <= global_variables.max_letters_in_company_names and unique:
        
            from_location = self.solar_system_object_link.current_planet.current_base
            owner = self.solar_system_object_link.current_player
            input_output_dict = {"input":{},"output":{},"timeframe":30,"byproducts":{}}
            distance = trade_route_selected["distance"]
            transport_type = trade_route_selected["transport_type"]
            new_merchant_firm = company.merchant(self.solar_system_object_link,from_location,to_location,input_output_dict,owner,name,transport_type,distance,resource)
            owner.owned_firms[name] = new_merchant_firm
            print_dict = {"text":"Built a merchant named " + str(name) + " between " + str(from_location.name) + " and " + str(to_location.name) + " trading in " + str(resource),"type":"general gameplay info"}
            self.solar_system_object_link.messages.append(print_dict)

            #clear up everything to make space
            self.exit()
            
        else:
            
            print_dict = {"text":"the selected name " + str(name) + " was too long. Has to be less than " + str(global_variables.max_letters_in_company_names) + " characters","type":"general gameplay info"}
            self.solar_system_object_link.messages.append(print_dict)

            
            self.window = gui_extras.fast_list(self.renderer) # has to make this temporarily to store selected name (it will be killed in the function call in two lines)
            self.window.selected_name = resource #has to put it back here, because of the way the merchant_pick_name works
            self.merchant_pick_name(to_location,trade_route_selected,give_length_warning=True)


    
    def commodity_size_selection(self):
        """
        This function creates a dialog asking the size of the firm to be built (unless it is a merchant, in which case it redirects to the select merchant destination box)
        The range of the size is from "1" where the it is just the input_output_dict
        to the integer at which the sum of the inputs are equal to 10% the population of the city (FIXME this rule is not implemented for AI - also note that it is more like 101% of the sum at present)
         
        """
        try: self.window.selected_name
        except: 
            print_dict = {"text":"Select something first","type":"general gameplay info"}
            self.solar_system_object_link.messages.append(print_dict)

        else:
            if self.window.selected_name in ["new base","merchant"]:
                raise Exception("This should have been distributed correctly already at the select_button_callback step")
            elif self.window.selected_name == "research":
                technology = {}
                technology["input_output_dict"] = {}
                technology["input_output_dict"]["input"] = {"labor":1}
                technology["input_output_dict"]["output"] = {"research:":1}
                technology["technology_name"] = "research"
            else:
                technology = self.solar_system_object_link.current_player.known_technologies[self.window.selected_name]
            input_size = 0
            
            
            #calculate the range allowed
            for input in technology["input_output_dict"]["input"].values():
                input_size = input_size + input
            if input_size < 2: 
                input_size = 2
            if self.solar_system_object_link.current_planet.current_base is None:
                raise Exception("very weird - there was no base selected")
            population = self.solar_system_object_link.current_planet.current_base.population
            max_size = int(population * 0.1 / float(input_size))
            
            
            #check if the current_player already owns a company of that technology in the current base
            existing_firm = None
            for firm_instance in self.solar_system_object_link.current_player.owned_firms.values():
                if firm_instance.location == self.solar_system_object_link.current_planet.current_base:
                    if firm_instance.technology_name == self.window.selected_name:
                        existing_firm = firm_instance
                        break
            
            
            #clean up the act
            self.exit()
            
            #create the dialog and scrollbar
            self.dialog = VFrame(Label("Choose size of firm"))
            self.dialog.align = ALIGN_LEFT
            self.size_range = (1,max_size)
            self.dialog.set_minimum_size(400,150)
            self.dialog.topleft = (300, 250)
            
            if existing_firm is None:
                top_label = Label("No existing firms of this type owned here")
                start_value = 1
            else:
                top_label = Label("An existing size " + str(existing_firm.size) + " firm of this type already owned here")
                start_value = ((existing_firm.size - self.size_range[0]) * 100 ) / self.size_range[1]
                print "calculated start value: " + str(start_value) #fixme or just change start_value to 1 for all. (the idea was that the slider should be at the current level  
            top_label.align = ALIGN_LEFT
    
            bottom_label = Label("")
            bottom_label.multiline = True
            bottom_label.align = ALIGN_LEFT
          
    
            hscrollbar = HScrollBar (300, 3300)
            hscrollbar.set_step(30)
            hscrollbar.value = start_value
            hscrollbar.connect_signal(SIG_VALCHANGED,self.commodity_update_size_selection,technology)
    
            ok_button = Button("#Ok")
            ok_button.connect_signal(SIG_CLICKED,self.commodity_ask_for_name,technology,existing_firm)
            cancel_button = Button("#Cancel")
            cancel_button.connect_signal(SIG_CLICKED,self.dialog.destroy)

            frame2 = HFrame()
            frame2.set_children([ok_button,cancel_button])
            self.dialog.set_children([top_label,hscrollbar,bottom_label,frame2])
#            self.dialog.set_child(frame1)
            self.commodity_update_size_selection(technology)
            
            self.renderer.add_widget(self.dialog)
    


    def commodity_update_size_selection(self,technology):
        """
        This function is activated on hscrollbar value change on the size selection box, and updates the input_output_dict
        """
        hscrollbar = self.dialog.children[1]
        normalized_size_requested = int(hscrollbar.value / 30.0)
        size_requested = int((normalized_size_requested * self.size_range[1]) / 100.0) + self.size_range[0]
        label = self.dialog.children[2]
        
        nice_input_output_line = "size: " + str(size_requested) + "\n\n"
        for put in ["input","output"]:
            nice_input_output_line = nice_input_output_line + put + ":\n"
            for resource in technology["input_output_dict"][put].keys():
                value = technology["input_output_dict"][put][resource]
                value = value * size_requested
                nice_input_output_line = nice_input_output_line + resource + ": " + str(value) + "\n"
            nice_input_output_line = nice_input_output_line + "\n"
        label.set_text(nice_input_output_line)



        
    def commodity_ask_for_name(self,technology,existing_firm,give_length_warning=False):
        """
        This command is called after the size selection box has been accepted
        """
        try:    self.size_requested
        except: #in this case (the usual case) we have to extract it from the scrollbar value, before destroying the scrollbar 
            for child in self.dialog.children: #checking which of the children (this index might change because of top_label)
                if isinstance(child, HScrollBar):
                    hscrollbar = child
            normalized_size_requested = int(hscrollbar.value / 30.0)
            self.size_requested = int((normalized_size_requested * self.size_range[1]) / 100.0) + self.size_range[0]

        else:   # in this case it is a re-run, probably from a non-accepted name, so we just use self.size_requested as it is
            pass   
            

        self.exit() #here we destroy the scrollbar
        
        if existing_firm is None:
            self.dialog = VFrame(Label("Choose name for firm"))
            self.dialog.set_minimum_size(400,150)
            self.dialog.topleft = (300, 250)
            
            
            top_label = Label("Size " + str(self.size_requested) + " " + technology["technology_name"] + " firm built in " + self.solar_system_object_link.current_planet.current_base.name)
        
            self.entry_box = Entry("")
            self.entry_box.activate()
            self.entry_box.minsize = (300,24)
    
            ok_button = Button("#Ok")
            ok_button.connect_signal(SIG_CLICKED,self.commodity_build_firm,technology,self.size_requested)
            cancel_button = Button("#Cancel")
            cancel_button.connect_signal(SIG_CLICKED,self.dialog.destroy)
            
            if give_length_warning:
                warning_label = Label("Name must be unique and between 1 and " + str(global_variables.max_letters_in_company_names) +" characters")
            
            frame2 = HFrame()
            frame2.set_children([ok_button,cancel_button])
            
            if give_length_warning:
                self.dialog.set_children([top_label,self.entry_box,frame2,warning_label])
            else:
                self.dialog.set_children([top_label,self.entry_box,frame2])
            
            self.renderer.add_widget(self.dialog)

        else: #in cases where the firm already exists, we preserve the name
            self.commodity_build_firm(technology, self.size_requested, existing_name = existing_firm.name)
            
            print_dict = {"text":"The firm already exists. Assuming a size change is wanted.","type":"general gameplay info"}
            self.solar_system_object_link.messages.append(print_dict)

        



    def commodity_build_firm(self,technology,size,existing_name = None):
        """
        The effectuating function for building commodity firms
        """
        if existing_name is None:
            name = self.entry_box.text
            #test if name is unique
            unique = True
            for company_instance in self.solar_system_object_link.companies.values():
                if name in company_instance.owned_firms.keys():
                    unique = False
        
            if not (0 < len(name) <= global_variables.max_letters_in_company_names and unique):
                print_dict = {"text":"the selected name " + str(name) + " was too long and/or not unique. Has to be less than " + str(global_variables.max_letters_in_company_names) + " characters","type":"general gameplay info"}
                self.solar_system_object_link.messages.append(print_dict)

                self.commodity_ask_for_name(technology,None,True)
                return None
            
        else: #if existing name exists, we use that
            name = existing_name
        
        
        
        
        location = self.solar_system_object_link.current_planet.current_base
        owner = self.solar_system_object_link.current_player
        
        owner.change_firm_size(location,size,technology["technology_name"], name)
        if isinstance(name, str) or isinstance(name, unicode):
            print_dict = {"text":"Built a firm named " + str(name) + " at " + str(location.name) + " for " + str(owner.name),"type":"general gameplay info"}
            self.solar_system_object_link.messages.append(print_dict)

        else:
            print name
            print name.__class__
            raise Exception("The name used: " + str(name) + " was of class " + str(name.__class__) + " but should have been a string")
        
        #clear up everything to make space
        self.exit()
            


        
    def exit(self):
        try: self.window
        except: pass
        else: 
            self.window.exit()
            del self.window
        try:    self.select_this_button_frame
        except: pass
        else:
            self.select_this_button_frame.destroy()
            del self.select_this_button_frame
            del self.select_this_button

        try: self.dialog._manager
        except: pass 
        else:
            self.dialog.destroy()
        try:    self.dialog
        except: pass
        else:   del self.dialog
            
            
            
        
    
    def notify(self,event):
        if event.signal == "change_base_window_type":
            if event.data == "base_build_menu":
                self.create_base_build_menu_window()
            else:
                self.exit()
        if event.signal in ["going_to_solar_system_mode_event","going_to_planetary_mode_event","going_to_company_window_event","going_to_firm_window_event","going_to_techtree_mode_event"]:
            self.exit()
            self.solar_system_object_link.build_base_mode = False
            try:    self.base_build_frame
            except: pass
            else:
                self.base_build_frame.destroy()
                del self.base_build_frame
        







class left_side_company_navigation(BaseObject):
    """
    The buttons on the left side which are only seen when in company mode. They are used to navigate between the subviews available
    for each company.
    """

    def __init__(self,solar_system_object,renderer,commandbox):
        BaseObject.__init__(self)
        self._signals["going_to_planetary_mode_event"] = []
        self._signals["going_to_solar_system_mode_event"] = []
        self._signals["going_to_base_mode_event"] = []
        self._signals["going_to_company_window_event"] = []
        self._signals["going_to_firm_window_event"] = []
        self._signals["going_to_techtree_mode_event"] = []
        self.renderer = renderer
        self.solar_system_object_link = solar_system_object
        self.topleft_pos = (0,0)
        self.area_size = (global_variables.window_size[0]*0.2 , global_variables.window_size[1])
        self.button_size = (130, 50)
        self.buttonlinks = ["company_ownership_info","company_finances_info","company_list_of_firms"]
        
        self.buttonnicenames = ["Ownership info","Financial info","Owned firms"]
        self.companywindow_selected = None
        
        #self.number = 0
        
        
    def notify(self,event):
        if event.signal == "going_to_company_window_event":
            self.create_left_side_company_navigation()
            self.company_selected = event.data
            
        if event.signal in ["going_to_solar_system_mode_event","going_to_planetary_mode_event","going_to_firm_window_event","going_to_base_mode_event","going_to_techtree_mode_event"]:
            self.exit()
            
    def company_window_type_set_callback(self,button_name):
        self.companywindow_selected = button_name
        self.manager.emit("change_company_window_type",self.companywindow_selected)
        

    def exit(self):
        
        try: self.frames
        except: pass
        else:
            iteration_list = self.frames.keys()
            for frame_name in self.frames.keys():
                self.frames[frame_name].destroy()
                del self.frames[frame_name]
            del self.frames
        try: self.buttons
        except: pass
        else:
            iteration_list = self.buttons.keys()
            for button_name in iteration_list:
                del self.buttons[button_name]
             

    def create_left_side_company_navigation(self):
        """
        The creation function. Doesn't return anything, but saves self.window variable and renderes using the self.renderer. 
        """
        try: self.frames
        except:
            self.buttons = {}
            self.frames = {}
            company_buttons_group = None
            vertical_slice = self.area_size[1] / len(self.buttonlinks)
            for i in range(0,len(self.buttonlinks)):
                y_pos = int( (i + 0.5) * vertical_slice ) - (self.button_size[1] / 2)
                x_pos = (self.area_size[0] / 2 ) - (self.button_size[0] / 2)
                self.frames[self.buttonlinks[i]] = VFrame()
                self.frames[self.buttonlinks[i]].topleft = (x_pos,y_pos)
                self.buttons[self.buttonlinks[i]] = RadioButton(self.buttonnicenames[i],company_buttons_group)
                self.buttons[self.buttonlinks[i]].connect_signal(Constants.SIG_TOGGLED,self.company_window_type_set_callback,self.buttonlinks[i])
                self.buttons[self.buttonlinks[i]].minsize = self.button_size
                self.frames[self.buttonlinks[i]].add_child(self.buttons[self.buttonlinks[i]])
                self.renderer.add_widget(self.frames[self.buttonlinks[i]])
                if i == 0:
                    company_buttons_group = self.buttons[self.buttonlinks[i]]
                    self.buttons[self.buttonlinks[i]].company_buttons_group = self.buttons[self.buttonlinks[i]]
            if self.companywindow_selected is not None:
                self.buttons[self.companywindow_selected].set_active(True)
                self.manager.emit("change_company_window_type",self.companywindow_selected)
            
        else: 
            if self.solar_system_object_link.message_printing["debugging"]:
                print_dict = {"text":"DEBUGGING: warning a create_left_side_company_navigation call was made when self.frames already existed"    ,"type":"debugging"}
                self.solar_system_object_link.messages.append(print_dict)





class company_ownership_info(BaseObject):
    """
    Subview of the company view. Shows miscellanous information about a company, such as decision parameters, capital and number of firms.
    """

    def __init__(self,solar_system_object,renderer,commandbox):
        BaseObject.__init__(self)
        self._signals["going_to_planetary_mode_event"] = []
        self._signals["going_to_solar_system_mode_event"] = []
        self._signals["going_to_base_mode_event"] = []
        self._signals["going_to_company_window_event"] = []
        self._signals["going_to_firm_window_event"] = []
        self._signals["change_company_window_type"] = []
        self._signals["going_to_techtree_mode_event"] = []
        self.renderer = renderer
        self.solar_system_object_link = solar_system_object
        self.list_size = (650,450)
        self.topleft = (200, 100)

        
    def notify(self,event):
        if event.signal == "change_company_window_type":
            if event.data == "company_ownership_info":
                self.create_company_ownership_info()
            else:
                self.exit()
                #print "DEBUGGING: exiting from company_ownership_info because of in_company change"
        if event.signal in ["going_to_solar_system_mode_event","going_to_planetary_mode_event","going_to_base_mode_event","going_to_firm_window_event","going_to_techtree_mode_event"]:
            self.exit()



    def exit(self):
        #print "DEBUGGING: Running exit signal for company_ownership_info"
        try: self.window
        except:
            pass
        else:
            #print "DEBUGGING: Running kill signal for company_ownership_info"
            self.window.exit()
            del self.window
            


    def create_company_ownership_info(self):
        """
        The creation function. Doesn't return anything, but saves self.window variable and renderes using the self.renderer. 
        """
        try: self.window
        except:
            company_selected = self.solar_system_object_link.company_selected
            if company_selected is not None:
                company_ownership_dict = {}
                
                for company_database_variable in company_selected.company_database:
                    company_database_variable_name_here = company_database_variable
                    if len(company_database_variable_name_here) > global_variables.max_letters_in_company_names:
                        company_database_variable_name_here = company_database_variable_name_here[0:global_variables.max_letters_in_company_names]
                    company_ownership_dict["parameter: " + company_database_variable_name_here] = {"info":str(company_selected.company_database[company_database_variable])} 
                
                company_ownership_dict["capital"] = {"info":company_selected.capital}
               
                company_ownership_dict["home cities, number of"] = {"info":str(len(company_selected.home_cities))}
                if 0 < len(company_selected.home_cities) < 4:
                    list_value = str(company_selected.home_cities.keys())
                    list_value = list_value.rstrip("]")
                    list_value = list_value.lstrip("[")
                    company_ownership_dict["home cities"] = {"info":list_value}
    
                company_ownership_dict["last_firm_evaluation"] = {"info":str(company_selected.last_firm_evaluation)}
                company_ownership_dict["last_market_evaluation"] = {"info":str(company_selected.last_market_evaluation)}
                company_ownership_dict["last_demand_evaluation"] = {"info":str(company_selected.last_demand_evaluation)}
                company_ownership_dict["last_supply_evaluation"] = {"info":str(company_selected.last_supply_evaluation)}

                company_ownership_dict["research"] = {"info":str(company_selected.research)}    
                
                company_ownership_dict["firms owned, number of"] = {"info":str(len(company_selected.owned_firms))}

                self.window = gui_extras.fast_list(self.renderer)
                self.window.receive_data(company_ownership_dict,column_order = ["rownames","info"],sort_by="rownames")
                self.window.topleft = self.topleft
                self.window.list_size = self.list_size
                self.window.create_fast_list()
                self.window.render_title()
    #        
            else:
                
                if self.solar_system_object_link.message_printing["debugging"]:
                    print_dict = {"text":"DEBUGGING: Company selected was None","type":"debugging"}
                    self.solar_system_object_link.messages.append(print_dict)

        else:
            if self.solar_system_object_link.message_printing["debugging"]:
                print_dict = {"text":"DEBUGGING: tried to paint a company_ownership_info, but this already existed","type":"debugging"}
                self.solar_system_object_link.messages.append(print_dict)







class company_financial_info(BaseObject):
    """
    Subview of the company view. Shows a graph of the capital of the company as it has been over the past years. 
    """

    def __init__(self,solar_system_object,renderer,commandbox):
        BaseObject.__init__(self)
        self._signals["going_to_planetary_mode_event"] = []
        self._signals["going_to_solar_system_mode_event"] = []
        self._signals["going_to_base_mode_event"] = []
        self._signals["going_to_company_window_event"] = []
        self._signals["going_to_firm_window_event"] = []
        self._signals["change_company_window_type"] = []
        self._signals["going_to_techtree_mode_event"] = []
        self.renderer = renderer
        self.solar_system_object_link = solar_system_object
        self.graph_size = (400,400)
        self.frame_size = 40
        self.topleft_everything = (300, 50)

        
    def notify(self,event):
        if event.signal == "change_company_window_type":
            if event.data == "company_finances_info":
                self.create_company_financial_info()
            else:
                self.exit()
        if event.signal in ["going_to_solar_system_mode_event","going_to_planetary_mode_event","going_to_base_mode_event","going_to_firm_window_event","going_to_techtree_mode_event"]:
            self.exit()


    def exit(self):
        try: self.graph_frame
        except:
            pass#"DEBUGGING: did not find 3"
        else:
            self.graph_frame.destroy()
            del self.graph_frame
            del self.graph_surface_label


    def create_company_financial_info(self):
        """
        The creation function. Doesn't return anything, but saves self.window variable and renderes using the self.renderer. 
        """
        
        company_selected = self.solar_system_object_link.company_selected
        company_accounting = company_selected.company_accounting
        history_surface = pygame.Surface(self.graph_size)
        history_surface.fill((234,228,223))
        if len(company_selected.company_accounting) == 0:
            no_history_label = global_variables.standard_font.render("No history for " + company_selected.name,True,(0,0,0))
            history_surface.blit(no_history_label,(0,self.graph_size[1]*0.5-4))
        else:
            start_date = company_accounting[0]["date"]
            end_date = company_accounting[len(company_accounting)-1]["date"]
            relative_numeric_start_date = (start_date - self.solar_system_object_link.start_date).days
            relative_numeric_end_date = (end_date - self.solar_system_object_link.start_date).days
            xlim = (relative_numeric_start_date,relative_numeric_end_date)
            dates = []
            capital = []
            for account_report in company_accounting:
                dates.append((account_report["date"] - self.solar_system_object_link.start_date).days)
                capital.append(account_report["capital"])
            ylim = (0,max(capital))
            if ylim[0] == ylim[1]:
                ylim = (ylim[0]-1,ylim[1]+1)
            if xlim[0] == xlim[1]:
                xlim = (xlim[0]-1,xlim[1]+1)
            
            history_surface = primitives.make_linear_y_axis(history_surface, self.frame_size, ylim, solar_system_object_link, unit = "capital")
            history_surface = primitives.make_linear_x_axis(history_surface,self.frame_size,xlim,solar_system_object_link = self.solar_system_object_link, unit="date")
            
            for i in range(1,len(capital)):
                x1_position = int(self.frame_size + ((self.graph_size[0]-self.frame_size*2) * (dates[i-1] - xlim[0])) / (xlim[1]-xlim[0]))
                y1_position = int(self.graph_size[1] - (self.frame_size + ( (self.graph_size[1]-self.frame_size*2) * (capital[i-1] - ylim[0]) / (ylim[1]-ylim[0]) )))
                x2_position = int(self.frame_size + ((self.graph_size[0]-self.frame_size*2) * (dates[i] - xlim[0])) / (xlim[1]-xlim[0]))
                y2_position = int(self.graph_size[1] - (self.frame_size + ( (self.graph_size[1]-self.frame_size*2) * (capital[i] - ylim[0]) / (ylim[1]-ylim[0]) )))
                pygame.draw.line(history_surface,(0,0,0),(x1_position,y1_position),(x2_position,y2_position))
        try: self.graph_surface_label
        except: 
            self.graph_surface_label = ImageLabel(history_surface)
            self.graph_frame = VFrame(Label("Capital history"))
            self.graph_frame.topleft = (self.topleft_everything[0] + 150,self.topleft_everything[1])
            self.graph_frame.add_child(self.graph_surface_label)
            self.renderer.add_widget(self.graph_frame)
        else:
            self.graph_surface_label.set_picture(history_surface)
            self.renderer.update()





class company_list_of_firms(BaseObject):
    """
    Subview of the company view. Shows a list of all firms owned by the company. A shortcut button allows quick zoom to the firm page of these firms.
    """

    def __init__(self,solar_system_object,renderer,commandbox):
        BaseObject.__init__(self)
        self._signals["going_to_planetary_mode_event"] = []
        self._signals["going_to_solar_system_mode_event"] = []
        self._signals["going_to_base_mode_event"] = []
        self._signals["going_to_company_window_event"] = []
        self._signals["going_to_firm_window_event"] = []
        self._signals["change_base_window_type"] = []
        self._signals["change_company_window_type"] = []
        self._signals["going_to_techtree_mode_event"] = []
        #self._signals["focus_on_company"] = []
        self.renderer = renderer
        self.solar_system_object_link = solar_system_object
        self.list_size = (650,400)
        self.topleft = (200,100)
        self.frame_size = 40

    def go_to_firm_window_event_callback(self):
        
        firm_selected = None
        for firm in self.solar_system_object_link.company_selected.owned_firms.values():
            if firm.name == self.window.selected_name:
                firm_selected = firm
        if firm_selected is None:
            if self.solar_system_object_link.message_printing["debugging"]:
                print_dict = {"text":"POSSIBLE DEBUGGING: - the firm asked for was of None type","type":"debugging"}
                self.solar_system_object_link.messages.append(print_dict)

        else:
            if isinstance(firm,company.base):
                self.manager.emit("going_to_base_mode_event",firm_selected)
                #print "DEBUGGING: emitted going to base_mode_event with " + str(firm_selected) + " of name " + str(firm_selected.name)
            else:
                self.manager.emit("going_to_firm_window_event",firm_selected)
                #print "DEBUGGING: emitted going to firm_window_event with " + str(firm_selected) + " of name " + str(firm_selected.name)
        


    def create_company_list_of_firms_window(self):
        """
        The creation function. Doesn't return anything, but saves self.window variable and renderes using the self.renderer. 
        """
        company_selected = self.solar_system_object_link.company_selected
        if company_selected is None:
            raise Exception("A list of firms was requested, but no company was selected")
        
        firm_data = {}
        for firm_instance in company_selected.owned_firms.values():
            firm_data[firm_instance.name] = {}
            try: firm_instance.last_profit
            except: 
                firm_data[firm_instance.name]["last profit"] = "NA"
            else: 
                firm_data[firm_instance.name]["last profit"] = firm_instance.last_profit
            
            firm_data[firm_instance.name]["location"] = firm_instance.location.name
            
            stock_amount = 0
            for stock_item in firm_instance.stock_dict.values():
                stock_amount = stock_amount + stock_item
            firm_data[firm_instance.name]["stock size"] = stock_amount
        self.window = gui_extras.fast_list(self.renderer)
        self.window.topleft = self.topleft
        self.window.list_size = self.list_size
        
        self.window.receive_data(firm_data) 
        
        self.window.create_fast_list()
        self.window.render_title()
        self.go_to_firm_window_button = Button("Firm page")
        self.go_to_firm_window_button.connect_signal(Constants.SIG_CLICKED,self.go_to_firm_window_event_callback)
        self.go_to_firm_window_button_frame = VFrame()
        self.go_to_firm_window_button_frame.topleft = (self.window.topleft[0]+(self.list_size[0]/2)-self.go_to_firm_window_button.size[0]/2,self.window.topleft[1] + self.list_size[1]+50)
        self.go_to_firm_window_button_frame.add_child(self.go_to_firm_window_button)
        self.renderer.add_widget(self.go_to_firm_window_button_frame)




        
    def exit(self):
        try: self.window 
        except:
            pass
        else:
            self.window.exit()
            del self.window
        try: self.go_to_firm_window_button_frame
        except: pass#print "DEBUGGING: Did not find self.go_to_company_window_button" 
        else:
            self.go_to_firm_window_button_frame.destroy()
            del self.go_to_firm_window_button_frame
            del self.go_to_firm_window_button

        
        
    def notify(self,event):
        if event.signal == "change_company_window_type":
            if event.data == "company_list_of_firms":
                try: self.window
                except:
                    self.create_company_list_of_firms_window()
            else:
                self.exit()
        #print "company_list_of_firms heard a " + str(event.signal) + " signal with data " + str(event.data)
        if event.signal in ["going_to_solar_system_mode_event","going_to_planetary_mode_event","going_to_base_mode_event","going_to_firm_window_event","going_to_techtree_mode_event"]:
            #print "DEBUGGING: in company_list_of_firms, the window should now close because it heard a competing mode_event"
            self.exit()
        
        
        
    






class left_side_firm_navigation(BaseObject):
    """
    The buttons on the left side which are only seen when in firm mode. They are used to navigate between the subviews available
    for each firm.
    """

    def __init__(self,solar_system_object,renderer,commandbox):
        BaseObject.__init__(self)
        self._signals["going_to_planetary_mode_event"] = []
        self._signals["going_to_solar_system_mode_event"] = []
        self._signals["going_to_base_mode_event"] = []
        self._signals["going_to_company_window_event"] = []
        self._signals["going_to_firm_window_event"] = []
        self._signals["going_to_techtree_mode_event"] = []
        self.renderer = renderer
        self.solar_system_object_link = solar_system_object
        self.topleft_pos = (0,0)
        self.area_size = (global_variables.window_size[0]*0.2 , global_variables.window_size[1])
        self.button_size = (130, 50)
        self.buttonlinks = ["firm_process_info","market","firm_trade_partners_info"]
        self.buttonnicenames = ["Production","Market","Trade partners"]
        self.firmwindow_selected = None
        
        
    def notify(self,event):
        if event.signal == "going_to_firm_window_event":
            self.solar_system_object_link.firm_selected = event.data
            self.create_left_side_firm_navigation()
        if event.signal in ["going_to_solar_system_mode_event","going_to_planetary_mode_event","going_to_company_window_event","going_to_base_mode_event","going_to_techtree_mode_event"]:
            self.exit()
            
    def firm_window_type_set_callback(self,button_name):
        self.firmwindow_selected = button_name
        self.manager.emit("change_firm_window_type",self.firmwindow_selected)

    def exit(self):
        try: self.frames
        except: pass
        else:
            iteration_list = self.frames.keys()
            for frame_name in self.frames.keys():
                self.frames[frame_name].destroy()
                del self.frames[frame_name]
            del self.frames
        try: self.buttons
        except: pass
        else:
            iteration_list = self.buttons.keys()
            for button_name in iteration_list:
                del self.buttons[button_name]
             

    def create_left_side_firm_navigation(self):
        try: self.frames
        except:
            self.buttons = {}
            self.frames = {}
            firm_buttons_group = None
            vertical_slice = self.area_size[1] / len(self.buttonlinks)
            for i in range(0,len(self.buttonlinks)):
                y_pos = int( (i + 0.5) * vertical_slice ) - (self.button_size[1] / 2)
                x_pos = (self.area_size[0] / 2 ) - (self.button_size[0] / 2)
                self.frames[self.buttonlinks[i]] = VFrame()
                self.frames[self.buttonlinks[i]].topleft = (x_pos,y_pos)
                self.buttons[self.buttonlinks[i]] = RadioButton(self.buttonnicenames[i],firm_buttons_group)
                self.buttons[self.buttonlinks[i]].connect_signal(Constants.SIG_TOGGLED,self.firm_window_type_set_callback,self.buttonlinks[i])
                self.buttons[self.buttonlinks[i]].minsize = self.button_size
                self.frames[self.buttonlinks[i]].add_child(self.buttons[self.buttonlinks[i]])
                self.renderer.add_widget(self.frames[self.buttonlinks[i]])
                if i == 0:
                    firm_buttons_group = self.buttons[self.buttonlinks[i]]
                    self.buttons[self.buttonlinks[i]].firm_buttons_group = self.buttons[self.buttonlinks[i]]
            if self.firmwindow_selected is not None:
                self.buttons[self.firmwindow_selected].set_active(True)
                self.manager.emit("change_firm_window_type",self.firmwindow_selected)
            #print "DEBGGING: emitted: " + str(self.firmwindow_selected)
        else: 
            if self.solar_system_object_link.message_printing["debugging"]:
                print_dict = {"text":"DEBUGGING: warning a create_left_side_firm_navigation call was made when self.frames already existed","type":"debugging"}
                self.solar_system_object_link.messages.append(print_dict)

            







class firm_trade_partners_info(BaseObject):
    """
    Subview of the firm view. Shows a list of past trading transactions for the firm.
    """
    def __init__(self,solar_system_object,renderer,commandbox):
        BaseObject.__init__(self)
        self._signals["going_to_planetary_mode_event"] = []
        self._signals["going_to_solar_system_mode_event"] = []
        self._signals["going_to_base_mode_event"] = []
        self._signals["going_to_company_window_event"] = []
        self._signals["going_to_firm_window_event"] = []
        self._signals["change_firm_window_type"] = []
        self._signals["going_to_techtree_mode_event"] = []
        self.renderer = renderer
        self.solar_system_object_link = solar_system_object
        self.list_size = (650,250)
        self.topleft = (200, 100)
        
        
    def notify(self,event):
        if event.signal == "change_firm_window_type":
            if event.data == "firm_trade_partners_info":
                self.create_firm_transactions_info()
                #print "DEBUGGING: Heard show firm_trade_partners_info"
            else:
                self.exit()
        if event.signal in ["going_to_solar_system_mode_event","going_to_planetary_mode_event","going_to_company_window_event","going_to_base_mode_event","going_to_techtree_mode_event"]:
            self.exit()
            


    def exit(self):
        try: self.window_transactions
        except: pass
        else: 
            self.window_transactions.exit()
            del self.window_transactions

            

        


    def create_firm_transactions_info(self):
        """
        The creation function. Doesn't return anything, but saves self.window_transactions variable and renders using the self.renderer. 
        """
        
        firm_selected = self.solar_system_object_link.firm_selected
        if isinstance(firm_selected,company.merchant):
            location_list = [firm_selected.from_location, firm_selected.to_location]
            
        else:
            location_list = [firm_selected.location]

        
        transactions = {}
        for k, location_instance in enumerate(location_list):
            market = location_instance.market
            for i, resource in enumerate(market["transactions"]):
                for j, transaction in enumerate(market["transactions"][resource]):
                    date = transaction["date"]
                    if transaction["buyer"] is not None:
                        buyer = transaction["buyer"].name
                    else:
                        buyer = None
                    if transaction["seller"] is not None:
                        seller = transaction["seller"].name
                    else:
                        seller = None
                    price = transaction["price"]
                    #print "The price is of class " + str(price.__class__)
                    quantity = transaction["quantity"]
                    if firm_selected.name in [buyer,seller]:
                        transactions[i*j*k] =  {"date":date,"buyer":buyer,"seller":seller,"price":price,"quantity":quantity}


                
        self.window_transactions = gui_extras.fast_list(self.renderer)
        self.window_transactions.receive_data(transactions,column_order = ["date","buyer","seller","price","quantity"],sort_by="date")
        self.window_transactions.topleft = self.topleft
        self.window_transactions.list_size = self.list_size
        self.window_transactions.create_fast_list()
        self.window_transactions.render_title()

                

        
        

class firm_process_info(BaseObject):
    """
    Subview of the firm view. Shows a list of the resources of interest for the firm. Both the stock and the production rate is shown.
    """

    def __init__(self,solar_system_object,renderer,commandbox):
        BaseObject.__init__(self)
        self._signals["going_to_planetary_mode_event"] = []
        self._signals["going_to_solar_system_mode_event"] = []
        self._signals["going_to_base_mode_event"] = []
        self._signals["going_to_company_window_event"] = []
        self._signals["going_to_firm_window_event"] = []
        self._signals["change_firm_window_type"] = []
        self._signals["going_to_techtree_mode_event"] = []
        self.renderer = renderer
        self.solar_system_object_link = solar_system_object
        self.list_size = (650,150)
        self.topleft = (200, 100)

        
    def notify(self,event):
        if event.signal == "change_firm_window_type":
            if event.data == "firm_process_info":
                self.create_firm_process_info()
            else:
                self.exit()
        if event.signal in ["going_to_solar_system_mode_event","going_to_planetary_mode_event","going_to_company_window_event","going_to_base_mode_event","going_to_techtree_mode_event"]:
            self.exit()
            


    def exit(self):
        try: self.window
        except:
            pass
        else:
            self.window.exit()
            del self.window
            


    def create_firm_process_info(self):
        """
        The creation function. Doesn't return anything, but saves self.window variable and renderes using the self.renderer. 
        """
        
        try:    self.window
        except:
            firm_selected = self.solar_system_object_link.firm_selected
            
            
            if firm_selected is not None:
                
                if isinstance(firm_selected, company.merchant):
                    process_and_stock_dict = {}
                    for direction_name in ["destination","origin"]:
                        if direction_name == "destination":
                            base = firm_selected.to_location
                        else:
                            base = firm_selected.from_location
                        
                        direction = "in " + base.name
                        for resource in [firm_selected.resource, firm_selected.transport_type]:
                             process_and_stock_dict[resource + " at " + direction_name] = {}
                             process_and_stock_dict[resource + " at " + direction_name]["direction"] = direction
                             if direction_name == "destination":
                                 process_and_stock_dict[resource + " at " + direction_name]["current stock"] = firm_selected.to_stock_dict[resource]
                             else:
                                 process_and_stock_dict[resource + " at " + direction_name]["current stock"] = firm_selected.from_stock_dict[resource]
                             process_and_stock_dict[resource + " at " + direction_name]["rate"] = "NA"
                     
                else:
                    process_and_stock_dict = {}
                    for direction in ["input","output"]:
                        for resource in firm_selected.input_output_dict[direction]:
                             process_and_stock_dict[resource] = {}
                             process_and_stock_dict[resource]["direction"] = direction
                             process_and_stock_dict[resource]["current stock"] = firm_selected.stock_dict[resource]
                             process_and_stock_dict[resource]["rate"] = firm_selected.input_output_dict[direction][resource]
            
    
                
                self.window = gui_extras.fast_list(self.renderer)
                self.window.receive_data(process_and_stock_dict,column_order = ["rownames","direction","rate","current stock"],sort_by="direction")
                self.window.topleft = self.topleft
                self.window.list_size = self.list_size
                self.window.create_fast_list()
                self.window.render_title()
            
        else:
            if self.solar_system_object_link.message_printing["debugging"]:
                print_dict = {"text":"DEBUGGING: Tried to make a firm_process_info when it already existed","type":"debugging"}
                self.solar_system_object_link.messages.append(print_dict)


            















