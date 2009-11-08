

import math
import random
import pygame
from xml.dom import minidom
import os
import global_variables
import primitives





class Tree():
	"""
	The tree is the class that holds all that exists. It started actually as an igraph object (from the igraph class),
	but because none of the igraph related functions were used it was migrated to instead by two variables called
	self.vertex_dict and self.edge_dict
	The self.vertex_dict is a dictionary of dictionaries, each key being the technology_name variable of the tech. The dictionary
	that is its value contains the following:
		cartesian_coordinates		the coordinates of the tech in cartesian coordinates
		polar_coordinates			the coordinates of the tech in polar coordinates (these two are calculated at the beginning and should not be changed)
		known_by					Dictionary of companies (names as keys) that know this tech. Can also be "everybody" in which case everybody, including newly started companies gets to know it.
		technology_name				The name of the technology. This is also the key by which it is called
		neighbours					list with links to the connected technologies.
		for_sale_by					Dictionary of with companies as keys and the price they sell at as values
	
	
	
	"""
	def __init__(self,coretree,solar_system_object_link):
		
		
		self.vertex_dict = {}
		self.vertex_dict["common knowledge"] = {}
		self.vertex_dict["common knowledge"]["input_output_dict"] = {"input":{},"output":{},"timeframe":None,"byproducts":{}}
		self.vertex_dict["common knowledge"]["polar_coordinates"] = (0,0)
		self.vertex_dict["common knowledge"]["cartesian_coordinates"] = (0,0)
		self.vertex_dict["common knowledge"]["known_by"] = "everybody"
		self.vertex_dict["common knowledge"]["for_sale_by"] = {}
		self.vertex_dict["common knowledge"]["technology_name"] = "common knowledge"
		self.vertex_dict["common knowledge"]["neighbours"] = []
		
		
		
		
		
		self.solar_system_object_link = solar_system_object_link
		
		self.tendency_to_choose_forward_parents = 0.5 #a number between 0 and 1. It describes the fraction of a sorted-by-distance list of potential parents (in the parent_area), to use in selecting parents  
		self.number_of_parents_list = [1,1,1,1,1,1,1,1,2,2,3,3,3,4] # list containing numbers of parents. A sample is taken from this list to determine the number of parents of any given new_iteration vertex

		self.click_map = {} # a dictionary with positions and vertex entries.


		self.coretree = coretree
		self.coretree.tree_link = self
		
		self.selected = None 
		
		self.zoomlevel = 0.02
		self.center = (0,0)
		self.stepsize = 60
		
	
	def receive_click(self,event):
		"""
		Function that handles everything that is done when the plot is clicked. Takes a the arguments:
			position	which is the (x,y) position with (0,0) being the topleft corner of the plot.
			click_type	which mousebutton is clicked (usually 1 is left and 3 is right)
			
		"""
		position = event.pos
		click_type = event.button
		click_spot = pygame.Rect(position[0]-4,position[1]-4,8,8)
		collision_test_result = click_spot.collidedict(self.click_map)

		if collision_test_result is not None:
			if click_type == 1:
				if self.selected != collision_test_result[1]:
					self.selected =  collision_test_result[1]
					if self.solar_system_object_link.current_player is not None:
						if self.selected in self.solar_system_object_link.current_player.known_technologies:
							destination = self.get_research_project(self.selected, self.solar_system_object_link.current_player.known_technologies)
							if destination is not None:
								self.solar_system_object_link.current_player.target_technology = destination["target_technology"]
								self.solar_system_object_link.current_player.target_technology_cost = int(destination["distance"] * self.solar_system_object_link.technology_research_cost)
								print_dict = {"text":self.solar_system_object_link.current_player.name + " selected to research from " + self.selected,"type":"general gameplay info"}
								self.solar_system_object_link.messages.append(print_dict)
	#							self.solar_system_object_link.current_player.target_technology = self.selected
							else:
								self.solar_system_object_link.current_player.target_technology = None
								print_dict = {"text":"Nothing useful can be discovered from " + self.selected,"type":"general gameplay info"}
								self.solar_system_object_link.messages.append(print_dict)
						else:
							self.solar_system_object_link.current_player.target_technology = None
							print_dict = {"text":self.selected + " is not known by " + self.solar_system_object_link.current_player.name + " and can not be used as origin of research","type":"general gameplay info"}
							self.solar_system_object_link.messages.append(print_dict)

				else:
					self.center = ( self.center[0]  - position[0] + global_variables.action_window_size[0]/2,   self.center[1] - (position[1] - global_variables.action_window_size[1]/2))
			elif click_type == 3:	
				self.center = ( self.center[0]  - position[0] + global_variables.action_window_size[0]/2,   self.center[1] - (position[1] - global_variables.action_window_size[1]/2))
                    
                
				if collision_test_result[1] != "common knowledge":
					message_text = collision_test_result[1] + " - "
					for put in ["input","output"]:
						message_text = message_text + put + ": "
						for resource in self.vertex_dict[collision_test_result[1]]["input_output_dict"][put]:
							message_text = message_text + resource + ": " + str(self.vertex_dict[collision_test_result[1]]["input_output_dict"][put][resource]) + ", "

					print_dict = {"text":message_text,"type":"general gameplay info"}
					self.solar_system_object_link.messages.append(print_dict)

			else:
				raise Exception("DEBUGGING: Unkown click_type " + str(click_type) + " in technology tree. This should not be able to happen")
				
		image = self.plot_total_tree(self.vertex_dict,zoomlevel=self.zoomlevel,center=self.center)
		
		
		return image
	
	def zoom(self,direction):
		"""
		Function that zooms the graph. Takes a character string denoting the direction
		direction	either "out" or "in"
		"""
		if direction == "out":
			self.zoomlevel = self.zoomlevel * 2
			self.center = (self.center[0]/2, self.center[1]/2)
		elif direction == "in":
			self.zoomlevel = self.zoomlevel / 2
			self.center = (self.center[0]*2, self.center[1]*2)
		else:
			Exception("The direction " + str(direction) + " was not recognized")
		
		image = self.plot_total_tree(self.vertex_dict,zoomlevel=self.zoomlevel,center=self.center)
		return image	
		
	def move(self,direction):
		"""
		Function that scrolls around the graph. Takes a character string denoting the direction
		direction	either "down","right","up", or "left"
		"""
		if direction == "down":
			self.center = (self.center[0], self.center[1] - self.stepsize)
		elif direction == "right":
			self.center = (self.center[0] - self.stepsize, self.center[1])
		elif direction == "up":
			self.center = (self.center[0], self.center[1] + self.stepsize)
		elif direction == "left":
			self.center = (self.center[0] + self.stepsize, self.center[1])
		else:
			Exception("The direction " + str(direction) + " was not recognized")
		
		image = self.plot_total_tree(self.vertex_dict,zoomlevel=self.zoomlevel,center=self.center)
		return image
		

	
	def get_research_project(self,origin_technology_name,known_technology_names):
		"""
		Function that returns a research project, when given an origin and a list of known_technologies. The known_technologies is
		just the list of known technologies as a list of strings. The origin is a string 
		with the name of a technology that is already known. The function will then select a child-technology from this. If any of 
		the children is already	known by another company, and there are other children that are not - the already known children 
		will not be selected. If there still is more than one possibility, it will select randomly between the options.
		
		If none is given as origin_technology, a random technology that has unknown children will be selected. 
		
		The function returns a dictionary with the keys:
			target_technology	the vertex targeted
			distance			the distance(or 'research points') to get there.
		"""

		known_technologies = {}
		for known_technology_name in known_technology_names:
			known_technologies[known_technology_name] = self.vertex_dict[known_technology_name]
		
		
		#if no origin_technology is selected, a technology with unknown neighbours is selected
		if origin_technology_name is None:
			possible_origins = []
			for technology_name in known_technologies:
				technology = self.vertex_dict[known_technology_name]
				for neighbour in technology["neighbours"]:
					if neighbour["technology_name"] not in known_technology_names:
						possible_origins.append(technology_name)
			if len(possible_origins) < 1:
				origin_technology_name = random.choice(known_technology_names)
				if self.solar_system_object_link.message_printing["debugging"]:
					print_dict = {"text":"DEBUGGING: There was a company that was not able to choose any origin technologies with unknown paths so a random known tech " + str(origin_technology) + " was chosen","type":"debugging"}
					self.solar_system_object_link.messages.append(print_dict)

			origin_technology_name = random.choice(possible_origins)
						
						
		if origin_technology_name not in known_technology_names:
			raise Exception("The origin_technology_name " + str(origin_technology_name) + " was not found among the known technologies for this company")
		 

		origin_technology_vertex = self.vertex_dict[origin_technology_name]
		
		#making a list of potential targets from the chosen origin_technology_vertex
		if len(origin_technology_vertex["neighbours"]) > 0:
			potential_targets = []
			for neighbour in origin_technology_vertex["neighbours"]:
				if neighbour["technology_name"] not in known_technology_names:
					potential_targets.append(neighbour)
		else:
#			print "DEBUGGING: The origin_technology selected: " + str(origin_technology_vertex["technology_name"]) + " does not have any connections to anything useful"
			return None 

		if len(potential_targets) < 1:
#			print "DEBUGGING: The origin_technology selected: " + str(origin_technology_vertex["technology_name"]) + " does not have any connections to anything that is not already known"
			return None
		
		
		#checking to see what connections from here are entirely unknown, and prioritize them if they exists.
		potential_unknown_targets = []
		for potential_target in potential_targets:
			if len(potential_target["known_by"]) > 0:
				potential_unknown_targets.append(potential_target)
		
		if len(potential_unknown_targets) < 1:
#			print "DEBUGGING: There were no potential entirely unknown targets, so a potential target that is known by other companies was chosen" #FIXME test this later
			pass
		else:
			potential_targets = potential_unknown_targets
			
		target_vertex = random.choice(potential_targets)
		
		distance = self.calculate_cartesian_distance(origin_technology_vertex["cartesian_coordinates"],target_vertex["cartesian_coordinates"])
		
		return {"target_technology":target_vertex,"distance":distance}
			
			 
	def check_technology_bid(self,known_technologies,technology):
		"""
		Function that checks if it is allowed to buy a given technology
		The rules are that only technologies that could potentially be research_targets can be bought - ie.
		it has to be connected to something known. On the other hand it can not be already known.
		Returns "already known", "ok", or "too advanced".
		"""
		
		if technology["technology_name"] in known_technologies.keys():
			return "already known"
		
		
		
		for neighbour in technology["neighbours"]:
			if neighbour["technology_name"] in known_technologies.keys():
				return "ok"
			
		return "too advanced"
		
		
		
		
		
		

	def techtree_to_surface(self, surface, vertex_dict, center, zoomlevel, point_of_view = None):
		"""
		The main plotting function for rendering tech trees.
		takes a surface and vertex_dixt, plus some positional info. It then renders the vertex_dict on the surface an returns it.
		
		Arguments are:
			surface					the surface to draw on
			vertex_dict				the dictionary of all vertexes (must contain edges as well)
			center					the center point of the plot
			zoomlevel				the zoomlevel of the plot
			point_of_view			if None the entire tree is shown, otherwise the tree is shown from the point_of_view of the company_instance given

		"""
		#readying for creation of click-map later
		self.click_map = {}
		click_size = 5
		
		#establishing which ones to plot
		if point_of_view is None:
			locally_known_vertices = vertex_dict
			globally_known_vertices = []
			unknown_vertices = []
		
		else: #find the technologies than can shown for this company
			locally_known_vertices = point_of_view.known_technologies
			globally_known_vertices = []
			unknown_vertices = []
			for vertex_name in vertex_dict:
				vertex = vertex_dict[vertex_name]
				if len(vertex["known_by"]) > 0 and vertex_name not in locally_known_vertices:
					globally_known_vertices.append(vertex_name)
				if len(vertex["known_by"]) == 0:
					unknown_vertices.append(vertex_name)


		
		
			
		for vertex_name in vertex_dict:
			vertex = vertex_dict[vertex_name]
			coordinates = vertex["cartesian_coordinates"]
			zoomed_coordinates = (coordinates[0] / zoomlevel, coordinates[1] / zoomlevel)
			transposed_coordinates = (zoomed_coordinates[0] + center[0], -zoomed_coordinates[1] + center[1])
			position = (int(transposed_coordinates[0]+global_variables.action_window_size[0]/2), int(transposed_coordinates[1]+global_variables.action_window_size[1]/2))

			#Drawing up the edges first
			if vertex_name in locally_known_vertices: 
				for neighbour in vertex["neighbours"]:
					neighbour_coordinates = neighbour["cartesian_coordinates"]
					neighbour_zoomed_coordinates = (neighbour_coordinates[0] / zoomlevel, neighbour_coordinates[1] / zoomlevel)
					neighbour_transposed_coordinates = (neighbour_zoomed_coordinates[0] + center[0], -neighbour_zoomed_coordinates[1] + center[1])
					neighbour_position = (int(neighbour_transposed_coordinates[0]+global_variables.action_window_size[0]/2), int(neighbour_transposed_coordinates[1]+global_variables.action_window_size[1]/2))
					if neighbour["technology_name"] in locally_known_vertices or neighbour["technology_name"] in globally_known_vertices:
						#draw edge in full
						pygame.draw.line(surface,(100,100,100),position,neighbour_position,1)
					else:
						#draw dotted line indicating direction
						delta_x = neighbour_transposed_coordinates[0] - transposed_coordinates[0]
						delta_y = neighbour_transposed_coordinates[1] - transposed_coordinates[1]
						polar_coordinate = self.cartesian_to_polar((delta_x,delta_y))
						polar_coordinate_shortened = (3, polar_coordinate[1])
						
						transposition = self.polar_to_cartesian(polar_coordinate_shortened)
						pygame.draw.line(surface,(100,100,100),(position[0] + 2*transposition[0], position[1]+ 2*transposition[1]),(position[0] + 3*transposition[0] ,position[1] + 3*transposition[1]),1)
						pygame.draw.line(surface,(100,100,100),(position[0] + 4*transposition[0], position[1]+ 4*transposition[1]),(position[0] + 5*transposition[0] ,position[1] + 5*transposition[1]),1)
						pygame.draw.line(surface,(100,100,100),(position[0] + 6*transposition[0], position[1]+ 6*transposition[1]),(position[0] + 7*transposition[0] ,position[1] + 7*transposition[1]),1)

			

			
			#Drawing the nodes that are known
			if vertex_name in locally_known_vertices or vertex_name in globally_known_vertices: 
				
				if 0 < position[0] < global_variables.action_window_size[0] and 0 < position[1] < global_variables.action_window_size[1]:
					
					click_rect = (position[0] - click_size, position[1] - click_size, 2 * click_size, 2 * click_size)
					self.click_map[click_rect] = vertex_name

					
					if vertex_name in locally_known_vertices:
						colour = (255,0,0)
					elif vertex_name in globally_known_vertices:
						colour = (125,125,125)
					else:
						raise Exception("missing vertex")

					pygame.draw.circle(surface,colour,position,6)
					pygame.draw.circle(surface,(0,0,0),position,6,1)
					
					
					#plotting labels that are not right next to the center.
					time_units_included = max(global_variables.action_window_size[0]/2,global_variables.action_window_size[1]/2) * zoomlevel
					if abs(vertex["polar_coordinates"][0]) > time_units_included * 0.3:
						label = global_variables.standard_font_small.render(vertex_name,False,(0,0,0))
						surface.blit(label,(int(position[0]),int(position[1])))
					
					if vertex_name == self.selected:
						pygame.draw.circle(surface,(255,255,255),position,5)
						
						
						
		
		
		return surface

	
	
	

	
	def plot_total_tree(self,vertex_dict,zoomlevel,center=(0,0)):
		"""
		Function that will first plot the distribution of subject areas, and then plot the new techs superimposed on them.
			vertex_dict				the vertices to plot. Will most often be the self.vertex_dict
			zoomlevel				time_units_per_pixel
			center					the center point. (0,0) is centered on origin.

		"""
		
		point_of_view = self.solar_system_object_link.current_player
		#for testing point-of-view
#		point_of_view_name = random.choice(self.solar_system_object_link.companies.keys())
#		point_of_view = self.solar_system_object_link.companies[point_of_view_name]
#		print "Chose " + str(point_of_view_name) + " for point of view"
		
		surface = pygame.Surface((global_variables.action_window_size[0],global_variables.action_window_size[1]))
		
		surface.fill((234,228,223))
				
		background = self.coretree.render_technology_web(surface,zoomlevel,global_variables.action_window_size[0],global_variables.action_window_size[1],center)
		
		foreground = self.techtree_to_surface(background,vertex_dict,center = center, zoomlevel = zoomlevel, point_of_view = point_of_view)

		return background
		


	def polar_to_cartesian(self,polar_coordinate):
		"""
		Converts polar (distance, direction) / (r, theta) to cartesian (x,y)
		"""
		direction_radians = math.radians(360-(polar_coordinate[1]-90))
		x	=	polar_coordinate[0] * math.cos(direction_radians)	
		y	=	polar_coordinate[0] * math.sin(direction_radians)
		
		return((x,y))
	
	def cartesian_to_polar(self,cartesian_coordinate):
		"""
		Converts cartesian (x, y) to polar (distance, direction) / (r, theta)
		"""
		r = math.sqrt(cartesian_coordinate[0]**2+cartesian_coordinate[1]**2)
		theta = math.atan2(cartesian_coordinate[0], cartesian_coordinate[1])
		#theta = theta - math.pi / 2
		theta_degrees = (int(math.degrees(theta)))
		
		if theta_degrees < 0:
			theta_degrees = theta_degrees + 360
		
		return((r,theta_degrees))
		
		
		
	def calculate_cartesian_distance(self,coordinate1,coordinate2):
		"""
		Calculates the distance between two cartesian coordinates
		"""
		delta_x = coordinate1[0] - coordinate2[0]
		delta_y = coordinate1[1] - coordinate2[1]
		distance = math.sqrt(delta_x ** 2 + delta_y ** 2)
		return distance
	

	
	
	def new_iteration(self,polar_coordinates):
		"""
		The function to add new technology to the tech tree. It works by receiving a location on the tree map (in
		polar coordiates). This can be controlled by any other function in a random scattering fashion - presently it
		is the implode_and_expand function that is the main controller.
		For the set of polar coordinates given as
			polar_coordinate	(r, theta)
		The new technology is created based on the data from the subject area in which it is found. It also is assigned
		parents from the vertexes in the square formed between the center point and the new vertex. Priority will be given to
		techs in the closer half of this square, but this can be controlled with the self.tendency_to_choose_forward_parents 
		variable in the init section.
		The ID of the newly formed vertex is returned.
		"""
		
		new_technology = {}


#		determining potential parents
		cartesian_coordinates = self.polar_to_cartesian(polar_coordinates)
		all_distances = {}
		all_cartesian_positions = {}
		all_polar_positions = {}
		for vertex_name in self.vertex_dict:
			vertex = self.vertex_dict[vertex_name]
			distance_to_here = self.calculate_cartesian_distance(vertex["cartesian_coordinates"],cartesian_coordinates)
			all_distances[distance_to_here] = vertex_name
			all_cartesian_positions[vertex["cartesian_coordinates"]] = vertex_name
			all_polar_positions[vertex["polar_coordinates"]] = vertex_name
		distance_list = all_distances.keys()
		distance_list.sort()
		if distance_list[0] < 1:
#			print "A vertex is at distance " + str(distance_list[0]) + " to the one being built - nothing was added. The polar coordinates were: " + str(polar_coordinates) + " and the distance_list was of length: " + str(len(distance_list))
			return None

		else:
			#rotate all other points with the same amount
			all_rotated_cartesian_positions = {}
			for polar_position in all_polar_positions:
				rotated_polar_position = (polar_position[0], polar_position[1] - (polar_coordinates[1] - 45))
				all_rotated_cartesian_positions[self.polar_to_cartesian(rotated_polar_position)] = all_polar_positions[polar_position]
			
			#potential parents
			potential_parents = []
			edge_of_square = polar_coordinates[0]* (1/math.sqrt(2))
			#print "The square is (0,0), (0,",str(edge_of_square),"),(",str(edge_of_square),",",str(edge_of_square),"),(0,",str(edge_of_square),")"
			for rotated_cartesian_position in all_rotated_cartesian_positions:
				if 0 <= (rotated_cartesian_position[0]) <= edge_of_square:
					if 0 <= (rotated_cartesian_position[1]) <= edge_of_square:
						potential_parents.append(all_rotated_cartesian_positions[rotated_cartesian_position])
			
			potential_parents_distances = {}
			for distance in all_distances:
				if all_distances[distance] in potential_parents:
					potential_parents_distances[distance] = all_distances[distance]
																				
			
			parent_distance_list = potential_parents_distances.keys()
			parent_distance_list.sort()
			number_of_potential_parents = int(len(parent_distance_list)*self.tendency_to_choose_forward_parents)
			if number_of_potential_parents >len(parent_distance_list):
				number_of_potential_parents = len(parent_distance_list)
				if self.solar_system_object_link.message_printing["debugging"]:
					print_dict = {"text":"DEBUGGING: Don't use self.tendency_to_choose_forward_parents above 1","type":"debugging"}
					self.solar_system_object_link.messages.append(print_dict)

			parent_distance_list_shortened = parent_distance_list[0:number_of_potential_parents] #take the closest half
			if len(parent_distance_list_shortened) == 0:
				parent_distance_list_shortened = [parent_distance_list[0]]
			
			close_potential_parents_list = []
			for potential_parent_distance in potential_parents_distances:
				if potential_parent_distance in parent_distance_list_shortened:
					close_potential_parents_list.append(potential_parents_distances[potential_parent_distance])
			


			#determine the type of technology 
			direction_dict = self.coretree.calculate_technology_web(polar_coordinates[0])
			inverted_direction_dict = primitives.invert_dict(direction_dict)
			inverted_direction_dict_keys = inverted_direction_dict.keys()
			inverted_direction_dict_keys.sort()
			for inverted_direction_dict_key in inverted_direction_dict_keys:
				if inverted_direction_dict_key > polar_coordinates[1]:
					found = True
					break
				else:
					found = False
			if not found:
				key_of_interest = inverted_direction_dict_keys[len(inverted_direction_dict_keys)-1]
			else:
				key_of_interest = inverted_direction_dict_keys[inverted_direction_dict_keys.index(inverted_direction_dict_key)-1]
			subject_name = inverted_direction_dict[key_of_interest][0]
			for vertex in self.coretree.subject_list:
				if vertex["technology_name"] == subject_name:
					subject_vertex = vertex
			new_technology["subject"] = subject_name
			
			#determining the new technology name
			not_unique = True
			tries = 0
			while not_unique:
				technology_name = self.get_name_for_vertex(subject_vertex)
				if technology_name not in self.vertex_dict.keys():
					not_unique = False
				else:
					if tries > 50:
						technology_name = "RANDOM_" + str(random.randint(1000,9999))
						raise Exception("DEBUGGING: DID NOT FIND A UNIQUE NAME in " + str(subject_name))

			new_technology["technology_name"] = technology_name


			

			

#			chose parents and number of parents randomly
			number_of_parents = random.choice(self.number_of_parents_list)
			if number_of_parents > len(close_potential_parents_list):
				number_of_parents = len(close_potential_parents_list)
			if number_of_parents < 1:
				raise Exception("We have got an orphan")
			selected_parents = random.sample(close_potential_parents_list,number_of_parents)
#			print "selected_parent: " + str(selected_parents)
			new_technology["neighbours"] = []
			for selected_parent_name in selected_parents:
				selected_parent = self.vertex_dict[selected_parent_name]
				new_technology["neighbours"].append(selected_parent)
				selected_parent["neighbours"].append(new_technology)


			
			new_technology["polar_coordinates"] = polar_coordinates
			new_technology["cartesian_coordinates"] = cartesian_coordinates
			
			
			
			
			######################
			#x<-seq(5,300,5)
			#
			#productivity_factor<-1
			#
			#input<-100 * ((x^(-0.2) + x * (-0.00))  / productivity_factor) 
			#output<-100 * (x^(0.2) + x * 0.001)
			#
			#plot(NULL,xlim=c(min(x),max(x)),ylim=c(0,max(max(input),max(output))))
			#points(x=x,y=input,col="red")
			#points(x=x,y=output,col="blue")

			
			
			#generate input_output_dict
			productivity_factor = 3 #multiplicator to the input vs output. The higher the more output per input in general
			input_exponent = -0.5 # should be negative. The more negative it is, the sharper the drop in input price with advancednes
			output_exponent = 0.2 # should be positive. The more positive it is, the sharper the increase in output with advancednes
			output_multiplicator = 0.001 # should be zero or positive. Multiplied directily to the advanceness level, so this determines linear progression
			break_even_radial_distance = 1 # can be used to alter the position of drops and plateus in tech return. Should probably be left to 1.
			percent_randomness = 0.2 #how much difference there can be between different input and outputs
			
			#add inherent productivity_multiplier in each technology
			productivity_factor = productivity_factor * subject_vertex["productivity_multiplier"]
			
			advancedness = polar_coordinates[0] / break_even_radial_distance
			total_value = {}
			total_value["input"] = 100 * ((advancedness ** input_exponent) / productivity_factor)
			total_value["output"] = 100 * ((advancedness ** output_exponent) + advancedness * output_multiplicator)
			input_output_dict = {}
			
			for put in ["input","output"]:
				put_dict = {}
				for resource in subject_vertex["abstract_process_dict"][put]:
					value_here = int(total_value[put] + ((random.random() - 0.5) * 2 * percent_randomness * total_value[put]))
					if value_here < 0:
						print advancedness
						print total_value
						raise Exception("Somehow the calculated value managed to become " + str(value_here) + " which is less than zero. Weird")
					elif value_here == 0:
						value_here = 1
					put_dict[resource] = value_here
				input_output_dict[put] = put_dict
			input_output_dict["timeframe"] = 30 #FIXME
			input_output_dict["byproducts"] = {}
			new_technology["input_output_dict"] = input_output_dict

			
			
			
			# calculating byproducts
			
			# rule 1: the CO2 emission from everything that has fossil fuel as input is proportional to the coal input +/- X % randomness
			percent_randomness = 0.2 # how many percent of ideal value, the final value can differ per resource - don't put more than 1.
			if "fossil fuel" in input_output_dict["input"].keys():
				fossil_fuel_input = input_output_dict["input"]["fossil fuel"]
				co2_emission = int(fossil_fuel_input + ((random.random() - 0.5) * 2 * percent_randomness * fossil_fuel_input))
				new_technology["input_output_dict"]["byproducts"]["carbondioxide"] = co2_emission
				 
			 
			# rule 2: the radioactive waste from everything that has fission source as input is proportional to the coal input +/- X % randomness (where X is high, to reflect the many various fission technologies)
			percent_randomness = 0.8 # how many percent of ideal value, the final value can differ per resource - don't put more than 1.
			if "fission source" in input_output_dict["input"].keys():
				fission_source_input = input_output_dict["input"]["fission source"]
				radioactive_waste_emission = int(fission_source_input + ((random.random() - 0.5) * 2 * percent_randomness * fission_source_input))
				new_technology["input_output_dict"]["byproducts"]["radioactive waste"] = radioactive_waste_emission 
			
			new_technology["known_by"] = {}
			new_technology["for_sale_by"] = {}
			
			self.vertex_dict[new_technology["technology_name"]] = new_technology
			
			return new_technology["technology_name"]


	
	def implode_and_expand(self,number_of_new_vertices = 150, start_with_standard_technologies=True):
		"""
		Function that adds new vertices. Arguments are:
			number_of_new_vertices				the number of new vertices to add. Will be added randomly, except for start_with_standard_technologies-cases
			start_with_standard_technologies	add a "standard technology" for each of the research areas available from the start.
		"""
		
		
		if start_with_standard_technologies: #then we check if they exist at time point "startout_value", and include them as "standard " + name.
			startout_value = 5 #the number of steps out from the center that standard technologies are placed. It is fault checked so they are not too close, but this will change the value. Use larger values for many coretechs
			technology_web = self.coretree.calculate_technology_web(startout_value)
			
			#only needed because the list of coretechs is a list of lists
			sorted_keys = []
			for coretech in self.coretree.subject_list:
				sorted_keys.append(coretech["technology_name"])

			# getting the correct theta for each
			for vertex in self.coretree.subject_list:
				if vertex["importance_function"] is not None:
					if vertex["technology_name"] in technology_web.keys():
						left_theta = technology_web[vertex["technology_name"]]
						position_in_sorted_keys = sorted_keys.index(vertex["technology_name"])
						neighbour = None
						new_order_of_sorted_keys = sorted_keys[(position_in_sorted_keys+1):len(sorted_keys)] + sorted_keys[0:position_in_sorted_keys]
						for potential_neighbour in new_order_of_sorted_keys:
							if potential_neighbour in technology_web.keys():
								neighbour = potential_neighbour
								break
						right_theta =  technology_web[neighbour]
						 
						#correcting for pos_eleven cases
						is_at_pos_eleven = right_theta < left_theta
						if is_at_pos_eleven:
							theta = (left_theta + right_theta+360) /2
						else:
							theta = (left_theta + right_theta) /2
						
						return_value = None
						while return_value is None:
							return_value = self.new_iteration((startout_value,theta))
							if return_value is None:
								startout_value = startout_value + 1
							else:
								technology_to_become_basic = self.vertex_dict[return_value]
								technology_to_become_basic["known_by"] = "everybody"
								technology_to_become_basic["technology_name"] = "basic " + technology_to_become_basic["subject"]
								self.vertex_dict[technology_to_become_basic["technology_name"]] = technology_to_become_basic
								del self.vertex_dict[return_value]
								
		for i in range(0,number_of_new_vertices):
			theta = random.randint(0,360)
			r = i * random.random()
			if start_with_standard_technologies:
				r = r + startout_value
			self.new_iteration((r,theta))

	
	
	def get_name_for_vertex(self,subject_vertex):
		"""
		Methods to create a name for a given subject. Takes the information from the co_descriptors_dict
		in the subject-vertex of interest
		"""
		
		
		adjectives = subject_vertex["co_descriptors"]["adjective"]
		connecting_words = subject_vertex["co_descriptors"]["connecting_word"]
		nouns = subject_vertex["co_descriptors"]["noun"]
		
		percent_with_connecting_words = (len(connecting_words) * 200) / float(len(nouns) +  len(adjectives))
		
		
		if percent_with_connecting_words > random.randint(0,100):
			if len(adjectives) == 0:
				chosen_adjectives = ""
			else:
				chosen_adjectives = adjectives[random.randint(0,len(adjectives)-1)] + " "
			if len(connecting_words) == 0:
				chosen_connecting_words = ""
			else:
				chosen_connecting_words = connecting_words[random.randint(0,len(connecting_words)-1)] + " "
	
			if len(nouns) == 0:
				raise Exception("No noun found for " + subject_vertex["technology_name"] + " it is not possible to create a name without")
			else:
				chosen_nouns = nouns[random.randint(0,len(nouns)-1)]
				technology_name = chosen_adjectives + chosen_connecting_words + chosen_nouns
		else:
			if len(adjectives) == 0:
				chosen_adjectives = ""
			else:
				chosen_adjectives = adjectives[random.randint(0,len(adjectives)-1)] + " "
			if len(nouns) == 0:
				raise Exception("No noun found for " + subject_vertex["technology_name"] + " it is not possible to create a name without")
			else:
				chosen_nouns = nouns[random.randint(0,len(nouns)-1)]
		
			technology_name = chosen_adjectives + chosen_nouns
		
		

		return str(technology_name)
		
	


class Backbone_Tree(Tree):
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
				
				if time_unit not in total_theta_dict[vertex["technology_name"]].keys(): #when the curve should not be drawn anymore
					#most of the time this will be true
					theta = None
					
					#but we check if it is a an end of line
					if i != 0:
						previous_time_unit = time_intervals[i-1]
						if previous_time_unit in total_theta_dict[vertex["technology_name"]].keys():
							new_order_of_coretech = self.order_of_core_techs[(vertex_id+1):len(self.order_of_core_techs)] + self.order_of_core_techs[0:vertex_id]
							for potential_neighbour in new_order_of_coretech:
#								print "previous_time_unit: " + str(previous_time_unit)
#								print "potential_neighbour: " + str(potential_neighbour)
								if previous_time_unit in total_theta_dict[potential_neighbour].keys():
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
				elif time_value_at_edge not in total_theta_dict[vertex].keys():
					pass
				#if not - we just put the between the two lines at the edge
				else:
					neighbour = None
					new_order_of_coretech = self.order_of_core_techs[(i+1):len(self.order_of_core_techs)] + self.order_of_core_techs[0:i]
					for potential_neighbour in new_order_of_coretech:
						if time_value_at_edge in total_theta_dict[potential_neighbour].keys():
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
			if abstract_process_dict_key not in abstract_process_dict.keys():
				raise Exception("The given abstract_process_dict must have the following keys: " + str(abstract_process_dict_keys) + " - did not find " + str(abstract_process_dict_key))
		for abstract_process_dict_key in abstract_process_dict.keys(): 
			if not isinstance(abstract_process_dict[abstract_process_dict_key],list):
				raise Exception("All values of the abstract_process_dict must be given as lists")
			if abstract_process_dict_key not in abstract_process_dict_keys:
				raise Exception("The given abstract_process_dict must only have the following keys: " + str(abstract_process_dict_keys) + " - no place for " + str(abstract_process_dict_key))
	
		# check to see that the co_descriptors are ok
		if not isinstance(co_descriptors,dict):
			raise Exception("co_descriptors must be dict, not a " + str(co_descriptors.__class__))
		co_descriptors_keys = ["connecting_word","adjective","noun"]
		for co_descriptors_key in co_descriptors_keys: 
			if co_descriptors_key not in co_descriptors.keys():
				raise Exception("The given co_descriptors must have the following keys: " + str(co_descriptors_keys) + " - did not find " + str(co_descriptors_key))
		for co_descriptors_key in co_descriptors.keys(): 
			if co_descriptors_key not in co_descriptors_keys:
				raise Exception("The given co_descriptors must only have the following keys: " + str(co_descriptors_keys) + " - no place for " + str(co_descriptors_key))
		for co_descriptors_values in co_descriptors.values(): 
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
				if crossover_value in crossoverdict.keys():
					if crossover_target_list not in crossoverdict[crossover_value]:
						crossoverdict[crossover_value].append(crossover_target_list)
				else:
					crossoverdict[crossover_value] = [crossover_target_list]

		
		#starting from the highest valued pairings each tech is assigned up to (but not more than) two neighbours-
		order_of_techs = []
		crossoverdict_keys = crossoverdict.keys()
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
						print order_of_techs
						print neighbour_dict
						print crossover_target_list
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
