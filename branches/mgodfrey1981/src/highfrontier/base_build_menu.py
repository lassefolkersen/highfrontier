import fast_list
import entry
import button
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

class base_build_menu():
    """
    Subview of the base view. Shows all options regarding building firms and other bases from the current base.
    
    The first list is derived from the list of currently known technologies + options to build research, merchants and new bases.
    
    The actions from choosing a commodity producer from the known technologies is to create that firm in the current city. Likewise, more
    or less, for research firms. Choosing merchant brings up question boxes about where the destination and what resource should be traded.
    Choosing new base building brings zooms out to base position mode.
    
    
    """
    def solarSystem(self):
        return global_variables.solar_system

    def __init__(self,action_surface):
        self.rect = pygame.Rect(50,50,700,500)
        self.action_surface = action_surface
        
        self.menu_position = "root"
        self.selections = {}
        self.text_receiver = None



    def create(self):
        """
        The creation function.  
        """
        self.text_receiver = None
        self.menu_position = "root"
        self.selections = {}
        

        buildoption_data = {}
        for technology_name in self.solarSystem().current_player.known_technologies:
            if technology_name != "common knowledge":
                technology = self.solarSystem().current_player.known_technologies[technology_name]
            
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

        buildoption_data["population transfer"] = {}
        buildoption_data["population transfer"]["input and output"] = "To existing or new base - costs depends on distance"
        
        self.fast_list = fast_list.fast_list(self.action_surface, buildoption_data, rect = self.rect)


    def receive_click(self,event):
        
        
        if event.button == 1:
            if self.menu_position == "pick name":
                if self.ok_button.rect.collidepoint(event.pos) == 1:
                    self.ok_button.activate(event)
                    return "clear"
            elif self.menu_position == "commodity size":
                if self.slider.rect.collidepoint(event.pos) == 1:
                    self.slider.activate(event.pos)
                if self.ok_button.rect.collidepoint(event.pos) == 1:
                    return self.ok_button.activate(event.pos)
                
            else:
                self.fast_list.receive_click(event)
        
        
        if event.button == 3:
            if self.menu_position in ["root","pick destination","pick resource"]:
                self.fast_list.receive_click(event)
            
            
            if self.menu_position == "root":
                if self.fast_list.selected_name is not None:
                    if self.fast_list.selected_name == "merchant":
                        self.merchant_pick_destination()
                    elif self.fast_list.selected_name == "population transfer":
                        return "population transfer"
                    else:
                        self.commodity_size_selection(self.fast_list.selected_name)
            
            elif self.menu_position == "pick destination":
                if self.fast_list.selected_name is not None:
                    self.merchant_pick_resource(self.fast_list.selected_name)
            
            elif self.menu_position == "pick resource":
                if self.fast_list.selected_name is not None:
                    self.merchant_pick_name(self.fast_list.selected_name)
                    
                





  
    def merchant_pick_destination(self):
        """
        Function to ask what destination the merchant should trade with
        """
        self.menu_position = "pick destination"
        destination_data = {}
        location = self.solarSystem().current_planet.current_base
        for destination_name in location.trade_routes:
            destination = location.trade_routes[destination_name]
            
            destination_data[destination_name] = {}
            destination_data[destination_name]["distance"] = destination["distance"]
            destination_data[destination_name]["type"] = destination["transport_type"]

        self.fast_list = fast_list.fast_list(self.action_surface, destination_data, rect = self.rect)

            
            
        
    def merchant_pick_resource(self, destination_name):
        """
        Function to ask what resource the merchant should trade in
        """
        self.menu_position = "pick resource"
        

        from_location = self.solarSystem().current_planet.current_base
        trade_route_selected = from_location.trade_routes[destination_name]
    
        #prepare direct links to the other endpoint location
        for endpoint in trade_route_selected["endpoint_links"]:
            if endpoint != from_location:
                to_location = endpoint
        
        #prepare resource data
        resource_data = {}
        for resource in self.solarSystem().trade_resources.keys():
            if self.solarSystem().trade_resources[resource]["transportable"]:
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
            
        self.fast_list = fast_list.fast_list(self.action_surface, resource_data, rect = self.rect)    
        
        
        
        
        
        from_location = self.solarSystem().current_planet.current_base
        trade_route_selected = from_location.trade_routes[destination_name]
        for endpoint in trade_route_selected["endpoint_links"]:
            if endpoint != from_location:
                to_location = endpoint
        self.selections = {"to_location":to_location,"from_location":from_location,"trade_route_selected":trade_route_selected}


    def merchant_pick_name(self,resource,give_length_warning=False):
        """
        Function to get the name of the merchant
        give_length_warning         If true, this will specify the max text size as part of the title.
        """
        self.menu_position = "pick name"
        
        self.selections["resource"] = resource


        #check that this does not already exist
        exists = False
        for firm_instance in self.solarSystem().current_player.owned_firms.values():
            if firm_instance.isMerchant():
                if firm_instance.from_location == self.selections["from_location"]:
                    if firm_instance.to_location == self.selections["to_location"]:
                        if firm_instance.resource == resource:
                            exists = True
        if exists:
            print_dict = {"text":"A merchant from " + str(self.selections["from_location"].name) + " to " + str(self.selections["to_location"].name) + " trading " + str(resource) + " does already exist","type":"general gameplay info"}
            self.solarSystem().messages.append(print_dict)

            
        else:
            
            pygame.draw.rect(self.action_surface, (212,212,212), self.rect)
            pygame.draw.rect(self.action_surface, (0,0,0), self.rect, 2)
            pygame.draw.line(self.action_surface, (255,255,255), (self.rect[0], self.rect[1]), (self.rect[0] + self.rect[2], self.rect[1]))
            pygame.draw.line(self.action_surface, (255,255,255), (self.rect[0], self.rect[1]), (self.rect[0], self.rect[1] + self.rect[3]))

            text = global_variables.standard_font.render("Choose name for merchant:",True,(0,0,0))
            self.action_surface.blit(text, (self.rect[0] + 10, self.rect[1] + 10))

        
        
            if give_length_warning:
                warning = global_variables.standard_font.render("Name must be unique",True,(0,0,0))
                self.action_surface.blit(warning, (self.rect[0] + 10, self.rect[1] + 50))
                
                
            self.text_receiver = entry.entry(self.action_surface, 
                                 topleft = (self.rect[0] + 10, self.rect[1] + 90), 
                                 width = self.rect[3] - 20, 
                                 max_letters = global_variables.max_letters_in_company_names)
            self.text_receiver.active = True
    
            self.ok_button = button.button("ok", 
                                                    self.action_surface,
                                                    self.merchant_build, 
                                                    function_parameter = None, 
                                                    fixed_size = (100,35), 
                                                    topleft = (self.rect[0] + 10, self.rect[1] + 150)
                                                    )
            

        
        
        
        
    def merchant_build(self,label,function_parameter):
        """
        Function to build the merchant
        """ 
        for test in ["to_location","from_location","trade_route_selected","resource"]:
            if test not in self.selections.keys():
                raise Exception("The " + test + " was not properly selected")
        
        resource = self.selections["resource"]
        
        
        name = self.text_receiver.text

        #test if name is unique
        unique = True
        for company_instance in self.solarSystem().companies.values():
            if name in company_instance.owned_firms.keys():
                unique = False
        
        if 0 < len(name) <= global_variables.max_letters_in_company_names and unique:
            owner = self.solarSystem().current_player
            input_output_dict = {"input":{},"output":{},"timeframe":30,"byproducts":{}}
            distance = self.selections["trade_route_selected"]["distance"]
            transport_type = self.selections["trade_route_selected"]["transport_type"]
            new_merchant_firm = merchant.merchant(self.solarSystem(),
                                                  self.selections["from_location"],
                                                  self.selections["to_location"],
                                                  input_output_dict,
                                                  owner,
                                                  name,
                                                  transport_type,
                                                  distance,
                                                  self.selections["resource"])
            owner.owned_firms[name] = new_merchant_firm
            print_dict = {"text":"Built a merchant named " + str(name) + " between " + str(self.selections["from_location"].name) + " and " + str(self.selections["to_location"].name) + " trading in " + str(self.selections["resource"]),"type":"general gameplay info"}
            self.solarSystem().messages.append(print_dict)
            self.selections = {}
            self.menu_position = "root"
        else:
            print_dict = {"text":"the selected name " + str(name) + " was too long. Has to be less than " + str(global_variables.max_letters_in_company_names) + " characters","type":"general gameplay info"}
            self.solarSystem().messages.append(print_dict)
            self.merchant_pick_name(self.selections["resource"],give_length_warning=True)


    
    def commodity_size_selection(self, firm_type):
        """
        This function creates a dialog asking the size of the firm to be built
        The range of the size is from "1" where the it is just the input_output_dict
        to the integer at which the sum of the inputs are equal to 10% the population of the city (FIXME this rule is not implemented for AI - also note that it is more like 101% of the sum at present)
         
        """
        self.menu_position = "commodity size"
        
        self.selections = {}
        self.selections["firm_type"] = firm_type
        
        if firm_type in ["population transfer","merchant"]:
            raise Exception("This should have been distributed correctly already at the select_button_callback step")
        elif firm_type == "research":
            technology = {}
            technology["input_output_dict"] = {}
            technology["input_output_dict"]["input"] = {"labor":1}
            technology["input_output_dict"]["output"] = {"research:":1}
            technology["technology_name"] = "research"
        else:
            technology = self.solarSystem().current_player.known_technologies[firm_type]
        
        input_size = 0
        
        
        #calculate the range allowed
        for input in technology["input_output_dict"]["input"].values():
            input_size = input_size + input
        if input_size < 2: 
            input_size = 2
        if self.solarSystem().current_planet.current_base is None:
            raise Exception("very weird - there was no base selected")
        population = self.solarSystem().current_planet.current_base.population
        max_size = max(int(population * 0.05 / float(input_size)),1)
        
        
        #check if the current_player already owns a company of that technology in the current base
        existing_firm = None
        for firm_instance in self.solarSystem().current_player.owned_firms.values():
            if firm_instance.location == self.solarSystem().current_planet.current_base:
                if firm_instance.technology_name == firm_type:
                    existing_firm = firm_instance
                    break
        
        
        #clean up the act
        pygame.draw.rect(self.action_surface, (212,212,212), self.rect)
        pygame.draw.rect(self.action_surface, (0,0,0), self.rect, 2)
        pygame.draw.line(self.action_surface, (255,255,255), (self.rect[0], self.rect[1]), (self.rect[0] + self.rect[2], self.rect[1]))
        pygame.draw.line(self.action_surface, (255,255,255), (self.rect[0], self.rect[1]), (self.rect[0], self.rect[1] + self.rect[3]))


        
        
        if existing_firm is None:
            start_value = 1
            existing_firm_rendered_text = global_variables.standard_font.render("Choose name of firm:",True,(0,0,0))
            self.action_surface.blit(existing_firm_rendered_text, (self.rect[0] + 90, self.rect[1] + 70))
            self.text_receiver = entry.entry(self.action_surface, 
                     topleft = (self.rect[0] + 100, self.rect[1] + 90, self.rect[2] - 100, self.rect[3] - 150), 
                     width = 300, 
                     max_letters = global_variables.max_letters_in_company_names)
            self.text_receiver.active = True

        
        else:
            
            start_value = existing_firm.size
            
             
            existing_firm_rendered_text = global_variables.standard_font.render("An existing size " + str(existing_firm.size) + " firm of this type already owned here.",True,(0,0,0))
            self.action_surface.blit(existing_firm_rendered_text, (self.rect[0] + 130, self.rect[1] + 70))
            existing_firm_rendered_text = global_variables.standard_font.render("Select new size and press ok if new size is required.",True,(0,0,0))
            self.action_surface.blit(existing_firm_rendered_text, (self.rect[0] + 130, self.rect[1] + 85))


        text = global_variables.standard_font.render("Choose size of firm:",True,(0,0,0))
        self.action_surface.blit(text, (self.rect[0] + 90, self.rect[1] + 150))

        
        fastest = global_variables.standard_font.render("Smallest",True,(0,0,0))
        self.action_surface.blit(fastest, (self.rect[0] + 40, self.rect[1] + 40))

        slowest = global_variables.standard_font.render("Largest",True,(0,0,0))
        self.action_surface.blit(slowest, (self.rect[0] + 40, self.rect[1] + self.rect[3]-  50))
        
        
        def execute(label, technology):
            """
            This function is activated on scrollbar value change on the size selection box, and updates the input_output_dict
            """

            update_rect = pygame.Rect(self.rect[0] + 50, self.rect[1] + 170, self.rect[2] - 100, self.rect[3] - 250) 
            pygame.draw.rect(self.action_surface, (212,212,212), update_rect)
            
            size_info = global_variables.standard_font_small.render("size: " + str(self.slider.position),True,(0,0,0))
            self.action_surface.blit(size_info, (self.rect[0] + 130, self.rect[1] + 170))
            lineno = 0
            for put in ["input","output"]:
                lineno = lineno + 1
                direction_info = global_variables.standard_font_small.render(put+":",True,(0,0,0))
                self.action_surface.blit(direction_info, (self.rect[0] + 130, self.rect[1] + 170 + lineno * 20))
#                print technology.keys()
                for resource in technology["input_output_dict"][put].keys():
                    lineno = lineno + 1
                    if resource in self.solarSystem().mineral_resources + ["food"] and put == "output":
                        mining_opportunity = self.solarSystem().current_planet.current_base.get_mining_opportunities(self.solarSystem().current_planet, resource)
                        unmodified_output = technology["input_output_dict"]["output"][resource]
                        value = (mining_opportunity / 10) * unmodified_output
                        value = int(value * self.slider.position)
                        value_info = global_variables.standard_font_small.render(resource + ": " + str(value) + " (location modifier: " + str(round(mining_opportunity,2)) + ")",True,(0,0,0))

                    else:
                        value = technology["input_output_dict"][put][resource]
                        value = value * self.slider.position
                        value_info = global_variables.standard_font_small.render(resource + ": " + str(value),True,(0,0,0))
                    
                    
                    self.action_surface.blit(value_info, (self.rect[0] + 150, self.rect[1] + 170 + lineno * 20))



            
            
            self.ok_button = button.button("ok", 
                                        self.action_surface,
                                        self.commodity_build_firm, 
                                        function_parameter = existing_firm, 
                                        fixed_size = (100,35), 
                                        topleft = (self.rect[0] + self.rect[2] - 110, self.rect[1] + self.rect[3] - 40))

            
            pygame.display.flip()
        
        if 1 >  start_value or max_size < start_value:
            print start_value
            print max_size
            print firm_type
            raise Exception("This has been observed before. See printout")
        
        self.slider = vscrollbar.vscrollbar (self.action_surface,
                                                execute,
                                                topleft = (self.rect[0] + 10, self.rect[1] + 30),
                                                length_of_bar_in_pixel = self.rect[3] - 60,
                                                range_of_values = (1,max_size),
                                                start_position = start_value,
                                                function_parameter = technology
                                                )
        execute(None,technology)
        
        self.selections["technology"] = technology 
      





#
#
#
#        
#    def commodity_ask_for_name(self,label,existing_firm,give_length_warning=False):
#        """
#        This command is called after the size selection box has been accepted
#        """
#        size_requested = self.slider.position
##        print "commodity_ask_for_name and existing_firm is " + str(existing_firm)
#        self.menu_position = "commodity name"
#        update_rect = pygame.Rect(self.rect[0] + 50, self.rect[1] + 70, self.rect[2] - 100, self.rect[3] - 150) 
#        pygame.draw.rect(self.action_surface, (212,212,212), update_rect)
#
#        
#        if existing_firm is None:
#            name = self.text_receiver.text
#            
#        else: #in cases where the firm already exists, we preserve the name
#             
#            
##            existing_info = global_variables.standard_font_small.render("Updating firm size",True,(0,0,0))
##            self.action_surface.blit(existing_info, (self.rect[0] + 130, self.rect[1] + 70))
##            pygame.display.flip()
##            print "commodity_ask_for_name knows that existing firm is not none but " + str(existing_firm)
#            self.commodity_build_firm(None, existing_firm)
#            return "clear"
#
#
#            
##            self.commodity_build_firm(technology, self.size_requested, existing_name = existing_firm.name)
#            
#
#        



    def commodity_build_firm(self,label,existing_firm):
        """
        The effectuating function for building commodity firms.
            either takes a name for a new firm
            or the instance for an existing firm
        """

        
        if existing_firm is None:
            name = self.text_receiver.text
            unique = True
            for company_instance in self.solarSystem().companies.values():
                if name in company_instance.owned_firms.keys():
                    unique = False
        
            if not (0 < len(name) <= global_variables.max_letters_in_company_names and unique):
                print_dict = {"text":"the selected name " + str(name) + " was too long and/or not unique. Has to be less than " + str(global_variables.max_letters_in_company_names) + " characters","type":"general gameplay info"}
                self.solarSystem().messages.append(print_dict)
                self.commodity_size_selection(self.selections["firm_type"])
                return None
            
        else: #if existing name exists, we use that
            name = existing_firm.name
        
        
        
        technology = self.selections["technology"]
        location = self.solarSystem().current_planet.current_base
        owner = self.solarSystem().current_player
        size = self.slider.position
        
        owner.change_firm_size(location,size,technology["technology_name"], name)
        if isinstance(name, str) or isinstance(name, unicode):
            print_dict = {"text":str(name) + ", a " + self.selections["firm_type"] + " firm of size " + str(size) + " was built at " + str(location.name) + " for " + str(owner.name),"type":"general gameplay info"}
            self.solarSystem().messages.append(print_dict)

        else:
            print name
            print name.__class__
            raise Exception("The name used: " + str(name) + " was of class " + str(name.__class__) + " but should have been a string")
        return "clear"




