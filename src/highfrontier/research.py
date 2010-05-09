import global_variables
import datetime

import tertiary

class research(tertiary.tertiary):
	def solarSystem(self):
		return global_variables.solar_system
	"""
	Special rules for research firms are included in this class, the most important being that they do not have any output
	from their input_output_dict, but instead add research points directly to the owning company.
	"""
        def isResearch(self):
            return True
	def __init__(self,solar_system_object,location,input_output_dict,owner,name):

		self.name = name
		self.owner = owner
		if not location.isBase():
			raise Exception(self.name + " is a research firm but received a location that was not a base: " + str(location))
		self.location = location
		self.picture_file = None
		self.last_consumption_date = self.solarSystem().current_date
		self.last_accounting = self.solarSystem().current_date
		self.accounting = []
		self.input_output_dict = input_output_dict
		
		self.stock_dict = {}
		self.technology_name = "research"
		self.size = 0
	
		self.for_sale = False #can be set to True when firm is offered up for sale.
		self.for_sale_bids = {} # a dictionary with the bidder as object as keys, and the price they bid as value
		self.for_sale_deadline = None # a date at which the bidding contest is over
		
		#self.decision_data = self.process_decision_data(decision_data)
		for resource in self.solarSystem().trade_resources:
			self.stock_dict[resource] = 0

	def execute_stock_change(self,current_date):
		"""
		Function to calculate the research. Basically works the same way as the parent execute_stock_exchange functions
		but instead of having a commodity as output, it adds to the research of the owning company. 
		"""
		try: self.last_consumption_date
		except:
			if (current_date - self.solarSystem().start_date).days > 100: #because it is an error if there is no last_consuptiom_data
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
				if keep_calculating:
					number_of_rounds = new_number_of_rounds
			
			if number_of_rounds > 0:
				if self.owner == self.solarSystem().current_player:
					print_dict = {"text":"for " + self.name + ", " + str(number_of_rounds) + " research rounds were completed adding research to " + self.owner.name,"type":"tech discovery"}
					self.solarSystem().messages.append(print_dict)

				for input_resource in new_stock_level:
					self.stock_dict[input_resource] = new_stock_level[input_resource]
				
				# we give one research point per labor unit used
				self.owner.research = self.owner.research + number_of_rounds * self.input_output_dict["input"]["labor"] 
