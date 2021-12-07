import math
import random
import pygame
from xml.dom import minidom
import os
from . import global_variables
from . import primitives
from . import Tree

class Backbone_Tree(Tree.Tree):
	"""
	A subclass of Tree that defines the core directions of technology.

	It contains a variable self.subject_list, which is an ordered list containing the technology subjects
	and their attached data as dictionaries. The import_core function reads a xml file at the location specified in init.
	The link_crossovers function, places the technologies next to each over based on their crossover value in the xml file
	(this is useful for putting related subjects next to each other).
	
	Other than that its main functions are to plot the subject areas on the tech tree
	 
	
	
	"""
	
	def __init__(self):
		
		self.subject_list = []
		
		self.import_core(os.path.join(os.getcwd(),"data","technology","technology.txt"))
		
		self.link_crossovers()
		

	

	def import_core(self,parsed_file_name):
		"""
		Function that will read in the xml file given as argument and add it to the core tech graph
		A core tech graph consists of a center vertex (initiated in __init__) and the core techs surrounding it. They are read from the
		parsed_file_name xml file.  
		"""
		parsed_file = minidom.parse(parsed_file_name)
		entries = parsed_file.getElementsByTagName("subject")
		for entry in entries:
			
			#getting title
			core_title_domlist = entry.getElementsByTagName("title")
			if len(core_title_domlist) > 1 or len(core_title_domlist) == 0:
				raise Exception("There is zero or more than one title for one of the subjects")
			core_title = str(core_title_domlist[0].childNodes[0].data)

			#getting productivity_multiplier
			core_productivity_multiplier_domlist = entry.getElementsByTagName("productivity_multiplier")
			if len(core_productivity_multiplier_domlist) > 1 or len(core_productivity_multiplier_domlist) == 0:
				raise Exception("There is zero or more than one productivity_multiplier for one of the subjects")
			core_productivity_multiplier = float(core_productivity_multiplier_domlist[0].childNodes[0].data)

			
			#getting abstract_process_dict
			abstract_process_dict_dom = entry.getElementsByTagName("abstract_process_dict")
			if len(abstract_process_dict_dom) > 1 or len(abstract_process_dict_dom) == 0:
				raise Exception("There is more or less than one abstract_process_dict for one of the subjects")
			abstract_process_dict = {}
			for put in ["input","output"]:
				put_domlist = abstract_process_dict_dom[0].getElementsByTagName(put)
				put_list = []
				if len(put_domlist) == 0:
					raise Exception("There is no " + put + " value for the subject " + core_title)
				for put_entry in put_domlist:
					if len(put_entry.childNodes) > 0:
						unicode_text = put_entry.childNodes[0].data
						put_list.append(str(unicode_text))
				abstract_process_dict[put] = put_list
			
			#getting co_descriptors
			co_descriptors_dict_dom = entry.getElementsByTagName("co_descriptors")
			if len(co_descriptors_dict_dom) > 1 or len(abstract_process_dict_dom) == 0:
				raise Exception("There is more or less than one co_descriptors for one of the subjects")
			co_descriptors_dict = {}
			for type in ["connecting_word","adjective","noun"]:
				type_domlist = co_descriptors_dict_dom[0].getElementsByTagName(type)
				type_list = []
				for type_entry in type_domlist:
					if len(type_entry.childNodes) > 0:
						unicode_text = type_entry.childNodes[0].data
						type_list.append(str(unicode_text))
		
				co_descriptors_dict[type] = type_list
			
			#getting crossover_dict
			crossover_dict_dom = entry.getElementsByTagName("crossover_dict")
			if len(crossover_dict_dom) == 0:
				raise Exception("There is no crossover_dict for one of the subjects")
			crossover_dict = {}
		
			crossover_domlist = crossover_dict_dom[0].getElementsByTagName("crossover")
			for type_entry in crossover_domlist:
				crossover_target_dom = type_entry.getElementsByTagName("crossover_target")
				if len(crossover_target_dom) > 1 or len(crossover_target_dom) == 0:
					raise Exception("There is " + str(len(crossover_target_dom)) + " crossover_target_dom for " + str(core_title))
				crossover_target = crossover_target_dom[0].childNodes[0].data

				crossover_weight_dom = type_entry.getElementsByTagName("crossover_weight")
				if len(crossover_weight_dom) > 1 or len(crossover_weight_dom) == 0:
					raise Exception("There is more or less than one crossover_weight_dom for one of the crossovers")
				crossover_weight = crossover_weight_dom[0].childNodes[0].data
				crossover_dict[str(crossover_target)] = int(crossover_weight)
			
			
			#importing importance_function
			importance_function_dom = entry.getElementsByTagName("importance_function")
			if len(importance_function_dom) > 1 or len(importance_function_dom) == 0:
				raise Exception("There is more or less than one importance_function for one of the subjects")
			importance_function = {}
			for type in ["a_value","b_value","c_value"]:
				type_domlist = importance_function_dom[0].getElementsByTagName(type)
				if len(type_domlist) == 1:
					for type_entry in type_domlist:
						if len(type_entry.childNodes) == 1:
							unicode_entry = type_entry.childNodes[0].data
							string_entry = str(unicode_entry)
							float_entry = float(string_entry)
						else:
							raise Exception("There is " + str(len(type_domlist)) + " entries in " + type + " in importance_functions for " + core_title) 
				else:
					raise Exception("There is " + str(len(type_entry.childNodes)) + " entries in " + type + " in importance_functions for " + core_title)
				importance_function[type] = float_entry
			
				
			self.add_core_vertex(label=core_title,abstract_process_dict=abstract_process_dict,co_descriptors=co_descriptors_dict,crossover_dict=crossover_dict,importance_function=importance_function,productivity_multiplier=core_productivity_multiplier)
		parsed_file.unlink()
		

	

		


				
		

	def calculate_technology_web(self,time_unit):
		"""
		Function to calculate which core_technology is chosen at a specific time_unit position.
		Takes the time_unit position, which has the same unit as given to the formulas in the importance_function.
		Outputs a dictionary with technology names as keys and the theta value of the left border as value. 
		"""
		theta_list = {}
		
		importance_vector = []
		for vertex in self.subject_list:
			a_value = vertex["importance_function"]["a_value"]
			b_value = vertex["importance_function"]["b_value"]
			c_value = vertex["importance_function"]["c_value"]
			
			importance_here = (time_unit ** 2) * a_value + time_unit * b_value + c_value
			if importance_here < 0:
				importance_here = 0
			
			importance_vector.append(importance_here)
		
		total_importance_value_at_this_time = float(sum(importance_vector)) #making it float to avoid stupid division round errors
		
		if total_importance_value_at_this_time <= 0:
			raise Exception("The total_importance_value_at_this_time was " + str(total_importance_value_at_this_time))
		
		importance_in_the_circle_before_here = 0
		for i, vertex in enumerate(self.subject_list):
			relative_importance_in_degrees_here = (360 * importance_vector[i]) / total_importance_value_at_this_time
			if relative_importance_in_degrees_here > 0:
				theta_list[vertex["technology_name"]] = importance_in_the_circle_before_here
				importance_in_the_circle_before_here = importance_in_the_circle_before_here + relative_importance_in_degrees_here
		return theta_list
		




		
	def render_technology_web(self,surface,zoomlevel,width,height,center=(0,0)):
		"""
		Paints the contents of the importance_dict. Takes the following arguments:
			surface									a surface to paint to
			zoomlevel								time_units_per_pixel
			width									width of the plot in pixels
			height									height of the plot in pixels
			center									the center of the plot. Give (0,0) for having the origin centered on the map
		"""
		
		#calculating the span of time units to calculate
		top_right_corner_cartesian = (center[0] + width/2, center[1] + height/2)
		top_left_corner_cartesian = (center[0] - width/2, center[1] + height/2)
		bottom_right_corner_cartesian = (center[0] + width/2, center[1] - height/2)
		bottom_left_corner_cartesian = (center[0] - width/2, center[1] - height/2)

		top_right_corner_polar = self.cartesian_to_polar(top_right_corner_cartesian)
		top_left_corner_polar = self.cartesian_to_polar(top_left_corner_cartesian)
		bottom_right_corner_polar = self.cartesian_to_polar(bottom_right_corner_cartesian)
		bottom_left_corner_polar = self.cartesian_to_polar(bottom_left_corner_cartesian)
		
		max_radius_in_pixels = max(top_right_corner_polar[0],top_left_corner_polar[0],bottom_right_corner_polar[0],bottom_left_corner_polar[0])
		min_radius_in_pixels = max(0,min(top_right_corner_polar[0],top_left_corner_polar[0],bottom_right_corner_polar[0],bottom_left_corner_polar[0])  - max(width,height)) #divide because of the cases where corners are farther than all of the edges
		
		max_theta = max(top_right_corner_polar[1],top_left_corner_polar[1],bottom_right_corner_polar[1],bottom_left_corner_polar[1])
		min_theta = min(top_right_corner_polar[1],top_left_corner_polar[1],bottom_right_corner_polar[1],bottom_left_corner_polar[1])

		
		if abs(center[0]) < width/2 and abs(center[1]) < height/2: #when the origin is on screen
			 min_radius_in_pixels = 0
			 max_theta = 360
			 min_theta = 0
		max_radius_in_time_units = max_radius_in_pixels * zoomlevel
		min_radius_in_time_units = min_radius_in_pixels * zoomlevel
		
		resolution_pixels_per_draw = 10.0 # pixels per point on plot
		resolution_timeunits_per_draw = resolution_pixels_per_draw * float(zoomlevel) # time_units per point on plot
		
		steps_to_calculate = int(math.ceil(max_radius_in_time_units / resolution_timeunits_per_draw))
		
		
		#creating a list of time_intervals of interest
		time_intervals = []
		for i in range(steps_to_calculate):
			time_interval = min_radius_in_time_units + i * resolution_timeunits_per_draw
			time_intervals.append(time_interval)
		
		
		total_theta_dict = {} #what a great name! Basically just a dict with theta values for each technology_name at each time step
		for vertex in self.subject_list:
			total_theta_dict[vertex["technology_name"]] = {}
		
		for time_unit in time_intervals:
			theta_dict = self.calculate_technology_web(time_unit)
			for vertex_name in theta_dict:
				total_theta_dict[vertex_name][time_unit] = theta_dict[vertex_name]

		
		for vertex_id, vertex in enumerate(self.subject_list):
			
			cartesian_list = []
			for i, time_unit in enumerate(time_intervals):
				
				if time_unit not in list(total_theta_dict[vertex["technology_name"]].keys()): #when the curve should not be drawn anymore
					#most of the time this will be true
					theta = None
					
					#but we check if it is a an end of line
					if i != 0:
						previous_time_unit = time_intervals[i-1]
						if previous_time_unit in list(total_theta_dict[vertex["technology_name"]].keys()):
							new_order_of_coretech = self.order_of_core_techs[(vertex_id+1):len(self.order_of_core_techs)] + self.order_of_core_techs[0:vertex_id]
							for potential_neighbour in new_order_of_coretech:
#								print "previous_time_unit: " + str(previous_time_unit)
#								print "potential_neighbour: " + str(potential_neighbour)
								if previous_time_unit in list(total_theta_dict[potential_neighbour].keys()):
									neighbour = potential_neighbour
									break
							theta = total_theta_dict[neighbour][previous_time_unit]

				else:
					theta = total_theta_dict[vertex["technology_name"]][time_unit]
				
				if theta is not None:
					cartesian_coordinate = self.polar_to_cartesian((time_unit / zoomlevel, theta))
					transposed_cartesian_coordinate = (cartesian_coordinate[0] + width/2 + center[0],  height - (cartesian_coordinate[1] + height/2 - center[1]))
					cartesian_list.append(transposed_cartesian_coordinate)


			if len(cartesian_list) > 1:	
				pygame.draw.lines(surface, (0,0,0), False, cartesian_list)
		
		for i, vertex in enumerate(self.order_of_core_techs):
		
			theta = None
			r = None
			
			time_value_at_edge = time_intervals[-10] # the place where we put the text
			
			# if the band exists at all
#			print "vertex: " + str(vertex)
			if len(total_theta_dict[vertex]) > 0:
			
				# if the band disappears before the end
				if sorted(total_theta_dict[vertex].keys())[-1] != time_intervals[-1]:
					theta_list = []
					for time in time_intervals: 
						try:	theta_list.append(total_theta_dict[vertex][time])
						except:
							pass #doesn't matter
					
					if len(theta_list) > 0:
						theta = theta_list[len(theta_list)-1]
						r = len(theta_list) * resolution_timeunits_per_draw
	
				
				# if the band appears after the end
				elif time_value_at_edge not in list(total_theta_dict[vertex].keys()):
					pass
				#if not - we just put the between the two lines at the edge
				else:
					neighbour = None
					new_order_of_coretech = self.order_of_core_techs[(i+1):len(self.order_of_core_techs)] + self.order_of_core_techs[0:i]
					for potential_neighbour in new_order_of_coretech:
						if time_value_at_edge in list(total_theta_dict[potential_neighbour].keys()):
							neighbour = potential_neighbour
							break
					
					
					left_theta = total_theta_dict[vertex][time_value_at_edge]
					right_theta = total_theta_dict[neighbour][time_value_at_edge]
					
					is_at_pos_eleven = right_theta < left_theta
					
	
					if is_at_pos_eleven:
						theta = (left_theta + right_theta+360) /2
					else:
						theta = (left_theta + right_theta) /2
					
					r = time_value_at_edge# * resolution_timeunits_per_draw
					
		
			
		
				#print "for " + vertex["technology_name"] + " " + str((r,theta))
				if theta is not None and r is not None:
					cartesian_coordinate= self.polar_to_cartesian((r, theta))
					
					scaled_cartesian_coordinate = (int(cartesian_coordinate[0] / zoomlevel), int(cartesian_coordinate[1] / zoomlevel))
					
					center_transposed_cartesian_coordinate = (scaled_cartesian_coordinate[0] + center[0], scaled_cartesian_coordinate[1] - center[1])
					
					frame_transposed_cartesian_coordinate = (int(center_transposed_cartesian_coordinate[0] + width/2),  int(height - (center_transposed_cartesian_coordinate[1] + height/2 )))
					#scaled_cartesian_coordinate = (int(transposed_cartesian_coordinate[0] / zoomlevel), int(transposed_cartesian_coordinate[1] / zoomlevel))
					text = global_variables.standard_font_small_bold.render(vertex,False,(0,0,0))
					text_size = global_variables.standard_font_small_bold.size(vertex)
					
					surface.blit(text,(frame_transposed_cartesian_coordinate[0] - text_size[0]/2 , frame_transposed_cartesian_coordinate[1]))
		
		return surface

		

		
		
	def add_core_vertex(self,label,abstract_process_dict,co_descriptors,crossover_dict,importance_function,productivity_multiplier):
		"""
		Function to add another core vertex to the backbone.
		Takes the following arguments
			label					The title of the technology concept (ie. ground transport, solar energy generation, nuclear energy generation, iron mining)
			abstract_process_dict	An abstraction of the input_output_dict, which contains input and output but no numbers of relativity. 
			co_descriptors			A dictionary with the keys: 'connecting_word', 'adjective' and 'noun'. Contains words for generating labels for all non_core technologies leading to this core_tech
			crossover_dict			A dictionary containing other core_techs as keys, and integers between 1 and 100 as values. Indicating the degree of crossover between two related disciplines.
			importance_function		A dictionary with the keys "a_value", "b_value" and "c_value". Defines the importance of a technology as time progresses. The importance function is defined as y = x^2 * a + x * b + c, where x takes the value 0 at global_variables.starting_data
			productivity_multiplier	A number that will decide how much output relative to input the core tech should be tuned to relative to others.
		"""
		
		if not isinstance(label,str):
			raise Exception("Label must be string, not a " + str(label.__class__))
	
		# check to see that the abstract_process_dict is ok
		if not isinstance(abstract_process_dict,dict):
			raise Exception("process_dict must be dict, not a " + str(process_dict.__class__))
		abstract_process_dict_keys = ["input","output"]
		for abstract_process_dict_key in abstract_process_dict_keys: 
			if abstract_process_dict_key not in list(abstract_process_dict.keys()):
				raise Exception("The given abstract_process_dict must have the following keys: " + str(abstract_process_dict_keys) + " - did not find " + str(abstract_process_dict_key))
		for abstract_process_dict_key in list(abstract_process_dict.keys()): 
			if not isinstance(abstract_process_dict[abstract_process_dict_key],list):
				raise Exception("All values of the abstract_process_dict must be given as lists")
			if abstract_process_dict_key not in abstract_process_dict_keys:
				raise Exception("The given abstract_process_dict must only have the following keys: " + str(abstract_process_dict_keys) + " - no place for " + str(abstract_process_dict_key))
	
		# check to see that the co_descriptors are ok
		if not isinstance(co_descriptors,dict):
			raise Exception("co_descriptors must be dict, not a " + str(co_descriptors.__class__))
		co_descriptors_keys = ["connecting_word","adjective","noun"]
		for co_descriptors_key in co_descriptors_keys: 
			if co_descriptors_key not in list(co_descriptors.keys()):
				raise Exception("The given co_descriptors must have the following keys: " + str(co_descriptors_keys) + " - did not find " + str(co_descriptors_key))
		for co_descriptors_key in list(co_descriptors.keys()): 
			if co_descriptors_key not in co_descriptors_keys:
				raise Exception("The given co_descriptors must only have the following keys: " + str(co_descriptors_keys) + " - no place for " + str(co_descriptors_key))
		for co_descriptors_values in list(co_descriptors.values()): 
			if not isinstance(co_descriptors_values,list):
				raise Exception("The co_descriptor dictionary values must all be lists")
			else:
				for co_descriptors_value in co_descriptors_values:
					if not isinstance(co_descriptors_value,str):
						raise Exception("The lists in the co_descriptor values must only contain strings")
				
		# check to see that the crossover_dict is ok
		if not isinstance(crossover_dict,dict):
			raise Exception("crossover_dict must be dict, not a " + str(crossover_dict.__class__))
		for crossover in crossover_dict:
			if not isinstance(crossover_dict[crossover],int):
				raise Exception("The crossover dict contained a value at key " + crossover + " was not an integer but a " + str(crossover_dict[crossover].__class__))
			if crossover_dict[crossover] < 1 or crossover_dict[crossover] > 100:
				raise Exception("The crossover dict contained a value at key " + crossover + " had a value of " + str(crossover_dict[crossover]) + " which is not allowed")
	
	
		#build the new vertex
		new_technology = {}
		new_technology["technology_name"] = label
		new_technology["abstract_process_dict"] = abstract_process_dict
		new_technology["co_descriptors"] = co_descriptors
		new_technology["crossover_dict"] = crossover_dict
		new_technology["importance_function"] = importance_function
		new_technology["productivity_multiplier"] = productivity_multiplier
		
		self.subject_list.append(new_technology)

		
		
	def link_crossovers(self):
		"""
		Function that will check the crossover_dict of each vertex in the self.subject_list and shuffle the entries around as needed
		Basically the idea is just to identify the highest valued pair, put them next to each, then identify the next highest valued pair
		and put them next to each other and continue until tech start appear where they already have two neighbours. When this happens
		The crossover is ignored.
		"""		
		#making a dictionary with the crossover values as keys and the pairings they correspond to on lists as values
		neighbour_dict = {}
		crossoverdict = {}
		for vertex in self.subject_list:
			neighbour_dict[vertex["technology_name"]] = []
			for crossover_target in vertex["crossover_dict"]:
				crossover_value = vertex["crossover_dict"][crossover_target]
				crossover_target_list = [crossover_target,vertex["technology_name"]]
				crossover_target_list.sort()	 
				if crossover_value in list(crossoverdict.keys()):
					if crossover_target_list not in crossoverdict[crossover_value]:
						crossoverdict[crossover_value].append(crossover_target_list)
				else:
					crossoverdict[crossover_value] = [crossover_target_list]

		
		#starting from the highest valued pairings each tech is assigned up to (but not more than) two neighbours-
		order_of_techs = []
		crossoverdict_keys = list(crossoverdict.keys())
		crossoverdict_keys.sort(reverse=True)
		for crossoverdict_key in crossoverdict_keys:
			for crossover_target_list in crossoverdict[crossoverdict_key]:
				if (len(neighbour_dict[crossover_target_list[0]]) < 2) and (len(neighbour_dict[crossover_target_list[1]]) < 2):
					if (crossover_target_list[0] not in order_of_techs) and (crossover_target_list[1] not in order_of_techs): 
						order_of_techs.append(crossover_target_list[0])
						order_of_techs.append(crossover_target_list[1])
					elif crossover_target_list[0] not in order_of_techs:
						index = order_of_techs.index(crossover_target_list[1])
						order_of_techs.insert(index,crossover_target_list[0])
					elif crossover_target_list[1] not in order_of_techs:
						index = order_of_techs.index(crossover_target_list[0])
						order_of_techs.insert(index,crossover_target_list[1])
					else:
						print(order_of_techs)
						print(neighbour_dict)
						print(crossover_target_list)
						raise Exception("problem for " + str(crossover_target_list) + " this has been observed before if crossoverdicts are not equal")
					neighbour_dict[crossover_target_list[0]].append(crossover_target_list[1])
					neighbour_dict[crossover_target_list[1]].append(crossover_target_list[0])
		
		for technology in self.subject_list:
			if technology["technology_name"] not in order_of_techs:
				order_of_techs.append(technology["technology_name"])
		
		self.order_of_core_techs = order_of_techs
		new_subject_list = []
		
		indices = []
		for technology in self.subject_list:
			indices.append(order_of_techs.index(technology["technology_name"]))
		for index in indices:	
			new_subject_list.append(self.subject_list[index])
			
			
		self.subject_list = new_subject_list
		




#







#
#
#
#
#
#backbone_tree_here = Backbone_Tree()
#technology_tree = Tree(backbone_tree_here,None)
#technology_tree.implode_and_expand()
#
#
##somevertex_name = random.sample(technology_tree.vertex_dict.keys(),10)
##print somevertex_name
##print technology_tree.vertex_dict["basic solar energy"].keys()
#
#known = []
#for vertex in technology_tree.vertex_dict:
#	known.append(vertex)
#	if random.randint(0,3) == 1:
#		break
#if "basic solar energy" not in known:
#	known = known + ["basic solar energy"]
#
#
#test = technology_tree.get_research_project("basic solar energy", known)
#print test["distance"]
#print test["target_technology"]["technology_name"]
