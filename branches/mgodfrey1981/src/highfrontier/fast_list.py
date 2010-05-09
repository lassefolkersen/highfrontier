import vscrollbar
import math
import global_variables
import pygame
import primitives

import time
import random

class fast_list():
    """
    A list similar to the ScrolledList, but faster
    """
    def __init__(self, surface, tabular_data, rect, column_order = None, sort_by = "rownames"):
        self.surface = surface
      

        self.rect = rect
        self.rect_for_main_list = pygame.Rect(self.rect[0],self.rect[1] + 20,self.rect[2]-20,self.rect[3]-20)
        self.text_height = global_variables.courier_font.size("abcdefghijklmnopqrstuvxysABCDEFGHIJKLMNOPQRSTU")[1]
        self.left_list_frame = 5 # how much the text in the list is indented
        self.top_frame_width = 5 # this is a guesstimate of how much the Frame is filling
        self.title = None #either None (in which case it can't be rendered" or else a dictionary with key "text", containing a string with the text to write, and key "entry_span" containing another dictionary with the column names as values and their length in pixels as keys
        self.original_tabular_data = tabular_data
        self.receive_data(tabular_data,column_order = column_order, sort_by = sort_by)
        self.selected = None
        self.selected_name = None

        self.reverse_sorting = False
        self.create_fast_list()

                
#        if self.title is not None:
#            self.render_title()

        
    def create_fast_list(self):
        """
        The creation function. Doesn't return anything, but saves self.list_frame variable and renders using the self.renderer.
        Needs to have something saved to self.data first 
        """
        

        title_surface = pygame.Surface((self.rect[2],20))
        title_surface.fill((224,218,213))
        if self.title is not None:
            rendered_titleline = global_variables.courier_font.render(self.title["text"],True,(0,0,0))
            title_surface.blit(rendered_titleline,(self.left_list_frame, 0))
        self.surface.blit(title_surface,(self.rect[0],self.rect[1]))
        
        
        #expanding rectangle to catch clicks on title
#        self.rect = pygame.Rect(self.rect[0],self.rect[1] - self.text_height, self.rect[2], self.rect[3] + self.text_height)

        self.lines_visible = int( math.floor( self.rect[3] / self.text_height) - 1)
        
        
        
        self.vscrollbar = vscrollbar.vscrollbar(self.surface, self.scrolling, (self.rect[0] + self.rect[2] - 20, self.rect[1]), self.rect[3], (0,len(self.data)), range_seen = self.lines_visible, start_position = 0, function_parameter=None)
        self.update_fast_list()
        pygame.display.flip()
        
    def scrolling(self,position,function_parameter):
        self.update_fast_list()
    
    def receive_click(self,event):
        if event.pos[0] > self.rect[0] + self.rect[2] - 20:
            self.vscrollbar.activate(event.pos)
            pygame.display.flip()
        else:
            if self.title is not None:
                if event.pos[1] < self.rect[1] + self.text_height:
                    for key in self.title["entry_span"].keys():
                        if key[0] < event.pos[0] and event.pos[0] < key[1]:
                            sort_by_this_column = self.title["entry_span"][key]
#                            print self.title["entry_span"][key]
#                        try: self.original_tabular_data
#                        except: raise Exception("The fast_list was supposed to have the self.orginal_tabular_data variable, but didn't")
#                        else: 
                    if self.sorted_by_this_column == sort_by_this_column:
                        self.reverse_sorting = not self.reverse_sorting
                    else:
                        self.reverse_sorting = self.reverse_sorting
                    self.receive_data(self.original_tabular_data, sort_by = sort_by_this_column , column_order = self.original_column_order, reverse_sort = self.reverse_sorting)
                    self.update_fast_list()                    
                    pygame.display.flip()
                    return


            
            index_selected = (event.pos[1] - 20 - self.rect[1] - self.top_frame_width) / self.text_height + self.interval[0]
            
#            print "clicked at relative y_pos: " + str(event.pos[1] - self.rect[1] - self.top_frame_width) + " which is index: " + str(index_selected)
            if 0 <= index_selected and index_selected < len(self.data):
                self.selected = self.data[index_selected]
                self.selected_name = self.selected.split("  ")[0]
                self.selected_name = self.selected_name.rstrip(" ")
                self.update_fast_list()
                pygame.display.flip()
        
        
#    def notify(self,event):
#        try: self.list_frame
#        except: pass
#        else:
#            try: self.vscrollbar
#            except: right_border = self.topleft[0] + self.list_size[0]
#            else: right_border = self.topleft[0] + self.list_size[0] - self.vscrollbar.width
#            
#            if self.topleft[0] < event.data.pos[0] and event.data.pos[0] < right_border:
#                if self.topleft[1] < event.data.pos[1] and event.data.pos[1] < self.topleft[1] + self.list_size[1]:    
#                    index_selected = (event.data.pos[1] - self.topleft[1] - self.top_frame_width) / self.text_height + self.interval[0]
#                    #print "clicked at relative y_pos: " + str(event.data.pos[1] - self.topleft[1] - self.top_frame_width) + " which is index: " + str(index_selected)
#                    if 0 <= index_selected and index_selected < len(self.data):
#                        self.selected = self.data[index_selected]
#                        self.selected_name = self.selected.split("  ")[0]
#                        self.selected_name = self.selected_name.rstrip(" ")
#                        self.update_fast_list()
#                        #print self.selected
#            
#                #checking to see if the click is on the titlebar
#                try: self.list_frame
#                except: pass
#                else:
#                    top_border = int(self.topleft[1] - 2 * self.text_height)
#                    bottom_border = int(self.topleft[1] - self.text_height + self.top_frame_width * 2) 
#                    if top_border < event.data.pos[1] and event.data.pos[1] < bottom_border:
#                        horizontal_position = event.data.pos[0] - self.topleft[0]
#                        for key in self.title["entry_span"].keys():
#                            if key[0] < horizontal_position and horizontal_position < key[1]:
#                                sort_by_this_column = self.title["entry_span"][key]
#                        try: self.original_tabular_data
#                        except: raise Exception("The fast_list was supposed to have the self.orginal_tabular_data variable, but didn't")
#                        else: 
#                            print "self.sorted_by_this_column: " + str(self.sorted_by_this_column)
#                            print "sort_by_this_column: " + str(sort_by_this_column)
#                            if self.sorted_by_this_column == sort_by_this_column:
#                                self.reverse_sorting = not self.reverse_sorting
#                            else:
#                                self.reverse_sorting = self.reverse_sorting
#                                
#                            
#                            self.receive_data(self.original_tabular_data, sort_by = sort_by_this_column , column_order = self.original_column_order, reverse_sort = self.reverse_sorting)
#                              
#                            self.update_fast_list()                    
                    
                        
                    
                    
                    
                    
    
    def update_fast_list(self):
        """
        Function to update the fast list. Changes the look of the surface "self.list_surface", sets it as picture in the
        self.list_surface_label and calls renderer.update. Adds scrollbar if necessary. 
        """
        if(len(set(self.data)) != len(self.data)):
            raise Exception("The fast_list contains non-unique values!")
        pygame.draw.rect(self.surface, (234,228,223), self.rect_for_main_list)
        
        
        
        #in the case where data can fit on screen
        if self.lines_visible >= len(self.data):
            self.interval = range(0,len(self.data))
            for i in range(0,len(self.data)):
                if self.data[i] == self.selected:
                    rendered_dataline = global_variables.courier_font.render(self.data[i],True,(255,0,0))
                else:
                    rendered_dataline = global_variables.courier_font.render(self.data[i],True,(0,0,0))
                
                self.surface.blit(rendered_dataline,(self.rect_for_main_list[0] + self.left_list_frame, self.rect_for_main_list[1] + i*self.text_height + self.top_frame_width))
                pygame.display.flip()
        
        #in the case where data can't fit on screen
        else:
            
            percentage_position = float(self.vscrollbar.position) / float(self.vscrollbar.range_of_values[1] - self.vscrollbar.range_of_values[0])
            per_entry_position = int(percentage_position * (len(self.data)-self.lines_visible))
            self.interval = range(int(per_entry_position),int(per_entry_position) + self.lines_visible)
            for j, i in enumerate(self.interval):
                if self.data[i] == self.selected:
                    rendered_dataline = global_variables.courier_font.render(self.data[i],True,(255,0,0))
                else:
                    rendered_dataline = global_variables.courier_font.render(self.data[i],True,(0,0,0))
                self.surface.blit(rendered_dataline,(self.rect_for_main_list[0] + self.left_list_frame, self.rect_for_main_list[1] + j*self.text_height + self.top_frame_width))

        
        
                
        
    





#
#    def render_title(self):
#        """
#        Function that will check if the fast_list has a self.title entry, and in that case
#        render it in a separate frame just above the main list
#        """
#        title_surface = pygame.Surface((self.rect[2],self.text_height))
#        title_surface.fill((234,228,223))
#        rendered_titleline = global_variables.courier_font.render(self.title["text"],True,(0,0,0))
#        title_surface.blit(rendered_titleline,(self.left_list_frame, 0))
#        
#        self.surface.blit(title_surface,(self.rect[0],self.rect[1]-self.text_height))
#        
#        pygame.display.flip()
#
#        #expanding rectangle to catch clicks on title
#        self.rect = pygame.Rect(self.rect[0],self.rect[1] - self.text_height, self.rect[2], self.rect[3] + self.text_height)





    def receive_data(self,data,sort_by="rownames",column_order=None,reverse_sort=False):
        """
        Function that takes tabular data either of the form imported by primitives.import_datasheet (a dictionary with rows as keys and values 
        being another dictionary were colums are keys and values are data entries) or else as a simple list.
        This is then saved in self.data as a regular list, with the data in flattened and sorted form.
        The first line of the data is the title
        Optional arguments:
            sort_by    A string .If given the table will be sorted by this column name. Defaults to sorting by row-title name
            column_order     a list. If given the columns will appear in this order. Use 'rownames' to refer to the rownames. Omitted entries will not be in the list.
        """
        
        if isinstance(data,list):
            self.data = data
        elif isinstance(data,dict):
            if data == {}:
                self.data = []
                self.title = {}
                self.title["text"] = ""
                self.title["entry_span"] = {}
            else:
                #checking that the column_order is correct
                collection = []
                self.original_tabular_data = data
                self.sorted_by_this_column = sort_by
                self.original_column_order = column_order
                try: data[data.keys()[0]].keys()
                except:
                    print data
                    raise Exception("The data given to fast_list did not follow standards. It has been printed above")
                original_columns = ["rownames"] + data[data.keys()[0]].keys()
                if column_order is None:
                    column_order = original_columns 
                else:
                    for column_name in column_order:
                        if column_name not in original_columns:
                            raise Exception("Received a column_order entry " + str(column_name) + " that was not located in the data columns: " + str(original_columns))
                
                
                #determining the max number of letters in each column
                max_letters_per_column = {"rownames":0}
                for column_name in column_order:
                    max_letters_per_column[column_name] = 0
                for row in data:
                    for column_name in column_order:
                        if column_name == "rownames":
                            entry = str(row)
                        else:
                            entry = data[row][column_name]
                        if isinstance(entry,int) or isinstance(entry,long) or isinstance(entry,float):
                            entry_length = 13 
                        else:
                            entry_length = len(str(entry))
                        max_letters_per_column[column_name] = max(max_letters_per_column[column_name],entry_length)
                for column_name in column_order:
                    max_letters_per_column[column_name] = max(max_letters_per_column[column_name],len(column_name))
                for max_letters_per_column_entry in max_letters_per_column:
                    max_letters_per_column[max_letters_per_column_entry] = max_letters_per_column[max_letters_per_column_entry] + 2
                
                
                #sorting the rows according to sort_by
                if sort_by not in column_order:
                    print column_order
                    raise Exception("The sort_by variable was not found in the column_order. Remember the rownames must also be present if needed") 
                if sort_by == "rownames":
                    sorting_list = data.keys()
                    sorting_list.sort()
                else:
                    temp_dict = {}
                    
                    #from http://mail.python.org/pipermail/python-list/2002-May/146190.html - thanks xtian
                    for row in data:
                        temp_dict[row] = data[row][sort_by]
                    def sorter(x, y):
                        return cmp(x[1],y[1])
            
                    i = temp_dict.items()
                    i.sort(sorter)
                    sorting_list = []
                    for i_entry in i:
                        sorting_list.append(i_entry[0])
                
                
                if reverse_sort:
                    sorting_list.reverse()
        
        
                
                
                for rowname in sorting_list:
                    rowstring = ""
                    for column_entry in column_order:
                        if column_entry == "rownames":
                            data_point_here = rowname
                        else:
                            data_point_here = data[rowname][column_entry]
                        
                        if isinstance(data_point_here,int) or isinstance(data_point_here,long) or isinstance(data_point_here,float):
                            if isinstance(data_point_here,float):
                                if abs(data_point_here) > 1000:
                                    data_point_here = int(data_point_here)
                                else:
                                    data_point_here = "%.4g" % data_point_here
                            
                            if isinstance(data_point_here,int) or isinstance(data_point_here,long):
                                if abs(data_point_here) > 1000*1000*1000*1000*1000*3:
                                    data_point_here = "%.4g" % data_point_here
                                elif abs(data_point_here) > 1000*1000*1000*1000*3:
                                    data_point_here = str(int(data_point_here / (1000*1000*1000*1000) )) + " trillion"
                                elif abs(data_point_here) > 1000*1000*1000*3:
                                    data_point_here = str(int(data_point_here / (1000*1000*1000) )) + " billion"
                                elif abs(data_point_here) > 1000*1000*3:
                                    data_point_here = str(int(data_point_here / (1000*1000) )) + " million"
                                elif abs(data_point_here) > 1000*3:
                                    data_point_here = str(int(data_point_here / 1000)) + " thousand"
                                else:
                                    data_point_here = str(data_point_here)
                                
                            #data_point_here = "%.3g" % data_point_here
                        else:
                            data_point_here = str(data_point_here)
                            
                            
                        seperator = "                                                                "        
            
                        seperator = seperator[0:(max_letters_per_column[column_entry] - len(data_point_here))]
                            
                        rowstring = rowstring + data_point_here + seperator
                    collection.append(rowstring)
                
                
                #creating title 
                #a dictionary with key "text", containing a string with the text to write, and key "entry_span" containing another 
                #dictionary with the column names as values and their length in pixels as keys
                self.title = {}
                self.title["text"] = ""
                self.title["entry_span"] = {}
                entry_end = 5 #FIXME?
                for column_entry in column_order:
                    if column_entry == "rownames":
                        column_title = ""
                    else:
                        column_title = column_entry
                        
                    seperator = "                                                                "        
                    seperator = seperator[0:(max_letters_per_column[column_entry] - len(column_title))]
                    
                    
                    entry_start = entry_end 
                    entry_end = global_variables.courier_font.size(column_title + seperator)[0] + entry_start
                    self.title["entry_span"][(entry_start,entry_end)] = column_entry
                    
        #            
                    self.title["text"] = self.title["text"] + column_title + seperator
                
                self.data = collection
    
            
        else:
            print data
            raise Exception("The data passed to the fast_list was not recognised")
    
    
    
    
    
    
    










