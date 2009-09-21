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
	"""
	The class that holds all methods of the companies
	"""
	
	def __init__(self,solar_system_object,model_company_database=None,deviation=0,company_name=None,capital=0):
		"""
		Starts the company. If no data is given, parameters are made up entirely
		Optionally these parameters can be used
			company_name - the company name
			company_database - a database from another company from which numbers should be taken as much as possible
			home_cities - a list of city names that the company operates in
			capital - starting capital (aka money)
		"""
		if company_name == None:
			self.company_name = self.make_up_names(self.make_up_wordlist())
		else:
			self.company_name = company_name
		
		self.name = self.company_name
		self.home_cities = {}
		self.owned_firms = {}
		self.capital = capital
		self.picture_file = None
		self.solar_system_object_link = solar_system_object
		self.last_firm_evaluation = self.solar_system_object_link.current_date
		self.last_market_evaluation = self.solar_system_object_link.current_date
		self.last_supply_evaluation = self.solar_system_object_link.current_date
		self.last_demand_evaluation = self.solar_system_object_link.current_date
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
		for vertex_name in self.solar_system_object_link.technology_tree.vertex_dict:
			vertex = self.solar_system_object_link.technology_tree.vertex_dict[vertex_name]
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
				if self.solar_system_object_link.message_printing["debugging"]:
					print_dict = {"text":"DEBUGGING: In get_company_background There are no JPGs in the given folder","type":"debugging"}
					self.solar_system_object_link.messages.append(print_dict)
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
			functions_to_choose_from = global_variables.market_decisions.start_research_firms
			function_to_choose = int(math.ceil(len(functions_to_choose_from) * (self.company_database["start_research_firms"] / 100.0)))
			functions_to_choose_from[function_to_choose](self)


		
		#check if commodity firms should be started
		##############################################
		if self.automation_dict["Commodities market (start commodity producing firms)"]:
			functions_to_choose_from = global_variables.market_decisions.evaluate_commodities_market
			function_to_choose = int(math.ceil(len(functions_to_choose_from) * (self.company_database["evaluate_commodities_market"] / 100.0)))
			functions_to_choose_from[function_to_choose](self)
		
		#check if nearby assets should be bought
		##############################################
		if self.automation_dict["Asset market (buy bases and firms)"]:
			functions_to_choose_from = global_variables.market_decisions.evaluate_asset_market
			function_to_choose = int(math.ceil(len(functions_to_choose_from) * (self.company_database["evaluate_asset_market"] / 100.0)))
			functions_to_choose_from[function_to_choose](self)
		
		 
		#check what decisions should be made on the tech market
		##############################################
		if self.automation_dict["Tech market (buy and sell technology)"]:
			functions_to_choose_from = global_variables.market_decisions.evaluate_tech_market
			function_to_choose = int(math.ceil(len(functions_to_choose_from) * (self.company_database["evaluate_tech_market"] / 100.0)))
			functions_to_choose_from[function_to_choose](self)

		#check if any merchant companies should be started up
		##############################################
		if self.automation_dict["Transport market (start up merchant firms)"]:
			functions_to_choose_from = global_variables.market_decisions.evaluate_intercity_trade_market
			function_to_choose = int(math.ceil(len(functions_to_choose_from) * (self.company_database["evaluate_intercity_trade_market"] / 100.0)))
			functions_to_choose_from[function_to_choose](self)


		
		#check if home_cities should be expanded
		##############################################
		if self.automation_dict["Expand area of operation (search for new home cities)"]:
			functions_to_choose_from = global_variables.market_decisions.evaluate_expansion_opportunities
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
		
		functions_to_choose_from = global_variables.market_decisions.evaluate_firms
		function_to_choose = int(math.ceil(len(functions_to_choose_from) * (self.company_database["evaluate_firms"] / 100.0)))
		functions_to_choose_from[function_to_choose](self)
		
		
		

	def pick_research(self):
		"""
		Function that will perform the pick_research function specified in the company database
		The database specifies numbers between 1 and 100, so this will have to be normalized
		to the number of entries in the database
		"""
		functions_to_choose_from = global_variables.market_decisions.pick_research
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
				for base in planet.bases.values():
					potential_bases.append(base)
			new_home_city = potential_bases[random.randint(0,len(potential_bases)-1)]
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
				if self.solar_system_object_link.message_printing["debugging"]:
					print_dict = {"text":"DEBUGGING: The expand_home_cities function did not find any new home_cities for " + self.name + " which have the current home_cities: " + str(self.home_cities),"type":"debugging"}
					self.solar_system_object_link.messages.append(print_dict)

				new_home_city_name = None
			
			if new_home_city_name is None:
				new_home_city = None
			else:
				for planet in solar_system_object.planets.values():
					for base in planet.bases.values():
						if base.base_name == new_home_city_name:
							new_home_city = base
			
		return new_home_city


	def close_company(self):
		"""
		Function that will take care of anything related to closing companies
		Most importantly it will close all firms 
		Later expansions might includes rules for selling off of values
		"""
		close_these_firms = []
		for firm_name in self.owned_firms:
			firm_instance = self.owned_firms[firm_name]
			if isinstance(firm_instance,base):
				#BASESALEPLACE
				firm_instance.for_sale = True
				firm_instance.for_sale_deadline = datetime.timedelta(30*6)+self.solar_system_object_link.current_date
				print_dict = {"text":firm_name + " is up for sale because the owning company " + self.name + " is going bankrupt","type":"base sales"}
				self.solar_system_object_link.messages.append(print_dict)

			else:
				close_these_firms.append(firm_name)
		
		for firm_to_close in close_these_firms:
			self.owned_firms[firm_to_close].close_firm()
			del self.owned_firms[firm_to_close]
		if len(self.owned_firms) == 0:
			
			#ok - no firms left. Now we check if for any technologies that it owns and removes it self from them
			for technology_name in self.solar_system_object_link.technology_tree.vertex_dict:
				technology = self.solar_system_object_link.technology_tree.vertex_dict[technology_name]
				if self in technology["for_sale_by"]:
					del technology["for_sale_by"][self]
			
			#finally the deletion
			self.solar_system_object_link.close_company(self.name)
		else:
			pass
		
		



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
		
		#checking if research is obtained:
		if self.research >= self.target_technology_cost and self.target_technology is not None:
			research_rest = self.research - self.target_technology_cost
			before = len(self.known_technologies)
			self.known_technologies[self.target_technology["technology_name"]] = self.target_technology
			try: self.target_technology["known_by"][self.name] = self
			except:
				if self.solar_system_object_link.message_printing["debugging"]:
					print_dict = {"text":"DEBUGGING: a firm discovered " + self.target_technology["technology_name"] + " which is known by " + str(self.target_technology["known_by"]) + " this is probably a mistake","type":"debugging"}
					self.solar_system_object_link.messages.append(print_dict)
			else:
				pass
			print_dict = {"text":self.name + " discovered " + self.target_technology["technology_name"] + " which cost " + str(self.target_technology_cost) + " the remaining " + str(research_rest) + " research points have been transferred to further research.","type":"tech discovery"}
			self.solar_system_object_link.messages.append(print_dict)
			self.target_technology = None
			self.research = research_rest
		if self.target_technology is None:
			if self.automation_dict["Pick research (pick research automatically)"]:
			 	self.pick_research()
 			else: #FIXME
				print_dict = {"text":self.name + " needs to pick a technology. Go to the technology window","type":"general gameplay info"}
				self.solar_system_object_link.messages.append(print_dict)
				
				


		#checking if any firms are for sale, if their bid_deadline is crossed and if so effectuates the sale
		for firm_instance in self.owned_firms.values():
			if firm_instance.for_sale:
				if firm_instance.for_sale_deadline > self.solar_system_object_link.current_date:
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
							self.solar_system_object_link.messages.append(print_dict)

							
							break
						else:
							winning_price = bids[i]
							for potential_winning_company in inverted_bids[winning_price]:
								if potential_winning_company.capital > winning_price:
									funding_not_ok = False
									winning_company = potential_winning_company
							
					
					if winning_company is not None:
						print_dict = {"text":firm_instance.name + " was for sale but was won by " + winning_company.name + " for the price of " + str(int(winning_price)) + " buying from " + self.name,"type":"base sales"}
						self.solar_system_object_link.messages.append(print_dict)
						
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
						firm_instance.for_sale_deadline = datetime.timedelta(30*6)+self.solar_system_object_link.current_date
						
					
		
		max_records_kept_in_account = 500
		self.company_accounting.append({"capital":self.capital,"date":self.solar_system_object_link.current_date})
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
				if (self.solar_system_object_link.current_date - self.last_firm_evaluation).days >  time_limit_of_firm_evaluation:
					self.last_firm_evaluation = self.solar_system_object_link.current_date
					self.evaluate_firms()
			
			#market evaluation
			time_limit_of_market_evaluation = int(((101 - self.company_database["evaluate_market_often"])/100.0) * (max_time_firm_and_market - min_time_firm_and_market) + min_time_firm_and_market)
			if (self.solar_system_object_link.current_date - self.last_market_evaluation).days >  time_limit_of_market_evaluation:
				self.last_market_evaluation = self.solar_system_object_link.current_date
				self.evaluate_market()
				
			#stock change evaluation - always done
			for firm_instance in self.owned_firms.values():
				firm_instance.execute_stock_change(self.solar_system_object_link.current_date)

			
			#supply evaluation
			#time_limit_of_supply_evaluation = ((101 - self.company_database["evaluate_supply_often"]) * max_time_supply_and_demand) / 100
			if self.automation_dict["Supply bidding (initiate selling bids)"]:
				time_limit_of_supply_evaluation = int(((101 - self.company_database["evaluate_supply_often"])/100.0) * (max_time_supply_and_demand - min_time_supply_and_demand) + min_time_supply_and_demand)
				if (self.solar_system_object_link.current_date - self.last_supply_evaluation).days >  time_limit_of_supply_evaluation:
					self.last_supply_evaluation = self.solar_system_object_link.current_date
					for firm_instance in self.owned_firms.values():
						firm_instance.calculate_supply_reaction()

			
			#demand evaluation
			if self.automation_dict["Demand bidding (initiate buying bids)"]:
				time_limit_of_demand_evaluation = int(((101 - self.company_database["evaluate_demand_often"])/100.0) * (max_time_supply_and_demand - min_time_supply_and_demand) + min_time_supply_and_demand)
				if (self.solar_system_object_link.current_date - self.last_demand_evaluation).days >  time_limit_of_demand_evaluation:
					self.last_demand_evaluation = self.solar_system_object_link.current_date
					for firm_instance in self.owned_firms.values():
						firm_instance.calculate_demand_reaction()


		
		else:
			if self != self.solar_system_object_link.current_player:
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
			if self.solar_system_object_link.message_printing["debugging"]:
				print_dict = {"text":"DEBUGGING: change_firm_size received a float " + str(size) + " -- correct this","type":"debugging"}
				self.solar_system_object_link.messages.append(print_dict)
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
						if not isinstance(firm_instance, base):
							firm_instance.close_firm()
							del self.owned_firms[firm_name]
							break
						else:
							firm_instance.for_sale = True
							firm_instance.for_sale_deadline = datetime.timedelta(30*6)+self.solar_system_object_link.current_date
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
							for company_instance in self.solar_system_object_link.companies.values():
								if firm_name in company_instance.owned_firms.keys():
									name_is_not_unique = True
					else:
				   		firm_name = name
					input_output_dict = {"input":{"labor":size},"output":{},"timeframe":30*6,"byproducts":{}}
					new_firm = research(self.solar_system_object_link, location,input_output_dict,self,firm_name)
					new_firm.size = size
					new_firm.last_consumption_date = self.solar_system_object_link.current_date
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
							for company_instance in self.solar_system_object_link.companies.values():
								if firm_name in company_instance.owned_firms.keys():
									name_is_not_unique = True
					else:
						firm_name = name
					new_firm = firm(self.solar_system_object_link,location,firm_specific_process,self,firm_name,technology_name)
					
					
					
					new_firm.size = size
					new_firm.last_consumption_date = self.solar_system_object_link.current_date
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
	
					



class firm():
	def __init__(self,solar_system_object,location,input_output_dict,owner,name,technology_name):
		self.name = name
		if not isinstance(location, base):
			raise Exception(self.name + " is a regular firm but received a location that was not a base: " + str(location))
		self.location = location
		self.picture_file = None
		self.owner = owner
		self.solar_system_object_link = solar_system_object
		self.last_consumption_date = self.solar_system_object_link.current_date
		self.last_accounting = self.solar_system_object_link.current_date
		self.accounting = []
		self.input_output_dict = input_output_dict
		self.stock_dict = {}
		self.technology_name = technology_name
		self.size = 0
	
		self.for_sale = False #can be set to True when firm is offered up for sale.
		self.for_sale_bids = {} # a dictionary with the bidder as object as keys, and the price they bid as value
		self.for_sale_deadline = None # a date at which the bidding contest is over
		
		#self.decision_data = self.process_decision_data(decision_data)
		for resource in self.solar_system_object_link.trade_resources:
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
				if self.solar_system_object_link.message_printing["debugging"]:
					print_dict = {"text":"DEBUGGING: In get_firm_background There are no JPGs in the given folder","type":"debugging"}
					self.solar_system_object_link.messages.append(print_dict)
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
		if self.owner == self.solar_system_object_link.current_player:
				print_dict = {"text":"The firm " + self.name + " is up for closing","type":"firm info"}
				self.solar_system_object_link.messages.append(print_dict)
		if isinstance(self,base):
			print self.name + " is up for closing, but it is a base - do something about this FIXME FIXME" #FIXME --- this should have been taken care of somehow else
		elif isinstance(self,merchant):
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
							if "buyer" in offer.keys():
								if self.name in offer["buyer"].name:
									delete_these.append(i)
							if "seller" in offer.keys():
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
						if "buyer" in offer.keys():
							if self.name in offer["buyer"].name:
								delete_these.append(i)
						if "seller" in offer.keys():
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
		timeframe = (self.solar_system_object_link.current_date - self.last_accounting).days
		
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
		#self.owner.company_accounting.append({"firm":self,"date":self.solar_system_object_link.current_date,"accounting_report":accounting_report})
		
		self.last_profit = accounting_report["profit"]
		return accounting_report
			
			
		
		
	
	
			

 
	
	def make_market_bid(self,market,own_offer):
		"""
		Function that takes a sell or buy offer (identified if it has "seller" or "buyer" in it
		and connects to the market to see if a corresponding offer exists. If it does it will connect
		seller and buyer. If not it will store the offer in market database. If market database is too
		long it will remove some of the highest price sell offers and the lowest price buy offers 
		"""
		
		#if self is a merchant we first need to assign the correct stock_dict 
		if isinstance(self, merchant): 
			if "seller" in own_offer.keys():
				self.stock_dict = self.to_stock_dict
			elif "buyer" in own_offer.keys():
				self.stock_dict = self.from_stock_dict
			else:
				raise Exception('unknown offer type')
			
			

		
		
		
		
		#defining basics and checking if the offer is valid
		if not (isinstance(own_offer["quantity"],int) or isinstance(own_offer["quantity"],long)):
			own_offer["quantity"] = int(own_offer["quantity"])
			if self.solar_system_object_link.message_printing["debugging"]: 
				print_dict = {"text":"DEBUGGING: The quantity given in an offer from " + str(self.name) + ", which is using " + str(self.decision_data["demand_function"]) + " and " + str(self.decision_data["supply_function"]) + " is not an integer. Try to keep it as integers","type":"debugging"}
				self.solar_system_object_link.messages.append(print_dict)

		if not isinstance(own_offer["price"],float):
			print_dict = {"text":"DEBUGGING: The price given in an offer from " + str(self.name) + ", which is using " + str(self.decision_data["demand_function"]) + " and " + str(self.decision_data["supply_function"]) + " is not a float. Try to keep it as floats","type":"debugging"}
			if self.solar_system_object_link.message_printing["debugging"]:
				self.solar_system_object_link.messages.append(print_dict)
				own_offer["price"] = float(own_offer["price"])
		resource = own_offer["resource"]
		
			 
		
		if "seller" in own_offer.keys():
			type = "sell_offer"
			opposite_bids = market["buy_offers"][resource]
			competing_bids = market["sell_offers"][resource]
			if self.stock_dict[resource] < own_offer["quantity"]:
				own_offer["quantity"] = int(self.stock_dict[resource])
				if self.solar_system_object_link.message_printing["debugging"]:
					print_dict = {"text":"DEBUGGING WARNING: adjusted " + resource + " sell offer from " + str(self.name) + " to " + str(own_offer["quantity"]) + " because of lack of resources  - you should try to correct this from the calculate_supply functions","type":"debugging"}
					self.solar_system_object_link.messages.append(print_dict)


				
		elif "buyer" in own_offer.keys():
			type = "buy_offer"
			opposite_bids = market["sell_offers"][resource]
			competing_bids = market["buy_offers"][resource]
			if self.owner.capital < (own_offer["price"] * own_offer["quantity"]):
				own_offer["quantity"] = int(self.owner.capital / own_offer["price"])
				if self.solar_system_object_link.message_printing["debugging"]:
					print_dict = {"text":"DEBUGGING WARNING: adjusted buy offer from " + str(self.name) + " to " + str(own_offer["quantity"]) +" because of lack of capital - you should try to correct this from the calculate_demand functions. The original price was " + str(own_offer["price"]) + " and the capital was " + str(self.owner.capital),"type":"debugging"}
					self.solar_system_object_link.messages.append(print_dict)

					   
		else:
			print "Unknown offer type in make_market_bid() function"
			raise Exception('unknown offer type')

		if own_offer["quantity"] < 0:
			if self.solar_system_object_link.message_printing["debugging"]:
				print_dict = {"text":"DEBUGGING WARNING: The quantity " + str(own_offer["quantity"]) + " offered by " + str(self.name) + " is not a positive amount. This should be corrected from market_decisions. It was set to 0 as a safeguard","type":"debugging"}
				self.solar_system_object_link.messages.append(print_dict)
			own_offer["quantity"] = 0
			
		#seeing how much resource can be found on market within the whished for price
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
			if isinstance(counterpart, merchant): 
				if "seller" in own_offer.keys():
					counterpart.stock_dict = counterpart.from_stock_dict
				elif "buyer" in own_offer.keys():
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
					if self.solar_system_object_link.message_printing["debugging"]:
						print_dict = {"text":"DEBUGGING WARNING: The quantity in an offer from " + counterpart.name + " was changed to " + str(opposite_bids[i]["quantity"]) + " during a " + type +" from " + str(self.name) + " regarding " + resource,"type":"debugging"}
						self.solar_system_object_link.messages.append(print_dict)
				
				quantity_found = opposite_bids[i]["quantity"] + quantity_found
				offers_of_interest.append(opposite_bids[i])
			 
			#if there are no more bid available at the price
			else:
				break
			i = i + 1
	


		#evaluating how much was found to be available on market
		if quantity_found > own_offer["quantity"]:
			balance_of_findings = quantity_found - own_offer["quantity"]

			if offers_of_interest[-1]["quantity"] - balance_of_findings < 0: #FIXME perhaps remove this
				print "DEBUGGING WARNING: I think I found it"
				print "balance_of_findings: " + str(balance_of_findings)
				print "offers_of_interest[-1][\"quantity\"]: " + str(offers_of_interest[-1]["quantity"])
				quantities = []
				for offer in offers_of_interest:
					quantities.append(offer["quantity"])
				print quantities
			
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
				if self.solar_system_object_link.message_printing["debugging"]:
					print_dict = {"text":"DEBUGGING WARNING: The quantity in an offer_of_interest from " + counterpart.name + " regarding " + resource + " was found to be " + str(offer_of_interest["quantity"]) + ". " + str(counterpart.name) + " has a calculate_supply_reaction parameter of " + str(counterpart.owner.company_database["calculate_supply_reaction"]) + " and a calculate_demand_reaction parameter of " + str(counterpart.owner.company_database["calculate_demand_reaction"]),"type":"debugging"}
					self.solar_system_object_link.messages.append(print_dict)

			counterparts_list.append(counterpart.name)
			
			if type == "sell_offer":
				counterpart = offer_of_interest["buyer"]
				counterpart.owner.capital = counterpart.owner.capital - offer_of_interest["price"] * offer_of_interest["quantity"] 
				counterpart.stock_dict[resource] = counterpart.stock_dict[resource] + offer_of_interest["quantity"] 
				self.owner.capital = self.owner.capital + offer_of_interest["price"] * offer_of_interest["quantity"] 
				self.stock_dict[resource] = self.stock_dict[resource] - offer_of_interest["quantity"] 
				
				if self.owner == self.solar_system_object_link.current_player or counterpart.owner == self.solar_system_object_link.current_player:
					print_dict = {"text":self.name + " sold " + str(offer_of_interest["quantity"]) + " units of " + resource + " to " + counterpart.name + " for a price of " + str(offer_of_interest["price"]),"type":"firm info"}
					self.solar_system_object_link.messages.append(print_dict)

				
				transaction_report = {"seller":self,"buyer":counterpart,"price":offer_of_interest["price"],"quantity":offer_of_interest["quantity"],"date":own_offer["date"],"resource":resource}
			elif type == "buy_offer":
				counterpart = offer_of_interest["seller"]
				counterpart.owner.capital = counterpart.owner.capital + offer_of_interest["price"] * offer_of_interest["quantity"] 
				counterpart.stock_dict[resource] = counterpart.stock_dict[resource] - offer_of_interest["quantity"] 
				self.owner.capital = self.owner.capital - offer_of_interest["price"] * offer_of_interest["quantity"] 
				self.stock_dict[resource] = self.stock_dict[resource] + offer_of_interest["quantity"] 
				if self.owner == self.solar_system_object_link.current_player or counterpart.owner == self.solar_system_object_link.current_player:
					print_dict = {"text":self.name + " bought " + str(offer_of_interest["quantity"]) + " units of " + resource + " from " + counterpart.name + " for a price of " + str(offer_of_interest["price"]),"type":"firm info"}
					self.solar_system_object_link.messages.append(print_dict)

				
				transaction_report = {"seller":counterpart,"buyer":self,"price":offer_of_interest["price"],"quantity":offer_of_interest["quantity"],"date":own_offer["date"],"resource":resource}
			else:
				raise typeError
			
			if isinstance(counterpart, merchant):
				counterpart.stock_dict = {} #to make sure no problems arise in the future 

			
			transaction_report["seller"].accounting.append(transaction_report)
			transaction_report["buyer"].accounting.append(transaction_report)
			market["transactions"][resource].append(transaction_report)
			
			if transaction_report["quantity"] < 0:
				#print 
				if self.solar_system_object_link.message_printing["debugging"]:
					print_dict = {"text":"DEBUGGING WARNING: The quantity in a " + type + " of " + resource + " by " + self.name + " was found to be " + str(transaction_report["quantity"]),"type":"debugging"}
					self.solar_system_object_link.messages.append(print_dict)
 
			
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
				if self.solar_system_object_link.message_printing["debugging"]:
					print_dict = {"text":"DEBUGGING MESSAGE: balance_of_findings was thought to be negative but was " + str(balance_of_findings) + " for " + self.name,"type":"debugging"}
					self.solar_system_object_link.messages.append(print_dict)
				
			
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
					if self.solar_system_object_link.message_printing["debugging"]:
						print_dict = {"text":"DEBUGGING WARNING: The quantity in an offer from " + self.name + " somehow ended up being negative","type":"debugging"}
						self.solar_system_object_link.messages.append(print_dict)
				
		
		
		#checking to see if the market database for this resource is getting too long. Deleting the worst offers in that case
		max_size_of_market = 50
		while len(competing_bids) > max_size_of_market:
			competing_bids.pop(-1)
		
		if isinstance(self, merchant):
			self.stock_dict = {} #to make sure no problems arise in the future 

			
		
		
	
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
			if (current_date - self.solar_system_object_link.start_date).days > 100: #because it is an error if there is no last_consumption_data
				if self.solar_system_object_link.message_printing["debugging"]:
					print_dict = {"text":"Small debugging warning. Did not find self.last_consumption_date for " + str(self.name) + " when doing execute_stock_change(). self.solar_system_object_link.start_date was used but this should be corrected at some point","type":"debugging"}
					self.solar_system_object_link.messages.append(print_dict)
 
			self.last_consumption_date = self.solar_system_object_link.start_date
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
						if isinstance(self,base):
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
					
			if time_span_days / timeframe > number_of_rounds and isinstance(self,base):
				if self.owner == self.solar_system_object_link.current_player:
					print_dict = {"text":self.name + " is a base, it is starving, but it will continue to produce","type":"base info"}
					self.solar_system_object_link.messages.append(print_dict)
				number_of_rounds = time_span_days / timeframe
			
			if number_of_rounds > 0:
				for input_resource in new_stock_level:
					self.stock_dict[input_resource] = new_stock_level[input_resource]
				for output_resource in self.input_output_dict["output"]:
					if not self.solar_system_object_link.trade_resources[output_resource]["storable"]:
						self.stock_dict[output_resource] = 0
						
					self.stock_dict[output_resource] = self.input_output_dict["output"][output_resource] * number_of_rounds + self.stock_dict[output_resource]

				for byproduct in self.input_output_dict["byproducts"]:
					self.location.home_planet.change_gas_in_atmosphere(byproduct,self.input_output_dict["byproducts"][byproduct])
					if self.owner == self.solar_system_object_link.current_player: 
						print_dict = {"text":"changed " + byproduct + " with " + str(self.input_output_dict["byproducts"][byproduct]) + " units on " + str(self.location.home_planet.name),"type":"firm info"}
						self.solar_system_object_link.messages.append(print_dict)

				
						
				
		

		

		


class base(firm):
	"""
	The class that holds all methods of the bases
	A base is a city or similar gathering of people on a planet. It has one owner, which is a company (on earth the countries are "companies")
	Algorithms exists that will calculate the demand of the people in the base. This is done in a sims-like fashion where different
	demand-types need to be fulfilled. It is done a little more advanced though, since for example lack of food will make the food demand
	soar much more than lack of consumer goods for example. See relevant function for details.
	
	The owner of the base decide what he wants to "pour" into the demand of the people. This is done by setting the wage for the base
	
	An owner can thus decide the "life-quality" level of the population. The benefits and penalties for doing this to the extreme should
	be as follows:
		starvation
		emigration
		low research
	FIXME This should be implemented later
	"""
	
	def __init__(self,solar_system_object,base_name,home_planet,base_data,owner):
#		self._signals["transaction"] = []
		
		self.location = self
		self.name = base_name
		self.base_name = base_name
		self.owner = owner
		self.home_planet = home_planet
		self.solar_system_object_link = solar_system_object
		
		self.for_sale = False #can be set to True when base is offered up for sale.
		self.for_sale_bids = {} # a dictionary with the bidder as object as keys, and the price they bid as value
		self.for_sale_deadline = None # a date at which the bidding contest is over
		
		
		# inserting initial base data values
		self.position_coordinate = (base_data["eastern_loc"], base_data["northern_loc"])
		self.gdp_per_capita_in_dollars = base_data["GDP_per_capita_in_dollars"]
		self.population = base_data["population"]
		self.GDP =  self.population * self.gdp_per_capita_in_dollars
		self.original_country = base_data["country"]
		self.wages = self.gdp_per_capita_in_dollars * 0.5 
		self.bitternes_of_base = 100.0 # setting a random variable to start with
		
		self.technology_name = "Base"
		self.size = self.population
		
		
		
		self.starving = "No" #reset to "No" every Year end, but set to "A little" or "A lot" by various events. Has impact on growth. 
		self.lacks_housing = "No" #reset to "No" every Year end, but set to "A little" or "A lot" by various events. Has impact on growth.
		
		self.picture_file = None
		self.is_on_dry_land = "Yes"
		self.trade_routes = {}
		self.last_accounting = self.solar_system_object_link.current_date
		self.accounting = []
		self.mining_opportunities = {}
		self.market = self.initialize_market() #a dictionary of traded resources as keys, and lists of past transaction as value
		
		
		self.input_output_dict = {"input":{"housing":1 * self.population,"food":1 * self.population,"consumer goods":1 * self.population},"output":{"labor":1 * self.population},"timeframe":30,"byproducts":{}} #however this is highly changeable
		

		self.stock_dict = {}
		for resource in self.solar_system_object_link.trade_resources:
			if self.solar_system_object_link.trade_resources[resource]["demanded_by_base"]:
				self.stock_dict[resource] = self.population
		for resource in self.input_output_dict["output"]:
			self.stock_dict[resource] = 0




	def calculate_demand_reaction(self):
		"""
		The calculation of the demand of a base is special because it is more elastic than the demand of firms. Simply put the idea
		is that you give the workers a wage (which is saved as self.wages for each base), and then THEY decide how they spend the money
		given their various demand as humans.
		
		Explained a little more each resource of interest to a population has a demand curve defined. A demand curve is a function of 
		the current stock of the resource. It is given as (a, b, c) where the function then is:
		
			y = c * ((x / self.population)^a + b)
				a must be below or equal to zero, b must be above or equal to zero, c must be above zero
				
		in the trade resources.txt where the values are specified a, b and c are known as
		a: base_demand_elasticity 
		b: base_demand_asymptote
		c: base_demand_intensity
		
		This explains what they do somewhat, but in other words: 
			The more negative a is, the steeper the demand increases when the resource is gone (ie. food etc)
			The more positive b is, the more constant is the demand, even though it is getting fulfilled (ie. education is always needed and more is better)
			The more positive c is, the more demand there generally is for this resource (ie. health care should not be higher in demand than food, even though they share the same profile)
			The "tipping" point for where "low-a" goods become flat is around self.population. One unit per population can therefore be thought of as a "pretty content" place. But of course content-ness is relative, so don't get stuck on it.
		
		An R function to plot the curves, just in case
			a<--0.5
			b<-0.5
			c<-1
			population = 10
			x = seq(0.00001 * population,population*2,population/1000)
			plot(x,((x/population)^a+b)*c)
		
		The function returns a dictionary with each of the resources of interest as keys, and a numerical of demand as value.
		
		Resources are then bought by the demands calculated. The quantity wanted is always 1 per person, but the price is in relation
		to the demand value. If all demand is for food, then the food price is set to the entire value of the wage per person. If even 
		demand is for food and housing, then the wage is only split between these two.
		
		The elasticity comes from the fact that the input_output_dict also changes with the demand. This is to reflect the fact
		that virtually no consumption of education exists if you are starving etc. (Maslow's theories if you will, but more mixed. You can
		both want housing and self realization - you just want one more). The input_output_dict is changed so that food demand is
		always 1 per person, but all other units are set by their ratio with food. If food demands are sufficently met, this can lead
		to very much higher demands for consumer goods etc.
		"""
		market = self.market
		if self.population <= 0:
			self.bitternes_of_base = 1500 #FIXME check at some point that this is an ok value for being bitter in an empty base
			return
		
		#First we calculate how the inhabitants feel about the world and what they demand
		base_demand_dict = {}
		for resource in self.solar_system_object_link.trade_resources:
			if self.solar_system_object_link.trade_resources[resource]["demanded_by_base"]:
				a = self.solar_system_object_link.trade_resources[resource]["base_demand_elasticity"]
				b = self.solar_system_object_link.trade_resources[resource]["base_demand_asymptote"]
				c = self.solar_system_object_link.trade_resources[resource]["base_demand_intensity"]
				
				resource_level = self.stock_dict[resource]
				if resource_level == 0:
					resource_level = 0.00001 * self.population #because we want the zero level to be the same no matter the size
				elif resource_level < 0:
					raise Exception(self.name + " had a negative amount (",str(resource_level),") of " + str(resource))
					
				demand_level = c * (((resource_level / float(self.population)) ** a) + b)
				
				base_demand_dict[resource] = demand_level
		
		
		
		
		#The bitterness of a base is the cumulative demand 
		bitternes_of_base = 0
		for demand_level_here in base_demand_dict.values():
			bitternes_of_base = bitternes_of_base + demand_level_here 
		self.bitternes_of_base = bitternes_of_base
		
		

		#When we convert we quite simply say that the wage given to the people is spent proportionally on the demands:
		for resource in base_demand_dict:
			#they always want to buy 1.0 unit per person - with the consumption rates given below this amounts to food for 10 turns, and the other goods in relation to this
			quantity_wanted = self.population

			#they always price the stuff at the level of demand and their income
			price = (base_demand_dict[resource] / bitternes_of_base) * (self.wages * self.population / quantity_wanted)

#			if self.name == "zygote":
#				print "in zygote price for " + resource + " is " + str(price) + " because the base_demand is + " + str(base_demand_dict[resource]) + " and bitternes_of_base " + str(bitternes_of_base) + " and self.wages " + str(self.wages) + " and quantity_wanted " + str(quantity_wanted)

			
			
			if quantity_wanted * price <= self.owner.capital and quantity_wanted > 0 and price > 0:
				buy_offer = {"resource":resource,"price":price,"buyer":self,"name":self.name,"quantity":quantity_wanted,"date":self.solar_system_object_link.current_date}
				
				self.make_market_bid(market,buy_offer)
				
				
		
		
			#finally we update the self.input_output_dict to reflect the new tastes of the inhabitants
			#the assumption here is that "food" is always at 0.1 unit per population, and the others are then consumed
			#by their relative demand ratio to food.
			self.input_output_dict["input"][resource] = int(0.1 *  ( base_demand_dict[resource] / base_demand_dict["food"] ) * self.population)


	def calculate_emigration(self):
		"""
		Function that calculates how many people will want to leave the city
		Tentative rules:
		compare bitterness_of_base to bitternes of trade_route partners. Calculate a fraction of the population that leaves based on this
		formula:
			
			percent emigration = 0.1 (bitterness_here - bitterness_there) / (max_bitternes_world - min_bitternes_world)
		
		This would make the situation with the worlds best city and the worlds worst yield a 10% migration and all otheres somewhere
		in between. Perhaps something with an exponential function or a threshold depending on route length.
		
		Also add to the emigration if the base 
			* is threathened by flooding (perhaps 20%)
			* there are any bases anywhere in the universe that offers prize-money for migration. (max 1% I think)
			 
		"""
		for trade_routes in self.trade_routes:
			if self.trade_routes[trade_routes]["endpoint_links"].index(self) == 1:
				neighbour = self.trade_routes[trade_routes]["endpoint_links"][0]
			else:
				neighbour = self.trade_routes[trade_routes]["endpoint_links"][1]
			
			
			if self.bitternes_of_base > neighbour.bitternes_of_base:
				percent_emigration_from_bitterness = (0.1 * (self.bitternes_of_base - neighbour.bitternes_of_base) / (self.solar_system_object_link.bitterness_of_world[1] - self.solar_system_object_link.bitterness_of_world[0]) ) / len(self.trade_routes) 
				
				if self.is_on_dry_land == "almost":
					percent_emigration_from_fear_of_flood = 0.2 / len(self.trade_routes)
					#print "DEBUGGING: 
					if self.owner == self.solar_system_object_link.current_player:
						print_dict = {"text":"the base: " + self.name + " is facing flooding and will experience a refuge surge","type":"base info"}
						self.solar_system_object_link.messages.append(print_dict)

				else:
					percent_emigration_from_fear_of_flood = 0
					
				
				
				people_leaving = int((percent_emigration_from_bitterness +  percent_emigration_from_fear_of_flood)* self.population)
				if people_leaving > 0:
					
#					if self.name in ["zygote","stockholm"]:
#						print self.name + " is neighbour with " + str(neighbour.name) + " - their relation should result in " + str(people_leaving) + " people emigrating from " + self.name + " this is " + str(int(100*(percent_emigration_from_bitterness +  percent_emigration_from_fear_of_flood))) + "%"
					
					if self.home_planet.solar_system_object_link.effectuate_growth_and_migration:
						if people_leaving < self.population:
							self.population = self.population - people_leaving
							neighbour.population = neighbour.population + people_leaving
						else:
							self.population = 0
							neighbour.population = neighbour.population + self.population
							if self.owner == self.solar_system_object_link.current_player: 
								print_dict = {"text":"The base " + self.name + " has lost all of its population due to migration","type":"base info"}
								self.solar_system_object_link.messages.append(print_dict)
						
		
			


	def calculate_growth_and_deaths(self):
		"""
		Function that calculates the "organic" size change of the base (ie. non-migration).
		Tentative rules:
		Fixed growth of say 2% per anno. 
		Perhaps these modifiers: 
			-20 % if self.stock_dict["food"] == 0
			-10 % if self.stock_dict["housing"] == 0
			-30 % if self.stock_dict["housing"] == 0 and terraformed_planet=False
		
		
		To perform this you'll need to include a self.was_starving and a self.lacked_housing variable that gets set
		to False at the end of each year, and that gets set to True if at anytime the food/housing supply hits zero.
		Perhaps instead of a logical, use "No", "Some", "A lot". The setting of these in times of trouble, should be set
		somewhere perhaps in the execute change functions. Also include an analysis of breathableness of the atmosphere
		and make the housing dependet on this.
		"""
		base_growth_percent = 0.022 #maximum global growth rate ever (1963) according to wikipeida 
		
		if self.starving == "A lot":
			starving_modifier = -0.2
		elif self.starving == "A little":
			starving_modifier = -0.1
		elif self.starving == "No":
			starving_modifier = 0.0
		else:
			raise Exception("Unknown self.starving parameter: " + str(self.starving))
		
		if self.lacks_housing == "A lot":
			housing_modifier = -0.2
		elif self.lacks_housing == "A little":
			housing_modifier = -0.1
		elif self.lacks_housing == "No":
			housing_modifier = 0.0
		else:
			raise Exception("Unknown self.lacks_housing parameter: " + str(self.lacks_housing))

		# if housing is lacking, a lot more people will die if the environment is unfriendly.
		if housing_modifier < 0:
			environmental_safety = self.home_planet.check_environmental_safety()
#			if self.name == "stockholm":
#				print self.home_planet.planet_data["athmospheric_surface_pressure_pa"]
#				print self.home_planet.planet_data["athmospheric_oxygen"]
#				print self.home_planet.planet_data["athmospheric_carbondioxide"]
#				print "For stockholm the answer is " + str(environmental_safety)
				
			if environmental_safety == "Barely":
				housing_modifier = housing_modifier * 2
			if environmental_safety == "No":
				housing_modifier = housing_modifier * 4
		
		growth_percent = base_growth_percent + starving_modifier + housing_modifier
		
#		if self.name in ["zygote","stockholm"]:
#			print self.name + " grew by " + str(int(100*growth_percent)) + "%, which equals " + str(int(self.population*growth_percent)) + " persons"

		if self.home_planet.solar_system_object_link.effectuate_growth_and_migration:
			self.population = int(self.population * (1.0 + growth_percent))
		
		
		


	def calculate_emissions(self):
		"""
		Function that calculates the gasous emmisions from a base
		Tentative rules:
			Perhaps all firms should just have an emission level, and then this function would sum them up.
		"""
		pass


			

	def initialize_market(self):
		""" 
		Function that fills in the self.market dictionary (a dictionary of traded resources as keys, and lists of 
		past transaction as value), with all resources and a few fake starting transaction to build future pricings on
		"""
		market = {}
		number_of_startup_transactions = 10
		market["sell_offers"] = {}
		market["buy_offers"] = {}
		market["transactions"] = {}

		for trade_resource in self.solar_system_object_link.trade_resources:
			market["sell_offers"][trade_resource] = []
			market["buy_offers"][trade_resource] = []
			market["transactions"][trade_resource] = []
			for i in range(1,number_of_startup_transactions):
				market["transactions"][trade_resource].append({"price":self.solar_system_object_link.trade_resources[trade_resource]["starting_price"],"buyer":None,"seller":None,"quantity":random.randint(500,1000),"date":self.solar_system_object_link.start_date-datetime.timedelta(0)})
		return market
		





		
	def get_base_background(self):
		"""
		Function that returns a background picture for each base
		It does this, by first investigating if a picture-name has already been assigned to the base
		then it scans the /images/base directory to see if a picture of the base exists here
		finally, if neither of the to other methods yield anything it assigns a random picture based on
		population (and fixes it into the instance so the same picture is used always)
		The pictures are imported, cropped and resized and served as surfaces for direct use
		"""
		if self.picture_file != None:
			file_name_and_path = self.picture_file
		else:
			if os.access(os.path.join("images","base",self.home_planet.planet_name),1):
				planet_base_dir = os.path.join("images","base",self.home_planet.planet_name)
			else:
				planet_base_dir = os.path.join("images","base","other")

			file_name = self.base_name + ".jpg"
			file_list = []
			for files in os.walk(planet_base_dir):
				for found_file in files[2]:
					file_list.append(found_file)

			if file_name in file_list:
				for files in os.walk(planet_base_dir):
					if file_name in files[2]:
						file_name_and_path = os.path.join(files[0],file_name)
			else:
				if self.population < 650000:
					size = "small_random"
				elif self.population > 1400000:
					size = "large_random"
				else:
					size = "medium_random"
				files_to_choose_from = os.listdir(os.path.join(planet_base_dir,size))
				files_to_choose_from_filtered = []
				for file_to_choose_from in files_to_choose_from:
					if file_to_choose_from.find(".jpg") != -1:
						files_to_choose_from_filtered.append(file_to_choose_from)
				number_of_files_to_pick_from = len(files_to_choose_from_filtered)
				if number_of_files_to_pick_from == 0:
					if self.solar_system_object_link.message_printing["debugging"]:
						print_dict = {"text":"DEBUGGING: in get_base_background there are no cities in the given folder","type":"debugging"}
						self.solar_system_object_link.messages.append(print_dict)

				else:
					my_pick = random.randrange(0,number_of_files_to_pick_from)
					file_name = files_to_choose_from_filtered[my_pick]
					file_name_and_path = os.path.join(planet_base_dir,size,file_name)
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
		
	def draw_base_window(self):
		"""
		The reason there is a special function for this is to keep to the same system as draw_planet.
		"""
		surface = self.get_base_background()
		return surface
		




	def calculate_trade_routes(self,planet):
		"""
		Function to calculate the trade routes of a base. Takes a planet instance and 
		uses that to calculate networks to other bases. 
		"""
		
		distance_dict = {}
		if self.population > 0:
			number_of_trade_routes = min(int(math.log10(self.population)), len(planet.bases)-1)
		else:
			number_of_trade_routes = 0
		
		position_one = (self.position_coordinate[0],self.position_coordinate[1])
		
		search_length = 0
		search_increment = 1
		while len(self.trade_routes) < number_of_trade_routes: 
			
			search_length = search_length + search_increment
			if search_length > 180:
				break
			for other_base in planet.bases.values():
				if other_base.base_name != self.base_name:
					position_two = (other_base.position_coordinate[0],other_base.position_coordinate[1])
					if position_one[0] - search_length < position_two[0] < position_one[0] + search_length and position_one[1] - search_length < position_two[1] < position_one[1] + search_length:
						if not other_base.base_name in self.trade_routes.keys():
							
							if len(other_base.trade_routes) < int(math.log10(other_base.population)):
								distance = planet.calculate_distance(position_one,position_two)
								
								transport_type = "ground transport"
								endpoints = [other_base.base_name,self.base_name] #try to remove this if you get the opportunity FIXME
								endpoint_links = [other_base,self]
								trade_route = {"distance":distance[0],"transport_type":transport_type,"endpoints":endpoints,"endpoint_links":endpoint_links} #converting distance from list to float (has to be list see planet
								self.trade_routes[other_base.base_name] = trade_route
								other_base.trade_routes[self.base_name] = trade_route
								#print trade_route
				
	
	def get_mining_opportunities(self,planet,resource,check_date = None, show_area=False):
		"""
		Calculates the mining_opportunities for a base. Takes a planet (to get the resource overlays)
		and a resource name. Saves the value in the self.resource_opportunities variable which is a dictionary
		for containing all the different resources as key
		Optional variables:
			check_date - the date when the opportunity check was performed. If given, this will be saved with the
						in the self.resource_opportunities variable, and used for check next time
			show_area - when this is set the, function will instead return an image with the resource overlay
						in question together with a designation of what area the base has its territory in
		"""
		update_interval = 1500 #days before a new update check should be made
		cost_addition_for_distance = 2 #the factor which is multiplied to the distance when calculating costs
		range_km = 400 #the width in km's of the farthest interval


		try:self.mining_opportunities[resource]
		except: 
			mining_opportunity_exists = False
		else:
			mining_opportunity_exists = True
			
		if mining_opportunity_exists and check_date is not None:
			if self.mining_opportunities[resource]["check_date"] is None:
				perform_calculation = True
			else:
				old_date = self.mining_opportunities[resource]["check_date"]
				
				time_difference = (check_date - old_date)
				print "time_difference: " + str(time_difference)
				if time_difference.days > update_interval:
					perform_calculation = True
				else:
					perform_calculation = False
		else:
			perform_calculation = True
		
		if perform_calculation is False and show_area is False:
			return self.mining_opportunities[resource]["sum_of_resources"]

		
		else:
			try: planet.resource_maps[resource]
			except:
				planet.calculate_resource_map(resource)
				
			resource_map = planet.resource_maps[resource]
			resource_map = resource_map.convert("L")
			distance_data = global_variables.distance_data
			#max_distance_in_matrix_degrees = distance_data["steps"] * distance_data["step_size"]
			planet_circumference = planet.planet_diameter_km * math.pi
			distance_matrix = distance_data["distance_matrix"]
			
			eastern_loc_degrees = self.position_coordinate[0]
			northern_loc_degrees = -self.position_coordinate[1]
			northern_loc_px = int((northern_loc_degrees + 90)/ 4)
			eastern_loc_px = int((eastern_loc_degrees + 180) / 4)
			resource_extrema = (resource_map.getextrema()[0] , resource_map.getextrema()[1] +1)
			
			#calculating a resource matrix - which is a dictionary, starting with distance as keys, then with positions at that distance as keys, and then finally with the resource_concentration as value.
			resource_matrix = {}
			distance_matrix_here = distance_matrix[(0,northern_loc_px)]
			
			max_distance_step_degrees = (float(range_km) / float(planet_circumference)) * 360.0
			max_distance_step_degrees_rounded = int(max_distance_step_degrees / distance_data["step_size"]) * distance_data["step_size"]
			if max_distance_step_degrees_rounded >= (distance_data["step_size"] * distance_data["steps"]):
				#print "it is long"
				max_distance_step_degrees_rounded = distance_data["step_size"] * (distance_data["steps"]-1)
			if max_distance_step_degrees_rounded == 0:
				max_distance_step_degrees_rounded = distance_data["step_size"] * 1
				#print "it is short"

			
			new_distance_matrix_here = {}
			for i in range(0,max_distance_step_degrees_rounded  + distance_data["step_size"] ,distance_data["step_size"]):
				new_distance_matrix_here[i] = distance_matrix_here[i]
				
			del distance_matrix_here
			distance_matrix_here = new_distance_matrix_here

			for distance in distance_matrix_here:
				resource_matrix[distance] = {}
				for zero_position in distance_matrix_here[distance]:
					
					real_position = (zero_position[0] +  eastern_loc_px,zero_position[1])
					
					if not 0 < real_position[0] < resource_map.size[0]:
						if 0 > real_position[0]:
							#print "too small"
							real_position = (zero_position[0] +  eastern_loc_px + resource_map.size[0],zero_position[1])
						else:
							#print "too big"
							real_position = (zero_position[0] +  eastern_loc_px - resource_map.size[0],zero_position[1])
	
					#print real_position
                                        real_position = (int(real_position[0]), int(real_position[1])) #this has been shown to be necessary on linux computeres for some reason
					resource_value = (100*(resource_map.getpixel(real_position) - resource_extrema[0])) / (resource_extrema[1] - resource_extrema[0])
					resource_matrix[distance][real_position] = resource_value
					
	
					
			
			
			
			if not show_area:
				#calculating the resource_intensity at the site
				sum_of_resources = 0
				for distance in resource_matrix:
					resources_at_distance = []
					for pixels in resource_matrix[distance]:
						resources_at_distance.append(resource_matrix[distance][pixels])
					sum_of_resources_at_distance = (float(sum(resources_at_distance) / len(resources_at_distance))) * (float(len(resource_matrix)) / float(distance_data["steps"])) 
					#normalize to the amounts of pixel in each distance category, and normalize to the number of 
					#distance categories (ie you dont want higher yield from the larger area far away from the base
					# not unless it is absolutely controlled by cost_addition_for_distance
					#and you don't want to punish bases on large planets.
					#print "at distance " + str(distance) + " the sum_of_resources_at_distance is " + str(sum_of_resources_at_distance) + " - these are found in " + str(len(resources_at_distance)) + " pixels"
					sum_of_resources = sum_of_resources_at_distance / ((distance+2) * cost_addition_for_distance) + sum_of_resources
					#print "at distance: " + str(distance) + " there is: " + str(sum_of_resources_at_distance) + " " + str(resource)
				
				
				#print "for resource " + str(resource) + " there is " + str(sum_of_resources) + " units at base " + str(self.base_name)
				self.mining_opportunities[resource] = {"sum_of_resources":sum_of_resources,"check_date":check_date}
				#print "self.mining_opportunities[resource]: " + str(self.mining_opportunities[resource]) 
				return sum_of_resources
					
			else: #creating the image of a resource overlay around a base
				territory_mask = Image.new("L",resource_map.size,0)
				for distance in resource_matrix:
					for pixels in resource_matrix[distance]:
						territory_mask.putpixel(pixels,255-(155* float(distance) / max(resource_matrix.keys())))
				
				return territory_mask
				
			 
		
		
		

		







	
	
class producer(firm):
	def __init__(self,input_output_dict):
		self.input_output_dict = input_output_dict
	


class primary(producer):
	pass

class farm(primary):
	pass


class mine(primary):
	pass




class secondary(firm):
	pass

class space(secondary):
	pass

class housing(secondary):
	pass



class tertiary(firm):
	pass

class research(tertiary):
	"""
	Special rules for research firms are included in this class, the most important being that they do not have any output
	from their input_output_dict, but instead add research points directly to the owning company.
	"""
	def __init__(self,solar_system_object,location,input_output_dict,owner,name):

		self.name = name
		self.owner = owner
		self.solar_system_object_link = solar_system_object
		if not isinstance(location, base):
			raise Exception(self.name + " is a research firm but received a location that was not a base: " + str(location))
		self.location = location
		self.picture_file = None
		self.last_consumption_date = self.solar_system_object_link.current_date
		self.last_accounting = self.solar_system_object_link.current_date
		self.accounting = []
		self.input_output_dict = input_output_dict
		
		self.stock_dict = {}
		self.technology_name = "research"
		self.size = 0
	
		self.for_sale = False #can be set to True when firm is offered up for sale.
		self.for_sale_bids = {} # a dictionary with the bidder as object as keys, and the price they bid as value
		self.for_sale_deadline = None # a date at which the bidding contest is over
		
		#self.decision_data = self.process_decision_data(decision_data)
		for resource in self.solar_system_object_link.trade_resources:
			self.stock_dict[resource] = 0

	def execute_stock_change(self,current_date):
		"""
		Function to calculate the research. Basically works the same way as the parent execute_stock_exchange functions
		but instead of having a commodity as output, it adds to the research of the owning company. 
		"""
		try: self.last_consumption_date
		except:
			if (current_date - self.solar_system_object_link.start_date).days > 100: #because it is an error if there is no last_consuptiom_data
				if self.solar_system_object_link.message_printing["debugging"]:
					print_dict = {"text":"Small debugging warning. Did not find self.last_consumption_date for " + str(self.name) + " when doing execute_stock_change(). self.solar_system_object_link.start_date was used but this should be corrected at some point","type":"debugging"}
					self.solar_system_object_link.messages.append(print_dict)
			self.last_consumption_date = self.solar_system_object_link.start_date
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
				if keep_calculating:
					number_of_rounds = new_number_of_rounds
			
			if number_of_rounds > 0:
				if self.owner == self.solar_system_object_link.current_player:
					print_dict = {"text":"for " + self.name + ", " + str(number_of_rounds) + " research rounds were completed adding research to " + self.owner.name,"type":"tech discovery"}
					self.solar_system_object_link.messages.append(print_dict)

				for input_resource in new_stock_level:
					self.stock_dict[input_resource] = new_stock_level[input_resource]
				
				# we give one research point per labor unit used
				self.owner.research = self.owner.research + number_of_rounds * self.input_output_dict["input"]["labor"] 


							


class merchant(tertiary):
	"""
	Special rules for merchant firms are included in this class, the most important being that demand and supply functions 
	should be quite different because they exist at two locations.
	"""
	def __init__(self,solar_system_object,from_location,to_location,input_output_dict,owner,name,transport_type,distance,resource):
		self.name = name
		self.owner = owner
		self.solar_system_object_link = solar_system_object
		if not isinstance(from_location, base):				
			raise Exception(self.name + " is a merchant firm but received a from_location that was not a base: " + str(from_location))
		self.from_location = from_location

		self.location = from_location #this is not really used, but for some less important checks throughout the code it is necessary

		if not isinstance(to_location, base):
			raise Exception(self.name + " is a merchant firm but received a to_location that was not a base: " + str(to_location))
		self.to_location = to_location

		
		self.picture_file = None
		self.last_consumption_date = self.solar_system_object_link.current_date
		self.last_accounting = self.solar_system_object_link.current_date
		self.accounting = []
		self.input_output_dict = input_output_dict
		
		
		self.stock_dict = {} #this is a virtual variable to which to_stock_dict and from_stock_dict is copied in the make_market_bid function, depending on bid direction. 
		self.to_stock_dict = {}
		self.from_stock_dict = {}
		
		self.technology_name = "merchant"
		self.size = 0
		
		self.transport_type = transport_type
		self.distance = distance
		self.resource = resource
	
		self.for_sale = False #can be set to True when firm is offered up for sale.
		self.for_sale_bids = {} # a dictionary with the bidder as object as keys, and the price they bid as value
		self.for_sale_deadline = None # a date at which the bidding contest is over
		
		#self.decision_data = self.process_decision_data(decision_data)
		for resource in self.solar_system_object_link.trade_resources:
			self.to_stock_dict[resource] = 0
			self.from_stock_dict[resource] = 0
			


	def execute_stock_change(self,current_date):
		"""
		Function to calculate the merchant activity.
		
		Essentially this function moves resources from the from_stock_dict to the to_stock_dict at the cost of transport
		 
		The amount of transportation units needed equals the amount of goods times the distance transported divided by 1000.
		"""
		
		
		
		transportation_capacity = int(math.floor((self.from_stock_dict[self.transport_type] * 1000.0) /  float(self.distance)))
		
		
		quantity_to_transport = min(self.from_stock_dict[self.resource], transportation_capacity)
		
		
		if quantity_to_transport > 0:
			self.to_stock_dict[self.resource] = self.to_stock_dict[self.resource] + quantity_to_transport
			
			self.from_stock_dict[self.resource] = self.from_stock_dict[self.resource] - quantity_to_transport
			
			self.from_stock_dict[self.transport_type] = self.from_stock_dict[self.transport_type] - int(math.ceil((quantity_to_transport * self.distance) / 1000.0))
			
			if self.owner == self.solar_system_object_link.current_player:
				print_dict = {"text":self.name + " transported " + str(quantity_to_transport) + " " + str(self.resource) + " from " + self.from_location.name + " to " + self.to_location.name + " using " + str(int((quantity_to_transport * self.distance) / 1000.0)) + " units of transport","type":"tech discovery"}
				self.solar_system_object_link.messages.append(print_dict)






	def calculate_demand_reaction(self):
		"""
		Function that will perform the calculate_intercity_demand_reaction function specified in the company database
		The database specifies numbers between 1 and 100, so this will have to be normalized
		to the number of entries in the databae
		"""
		
		functions_to_choose_from = global_variables.market_decisions.calculate_intercity_demand
		function_to_choose = int(math.ceil(len(functions_to_choose_from) * (self.owner.company_database["calculate_intercity_demand"] / 100.0)))
		functions_to_choose_from[function_to_choose](self)

		

	def calculate_supply_reaction(self):
		"""
		Function that will perform the calculate_intercity_supply_reaction function specified in the company database
		The database specifies numbers between 1 and 100, so this will have to be normalized
		to the number of entries in the databae
		"""
		pass
		functions_to_choose_from = global_variables.market_decisions.calculate_intercity_supply
		function_to_choose = int(math.ceil(len(functions_to_choose_from) * (self.owner.company_database["calculate_intercity_supply"] / 100.0)))
		functions_to_choose_from[function_to_choose](self)

							




