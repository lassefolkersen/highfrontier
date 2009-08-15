import math
from ocempgui.widgets.Constants import *
from ocempgui.object import BaseObject
from ocempgui.widgets import *
import global_variables
import pygame
import primitives




class fast_list(BaseObject):
    """
    A list similar to the ScrolledList, but faster
    """
    def __init__(self,renderer):
        BaseObject.__init__(self)
        self._signals[SIG_CLICKED] = []
        self.renderer = renderer
        self.renderer.get_managers()[0].add_object(self, 5)
        self.list_size = (400,400)
        self.topleft = (50, 50)
        self.data = []
        self.text_height = global_variables.courier_font.size("abcdefghijklmnopqrstuvxysABCDEFGHIJKLMNOPQRSTU")[1]
        self.left_list_frame = 5 # how much the text in the list is indented
        self.top_frame_width = 5 # this is a guestimate of how much the Frame is filling
        self.selected = None
        self.selected_name = None
        self.title = None #either None (in which case it can't be rendered" or else a dictionary with key "text", containing a string with the text to write, and key "entry_span" containing another dictionary with the column names as values and their length in pixels as keys
        self.reverse_sorting = False
        
    def create_fast_list(self):
        """
        The creation function. Doesn't return anything, but saves self.list_frame variable and renders using the self.renderer.
        Needs to have something saved to self.data first 
        """
        blank_surface = pygame.Surface(self.list_size)
        blank_surface.fill((234,228,223))
        self.list_surface_label = ImageLabel(blank_surface)
        self.update_fast_list()
        self.list_frame = HFrame()
        self.list_frame.topleft = self.topleft
        self.list_frame.add_child(self.list_surface_label)
        try: self.vscrollbar
        except: pass
        else:
            self.list_frame.add_child(self.vscrollbar)
        self.renderer.add_widget(self.list_frame)
        
    def scrolling(self):
        self.update_fast_list()
    

    def exit(self):
        try:  self.list_frame
        except: pass
        else:
            self.list_frame.destroy()
            del self.list_frame
            del self.list_surface_label 
        try: self.vscrollbar
        except: pass
        else:
            del self.vscrollbar
        
        
        try: self.title
        except: pass
        else: del self.title
        
        try: self.title_frame
        except: pass
        else:
            self.title_frame.destroy()
            del self.title_frame
        
    def notify(self,event):
        try: self.list_frame
        except: pass
        else:
            try: self.vscrollbar
            except: right_border = self.topleft[0] + self.list_size[0]
            else: right_border = self.topleft[0] + self.list_size[0] - self.vscrollbar.width
            
            if self.topleft[0] < event.data.pos[0] and event.data.pos[0] < right_border:
                if self.topleft[1] < event.data.pos[1] and event.data.pos[1] < self.topleft[1] + self.list_size[1]:    
                    index_selected = (event.data.pos[1] - self.topleft[1] - self.top_frame_width) / self.text_height + self.interval[0]
                    #print "clicked at relative y_pos: " + str(event.data.pos[1] - self.topleft[1] - self.top_frame_width) + " which is index: " + str(index_selected)
                    if 0 <= index_selected and index_selected < len(self.data):
                        self.selected = self.data[index_selected]
                        self.selected_name = self.selected.split("  ")[0]
                        self.selected_name = self.selected_name.rstrip(" ")
                        self.update_fast_list()
                        #print self.selected
            
                #checking to see if the click is on the titlebar
                try: self.list_frame
                except: pass
                else:
                    top_border = int(self.topleft[1] - 2 * self.text_height)
                    bottom_border = int(self.topleft[1] - self.text_height + self.top_frame_width * 2) 
                    if top_border < event.data.pos[1] and event.data.pos[1] < bottom_border:
                        horizontal_position = event.data.pos[0] - self.topleft[0]
                        for key in self.title["entry_span"].keys():
                            if key[0] < horizontal_position and horizontal_position < key[1]:
                                sort_by_this_column = self.title["entry_span"][key]
                        try: self.original_tabular_data
                        except: raise Exception("The fast_list was supposed to have the self.orginal_tabular_data variable, but didn't")
                        else: 
                            print "self.sorted_by_this_column: " + str(self.sorted_by_this_column)
                            print "sort_by_this_column: " + str(sort_by_this_column)
                            if self.sorted_by_this_column == sort_by_this_column:
                                self.reverse_sorting = not self.reverse_sorting
                            else:
                                self.reverse_sorting = self.reverse_sorting
                                
                            
                            self.receive_data(self.original_tabular_data, sort_by = sort_by_this_column , column_order = self.original_column_order, reverse_sort = self.reverse_sorting)
                              
                            self.update_fast_list()                    
                    
                        
                    
                    
                    
                    
    
    def update_fast_list(self):
        """
        Function to update the fast list. Changes the look of the surface "self.list_surface", sets it as picture in the
        self.list_surface_label and calls renderer.update. Adds scrollbar if necessary. 
        """
        if(len(set(self.data)) != len(self.data)):
            raise Exception("The fast_list contains non-unique values!")
        surface = pygame.Surface(self.list_size)
        surface.fill((234,228,223))
        self.lines_visible = int( math.floor( self.list_size[1] / self.text_height) )
        #print "self.lines_visible " + str(self.lines_visible )

        #in the case where data can fit on screen
        if self.lines_visible >= len(self.data):
            try: self.vscrollbar
            except: pass
            else:
                self.vscrollbar.destroy()
                del self.vscrollbar

            self.interval = range(0,len(self.data))
            for i in range(0,len(self.data)):
                if self.data[i] == self.selected:
                    rendered_dataline = global_variables.courier_font.render(self.data[i],True,(255,0,0))
                else:
                    rendered_dataline = global_variables.courier_font.render(self.data[i],True,(0,0,0))
                surface.blit(rendered_dataline,(self.left_list_frame, i*self.text_height))
            
        
        #in the case where data can't fit on screen
        else:
            try: self.vscrollbar
            except:
                self.vscrollbar = VScrollBar(self.list_size[1],self.text_height * (len(self.data)+1))
                self.vscrollbar.set_step(self.text_height)
                self.vscrollbar.connect_signal(SIG_VALCHANGED, self.scrolling)
            else:
                if self.vscrollbar.maximum != self.text_height * (len(self.data)+1):
                    self.vscrollbar.set_maximum(self.text_height * (len(self.data)+1))
                    
            self.interval = range(int(self.vscrollbar.value / self.text_height),int((self.vscrollbar.value / self.text_height) + self.lines_visible))
            #print "raw interval " + str((self.vscrollbar.value / self.text_height,(self.vscrollbar.value / self.text_height) + self.lines_visible))
            for j, i in enumerate(self.interval):
                if self.data[i] == self.selected:
                    rendered_dataline = global_variables.courier_font.render(self.data[i],True,(255,0,0))
                else:
                    rendered_dataline = global_variables.courier_font.render(self.data[i],True,(0,0,0))
                surface.blit(rendered_dataline,(self.left_list_frame, j*self.text_height))

        
        self.list_surface_label.set_picture(surface)
        self.renderer.update()        
        
    






    def render_title(self):
        """
        Function that will check if the fast_list has a self.title entry, and in that case
        render it in a separate frame just above the main list
        """
        
        try: self.title
        except: print "DEBUGGING: a fast_list had had a title_Frame request trough the render_title function, but no title exists"
        else:
            self.title_frame = VFrame()
            title_surface = pygame.Surface((self.list_size[0],self.text_height))
            title_surface.fill((234,228,223))
            rendered_titleline = global_variables.courier_font.render(self.title["text"],True,(0,0,0))
            title_surface.blit(rendered_titleline,(self.left_list_frame, 0))
            title_surface_label = ImageLabel(title_surface)
            self.title_frame = VFrame()
            self.title_frame.topleft = (self.topleft[0], self.topleft[1] - 2 * self.text_height)
            self.title_frame.add_child(title_surface_label)
            self.renderer.add_widget(self.title_frame)






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
                            raise Exception("Received a column_order entry that was not located in data columns")
                
                
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
        
        
                #print "data is shown here: " + str(data)
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
                entry_end = self.left_list_frame
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
                    
                    
        #            print column_title
        #            print seperator
        #            
                    self.title["text"] = self.title["text"] + column_title + seperator
                
                self.data = collection
    
            
        else:
            print data
            raise Exception("The data passed to the fast_list was not recognised")
    
    
    
    
    
    
    









#import random
#from ocempgui.widgets import *
#from ocempgui.events import EventManager
#re = Renderer()
##input = ["one test line","another test line","yet another test line","even one more test line","an extremely long line that is way too long and perhaps should give a warning"]
##input_long = []
##for i in range(0,23):
##    realwords = input[random.randint(0,len(input)-1)]
##    input_long.append(realwords + " " + str(random.randint(1,10000)))  
#
#
#
#
#
#fast_list_instance = fast_list(re)
#fast_list_instance.title={}
##fast_list_instance.title["text"] = "Test1 test2 test3 test4"
##fast_list_instance.title["entry_span"] = {(5,30):"Test1",(30,70):"test2",(70,160):"test3",(160,250):"test4"}
##fast_list_instance.data = input_long
#
#
#import os
#data_file_name = os.path.join("data","economy","trade resources.txt")
#trade_resources = primitives.import_datasheet(data_file_name)
#fast_list_instance.listify_tabular_data(trade_resources)
#
##print trade_resources
#
#fast_list_instance.create_fast_list()
#fast_list_instance.render_title()
#
#
##print fast_list_instance.title
#re.create_screen (800, 600)
#re.title = "Window examples"
#re.color = (234, 228, 223)
#
#re.start ()
#

