import market_decisions
import research
import firm
import global_variables
import datetime
import primitives
import os
import random
import string
import math
import time

import Image, ImageChops
import pygame



class company:
	def solarSystem(self):
		return global_variables.solar_system
	def marketDecisions(self):
		if(global_variables.market_decisions==None):
			global_variables.market_decisions=market_decisions.market_decisions()
		return global_variables.market_decisions
	def close_company(self):
		"""
		Function that will take care of anything related to closing companies
		Most importantly it will close all firms 
		Later expansions might includes rules for selling off of values
		"""
		if self.solarSystem().company_selected == self:
			self.solarSystem().company_selected = None

		
		close_these_firms = []
		for firm_name in self.owned_firms:
			firm_instance = self.owned_firms[firm_name]
			if firm_instance.isBase():
				firm_instance.for_sale = True
				firm_instance.for_sale_deadline = datetime.timedelta(30*6)+self.solarSystem().current_date
				print_dict = {"text":firm_name + " is up for sale because the owning company " + self.name + " is going bankrupt","type":"base sales"}
				self.solarSystem().messages.append(print_dict)

			else:
				close_these_firms.append(firm_name)
		
		for firm_to_close in close_these_firms:
			self.owned_firms[firm_to_close].close_firm()
			del self.owned_firms[firm_to_close]
		if len(self.owned_firms) == 0:
			
			#ok - no firms left. Now we check if for any technologies that it owns and removes it self from them
			for technology_name in self.solarSystem().technology_tree.vertex_dict:
				technology = self.solarSystem().technology_tree.vertex_dict[technology_name]
				if self in technology["for_sale_by"]:
					del technology["for_sale_by"][self]
			
			#finally the deletion
			self.solarSystem().close_company(self.name)
		else:
			pass
	"""
	The class that holds all methods of the companies
	"""
	
	def __init__(self,solar_system_object,model_company_database=None,deviation=0,companyName=None,capital=0):
		"""
		Starts the company. If no data is given, parameters are made up entirely
		Optionally these parameters can be used
			companyName - the company name
			company_database - a database from another company from which numbers should be taken as much as possible
			home_cities - a list of city names that the company operates in
			capital - starting capital (aka money)
		"""
		if companyName == None:
			self.companyName = self.make_up_names(self.make_up_wordlist())
		else:
			self.companyName = companyName
		
		self.name = self.companyName
		self.home_cities = {}
		self.owned_firms = {}
		self.capital = capital
		self.picture_file = None
		self.last_firm_evaluation = self.solarSystem().current_date
		self.last_market_evaluation = self.solarSystem().current_date
		self.last_supply_evaluation = self.solarSystem().current_date
		self.last_demand_evaluation = self.solarSystem().current_date
		self.calculate_company_database(model_company_database,deviation)
		self.company_accounting = []
		 
		self.research = 0
		self.target_technology = None
		self.target_technology_cost = 9999999

		#The automation_dict is tested for all automation steps to see if they should be carrierd through
		self.automation_dict = {
							    "Demand bidding (initiate buying bids)":True,
							    "Supply bidding (initiate selling bids)":True,
							    "Asset market (buy bases and firms)":True,
							    "Commodities market (start commodity producing firms)":True,
							    "Tech market (buy and sell technology)":True,
							    "Transport market (start up merchant firms)":True,
							    "Evaluate firms (close problematic firms)":True,
							    "Start research firms":True,
							    "Pick research (pick research automatically)":True,
							    "Expand area of operation (search for new home cities)":True
							    }

		
		self.known_technologies = {}
		for vertex_name in self.solarSystem().technology_tree.vertex_dict:
			vertex = self.solarSystem().technology_tree.vertex_dict[vertex_name]
			if vertex["known_by"] == "everybody":
				self.known_technologies[vertex_name] = vertex
		
		
	  
	def calculate_company_database(self,model_company_database,standard_deviation=0):
		"""
		Takes a dictionary of any kind, and compares its keys with the headers specified in the data/economy/companies.txt
		All values not found here, are generated at complete random
		All int values found in both the submitted dict and the header_list, are taken and modified as given by standard_deviation (see this).
		All non-int values are copied exactly
		All values found only in submitted dict are removed (they are probably mistakes of some kind)
		Optional parameteres:
			standard_deviation - a measure of how much to modify the values, as given as the standard_deviation in a gauss function
		"""
		
		
		
		
		try: global_variables.company_database_headers
		except:
			company_database_headers_file = file(os.path.join("data","economy","companies.txt"))
			company_database_headers = company_database_headers_file.readline()
			company_database_headers = company_database_headers.split("\t")
			explanation = company_database_headers_file.readline()
			company_database_header_type = company_database_headers_file.readline()
			company_database_header_type = company_database_header_type.split("\t")
			for i, header in enumerate(company_database_headers):
				company_database_headers[i] = header.rstrip("\n") 
			for i, type in enumerate(company_database_header_type):
				company_database_header_type[i] = type.rstrip("\n") 
			global_variables.company_database_headers = {}
			for i, header in enumerate(company_database_headers):
				global_variables.company_database_headers[header] = company_database_header_type[i]
			company_database_headers_file.close()

		
		if model_company_database is None:
			model_company_database = {}
		new_company_database = {}
		for headers in global_variables.company_database_headers:
			if global_variables.company_database_headers[headers] == "int":
				if headers in model_company_database.keys():
					if standard_deviation == 0:
						new_company_database[headers] = model_company_database[headers]
					else:
						new_company_database[headers] = int(math.fabs(random.gauss(model_company_database[headers],standard_deviation)))
						while 1 > new_company_database[headers] or new_company_database[headers] > 100: #to make the deviation correct, even at the ends. I wonder if this is a good idea 
							if new_company_database[headers] > 100:
								new_company_database[headers] = 200 - new_company_database[headers] 
							if new_company_database[headers] < 1:
								new_company_database[headers] = 2 - new_company_database[headers]
				else:
					new_company_database[headers] = random.randint(1,100)

			elif global_variables.company_database_headers[headers] == "string":
				if headers in model_company_database.keys():
					new_company_database[headers] = model_company_database[headers]
				else:
					new_company_database[headers] = None
		self.company_database = new_company_database



	def get_company_background(self):
		"""
		Function that returns a background picture for each company
		At present this is just a random picture from the folder /images/company/
		"""
		if self.picture_file != None:
			file_name_and_path = self.picture_file
		else:
			company_base_dir = os.path.join("images","company")
			file_list = []
			for files in os.walk(company_base_dir):
				for found_file in files[2]:
					if found_file.find(".jpg", len(found_file) - 4, len(found_file)) != -1:
						file_list.append(found_file)

			number_of_files_to_pick_from = len(file_list)
			if number_of_files_to_pick_from == 0:
				if self.solarSystem().message_printing["debugging"]:
					print_dict = {"text":"DEBUGGING: In get_company_background There are no JPGs in the given folder","type":"debugging"}
					self.solarSystem().messages.append(print_dict)
			else:
				my_pick = random.randrange(0,number_of_files_to_pick_from)
				file_name = file_list[my_pick]
				file_name_and_path = os.path.join(company_base_dir,file_name)
			self.picture_file = file_name_and_path

		image = Image.open(file_name_and_path)
		
		#resizing to fit the window
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
		
	def draw_company_window(self):
		surface = self.get_company_background()
		return surface
		
		
		
	def evaluate_market(self):
		"""
		Function that will perform the evaluate_market function specified in the company database
		The database specifies numbers between 1 and 100, so this will have to be normalized
		to the number of entries in the databae
		"""
		#check if research firms should be started.
		##############################################
		if self.automation_dict["Start research firms"]:
			functions_to_choose_from = self.marketDecisions().start_research_firms
			function_to_choose = int(math.ceil(len(functions_to_choose_from) * (self.company_database["start_research_firms"] / 100.0)))
			functions_to_choose_from[function_to_choose](self)


		
		#check if commodity firms should be started
		##############################################
		if self.automation_dict["Commodities market (start commodity producing firms)"]:
			functions_to_choose_from = self.marketDecisions().evaluate_commodities_market
			function_to_choose = int(math.ceil(len(functions_to_choose_from) * (self.company_database["evaluate_commodities_market"] / 100.0)))
			functions_to_choose_from[function_to_choose](self)
		
		#check if nearby assets should be bought
		##############################################
		if self.automation_dict["Asset market (buy bases and firms)"]:
			functions_to_choose_from = self.marketDecisions().evaluate_asset_market
			function_to_choose = int(math.ceil(len(functions_to_choose_from) * (self.company_database["evaluate_asset_market"] / 100.0)))
			functions_to_choose_from[function_to_choose](self)
		
		 
		#check what decisions should be made on the tech market
		##############################################
		if self.automation_dict["Tech market (buy and sell technology)"]:
			functions_to_choose_from = self.marketDecisions().evaluate_tech_market
			function_to_choose = int(math.ceil(len(functions_to_choose_from) * (self.company_database["evaluate_tech_market"] / 100.0)))
			functions_to_choose_from[function_to_choose](self)

		#check if any merchant companies should be started up
		##############################################
		if self.automation_dict["Transport market (start up merchant firms)"]:
			functions_to_choose_from = self.marketDecisions().evaluate_intercity_trade_market
			function_to_choose = int(math.ceil(len(functions_to_choose_from) * (self.company_database["evaluate_intercity_trade_market"] / 100.0)))
			functions_to_choose_from[function_to_choose](self)


		
		#check if home_cities should be expanded
		##############################################
		if self.automation_dict["Expand area of operation (search for new home cities)"]:
			functions_to_choose_from = self.marketDecisions().evaluate_expansion_opportunities
			function_to_choose = int(math.ceil(len(functions_to_choose_from) * (self.company_database["evaluate_expansion_opportunities"] / 100.0)))
			functions_to_choose_from[function_to_choose](self)

		
		 
#
#	def evaluate_firms(self):
#		"""
#		Function that will perform the evaluate_firms function specified in the company database
#		The database specifies numbers between 1 and 100, so this will have to be normalized
#		to the number of entries in the databae
#		"""
#		
#		functions_to_choose_from = global_vajhjhksdariables.madadsrket_decisions.evaluate_firms
#		function_to_choose = int(math.ceil(len(functions_to_choose_from) * (self.company_database["evaluate_firms"] / 100.0)))
#		functions_to_choose_from[function_to_choose](self)
#		


	def evaluate_firms(self):
		"""
		Function that will perform the evaluate_firms function specified in the company database
		The database specifies numbers between 1 and 100, so this will have to be normalized
		to the number of entries in the databae
		"""
		
		functions_to_choose_from = self.marketDecisions().evaluate_firms
		function_to_choose = int(math.ceil(len(functions_to_choose_from) * (self.company_database["evaluate_firms"] / 100.0)))
		functions_to_choose_from[function_to_choose](self)
		
		
		

	def pick_research(self):
		"""
		Function that will perform the pick_research function specified in the company database
		The database specifies numbers between 1 and 100, so this will have to be normalized
		to the number of entries in the database
		"""
		functions_to_choose_from = self.marketDecisions().pick_research
		function_to_choose = int(math.ceil(len(functions_to_choose_from) * (self.company_database["pick_research"] / 100.0)))
		functions_to_choose_from[function_to_choose](self)

	

	def expand_home_cities(self,solar_system_object):
		"""
		Function that can be called if the the company still has desire to expand
		Will return the name of one new home_city which is connected to one of the earlier home_cities
		"""
		
		if len(self.home_cities)==0:
			potential_bases = []
			for planet in solar_system_object.planets.values():
				for base_names in planet.bases:
					potential_bases.append(base_names)
			new_home_city_name = random.choice(potential_bases)
#			print "made a list of " + str(len(potential_bases)) + " and picked from this " + str(new_home_city_name)
		else:
			potential_base_names = []
			for planet in solar_system_object.planets.values():
				for base in planet.bases.values():
					if base.base_name in self.home_cities:
						if len(base.trade_routes) > 0:
							potential_base_names = potential_base_names + base.trade_routes.keys()
			
			for existing_home_base_name in self.home_cities.keys():
				if existing_home_base_name in potential_base_names:
					i = potential_base_names.index(existing_home_base_name)
					del potential_base_names[i]

			if len(potential_base_names) > 0:
				new_home_city_name = potential_base_names[random.randint(0,len(potential_base_names)-1)]
			else:
				if self.solarSystem().message_printing["debugging"]:
					print_dict = {"text":"DEBUGGING: The expand_home_cities function did not find any new home_cities for " + self.name + " which have the current home_cities: " + str(self.home_cities),"type":"debugging"}
					self.solarSystem().messages.append(print_dict)

				new_home_city_name = None
			
		if new_home_city_name is None:
			new_home_city = None
		else:
			for planet in solar_system_object.planets.values():
				for base in planet.bases.values():
					if base.base_name == new_home_city_name:
						new_home_city = base
			
		return new_home_city


		
		



	def evaluate_self(self):
		"""
		This is the entry function for almost all of the action going on in the simulation. It will evaluate each company 
		each game step by doing the following steps:
		It will evaluate research and call necessary functions if applicable, such as when discoveries have been made
		It will check if any firm auctions are completed and effectuate them
		It will evaluate company holdings and close it if they are negative
		and then call the evaluate_firms and evaluate_market functions
		This function will also save the company capital in self.company_accounting for later plotting 
		
		"""
		#making sure at least one home_city is found
		if len(self.home_cities) == 0:
			new_home_city = self.expand_home_cities(self.solarSystem())
			self.home_cities[new_home_city.name] = new_home_city
			
		
		
		#checking if research is obtained:
		if self.research >= self.target_technology_cost and self.target_technology is not None:
			research_rest = self.research - self.target_technology_cost
			before = len(self.known_technologies)
			self.known_technologies[self.target_technology["technology_name"]] = self.target_technology
			try: self.target_technology["known_by"][self.name] = self
			except:
				if self.solarSystem().message_printing["debugging"]:
					print_dict = {"text":"DEBUGGING: a firm discovered " + self.target_technology["technology_name"] + " which is known by " + str(self.target_technology["known_by"]) + " this is probably a mistake","type":"debugging"}
					self.solarSystem().messages.append(print_dict)
			else:
				pass
			print_dict = {"text":self.name + " discovered " + self.target_technology["technology_name"] + " which cost " + str(self.target_technology_cost) + " the remaining " + str(research_rest) + " research points have been transferred to further research.","type":"tech discovery"}
			self.solarSystem().messages.append(print_dict)
			self.target_technology = None
			self.research = research_rest
		if self.target_technology is None:
			if self.automation_dict["Pick research (pick research automatically)"]:
			 	self.pick_research()
 			else: #FIXME
				if self.research > 0:
					print_dict = {"text":self.name + " needs to pick a technology. Go to the technology window","type":"general gameplay info"}
					self.solarSystem().messages.append(print_dict)
				
				


		#checking if any firms are for sale, if their bid_deadline is crossed and if so effectuates the sale
		for firm_instance in self.owned_firms.values():
			if firm_instance.for_sale:
				if firm_instance.for_sale_deadline > self.solarSystem().current_date:
					bids = firm_instance.for_sale_bids.values()
					bids.sort()
					inverted_bids = primitives.invert_dict(firm_instance.for_sale_bids)
					funding_not_ok = True
					winning_company = None
					i = 0
					while funding_not_ok:
						i = i - 1
						try: bids[i]
						except: 
							print_dict = {"text":"Did not find a buyer for base " + firm_instance.name + " - extending deadline with half a year","type":"base sales"}
							self.solarSystem().messages.append(print_dict)

							
							break
						else:
							winning_price = bids[i]
							for potential_winning_company in inverted_bids[winning_price]:
								if potential_winning_company.capital > winning_price:
									funding_not_ok = False
									winning_company = potential_winning_company
							
					
					if winning_company is not None:
						print_dict = {"text":firm_instance.name + " was for sale but was won by " + winning_company.name + " for the price of " + str(int(winning_price)) + " buying from " + self.name,"type":"base sales"}
						self.solarSystem().messages.append(print_dict)
						
						winning_company.capital = winning_company.capital - winning_price
						self.capital = self.capital - winning_price
						winning_company.home_cities[firm_instance.name] = firm_instance
						del self.owned_firms[firm_instance.name]
						winning_company.owned_firms[firm_instance.name] = firm_instance
						firm_instance.owner = winning_company
						firm_instance.for_sale = False
						firm_instance.for_sale_deadline = None
						firm_instance.for_sale_bids = {}
					else:
						firm_instance.for_sale_deadline = datetime.timedelta(30*6)+self.solarSystem().current_date
						
					
		
		max_records_kept_in_account = 500
		self.company_accounting.append({"capital":self.capital,"date":self.solarSystem().current_date})
		while len(self.company_accounting) > max_records_kept_in_account:
			del self.company_accounting[0]

		#Provided that the company still has money left, all firms are evaluated:
		if self.capital > 1000: #FIXME check that it is a good idea to set this above zero
			#Ok the company is still going check timing
			max_time_firm_and_market = 5 * 365 #days
			min_time_firm_and_market = 365 / 2#days
			
			max_time_supply_and_demand = 300 #days
			min_time_supply_and_demand = 60 #days
			

			#firm evaluation
			if self.automation_dict["Evaluate firms (close problematic firms)"]:
				time_limit_of_firm_evaluation = int(((101 - self.company_database["evaluate_firms_often"])/100.0) * (max_time_firm_and_market - min_time_firm_and_market) + min_time_firm_and_market)
				if (self.solarSystem().current_date - self.last_firm_evaluation).days >  time_limit_of_firm_evaluation:
					self.last_firm_evaluation = self.solarSystem().current_date
					self.evaluate_firms()
			
			#market evaluation
			time_limit_of_market_evaluation = int(((101 - self.company_database["evaluate_market_often"])/100.0) * (max_time_firm_and_market - min_time_firm_and_market) + min_time_firm_and_market)
			if (self.solarSystem().current_date - self.last_market_evaluation).days >  time_limit_of_market_evaluation:
				self.last_market_evaluation = self.solarSystem().current_date
				self.evaluate_market()
				
			#stock change evaluation - always done
			for firm_instance in self.owned_firms.values():
				firm_instance.execute_stock_change(self.solarSystem().current_date)

			
			#supply evaluation
			#time_limit_of_supply_evaluation = ((101 - self.company_database["evaluate_supply_often"]) * max_time_supply_and_demand) / 100
			if self.automation_dict["Supply bidding (initiate selling bids)"]:
				time_limit_of_supply_evaluation = int(((101 - self.company_database["evaluate_supply_often"])/100.0) * (max_time_supply_and_demand - min_time_supply_and_demand) + min_time_supply_and_demand)
				if (self.solarSystem().current_date - self.last_supply_evaluation).days >  time_limit_of_supply_evaluation:
					self.last_supply_evaluation = self.solarSystem().current_date
					for firm_instance in self.owned_firms.values():
						firm_instance.calculate_supply_reaction()

			
			#demand evaluation
			if self.automation_dict["Demand bidding (initiate buying bids)"]:
				time_limit_of_demand_evaluation = int(((101 - self.company_database["evaluate_demand_often"])/100.0) * (max_time_supply_and_demand - min_time_supply_and_demand) + min_time_supply_and_demand)
				if (self.solarSystem().current_date - self.last_demand_evaluation).days >  time_limit_of_demand_evaluation:
					self.last_demand_evaluation = self.solarSystem().current_date
					for firm_instance in self.owned_firms.values():
						firm_instance.calculate_demand_reaction()


		
		else:
			if self != self.solarSystem().current_player:
				self.close_company()
			else:
				raise Exception("Game over - the current player does not have any more money")
			

			
			
		
		
	
	def make_up_wordlist(self,stock_exchanges=["LSE.txt","NYSE.txt","TSE.txt"]):
		"""
		Loads the lists of companies on the LSE, NYSE and TSE and creates a word list, which is a dictionary
		with four keys: first_words, second_words, third_words, and last_words. This can be used for later
		creation of company names
		"""
		try: global_variables.word_list
		except:
			first_words = []
			second_words = []
			third_words = []
			last_words = []
	
			for stock_exchange in stock_exchanges:
				file_name = os.path.join("data","company_data",stock_exchange)
				
				file = open(file_name)
				raw_read = file.readlines()
				file.close()
				
				for line in raw_read:
					line = line.rstrip("\n")
					line = line.rstrip()
					old_splitline = line.split(" ")
					
					splitline = []
					for singleword in old_splitline:
						singleword = string.capitalize(singleword)
						splitline.append(singleword)
					
					if len(splitline) > 1:
						if len(splitline) == 2:
							first_words.append(splitline[0])
							last_words.append(splitline[1])
						elif len(splitline) == 3:
							first_words.append(splitline[0])
							second_words.append(splitline[1])
							last_words.append(splitline[2])
						elif len(splitline) == 4:
							first_words.append(splitline[0])
							second_words.append(splitline[1])
							third_words.append(splitline[2])
							last_words.append(splitline[3])
						else:
							pass
			word_list = {"first_words":first_words,"second_words":second_words,"third_words":third_words,"last_words":last_words}
			global_variables.word_list = word_list
		else:
			word_list = global_variables.word_list
		
		return word_list
		
	def make_up_names(self,wordlist):
		"""
		Give this function a word list as seen in make_up_names() and it will mash them into
		(hopefully) unrecognizable new company names 
		"""
		first_words = wordlist["first_words"]
		second_words = wordlist["second_words"]
		third_words = wordlist["third_words"]
		last_words = wordlist["last_words"]
		
		first_word = first_words[random.randrange(0,len(first_words))]
		last_word = last_words[random.randrange(0,len(last_words))]
		number_of_middle_words = random.randrange(1,2)
		if number_of_middle_words == 2:
			middle_words = str(second_words[random.randrange(0,len(second_words))]) + " " + str(third_words[random.randrange(0,len(thirds_words))])
			word = first_word + " " + middle_words + " " + last_word
		if number_of_middle_words == 1:
			all_middle_words = second_words + third_words 
			middle_words = str(all_middle_words[random.randrange(0,len(all_middle_words))])
			word = first_word + " " + middle_words + " " + last_word
		else:
			word = first_word + " " + last_word
		
		#shortening the length of very long company names.
		while len(word) > global_variables.max_letters_in_company_names:
			next_shortest_pos_at_space = word.rfind(" ")
			if next_shortest_pos_at_space > 10: 
				word = word[0:next_shortest_pos_at_space]
			else: #for the case where there just is one very long string without spaces as the name.
				word = word[0:global_variables.max_letters_in_company_names]
			
			
		return word
		
	


	def change_firm_size(self,location,size,technology_name, name = None):
		"""
		The purpose of this function is to start and close firms or modify their size. It takes a size, which is
		an integer multiplicator of the process_dict and a location. If the size is zero it closes down any firms owned
		by the company in that location. Else it sets the size of a firm owned by that company to as specified, creating it
		from new if required.
		
		Accepts the special technology_name string of "research" which will instead start a research firm
		
		The name argument can optionally be given to specify the name. Defaults to a random name based on technology
		"""
		
		#first some checking of the size variable we got
		if isinstance(size,float):
			if self.solarSystem().message_printing["debugging"]:
				print_dict = {"text":"DEBUGGING: change_firm_size received a float " + str(size) + " -- correct this","type":"debugging"}
				self.solarSystem().messages.append(print_dict)
			size = int(size)
		elif isinstance(size,int) or isinstance(size,long):
			pass
		else:
			print self.name
			print size
			raise Exception("Did not recognize the type of size given")
		if size < 0:
			raise Exception("Received a negative size for a firm. This is not allowed")

		#then reaction to a size of zero - which is the same as a closing order - firms are closed outright, and bases are put for sale
		elif size == 0:
			for firm_name in self.owned_firms:
				firm_instance = self.owned_firms[firm_name]
				if firm_instance.location == location:
					if firm_instance.technology_name == technology_name:
						if not firm_instance.isBase():
							firm_instance.close_firm()
							del self.owned_firms[firm_name]
							break
						else:
							firm_instance.for_sale = True
							firm_instance.for_sale_deadline = datetime.timedelta(30*6)+self.solarSystem().current_date
		elif 0 < size and size < 1:
			raise Exception("Received a size " + str(size) + " - this will risk creating zero input processes")
		
		#This is the reaction to a size that is not zero - ie. a "build something" or "change the size of something" order
		else:
			#first checking if it already exists:
			existing_firm = None
			for firm_instance in self.owned_firms.values():
				 if firm_instance.location == location:
					if firm_instance.technology_name == technology_name:
						existing_firm = firm_instance
						break
			
			if existing_firm is None: #start up a new one
				#special if it is a research firm which have a more or less fixed input_output_dict
				if technology_name == "research":
					if name is None:
						name_is_not_unique = True
						while name_is_not_unique:
							name_is_not_unique = False
							firm_name = technology_name + "_" + str(random.randint(10000,99999))
							for company_instance in self.solarSystem().companies.values():
								if firm_name in company_instance.owned_firms.keys():
									name_is_not_unique = True
					else:
				   		firm_name = name
					input_output_dict = {"input":{"labor":size},"output":{},"timeframe":30*6,"byproducts":{}}
					new_firm = research.research(self.solarSystem(), location,input_output_dict,self,firm_name)
					new_firm.size = size
					new_firm.last_consumption_date = self.solarSystem().current_date
					self.owned_firms[firm_name] = new_firm
					
				
				#if it is not we search for the process requested
				else:
					if technology_name not in self.known_technologies.keys():
						print technology_name
						print self.known_technologies.keys()
						raise Exception("The requested technology was not found")

					firm_specific_process = {}
					for direction in ["input","output"]:
						firm_specific_process[direction] = {}
						for resource_processed in self.known_technologies[technology_name]["input_output_dict"][direction]:
							firm_specific_process[direction][resource_processed] = self.known_technologies[technology_name]["input_output_dict"][direction][resource_processed] * size
					for other_keys in self.known_technologies[technology_name]["input_output_dict"].keys(): #to include whatever might have been in the input_output_dict
						if other_keys not in ["input","output"]:
							 firm_specific_process[other_keys] = self.known_technologies[technology_name]["input_output_dict"][other_keys]
					
					if name is None:
						name_is_not_unique = True
						while name_is_not_unique:
							name_is_not_unique = False
							firm_name = technology_name + "_" + str(random.randint(10000,99999))
							for company_instance in self.solarSystem().companies.values():
								if firm_name in company_instance.owned_firms.keys():
									name_is_not_unique = True
					else:
						firm_name = name
					new_firm = firm.firm(self.solarSystem(),location,firm_specific_process,self,firm_name,technology_name)
					
					
					
					new_firm.size = size
					new_firm.last_consumption_date = self.solarSystem().current_date
					self.owned_firms[firm_name] = new_firm
	
					#checking input_output_dict FIXME this check can perhaps be omitted
					for resource in new_firm.input_output_dict["input"]:
						if new_firm.input_output_dict["input"][resource] <= 0:
							raise Exception("The " + firm_name + " just created had an input of " + resource + " of " + str(new_firm.input_output_dict["input"][resource]))
			
			else: #in the cases where the firm already exists
				#first we see if it is a research firm in which it is a simple change of the input_output dict
				if technology_name == "research":
					existing_firm.size = size
					existing_firm.input_output_dict["input"]["labor"] = size
				   
				else:
					original_size = existing_firm.size
					for direction in ["input","output"]:
						for resource in existing_firm.input_output_dict[direction]:
							existing_value = existing_firm.input_output_dict[direction][resource]
							existing_firm.input_output_dict[direction][resource] = (existing_value * size) / original_size
							existing_firm.size = size
							
					#checking input_output_dict
					for resource in existing_firm.input_output_dict["input"]:
						if existing_firm.input_output_dict["input"][resource] <= 0:
							raise Exception("The " + existing_firm.name + " just size-changed had an input of " + resource + " of " + str(existing_firm.input_output_dict["input"][resource]) + " the requested size was " + str(size) + " and the original size was " + str(original_size))
