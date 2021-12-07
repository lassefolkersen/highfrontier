from . import firm
from . import global_variables
class base_construction(firm.firm):
        def isBaseConstruction(self):
		return True
	def solarSystem(self):
		return global_variables.solar_system

	"""
	Class containing the construction of a new base before it is shipped out
	"""
	def __init__(self,input_output_dict, location, name, home_planet, base_to_be_build_data, owner, size):	
		self.name = name
		self.location = location
		self.owner = owner
		self.picture_file = None
		self.technology_name = name
		self.last_consumption_date = self.solarSystem().current_date
		self.last_accounting = self.solarSystem().current_date
		self.accounting = []
		self.input_output_dict = input_output_dict
		self.stock_dict = {}
		self.size = size
		self.for_sale = False
		self.base_to_be_build_data = base_to_be_build_data
		
		for resource in self.solarSystem().trade_resources:
			self.stock_dict[resource] = 0

	def execute_stock_change(self,current_date):
		"""
		Function to calculate the production based on the input_output_dict.
		This is a special function for the base_construction class since its only function
		is to check when all resources are present, build the new base when this happens
		and close down itself.
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
			all_materials_present = True
			for input_resource in self.input_output_dict["input"]:
				if self.input_output_dict["input"][input_resource] > self.stock_dict[input_resource]: 
					all_materials_present = False
					break
			

			if all_materials_present:
				owner = self.base_to_be_build_data["owner"]
				name = self.base_to_be_build_data["name"]

				#checking population size
				if self.base_to_be_build_data["population"] > self.location.population:
					if self.base_to_be_build_data["population"] == 0:
						print_dict = {"text":"Population of " + str(self.location.name)+ " was zero and the construction have been cancelled.","type":"general gameplay info"}
						self.solarSystem().messages.append(print_dict)
						owner.change_firm_size(
											   location = self.location,
											   size = 0,
											   technology_name = self.technology_name)
						return
					else:
						print_dict = {"text":"Population of " + str(self.location.name)+ " was less than required for " + self.name + ". Only + " + str(self.base_to_be_build_data["population"]) + " people have been sent.","type":"general gameplay info"}
						self.solarSystem().messages.append(print_dict)
						self.base_to_be_build_data["population"] = self.location.population
				   
				#removing the population from building base
				self.location.population = self.location.population - self.base_to_be_build_data["population"]
				
				
				#if this is just a population transfer
				if self.base_to_be_build_data["destination_base"] is not None:
					destination_base = self.base_to_be_build_data["destination_base"] 
					destination_base.population = destination_base.population + self.base_to_be_build_data["population"] 
					print_dict = {"text":str(self.base_to_be_build_data["population"]) + " people have moved from " + str(self.location.name) + " to " + str(destination_base.name),"type":"general gameplay info"}
					self.solarSystem().messages.append(print_dict)
				
				#if this is a new base
				else:
					base_data_here = {
								 "northern_loc":self.base_to_be_build_data["northern_loc"],
								 "eastern_loc":self.base_to_be_build_data["eastern_loc"],
								 "population":self.base_to_be_build_data["population"],
								 "country":self.base_to_be_build_data["country"],
								 "GDP_per_capita_in_dollars":self.base_to_be_build_data["GDP_per_capita_in_dollars"]
								 }
					
					new_base = base(
										    self.solarSystem(),
										    base_name = name,
										    home_planet = self.base_to_be_build_data["home_planet"],
										    base_data = base_data_here,
										    owner = owner)
		
	
					#making the trade route from the founding base
					distance = self.base_to_be_build_data["distance_to_origin"]
					transport_type = self.base_to_be_build_data["transport_type_to_origin"]
					endpoints = [new_base.base_name,self.location.base_name] #try to remove this if you get the opportunity FIXME
					endpoint_links = [new_base,self.location]
					trade_route = {"distance":distance,"transport_type":transport_type,"endpoints":endpoints,"endpoint_links":endpoint_links} #converting distance from list to float (has to be list see planet
					new_base.trade_routes[self.location.base_name] = trade_route
					self.location.trade_routes[new_base.base_name] = trade_route
					
					owner.owned_firms[name] = new_base
					self.base_to_be_build_data["home_planet"].bases[name] = new_base
					owner.home_cities[name] = new_base
	
					print_dict = {"text":"Building a base named " + str(name),"type":"general gameplay info"}
					self.solarSystem().messages.append(print_dict)

				#closing and shutting down
				owner.change_firm_size(
									   location = self.location,
									   size = 0,
									   technology_name = self.technology_name)
