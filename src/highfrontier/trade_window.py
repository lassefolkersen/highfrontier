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
import gui_components
import random
import time

class trade_window():
    """
    This windows shows an overview of all assets (bases and firms) and tech that is for sale, ie. all non-location specific offers.
    """
    def __init__(self,solar_system_object,action_surface):
        self.solar_system_object_link = solar_system_object
        self.rect = pygame.Rect(25,50,825,500)
        self.action_surface = action_surface
        self.text_receiver = None
        self.menu_position = "root"
        self.selections = {}
        

    def create(self):
        """
        The creation function. Doesn't return anything.
        """
        self.text_receiver = None
        self.menu_position = "root"
        self.selections = {}
        
        asset_and_tech_data = {}
        for planet_instance in self.solar_system_object_link.planets.values():
            for base_instance in planet_instance.bases.values():
                if base_instance.for_sale:
                    
                    data_here = {"Type":"base","Best price":"for auction (pop: " + str(base_instance.population) + ")","For sale by":base_instance.owner.name,"for_sale_by_link":[base_instance.owner],"object":base_instance}

                    asset_and_tech_data[base_instance.name] = data_here
                
        #for company_instance in self.solar_system_object_link.companies.values():
            #pass #FIXME add firms for sale here, whenever that is implemented
        
        for technology in self.solar_system_object_link.technology_tree.vertex_dict.values():
            if len(technology["for_sale_by"]) > 0:
                prices = technology["for_sale_by"].values()
                prices.sort()
                best_price = prices[0]
                
                if len(technology["for_sale_by"]) == 1:
                    for_sale_by = str(technology["for_sale_by"].keys()[0].name)
                else:
                    for_sale_by = str(len(technology["for_sale_by"])) + " companies"
                for_sale_by_link = technology["for_sale_by"].keys()
                
                check_result = self.solar_system_object_link.technology_tree.check_technology_bid(self.solar_system_object_link.current_player.known_technologies,technology)
                if check_result != "already known": #only include if we don't already know it
                    if check_result is not "ok": #include it as a sales-piece if too advaned, but not possible to buy
                        type = "advanced tech."
                    else:
                        type = "technology"
                        
                    data_here = {"Type":type,"Best price":best_price,"For sale by":for_sale_by,"for_sale_by_link":for_sale_by_link,"object":technology}
                    asset_and_tech_data[technology["technology_name"]] = data_here
        
        if len(asset_and_tech_data) == 0:
            pygame.draw.rect(self.action_surface, (224,218,213), self.rect)
            pygame.draw.rect(self.action_surface, (0,0,0), self.rect, 2)
            pygame.draw.line(self.action_surface, (255,255,255), (self.rect[0], self.rect[1]), (self.rect[0] + self.rect[2], self.rect[1]))
            pygame.draw.line(self.action_surface, (255,255,255), (self.rect[0], self.rect[1]), (self.rect[0], self.rect[1] + self.rect[3]))
            
            warning = global_variables.standard_font.render("Nothing is for sale on the tech and asset market.",True,(0,0,0))
            self.action_surface.blit(warning, (self.rect[0] + self.rect[2] /2 - warning.get_width() / 2, self.rect[1] + self.rect[3] / 2 - warning.get_height() /2))


        else:
            
            column_order = ["rownames","Type","Best price","For sale by"]
            self.fast_list = gui_components.fast_list(self.action_surface, asset_and_tech_data, rect = self.rect, column_order = column_order)

    def receive_click(self,event):
        #if event.button == 1:
        if self.menu_position == "root":
            self.fast_list.receive_click(event)            
        elif self.menu_position == "pick_seller":
            self.fast_list.receive_click(event)            
        elif self.menu_position == "base bidding":
            if self.bid_button.rect.collidepoint(event.pos) == 1:
                return self.bid_button.activate(event)
        else:
            raise Exception("Unknown menu_position: " + str(self.menu_position))
        
        if event.button == 3:
            if self.fast_list.selected_name is not None:
                if self.menu_position == "root":
                    return self.process_bid(self.fast_list.selected_name)            
                elif self.menu_position == "pick_seller":
#                    print self.fast_list.selected_name
                    return self.perform_bid(self.fast_list.selected_name)            
                else:
                    raise Exception("Unknown menu_position: " + str(self.menu_position))



    def process_bid(self, bid_on):
        """
        Where clicks from the initial menu should be send. Bid_on is the name given in this first menu
        
        """
        self.selections["for_sale_by"] = self.fast_list.original_tabular_data[bid_on]["for_sale_by_link"]
        self.selections["sale_object"] = self.fast_list.original_tabular_data[bid_on]["object"]
        self.selections["type"] = self.fast_list.original_tabular_data[bid_on]["Type"]
        self.selections["price"] = self.fast_list.original_tabular_data[bid_on]["Best price"]
        self.selections["bid_on"] = bid_on
        
        if self.selections["type"] in ["technology","advanced tech."]:
            current_player_tech = self.solar_system_object_link.current_player.known_technologies
            check_result = self.solar_system_object_link.technology_tree.check_technology_bid(current_player_tech,self.selections["sale_object"] )
            if check_result != "ok":
                print_dict = {"text":"Can not bid for " + self.selections["bid_on"] + " because it is " + check_result,"type":"general gameplay info"}
                self.solar_system_object_link.messages.append(print_dict)
                return None

        
        if len(self.selections["for_sale_by"]) > 1:
            if self.selections["type"] not in ["technology","advanced tech."]:
                raise Exception("A bid was made for a type: " + str(self.selections["type"]) + " asset, with more than one seller. This should not be possible") 
            self.menu_position = "pick_seller"
            sellers_data = {}
            for seller in self.selections["sale_object"]["for_sale_by"]:
                price_here = self.selections["sale_object"]["for_sale_by"][seller]
                sellers_data[seller.name] = {"Price":price_here,"seller_link":seller}
    
            column_order = ["rownames","Price"]
            self.fast_list = gui_components.fast_list(self.action_surface,sellers_data,self.rect,column_order)
    
        else: #only one seller - just go for standard algorithm
            return self.perform_bid(self.selections["for_sale_by"][0].name) #chose the only one
        

                
                        
    def perform_bid(self, chosen_seller_name):
        """
        Function that allows the player to bid on an asset or technology
        """
        if chosen_seller_name not in self.solar_system_object_link.companies.keys():
            print_dict = {"text": str(chosen_seller_name) + " was not found - perhaps it was shut down recently.","type":"general gameplay info"}
            self.solar_system_object_link.messages.append(print_dict)
#            print "We had an instance of an unknown name: " + str(chosen_seller_name)
        else:
            chosen_seller = self.solar_system_object_link.companies[chosen_seller_name]
            current_player = self.solar_system_object_link.current_player
            
            
            
            
            if self.selections["type"] == "base":
                self.menu_position = "base bidding"
                pygame.draw.rect(self.action_surface, (224,218,213), self.rect)
                pygame.draw.rect(self.action_surface, (0,0,0), self.rect, 2)
                pygame.draw.line(self.action_surface, (255,255,255), (self.rect[0], self.rect[1]), (self.rect[0] + self.rect[2], self.rect[1]))
                pygame.draw.line(self.action_surface, (255,255,255), (self.rect[0], self.rect[1]), (self.rect[0], self.rect[1] + self.rect[3]))
                
                instruction = global_variables.standard_font.render("Enter bid for " + self.selections["bid_on"] + " (pop:" + str(self.selections["sale_object"].population) + ") with deadline " + str(self.selections["sale_object"].for_sale_deadline),True,(0,0,0))
                self.action_surface.blit(instruction, (self.rect[0] + 10, self.rect[1] + 10))
                
                
                # estimating a value of the base
                potential_base = self.selections["sale_object"]
                if potential_base.is_on_dry_land == "Yes":
                    dry_term = 1
                else:
                    dry_term = 0.01
                mining_values = []
                for resource in potential_base.mining_opportunities:
                    mining_opportunity = potential_base.mining_opportunities[resource]
                    price_of_resource = []
                    for trade_route in potential_base.trade_routes.values():
                        if trade_route["endpoint_links"].index(potential_base) == 1:
                            neighbour = trade_route["endpoint_links"][0]
                        else:
                            neighbour = trade_route["endpoint_links"][1]
                        try: neighbour.market["buy_offers"][resource]
                        except: 
                            if self.solar_system_object_link.message_printing["debugging"]:
                                print_dict = {"text":"DEBUGGING: When calculating bid, we did not find a market in neighbour " + str(neighbour.name),"type":"debugging"}
                                self.solar_system_object_link.messages.append(print_dict)
                        else:
                            if len(neighbour.market["buy_offers"][resource]) > 0:
                                price_of_resource.append(neighbour.market["buy_offers"][resource][0]["price"])
                    if len(price_of_resource) > 0:
                        mean_price_of_resource = sum(price_of_resource) / len(price_of_resource)
                        value = mining_opportunity * mean_price_of_resource
                        mining_values.append(value)
                mining_value_term = sum(mining_values)
                population_term = potential_base.population
                company_term = current_player.company_database["buy_out_tendency"]
                base_value = int(dry_term * mining_value_term * population_term * company_term * 0.00000001)
                
                #start the entry box
                self.text_receiver = gui_components.entry(self.action_surface,
                                     (self.rect[0] + 10, self.rect[1] + 40), 
                                     300, 32, 
                                     starting_text = str(base_value))
                
                
                self.bid_button = gui_components.button(
                                    "Bid",
                                    self.action_surface,
                                    self.effectuate_base_bid,
                                    function_parameter = None,
                                    topleft = (self.rect[0] + 10, self.rect[1] + 100)
                                    )
                return None
                
            
            if current_player.capital > self.selections["price"]:
                if self.selections["type"] in ["technology","advanced tech."]:
                        self.solar_system_object_link.current_player.known_technologies[self.selections["bid_on"]] = self.selections["sale_object"] 
                        current_player.capital = current_player.capital - self.selections["price"]
                        chosen_seller.capital = chosen_seller.capital + self.selections["price"]
                        print_dict = {"text":str(self.selections["bid_on"]) + " was bought for " + str(self.selections["price"]) + " from " + str(chosen_seller.name),"type":"general gameplay info"}
                        self.solar_system_object_link.messages.append(print_dict)
                         
                        
                elif self.selections["type"] == "base":
                        print_dict = {"text":"base buying not implemented yet","type":"general gameplay info"}
                        self.solar_system_object_link.messages.append(print_dict)
        
                else:
                    raise Exception("Unknown type: " + str(self.selections["type"]) + " asked for in the asset sales GUI")
        
                    
            else:
                print_dict = {"text":current_player.name + " has a capital of " + str(current_player.capital) + " and can't bid " + str(self.selections["price"]),"type":"general gameplay info"}
                self.solar_system_object_link.messages.append(print_dict)
        
        return "clear"     
    
    
    def effectuate_base_bid(self, label, function_parameters):
        
        price_string = self.text_receiver.text
        try: int(price_string)
        except:
            print_dict = {"text":"The bid: " + str(price_string) + " was not a number","type":"general gameplay info"}
            self.solar_system_object_link.messages.append(print_dict)
            return None
        else:
            price = int(price_string)

        if 3 * price > self.solar_system_object_link.current_player.capital: 
            print_dict = {"text":"The bid: " + str(price_string) + " was too expensive - more than 3 times capital is required","type":"general gameplay info"}
            self.solar_system_object_link.messages.append(print_dict)
            return None
#        else:
#            print str(price) + " is ok within capital"

        
        if self.selections["sale_object"].for_sale_deadline is not None:
            if self.selections["sale_object"].for_sale_deadline <= self.solar_system_object_link.current_date:
                print_dict = {"text":"You are too late for the bidding deadline, which was " + str(self.selections["sale_object"].for_sale_deadline),"type":"general gameplay info"}
                self.solar_system_object_link.messages.append(print_dict)
                return "clear"
#            else:
#                print str(self.selections["sale_object"].for_sale_deadline) + " is ok within time-limit"        
        else:
            print_dict = {"text":"You are too late for the bidding deadline","type":"general gameplay info"}
            self.solar_system_object_link.messages.append(print_dict)
            return "clear"

            
        self.selections["sale_object"].for_sale_bids[self.solar_system_object_link.current_player] = price
        print_dict = {"text":"You have bid " + str(price) + " for " + str(self.selections["bid_on"]) + " - the auction will run till: " + str(self.selections["sale_object"].for_sale_deadline),"type":"general gameplay info"}
        self.solar_system_object_link.messages.append(print_dict)
        return "clear"
