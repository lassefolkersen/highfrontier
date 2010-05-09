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

class base_and_firm_market_window():
    """
    Subview of the base view and also of the firm view. Shows information about the market in the base. For a chosen resource this can be either
    a history of what transactions has been made, or an overview of the bids currently in effect.
    
    This is also the interface where manual bids can be made
    """

    def __init__(self,solar_system_object,action_surface):
        self.solar_system_object_link = solar_system_object
        self.rect = pygame.Rect(50,50,700,500)
        self.action_surface = action_surface
        

        self.resource_selected = self.solar_system_object_link.trade_resources.keys()[0]
        self.graph_rect = pygame.Rect(200,100,400,400)


        self.frame_size = 40
        self.blank_area_in_middle_height = 30 #the middle area in the market bid mode
        self.graph_selected = "history"
        self.positional_database = {"bidding_mode":{},"non_bidding_mode":{}} #can be filled with information about clicks that the graphs receive
        self.highlighted_transactions = []
        self.bidding_mode = False #if click on the map should result in bidding


    def trade_resource_set_callback(self,label,function_parameter):
        self.resource_selected = label
        self.update_data(None, None)

    def graph_mode_callback(self,label,function_parameter):
        self.graph_selected = label
        self.update_data(None, None)    


    def market_selection_callback(self,label,function_parameter):
        self.base_selected_for_merchant = function_parameter[label]
        self.update_data(None, None)
#        
    def place_bid_callback(self,label,function_parameter):
        self.bidding_mode = label

    
    def create(self):
        """
        The creation function. Doesn't return anything, but saves and renders using the self.renderer. 
        """
        if self.graph_selected == "place bid mode":
            self.graph_selected = "history"
        
        
        pygame.draw.rect(self.action_surface, (212,212,212), self.rect)
        pygame.draw.rect(self.action_surface, (0,0,0), self.rect, 2)
        pygame.draw.line(self.action_surface, (255,255,255), (self.rect[0], self.rect[1]), (self.rect[0] + self.rect[2], self.rect[1]))
        pygame.draw.line(self.action_surface, (255,255,255), (self.rect[0], self.rect[1]), (self.rect[0], self.rect[1] + self.rect[3]))
        
        #first making a list of the resources that should be displayed
        if self.solar_system_object_link.display_mode == "base":
            resource_button_names = self.solar_system_object_link.trade_resources.keys()
        elif self.solar_system_object_link.display_mode == "firm":
            firm_selected = self.solar_system_object_link.firm_selected
            if firm_selected.isMerchant():
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
        self.resource_buttons = gui_components.radiobuttons(
                                                        resource_button_names, 
                                                        self.action_surface, 
                                                        function = self.trade_resource_set_callback, 
                                                        function_parameter = None, 
                                                        topleft = (self.rect[0] + 10 , self.rect[1] + 10), 
                                                        selected = self.resource_selected)
        
        
        self.graph_buttons = gui_components.radiobuttons(
                                                        ["history","market bids"], 
                                                        self.action_surface, 
                                                        function = self.graph_mode_callback, 
                                                        function_parameter = None, 
                                                        topleft = (self.rect[0] + 10 , self.rect[1] + 40 + self.resource_buttons.rect[3]),
                                                        selected = self.graph_selected)

        
        
        #in case it is a merchant selected we have to also pick the markets looked upon.
        if self.solar_system_object_link.display_mode == "firm":
            firm_selected = self.solar_system_object_link.firm_selected
            if firm_selected.isMerchant():
                self.market_selection_buttons = gui_components.radiobuttons(
                                                        ["From: " + firm_selected.from_location.name,"To: " + firm_selected.to_location.name], 
                                                        self.action_surface, 
                                                        function = self.market_selection_callback, 
                                                        function_parameter = {"From: " + firm_selected.from_location.name:firm_selected.from_location,"To: " + firm_selected.to_location.name:firm_selected.to_location}, 
                                                        topleft = (self.rect[0] + 10 , self.graph_buttons.rect[1] + self.graph_buttons.rect[3] + 40),
                                                        selected = "From: " + firm_selected.from_location.name)

                self.base_selected_for_merchant = firm_selected.from_location

                
            else:
                self.market_selection_buttons = None
                
        elif self.solar_system_object_link.display_mode == "base":
            self.market_selection_buttons = None
            firm_selected = self.solar_system_object_link.current_planet.current_base 
        else:
            raise Exception("Unknown display_mode: " + str(global_variabes.display_mode))
                    
        #Add an update button that allows for updates to be done
        try:    self.market_selection_buttons.rect
        except: update_button_topleft = (self.rect[0] + 10, self.graph_buttons.rect[1]+ self.graph_buttons.rect[3] + 20)
        else:   update_button_topleft = (self.rect[0] + 10, self.market_selection_buttons.rect[1]+ self.market_selection_buttons.rect[3] + 20)   

        
        self.update_button = gui_components.button("Update",
                                                   self.action_surface,
                                                   function = self.update_data,
                                                   function_parameter = None, 
                                                   topleft = update_button_topleft, 
                                                   fixed_size = None)
        


        
        #Finally, in case the firm selected is owned by the player, we add a "make market bid button"
        if firm_selected.name in self.solar_system_object_link.current_player.owned_firms.keys():
            self.bid_button = gui_components.togglebutton("Make market bid",
                                           self.action_surface,
                                           function = self.place_bid_callback,
                                           function_parameter = None, 
                                           topleft = (self.rect[0] + 10, self.update_button.rect[1] + self.update_button.rect[3] +20), 
                                           fixed_size = None)

            
            self.bidding_mode = False
        else:
            self.bid_button = None
            self.bidding_mode = False
            
        self.update_data(None, None)
            
        
    def update_data(self, label, function_parameter):
        """
        Function to update the data in the market analysis window. Its most important function is that it calls the relevant
        analysis function (market bids or market history) depending on the self.graph_selected variable.
        """
        
        self.highlighted_transactions = []
        if self.graph_selected == "market bids":
            surface = self.update_data_market_bids()
        elif self.graph_selected == "history":
            surface = self.update_data_history()
        elif self.graph_selected == "place bid mode":
            return None
        else:
            raise Exception("Unknown graph type " + self.graph_selected)

        if not isinstance(surface,pygame.Surface):
            print self.graph_selected
            print surface
            print self.update_data_history()
            print self.update_data_market_bids()
            raise Exception("The surface returned in the market window was not recognised")
        
        self.action_surface.blit(surface, (self.graph_rect[0],self.graph_rect[1]))
        pygame.display.flip()


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
                if firm_selected.isMerchant():
                    market = self.base_selected_for_merchant.market
                else:
                    market = firm_selected.location.market
            else:
                raise Exception("The display mode " + str(self.solar_system_object_link.display_mode) + " is not supposed to show market data")

            #painting the basic market_analysis surface
            market_analysis_surface = pygame.Surface((self.graph_rect[2],self.graph_rect[3]))
            market_analysis_surface.fill((212,212,212))
            pygame.draw.line(market_analysis_surface,(50,50,50),(0,self.graph_rect[3]*0.5+7),(self.graph_rect[3],self.graph_rect[3]*0.5+7),3)
            pygame.draw.line(market_analysis_surface,(50,50,50),(0,self.graph_rect[3]*0.5-7),(self.graph_rect[3],self.graph_rect[3]*0.5-7),3)
            
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
                market_analysis_surface.blit(market_price_label,(0,self.graph_rect[3]*0.5-5))
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
                    market_analysis_surface.blit(buy,(0,self.graph_rect[3]-15))

                else:
                    market_price_description = "Highest buy offer: " + "%.5g" % market["buy_offers"][resource][0]["price"] + ". Lowest sell offer: " + "%.5g" % market["sell_offers"][resource][0]["price"] 
                    market_price = (market["sell_offers"][resource][0]["price"] + market["buy_offers"][resource][0]["price"]) * 0.5
                    market_analysis_surface.blit(sell,(0,0))
                    market_analysis_surface.blit(buy,(0,self.graph_rect[3]-15))
                market_price_label = global_variables.standard_font.render(market_price_description,True,(0,0,0))
                market_analysis_surface.blit(market_price_label,(self.graph_rect[2]/100,self.graph_rect[3]*0.5-4))
                
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
                    
                    plotting_area_height = self.graph_rect[3] - self.frame_size * 2 - self.blank_area_in_middle_height
                    y_position_before = y_position_here
                    if i == 0:
                        y_position_here = (self.graph_rect[3] - self.frame_size) - (((prices[i] - ylim[0]) / ( ylim[1] - ylim[0])) * plotting_area_height )
                    else:
                        y_position_here = y_position_next
                    
                    if i == len(prices)-1:
                        y_position_next = self.graph_rect[3] - self.frame_size
                    else:
                        y_position_next = (self.graph_rect[3] - self.frame_size) - (((prices[i+1] - ylim[0]) / ( ylim[1] - ylim[0])) * plotting_area_height )
                    
                    x_length = int((self.graph_rect[3]) * math.log10(quantities[i]) / math.log10(xlim[1]) ) 
                    
                    if ((prices[i] - ylim[0]) / ( ylim[1] - ylim[0])) > 0.5: #ie if this is a sell offer
                        y_position_here = y_position_here - self.blank_area_in_middle_height
                    pygame.draw.line(market_analysis_surface,(50,50,50),(0,y_position_here),(x_length,y_position_here))
                    
                    #making positional database for linking clicking on the graph
                    max_width_of_selection_area = 10
                    top_border_length = min((y_position_here - y_position_before)/2,max_width_of_selection_area)
                    bottom_border_length = min((y_position_next - y_position_here)/2,max_width_of_selection_area)
                    top_border = y_position_here - top_border_length + self.graph_rect[1]
                    height = top_border_length + bottom_border_length
                    if height == 0: height = 1
                    left_border = self.graph_rect[0]
                    width = x_length
                    #debugging_info = "exact y_pos: " + str(y_position_here + self.rect[1] + 21) + " top border: +" + str(top_border_length) + " bottom border: -" + str(bottom_border_length) 
                    self.positional_database["non_bidding_mode"][(left_border,top_border,width,height)] = {"linkto":provider[i],"text":provider[i].name + ": " + "%.5g" % prices[i],"figure":((left_border,y_position_here + self.graph_rect[1]),(left_border + width,y_position_here + self.graph_rect[1]))}
                
                
                #making x-axis scale
                x_axis_vertical_position_percent_of_frame = 0.9 # in percent of lower frame where 1 is at top of frame
                x_axis_vertical_position = self.graph_rect[3]-int(self.frame_size*x_axis_vertical_position_percent_of_frame)
                pygame.draw.line(market_analysis_surface,(0,0,0),(0,x_axis_vertical_position),(self.graph_rect[2],x_axis_vertical_position),3)
                pygame.draw.line(market_analysis_surface,(0,0,0),(0,self.graph_rect[3] - x_axis_vertical_position),(self.graph_rect[2],self.graph_rect[3] - x_axis_vertical_position),3)
                pygame.draw.line(market_analysis_surface,(0,0,0),(0,x_axis_vertical_position),(0,self.graph_rect[3] - x_axis_vertical_position),3)
                pygame.draw.line(market_analysis_surface,(0,0,0),(self.graph_rect[2],x_axis_vertical_position),(self.graph_rect[2],self.graph_rect[3] - x_axis_vertical_position),3)
                max_x_axis_mark = 10 ** math.floor(math.log10(max_quantity)) #the value of the maximal x-axis mark. If eg. max_quantity is 1021, the max_x_axis_mark is 10^4
                if (max_quantity / max_x_axis_mark) < 6: # because then there is no room for the "units" marker
                    max_x_axis_mark = max_x_axis_mark / 10
                max_x_axis_mark_pos = int((self.graph_rect[3]) * math.log10(max_x_axis_mark) / math.log10(xlim[1]) )
                mark_height = self.graph_rect[3] / 50
                for i in range(0,10): #iterating "downwards" so to speak, because the x_mark_line will give the lineage of 10fold lower marks
                    x_mark_here = int(max_x_axis_mark / (10**i))
                    if x_mark_here < 10: #we stop the show at 10
                        break
                    x_pos_here = int((self.graph_rect[3]) * math.log10(x_mark_here) / math.log10(xlim[1]) )
                    pygame.draw.line(market_analysis_surface,(0,0,0),(x_pos_here,x_axis_vertical_position + mark_height/2),(x_pos_here,x_axis_vertical_position - mark_height/2))
                    x_mark_label_text = "10^"+str(int(math.log10(x_mark_here)))
                    if i == 0:
                        x_mark_label_text = x_mark_label_text + " units"  
                    x_mark_label = global_variables.standard_font.render(x_mark_label_text,True,(0,0,0))
                    market_analysis_surface.blit(x_mark_label,(x_pos_here-self.graph_rect[2]/100,x_axis_vertical_position + (mark_height)))
                    if market_analysis_surface is None:
                        raise Exception("At the end of the market_analysis_surface section, the surface had become None")
                
        return market_analysis_surface
                
        

            


    def update_data_history(self):
        history_surface = pygame.Surface((self.graph_rect[2],self.graph_rect[3]))
        history_surface.fill((212,212,212))
        resource = self.resource_selected

        #determining which market to look at. If in base mode it is obvious which. In firm for non-merchants it is home city, and for merchant it should be selectable
        if self.solar_system_object_link.display_mode == "base":
            market = self.solar_system_object_link.current_planet.current_base.market
        elif self.solar_system_object_link.display_mode == "firm":
            firm_selected = self.solar_system_object_link.firm_selected
            if firm_selected.isMerchant():
                market = self.base_selected_for_merchant.market
            else:
                market = firm_selected.location.market
        else:
            raise Exception("The display mode " + str(self.solar_system_object_link.display_mode) + " is not supposed to show market data")

        if len(market["transactions"][resource])==0:
            no_history_label = global_variables.standard_font.render("No " + resource + " sold on market",True,(0,0,0))
            history_surface.blit(no_history_label,(0,self.graph_rect[3]*0.5-4))
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
                x_position = int(self.frame_size + ((self.graph_rect[2]-self.frame_size*2) * (dates[i] - xlim[0])) / (xlim[1]-xlim[0]))
                y_position = int(self.graph_rect[3] - (self.frame_size + ( (self.graph_rect[3]-self.frame_size*2) * (price[i] - ylim[0]) / (ylim[1]-ylim[0]) )))
                try: dot_size = int(math.log10(quantity[i]))
                except:
                    dot_size = 1
                pygame.draw.circle(history_surface,(0,0,0),(x_position,y_position),dot_size)
                
                
                left_border = x_position + self.graph_rect[0] - dot_size
                top_border = y_position + self.graph_rect[1] - dot_size 
                if seller[i] is not None and buyer[i] is not None: #can happen with the empty startup transactions
                    self.positional_database["non_bidding_mode"][(left_border,top_border,2*dot_size,2*dot_size)] = {"linkto":seller[i],"text":str(seller[i].name) + " to " + str(buyer[i].name) + ": 10^" + str(dot_size) + "units","figure":((dot_size),(x_position + self.graph_rect[0],y_position + self.graph_rect[1])),"debug":left_border- dot_size}

            if len(price) != len(quantity) or len(price) != len(dates):
                raise Exception("DEBUGGING WARNING: There is a problem with unequal length in the markethistoryplotter")
                    
        return(history_surface)





    def make_manual_bid(self,initial_price = None,initial_quantity = None):
        """
        Function that will give the player the option to place a manual bid.
        First pre-selected parameters for resource-choice, initial choice and range of price, intial choice and range of quantity
        #transaction-direction (buy or sell), and for location choices (for merchants) are choosen. 
        """
        
        self.graph_selected = "place bid mode"
        resource = self.resource_selected
        
        if self.solar_system_object_link.display_mode == "base":
            firm_selected = self.solar_system_object_link.current_planet.current_base
        elif self.solar_system_object_link.display_mode == "firm":
            firm_selected = self.solar_system_object_link.firm_selected
        else:
            raise Exception("The display mode " + str(self.solar_system_object_link.display_mode) + " is not supposed to show market data")
        
        

        
        #seller or buyer
        if firm_selected.isMerchant():
            if self.base_selected_for_merchant == firm_selected.from_location:
                direction = "buy"
            else:
                direction = "sell"
        elif firm_selected.isBaseConstruction():
            direction = "buy"
        elif resource in firm_selected.input_output_dict["input"].keys():
            direction = "buy"
        elif resource in firm_selected.input_output_dict["output"].keys():
            direction = "sell"
        else:
            raise Exception("Oddly the resource " + str(resource) + " was neither found in the input or output of " + str(firm_selected.name)) 
        
        
        
        
        #quantity
        quantity_max = 0
        if direction == "sell": #in this case we are mostly interested in the stock
            #sell quantity
            if firm_selected.isMerchant():
                if self.base_selected_for_merchant == firm_selected.from_location:
                    quantity_max = max(quantity_max, firm_selected.from_stock_dict[resource])
                elif self.base_selected_for_merchant == firm_selected.to_location:
                    quantity_max = max(quantity_max, firm_selected.to_stock_dict[resource])
                else:
                    raise Exception("The self.base_selected_for_merchant " + str(self.base_selected_for_merchant.name) + " was neither in the from or the to_location of " + str(firm_selected.name))
            else:
                quantity_max = max(quantity_max, firm_selected.stock_dict[resource])
                

        else:
            #buy quantity
            if firm_selected.isMerchant():
                quantity_max = max(quantity_max, (firm_selected.from_location.population + firm_selected.to_location.population) / 2) 
            else:
                quantity_max = max(quantity_max, firm_selected.input_output_dict["input"][resource] * 50)


        if initial_quantity is not None:
            quantity_max = max(initial_quantity, quantity_max)
             
            
        if firm_selected.isBaseConstruction():
            quantity_max = firm_selected.input_output_dict["input"][resource]

        if initial_quantity is None:
            initial_quantity = quantity_max

        
        quantity_max = int(quantity_max)
        quantity_range = (0,quantity_max)

        if initial_quantity is not None:
            pre_selected_quantity = int(initial_quantity)
        else:
            pre_selected_quantity = int(quantity_max / 2)
        
        #marketsetting
        if firm_selected.isMerchant():
            market = self.base_selected_for_merchant.market
        else:
            market = firm_selected.location.market
            
        
            
        
        max_price = 0
        
        if initial_price is not None:
            max_price = max(initial_price, max_price)
    
        if len(market["buy_offers"][resource]) > 0:
            max_price = max(market["buy_offers"][resource][0]["price"], max_price)

        for transaction in market["transactions"][resource]:
            max_price = max(max_price, transaction["price"])
        
            
        price_range = (0,int(max_price * 2))    
        
        
#        print "initial_quantity: " + str(initial_quantity)
#        print "quantity_range: " + str(quantity_range)
#        print "initial_price: " + str(initial_price)
#        print "price_range: " + str(price_range)
        
        
        pygame.draw.rect(self.action_surface,(212,212,212),self.graph_rect)
        height_to_draw = 10
        
        
        
        #row 1 set the price
        fixed_price_text = global_variables.standard_font.render("Set the price:",True,(0,0,0))
        self.action_surface.blit(fixed_price_text, (self.graph_rect[0], self.graph_rect[1] + height_to_draw))
        price_rect = pygame.Rect(self.graph_rect[0] + fixed_price_text.get_width(), self.graph_rect[1] + height_to_draw,self.graph_rect[2] - fixed_price_text.get_width(),fixed_price_text.get_height())
        variable_price_text = global_variables.standard_font.render(str(int(initial_price)),True,(0,0,0))
        self.action_surface.blit(variable_price_text, (price_rect[0], price_rect[1]))
        
        
        def price_execute(label, price_rect):
            pygame.draw.rect(self.action_surface,(212,212,212),price_rect)
            variable_price_text = global_variables.standard_font.render(str(self.price_bar.position),True,(0,0,0))
            self.action_surface.blit(variable_price_text, (price_rect[0], price_rect[1]))
            pygame.display.update(price_rect)
            
        if price_range[0] > int(initial_price) or int(initial_price) > price_range[1]:
            print int(max_price)
            print price_range
            raise Exception("This has been observed before... check print outs")
        
        
        self.price_bar = gui_components.hscrollbar(self.action_surface, 
                                  price_execute, 
                                  (self.graph_rect[0] + 10, self.graph_rect[1] + height_to_draw + 20), 
                                  self.graph_rect[2]-20, 
                                  price_range, 
                                  start_position = int(max_price), 
                                  function_parameter=price_rect)



        #row 2 set the quantity
        height_to_draw = height_to_draw + 60
        
        fixed_quantity_text = global_variables.standard_font.render("Set the quantity:",True,(0,0,0))
        self.action_surface.blit(fixed_quantity_text, (self.graph_rect[0], self.graph_rect[1] + height_to_draw))
        quantity_rect = pygame.Rect(self.graph_rect[0] + fixed_quantity_text.get_width(), self.graph_rect[1] + height_to_draw,self.graph_rect[2] - fixed_quantity_text.get_width(),fixed_quantity_text.get_height())
        variable_quantity_text = global_variables.standard_font.render(str(initial_quantity),True,(0,0,0))
        self.action_surface.blit(variable_quantity_text, (quantity_rect[0], quantity_rect[1]))
        

        
        def quantity_execute(label, quantity_rect):
            pygame.draw.rect(self.action_surface,(212,212,212),quantity_rect)
            variable_quantity_text = global_variables.standard_font.render(str(self.quantity_bar.position),True,(0,0,0))
            self.action_surface.blit(variable_quantity_text, (quantity_rect[0], quantity_rect[1]))
            pygame.display.update(quantity_rect)

        self.quantity_bar = gui_components.hscrollbar(self.action_surface, 
                                  quantity_execute, 
                                  (self.graph_rect[0] + 10, self.graph_rect[1] + height_to_draw + 20), 
                                  self.graph_rect[2]-10, 
                                  quantity_range, 
                                  start_position = pre_selected_quantity, 
                                  function_parameter=quantity_rect)


        

        
        #row 3: direction info
        height_to_draw = height_to_draw + 50
        direction_text  = global_variables.standard_font.render("Transaction type:",True,(0,0,0))
        self.action_surface.blit(direction_text, (self.graph_rect[0], self.graph_rect[1] + height_to_draw))
        
        def direction_execute(label, function_parameter):
#            print "direction"
#            print label
#            print function_parameter
            pass
            
        
        self.direction_buttons = gui_components.radiobuttons(["buy","sell"],
                                   self.action_surface, 
                                   direction_execute,
                                   function_parameter = None, 
                                   topleft = (self.graph_rect[0] + 10, self.graph_rect[1] + height_to_draw + 20), 
                                   selected = direction)
        
        
     

        #effectuate buttons
        self.ok_button = gui_components.button("ok", 
                                                self.action_surface,
                                                self.effectuate_market_bid, 
                                                function_parameter = market, 
                                                fixed_size = (100,35), 
                                                topleft = (self.graph_rect[0] + self.graph_rect[2] - 110, self.graph_rect[1] + self.graph_rect[3] - 40)
                                                )


        


    def effectuate_market_bid(self, label, market):
        """
        Function that will check if the given numbers are ok, and if so effectuate the market bid
        """
        
#        all_ok = True
        if self.solar_system_object_link.display_mode == "base":
            firm_selected = self.solar_system_object_link.current_planet.current_base
        elif self.solar_system_object_link.display_mode == "firm":
            firm_selected = self.solar_system_object_link.firm_selected
        else:
            raise Exception("The display mode " + str(self.solar_system_object_link.display_mode) + " is not supposed to show market data")
        price = self.price_bar.position
        quantity = self.quantity_bar.position
        
        #determining direction
        direction = self.direction_buttons.selected
        
        #determining resource
        resource = self.resource_selected
        
        #determining unit
        unit = self.solar_system_object_link.trade_resources[resource]["unit_of_measurment"]
        
        if direction == "buy":
            if price * quantity > firm_selected.owner.capital:
                print_dict = {"text":"Too low capital to bid for " + str(quantity) + " " + str(unit) + " of " + str(resource) + " at price " + str(price),"type":"general gameplay info"}
                self.solar_system_object_link.messages.append(print_dict)
                return
            own_offer = {"resource":resource,"price":float(price),"buyer":firm_selected,"name":firm_selected.name,"quantity":int(quantity),"date":self.solar_system_object_link.current_date}
        elif direction == "sell":
            if firm_selected.isMerchant():
                if market == firm_selected.from_location.market:
                    quantity_available = firm_selected.from_stock_dict[resource]
                elif market == firm_selected.to_location.market:
                    quantity_available = firm_selected.to_stock_dict[resource]
                else:
                    raise Exception("Unknown direction for merchant type firm")
            else:
                quantity_available = firm_selected.stock_dict[resource]
            if quantity > quantity_available:
                print_dict = {"text":firm_selected.name + " only has " + str(firm_selected.stock_dict[resource]) + " " + str(unit) + " and can't offer " + str(quantity) + " for sale","type":"general gameplay info"}
                self.solar_system_object_link.messages.append(print_dict)
                return
            own_offer = {"resource":resource,"price":float(price),"seller":firm_selected,"name":firm_selected.name,"quantity":int(quantity),"date":self.solar_system_object_link.current_date}
        else:
            raise Exception("Unknown direction " + str(direction))
        
        firm_selected.make_market_bid(market,own_offer)
        
        print_dict = {"text":firm_selected.name + " succesfully made a " + str(direction) + " bid for " + str(quantity) + " " + str(unit) + " of " + str(resource) + " at price " + str(price),"type":"general gameplay info"}
        self.solar_system_object_link.messages.append(print_dict)
        self.graph_selected = "market bids"
        return "clear"


                    


        
    def receive_click(self,event):
        """
        Function that will take the position of a mouse click and check if any market-window variables (either history or market bids)
        are present at that position. If so, it will highlight these with further info on first click and provide a link on second click
        """ 
        #transposing position to take the main window rect into account

        position = event.pos
        if self.graph_rect.collidepoint(position) == 1:
            if self.graph_selected == "place bid mode": #if we are in bidding mode
                
                if self.price_bar.rect.collidepoint(position) == 1:
                    self.price_bar.activate(position)
                if self.quantity_bar.rect.collidepoint(position) == 1:
                    self.quantity_bar.activate(position)
                if self.direction_buttons.rect.collidepoint(position) == 1:
                    self.direction_buttons.activate(position)
                if self.ok_button.rect.collidepoint(position) == 1:
                    return self.ok_button.activate(position)


            
            
            else: #if we are in history or market mode
                if self.bidding_mode: #if the graphs accept bids we start the bidding sections up
                    
                    if self.graph_selected == "market bids":
                        top_of_plot = self.rect[1] + self.frame_size  + 21
                        self.blank_area_in_middle_height
                        y_position =  position[1] - top_of_plot
                        if y_position > (self.graph_rect[3] - 2 * self.frame_size) / 2 + self.blank_area_in_middle_height/2:
                            y_position = y_position - self.blank_area_in_middle_height #more than half - correct and move on
                        elif y_position > (self.graph_rect[3] - 2 * self.frame_size) / 2 - self.blank_area_in_middle_height/2:
                            return None #Hit half - don't continue
                        height_of_plot = self.graph_rect[3] - 2 * self.frame_size - self.blank_area_in_middle_height 
                        y_relative_position = 1.0 - (y_position / float(height_of_plot))
                    else: #in history graph
                        y_relative_position =  ((self.graph_rect[3] - self.frame_size) - (position[1] - self.rect[1] - 21)) / float(self.graph_rect[3] - self.frame_size)
        
        
                    
        
                    x_relative_position =  (position[0] - self.rect[0] - 150) / float(self.graph_rect[2])
                    if 0 < x_relative_position < 1:
                        if 0 < y_relative_position < 1:
                            if "price" in self.positional_database["bidding_mode"].keys():
                                min_price = self.positional_database["bidding_mode"]["price"][0]
                                max_price = self.positional_database["bidding_mode"]["price"][1]
                                price = y_relative_position * (max_price - min_price) + min_price
                                if price < 0:
                                    price = 0
                                    if self.solar_system_object_link.message_printing["debugging"]:
                                        print_dict = {"text":"Changed price from " + str(price) + " to 0","type":"debugging"} 
                                        self.solar_system_object_link.messages.append(print_dict)

                            else:
                                price = None
                                
                            if "quantity" in self.positional_database["bidding_mode"].keys():
                                max_qt = self.positional_database["bidding_mode"]["quantity"][1]
                                try:    math.log10(max_qt)
                                except: 
                                    if self.solar_system_object_link.message_printing["debugging"]:
                                        print_dict = {"text":"DEBUGGING: no good selection of log10 max_qt","type":"debugging"} 
                                        self.solar_system_object_link.messages.append(print_dict)
                                    quantity = None
                                else:
                                    quantity = int(10 ** (math.log10(max_qt) * x_relative_position))  
                            else:
                                quantity = None
                        
#                            print "click at " + str((x_relative_position,y_relative_position)) + " gives price: " + str(price) + " and qt: " + str(quantity)
                            self.make_manual_bid(price,quantity)
                                
    
                else:  #if the graphs do not accept bids we only display some information
                    click_spot = pygame.Rect(position[0]-1,position[1]-1 ,2,2)
                    click_spot_result = click_spot.collidedict(self.positional_database["non_bidding_mode"])
                    if click_spot_result is not None:
                        if event.button == 3:
                            if not click_spot_result[1]["linkto"].isBase():
                                linkto = click_spot_result[1]["linkto"]
                                if linkto.isBase():
                                    self.solar_system_object_link.display_mode = "base"
                                    self.solar_system_object_link.current_planet.current_base = linkto
                                elif linkto.isFirm() or linkto.isMerchant() or linkto.isResearch():
                                    self.solar_system_object_link.display_mode = "firm"
                                    self.solar_system_object_link.firm_selected = linkto
                                else:
                                    raise Exception("The class of " + linkto.name + " was " + linkto.__class__)
                                return "clear"
                        else:
                            self.highlighted_transactions.append(click_spot_result[1])
                            
                            text_size = global_variables.standard_font_small.size(click_spot_result[1]["text"]) 
                            text = global_variables.standard_font_small.render(click_spot_result[1]["text"],True,(0,0,0))
                            
                            text_position = (click_spot_result[1]["figure"][1][0]-text_size[0] / 2,click_spot_result[1]["figure"][1][1])
                            
                            if text_position[0] < self.graph_rect[0] + self.frame_size:
                                text_position = (self.graph_rect[0] + self.frame_size, text_position[1])
                            if text_position[0] + text_size[0] > self.graph_rect[0] + self.graph_rect[2]:
                                text_position = (self.graph_rect[0] + self.graph_rect[2] - text_size[0], text_position[1])

                            
                            self.action_surface.blit(text,text_position)
                            
                            if self.graph_selected == "market bids":
                                pygame.draw.line(self.action_surface,(100,100,255),click_spot_result[1]["figure"][0],click_spot_result[1]["figure"][1])
                            elif self.graph_selected == "history":
                                pygame.draw.circle(self.action_surface,(100,100,255),click_spot_result[1]["figure"][1],click_spot_result[1]["figure"][0])
                            else:
                                raise Exception("Unknown graph type " + self.graph_selected)
        
                            pygame.display.flip()


                            
        else: #if the click is elsewhere than the graph window
            if self.graph_selected != "place bid mode":
                if self.update_button.rect.collidepoint(event.pos) == 1:
                    self.update_button.activate(event.pos)
                if self.resource_buttons.rect.collidepoint(event.pos) == 1:
                    self.resource_buttons.activate(event.pos)
                if self.graph_buttons.rect.collidepoint(event.pos) == 1:
                    self.graph_buttons.activate(event.pos)
                if "activate" in dir(self.market_selection_buttons):
                    if self.market_selection_buttons.rect.collidepoint(event.pos) == 1:
                        self.market_selection_buttons.activate(event.pos)
                if "activate" in dir(self.bid_button):
                    if self.bid_button.rect.collidepoint(event.pos) == 1:
                        self.bid_button.activate(event.pos)
            
            
            
                    
            


