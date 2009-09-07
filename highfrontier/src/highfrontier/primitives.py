import pygame
import global_variables
import datetime
#from ocempgui.widgets import *
#from ocempgui.widgets.Constants import *



def sort_dict(dict):
    items = dict.items()
    items.sort()
    return [value for key, value in items]


def invert_dict(d):
    inv = {}
    for k,v in d.iteritems():
        keys = inv.setdefault(v, [])
        keys.append(k)
    return inv


def make_linear_x_axis(surface,frame_size,xlim,solar_system_object_link,unit=""):
    """
    Function that paints a linear x axis on a surface and returns it. Needs the surface, the frame size (how much space should be left in
    corners). The xlim - ie the range of x-values. Optional values 
        unit - a string specifying the unit type. If 'date' the vector given as int's representing time since start_date 
    """
    size = surface.get_size()
    tick_mark_width = size[1] / 100
    pygame.draw.line(surface,(0,0,0),(0,size[1]-frame_size),(size[0],size[1]-frame_size))

    if unit == "date":
        tick_marks = 3
    else:
        tick_marks = 5
    
    step_between_ticks = (size[0] - 2 * frame_size) / (tick_marks-1)
    
    for i in range(0,tick_marks):
        tick_mark_placement = size[0] - (i * step_between_ticks + frame_size)
        
        if unit == "date":
            tick_mark_value_raw = xlim[1] - ((xlim[1]-xlim[0]) * (i/float(tick_marks-1)))
            tick_mark_value = datetime.timedelta(tick_mark_value_raw) + solar_system_object_link.start_date
            tick_mark_rendered_value = global_variables.standard_font.render(str(tick_mark_value),True,(0,0,0))
            tick_mark_rendered_value_size = global_variables.standard_font.size(str(tick_mark_value)) 
        else: 
            tick_mark_value = xlim[1] - ((xlim[1]-xlim[0]) * (i/float(tick_marks-1)))
            tick_mark_rendered_value = global_variables.standard_font.render("%.3g" %tick_mark_value,True,(0,0,0))
            tick_mark_rendered_value_size = global_variables.standard_font.size("%.3g" %tick_mark_value)
            
        pygame.draw.line(surface,(0,0,0),(tick_mark_placement,size[1]-frame_size-tick_mark_width),(tick_mark_placement,size[1]-frame_size+tick_mark_width))
        x_correction = 0
        y_correction = 0
        surface.blit(tick_mark_rendered_value,(tick_mark_placement - tick_mark_rendered_value_size[0]/2, size[1]-frame_size + tick_mark_rendered_value_size[1]))
                
    if unit not in ["","date"]:
        unit_rendered_value = global_variables.standard_font.render(unit,True,(0,0,0))
        unit_rendered_value_size = global_variables.standard_font.size(unit)
        surface.blit(unit_rendered_value,(size[0]-frame_size, size[1]-frame_size))
    return surface
    
    
    
    
    
def make_linear_y_axis(surface,frame_size,ylim,solar_system_object_link, unit=""):
    """
    Function that paints a linear y axis on a surface and returns it. Needs the surface, the frame size (how much space should be left in
    corners). The ylim - ie the range of y-values. Optional values 
        unit - a string specifying the unit type. If 'date' the vector given as int's representing time since start_date 
    """
    size = surface.get_size()
    tick_mark_width = size[0] / 100
    pygame.draw.line(surface,(0,0,0),(frame_size,0),(frame_size,size[1]))

    if unit == "date":
        tick_marks = 3
    else:
        tick_marks = 5
    
    step_between_ticks = (size[1] - 2 * frame_size) / (tick_marks-1)
    
    for i in range(0,tick_marks):
        tick_mark_placement = i * step_between_ticks + frame_size
        
        if unit == "date":
            tick_mark_value_raw = ylim[1] - ((ylim[1]-ylim[0]) * (i/float(tick_marks-1)))
            tick_mark_value = datetime.timedelta(tick_mark_value_raw) + solar_system_object_link.start_date
            tick_mark_rendered_value = global_variables.standard_font.render(str(tick_mark_value),True,(0,0,0))
            tick_mark_rendered_value_size = global_variables.standard_font.size(str(tick_mark_value)) 
        else: 
            tick_mark_value = ylim[1] - ((ylim[1]-ylim[0]) * (i/float(tick_marks-1)))
            tick_mark_rendered_value = global_variables.standard_font.render("%.3g" %tick_mark_value,True,(0,0,0))
            tick_mark_rendered_value_size = global_variables.standard_font.size("%.3g" %tick_mark_value)
            
        pygame.draw.line(surface,(0,0,0),(frame_size-tick_mark_width,tick_mark_placement),(frame_size+tick_mark_width,tick_mark_placement))
        
        
        if frame_size-tick_mark_width*2-tick_mark_rendered_value_size[0] < 0: #to make sure that the unit doesn't wrap off screen
            x_correction = -(frame_size-tick_mark_width*2-tick_mark_rendered_value_size[0])
            y_correction = (size[1] / 100)
        else:
            x_correction = 0
            y_correction = 0
        surface.blit(tick_mark_rendered_value,(frame_size-tick_mark_width*2-tick_mark_rendered_value_size[0]+x_correction,tick_mark_placement-tick_mark_rendered_value_size[1]/2 - y_correction))
                
    if unit not in ["","date"]:
        unit_rendered_value = global_variables.standard_font.render(unit,True,(0,0,0))
        unit_rendered_value_size = global_variables.standard_font.size(unit)
        surface.blit(unit_rendered_value,(frame_size - unit_rendered_value_size[0], frame_size - unit_rendered_value_size[1]-(size[1] / 50)))
            
    
    return surface



def import_datasheet(data_file_name):
        data_file = open(data_file_name)
        database = {}
        headers = data_file.readline()
        headers = headers.split("\t")
        headers[-1] = headers[-1].rstrip("\n")
        headers[-1] = headers[-1].rstrip("\r")
        
        data_types = data_file.readline()
        data_types = data_types.split("\t")
        if data_types[0] == "explanation":
            data_types = data_file.readline()
            data_types = data_types.split("\t")
            #print data_types
        data_types[-1] = data_types[-1].rstrip("\n")
        data_types[-1] = data_types[-1].rstrip("\r")
        
        
        for line in data_file.readlines():
            splitline = line.split("\t")
            splitline[-1] = splitline[-1].rstrip("\n")
            splitline[-1] = splitline[-1].rstrip("\r")
            single_entry_data = {}
            for i in range(1,len(splitline)):
                if data_types[i] == "int":
                    if splitline[i] == "NA":
                        single_entry_data[headers[i]] = None
                    else:
                        single_entry_data[headers[i]] = int(splitline[i])
                elif data_types[i] == "float":
                    if splitline[i] == "NA":
                        single_entry_data[headers[i]] = None
                    else:
                        single_entry_data[headers[i]] = float(splitline[i])
                elif data_types[i] == "string":
                    if splitline[i] == "NA":
                        single_entry_data[headers[i]] = None
                    else:
                        single_entry_data[headers[i]] = str(splitline[i])
                elif data_types[i] == "logical":
                    if splitline[i] == "NA":
                        single_entry_data[headers[i]] = None
                    elif splitline[i] == "True":
                        single_entry_data[headers[i]] = True
                    elif splitline[i] == "False":
                        single_entry_data[headers[i]] = False
                    else:
                        print "Problem with: "  + str(headers[i])

                elif data_types[i] == "tuple":
                        if splitline[i] == "NA":
                            single_entry_data[headers[i]] = None
                        else:
                            raw_read = str(splitline[i])
                            split_read = raw_read.split(" ")
                            for j in range(0,len(split_read)):
                                split_read[j] = int(split_read[j])
                            tuple_read = tuple(split_read)
                            single_entry_data[headers[i]] = tuple_read
                else:
                    print "Problem with: "  + str(headers[i])
                
                database[splitline[0]] = single_entry_data 
        data_file.close()
        #if verbose:
            #print database
        
        return database




def flatten(lst):
    list = []
    for elem in lst:
        for i in elem:
            list.append(i)
    return list









def listify_tabular_data(data,size,manager,sort_by="rownames",column_order=None,interval = (0,200),reverse_sort=False):
    """
    Function that takes tabular data of the form imported by primitives.import_datasheet (a dictionary with rows as keys and values being another dictionary were colums are keys and values are data entries)
    returns a surface with a scrolled list with the data, which can be rendered directly on screen.
    Optional arguments:
        sort_by    A string .If given the table will be sorted by this column name. Defaults to sorting by row-title name
        column_order     a list. If given the columns will appear in this order. Use 'rownames' to refer to the rownames. Omitted entries will not be in the list.
    """
    
    print "1"
    
    #checking that the column_order is correct
    collection = ListItemCollection()
    original_columns = ["rownames"] + data[data.keys()[0]].keys()
    if column_order is None:
        column_order = original_columns 
    else:
        for column_name in column_order:
            if column_name not in original_columns:
                raise Exception("Recieved a column_order entry that was not located in data columns")
    
    print "2"
    #determining the max number of letters in each column
    max_letters_per_column = {"rownames":0}
    for column_name in column_order:
        max_letters_per_column[column_name] = 0
    for row in data:
        for column_name in column_order:
            if column_name == "rownames":
                entry = str(row)
            else:
                entry = str(data[row][column_name])
            max_letters_per_column[column_name] = max(max_letters_per_column[column_name],len(entry))
    for max_letters_per_column_entry in max_letters_per_column:
        max_letters_per_column[max_letters_per_column_entry] = max_letters_per_column[max_letters_per_column_entry] + 2
    print "3"
    

    #creating the sorting buttons - this is a time lag thing. 
    sorting_button_frame = HFrame()
    sorting_buttons = {}
    seperator = "                                                                "
    for column_name in column_order:
        sorting_buttons[column_name] = Button(column_name)
        textSize = global_variables.courier_font.size(seperator[0:max_letters_per_column[column_name]])
        sorting_buttons[column_name].set_minimum_size(textSize[0],textSize[1])
        sorting_button_frame.add_child(sorting_buttons[column_name])
        if textSize[0] != sorting_buttons[column_name].size[0]:
            max_letters_per_column[column_name] = sorting_buttons[column_name].size[0] / 10
            
         
        

        
    print "4"
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
    print "5"
    create_cutoff_buttons = False
    if interval[0] < 0:
        raise Exception("Can't give an interval below zero")
    elif interval[0] == 0:
        pass
    else:
        create_cutoff_buttons = True
        print "set create_cutoff_buttons true because interval[0] was above 0"
    
    if len(sorting_list) < interval[1]:
        interval = (interval[0],len(sorting_list))
    elif len(sorting_list) == interval[1]:
        pass
    else:
        create_cutoff_buttons = True
        print "set create_cutoff_buttons true because interval[1] was less than len(sorting_list)"
    print "6"   
    #cutoff_buttons:
    if create_cutoff_buttons:
        up_button = Button("Previous page")
        down_button = Button("Next page")
        if interval[0] == 0:
            up_button.sensitive = False
        if interval[1] == len(sorting_list):
            down_button.sensitive = False
        cutoff_frame = HFrame()
        cutoff_frame.add_child(up_button,down_button)
        
        
    sorting_list = sorting_list[interval[0]:interval[1]]
        
    
    
    print "7"
    for rowname in sorting_list:
        rowstring = ""
        for column_entry in column_order:
            if column_entry == "rownames":
                data_point_here = rowname
            else:
                data_point_here = str(data[rowname][column_entry])
                #print len(data_point_here)
            
            seperator = "                                                                "        

            seperator = seperator[0:(max_letters_per_column[column_entry] - len(data_point_here))]
                
            rowstring = rowstring + data_point_here + seperator
        #rowlistitem = TextListItem(rowstring)
        #rowlistitem.get_style()['font']['name'] = "Courier"
        collection.append(rowstring)
    print "8"
    list = fast_list()
    print "8.1"
    #list.set_selectionmode()
    print "8.2"
    #print collection
    #list.items = collection 
    
    print "9"
    
    
    
        
    
    
    
    super_frame = VFrame()
    super_frame.align = ALIGN_LEFT
    
    
    super_frame.add_child(sorting_button_frame,list)
    if create_cutoff_buttons:
        super_frame.add_child(cutoff_frame)
    print "10"
    return super_frame
#    
































#
#def present_tabular_data(data,size,sort_by="rownames",column_order=None):
#    """
#    Wrapper around listify_tabular_data 
#    Like that, it takes tabular data of the form imported by primitives.import_datasheet (a dictionary with rows as keys and values being another dictionary were colums are keys and values are data entries)
#    but this will return a frame with the output of listify_tabular_data, and buttons for each column_order entry that can be used to sort the list.
#    Optional arguments:
#        sort_by    A string .If given the table will be sorted by this column name. Defaults to sorting by row-title name
#        column_order     a list. If given the columns will appear in this order. Use 'rownames' to refer to the rownames. Omitted entries will not be in the list.
#    """
#    
#    HFrame()
#    
#    HFrame.addwidget()
#    
#    
     
    
