

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

plt.rcParams["font.family"] = "monospace"

#https://stackoverflow.com/questions/60952034/add-a-hyperlink-in-a-matplotlib-plot-inside-a-pdfpages-page-python

def get_y_value_for_user_topic_nr(original_nr, order_mapping_flattened, order_mapping):
    if not order_mapping:
        return original_nr
    else: # User don't use 0
        original_nr = original_nr + 1
        return order_mapping_flattened.index(original_nr)
        
def flatten_extend(order_list):
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


###
# Start
#####

def make_plot(model_file, outputdir, metadata_file_name, file_name, add_for_coliding_dates=False, label_length=20, normalise_for_nr_of_texts=False, use_date_format=True, vertical_line_to_represent_nr_of_documents=False, log=False, hours_between_label_dates=24, width_vertical_line=0.0000001, extra_x_length=0.07, order_mapping=None, use_separate_max_confidence_for_each_topic=True):

    order_mapping_flattened = flatten_extend(order_mapping)

    
    if log:
        print("Not yet implemented")
        sys.exit(0)
        
    label_translations = False # TODO: Add as an option
    print("use_date_format", use_date_format)
    obj = None
    
    with open(model_file, 'r') as f:
        data = f.read()
        obj = json.loads(data)

    
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
    print(max_decimal_part_for_year)
    
    # Collect all topics for the documents. # Store in document_info, with "base_name" of the documetn as the key
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

    #
    timestamps = sorted(meta_data_dict.keys())
    timestamp_topics_dict = {}
    max_confidence_for_year_dict = {}
    timestamp_basename_dict = {}
    max_texts = 0

    for i in range(0, len(timestamps)):
        timestamp = timestamps[i]
        base_names = meta_data_dict[timestamp]
    
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
            if use_date_format:
                part = int(1/len(base_names)*hours_between_label_dates)
                distance = np.timedelta64(part, 'h')
            else:
                distance = 1/len(base_names) #TODO does not work
                exit("SPREAD OUT NOT YET IMPLEMENTED FOR NON_DATES")
            
            for base_name in base_names:
                if use_date_format:
                    year = timestamp.astype(object).year
                else:
                    year = int(timestamp)
                    
                if base_name in document_info:
                    for document_topic in document_info[base_name]:
                        topic_index = document_topic["topic_index"]
                        topic_confidence = document_topic["topic_confidence"]
                        
                        timestamp_topics_dict[timestamp][topic_index] = topic_confidence
                        if topic_confidence > max_topic_confidence:
                            max_topic_confidence = topic_confidence
                        
                        if (year, topic_index) in max_confidence_for_year_dict:
                            if max_confidence_for_year_dict[(year, topic_index)] < topic_confidence:
                                max_confidence_for_year_dict[(year, topic_index)] = topic_confidence
                        else:
                            max_confidence_for_year_dict[(year, topic_index)] = topic_confidence
                            
                timestamp_basename_dict[timestamp] = base_name
                
                timestamp = timestamp + distance #spread out the documents over the day
                timestamp_topics_dict[timestamp] = {}
         
    for key, item in timestamp_topics_dict.items():
        print(key, item)

    min_timestamp = min_timestamp - (max_timestamp - min_timestamp)*extra_x_length #TODO: Make more generic
    max_timestamp = max_timestamp + (max_timestamp - min_timestamp)*extra_x_length
#TODO: Make more generic

    print("max_texts", max_texts)
    print("nr_of_texts_for_max_topic_confidence", nr_of_texts_for_max_topic_confidence)
     #70
     
    # Give the topics their labels to show to the user and the number for the topic to show to the user
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

    #scatter_dict_science, year_title_dict_science, max_topic_confidence_science = create_scatter_dict_and_year_title_tuple(document_info)

    print("max_topic_confidence", max_topic_confidence)

    #plt.figure(figsize = (8.268, 11.693))
    fig, ax1 = plt.subplots(figsize = (11.693, 8.268))

    ax1.set(xlim=(min_timestamp, max_timestamp))
    #plt.yticks([-y for y in range(0, len(topic_names), 1)], topic_names)
    
    if use_date_format:
        plt.gca().xaxis.set_major_locator(mdates.YearLocator())
        plt.gca().xaxis.set_minor_locator(mdates.MonthLocator())
    else:
        years = [int (a) for a in timestamps_sorted]
        plt.gca().xaxis.set_major_locator(FixedLocator(years))
   
    ax1.set_xticklabels(ax1.xaxis.get_majorticklabels(), rotation=-90)

    ax1.yaxis.set_label_position("right")
    ax1.yaxis.tick_right()
    
    
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
    current_simplifyed_color = "lavender"
    color_mapping = {} # Mapping from user-shown topic nr:s to colors
    ys_when_color_is_updated = [] # To be able to draw a line between the colors
    for el in range(0, len(topic_names)):
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
        if current_color_number != previous_color_number: #color is updated
            ys_when_color_is_updated.append(el)
            
            if current_simplifyed_color == "lavender":
                current_simplifyed_color = "honeydew"
            else:
                current_simplifyed_color = "lavender"
        

        previous_color_number = current_color_number
        

    
    # Make the horizontal colors and lines
    topic_names_resorted = [0]*len(topic_names) # For the y-tick-labels
    y_width = 0.5
    for user_topic_nr in range(0, len(topic_names), 1):
        
        y = get_y_value_for_user_topic_nr(user_topic_nr, order_mapping_flattened, order_mapping)
        
        topic_names_resorted[y] = topic_names[user_topic_nr]
        
        ty = -y
        
        
        plt.axhline(y=ty, linewidth=0.1, color='black', zorder = -50)
        if add_for_coliding_dates and vertical_line_to_represent_nr_of_documents: # To make the discrete times more connected
            # make the horizontal line thicker
            plt.axhline(y=ty, linewidth=0.9, color='black', zorder = -50)
            
        current_color = color_mapping[user_topic_nr + 1]
        
        
        edgecolor = [0.9, 0.9, 0.9, 0.2]
            
        ax1.fill([min_timestamp, max_timestamp, max_timestamp, min_timestamp, min_timestamp], [ty - y_width, ty - y_width, ty + y_width, ty + y_width, ty - y_width], color = current_color, edgecolor = edgecolor, linewidth=2, linestyle="solid", zorder = -10000)
      
    plt.yticks([-y for y in range(0, len(topic_names), 1)], topic_names_resorted, minor=True)
    
    # lines separating the colors
    plt.axhline(y=+y_width, linewidth=1, color='black', zorder = -50)
    for y in ys_when_color_is_updated:
        plt.axhline(y=-y-y_width, linewidth=0.5, color='black', zorder = -50)
    plt.yticks([+y_width] + [-y-y_width for y in ys_when_color_is_updated], [], minor=False) # Mark color change with y-tick-lines also
    
    print("Created background")
    
      
    
    nr_of_plotted = 0
    vertical_line_color = "lightgrey"
    bar_height = 0.5
    bar_strength = 0.2
    
    for timestamp, topic_dict in timestamp_topics_dict.items():
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
            bar_strength = 3.0
            bar_height = 0.9
            plt.axvline(x=timestamp, linewidth=bar_strength*nr_of_texts/max_texts, color='lightgrey', zorder = -1000)
        elif add_for_coliding_dates:
            bar_strength = 1.0
            bar_height = 1.0
            
            plt.axvline(x=int(timestamp), linewidth=0.1, color='gainsboro', zorder = -1000)
        else:
            plt.axvline(x=timestamp, linewidth=width_vertical_line, color=vertical_line_color, zorder = -1000)
        
        if vertical_line_color == "lightgrey":
            vertical_line_color = "gainsboro"
        else:
            vertical_line_color = "lightgrey"
        
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

            # Probably only confuses, so remove
            #ax1.scatter(timestamp, ty, color="black", s=cw2*2, marker="*")
            
            if add_for_coliding_dates and normalise_for_nr_of_texts:
                base_names = meta_data_dict[timestamp]
                nr_of_texts = len(base_names)
                max_weighted_confidence = max_topic_confidence/nr_of_texts_for_max_topic_confidence
                cw2 = 0.6*confidence/nr_of_texts/max_weighted_confidence
            
            ax1.plot([timestamp, timestamp], [ty + cw2, ty - cw2], '-', markersize=0, color = "black", linewidth=bar_strength)
            
            # give labels to the most strong document occurrences
            if not add_for_coliding_dates:
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
    
    
        if nr_of_plotted > 200:
            #break
            pass
    
    plt.yticks(fontsize=9)
    plt.tight_layout()

    if not os.path.exists(outputdir):
        os.mkdir(outputdir)
    save_to = os.path.join(outputdir, file_name)
    print("Save plot in: ", save_to)
    plt.savefig(save_to, dpi = 700, transparent=False, format="pdf")



