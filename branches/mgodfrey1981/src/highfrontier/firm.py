import primitives
import Image, ImageChops
import pygame
import random
import os
import global_variables
import math
import datetime

class firm:
    def solarSystem(self):
        return global_variables.solar_system
    def make_market_bid(self,market,own_offer):
            """
            Function that takes a sell or buy offer (identified if it has "seller" or "buyer" in it
            and connects to the market to see if a corresponding offer exists. If it does it will connect
            seller and buyer. If not it will store the offer in market database. If market database is too
            long it will remove some of the highest price sell offers and the lowest price buy offers
            """

            #if self is a merchant we first need to assign the correct stock_dict
            if self.isMerchant():
                    if "seller" in list(own_offer.keys()):
                            self.stock_dict = self.to_stock_dict
                    elif "buyer" in list(own_offer.keys()):
                            self.stock_dict = self.from_stock_dict
                    else:
                            raise Exception('unknown offer type')
            #defining basics and checking if the offer is valid
            if not (isinstance(own_offer["quantity"],int) or isinstance(own_offer["quantity"],int)):
                    own_offer["quantity"] = int(own_offer["quantity"])
                    if self.solarSystem().message_printing["debugging"]:
                            print_dict = {"text":"DEBUGGING: The quantity given in an offer from " + str(self.name) + ", which is using " + str(self.decision_data["demand_function"]) + " and " + str(self.decision_data["supply_function"]) + " is not an integer. Try to keep it as integers","type":"debugging"}
                            self.solarSystem().messages.append(print_dict)
            if not isinstance(own_offer["price"],float):
                    print_dict = {"text":"DEBUGGING: The price given in an offer from " + str(self.name) + ", which is using " + str(self.decision_data["demand_function"]) + " and " + str(self.decision_data["supply_function"]) + " is not a float. Try to keep it as floats","type":"debugging"}
                    if self.solarSystem().message_printing["debugging"]:
                            self.solarSystem().messages.append(print_dict)
                            own_offer["price"] = float(own_offer["price"])
            resource = own_offer["resource"]
            if "seller" in list(own_offer.keys()):
                    type = "sell_offer"
                    opposite_bids = market["buy_offers"][resource]
                    competing_bids = market["sell_offers"][resource]
                    if self.stock_dict[resource] < own_offer["quantity"]:
                            own_offer["quantity"] = int(self.stock_dict[resource])
                            if self.solarSystem().message_printing["debugging"]:
                                    print_dict = {"text":"DEBUGGING WARNING: adjusted " + resource + " sell offer from " + str(self.name) + " to " + str(own_offer["quantity"]) + " because of lack of resources  - you should try to correct this from the calculate_supply functions","type":"debugging"}
                                    self.solarSystem().messages.append(print_dict)
            elif "buyer" in list(own_offer.keys()):
                    type = "buy_offer"
                    opposite_bids = market["sell_offers"][resource]
                    competing_bids = market["buy_offers"][resource]
                    if self.owner.capital < (own_offer["price"] * own_offer["quantity"]):
                            own_offer["quantity"] = int(self.owner.capital / own_offer["price"])
                            if self.solarSystem().message_printing["debugging"]:
                                    print_dict = {"text":"DEBUGGING WARNING: adjusted buy offer from " + str(self.name) + " to " + str(own_offer["quantity"]) +" because of lack of capital - you should try to correct this from the calculate_demand functions. The original price was " + str(own_offer["price"]) + " and the capital was " + str(self.owner.capital),"type":"debugging"}
                                    self.solarSystem().messages.append(print_dict)
            else:
                    print("Unknown offer type in make_market_bid() function")
                    raise Exception('unknown offer type')
            if own_offer["quantity"] < 0:
                    if self.solarSystem().message_printing["debugging"]:
                            print_dict = {"text":"DEBUGGING WARNING: The quantity " + str(own_offer["quantity"]) + " offered by " + str(self.name) + " is not a positive amount. This should be corrected from market_decisions. It was set to 0 as a safeguard","type":"debugging"}
                            self.solarSystem().messages.append(print_dict)
                    own_offer["quantity"] = 0
            quantity_found = 0
            i = 0
            offers_of_interest = []
            while quantity_found < own_offer["quantity"]:
                    # if there are no more bids available but still a quantity left to fulfill of own_offer
                    if i + 1 > len(opposite_bids):
                            balance_of_findings = - own_offer["quantity"]
                            need_to_find_more = True
                            break
                    #defining directions
                    if type == "sell_offer":
                            counterpart = opposite_bids[i]["buyer"]
                    elif type == "buy_offer":
                            counterpart = opposite_bids[i]["seller"]
                    else:
                            raise Exception('unknown offer type')
                    #if counterpart is a merchant we first need to assign the correct stock_dict
                    if counterpart.isMerchant():
                            if "seller" in list(own_offer.keys()):
                                    counterpart.stock_dict = counterpart.from_stock_dict
                            elif "buyer" in list(own_offer.keys()):
                                    counterpart.stock_dict = counterpart.to_stock_dict
                            else:
                                    raise Exception('unknown offer type')

                    # if there are bids available at an ok price
                    if (opposite_bids[i]["price"] >= own_offer["price"] and type == "sell_offer") or (opposite_bids[i]["price"] <= own_offer["price"] and type == "buy_offer"):
                            if counterpart.stock_dict[resource] < opposite_bids[i]["quantity"] and type == "buy_offer":
                                    opposite_bids[i]["quantity"] = max(int(counterpart.stock_dict[resource]),0)
                            if counterpart.owner.capital < (opposite_bids[i]["quantity"] * opposite_bids[i]["price"]) and type == "sell_offer":
                                    opposite_bids[i]["quantity"] = max(int(counterpart.owner.capital / opposite_bids[i]["price"]),0)
                            if opposite_bids[i]["quantity"]<0:
                                    if self.solarSystem().message_printing["debugging"]:
                                            print_dict = {"text":"DEBUGGING WARNING: The quantity in an offer from " + counterpart.name + " was changed to " + str(opposite_bids[i]["quantity"]) + " during a " + type +" from " + str(self.name) + " regarding " + resource,"type":"debugging"}
                                            self.solarSystem().messages.append(print_dict)

                            quantity_found = opposite_bids[i]["quantity"] + quantity_found
                            offers_of_interest.append(opposite_bids[i])

                    #if there are no more bid available at the price
                    else:
                            break
                    i = i + 1

            #evaluating how much was found to be available on market
            if quantity_found > own_offer["quantity"]:
                    balance_of_findings = quantity_found - own_offer["quantity"]

                    offers_of_interest[-1]["quantity"] = offers_of_interest[-1]["quantity"] - balance_of_findings
                    need_to_find_more = False
            elif quantity_found == own_offer["quantity"]:
                    balance_of_findings = 0
                    need_to_find_more = True
            else:
                    balance_of_findings = quantity_found - own_offer["quantity"]
                    need_to_find_more = True

            # Effectuating the transactions
            counterparts_list = []
            for offer_of_interest in offers_of_interest:
                    if type == "sell_offer":
                            counterpart = offer_of_interest["buyer"]
                    elif type == "buy_offer":
                            counterpart = offer_of_interest["seller"]
                    else:
                            raise Exception('unknown offer type')
                    if offer_of_interest["quantity"] < 0:
                            if self.solarSystem().message_printing["debugging"]:
                                    print_dict = {"text":"DEBUGGING WARNING: The quantity in an offer_of_interest from " + counterpart.name + " regarding " + resource + " was found to be " + str(offer_of_interest["quantity"]) + ". " + str(counterpart.name) + " has a calculate_supply_reaction parameter of " + str(counterpart.owner.company_database["calculate_supply_reaction"]) + " and a calculate_demand_reaction parameter of " + str(counterpart.owner.company_database["calculate_demand_reaction"]),"type":"debugging"}
                                    self.solarSystem().messages.append(print_dict)
                    counterparts_list.append(counterpart.name)
                    if type == "sell_offer":
                            counterpart = offer_of_interest["buyer"]
                            counterpart.owner.capital = counterpart.owner.capital - offer_of_interest["price"] * offer_of_interest["quantity"]
                            counterpart.stock_dict[resource] = counterpart.stock_dict[resource] + offer_of_interest["quantity"]
                            self.owner.capital = self.owner.capital + offer_of_interest["price"] * offer_of_interest["quantity"]
                            self.stock_dict[resource] = self.stock_dict[resource] - offer_of_interest["quantity"]
                            if self.owner == self.solarSystem().current_player or counterpart.owner == self.solarSystem().current_player:
                                    print_dict = {"text":self.name + " sold " + str(offer_of_interest["quantity"]) + " units of " + resource + " to " + counterpart.name + " for a price of " + str(offer_of_interest["price"]),"type":"firm info"}
                                    self.solarSystem().messages.append(print_dict)
                            transaction_report = {"seller":self,"buyer":counterpart,"price":offer_of_interest["price"],"quantity":offer_of_interest["quantity"],"date":own_offer["date"],"resource":resource}
                    elif type == "buy_offer":
                            counterpart = offer_of_interest["seller"]
                            counterpart.owner.capital = counterpart.owner.capital + offer_of_interest["price"] * offer_of_interest["quantity"]
                            counterpart.stock_dict[resource] = counterpart.stock_dict[resource] - offer_of_interest["quantity"]
                            self.owner.capital = self.owner.capital - offer_of_interest["price"] * offer_of_interest["quantity"]
                            self.stock_dict[resource] = self.stock_dict[resource] + offer_of_interest["quantity"]
                            if self.owner == self.solarSystem().current_player or counterpart.owner == self.solarSystem().current_player:
                                    print_dict = {"text":str(self.name) + " bought " + str(offer_of_interest["quantity"]) + " units of " + str(resource) + " from " + str(counterpart.name) + " for a price of " + str(offer_of_interest["price"]),"type":"firm info"}
                                    self.solarSystem().messages.append(print_dict)

                            transaction_report = {"seller":counterpart,"buyer":self,"price":offer_of_interest["price"],"quantity":offer_of_interest["quantity"],"date":own_offer["date"],"resource":resource}
                    else:
                            raise typeError

                    if counterpart.isMerchant():
                            counterpart.stock_dict = {} #to make sure no problems arise in the future

                    transaction_report["seller"].accounting.append(transaction_report)
                    transaction_report["buyer"].accounting.append(transaction_report)
                    market["transactions"][resource].append(transaction_report)

                    if transaction_report["quantity"] < 0:
                            #print
                            if self.solarSystem().message_printing["debugging"]:
                                    print_dict = {"text":"DEBUGGING WARNING: The quantity in a " + type + " of " + resource + " by " + self.name + " was found to be " + str(transaction_report["quantity"]),"type":"debugging"}
                                    self.solarSystem().messages.append(print_dict)

            #removing bids from the market if they have been effectuated
            remove_these = []
            for i, opposite_bid in enumerate(opposite_bids):
                    if type == "sell_offer":
                            if opposite_bid["buyer"].name in counterparts_list:
                               if offers_of_interest[-1]["buyer"].name == opposite_bid["buyer"].name and not need_to_find_more:
                                            offers_of_interest[-1]["quantity"] = balance_of_findings
                               else:
                                       remove_these.append(i)
                    if type == "buy_offer":
                            if opposite_bid["seller"].name in counterparts_list:
                               if offers_of_interest[-1]["seller"].name == opposite_bid["seller"].name and not need_to_find_more:
                                            offers_of_interest[-1]["quantity"] = balance_of_findings
                               else:
                                       remove_these.append(i)
            if len(remove_these) > 0:
                    remove_these.reverse()
                    for remove_this in remove_these:
                            del opposite_bids[remove_this]


            #checking to see if the offer was satisfied, and if not, adds it to the market database
            if need_to_find_more and balance_of_findings != 0:
                    if balance_of_findings >= 0:
                            if self.solarSystem().message_printing["debugging"]:
                                    print_dict = {"text":"DEBUGGING MESSAGE: balance_of_findings was thought to be negative but was " + str(balance_of_findings) + " for " + self.name,"type":"debugging"}
                                    self.solarSystem().messages.append(print_dict)


                    own_offer["quantity"] = -balance_of_findings
                    if len(competing_bids) == 0:
                            competing_bids.append(own_offer)
                    else:
                            did_not_pass_price_range = True
                            for i, competing_bid in enumerate(competing_bids):
                                    if (type == "sell_offer" and competing_bid["seller"].name == self.name) or (type == "buy_offer" and competing_bid["buyer"].name == self.name):
                                            competing_bids.pop(i)
                                    if (competing_bid["price"] > own_offer["price"] and type == "sell_offer" and did_not_pass_price_range) or (competing_bid["price"] < own_offer["price"] and type == "buy_offer" and did_not_pass_price_range):
                                            insert_own_offer_at = i
                                            did_not_pass_price_range = False
                            try: insert_own_offer_at
                            except:
                                    insert_own_offer_at = len(competing_bids)
                            competing_bids.insert(insert_own_offer_at,own_offer)

                            if own_offer["quantity"]<0:
                                    if self.solarSystem().message_printing["debugging"]:
                                            print_dict = {"text":"DEBUGGING WARNING: The quantity in an offer from " + self.name + " somehow ended up being negative","type":"debugging"}
                                            self.solarSystem().messages.append(print_dict)



            #checking to see if the market database for this resource is getting too long. Deleting the worst offers in that case
            max_size_of_market = 50
            while len(competing_bids) > max_size_of_market:
                    competing_bids.pop(-1)

            if self.isMerchant():
                    self.stock_dict = {} #to make sure no problems arise in the future
    def isResearch(self):
        return False
    def isBase(self):
        return False
    def isTertiary(self):
        return False
    def isMerchant(self):
        return False
    def isBaseConstruction(self):
        return False
    def __init__(self,solar_system_object,location,input_output_dict,owner,name,technology_name):
            self.name = name
            if not location.isBase():
                    raise Exception(self.name + " is a regular firm but received a location that was not a base: " + str(location))
            self.location = location
            self.picture_file = None
            self.owner = owner
            self.last_consumption_date = self.solarSystem().current_date
            self.last_accounting = self.solarSystem().current_date
            self.accounting = []
            self.input_output_dict = input_output_dict
            self.stock_dict = {}
            self.technology_name = technology_name
            self.size = 0

            self.for_sale = False #can be set to True when firm is offered up for sale.
            self.for_sale_bids = {} # a dictionary with the bidder as object as keys, and the price they bid as value
            self.for_sale_deadline = None # a date at which the bidding contest is over


            #modifying output for mining
            for resource in input_output_dict["output"]:
                    if resource in self.solarSystem().mineral_resources + ["food"]:
                            mining_opportunity = self.location.mining_opportunities[resource]
                            unmodified_output = input_output_dict["output"][resource]
                            input_output_dict["output"][resource] = (mining_opportunity / 10) * unmodified_output
            for resource in self.solarSystem().trade_resources:
                    self.stock_dict[resource] = 0

    def get_firm_background(self):
            """
            Function that returns a background picture for each firm
            At present this is just a random picture from the folder /images/firm/
            """
            if self.picture_file != None:
                    file_name_and_path = self.picture_file
            else:
                    company_base_dir = os.path.join("images","firm")
                    file_list = []
                    for files in os.walk(company_base_dir):
                            for found_file in files[2]:
                                    if found_file.find(".jpg", len(found_file) - 4, len(found_file)) != -1:
                                            file_list.append(found_file)

                    number_of_files_to_pick_from = len(file_list)
                    if number_of_files_to_pick_from == 0:
                            if self.solarSystem().message_printing["debugging"]:
                                    print_dict = {"text":"DEBUGGING: In get_firm_background There are no JPGs in the given folder","type":"debugging"}
                                    self.solarSystem().messages.append(print_dict)
                    else:
                            my_pick = random.randrange(0,number_of_files_to_pick_from)
                            file_name = file_list[my_pick]
                            file_name_and_path = os.path.join(company_base_dir,file_name)
                    self.picture_file = file_name_and_path
            image = Image.open(file_name_and_path)
            window_size = global_variables.window_size
            aspect_ratio_needed = float(window_size[0])/float(window_size[1])
            aspect_ratio_found = float(image.size[0])/float(image.size[1])
            if aspect_ratio_needed > aspect_ratio_found:
                    image = image.crop((0,0,int(image.size[0]/aspect_ratio_needed),image.size[0]))
            elif aspect_ratio_needed < aspect_ratio_found:
                    image = image.crop((0,0,image.size[1],int(image.size[1]/aspect_ratio_needed)))
            else:
                    pass
            image = image.resize(global_variables.window_size)
            image_string = image.tostring()
            surface = pygame.image.fromstring(image_string , global_variables.window_size, "RGB")
            return surface

    def draw_firm_window(self):
            surface = self.get_firm_background()
            return surface
    def calculate_demand_reaction(self):
            """
            Function that will perform the calculate_demand_reaction function specified in the company database
            The database specifies numbers between 1 and 100, so this will have to be normalized
            to the number of entries in the databae
            """

            functions_to_choose_from = global_variables.market_decisions.calculate_demand_reaction
            function_to_choose = int(math.ceil(len(functions_to_choose_from) * (self.owner.company_database["calculate_demand_reaction"] / 100.0)))
            functions_to_choose_from[function_to_choose](self)

    def calculate_supply_reaction(self):
            """
            Function that will perform the calculate_supply_reaction function specified in the company database
            The database specifies numbers between 1 and 100, so this will have to be normalized
            to the number of entries in the databae
            """
            functions_to_choose_from = global_variables.market_decisions.calculate_supply_reaction
            function_to_choose = int(math.ceil(len(functions_to_choose_from) * (self.owner.company_database["calculate_supply_reaction"] / 100.0)))
            functions_to_choose_from[function_to_choose](self)

    def close_firm(self):
            """
            Function that will take care of anything related to closing firms
            Most importantly it will withdraw all bids in the market
            But later expansions might includes rules for selling of values
            """
            if self.solarSystem().firm_selected == self:
                    self.solarSystem().firm_selected = None


            if self.owner == self.solarSystem().current_player:
                            print_dict = {"text":"The firm " + self.name + " is up for closing","type":"firm info"}
                            self.solarSystem().messages.append(print_dict)
            if self.isMerchant():
                    for place in ["from","to"]:
                            if place == "from":
                                    location = self.from_location
                            elif place == "to":
                                    location = self.to_location
                            else:   raise Exception("weird")

                            offer_types = ["sell_offers","buy_offers"]
                            for offer_type in offer_types:
                                    for resource in [self.resource, self.transport_type]:
                                            delete_these = []
                                            for i, offer in enumerate(location.market[offer_type][resource]):
                                                    if "buyer" in list(offer.keys()):
                                                            if self.name in offer["buyer"].name:
                                                                    delete_these.append(i)
                                                    if "seller" in list(offer.keys()):
                                                            if self.name in offer["seller"].name:
                                                                    delete_these.append(i)
                                            delete_these.reverse()

                                            for delete_this in delete_these:
                                                    del location.market[offer_type][resource][delete_this]
            else:
                    offer_types = ["sell_offers","buy_offers"]
                    for offer_type in offer_types:
                            for resource in self.location.market[offer_type]:
                                    delete_these = []
                                    for i, offer in enumerate(self.location.market[offer_type][resource]):
                                            if "buyer" in list(offer.keys()):
                                                    if self.name in offer["buyer"].name:
                                                            delete_these.append(i)
                                            if "seller" in list(offer.keys()):
                                                    if self.name in offer["seller"].name:
                                                            delete_these.append(i)
                                    delete_these.reverse()
                                    for delete_this in delete_these:
                                            del self.location.market[offer_type][resource][delete_this]




    def update_accounting(self):
            """
            gives the accounting report to the mother company and deletes the contents locally
            """
            revenue = 0
            profit = 0
            timeframe = (self.solarSystem().current_date - self.last_accounting).days

            if len(self.accounting) == 0:

                    accounting_report = {"revenue":0,"profit":0,"timeframe":timeframe}
            else:
                    for transaction_report in self.accounting:
                            value = transaction_report["price"] * transaction_report["quantity"]
                            if transaction_report["seller"].name == self.name:
                                    revenue = revenue + value
                                    profit = profit + value
                            elif transaction_report["buyer"].name == self.name:
                                    profit = profit - value
                            else:
                                    raise Exception("Faulty accounting report found")
                    accounting_report = {"revenue":revenue,"profit":profit,"timeframe":timeframe}

            self.accounting = []
            #self.owner.company_accounting.append({"firm":self,"date":self.solarSystem().current_date,"accounting_report":accounting_report})

            self.last_profit = accounting_report["profit"]
            return accounting_report










    def execute_stock_change(self,current_date):
            """
            Function to calculate the production based on the input_output_dict.
            The input_output_dict is a dictionary with three keys: input, output and timeframe.
            Each value is another dictionary, listing the resources as key and an integer as
            value. One input_output_dict represents one "round" of production during the specified timeframe.
            After executing the self.stock_dict will change to values compatible with consumption between
            the served variable current_date, and the self.last_consumption_date and the self.last_consumption_date
            will be updated.
            """
            try: self.last_consumption_date
            except:
                    if (current_date - self.solarSystem().start_date).days > 100: #because it is an error if there is no last_consumption_data
                            if self.solarSystem().message_printing["debugging"]:
                                    print_dict = {"text":"Small debugging warning. Did not find self.last_consumption_date for " + str(self.name) + " when doing execute_stock_change(). self.solarSystem().start_date was used but this should be corrected at some point","type":"debugging"}
                                    self.solarSystem().messages.append(print_dict)
                    self.last_consumption_date = self.solarSystem().start_date
            time_since_last_calculation = current_date - self.last_consumption_date
            time_span_days = time_since_last_calculation.days
            timeframe = self.input_output_dict["timeframe"]

            if time_span_days > timeframe:
                    number_of_rounds = time_span_days / timeframe
                    keep_calculating = True
                    self.last_consumption_date =  self.last_consumption_date + datetime.timedelta(number_of_rounds * timeframe)

                    while keep_calculating:
                            keep_calculating = False
                            new_stock_level = {}
                            for input_resource in self.input_output_dict["input"]:
                                    new_stock_level[input_resource] = self.stock_dict[input_resource] - self.input_output_dict["input"][input_resource] * number_of_rounds
                                    if 0 > new_stock_level[input_resource]:
                                            new_number_of_rounds = number_of_rounds - 1
                                            keep_calculating = True
                                            #For bases we need to see that the essentials are met
                                            if self.isBase():
                                                    if input_resource == "food":
                                                            if self.starving == "No":
                                                                    self.starving = "A little"
                                                            if self.starving == "A little":
                                                                    self.starving = "A lot"
                                                    if input_resource == "housing":
                                                            if self.lacks_housing == "No":
                                                                    self.lacks_housing = "A little"
                                                            if self.lacks_housing == "A little":
                                                                    self.lacks_housing = "A lot"
                            if keep_calculating:
                                    number_of_rounds = new_number_of_rounds

                    if time_span_days / timeframe > number_of_rounds and self.isBase():
                            if self.owner == self.solarSystem().current_player:
                                    print_dict = {"text":self.name + " is a base, it is starving, but it will continue to produce","type":"base info"}
                                    self.solarSystem().messages.append(print_dict)
                            number_of_rounds = time_span_days / timeframe

                    if number_of_rounds > 0:
                            for input_resource in new_stock_level:
                                    self.stock_dict[input_resource] = new_stock_level[input_resource]
                            for output_resource in self.input_output_dict["output"]:
                                    if not self.solarSystem().trade_resources[output_resource]["storable"]:
                                            self.stock_dict[output_resource] = 0

                                    self.stock_dict[output_resource] = self.input_output_dict["output"][output_resource] * number_of_rounds + self.stock_dict[output_resource]
                            #adding byproducts to the atmosphere
                            for byproduct in self.input_output_dict["byproducts"]:
                                    self.location.home_planet.change_gas_in_atmosphere(byproduct,self.input_output_dict["byproducts"][byproduct] * number_of_rounds)
                                    if self.owner == self.solarSystem().current_player:
                                            print_dict = {"text":"Because of " + self.name + " " + byproduct + " changed with " + str(self.input_output_dict["byproducts"][byproduct] * number_of_rounds) + " units on " + str(self.location.home_planet.name),"type":"climate"}
                                            self.solarSystem().messages.append(print_dict)

                            for resource in self.input_output_dict["output"]:
                                    if resource in self.solarSystem().mineral_resources:
                                            self.location.mining_performed[resource] = self.location.mining_performed[resource] + number_of_rounds * self.input_output_dict["output"][resource]
                                            if self.owner == self.solarSystem().current_player:
                                                    print_dict = {"text":self.name + " mined " + primitives.nicefy_numbers(int(number_of_rounds * self.input_output_dict["output"][resource])) + " on " + str(self.location.home_planet.name),"type":"mining"}
                                                    self.solarSystem().messages.append(print_dict)
