from . import market_decisions
from . import research
from . import firm
from . import global_variables
import datetime
from . import primitives
import os
import random
import string
import math
import time

import Image, ImageChops
import pygame
import pygame

import Image
import os
from . import firm
import random
import datetime
import math
from . import global_variables


class base(firm.firm):
	def solarSystem(self):
		return global_variables.solar_system
        def isBase(self):
            return True

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
		self.location = self
		self.name = base_name
		self.base_name = base_name
		self.owner = owner
		self.home_planet = home_planet
		
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
		
		self.terrain_type = self.check_terrain_type()
		
		self.starving = "No" #reset to "No" every Year end, but set to "A little" or "A lot" by various events. Has impact on growth. 
		self.lacks_housing = "No" #reset to "No" every Year end, but set to "A little" or "A lot" by various events. Has impact on growth.
		
		self.picture_file = None
		self.is_on_dry_land = "Yes"
		self.trade_routes = {}
		self.last_accounting = self.solarSystem().current_date
		self.last_mining_check = self.solarSystem().current_date
		self.mining_check_interval = random.randint(6000,10000) #just to keep it from cropping up everybody at the same time
		self.accounting = []
		self.mining_opportunities = {}
		self.mining_performed = {} #a dictionary with the amount of mined materials taken from the ground, used for updating mining.
		for resource in self.solarSystem().mineral_resources:
			self.mining_performed[resource] = 0

		
		self.market = self.initialize_market() #a dictionary of traded resources as keys, and lists of past transaction as value
		
		
		self.input_output_dict = {"input":{"housing":1 * self.population,"food":1 * self.population,"consumer goods":1 * self.population},"output":{"labor":1 * self.population},"timeframe":30,"byproducts":{}} #however this is highly changeable
		

		self.stock_dict = {}
		
		for resource in self.solarSystem().trade_resources:
			if self.solarSystem().trade_resources[resource]["demanded_by_base"]:
				self.stock_dict[resource] = self.population
		
		for resource in self.input_output_dict["output"]:
			self.stock_dict[resource] = 0


	def check_terrain_type(self):
		"""
		Function that checks what type of terrain the base is in.
		The reason for a per-base decision is
		"""
		if self.position_coordinate == (None, None):
			return "Space"
		
		#check atmospheric safety
		environmental_safety = self.home_planet.check_environmental_safety()
		
		#check local safety (radiation)
		
		return environmental_safety


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
		for resource in self.solarSystem().trade_resources:
			if self.solarSystem().trade_resources[resource]["demanded_by_base"]:
				a = self.solarSystem().trade_resources[resource]["base_demand_elasticity"]
				b = self.solarSystem().trade_resources[resource]["base_demand_asymptote"]
				c = self.solarSystem().trade_resources[resource]["base_demand_intensity"]
				
				resource_level = self.stock_dict[resource]
				if resource_level == 0:
					resource_level = 0.00001 * self.population #because we want the zero level to be the same no matter the size
				elif resource_level < 0:
					raise Exception(self.name + " had a negative amount (",str(resource_level),") of " + str(resource))
					
				demand_level = c * (((resource_level / float(self.population)) ** a) + b)
				
				base_demand_dict[resource] = demand_level
		
		
		
		
		#The bitterness of a base is the cumulative demand 
		bitternes_of_base = 0
		for demand_level_here in list(base_demand_dict.values()):
			bitternes_of_base = bitternes_of_base + demand_level_here 
		self.bitternes_of_base = bitternes_of_base
		
		

		#When we convert we quite simply say that the wage given to the people is spent proportionally on the demands:
		for resource in base_demand_dict:
			#they always want to buy 1.0 unit per person - with the consumption rates given below this amounts to food for 10 turns, and the other goods in relation to this
			quantity_wanted = self.population

			#they always price the stuff at the level of demand and their income
			price = (base_demand_dict[resource] / bitternes_of_base) * (self.wages * self.population / quantity_wanted)

			
			if quantity_wanted * price <= self.owner.capital and quantity_wanted > 0 and price > 0:
				buy_offer = {"resource":resource,"price":price,"buyer":self,"name":self.name,"quantity":quantity_wanted,"date":self.solarSystem().current_date}
				
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
				percent_emigration_from_bitterness = (0.1 * (self.bitternes_of_base - neighbour.bitternes_of_base) / (self.solarSystem().bitterness_of_world[1] - self.solarSystem().bitterness_of_world[0]) ) / len(self.trade_routes) 
				
				if self.is_on_dry_land == "almost":
					percent_emigration_from_fear_of_flood = 0.2 / len(self.trade_routes)
					#print "DEBUGGING: 
					if self.owner == self.solarSystem().current_player:
						print_dict = {"text":"the base: " + self.name + " is facing flooding and will experience a refuge surge","type":"base info"}
						self.solarSystem().messages.append(print_dict)

				else:
					percent_emigration_from_fear_of_flood = 0
					
				
				
				people_leaving = int((percent_emigration_from_bitterness +  percent_emigration_from_fear_of_flood)* self.population)
				if people_leaving > 0:
					if self.solarSystem().effectuate_migration:
						if people_leaving < self.population:
							self.population = self.population - people_leaving
							neighbour.population = neighbour.population + people_leaving
						else:
							self.population = 0
							neighbour.population = neighbour.population + self.population
							if self.owner == self.solarSystem().current_player: 
								print_dict = {"text":"The base " + self.name + " has lost all of its population due to migration","type":"base info"}
								self.solarSystem().messages.append(print_dict)
						

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
			if self.terrain_type in ["Barely survivable"]:
				housing_modifier = housing_modifier * 2
			if self.terrain_type in ["Space","No atmosphere","Radiation"]:
				housing_modifier = housing_modifier * 4
		
		growth_percent = base_growth_percent + starving_modifier + housing_modifier
		

		if self.solarSystem().effectuate_growth:
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

		for trade_resource in self.solarSystem().trade_resources:
			market["sell_offers"][trade_resource] = []
			market["buy_offers"][trade_resource] = []
			market["transactions"][trade_resource] = []
			for i in range(1,number_of_startup_transactions):
				market["transactions"][trade_resource].append({"price":self.solarSystem().trade_resources[trade_resource]["starting_price"],"buyer":None,"seller":None,"quantity":random.randint(500,1000),"date":self.solarSystem().start_date-datetime.timedelta(0)})
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
			if self.position_coordinate == (None, None):
				planet_base_dir = os.path.join("images","base","space")
			else:
				if os.access(os.path.join("images","base",self.home_planet.planet_name),os.R_OK):
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
					if self.solarSystem().message_printing["debugging"]:
						print_dict = {"text":"DEBUGGING: in get_base_background there are no cities in the given folder","type":"debugging"}
						self.solarSystem().messages.append(print_dict)

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
		if self.terrain_type != "Space": #only ground bases
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
				for other_base in list(planet.bases.values()):
					if other_base.base_name != self.base_name:
						position_two = (other_base.position_coordinate[0],other_base.position_coordinate[1])
						if position_one[0] - search_length < position_two[0] < position_one[0] + search_length and position_one[1] - search_length < position_two[1] < position_one[1] + search_length:
							if not other_base.base_name in list(self.trade_routes.keys()):
								
								if len(other_base.trade_routes) < int(math.log10(other_base.population)):
									distance = planet.calculate_distance(position_one,position_two)
									
									transport_type = "ground transport"
									endpoints = [other_base.base_name,self.base_name] #try to remove this if you get the opportunity FIXME
									endpoint_links = [other_base,self]
									trade_route = {"distance":distance[0],"transport_type":transport_type,"endpoints":endpoints,"endpoint_links":endpoint_links} #converting distance from list to float (has to be list see planet
									self.trade_routes[other_base.base_name] = trade_route
									other_base.trade_routes[self.base_name] = trade_route
		else: #space station trade route
			possible_space_ports = []
			for other_base in list(planet.bases.values()):
				if other_base.terrain_type != "Space": #don't connect to other space stations
					if other_base.original_country == self.original_country:
						possible_space_ports.append(other_base)
#			print self.name + " has " +str(len(possible_space_ports))  + " possible space port. no 1 is " + str(possible_space_ports[0].name)
			if len(possible_space_ports) == 0:
				raise Exception("No possible space ports for " + str(self.name))
			space_port = random.choice(possible_space_ports)
			distance = planet.gravity_at_surface #fixme? for now the distance is set to gravity_at_surface to give the escape velocity
			transport_type = "space transport"
			endpoints = [space_port.base_name,self.base_name] #try to remove this if you get the opportunity FIXME
			endpoint_links = [space_port,self]
			trade_route = {"distance":distance,"transport_type":transport_type,"endpoints":endpoints,"endpoint_links":endpoint_links} #converting distance from list to float (has to be list see planet
			self.trade_routes[space_port.base_name] = trade_route
			space_port.trade_routes[self.base_name] = trade_route
						
			


	
	def get_mining_opportunities(self,planet,resource):
		"""
		Calculates the mining_opportunities for a base. Takes a planet (to get the resource overlays)
		and a resource name. Saves the value in the self.resource_opportunities variable which is a dictionary
		for containing all the different resources as key
		"""
		
		cost_addition_for_distance = 2 #the factor which is multiplied to the distance when calculating costs
		range_km = 400 #the width in km's of the farthest interval
		
		self.last_mining_check = self.solarSystem().current_date


		#for space stations
		if self.terrain_type == "Space":
			self.mining_opportunities[resource] = 0
			return self.mining_opportunities[resource]

		if resource == "food":
			if self.terrain_type == "Breathable atmosphere":
				food_multiplier = 1.0
			elif self.terrain_type == "Survivable atmosphere":
				food_multiplier = 0.8
			else:
				food_multiplier = 0.4
			
			earth_sun_distance = self.solarSystem().planets["earth"].planet_data["semi_major_axis"]
			effective_sun_distance = float(max(self.home_planet.planet_data["semi_major_axis"], earth_sun_distance))
			food_multiplier = ((earth_sun_distance / effective_sun_distance) ** 0.5) * food_multiplier
			self.mining_opportunities[resource] = food_multiplier * 20
			return food_multiplier * 20

		else:#mineral resources
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
			resource_extrema = (50, 255)

			
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
					
		
		
		#adjusting the resource levels of the planet in case there has been extensive mining
		if self.mining_performed[resource] > 0:
			deposit_reduction = (self.mining_performed[resource] / 50000.0) / global_variables.mineral_deposit_size_multiplier
			if deposit_reduction > 1:
				deposit_reduction_rest = deposit_reduction % 1
				self.mining_performed[resource] = 50000.0 * global_variables.mineral_deposit_size_multiplier * deposit_reduction_rest 
				for distance in resource_matrix:
					for pixels in resource_matrix[distance]:
						original_tuple = planet.resource_maps[resource].getpixel(pixels)
						
						reduced_value = int(original_tuple[1] - int(deposit_reduction) * (4 - distance))
						new_tuple= (original_tuple[0], reduced_value, original_tuple[2])
						
						planet.resource_maps[resource].putpixel(pixels,new_tuple)
					

		
		
		
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
		self.mining_opportunities[resource] = sum_of_resources
		#print "self.mining_opportunities[resource]: " + str(self.mining_opportunities[resource]) 
		return sum_of_resources
				

		
		
		
		
	def draw_mining_area(self, planet, overlay_image):
		"""
		creating the image of a resource overlay around a base
		"""
		update_interval = 1500 #days before a new update check should be made
		cost_addition_for_distance = 2 #the factor which is multiplied to the distance when calculating costs
		range_km = 400 #the width in km's of the farthest interval

		#for space stations
		if self.terrain_type == "Space":
			return overlay_image

		distance_data = global_variables.distance_data
		planet_circumference = planet.planet_diameter_km * math.pi
		distance_matrix = distance_data["distance_matrix"]
		
		eastern_loc_degrees = self.position_coordinate[0]
		northern_loc_degrees = -self.position_coordinate[1]
		northern_loc_px = int((northern_loc_degrees + 90)/ 4)
		eastern_loc_px = int((eastern_loc_degrees + 180) / 4)
		resource_extrema = (50, 255)
		
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

		base_area_mask = Image.new("L",overlay_image.size,0)
		for distance in distance_matrix_here:
			for pixels in distance_matrix_here[distance]:
				colour = 255-(155* float(distance) / max(distance_matrix_here.keys()))
				pixel_transposed = (eastern_loc_px + pixels[0], pixels[1])
				if not 0 < pixel_transposed[0] < overlay_image.size[0]:
					if 0 > pixel_transposed[0]:
						pixel_transposed = (pixel_transposed[0] + overlay_image.size[0],pixel_transposed[1])
					else:
						pixel_transposed = (pixel_transposed[0] - overlay_image.size[0],pixel_transposed[1])
				base_area_mask.putpixel(pixel_transposed,colour)

		blank_image = Image.new(overlay_image.mode, overlay_image.size, (0,0,0))
		overlay_image.paste(blank_image,None,base_area_mask)
		return overlay_image	
