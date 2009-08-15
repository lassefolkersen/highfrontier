import os
import math
import Image
import pygame
import random
import datetime
import time
import planet
import company
import global_variables
import primitives
import technology
import cPickle
import Image
#import copy







class solarsystem:
    """
    The class that holds everything about the solarsystem.
    An instance of class solarsystem also holds all the planet instances within.
    """

    def __init__(self,start_date, de_novo_initialization = True):
#        global_variables.market_decisions = company.market_decisions()
        if de_novo_initialization:
            self.display_mode = "planetary"
            self.effectuate_growth_and_migration = global_variables.effectuate_growth_and_migration #if False all growth and migration calculations are performed, but are not actually applied to population numbers. Useful for equilibrizing the markets first.
            self.current_player = None #switch that determines what company is playing. If None it would default to simulatormode without possibility of interaction. Else it should be a company object.
            self.start_date = start_date
            self.current_date = self.start_date
            self.step_delay_time = global_variables.step_delay_time # how much delay (in miliseconds, I think) there should be before initiating the next iteration. This can be changed from the settings within the game
            self.technology_research_cost = global_variables.technology_research_cost #a variable specifying how much technology costs (in fact it is conversion factor for distance in the technology tree to research points) (100000 is pretty fast)
            self.bitterness_of_world = (None,None) # how much bitterness there is in the world. First entry is lowest bitterness level
            self.build_base_mode = False #a variable that specifies if a click on the map translates into building a base
            self.messages = []
            self.message_printing = {"general gameplay info":True,
                                "general company info":True,
                                "tech discovery":False,
                                "debugging":False,
                                "base sales":False,
                                "firm info":True, #this one only goes for the players own firms
                                "base info":True, #this one only goes for the players own firms
                                }
    
            
            # importing the trade resource text and the mineral_resources
            if os.access(os.path.join("data","economy","trade resources.txt"),1):
                data_file_name = os.path.join("data","economy","trade resources.txt")
                trade_resources = primitives.import_datasheet(data_file_name)
                mineral_resources = []
                for resource_name in trade_resources:
                    if trade_resources[resource_name]["type"] == "mineral":
                        mineral_resources.append(resource_name)
                        self.mineral_resources = mineral_resources
                self.trade_resources = trade_resources
            else:
                raise Exception("Did not find trade_resources.txt file. Warning - this might endanger the integrity of the program")
                

    
            
#            self.intialize_globals()
            
            self.window_size = global_variables.window_size
            self.universe_creation_date = datetime.date(1969,7,16)
            self.current_date = start_date
            self.solar_system_zoom = 20480
            self.areas_of_interest = {}
            self.company_selected = None
            self.firm_selected = None
            
    
            self.go_to_planetary_mode = False
    
            print "initializing planets"
            self.planets = self.initialize_planets()
            print "done initializing planets"
            
            print "initializing tech tree"
            backbone_tree_here = technology.Backbone_Tree()
            self.technology_tree = technology.Tree(backbone_tree_here,self)
            self.technology_tree.implode_and_expand()
            print "done initializing tech tree"
    
            
            print "initializing companies"
            self.companies = self.initialize_companies()
            print "done initializing companies"
    
            self.current_planet = self.planets["sun"]
        
        
        
        

    def close_company(self,company_name):
        """
        Function that closes down a company by simply deleting it from the list of companies  
        """
        del self.companies[company_name]
            
            
            
    def evaluate_each_game_step(self):
        """
        Function that is evaluated every single game loop. This is different than the company.evaluate_self functions where
        the evaluation frequency is a competition parameter that should be tuneable by selection.
        
        Things to put in here:
            Annual base stuff
                * migration
                * pollution
         
             Perhaps a year report?
             
        """         
        
        #This should only be done once a year - perhaps ok to say once every 360 days ie. every 12 game loops.
        
        try: self.last_evaluation_day_for_evaluate_each_game_step
        except: 
            self.last_evaluation_day_for_evaluate_each_game_step = self.current_date
        else:
            if self.current_date.year != self.last_evaluation_day_for_evaluate_each_game_step.year:
                self.last_evaluation_day_for_evaluate_each_game_step = self.current_date
                print_dict = {"text":"running the " + str(self.current_date.year) + " yearly part of evaluate_each_game_step","type":"general gameplay info"}
                self.messages.append(print_dict)
                self.bitterness_of_world = (None,None)
                for planet in self.planets.values():
                    for base in planet.bases.values():
                        if self.bitterness_of_world[0] is None or self.bitterness_of_world[1] is None:
                            self.bitterness_of_world = (base.bitternes_of_base, base.bitternes_of_base) 
                        if base.bitternes_of_base > self.bitterness_of_world[1]:
                            self.bitterness_of_world = (self.bitterness_of_world[0], base.bitternes_of_base)
                        if base.bitternes_of_base < self.bitterness_of_world[0]:
                            self.bitterness_of_world = (base.bitternes_of_base, self.bitterness_of_world[1])
         
                for planet in self.planets.values():
                    for base in planet.bases.values():
                        base.calculate_emigration()
                        base.calculate_growth_and_deaths()
                        base.calculate_emissions()
                        
 
                people = 0
                for planet in self.planets.values():
                    for base in planet.bases.values():
                        people = people + base.population
                number_of_companies = people / global_variables.persons_per_company 
                if number_of_companies > global_variables.max_number_of_companies:
                    number_of_companies = global_variables.max_number_of_companies
                number_of_companies = number_of_companies - len(self.companies) #do not count the country/companies already in existence
                #print "number_of_companies " + str(number_of_companies)
                
                if number_of_companies > 0:
                    richness_database = {}
                    for company_name in self.companies:
                        richness_database[self.companies[company_name].capital] = self.companies[company_name] 
                    richness_list = richness_database.keys()
                    richness_list.sort()
                    
                    richness_list = richness_list[(len(richness_list) * 2 / 3):len(richness_list)] #"This is the richest 1/3 of all companies"
                    list_of_model_companies = []
                    for key in richness_list:
                        list_of_model_companies.append(richness_database[key])
                    #list_of_model_companies_names is just for debugging
                    list_of_model_companies_names = []
                    
                    for i in range(0,number_of_companies):
                        model_company_number = random.randint(0,len(list_of_model_companies)-1)
                        model_company = list_of_model_companies[model_company_number] 
                        new_company = company.company(self,model_company_database=model_company.company_database,capital = 10000000) #FIXME change capital
                        self.companies[new_company.name] = new_company
                        
                        list_of_model_companies_names.append(model_company.name)
                    
                    print_dict = {"text":"Made " + str(len(list_of_model_companies_names)) + " new companies on the model of: " + str(list_of_model_companies_names),"type":"general company info"}
                    self.messages.append(print_dict)
                   
               
               
           
           
           
#        
#    def intialize_globals(self):
#        """ 
#        Function that takes care of importing and processing all initial global variables
#        """
#        
        
        

        




    
    def initialize_planets(self):
        data_file_name = os.path.join("data","planets.txt")
        read_planet_database = primitives.import_datasheet(data_file_name)
        planet_database = {}
        
        for planet_name in read_planet_database: 
            planet_instance = planet.planet(planet_name,self,read_planet_database[planet_name]) #creating the planet instance
            
            try: global_variables.distance_data
            except: global_variables.distance_data = planet_instance.calculate_all_distances()
            
            planet_database[planet_name] = planet_instance
        
        #checking that all projections exist
        random_planet_name = random.choice(planet_database.keys())
        random_planet = planet_database[random_planet_name]
        random_planet.pickle_all_projection_calculations()
        
        return planet_database
            
            
    def initialize_companies(self):
        base_to_country_list = {} 
        base_to_GNP_list = {}
        for planet in self.planets.values():
            for base in planet.bases.values():
                base_to_country_list[base.base_name] = base.original_country
                base_to_GNP_list[base.base_name] = base.GDP

        country_to_base_list = primitives.invert_dict(base_to_country_list)
        
        
        country_to_GNP_list = {}
        for country in country_to_base_list:
            country_GNP = 0
            for base in country_to_base_list[country]:
                country_GNP = base_to_GNP_list[base] + country_GNP
            country_to_GNP_list[country] = country_GNP
                
        
        ### Start up countries from companies.txt in data/economy
        data_file_name = os.path.join("data","economy","companies.txt")
        read_company_database = primitives.import_datasheet(data_file_name)
        
        random_company_name = random.choice(read_company_database.keys())
        for key in read_company_database[random_company_name]:
            if len(key) > global_variables.max_letters_in_company_names:
                raise Exception(key + " is " + str(len(key)) + " - maximum is " + str(global_variables.max_letters_in_company_names))
        
        
        
        #print read_company_database
        company_database = {}
        for company_name in read_company_database: 
            company_instance = company.company(self,company_name=company_name,model_company_database=read_company_database[company_name],capital = country_to_GNP_list[company_name]) #creating the company instance
            for planet in self.planets.values():
                for base in planet.bases.values(): 
                    if base.base_name in country_to_base_list[company_name]:
                        company_instance.owned_firms[base.base_name] = base
                        company_instance.home_cities[base.base_name] = base
#                        self.firms[base.base_name] = company_instance.home_cities[base.base_name]
            company_database[company_name] = company_instance
            

        
        ### starting up all companies (=countries) which are mentioned as owners of a base in the base_data files (and therefore
        ### put in the self.original_country variable), but which are not found in the above
        model_company_data = company_database["united states of america"].company_database #hehe - as if
        for company_name in country_to_base_list:
            if company_name not in company_database: 
                single_company_data = {}
                company_instance = company.company(self,model_company_database=model_company_data,company_name=company_name,capital = country_to_GNP_list[company_name]) #creating the company instance
                #company_instance.calculate_company_database(model_company_data, 10)
                
                company_instance.company_database["type"] = "country"
                for planet in self.planets.values():
                    for base in planet.bases.values(): 
                        if base.base_name in country_to_base_list[company_name]:
                            company_instance.owned_firms[base.base_name] = base
                            company_instance.home_cities[base.base_name] = base
#                            self.firms[base.base_name] = company_instance.home_cities[base.base_name]
                company_database[company_name] = company_instance

            
        
        #### Start up misc private companies
        people = []
        for planet in self.planets.values():
            for base in planet.bases.values():
                people.append(base.population)
        number_of_companies = sum(people) / global_variables.persons_per_company 
        if number_of_companies > global_variables.max_number_of_companies:
            number_of_companies = global_variables.max_number_of_companies
        number_of_companies = number_of_companies - len(company_database) #do not count the country/companies already included
        GWP = 0
        for planet in self.planets:
            for base in self.planets[planet].bases:
                GWP = self.planets[planet].bases[base].GDP + GWP
        mean_capital_per_company = GWP / number_of_companies
        
        all_bases = {}
        for planet in self.planets.values():
            for base in planet.bases.values():
                all_bases[base.base_name] = base
                
        for i in range(0,number_of_companies):
            #print "starting another company"
            capital = random.gauss(mean_capital_per_company,mean_capital_per_company/4)
            if capital < 1000:
                capital = 1000
            home_city = all_bases.keys()[random.randint(0,len(all_bases)-1)]
            company_instance = company.company(self,capital=capital)
            company_instance.company_database["type"] = "private company"
            
            #print company_instance.company_database
            company_instance.home_cities[home_city] = all_bases[home_city]
            company_database[company_instance.company_name] = company_instance
            
        #Setting base-ownership for all bases and calculating mining values (this is done now, because all necessary components first are ready now)
        for planet in self.planets.values():
            for base in planet.bases.values():
                base_owner_name = base.original_country
                base.owner = company_database[base_owner_name]
                for resource in self.mineral_resources:
                    base.get_mining_opportunities(planet,resource,check_date = self.start_date)
        
        
        
        
#        for company_instance in company_database.values():
#            if len(company_instance.owned_firms) > 0:
#                print company_instance.name + " has owned firms"
#                print company_instance.owned_firms
#        
        return company_database




    def save_solar_system(self,filename, prepare_scenario = False):
        """
        Function that will save the settings. One of the tricky things of doing this is that pictures can not be pickled, so
        the function includes the sub-function "get_sub_entry" to find out where pictures are saved. This, however, is not called
        by default since it is known where to find the pictures. Pictures are then converted to strings before saving, and
        re-converted back after saving. The planet surface pictures that are loaded in memory for faster rendering are removed temporarilu
        before the save but inserted afterwards. This means that they are lost on reload, which shouldn't be a big issue.
        
        prepare_for_scenario    Kills the current_player
        """
        
        def get_sub_entry(entry,i,before):
            """
            This small primitive recursive searcher can be used to check if there are images in the solar system
            Suggested use is to call just before the pickle step, to see if the system is clear. However, the call should
            be commented out by default since it is really silly extra time to use if it is already known where the pictures are
            """
            i = i + 1
            if i < 6:
                for sub_entry_name in dir(entry):
                    if sub_entry_name[0:2] != "__":
                        
                        sub_entry = getattr(entry, sub_entry_name)
#                        file = open(os.path.join("savegames","test"),"w")
#                        
#                        try:    
#                            cPickle.dump(sub_entry,file)
#                        except:
##                            if sub_entry
#                            print "found the culprit!"
#                            print sub_entry_name
#                            print sub_entry
#                            print before
#                            cPickle.dump(sub_entry,file)
#                        else:
#                            pass
#
#                        file.close()
                        if isinstance(sub_entry, instancemethod):
                            print "found the culprit!"
                            print sub_entry_name
                            print sub_entry
                        
                        if isinstance(sub_entry, pygame.Surface):
                            print str(sub_entry_name) + " is a surface"
                        try:    sub_entry.__class__
                        except: pass
                        else:
                            if issubclass(sub_entry.__class__, Image.Image):
                                print "The entry_name " + str(sub_entry_name) + " is a " + str(sub_entry.__class__) + " it is found at " + str(before) 

                        
                        before = before + " - " + sub_entry_name
                        get_sub_entry(sub_entry,i,before)
            
        

        if prepare_scenario:
            print self
            print self.current_player
            try:    self.current_player.name
            except:
                print "Preparing for scenario"
            else:
                raise Exception("Don't prepare for scenario when a player has been started up")
            self.current_date = datetime.date(time.localtime()[0],time.localtime()[1],time.localtime()[2]) #this is just for use when creating start out games
            
            self.step_delay_time = global_variables.step_delay_time 
            
            #resetting the technologies
            for company_instance in self.companies.values():
                company_instance.known_technologies = {}
                company_instance.pick_research()
                company_instance.research = 0
            for technology_name in self.technology_tree.vertex_dict:
                technology = self.technology_tree.vertex_dict[technology_name]
                if technology["known_by"] != "everybody":
                    technology["known_by"] = {}


        #removing pre-drawn surfaces and stringifiyng resource_maps        
        backup_up_pre_drawn_surfaces = {}
        known_planet_images = ["wet_areas","topo_image"] #this can be tested with above commented out block - also remember to change accordingly in the load function
        for planet_instance in self.planets.values():
            planet_instance.unload_from_drawing()

            
            
            for known_planet_image in known_planet_images:
                try:    getattr(planet_instance, known_planet_image)
                except: pass
                else:   
                    image = getattr(planet_instance, known_planet_image)
                    size = image.size
                    mode = image.mode
                    image_string = image.tostring()
                    setattr(planet_instance, known_planet_image, {"string":image_string,"mode":mode,"size":size})

            
            if planet_instance.pre_drawn_surfaces != {}:
                backup_up_pre_drawn_surfaces[planet_instance.name] = {}
                for pre_drawn_surface_key in planet_instance.pre_drawn_surfaces:
                     pre_drawn_surface = planet_instance.pre_drawn_surfaces[pre_drawn_surface_key]

                     backup_up_pre_drawn_surfaces[planet_instance.name][pre_drawn_surface_key] = pre_drawn_surface
                planet_instance.pre_drawn_surfaces = {}
                 
            #this is where the resource maps gets stringified
            if planet_instance.resource_maps != {}:
                for resource in planet_instance.resource_maps:
                    image = planet_instance.resource_maps[resource]
                    size = image.size
                    mode = image.mode
                    image_string = image.tostring()
                    planet_instance.resource_maps[resource] = {"string":image_string,"mode":mode,"size":size}

#        get_sub_entry(self,0,"") #can be used to search for pictures. See get_sub_entry.__doc__
        
        
        #this is the actual save command
#        self.current_date = datetime.date(time.localtime()[0],time.localtime()[1],time.localtime()[2]) #this is just for use when creating start out games
        file = open(filename,"w")
        try:  cPickle.dump(self,file)
        except MemoryError:
            print "DEBUGGING: cPickle failed, likely because of memory issue. Switching to regular pickle. Regular pickle is slower but less memory intensive."
            import pickle
            try:    pickle.dump(self,file)
            except: print "DEBUGGING: regular pickle also failed. The game was NOT saved"
            else:   print "game saved"
        except: 
            print "some weird error with cPickle - shown here:"
            cPickle.dump(self,file)
        else:
            print "game saved"
        file.close()

        #here we restore the pre_drawn surfaces
        for planet_name in backup_up_pre_drawn_surfaces:
            planet_instance = self.planets[planet_name] 
            for pre_drawn_surface_key in backup_up_pre_drawn_surfaces[planet_name]:
                 pre_drawn_surface = backup_up_pre_drawn_surfaces[planet_name][pre_drawn_surface_key]
                 planet_instance.pre_drawn_surfaces[pre_drawn_surface_key] = pre_drawn_surface


        #here we de-stringify the resource maps and other known images
        for planet_instance in self.planets.values():
            for known_planet_image in known_planet_images:
                if hasattr(planet_instance, known_planet_image):
                    image_parts = getattr(planet_instance, known_planet_image)
                    image = Image.fromstring(image_parts["mode"],image_parts["size"],image_parts["string"])
                    setattr(planet_instance, known_planet_image, image)

            
            if planet_instance.resource_maps != {}:
                for resource in planet_instance.resource_maps:
                    image_parts = planet_instance.resource_maps[resource]
                    
                    image = Image.fromstring(image_parts["mode"],image_parts["size"],image_parts["string"])
                    planet_instance.resource_maps[resource] = image

              
    def load_solar_system(self,filename):
        """
        Function that loads the solar system
        
        """
        file = open(filename,"r")
        new_solar_system = cPickle.load(file)
        file.close()
        
#        print "loaded " + str(new_solar_system)
        #here we de-stringify the resource maps and other known planet images
        known_planet_images = ["wet_areas","topo_image"] 
        for planet_instance in new_solar_system.planets.values():
            for known_planet_image in known_planet_images:
                if hasattr(planet_instance, known_planet_image):
                    image_parts = getattr(planet_instance, known_planet_image)
                    image = Image.fromstring(image_parts["mode"],image_parts["size"],image_parts["string"])
                    
#                    try:    image.save("test_" + known_planet_image + ".jpg")
#                    except: print "Could save " + known_planet_image
#                    else:   pass
                    
                    setattr(planet_instance, known_planet_image, image)

            if planet_instance.resource_maps != {}:
                for resource in planet_instance.resource_maps:
                    image_parts = planet_instance.resource_maps[resource]
                    
                    image = Image.fromstring(image_parts["mode"],image_parts["size"],image_parts["string"])
                    planet_instance.resource_maps[resource] = image
        
        
#        print "untouched:"
#        list = []
#        for company_instance in self.companies.values():
#            list.append(str(company_instance.solar_system_object_link))
#        print "The first and second of company solar_system_object: " + str(list[0:2])
#        print "new_solar_system: " + str(new_solar_system)
#        print "self: " + str(self)
#        try:    self.technology_tree.solar_system_object_link
#        except: 
#            print "no tech tree"
#        else:
#            print "self.technology_tree.solar_system_object_link: " + str(self.technology_tree.solar_system_object_link)
        
        #inserting all variables in self
        for entry_name in dir(self):
            if not hasattr(new_solar_system, entry_name):
                delattr(self,entry_name)
        
        for entry_name in dir(new_solar_system):
            entry = getattr(new_solar_system, entry_name)
            setattr(self,entry_name, entry)
            
#        print "loaded:"
#        list = []
#        for company_instance in self.companies.values():
#            list.append(str(company_instance.solar_system_object_link))
#        print "The first and second of company solar_system_object: " + str(list[0:2])
#        print "new_solar_system: " + str(new_solar_system)
#        print "self: " + str(self)
#        print "self.technology_tree.solar_system_object_link: " + str(self.technology_tree.solar_system_object_link)
            
        #updating all solar_system_object_links (this is actually rather weird that it has to be done)
        for company_instance in self.companies.values():
            company_instance.solar_system_object_link = self
            for owned_firm_instance in company_instance.owned_firms.values():
                owned_firm_instance.solar_system_object_link = self
        for planet_instance in self.planets.values():
            planet_instance.solars_system_object_link = self
        self.technology_tree.solar_system_object_link = self
#        gui.commandbox.solar_system_object_link = self
#        for gui_window in gui.commandbox.all_windows.values():
#            gui_window.solar_system_object_link = self

#        print "modified:"
#        list = []
#        for company_instance in self.companies.values():
#            list.append(str(company_instance.solar_system_object_link))
#        print "The first and second of company solar_system_object: " + str(list[0:2])
#        print "new_solar_system: " + str(new_solar_system)
#        print "self: " + str(self)
#        print "self.technology_tree.solar_system_object_link: " + str(self.technology_tree.solar_system_object_link)
            

    
    def get_satellite_to_center_position(self,object,zoom_level,date_variable):
        """
        given the orbital parameters and satellite, this returns 
        the coordinate transposition from the satellite to its center of orbit
        """
        orbital_position = self.get_planet_position(object,date_variable)
        semi_major_axis = self.planets[object].planet_data["semi_major_axis"] #in km
         
        eccentricity = self.planets[object].planet_data["eccentricity"]
        
        #relative_semi_major_axis = float ( mpf(semi_major_axis) * mpq(max(self.window_size) , 17000000000/zoom_level))  #this setting is made so zoom_level = 1 gives a view of all bodies including pluto
        relative_semi_major_axis = float ( semi_major_axis * max(self.window_size) / (17000000000/zoom_level))  #this setting is made so zoom_level = 1 gives a view of all bodies including pluto
        
        relative_semi_minor_axis = ((relative_semi_major_axis ** 2) * (1 - (eccentricity **2) )) ** 0.5 
        x = relative_semi_major_axis * math.cos(orbital_position - math.pi)
        y = relative_semi_minor_axis * math.sin(orbital_position - math.pi)
        
        return (int(-x),int(-y))


    
    def get_planet_position(self,satellite,date_variable):
        """
        given the time and planet name, this returns the orbital position as a number between 0 and 2pi
        """
        
        elapsed_time = date_variable - self.universe_creation_date
        
        orbital_period = self.planets[satellite].planet_data["orbital_period_days"]
        orbital_position = (int(elapsed_time.days) % orbital_period) / orbital_period
        orbital_position = orbital_position * 2 * math.pi
        return orbital_position

        

    def get_areas_of_interest(self,zoom_level,date_variable,center_object):
        """
        Returns a dictionary of the area of interest of all objects in view, meaning the on-screen coordinate and a some radius 
        (size_of_target) around it. The keys are the objects orbiting the center_object and all objects with same or
        higher hierarchial level
        """
        
        areas_of_interest_here = {}
        positions_of_interest = {}
        size_of_target = 5
        self.window_size

        #Determine which orbits to draw 
        satellite_iterator = self.planets[center_object].planet_data["satellite_of"]
        hierarchy_list = [center_object]
        while satellite_iterator is not None:
            hierarchy_list.append(satellite_iterator)
            satellite_iterator = self.planets[satellite_iterator].planet_data["satellite_of"]
        
        #Which orbits to draw - returns the names of all objects that are satellites of the center_object or an object higher in the hierarchy
        hierarchy_dependent_transposition = (0,0)
        for orbit_center in hierarchy_list:
            list = self.calculate_from_a_center(zoom_level,date_variable,surface=None,orbit_center=orbit_center,hierarchy_dependent_transposition=hierarchy_dependent_transposition,draw=False)
            positions_of_interest.update(list)
            if orbit_center != "sun":
                new_hierarchy_dependent_transposition = self.get_satellite_to_center_position(orbit_center,zoom_level,date_variable)
                hierarchy_dependent_transposition =  (new_hierarchy_dependent_transposition[0] + hierarchy_dependent_transposition[0],new_hierarchy_dependent_transposition[1] + hierarchy_dependent_transposition[1])
        #Include the sun
        sun_position = (hierarchy_dependent_transposition[0] + global_variables.window_size[0] * 0.5, hierarchy_dependent_transposition[1] + global_variables.window_size[1] * 0.5)
        positions_of_interest["sun"] = sun_position
        
        #assign the rectangles
        for planet in positions_of_interest:
            areas_of_interest_here[(positions_of_interest[planet][0],positions_of_interest[planet][1],size_of_target,size_of_target)] = planet
            

        self.areas_of_interest = areas_of_interest_here
        

    
    
    def calculate_from_a_center(self,zoom_level,date_variable,surface,orbit_center,hierarchy_dependent_transposition,draw=True):
        """
        This function takes an existing surface, and some orbit-data on a center planet 
        then adds the orbits and drawings of all the satellites of the center_planet. The drawing can be
        moved by using the hierarchy_dependent_transposition variable.
        If boolean Draw is false, it will only return a list of positions of the planets
        """
        if not draw:
            position_list = {}
        #print "Info from calculate_from_a_center"
        #print "Now drawing from center: " + str(orbit_center)
        for object in self.planets:
            if self.planets[object].planet_data["satellite_of"] == orbit_center: #draw all the satellites of each of the preceding planets
                semi_major_axis = self.planets[object].planet_data["semi_major_axis"] #in km 
                
#                relative_semi_major_axis = float ( mpf(semi_major_axis) * mpq(max(self.window_size) , 17000000000/zoom_level))  #this setting is made so zoom_level = 1 gives a view of all bodies including pluto
                relative_semi_major_axis = float( semi_major_axis) * max(self.window_size) / (17000000000/zoom_level)  #this setting is made so zoom_level = 1 gives a view of all bodies including pluto
                
                #if relative_semi_major_axis < 1000: #for protecting against very large numbers slowing down the process
                eccentricity = self.planets[object].planet_data["eccentricity"]
                relative_semi_minor_axis = ((relative_semi_major_axis ** 2) * (1 - (eccentricity **2) )) ** 0.5 
                type = self.planets[object].planet_type
                orbit_color = self.planets[object].planet_data["orbit_color"]
                smallplanet_color = self.planets[object].planet_data["smallplanet_color"]
                
                #satellite_diameter = mpf(self.planets[object].planet_diameter_km) * mpq(max(self.window_size)*int(zoom_level) , 17000000000)
                satellite_diameter = self.planets[object].planet_diameter_km * max(self.window_size)*int(zoom_level) / 17000000000
                
                orbital_position = self.get_planet_position(object, date_variable)
                orbit_placement = int((orbital_position * 99) / (2 * math.pi))
                
                orbit = []
                for i in range(0,100 ):
                    t = -math.pi + i * ((2 * math.pi) / 100 )
                    x = self.window_size[0]/2 + relative_semi_major_axis * math.cos(t) + hierarchy_dependent_transposition[0]
                    y = self.window_size[1]/2 + relative_semi_minor_axis * math.sin(t) + hierarchy_dependent_transposition[1]
                    orbit.append((x,y))

                if draw:
                    for i in range(0,len(orbit)):
                        if i == len(orbit)-1:
                            pygame.draw.line(surface,(orbit_color),orbit[0],orbit[len(orbit)-1])
                        elif i in [orbit_placement -1, orbit_placement +1]:
                            pass
                        elif i == orbit_placement:
                            x = self.window_size[0]/2 + relative_semi_major_axis * math.cos(orbital_position - math.pi) + hierarchy_dependent_transposition[0]
                            y = self.window_size[1]/2 + relative_semi_minor_axis * math.sin(orbital_position - math.pi) + hierarchy_dependent_transposition[1]
                            if 0 < x < self.window_size[0] and 0 < y < self.window_size[1]:
                                self.draw_small_object(satellite_diameter,(x,y),object,surface)
                        else:
                            try: pygame.draw.line(surface,orbit_color,orbit[i],orbit[i+1])
                            except:
                                print "orbit[i] " + str(orbit[i])
                                print "orbit[i+1] " + str(orbit[i+1])
                                print "orbit_color " + str(orbit_color)
                                try:    surface.size
                                except: pass
                                else:   print "surface size " + str(surface.size)
                                print orbit
                                raise Exception("This bug has been observed before, on a backward press from Phobos")
    
                
                if not draw:
                    x = self.window_size[0]/2 + relative_semi_major_axis * math.cos(orbital_position - math.pi) + hierarchy_dependent_transposition[0]
                    y = self.window_size[1]/2 + relative_semi_minor_axis * math.sin(orbital_position - math.pi) + hierarchy_dependent_transposition[1]
                    if 0 < x < self.window_size[0] and 0 < y < self.window_size[1]:
                        position_list[object] = (int(x),int(y))

        if draw:
            return surface
        if not draw:
            return position_list
        






        
    def draw_small_object(self,diameter,position,object,surface):
        """
        How to draw the individual heavenly bodies
        The diameter is a relative diameter corrected for zoom_level as seen in calculate_from_a_center
        The position is a tupple of on-screen coordinates
        The object is a string with the object name
        The surface is a pygame surface on which to draw the small object
        These orbital data is used to draw the object as specified on the surface. If zoom is large enough, we go to planetary mode
        """
        smallplanet_color = self.planets[object].planet_data["smallplanet_color"]
        if self.solar_system_zoom > 2000000:
            if object != "sun":
                self.display_mode = "planetary"
                self.go_to_planetary_mode = True
            else: #this will keep the zoom from going to far in on the sun
                self.solar_system_zoom = self.solar_system_zoom / 2
                self.draw_small_object(diameter, position, object, surface)
        elif diameter < 2.0:
            pygame.draw.polygon(surface,smallplanet_color,[position,(position[0],position[1]+1),(position[0]+1,position[1]),(position[0]+1,position[1]+1)])
        elif diameter > 20.0 and object != "sun": 
            if object == self.current_planet.planet_name:
                self.display_mode = "planetary"
                self.go_to_planetary_mode = True
            else:
                print str(object) + " should be drawn as a real planet, since it has a diameter of " +str(diameter)
                
                if 20 < diameter < 40:
                    projection_scaling_here = 45
                elif 40 <= diameter < 80:
                    projection_scaling_here = 90
                elif 80 <= diameter < 160:
                    projection_scaling_here = 180
                else:
                    projection_scaling_here = 360
                    
                print "projection_scaling_here: " + str(projection_scaling_here)
                custom_drawn_planet = self.planets[object].draw_image(0,90,projection_scaling_here,fast_rendering=True)
                surface.blit(custom_drawn_planet,(position[0]-projection_scaling_here/2,position[1]-projection_scaling_here/2))
        else:
            #print "Info from draw_small_object: this is a medium size drawing" 
            #print "object:" + str(object) + " - position: " + str(position) + " - diamter: " + str(diameter)
            
            pointlist = []
            for i in range(1,50):
                t = -math.pi + i * ((2 * math.pi) / 50 )
                x = position[0] + 0.5* diameter * math.cos(t)
                y = position[1] + 0.5* diameter * math.sin(t)
                pointlist.append((x,y))
            pygame.draw.polygon(surface,smallplanet_color,pointlist)

   







    
    def draw_solar_system(self,zoom_level,date_variable,center_object):
        """
        This is the function that draws the entire solar system
        It is a more generalised and experimental version of what is found in the old
        draw_solar_system. It still needs to include the sun in the drawing, and also there
        possibly is a problem with planets when looking on moons
        """
        self.go_to_planetary_mode = False
        
        #self.notify("zoom_level",self.zoom_level,zoom_level)
        
        #Draw the empty space
        surface = pygame.Surface(self.window_size)
        surface.fill((0,0,0))
        
        #Determine which orbits to draw 
        satellite_iterator = self.planets[center_object].planet_data["satellite_of"]
        hierarchy_list = [center_object]
        while satellite_iterator is not None:
            hierarchy_list.append(satellite_iterator)
            satellite_iterator = self.planets[satellite_iterator].planet_data["satellite_of"]
            
            
        
        #Which orbits to draw - returns the names of all objects that are satellites of the center_object or an object higher in the hierarchy
        hierarchy_dependent_transposition = (0,0)
        for orbit_center in hierarchy_list:
            surface = self.calculate_from_a_center(zoom_level,date_variable,surface,orbit_center,hierarchy_dependent_transposition,True)
            if orbit_center != "sun":
                new_hierarchy_dependent_transposition = self.get_satellite_to_center_position(orbit_center,zoom_level,date_variable)
                hierarchy_dependent_transposition =  (new_hierarchy_dependent_transposition[0] + hierarchy_dependent_transposition[0],new_hierarchy_dependent_transposition[1] + hierarchy_dependent_transposition[1])
                #print "The hiearchy_dependent_transposition for " + str(orbit_center) + " is " + str(hierarchy_dependent_transposition)  
        
        #Drawing the sun
#        sun_diameter = mpf(self.planets["sun"].planet_diameter_km) * mpq(max(self.window_size)*int(zoom_level) , 17000000000)
        sun_diameter = self.planets["sun"].planet_diameter_km * max(self.window_size)*int(zoom_level) / 17000000000
        
        sun_position = (hierarchy_dependent_transposition[0] + global_variables.window_size[0] * 0.5, hierarchy_dependent_transposition[1] + global_variables.window_size[1] * 0.5)
        self.draw_small_object(sun_diameter, sun_position , "sun", surface)

        if self.go_to_planetary_mode is True:
            surface = "planetary_mode"
        else:
            self.get_areas_of_interest(zoom_level,date_variable,center_object)
        
        
        return surface
    
    
        
        
    
                        
                    
                    
                        
