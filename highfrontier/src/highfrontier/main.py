
# The main loop of the game. This procedure is running
# whenever the game is on the screen.



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
    
    icon = pygame.image.load(os.path.join("images","window_icon.png"))
    pygame.display.set_icon(icon) 
    
    #initializing the world - depends on if a previous game should be loaded
#    manager = EventManager()
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
        
        
     
        
    
    #loading planets that are often used:
    print "loading earth"
    sol.planets["earth"].pickle_all_projections()
    print "finished loading"
    
    

    
    #divide the surface in action and non-action
    action_rect = pygame.Rect(0,0,global_variables.window_size[0] - 150, global_variables.window_size[1])
    subcommand_rect = pygame.Rect(global_variables.window_size[0] - 150,global_variables.window_size[1] - 400, 150, 400)
    command_rect = pygame.Rect(global_variables.window_size[0] - 150, 0, 150, global_variables.window_size[1] - 400)
    
    action_surface = window.subsurface(action_rect)
    subcommand_surface = window.subsurface(subcommand_rect)
    command_surface = window.subsurface(command_rect)

    
    #switch to determine planetary mode or solarsystem mode from beginning
    mode_before_change = sol.display_mode 
    if sol.display_mode == "solar_system":
        surface = sol.draw_solar_system(zoom_level=sol.solar_system_zoom,date_variable=sol.current_date,center_object=sol.current_planet.planet_name)
        
    if sol.display_mode == "planetary":
        sol.current_planet = sol.planets["earth"]
        surface = sol.current_planet.draw_entire_planet(sol.current_planet.eastern_inclination,sol.current_planet.northern_inclination,sol.current_planet.projection_scaling)
    
    action_surface.blit(surface,(0,0))
    pygame.display.flip()
    
    
    #Initialising the GUI
    gui_instance = gui.gui(command_surface, subcommand_surface, action_surface, sol)

    


    #getting psyco if available
    try:
        import psyco
        #print "initialising psyco"
        psyco.log()
        psyco.profile()
    except ImportError:
        pass
    

    

    
    

    
    i = 0
    while True:    
        events = pygame.event.get()
        for event in events: 
            
            
            
            if event.type == QUIT: 
                sys.exit(0)
            if event.type == 5: #mouse down event
                gui_instance.receive_click(event)
                
                
            if event.type == 2: #key down event
                if "text_receiver" in dir(gui_instance.active_window):
                    if gui_instance.active_window.text_receiver is not None:
                        gui_instance.active_window.text_receiver.receive_text(event)
                        break
                        
                
#                if event.key == 113: #q
#                    gui_instance.start_nuclear_war(event)
                if event.key == 280: #pgup
                    gui_instance.zoom_in(event)
                if event.key == 281: #pgdown
                    gui_instance.zoom_out(event)
                if event.key == 276: #left
                    gui_instance.go_left(event)
                if event.key == 275: #right
                    gui_instance.go_right(event)
                if event.key == 273: #up
                    gui_instance.go_up(event)
                if event.key == 274: #down
                    gui_instance.go_down(event)


        
        
        pygame.time.delay(15)
        
        
        
        i = i + 1
        if i%sol.step_delay_time == 0:
            i = 0
            sol.current_date = datetime.timedelta(30)+sol.current_date
#            manager.emit("update_infobox",None)
            
                #            
            sol.evaluate_each_game_step()
           
            for company_instance in sol.companies.values():
                company_instance.evaluate_self()
                

            
            if sol.display_mode == "solar_system":
                surface = sol.draw_solar_system(zoom_level=sol.solar_system_zoom,date_variable=sol.current_date,center_object=sol.current_planet.planet_name)
                action_surface.blit(surface,(0,0))
                pygame.display.flip()
            else:
                pass
                #because the others need not be updated continously.
                
        


#    import hotshot
#    prof = hotshot.Profile("hotshot_edi_stats")
#    prof.runcall(temp_function,manager,renderer)
#    prof.close()
#    temp_function(manager,renderer)

start_loop(company_name = "Test2", company_capital = 1000000, load_previous_game = None)#os.path.join("pickledmiscellanous","A_small_test_game"))

   
