

import numpy as np
import matplotlib.pyplot as plt
import json
import matplotlib.markers as markers
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator, MaxNLocator, FixedLocator)
from matplotlib import cm
import math
import matplotlib.colors as colors
import os
import matplotlib.dates as mdates
from math import modf
import sys
import datetime
import matplotlib
from collections import Counter

#matplotlib.use('pgf')


plt.rcParams["font.family"] = "monospace"
#plt.rc('text', usetex=True)
#plt.rc('font', family='serif')
#matplotlib.rcParams['pgf.preamble'] = [r'\usepackage{hyperref}', ]

#https://stackoverflow.com/questions/60952034/add-a-hyperlink-in-a-matplotlib-plot-inside-a-pdfpages-page-python
#https://matplotlib.org/stable/gallery/misc/hyperlinks_sgskip.html
# https://stackoverflow.com/questions/15417586/python-matlplotlib-add-hyperlink-to-text

def get_y_value_for_user_topic_nr(original_nr, order_mapping_flattened, order_mapping):
    if not order_mapping:
        return original_nr
    else: # User don't use 0
        original_nr = original_nr + 1
        return order_mapping_flattened.index(original_nr)
        
def flatten_extend(order_list):
    if not order_list: #None
        return order_list
    flat_list = []
    for item in order_list:
        if type(item) is list:
            flat_list.extend(item)
        else:
            flat_list.append(item)
    return flat_list
        
def update_color(current_color_number, index_for_color_number, order_mapping):
    if not order_mapping:
        return current_color_number + 1, index_for_color_number
    
    if not type(order_mapping[current_color_number]) is list:
        return current_color_number + 1, index_for_color_number
    
    if index_for_color_number + 1 >= len(order_mapping[current_color_number]):
         return current_color_number + 1, 0
    else:
        return current_color_number, index_for_color_number + 1

def get_weaker_form_of_named_color(color_name, transparancy):
     rgb = list(colors.to_rgb(color_name))
     rgb.append(transparancy)
     return rgb
     
###
# Start
#####

def make_plot(model_file, outputdir, metadata_file_name, file_name, add_for_coliding_dates=False, label_length=20, normalise_for_nr_of_texts=False, use_date_format=True, vertical_line_to_represent_nr_of_documents=False, log=False, hours_between_label_dates=24, width_vertical_line=0.0000001, extra_x_length=0.005, order_mapping=None, use_separate_max_confidence_for_each_topic=True, link_mapping_func=None, link_mapping_dict=None, bar_width=0.1, bar_transparency=0.2, circle_scale_factor=400):

    order_mapping_flattened = flatten_extend(order_mapping)
    counter = Counter(order_mapping_flattened)
    potentinal_dupblicates = ([dbl for dbl in counter if counter[dbl] > 1])
    if len(potentinal_dupblicates) > 0:
        print("There are dublicates in 'order_mapping', remove them. The following: ", potentinal_dupblicates)
        exit()
    
    if log:
        print("Not yet implemented")
        sys.exit(0)
        
    label_translations = False # TODO: Add as an option
    print("use_date_format", use_date_format)
    obj = None
    
    with open(model_file, 'r') as f:
        data = f.read()
        obj = json.loads(data)

    # Collect "meta_data_dict"
    # In "meta_data_dict": Each item contains a date and the list of documents (basename for document) associated
    # with this date. E.g.
    # 1964-01-01 ['Diabetes_1964_vol014_nr001_0023.txt', 'Diabetes_1964_vol014_nr001_0020.txt', 'Diabetes_1964_vol014_nr001_0025.txt', 'Diabetes_1964_vol014_nr001_0009.txt', 'Diabetes_1964_vol014_nr001_0006.txt', 'Diabetes_1964_vol014_nr001_0010.txt', 'Diabetes_1964_vol014_nr001_0024.txt', 'Diabetes_1964_vol014_nr001_0016.txt', 'Diabetes_1964_vol014_nr001_0013.txt', 'Diabetes_1964_vol014_nr001_0007.txt', 'Diabetes_1964_vol014_nr001_0018.txt', 'Diabetes_1964_vol014_nr001_0022.txt', 'Diabetes_1964_vol014_nr001_0015.txt', 'Diabetes_1964_vol014_nr001_0011.txt', 'Diabetes_1964_vol014_nr001_0004.txt', 'Diabetes_1964_vol014_nr001_0014.txt', 'Diabetes_1964_vol014_nr001_0012.txt', 'Diabetes_1964_vol014_nr001_0032.txt', 'Diabetes_1964_vol014_nr001_0008.txt', 'Diabetes_1964_vol014_nr001_0019.txt', 'Diabetes_1964_vol014_nr001_0035.txt']
    
    meta_data_dict = {}
    max_topic_confidence = 0
    
    nr_of_texts_for_max_topic_confidence = None
    if use_date_format:
        min_timestamp = np.datetime64('9999-01-02')
        max_timestamp = np.datetime64('0000-01-02')
    else:
        min_timestamp = math.inf
        max_timestamp = -math.inf

    max_decimal_part_for_year = {}
    with open(metadata_file_name) as metadata_file:
        for line in metadata_file:
            sp = line.strip().split("\t")
            str_date = sp[1]
            if label_translations:
                if str_date in label_translations:
                    str_date = label_translations[str_date]
            if use_date_format:
                timestamp = np.datetime64(str_date)
            else:
                timestamp = float(str_date)
            if timestamp not in meta_data_dict:
                meta_data_dict[timestamp] = []
            base_name = os.path.basename(sp[0])
            meta_data_dict[timestamp].append(base_name)
            if not use_date_format:
                year = int(timestamp)
                print("year", year)
                decimal_part = modf(timestamp)[0]
                if year in max_decimal_part_for_year:
                    if decimal_part > max_decimal_part_for_year[year]:
                        max_decimal_part_for_year[year] = decimal_part
                else:
                    max_decimal_part_for_year[year] = decimal_part

    print("Nr of dates found in metadata", len(meta_data_dict.keys()))
    
    # Loop through the documents, and collect topics for the documents. # Store in document_info, with "base_name" of the document as the key
    document_info = {}
    max_topic_confidence_for_topic = {}
    for el in obj["topic_model_output"]["documents"]:
        base_name = el["base_name"]
        filtered_labels = [l for l in el["additional_labels"] if l.replace(".", "").replace("-", "").replace(":", "").replace("T", "").isdigit()]
        if len(filtered_labels) == 0:
            print("No timestamp", el)
            exit()
            
        str_date = filtered_labels[0]
        if label_translations:
            if str_date in label_translations:
                str_date = label_translations[str_date]
            
        if use_date_format:
            timestamp = np.datetime64(str_date)
        else:
            timestamp = float(str_date)
      
        document_topics = []
        for t in el["document_topics"]:
            topic_info = {}
            topic_info["terms_found_in_text"] = t["terms_found_in_text"]
            topic_info["topic_index"] = t["topic_index"]
            topic_info["topic_confidence"] = t["topic_confidence"]
            #if len(topic_info["terms_found_in_text"]) > 1: # At least two terms included in text to include
            
            document_topics.append(topic_info)
            
            # Record information on max confidence for topic in max_topic_confidence_for_topic
            if topic_info["topic_index"] not in max_topic_confidence_for_topic:
                max_topic_confidence_for_topic[topic_info["topic_index"]] = topic_info["topic_confidence"]
            else:
                if topic_info["topic_confidence"] > max_topic_confidence_for_topic[topic_info["topic_index"]]:
                    max_topic_confidence_for_topic[topic_info["topic_index"]] = topic_info["topic_confidence"]
 
        document_info[base_name] = document_topics

    print("Nr of documents found", len(document_info.items()))
    # Create timestamp_topics_dict
    # Where the each element is a key with a timestamp, and
    # which in turn contains a dictionary of confidence for the
    # differen topics for this timestamp
    # 1990-12-28T03 {16: 0.06963693325855479, 44: 0.08608091116481784, 47: 0.28642090183730934, 57: 0.4293435359283798}
    timestamps = sorted(meta_data_dict.keys())
    timestamp_topics_dict = {}
    max_confidence_for_year_dict = {}
    timestamp_basename_dict = {} # To be able to connect timestamps to filename
    max_texts = 0
    
    latest_timestamp_used_so_far = np.datetime64('0000-01-02')

    total_nr_of_topics_found_in_documents = 0
    for i in range(0, len(timestamps)):
        timestamp = timestamps[i]
        base_names = sorted(meta_data_dict[timestamp]) #Collected unsorted, so need to sort here
        
        timestamp_topics_dict[timestamp] = {}
        
        if timestamp < min_timestamp:
            min_timestamp = timestamp
        if timestamp > max_timestamp:
            max_timestamp = timestamp
        
        if add_for_coliding_dates:
            if len(base_names) > max_texts:
                max_texts = len(base_names)
            for base_name in base_names:
                if base_name in document_info:
                    for document_topic in document_info[base_name]:
                        topic_index = document_topic["topic_index"]
                        if topic_index not in timestamp_topics_dict[timestamp]:
                            timestamp_topics_dict[timestamp][topic_index] = 0
                        timestamp_topics_dict[timestamp][topic_index] = timestamp_topics_dict[timestamp][topic_index] + document_topic["topic_confidence"]
                        
                        # Check if maximum summed topic confidence so far
                        if timestamp_topics_dict[timestamp][topic_index] > max_topic_confidence:
                            max_topic_confidence = timestamp_topics_dict[timestamp][topic_index]
                            nr_of_texts_for_max_topic_confidence = len(base_names)
        else:
            if hours_between_label_dates == 0:
                print("'hours_between_label_dates' needs to be larger than 0")
                exit()
            if use_date_format:
                if hours_between_label_dates >= 1:
                    # TODO: Why divide by len(base_names)?
                    #part = math.ceil(1/len(base_names)*hours_between_label_dates)
                    part = abs(hours_between_label_dates)
                    if part == 0:
                        print("Warning the spread seems to be 0.")
                        exit()
                    spread_distance = np.timedelta64(part, 'h')
                    print("Texts with the same timestamp will be spread out with ", spread_distance, "hours")
                else:
                    seconds = math.ceil(3600*hours_between_label_dates)
                    spread_distance = np.timedelta64(seconds, 's')
                    print("Texts with the same timestamp will be spread out with ", spread_distance, "seconds")
            else:
                spread_distance = 1/len(base_names) #TODO does not work
                exit("SPREAD OUT NOT YET IMPLEMENTED FOR NON_DATES")
            
            
            # Add one element in timestamp_topics_dict for each basename with topic
            for base_name in base_names:
                if use_date_format:
                    year = timestamp.astype(object).year
                else:
                    year = int(timestamp)
                
                    
                if base_name in document_info:
                    for document_topic in document_info[base_name]:
                            
                        total_nr_of_topics_found_in_documents = total_nr_of_topics_found_in_documents + 1
                        topic_index = document_topic["topic_index"]
                        topic_confidence = document_topic["topic_confidence"]
                        
                        timestamp_topics_dict[timestamp][topic_index] = topic_confidence
                        
                        # Gather max values
                        if topic_confidence > max_topic_confidence:
                            max_topic_confidence = topic_confidence
                        if (year, topic_index) in max_confidence_for_year_dict:
                            if max_confidence_for_year_dict[(year, topic_index)] < topic_confidence:
                                max_confidence_for_year_dict[(year, topic_index)] = topic_confidence
                        else:
                            max_confidence_for_year_dict[(year, topic_index)] = topic_confidence
                            
                #To be able to connect timestamps to filename, for links
                timestamp_basename_dict[timestamp] = base_name
                
                #Create a new timpestamp to spread out texts that would
                # otherwise get the same x-vaile over the day
                old_timestamp = timestamp
                timestamp = timestamp + spread_distance
                if timestamp <= latest_timestamp_used_so_far:
                    print("The timestamps are spread out so much so that they collide with coming texts. Decrease the 'hours_between_label_dates' value when calling the visualisation")
                    print("timestamp", timestamp)
                    print("latest_timestamp_used_so_far", latest_timestamp_used_so_far)
                    exit()
                latest_timestamp_used_so_far = timestamp
                
                if timestamp == old_timestamp:
                    print("Distance seems to be 0. New timestamp is same as old")
                    print("old_timestamp", old_timestamp)
                    print("timestamp", timestamp)
                    print("spread_distance", spread_distance)
                    exit()
                if timestamp in timestamp_topics_dict:
                    print(timestamp_topics_dict)
                    print("The new timestamp is already in the dictionary. Something seems to be wrong")
                    print("timestamp", timestamp)
                    exit()
                timestamp_topics_dict[timestamp] = {}
                
                # Check that it is not spread out so much that
                # documents from one year will be plotted for the next year
                timestamp_year = timestamp.astype(object).year
                timestamp_year_before_spreading_out = timestamps[i].astype(object).year
                
                #TODO. Consider to add this
                """
                if timestamp_year != timestamp_year_before_spreading_out:
                    print("Original year: ", timestamp_year, ". Year after spread out:", timestamp_year_before_spreading_out)
                    print("ERROR: The documents are spread out so much that documents from one year will be plotted for the next year in the graph. Lower the parameter 'hours_between_label_dates'")
                    exit(1)
                """
    print("total_nr_of_topics_found_in_documents", total_nr_of_topics_found_in_documents)
    
    
    # End filling "timestamp_basename_dict"
    nr_of_plots_to_make = 0
    for key, item in timestamp_topics_dict.items():
        nr_of_plots_to_make = nr_of_plots_to_make + len(item)
    print("Nr of timestamps", len(timestamp_topics_dict.keys()))
    #print(timestamp_topics_dict.keys())
    print("nr_of_plots_to_make", nr_of_plots_to_make)

    min_timestamp = min_timestamp - (max_timestamp - min_timestamp)*extra_x_length
    max_timestamp = max_timestamp + (max_timestamp - min_timestamp)*extra_x_length

    print("max_texts", max_texts)
    print("nr_of_texts_for_max_topic_confidence", nr_of_texts_for_max_topic_confidence)
     #70
     
    # Give the topics the labels to show to the user and the number for the topic to show to the user
    topic_names = []
    show_to_user_nr_topic_index_mapping = {}
    for nr, el in enumerate(obj["topic_model_output"]["topics"]):
        topic_index = el["id"]
        show_to_user_nr_topic_index_mapping[topic_index] = nr
        terms = [t['term'] for t in el['topic_terms']]
        repr_terms = []
        for t in terms:
            term_to_pick_as_rep = "123456789123456789123456789123456789123456789123456789"
            #for s in t.split("/"):
            #    if "_" in s:
            #        term_to_pick_as_rep = s
            #if term_to_pick_as_rep == "123456789123456789123456789123456789123456789123456789":
            for s in t.split("/"):
                if len(s.strip()) < len(term_to_pick_as_rep):
                    term_to_pick_as_rep = s.strip()
            repr_terms.append(term_to_pick_as_rep.strip())
            
        third_length = int(len(repr_terms)/3)
        topic_name = ", ".join(repr_terms)[0:label_length].strip() +"..."
        nr_str = str(nr + 1)
        if len(nr_str) == 1:
            nr_str = " " + nr_str
        topic_names.append(nr_str + ": " + topic_name)



    topic_sorted_for_id = sorted(obj["topic_model_output"]["topics"], key=lambda t: t["id"])
    timestamps_sorted = sorted(timestamp_topics_dict.keys())

    print("max_topic_confidence", max_topic_confidence)

    #plt.figure(figsize = (8.268, 11.693))
    fig, ax1 = plt.subplots(figsize = (11.693, 8.268))

    ax1.set(xlim=(min_timestamp-20, max_timestamp+20))
    #plt.yticks([-y for y in range(0, len(topic_names), 1)], topic_names)
    
    if use_date_format:
        plt.gca().xaxis.set_major_locator(mdates.YearLocator())
        plt.gca().xaxis.set_minor_locator(mdates.MonthLocator())
    else:
        years = [int (a) for a in timestamps_sorted]
        plt.gca().xaxis.set_major_locator(FixedLocator(years))
   
 
    

    
    # Create a color mapping
    """
    # Perhaps use later. Currently, only use two colors
    main_colors = plt.colormaps['cool'].resampled(len(topic_names))
    
    if order_mapping:
        main_colors = plt.colormaps['cool'].resampled(len(order_mapping))
    
    colors_as_list = list(set([main_colors(a) for a in np.linspace(0,1,len(topic_names))]))
    
    
    main_colors_contrast = [] # Make neighbouring colors as much contrast as possible by
    # combining to maps
    for c1, c2 in zip(colors_as_list, colors_as_list[::-1]):
        main_colors_contrast.append(c1)
        main_colors_contrast.append(c2)
    """
    
    
    previous_color_number = 0
    current_color_number = 0
    index_for_color_number = 0
    current_simplifyed_color = get_weaker_form_of_named_color("lavender", 0.4)
    current_stronger_color =  "mediumpurple"
    color_mapping = {} # Mapping from user-shown topic nr:s to colors
    color_mapping_stronger = {}
    ys_when_color_is_updated = [] # To be able to draw a line between the colors-shifts
    
    
    for el in range(0, len(topic_names)):
        if order_mapping:
            if type(order_mapping[current_color_number]) is list:
                user_topic_nr = order_mapping[current_color_number][index_for_color_number]
            else:
                user_topic_nr = order_mapping[current_color_number]
            
            """ # Perhaps use colormap later
            current_color = list(main_colors_contrast[current_color_number])
            current_color[3] = 0.7
            color_mapping[user_topic_nr] = current_color
            """
            
            current_color_number, index_for_color_number = update_color(current_color_number, index_for_color_number, order_mapping)
         
            color_mapping[user_topic_nr] = current_simplifyed_color
            color_mapping_stronger[user_topic_nr] = current_stronger_color
            
            if current_color_number != previous_color_number: #color is updated
                ys_when_color_is_updated.append(el)
                
                if current_simplifyed_color == get_weaker_form_of_named_color("lavender", 0.4):
                    current_simplifyed_color = get_weaker_form_of_named_color("honeydew", 0.5)
                    current_stronger_color = "darkseagreen"
                else:
                    current_simplifyed_color = get_weaker_form_of_named_color("lavender", 0.4)
                    current_stronger_color = "mediumpurple"

            previous_color_number = current_color_number
        else: # Use every other
            color_mapping[el + 1] = current_simplifyed_color
            if current_simplifyed_color == get_weaker_form_of_named_color("lavender", 0.4):
                current_simplifyed_color = get_weaker_form_of_named_color("honeydew", 0.5)
            else:
                current_simplifyed_color = get_weaker_form_of_named_color("lavender", 0.4)
  

    
    # Make the horizontal colors and lines
    
    min_year = min_timestamp.astype(object).year + 1
    max_year = max_timestamp.astype(object).year + 1
    years_to_plot = range(min_year, max_year)
    
                
    topic_names_resorted = [0]*len(topic_names) # For the y-tick-labels
    topic_names_resorted_only_numbers = [0]*len(topic_names) # For left side y-tick-labels
    y_width = 0.5
    for user_topic_nr in range(0, len(topic_names), 1):
        
        y = get_y_value_for_user_topic_nr(user_topic_nr, order_mapping_flattened, order_mapping)
        
        print(topic_names_resorted[y])
        print(topic_names[user_topic_nr])
        topic_names_resorted[y] = topic_names[user_topic_nr]
        topic_names_resorted_only_numbers[y] = str(user_topic_nr + 1)
        ty = -y
        
        # The horizontal line in the middle of each topic
        plt.axhline(y=ty, linewidth=0.1, color='black', zorder = -50)
        if add_for_coliding_dates and vertical_line_to_represent_nr_of_documents: # To make the discrete times more connected
            # make the horizontal line thicker
            plt.axhline(y=ty, linewidth=0.9, color='black', zorder = -50)
            
        current_color = color_mapping[user_topic_nr + 1]
        
        if order_mapping:
            edgecolor = color_mapping_stronger[user_topic_nr + 1]
        
        # The colored filling
        if order_mapping:
            ax1.fill([min_timestamp, max_timestamp, max_timestamp, min_timestamp, min_timestamp], [ty - y_width, ty - y_width, ty + y_width, ty + y_width, ty - y_width], color = current_color, edgecolor = edgecolor, linewidth=0.2, linestyle="solid", zorder = -10000)
        else:
            ax1.fill([min_timestamp, max_timestamp, max_timestamp, min_timestamp, min_timestamp], [ty - y_width, ty - y_width, ty + y_width, ty + y_width, ty - y_width], color = current_color, linewidth=0.1, linestyle="solid", zorder = -10000)
            if current_color == get_weaker_form_of_named_color("lavender", 0.4):
            #TODO: a better solution for comparing to get_weaker_form_of_named_color
                dots_color = "mediumpurple"
            else:
                dots_color = "darkseagreen"
                    
            for year_to_plot in years_to_plot:
                first_day = np.datetime64(str(year_to_plot) + "-01-01")
                middle_year = np.datetime64(str(year_to_plot) + "-07-01")
                ax1.scatter(first_day,-y-y_width, color=dots_color, zorder=-50, marker='D', s=0.1)
                ax1.scatter(middle_year,-y-y_width, color=dots_color, zorder=-50, marker='D', s=0.01)
    for year_to_plot in years_to_plot:
        first_day = np.datetime64(str(year_to_plot) + "-01-01")
        middle_year = np.datetime64(str(year_to_plot) + "-07-01")
        ax1.scatter(first_day, 0+y_width, color="mediumpurple", zorder=-50, marker='D', s=0.1)
        ax1.scatter(middle_year, 0+y_width, color="mediumpurple", zorder=-50, marker='D', s=0.01)
    
    
    # lines separating the colors
    if order_mapping:
        separating_color = "mediumpurple"
        plt.axhline(y=+y_width, linewidth=1, color="black", zorder = -40) #start with a black line
        for y in ys_when_color_is_updated[:-1]:
            if separating_color == "mediumpurple":
                separating_color = "darkseagreen"
            else:
                separating_color = "mediumpurple"
            plt.axhline(y=-y-y_width, linewidth=1, color=separating_color, zorder = -40)
        plt.axhline(y=-ys_when_color_is_updated[-1]-y_width, linewidth=1, color="black", zorder = -40) # End with a black line
        plt.yticks([+y_width] + [-y-y_width for y in ys_when_color_is_updated], [], minor=False) # Mark color change with y-tick-lines also
        plt.yticks([-y for y in range(0, len(topic_names), 1)], topic_names_resorted, minor=True)
    else:
        plt.yticks([-y for y in range(0, len(topic_names), 1)], topic_names_resorted, minor=False)
    
    ax1.set_xticklabels(ax1.xaxis.get_majorticklabels(), rotation=-90)

    ax1.yaxis.set_label_position("right")
    ax1.yaxis.tick_right()
    
    # Add topic number in small letters to the left
    
    for y in range(0, len(topic_names)):
        if order_mapping_flattened:
            ax1.text(min_timestamp-5, -y, order_mapping_flattened[y], fontsize=2)
        else:
            ax1.text(min_timestamp-5, -y, str(y+1), fontsize=2)
        
    # Make colors markings in the beginning and end of the timeline
    # And extra horisonal, dotted lines when 'order_mapping' is given
    if order_mapping:
        striped_transpar = 1
        for y in range(0, len(topic_names)):
            user_nr = order_mapping_flattened[y]
            color_to_use = color_mapping_stronger[user_nr]
            
            if striped_transpar:
                color_to_use = get_weaker_form_of_named_color(color_to_use, 0.1)
            
            
            if y not in ys_when_color_is_updated:
                if striped_transpar:
                    for year_to_plot in years_to_plot:
                        first_day = np.datetime64(str(year_to_plot) + "-01-01")
                        middle_year = np.datetime64(str(year_to_plot) + "-07-01")
                        ax1.scatter(first_day,-y-0.5, color=color_mapping_stronger[user_nr], facecolor=color_mapping[user_nr], zorder=-50, marker='D', s=0.1)
                        ax1.scatter(middle_year,-y-0.5, color=color_mapping_stronger[user_nr], facecolor=color_mapping[user_nr], zorder=-50, marker='D', s=0.01)
                else:
                    ax1.axhline(-y-0.5, color=color_mapping_stronger[user_nr], zorder=-50, linewidth=0.1, linestyle="solid")
            if striped_transpar == 1:
                striped_transpar = 0
            else:
                striped_transpar = 1
            
    print("Created background")
    # For each document, plot its corresponding topics
    nr_of_plotted = 0
    bar_height = 0.5
    
    for timestamp, topic_dict in timestamp_topics_dict.items():
        #print("timestamp", timestamp)
        original_timestamp = timestamp
        if use_date_format:
            year = timestamp.astype(object).year
        else:
            if max_decimal_part_for_year[year] != 0: #TODO: Check if it works
                dec_part, year = modf(timestamp)
                year = int(year)
                dec_part = dec_part*0.999/max_decimal_part_for_year[year] # To make it more even spread out
                timestamp = year + dec_part
            

        # The vertical line, representing documents
        if add_for_coliding_dates and vertical_line_to_represent_nr_of_documents: #make the line width represent the number of documents
            base_names = meta_data_dict[timestamp]
            nr_of_texts = len(base_names)
            bar_width = 3.0
            bar_height = 0.9
            plt.axvline(x=timestamp, linewidth=bar_width*nr_of_texts/max_texts, color = [0, 0, 0, 0], zorder = -1000)
        elif add_for_coliding_dates:
            bar_width = 1.0
            bar_height = 1.0
            
            plt.axvline(x=int(timestamp), linewidth=0.1, color='gainsboro', zorder = -1000)
        else:
            plt.axvline(x=timestamp, linewidth=width_vertical_line, color= [0.9, 0.9, 0.9, 1], zorder = -1000)
        
        
        # Plot the occurrences of topics in the documents
        for topic_index, confidence in topic_dict.items():
            topic_nr_show_to_user = show_to_user_nr_topic_index_mapping[topic_index]
            y_value_for_topic_nr = get_y_value_for_user_topic_nr(topic_nr_show_to_user, order_mapping_flattened, order_mapping)
                 
            max_confidence_for_topic = max_topic_confidence_for_topic[topic_index]
            ty = -y_value_for_topic_nr
            if use_separate_max_confidence_for_each_topic:
                cw2 = bar_height*confidence/max_confidence_for_topic
            else:
                cw2 = bar_height*confidence/max_topic_confidence
            
            if log:
                if confidence < 0.1:
                    continue # Don't plot very small values
                multiplied_confidence = confidence*10
                if multiplied_confidence < 1:
                    print("To small confidence to plot", multiplied_confidence, confidence)
                    exit()
                cw2 = bar_height*math.log(multiplied_confidence, 1000)/math.log(10*max_topic_confidence, 1000)


            
            if add_for_coliding_dates and normalise_for_nr_of_texts:
                base_names = meta_data_dict[timestamp]
                nr_of_texts = len(base_names)
                max_weighted_confidence = max_topic_confidence/nr_of_texts_for_max_topic_confidence
                cw2 = 0.6*confidence/nr_of_texts/max_weighted_confidence
            
            # The actual vertical bar showing the strength of the topic for the text
            ax1.plot([timestamp, timestamp], [ty + cw2, ty - cw2], '-', markersize=0, color = [0, 0, 0, bar_transparency], linewidth=bar_width, zorder = -2*cw2)
                        

            s1 = ax1.scatter([timestamp], [ty], color=[0, 0, 0, bar_transparency], facecolor=[0, 0, 0, bar_transparency/5], marker="o", s=cw2*cw2*circle_scale_factor, linewidth=0.1, zorder=-cw2*20)
            s2 = ax1.scatter([timestamp, timestamp], [ty + cw2,  ty - cw2], color=[0, 0, 0, bar_transparency], facecolor=[0, 0, 0, bar_transparency], marker="s", s=cw2*bar_width*1.5, linewidth=0.1, zorder=-cw2)

            if link_mapping_func:
                #s = ax1.scatter([timestamp, timestamp], [ty + cw2,  ty - cw2], color=[0, 0, 0, 0.5], facecolor=[0, 0, 0, 0.5], marker="s", s=cw2*10, linewidth=0.1, zorder=-cw2)
                
                link = link_mapping_func(timestamp_basename_dict[timestamp])
                s1.set_urls([link, link]) # Seems to be a bug, you need at least two links, although it's only one scatter point
                s2.set_urls([link, link])
                # Can't set urls on lines, only scatter markers. So add three scatter markers with links
    

            
            # give labels to the most strong document occurrences
            if False: #not add_for_coliding_dates:
                max_confidence_for_topic_for_year = max_confidence_for_year_dict[(year, topic_index)]
                base_name = timestamp_basename_dict[original_timestamp]
                if confidence == max_confidence_for_topic_for_year:
                    ax1.text(timestamp, ty + cw2, base_name, size=0.01, color="lightgrey")
                elif confidence > max_confidence_for_topic_for_year*0.90:
                    ax1.text(timestamp, ty - cw2, base_name, size=0.01, color="lightgrey")
                elif confidence > max_confidence_for_topic_for_year*0.80:
                    ax1.text(timestamp, ty, base_name, size=0.01, color="lightgrey")

            nr_of_plotted = nr_of_plotted + 1
            if nr_of_plotted % 100 == 0:
                print(timestamp, end=" ", flush=True)
    
        # For debug
        if nr_of_plotted > 400:
            #break
            pass
    
    plt.yticks(fontsize=9)
    plt.tight_layout()


    if not os.path.exists(outputdir):
        os.mkdir(outputdir)
    save_to_pdf = os.path.join(outputdir, file_name + ".pdf")
    save_to_svg = os.path.join(outputdir, file_name + ".html")
        
    print("Save plot in: ", save_to_pdf, "and", save_to_svg)
    plt.savefig(save_to_svg, dpi = 700, transparent=False, format="svg")
    plt.savefig(save_to_pdf, dpi = 700, transparent=False, format="pdf")



