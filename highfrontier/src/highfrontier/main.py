
# The main loop of the game. This procedure is running
# whenever the game is on the screen.



import pygame
from pygame.locals import *
from ocempgui.widgets import *
from ocempgui.events import EventManager
from ocempgui.object import BaseObject
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

















def start_loop(company_name = None, company_capital = None, load_previous_game = None):
    """
    company_name          string of a company that will play as current player. If none, the game will run in simulation mode
    company_capital       int with the starting capital of the newly started company.
    load_previous_game    filename of a save game that can be loaded
    
    """
    
    #initilizing screen stuff
    window_size = global_variables.window_size
    pygame.init()
    if global_variables.fullscreen:
        window = pygame.display.set_mode(window_size,FULLSCREEN) 
    else:
        window = pygame.display.set_mode(window_size)
    screen = pygame.display.get_surface()
    pygame.display.set_caption('The High Frontier')
    icon = pygame.image.load(os.path.join("images","window_icon.png"))
    pygame.display.set_icon(icon) 
    
    #initializing the world - depends on if a previous game should be loaded
    manager = EventManager()
    if load_previous_game is not None:
        sol = solarsystem.solarsystem(global_variables.start_date, de_novo_initialization = False)
        sol.load_solar_system(load_previous_game)
    else:
        sol = solarsystem.solarsystem(global_variables.start_date, de_novo_initialization = True)
    
    #initialize current player company
    if company_name is not None:
        if sol.current_player is not None:
            raise Exception("The loaded solar system already had a current player")
        
        if company_name in sol.companies.keys():
            raise Exception("The company_name " + str(company_name) + " already existed")
            
        model_company_name = random.choice(sol.companies.keys())
        model_company = sol.companies[model_company_name]

        new_company = company.company(sol,model_company.company_database,deviation=5,company_name=company_name,capital=company_capital)
        sol.companies[company_name] = new_company
        new_company.automation_dict = {
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
        sol.current_player = new_company
        
        #double checking that all solar_system_object_link -- very weird that this has to be done, but otherwise it seems that an old link is preserved
#        for company_instance in sol.companies.values():
#            company_instance.solar_system_object_link = sol
#            for owned_firm_instance in company_instance.owned_firms.values():
#                owned_firm_instance.solar_system_object_link = sol
#        for planet_instance in sol.planets.values():
#            planet_instance.solars_system_object_link = sol
#        sol.technology_tree.solar_system_object_link = sol
        
        
     
        
    
    #loading planets that are often used:
    print "loading earth"
    sol.planets["earth"].pickle_all_projections()
    print "finished loading"
    
    
    
    #FIXME artificially adding some space stations to earth
    ISS = {
           "name":"ISS",
           "population":10,
           "semi_major_axis":358 + (sol.planets["earth"].planet_diameter_km / 2),
           "orbital_period_days":0.0634,
           "inclination_degrees":51.64,
           "eccentricity":0
           }
    
    EOSAM1 = {
           "name":"EOSAM1",
           "population":0,
           "semi_major_axis":685 + (sol.planets["earth"].planet_diameter_km / 2),
           "orbital_period_days":0.0681,
           "inclination_degrees":98.2,
           "eccentricity":0
           } 

    GEO1 = {
           "name":"GEO1",
           "population":0,
           "semi_major_axis":35700 + (sol.planets["earth"].planet_diameter_km / 2),
           "orbital_period_days":0.0681,
           "inclination_degrees":1,
           "eccentricity":0
           } 
    
    
    sol.planets["earth"].space_stations = {}
    
    
    sol.planets["earth"].space_stations["EOSAM1"] = EOSAM1
    sol.planets["earth"].space_stations["ISS"] = ISS
    sol.planets["earth"].space_stations["GEO1"] = GEO1
    
    

    
    #switch to determine planetary mode or solarsystem mode from beginning
    mode_before_change = sol.display_mode 
    if sol.display_mode == "solar_system":
        surface = sol.draw_solar_system(zoom_level=sol.solar_system_zoom,date_variable=sol.current_date,center_object=sol.current_planet.planet_name)
    if sol.display_mode == "planetary":
        sol.current_planet = sol.planets["earth"]
        surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
    
    mainscreen = ImageLabel(surface)
    mainscreen.padding = 0
    

    
    #Drawing the world
    renderer = Renderer()
    renderer.screen = screen
    
    mainscreen.set_picture(surface)
    

    
    #Initialising the GUI
    commandbox = gui.commandbox(renderer,manager,sol)
    commandbox.manager = manager
    


    #getting psyco if available
    try:
        import psyco
        #print "initialising psyco"
        psyco.log()
        psyco.profile()
    except ImportError:
        pass
    
    
    #Drawing the GUI
    renderer.add_widget(mainscreen)
    renderer.add_widget(commandbox.table)
    renderer.update()
    
    #defining all callbacks


    class Main(BaseObject):
        """
        class that holds all the most basic navigational functions
        """
        def __init__(self,manager):
            BaseObject.__init__(self)
            self._signals["zoom_in"] = []
            self._signals["zoom_out"] = []
            self._signals["center_on"] = []
            self._signals["go_left"] = []
            self._signals["go_right"] = []
            self._signals["go_down"] = []
            self._signals["go_up"] = []
            self._signals["lower_waters"] = []
            self._signals["raise_waters"] = []
            self._signals["start nuclear war"] = []
            self._signals["display_overlay"] = []
            self._signals["going_to_company_window_event"] = []
            self._signals["going_to_firm_window_event"] = []
            self._signals["going_to_base_mode_event"] = []
            self._signals["going_to_techtree_mode_event"] = []
            
#            self._signals["insert_new_solar_system"] = []
            self.manager = manager

        def notify(self,event):
            if event.signal == "zoom_in":
                if sol.display_mode == "solar_system":
                    sol.solar_system_zoom = sol.solar_system_zoom * 2
                    surface = sol.draw_solar_system(zoom_level=sol.solar_system_zoom,date_variable=sol.current_date,center_object=sol.current_planet.planet_name)
                    if surface == "planetary_mode":
                        manager.emit("going_to_planetary_mode_event",sol.current_planet)
                        sol.solar_system_zoom = sol.solar_system_zoom / 2
                        sol.display_mode = "planetary"
                        sol.current_planet.load_for_drawing()
                        surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
                        mainscreen.set_picture(surface)
                        renderer.update()
                    else:
                        mainscreen.set_picture(surface)
                        renderer.update()
                elif sol.display_mode == "planetary":
                    if sol.current_planet.projection_scaling < 720:
                        sol.current_planet.projection_scaling = sol.current_planet.projection_scaling * 2
                        surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)                        
                        mainscreen.set_picture(surface)
                        renderer.update()
                    else:
                        if sol.current_planet.current_base is not None: #if a base is selected on this planet, we'll zoom in on it
                            sol.display_mode = "base"
                            manager.emit("going_to_base_mode_event",sol.current_planet.current_base)
                elif sol.display_mode in ["base","firm","company"]:
                    print "Can't zoom further in"
                elif sol.display_mode in ["techtree"]:
                    surface = sol.technology_tree.zoom("in")
                    mainscreen.set_picture(surface)
                    renderer.update()
                else:
                    print "error. The mode: " + sol.display_mode +" is unknown"
            
            
            if event.signal == "zoom_out":
                if sol.display_mode == "solar_system":
                    if sol.solar_system_zoom >= 2:
                        sol.solar_system_zoom = sol.solar_system_zoom / 2
                        surface = sol.draw_solar_system(zoom_level=sol.solar_system_zoom,date_variable=sol.current_date,center_object=sol.current_planet.planet_name)
                        mainscreen.set_picture(surface)
                        renderer.update()
        
                
                elif sol.display_mode == "planetary":
                    if sol.current_planet.projection_scaling >= 90:
                        sol.current_planet.projection_scaling = sol.current_planet.projection_scaling / 2
                        surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
                        mainscreen.set_picture(surface)
                        renderer.update()
                    else:
                        manager.emit("going_to_solar_system_mode_event",None)
                        sol.current_planet.unload_from_drawing()
                        sol.display_mode = "solar_system" 
                        surface = sol.draw_solar_system(zoom_level=sol.solar_system_zoom,date_variable=datetime.date(2102,1,22),center_object=sol.current_planet.planet_name)
                        mainscreen.set_picture(surface)
                        renderer.update()
                elif sol.display_mode in ["firm","company","base"]:
#                    sol.current_planet.projection_scaling = sol.current_planet.projection_scaling / 2
                    manager.emit("going_to_planetary_mode_event",sol.current_planet)
                    surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
                    mainscreen.set_picture(surface)
                    renderer.update()
                    sol.display_mode = "planetary"

                elif sol.display_mode in ["techtree"]:
                    surface = sol.technology_tree.zoom("out")
                    mainscreen.set_picture(surface)
                    renderer.update()
                    
                else:
                    print "error. The mode: " + sol.display_mode +" is unknown"                

            
            if event.signal == "center_on":
                if isinstance(event.data,str): # in this case it is a string with instructions on where to center
                    position = event.data
                    sol.current_planet.unload_from_drawing()
                    sol.current_planet = sol.planets[position]
                    sol.current_planet.load_for_drawing()
                    surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
                    sol.display_mode = "planetary"
                    sol.solar_system_zoom = 200000000 / sol.current_planet.planet_diameter_km
                    manager.emit("going_to_planetary_mode_event",sol.current_planet)
                    mainscreen.set_picture(surface)
                    renderer.update()
                else: #in this case it is a mouse click
                    position = event.data.pos
                    button = event.data.button
                    click_spot = pygame.Rect(position[0]-2,position[1]-2,4,4)
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
                                
                                
                        
                            mainscreen.set_picture(surface)
                            renderer.update()
                    
                    
                    elif sol.display_mode == "planetary":
                    
                        if sol.build_base_mode: #if we are in the special build base mode, there should be a base creation instead.
                            sphere_coordinates = sol.current_planet.check_base_position(position)
                            if isinstance(sphere_coordinates, tuple): #if the selection was correctly verified by check_base_position we send it back to the GUI for further processing
                                sol.build_base_mode = False
                                commandbox.all_windows["left_side_base_navigation"].basewindow_selected = None
                                commandbox.all_windows["base_build_menu"].new_base_ask_for_name(sphere_coordinates)
                        
                        else: #if we are not in build_base_mode we work as normally
                            areas_of_interest = sol.current_planet.areas_of_interest[(sol.current_planet.northern_inclination,sol.current_planet.eastern_inclination,sol.current_planet.projection_scaling)]
                            collision_test_result = click_spot.collidedict(areas_of_interest)
                            if collision_test_result != None:
                                current_base = sol.current_planet.bases[collision_test_result[1]]
                                #print "current_base " + str(current_base)
                                sol.current_planet.current_base = current_base
                                if button == 1:
                                    surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
                                    mainscreen.set_picture(surface)
                                    renderer.update()
                                if button == 3:
                                    manager.emit("going_to_base_mode_event",current_base)
                    
                    
                    elif sol.display_mode in ["techtree"]:
                        surface = sol.technology_tree.receive_click(position,button)
                        mainscreen.set_picture(surface)
                        renderer.update()
                    
                    elif sol.display_mode in ["company","firm","base"]:
                        pass            
                    else:
                        print "error. The mode: " + sol.display_mode +" is unknown"                

                    
                    
                    
            
            if event.signal == "go_left":
                if sol.display_mode == "planetary":
                    
                    
                    
                    sol.current_planet.eastern_inclination = sol.current_planet.eastern_inclination - 30
                    if sol.current_planet.eastern_inclination <= -180:
                        sol.current_planet.eastern_inclination = sol.current_planet.eastern_inclination + 360
                    surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
                    
        #            sol.current_planet.draw_space_stations(surface,sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling) #FIXME - this can be removed
                    mainscreen.set_picture(surface)
                    renderer.update()
                elif sol.display_mode == "techtree":
                    surface = sol.technology_tree.move("left")
                    mainscreen.set_picture(surface)
                    renderer.update()                     
                else:
                    print "error. The mode: " + sol.display_mode +" does not accept arrow input"
                
            if event.signal == "go_right":
                if sol.display_mode == "planetary":
                    sol.current_planet.eastern_inclination = sol.current_planet.eastern_inclination + 30
                    if sol.current_planet.eastern_inclination > 180:
                        sol.current_planet.eastern_inclination = sol.current_planet.eastern_inclination - 360
                    #surface = sol.current_planet.draw_overlay_map(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling,"iron")
                    surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
                    mainscreen.set_picture(surface)
                    renderer.update()
                elif sol.display_mode == "techtree":
                    surface = sol.technology_tree.move("right")
                    mainscreen.set_picture(surface)
                    renderer.update()                     
                else:
                    print "error. The mode: " + sol.display_mode +" does not accept arrow input"
        
                
            if event.signal == "go_down":
                if sol.display_mode == "planetary":
                    if sol.current_planet.northern_inclination > -90:
                        sol.current_planet.northern_inclination = sol.current_planet.northern_inclination - 30
                        surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
                        mainscreen.set_picture(surface)
                        renderer.update()
            
                    else:
                        print "Can't go further south"
                elif sol.display_mode == "techtree":
                    surface = sol.technology_tree.move("down")
                    mainscreen.set_picture(surface)
                    renderer.update()                     
                else:
                    print "error. The mode: " + sol.display_mode +" does not accept arrow input"
        
            
            if event.signal == "go_up":
                if sol.display_mode == "planetary":
                    if sol.current_planet.northern_inclination < 90:
                        sol.current_planet.northern_inclination = sol.current_planet.northern_inclination + 30
                        surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
                        mainscreen.set_picture(surface)
                        renderer.update()
                    else:
                        print "Can't go further north"
                elif sol.display_mode == "techtree":
                    surface = sol.technology_tree.move("up")
                    mainscreen.set_picture(surface)
                    renderer.update()                     
                else:
                    print "error. The mode: " + sol.display_mode +" does not accept arrow input"
        
        
            if event.signal == "raise_waters":
                if sol.display_mode == "planetary":
                    sol.current_planet.change_water_level(sol.current_planet.water_level + 0.5)
                    surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
                    mainscreen.set_picture(surface)
                    renderer.update()
                else:
                    pass
        #            print "error. The mode: " + sol.display_mode +" does not accept a/z input"
        
                
            
            if event.signal == "lower_waters":
                if sol.display_mode == "planetary":
                    sol.current_planet.change_water_level(sol.current_planet.water_level - 0.5)                        
                    surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
                    mainscreen.set_picture(surface)
                    renderer.update()
                else:
                    pass
        
        
            if event.signal == "start nuclear war":
                if sol.display_mode == "planetary":
                    earth = sol.planets["earth"]
                    base_names_chosen = ["stockholm","glasgow","bremen","rotterdam","stuttgart","genoa"]
                    bases_chosen = {}
                    for base_name_chosen in base_names_chosen:
                        bases_chosen[base_name_chosen] = earth.bases[base_name_chosen]
                    earth.explode(56,10,bases_chosen,mainscreen,renderer)
                else:
                    pass

        #            print "error. The mode: " + sol.display_mode +" does not accept a/z input"
        
        
            if event.signal == "display_overlay":
                type_of_overlay = event.data
                sol.current_planet.planet_display_mode = type_of_overlay
                surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
                mainscreen.set_picture(surface)
                renderer.update()
        
        
            if event.signal == "going_to_company_window_event":
                company_selected = event.data
                mode_before_change = sol.display_mode
                sol.display_mode = "company"
                surface = company_selected.draw_company_window()
                mainscreen.set_picture(surface)
                renderer.update()
        
            if event.signal == "going_to_firm_window_event":
                firm_selected = event.data
                mode_before_change = sol.display_mode
                sol.display_mode = "firm"
                surface = firm_selected.draw_firm_window()
                mainscreen.set_picture(surface)
                renderer.update()
                
            if event.signal == "going_to_base_mode_event":
                base_selected = event.data
                mode_before_change = sol.display_mode
                sol.current_planet.current_base = base_selected
                sol.current_planet = base_selected.home_planet
                sol.display_mode = "base"
                surface = base_selected.draw_base_window()
                mainscreen.set_picture(surface)
                renderer.update()
        
        
            if event.signal == "going_to_techtree_mode_event":
                mode_before_change = sol.display_mode
                sol.display_mode = "techtree"
                surface = sol.technology_tree.plot_total_tree(sol.technology_tree.vertex_dict,sol.technology_tree.zoomlevel,center = sol.technology_tree.center)
                mainscreen.set_picture(surface)
                renderer.update()
#                


    main = Main(manager)
    

    
    

    
    i = 0
    while True:    
        events = pygame.event.get()
        for event in events: 
            if event.type == QUIT: 
                sys.exit(0)
            if event.type == 5: #mouse down event
                
                manager.emit("center_on",event)
                manager.emit("update_infobox",None)
                
            if event.type == 2: #key down event
                
                if event.key == 113: #q
                    manager.emit("start nuclear war",None)
                if event.key == 280: #pgup
                    manager.emit("zoom_in",None)
                    manager.emit("update_infobox",None)
                if event.key == 281: #pgdown
                    manager.emit("zoom_out",None)
                    manager.emit("update_infobox",None)
                if event.key == 276: #left
                    manager.emit("go_left",None)
                    manager.emit("update_infobox",None)
                if event.key == 275: #right
                    manager.emit("go_right",None)
                    manager.emit("update_infobox",None)
                if event.key == 273: #up
                    manager.emit("go_up",None)
                    manager.emit("update_infobox",None)
                if event.key == 274: #down
                    manager.emit("go_down",None)
                    manager.emit("update_infobox",None)
    
    
        renderer.distribute_events(*events)
        
        pygame.time.delay(15)
        
        
        
        i = i + 1
        if i%sol.step_delay_time == 0:
            i = 0
            sol.current_date = datetime.timedelta(30)+sol.current_date
            manager.emit("update_infobox",None)
            
                #            
            sol.evaluate_each_game_step()
           
            for company_instance in sol.companies.values():
                company_instance.evaluate_self()
                

            
            if sol.display_mode == "solar_system":
                surface = sol.draw_solar_system(zoom_level=sol.solar_system_zoom,date_variable=sol.current_date,center_object=sol.current_planet.planet_name)
                mainscreen.set_picture(surface)
                renderer.update()
            else:
                pass
                #because the others need not be updated continously.
                
        


#    import hotshot
#    prof = hotshot.Profile("hotshot_edi_stats")
#    prof.runcall(temp_function,manager,renderer)
#    prof.close()
#    temp_function(manager,renderer)

#start_loop(company_name = "Test2", company_capital = 1000000, load_previous_game = None)

   
