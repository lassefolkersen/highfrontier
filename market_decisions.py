from . import global_variables
import datetime
from . import primitives
import random
import string
from . import company




class market_decisions:
    """
    Class that holds all the algorithms pertaining to market decision.
    The class consists of self dictionaries, organized by theme:
        pick_reseach
        start_research_firms
        evaluate_commodities_market
        evaluate_assets_market
        evaluate_tech_market
        
        evaluate_firms
        calculate_supply_reaction
        calculate_demand_reaction
        
    
    Each dictionary should have a number between 1 and len(self) as keys, and a function as value
    
    Note that all functions have (market_decision_class,self,...) instead of (self,...). That is because
    the functions themselves will be shipped somewhere else, and so the market_decisions class is not used
    as a conventional .self.
    
    Yes it is quite possible that it would have been easier to put the function under firm and company classes
    respectively but I think this keeps it cleaner, when the "variable" parts are apart.
    """
    
    def __init__(self):
        """
        Loads the algorithms as specified
        """
        self.pick_research = {1:self.pick_research_01}
        self.start_research_firms = {1:self.start_research_firms_01}
        self.evaluate_commodities_market = {1:self.evaluate_commodities_market_01}
        self.evaluate_asset_market = {1:self.evaluate_asset_market_01}
        self.evaluate_tech_market = {1:self.evaluate_tech_market_01}
        self.evaluate_intercity_trade_market = {1:self.evaluate_intercity_trade_market_01}
        self.evaluate_expansion_opportunities = {1:self.evaluate_expansion_opportunities_01}
        self.evaluate_firms = {1:self.evaluate_firms_01}
        self.calculate_demand_reaction = {1:self.calculate_demand_reaction_01,2:self.calculate_demand_reaction_02,3:self.calculate_demand_reaction_03,4:self.calculate_demand_reaction_04}
        self.calculate_intercity_demand = {1:self.calculate_intercity_demand_01}
        self.calculate_supply_reaction = {1:self.calculate_supply_reaction_01,2:self.calculate_supply_reaction_02,3:self.calculate_supply_reaction_03}
        self.calculate_intercity_supply = {1:self.calculate_intercity_supply_01}
    
    
    
    
    
    
    
    
    def pick_research_01(market_decision_class,self):
        """
        Function that is executed whenever the self.target_technology is None
        Will change the self.target_technology to a new aim
        
        This flavour just picks a random technology
        """
        if len(self.known_technologies) == 0:
#            print 
            if self.solar_system_object_link.message_printing["debugging"]:
                print_dict = {"text":"WARNING: the " + str(self.name) + " does not know any technologies to begin with. This must be a mistake","type":"debugging"}
                self.solar_system_object_link.messages.append(print_dict)

        else:
            destination = None
            i = 0
            while destination is None:
                chosen_origination_point_name = random.choice(list(self.known_technologies.keys()))
                chosen_origination_point = self.solar_system_object_link.technology_tree.vertex_dict[chosen_origination_point_name]
                destination = self.solar_system_object_link.technology_tree.get_research_project(chosen_origination_point_name,self.known_technologies)
                i = i +1
                if i > 50:
                    if self.solar_system_object_link.message_printing["debugging"]:
                        print_dict = {"text":"WARNING: It does not seem like there are any technologies left to research for " + str(self.name) + " perhaps use the implode_and_expand function?","type":"debugging"}
                        self.solar_system_object_link.messages.append(print_dict)

                    break
            if destination is not None:
                self.target_technology = destination["target_technology"]
                self.target_technology_cost = int(destination["distance"] * self.solar_system_object_link.technology_research_cost)
    
    
    def start_research_firms_01(market_decision_class,self):
        """
        Evaluates the research activities of the company and decides if new research companies should be started.
        It returns the number of firms that has been started.
        
        This flavour just makes sure the firm volume is divided between research and non-research as specified in company database
        
        FIXME include function to close down research
        """
        #determining if research is ok:
        research_volume = 0
        non_research_volume = 0
        for firm_instance in list(self.owned_firms.values()):
            if isinstance(firm_instance, company.research):
                research_volume = research_volume + firm_instance.size
                
            else:
                non_research_volume = non_research_volume + firm_instance.size
        
        
        if float(research_volume + non_research_volume) > 0:
            research_ratio = float(research_volume) / float(research_volume + non_research_volume)
        else:
            research_ratio = 100 #because we don't want companies to start research immediatly 
             
        if research_ratio < self.company_database["desired_research"]:
            #determine location (this can be expanded a lot)
            home_city_names = list(self.home_cities.keys())
            
            try:    location_choice_name = random.choice(home_city_names)
            except: 
                print(self.name)
                print(self.home_cities)
                raise Exception("This bug has been observed before and probably results from a company not having any home_cities")
            
            location_choice = self.home_cities[location_choice_name]
            
            desired_research_size = (research_volume + non_research_volume) * self.company_database["desired_research"] 
            desired_research_size_increase = (int(desired_research_size) - research_volume) / 100
            
            if desired_research_size_increase < 0:
                print(desired_research_size_increase)
                raise Exception("The desired_research_size_increase is negative")
            elif desired_research_size_increase == 0:
                #do nothing
                pass
            else:
                self.change_firm_size(location_choice,desired_research_size_increase,"research")
#                    print "at " + str(location_choice.name) + ", " + self.name + " started a research firm of size " + str(desired_research_size_increase)


    
    
    def evaluate_commodities_market_01(market_decision_class,self):
        """
        Function that evaluates the commodity markets of all the self.home_cities and decides if any
        new firms should be opened. 
        """
        quickness_to_start_firm = (101 - self.company_database["quickness_to_start_firm"])/ 20.0  # ratio of buy_offers to sell_offers at which a new firm will be started
        size_of_started_firm = self.company_database["size_of_started_firm"] / 100.0 # decision of the scaling factor of the size of a new-started firm. If one, it will match the output to the quantity currently sought on the market

#        available_processes = self.get_available_processes()
        
        current_date = self.solar_system_object_link.current_date
        
        
        #first we iterate on all possible goods that can be sold in a given market
        for base in list(self.home_cities.values()):
            for resource in base.market["buy_offers"]:
                useful_processes = {}
                for process_name in self.known_technologies:
                    process = self.known_technologies[process_name]["input_output_dict"]
                    if resource in list(process["output"].keys()):
                        output_volume = 0
                        for resource_here in process["output"]:
                            output_volume = process["output"][resource_here] + output_volume
                        input_volume = 0
                        for resource_here in process["input"]:
                            input_volume = process["input"][resource_here] + input_volume
                        
                        useful_processes[float(output_volume) / float(input_volume)] = process_name
                
                #if any useful processes are found, we prioritize them and select the one with highest input / output ratio
                if len(useful_processes) > 0:
                    useful_processes_keys = list(useful_processes.keys()) 
                    useful_processes_keys.sort()
                    chosen_process_name = useful_processes[useful_processes_keys[-1]]
                    process_here = self.known_technologies[chosen_process_name]["input_output_dict"]
                    quantity_wanted_on_market = 0
                    for offer in base.market["buy_offers"][resource]:
                        quantity_wanted_on_market = offer["quantity"] + quantity_wanted_on_market

                    #it is a problem if the quantity wanted is too big, because then the firms created will be so huge that they can never get started therefore this:
                    quantity_wanted_on_market = min(quantity_wanted_on_market, base.population)
                                
                    decided_scaling_factor = int(int(quantity_wanted_on_market / (process_here["output"][resource])) * size_of_started_firm * (random.random() * 0.90 + 0.1))
                                
                    self.change_firm_size(base,decided_scaling_factor,chosen_process_name)
                    





    
    def evaluate_asset_market_01(market_decision_class,self):
        """
        Function that evaluates assets (firms, bases etc) to buy
        """
        
        neighbours = []
        for home_city_instance in list(self.home_cities.values()):
            if home_city_instance not in neighbours:
                neighbours.append(home_city_instance)
            for trade_route in list(home_city_instance.trade_routes.values()):
                for endpoint_instance in trade_route["endpoint_links"]:
                    if endpoint_instance != home_city_instance:
                        if endpoint_instance not in neighbours:
                            neighbours.append(endpoint_instance)

        
        
        potential_bases_to_buy = []
        for neighbour in neighbours:
            if neighbour.owner != self:
                if neighbour.for_sale:
                    potential_bases_to_buy.append(neighbour)
        
        for potential_base_to_buy in potential_bases_to_buy:
            if potential_base_to_buy.is_on_dry_land == "Yes":
                dry_term = 1
            else:
                dry_term = 0.01
                
            mining_values = []
            for resource in potential_base_to_buy.mining_opportunities:
                mining_opportunity = potential_base_to_buy.mining_opportunities[resource]
                price_of_resource = []
                
                for neighbour in neighbours:
                    try: neighbour.market["buy_offers"][resource]
                    except: pass
                    else:
                        if len(neighbour.market["buy_offers"][resource]) > 0:
                            price_of_resource.append(neighbour.market["buy_offers"][resource][0]["price"])
                if len(price_of_resource) > 0:
                    mean_price_of_resource = sum(price_of_resource) / len(price_of_resource)
                    value = mining_opportunity * mean_price_of_resource
                    mining_values.append(value)
            mining_value_term = sum(mining_values)
                
            population_term = potential_base_to_buy.population
            
            company_term = self.company_database["buy_out_tendency"]
                
            base_value = int(dry_term * mining_value_term * population_term * company_term * 0.00000001)
            
            if base_value > 0:
                if self.capital > base_value: 
                    potential_base_to_buy.for_sale_bids[self] = base_value

            


    def evaluate_tech_market_01(market_decision_class,self):
        """
        Function that evaluates assets technologies to buy and sell
        
        This flavour tries to set a selling price for technology by calculating how much labor it cost to get it.
        If there is tech for sale and it is affordable it will be bought with this algorithm
        improvement suggestions FIXME:
            take into account how advanced the technology is when calculating selling price
            don't stop the function just because there is no labor price in selling price

        """
        sell_tech = random.randint(1,100) < 4 #FIXME opportunity for tuningparameter ("how often to check for tech sales")
        buy_tech = random.randint(1,100) < 10 #FIXME opportunity for tuningparameter ("how often to check for tech buys")    
        
#        basic_research_technology = self.solar_system_object_link.technology_tree.vertex_dict["basic research"] #FIXME perhaps one day include a check to see if this is the best research tech

        if sell_tech:
            #first we calculate the mean price of labor, since this is what the price of the tech is based on 
            labor_prices = []
            for base_instance in list(self.home_cities.values()):
                labor_price_here = None
                try:    base_instance.market["sell_offers"]["labor"]
                except: pass 
                else:
                    if len(base_instance.market["sell_offers"]["labor"]) > 0:
                        labor_price_here = base_instance.market["sell_offers"]["labor"][0]["price"]
                if labor_price_here is None:
                    try:    base_instance.market["buy_offers"]["labor"]
                    except: pass
                    else:
                        if len(base_instance.market["buy_offers"]["labor"]) > 0:
                            labor_price_here = base_instance.market["buy_offers"]["labor"][0]["price"]
                if labor_price_here is not None:
                    labor_prices.append(labor_price_here)
            if len(labor_prices) > 0:
                mean_labor_price = sum(labor_prices) / len(labor_prices)
    
                #calculate the research point per labor 
                research_point_per_labor = 1.0 #this is always one as specified in the research class

                for technology_name in self.known_technologies:
                    technology = self.known_technologies[technology_name]
                    #here we price the technology of something known by 10 others or more at the price of the labor that made it. More exotic techs are more expensive
                    if technology["known_by"] != "everybody":
                        known_by_number = len(technology["known_by"])
                        if known_by_number  > 10:
                            known_by_number  = 10
                        price = ((mean_labor_price / research_point_per_labor) * (self.solar_system_object_link.technology_research_cost / 1000) ) * ((known_by_number  - 9)**2)
                        print_dict = {"text":self.name + " considers selling " + technology_name + " for " + str(price),"type":"tech discovery"}
                        self.solar_system_object_link.messages.append(print_dict)

                        technology["for_sale_by"][self] = price
            if buy_tech:
                for technology in list(self.solar_system_object_link.technology_tree.vertex_dict.values()):

                    if len(technology["for_sale_by"]) > 0:
                        if technology["technology_name"] not in list(self.known_technologies.keys()):
                            prices = list(technology["for_sale_by"].values())
                            prices.sort()
                            winning_price = prices[-1]
                            inverted_prices = primitives.invert_dict(technology["for_sale_by"])
                            selling_company = inverted_prices[winning_price][0]

                            
                                                        
                            if winning_price < self.capital:
                                check_result = self.solar_system_object_link.technology_tree.check_technology_bid(self.known_technologies,technology)
                                if check_result == "ok":
                                    self.known_technologies[technology["technology_name"]] = technology
                                    self.capital = self.capital - winning_price
                                    selling_company.capital = selling_company.capital + winning_price
                                    if self == self.solar_system_object_link.current_player:
                                        print_dict = {"text":str(technology["technology_name"]) + " is not known by " + str(self.name) + ". It was bought from " + selling_company.name + " at a price of " + str(winning_price),"type":"tech discovery"}
                                        self.solar_system_object_link.messages.append(print_dict)




    def evaluate_intercity_trade_market_01(market_decision,self):
        """
        Function used to decide if and where merchant firms should be started.
        
        
        Improvement options: transportation costs are not taken into account
        """
        tendency_to_start_trade_routes = 101 - self.company_database["tendency_to_start_trade_routes"]


        #first we see what bases are already connected by the merchant firms of the company
        already_connected = []
        for firm_instance in list(self.owned_firms.values()):
            if isinstance(firm_instance, company.merchant):
                existing_pair = [firm_instance.from_location, firm_instance.to_location, firm_instance.resource]
                already_connected.append(existing_pair)
        
        
        for seller_base_name in self.home_cities:
            seller_base = self.home_cities[seller_base_name]
            for trade_route_name in seller_base.trade_routes:
                trade_route = seller_base.trade_routes[trade_route_name]
                for buyer_base in trade_route["endpoint_links"]:
                    if buyer_base != seller_base: #just makes sure that the non-"home"-base is chosen
                        if buyer_base.name in list(self.home_cities.keys()): #ok this proves that it is within the network of the company
                            
                            #finding out what the transportation costs are
                            transport_prices = []
                            for base_instance in [buyer_base,seller_base]:
                                if len(base_instance.market["sell_offers"][trade_route["transport_type"]]) > 0:
                                    transport_prices.append(base_instance.market["sell_offers"][trade_route["transport_type"]][0]["price"])
                            if len(transport_prices) > 0:
                                transport_unit_price = min(transport_prices)
                            else:
                                transport_unit_price = self.solar_system_object_link.trade_resources[trade_route["transport_type"]]["starting_price"]
                            transportation_cost = (transport_unit_price * trade_route["distance"]) / 1000.0 

                            
                            for resource in list(seller_base.market["sell_offers"].keys()):
                                if self.solar_system_object_link.trade_resources[resource]["transportable"]:
                                    connection = [seller_base,buyer_base,resource]
                                    if connection not in already_connected:
                                        if len(seller_base.market["sell_offers"][resource]) > 0 and len(buyer_base.market["buy_offers"][resource]) > 0:
                                            sellprice = seller_base.market["sell_offers"][resource][0]["price"]
                                            buyprice = buyer_base.market["buy_offers"][resource][0]["price"]
                                            profit_margin = sellprice - buyprice - transportation_cost
                                            if buyprice > 0:
                                                if (profit_margin / buyprice) > (tendency_to_start_trade_routes/100.0): #only consider the trade if the profit_margin is a higher percentage of the buyprice than the tendency to start trades
                                                    already_connected.append([seller_base,buyer_base,resource])
                                                    
                                                    name_is_not_unique = True
                                                    while name_is_not_unique:
                                                        name_is_not_unique = False
                                                        name = "merchant" + "_" + str(random.randint(10000,99999))
                                                        for company_instance in list(self.solar_system_object_link.companies.values()):
                                                            if name in list(company_instance.owned_firms.keys()):
                                                                name_is_not_unique = True
                                                    owner = self
                                                    input_output_dict = {"input":{},"output":{},"timeframe":30,"byproducts":{}}
                                                    distance = trade_route["distance"]
                                                    transport_type = trade_route["transport_type"]
                                                    new_merchant_firm = company.merchant(self.solar_system_object_link, seller_base,buyer_base,input_output_dict,owner,name,transport_type,distance,resource)
                                                    self.owned_firms[name] = new_merchant_firm
                                                    if self == self.solar_system_object_link.current_player:
                                                        print_dict = {"text":self.name + " started up a merchant between " + str(seller_base.name) + " and " + str(buyer_base.name),"type":"tech discovery"}
                                                        self.solar_system_object_link.messages.append(print_dict)

    
    

    def evaluate_expansion_opportunities_01(market_decision_class,self):
        """
        Function that evaluates the home_cities of the company and decide if they should be expanded 
        """
        
        if random.randint(0,10) == 1:
            new_home_city = self.expand_home_cities(self.solar_system_object_link)
            if new_home_city == None:
                pass
            else:
                self.home_cities[new_home_city.name] = new_home_city
        
        
    
    
    def evaluate_firms_01(market_decision_class,self):
        """
        Function that makes the company scan through all its owned firms,
        decide if any should be closed and effectuate that closing.
        """
        closing_firms_at_this_margin = -self.company_database["closing_firms_at_this_margin"] / 100.0 
        
        close_these_firms = []
        
        for firm_name in self.owned_firms:
            firm_instance = self.owned_firms[firm_name]
            if not isinstance(firm_instance,company.research): #do not close research firms here, since they will always give negative results (this is done in the start_research_firms function

                if isinstance(firm_instance,company.base):
                    #checking what to do with the base
                    if self.company_database["Target_bitterness_of_base"] < firm_instance.bitternes_of_base:
                        firm_instance.wages = firm_instance.wages * 1.1  
                        
                accounting_report =  firm_instance.update_accounting()
                if accounting_report["revenue"] > 0:
                    operating_margin = accounting_report["profit"] / accounting_report["revenue"]
                else:
                    operating_margin = 0
                if operating_margin < closing_firms_at_this_margin:
                    close_these_firms.append(firm_name)
        
        for firm_to_close in close_these_firms:
            if not isinstance(self.owned_firms[firm_to_close], company.base):
                self.owned_firms[firm_to_close].close_firm()
                del self.owned_firms[firm_to_close]
                
                
            else:
                #BASESALEPLACE
                self.owned_firms[firm_to_close].for_sale = True
                self.owned_firms[firm_to_close].for_sale_deadline = datetime.timedelta(30*6)+self.solar_system_object_link.current_date
        
    
    
    
    
         
        
    
    def calculate_demand_reaction_01(market_decision_class,self):
        """
        Function that will decide if a "buy" offer should be emitted, and at what price and quantity
        """
        market = self.location.market
        current_date = self.solar_system_object_link.current_date
        timeframe_considered = int(self.input_output_dict["timeframe"] * (self.owner.company_database["timeframe_considered"] / 20.0)) 
        
        
        for resource in self.input_output_dict["input"]:
            if self.input_output_dict["input"][resource]*timeframe_considered > self.stock_dict[resource]:
                if not isinstance(self, company.base_construction):
                    quantity_wanted = int(self.input_output_dict["input"][resource]*timeframe_considered - self.stock_dict[resource] ) + 1
                else:
                    quantity_wanted = self.input_output_dict["input"][resource] - self.stock_dict[resource]
                try: market["sell_offers"][resource][0]
                except:
                    price = float(random.randint(1,100)) 
                else:
                    price = float(market["sell_offers"][resource][0]["price"])
                if quantity_wanted * price <= self.owner.capital:
                    buy_offer = {"resource":resource,"price":float(price),"buyer":self,"name":self.name,"quantity":int(quantity_wanted),"date":current_date}
                    self.make_market_bid(market,buy_offer)
                    
    
    def calculate_demand_reaction_02(market_decision_class,self):
        """
        Function that will decide if a "buy" offer should be emitted, and at what price and quantity
        """
        market = self.location.market
        timeframe_considered = int(self.input_output_dict["timeframe"] * (self.owner.company_database["timeframe_considered"] / 20.0))
        current_date = self.solar_system_object_link.current_date
        for resource in self.input_output_dict["input"]:
            try: self.urgency
            except:
                self.urgency = {}
            try: self.urgency[resource]
            except:
                self.urgency[resource] = 1
    
            if self.stock_dict[resource] < self.input_output_dict["input"][resource] * timeframe_considered:
                if len(market["sell_offers"][resource]) > 0:
                    price = market["sell_offers"][resource][0]["price"]
                else:
                    price = 10 
                price = float(price * self.urgency[resource])
                self.urgency[resource] = self.urgency[resource] * 1.5
                
                if not isinstance(self, company.base_construction):
                    quantity_wanted = int(self.input_output_dict["input"][resource]) * timeframe_considered 
                else:
                    quantity_wanted = self.input_output_dict["input"][resource] - self.stock_dict[resource]

                if quantity_wanted * price > self.owner.capital:
                    quantity_wanted = int(self.owner.capital / price )
                
                quantity_wanted = int(quantity_wanted)
                
                if quantity_wanted > 1:
                    if quantity_wanted * price <= self.owner.capital:
                        if not (isinstance(quantity_wanted,int) or isinstance(quantity_wanted,int)):
                            if self.solar_system_object_link.message_printing["debugging"]:
                                print_dict = {"text":"DEBUGGING WARNING: in calculate_demand_reaction_02 quantity_wanted: " + str(quantity_wanted),"type":"debugging"}
                                self.solar_system_object_link.messages.append(print_dict)

                            
                        if quantity_wanted < 0:
                            if self.solar_system_object_link.message_printing["debugging"]:
                                print_dict = {"text":"DEBUGGING WARNING: in calculate_demand_reaction_02 quantity_is negative. VERY WEIRD","type":"debugging"}
                                self.solar_system_object_link.messages.append(print_dict)

                        
                        buy_offer = {"resource":resource,"price":float(price),"buyer":self,"name":self.name,"quantity":int(quantity_wanted),"date":current_date}
                        self.make_market_bid(market,buy_offer)
                        
            else:
                self.urgency[resource] = 1
    
    
    def calculate_demand_reaction_03(market_decision_class,self):
        """
        Function that will decide if a "buy" offer should be emitted, and at what price and quantity
        """
        market = self.location.market
        current_date = self.solar_system_object_link.current_date
        for resource in self.input_output_dict["input"]:
                prices = []
                for transaction in market["transactions"][resource]:
                    prices.append(transaction["price"])
                price = random.random() * (max(prices)-min(prices)) + min(prices)
                

                if not isinstance(self, company.base_construction):
                    quantity_wanted = int(self.input_output_dict["input"][resource] * (random.random()*2.0 + 0.5))    
                else:
                    quantity_wanted = self.input_output_dict["input"][resource] - self.stock_dict[resource]
                
                if quantity_wanted > 1:
                    if quantity_wanted * price <= self.owner.capital:
                        if quantity_wanted < 0:
                            if self.solar_system_object_link.message_printing["debugging"]:
                                print_dict = {"text":"DEBUGGING WARNING: in calculate_demand_reaction_03 quantity_is negative. VERY WEIRD","type":"debugging"}
                                self.solar_system_object_link.messages.append(print_dict)

                        
                        buy_offer = {"resource":resource,"price":float(price),"buyer":self,"name":self.name,"quantity":int(quantity_wanted),"date":current_date}
                        self.make_market_bid(market,buy_offer)
    
                    
    def calculate_demand_reaction_04(market_decision_class,self):
        """
        Function that will decide if a "buy" offer should be emitted, and at what price and quantity
        
        This flavor pays the price of a good in relation to how its much its output can be sold for
        """
        market = self.location.market
        current_date = self.solar_system_object_link.current_date
        timeframe_considered = int(self.input_output_dict["timeframe"] * (self.owner.company_database["timeframe_considered"] / 20.0)) 
        
        
        market_price_of_output = 0
        output_volume = 0
        for resource in self.input_output_dict["output"]:
            output_volume = self.input_output_dict["output"][resource] + output_volume
            try: market["buy_offers"][resource][0]
            except: pass
            else:
                market_price_of_output = market["buy_offers"][resource][0]["price"] * self.input_output_dict["output"][resource] + market_price_of_output
        
        chosen_price_of_input_total = market_price_of_output * (random.random() * 0.2 + 0.7) #FIXME this can be made genetical
        
        input_volume = 0
        for resource in self.input_output_dict["input"]:
            input_volume = self.input_output_dict["input"][resource] + input_volume
        
        if input_volume <= 0:
            print(input_volume)
            print(self.name)
            print(self.input_output_dict)
            raise Exception("Somehow the cumulative input of a process managed to be 0 or less")
        
        chosen_price_of_input_per_unit = chosen_price_of_input_total / input_volume
        
        for resource in self.input_output_dict["input"]:
            if self.input_output_dict["input"][resource]*timeframe_considered > self.stock_dict[resource]:
                
                if not isinstance(self, company.base_construction):
                    quantity_wanted = int(self.input_output_dict["input"][resource]*timeframe_considered - self.stock_dict[resource] ) + 1
                else:
                    quantity_wanted = self.input_output_dict["input"][resource] - self.stock_dict[resource] 

                
                try: market["sell_offers"][resource][0]
                except:
                    price = chosen_price_of_input_per_unit  
#                    print self.name + " used calculate_demand_reaction_04 to set a price of " + resource + " to " + str(int(price)) + " because the output could be sold for " + str(int(market_price_of_output)) + " - the input_volume is " + str(input_volume) + " and the output_volume is " + str(output_volume) + " so each output could be sold for " + str(int(market_price_of_output/output_volume)) 
                else:
                    price = float(market["sell_offers"][resource][0]["price"])

                if quantity_wanted * price <= self.owner.capital:
                    buy_offer = {"resource":resource,"price":float(price),"buyer":self,"name":self.name,"quantity":int(quantity_wanted),"date":current_date}
                    self.make_market_bid(market,buy_offer)




    def calculate_intercity_demand_01(market_decision_class,self):
        """
        Function that investigates what the merchant should buy 
        
        This flavour is a pretty simple variant of setting the price somewhere between the max and the min.
        And the quantity somewhere between 1 and the total amount needed at destination
        """
        
        
        from_market = self.from_location.market
        to_market = self.to_location.market
        current_date = self.solar_system_object_link.current_date
        resources = [self.resource, self.transport_type]
        
        for resource in resources:
            prices = []
            for transaction in from_market["transactions"][resource]:
                prices.append(transaction["price"])
            price = random.random() * (max(prices)-min(prices)) + min(prices)
    
            if resource == self.resource:
                quantity_wanted = 0
                for buy_offer in to_market["buy_offers"][resource]:
                    quantity_wanted = quantity_wanted + buy_offer["quantity"]
                quantity_wanted = int(quantity_wanted * random.random() + 1)
            else: #transportation
                transportation_needed = int((self.from_stock_dict[self.resource] * self.distance) / 1000.0)
                quantity_wanted = transportation_needed - self.from_stock_dict[self.transport_type]
                if self.owner == self.solar_system_object_link.current_player:
                    print_dict = {"text":"the transport quantity wanted was " + str(quantity_wanted) + " and self.from_stock_dict[self.resource] was " + str(self.from_stock_dict[self.resource]),"type":"firm info"}
                    self.solar_system_object_link.messages.append(print_dict)
            
            if quantity_wanted > 1:
                if quantity_wanted * price <= self.owner.capital:
                    if quantity_wanted < 0:
                        if self.solar_system_object_link.message_printing["debugging"]:
                            print_dict = {"text":"DEBUGGING WARNING: in calculate_demand_reaction_03 quantity_is negative. VERY WEIRD","type":"debugging"}
                            self.solar_system_object_link.messages.append(print_dict)

                    buy_offer = {"resource":resource,"price":float(price),"buyer":self,"name":self.name,"quantity":int(quantity_wanted),"date":current_date}
                    self.make_market_bid(from_market,buy_offer)
                    if self.owner == self.solar_system_object_link.current_player:
                        print_dict = {"text":self.name + " is buying " + resource + " at " + self.from_location.name + " at price " + str(int(price)) + " and qt " + str(quantity_wanted),"type":"firm info"}
                        self.solar_system_object_link.messages.append(print_dict)
    



    



    def calculate_supply_reaction_01(market_decision_class,self):
        """
        Function that will decide if a "sell" offer should be emitted, and at what price and quantity
        More functions like this can be made, but they should be renamed similarly, the calculate_demand_reaction() should be updated
        and the global_variables number_of_functions be updated
        """
        market = self.location.market
        tendency_to_sell_expensive = ((self.owner.company_database["tendency_to_sell_expensive"] - 50) / 100.0 ) + 1
        tendency_to_focus_on_history = ((self.owner.company_database["tendency_to_focus_on_history"] - 50) / 100.0) + 1
        
        current_date = self.solar_system_object_link.current_date
        for resource in self.input_output_dict["output"]:
            resource_level = self.stock_dict[resource]
            production_level = self.input_output_dict["output"][resource] 
            if production_level > 0:
                surplus_ratio = float(resource_level) / float(production_level)
                if surplus_ratio > 0:
                    past_prices = []
                    past_past_time_difference = []
                    transaction_history_length = current_date - market["transactions"][resource][-1]["date"]
                    transaction_history_length = transaction_history_length.days
                    
                    weighted_mean_numerator = 0.0
                    weighted_mean_denominator = 0.0
                    
                    for past_transactions in market["transactions"][resource]: 
                        past_time_difference = current_date - past_transactions["date"]
                        past_time_difference = past_time_difference.days
                        
                        
                        weight = abs(transaction_history_length - past_time_difference) ** tendency_to_focus_on_history
                        price = past_transactions["price"]
                        weighted_mean_numerator =  price * weight + weighted_mean_numerator
                        weighted_mean_denominator = weight + weighted_mean_denominator
                        #print "weight: " + str(weight) + " price: " + str(price) + " weighted_mean_numerator: " + str(weighted_mean_numerator) + " weighted_mean_denominator: " + str(weighted_mean_denominator)
                    
                    if weighted_mean_denominator == 0:
                        #print "it seems like all dates were the same"
                        mean_price_calculation = 0.0
                        for past_transactions in market["transactions"][resource]: 
                            mean_price_calculation = past_transactions["price"] + mean_price_calculation
                        weighted_past_price = mean_price_calculation / len(market["transactions"][resource])
                    else:
                        weighted_past_price = weighted_mean_numerator / weighted_mean_denominator
                
                    price = float(( weighted_past_price / surplus_ratio ) * tendency_to_sell_expensive)  
                    
                    quantity_offered = int(resource_level)
                    
                    if quantity_offered > 1 and price > 0:
                        sell_offer = {"resource":resource,"price":float(price),"seller":self,"name":self.name,"quantity":int(quantity_offered),"date":current_date}
                        self.make_market_bid(market,sell_offer)
                    
                    
                    
    
    def calculate_supply_reaction_02(market_decision_class,self):
        """
        Function that will decide if a "sell" offer should be emitted, and at what price and quantity
        """
        market = self.location.market
        timeframe_considered = int(self.input_output_dict["timeframe"] * (self.owner.company_database["timeframe_considered"] / 20.0))
        tendency_save_before_selling = (self.owner.company_database["tendency_save_before_selling"] / 30.0) + 1
        tendency_to_decrease_price_fast = (self.owner.company_database["tendency_to_decrease_price_fast"] / 30.0) + 1
        #        
    
        current_date = self.solar_system_object_link.current_date
        try: self.urgency
        except: self.urgency = {}
        
        
        for resource in self.input_output_dict["output"]:
            try: self.urgency[resource]
            except:
                self.urgency[resource] = 1.0

            
            if self.stock_dict[resource] < (tendency_save_before_selling * self.input_output_dict["output"][resource]):
                self.urgency[resource] = 1.0
                
            else: 
                
                self.urgency[resource] = self.urgency[resource] * tendency_to_decrease_price_fast

                prices = []
                for transaction in market["transactions"][resource]:
                    #print "transaction: " + str(transaction)
                    prices.append(transaction["price"])
                
                price = float(max(prices) / self.urgency[resource])
                
                quantity_offered = int(self.stock_dict[resource])   
                if quantity_offered > 1 and price > 0:
                    sell_offer = {"resource":resource,"price":float(price),"seller":self,"name":self.name,"quantity":int(quantity_offered),"date":current_date}
                    self.make_market_bid(market,sell_offer)
    
    





    
    def calculate_supply_reaction_03(market_decision_class,self):
        """
        Function that will decide if a "sell" offer should be emitted, and at what price and quantity
        
        This flavour just cells at a random price between zero and 1.2 times the previously highest price
        """
        market = self.location.market
        current_date = self.solar_system_object_link.current_date
        for resource in self.input_output_dict["output"]:
                prices = []
                for transaction in market["transactions"][resource]:
                    prices.append(transaction["price"])
                price = random.random() * max(prices) * 1.2 
                
                quantity_offered = int(self.stock_dict[resource])   
                if quantity_offered > 1 and price > 0:
                    sell_offer = {"resource":resource,"price":float(price),"seller":self,"name":self.name,"quantity":int(quantity_offered),"date":current_date}
                    self.make_market_bid(market,sell_offer)
                


    def calculate_intercity_supply_01(market_decision_class,self):
        """
        Function that will decide to sell for an intercity merchant, and at what price and quantity
        
        This flavour just cells at a random price between zero and 1.2 times the previously highest price
        """
        

        
        market = self.to_location.market
        current_date = self.solar_system_object_link.current_date
        resource = self.resource
        prices = []
        for transaction in market["transactions"][resource]:
            prices.append(transaction["price"])
        price = random.random() * max(prices) * 1.2 
        quantity_offered = self.to_stock_dict[resource]   
        if quantity_offered > 1 and price > 0:
            sell_offer = {"resource":resource,"price":float(price),"seller":self,"name":self.name,"quantity":int(quantity_offered),"date":current_date}
            self.make_market_bid(market,sell_offer)
            if self.owner == self.solar_system_object_link.current_player:
                print_dict = {"text":self.name + " is selling " + resource + " at " + self.to_location.name + " at price " + str(int(price)) + " and qt " + str(quantity_offered),"type":"firm info"}
                self.solar_system_object_link.messages.append(print_dict)
