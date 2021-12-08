import global_variables
import math
import tertiary

class merchant(tertiary.tertiary):
	def solarSystem(self):
		return global_variables.solar_system
        def isMerchant(self):
            return True
	"""
	Special rules for merchant firms are included in this class, the most important being that demand and supply functions
	should be quite different because they exist at two locations.
	"""
	def __init__(self,solar_system_object,from_location,to_location,input_output_dict,owner,name,transport_type,distance,resource):
		self.name = name
		self.owner = owner
		if not from_location.isBase():
			raise Exception(self.name + " is a merchant firm but received a from_location that was not a base: " + str(from_location))
		self.from_location = from_location

		self.location = from_location #this is not really used, but for some less important checks throughout the code it is necessary

		if not to_location.isBase():
			raise Exception(self.name + " is a merchant firm but received a to_location that was not a base: " + str(to_location))
		self.to_location = to_location


		self.picture_file = None
		self.last_consumption_date = self.solarSystem().current_date
		self.last_accounting = self.solarSystem().current_date
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
		for resource in self.solarSystem().trade_resources:
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

			if self.owner == self.solarSystem().current_player:
				print_dict = {"text":self.name + " transported " + str(quantity_to_transport) + " " + str(self.resource) + " from " + self.from_location.name + " to " + self.to_location.name + " using " + str(int((quantity_to_transport * self.distance) / 1000.0)) + " units of transport","type":"tech discovery"}
				self.solarSystem().messages.append(print_dict)






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








