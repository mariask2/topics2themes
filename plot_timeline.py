

import numpy as np
import matplotlib.pyplot as plt
import json
import matplotlib.markers as markers
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
from matplotlib import cm
import math
import matplotlib.colors as colors
import os



def plot_topics_text(topics_reps,  topic_in_text_dict, manually_sorted_ids, title, file_name, min_year, max_year, year_title_dict, ax, xlabels, color_map, max_topic_confidence):

    margin_to_topics = 0.20
        
    classification_display_size = 0.75

    y_max_lim = len(topics_reps) + classification_display_size*len(classes_filtered) - 0.1
    ax.set_ylim(y_max_lim, -0.5)
    x_min_lim = min_year - 0.4
    x_max_lim = max_year + 1.1
    ax.set_xlim(x_min_lim , x_max_lim)
       
    
    
    ax.yaxis.set_ticklabels([])
   
    ax.yaxis.set_ticks_position('none')
    ax.xaxis.set_minor_locator(MultipleLocator(1))
   
    plt.xticks(fontsize=6)
    plt.yticks(fontsize=5.5)
   
    
 
    ax.spines["left"].set_color("silver")
    ax.spines["right"].set_color("silver")
    ax.spines["top"].set_color("silver")
    ax.spines["bottom"].set_color("silver")
    
 
    # The tick labels for the topics (y axis), and horisontal color bars
    TOPIC_DESCRIPTION_LENGTH = 20
    y_width = 0.35
    y_ticks = [el[:20].replace("_", " ") + "..." for el in topics_reps] + [""]
    
    # Before these row numbers (= y), the manual labels will be printed
    at_which_y_to_print_labels = [0, 1, 5, 9, 12, 13]
    
    # Colors for the manual labels
    econ_label_colors = [[102, 0, 102]]
    tech_label_colors = [[0, 76, 153]]
    gov_label_colors = [[153, 76, 0]]
    sci_label_colors = [[25, 51, 0]]
    com_label_colors = [[153, 0, 0]]
    other_label_colors = [[0, 102, 102]]

    color_map_label = []
    for c in econ_label_colors + tech_label_colors + gov_label_colors + sci_label_colors + com_label_colors + other_label_colors:
        color_map_label.append([c[0]/255, c[1]/255, c[2]/255, 1])
        
    
    
    ####
    # The tic labels to the right of the plot
    extra_y_for_room_for_labels = 0
    for y, (topic_id, topic_repr) in enumerate(zip(manually_sorted_ids, topics_reps)):
        color_index = y
        
        #+ " (from Hulme et al.)"
        if y in at_which_y_to_print_labels:
            label_space_nr = at_which_y_to_print_labels.index(y)
            ax.text(x_max_lim+0.23, y + extra_y_for_room_for_labels - classification_display_size/30, classes_filtered[label_space_nr], size=3.2, color = color_map_label[label_space_nr], verticalalignment='center')
            
            extra_y_for_room_for_labels = extra_y_for_room_for_labels + classification_display_size
        
        y = y + extra_y_for_room_for_labels
        
        line_color = [color_map[color_index][0], color_map[color_index][1], color_map[color_index][2], 0.20]
        text_color = [color_map[color_index][0], color_map[color_index][1], color_map[color_index][2], 1.0]
        plt.axhline(y=y, linewidth=0.55, color = line_color)
        #ax.text(x_min_lim-3,y, "Topic " + str(topic_id), size=5.0, color = "black", verticalalignment='center')
        #ax.text(x_min_lim-3,y, "Topic ", size=5.0, color = text_color, verticalalignment='center')
        ax.text(x_min_lim-3,y, manual_topic_names[color_index], size=5.0, color = text_color, verticalalignment='center')
        
        ax.text(x_max_lim + 0.25, y, y_ticks[color_index], size=3.5, color = text_color, verticalalignment='center')

        ax.fill([x_min_lim, x_max_lim, x_max_lim, x_min_lim, x_min_lim], [y - y_width, y - y_width, y + y_width, y + y_width, y - y_width], color = color_map[color_index], edgecolor = color_map[color_index])
    for c, t in zip(color_map, ax.yaxis.get_ticklabels()):
        text_color = [c[0], c[1], c[2], 1.0]
        t.set_color(text_color)
        
    # The tick labels for the labelled classes
    """
    for c_nr, class_name in enumerate(classes):
        y = len(topics_reps) + margin_to_topics + c_nr*classification_display_size
        
        y_width_class = classification_display_size/3
        class_color = "white"
        text_color = "darkgray"
        text_x_diff = 1.0
        text_x_diff_right = 0.15
        text = class_name
        if c_nr % 2 == 0:
            class_color = "whitesmoke"
            text_color = "dimgray"
            text_x_diff = 1.5
            text_x_diff_right = 0.65
            text = class_name
        ax.text(x_min_lim-text_x_diff,y, text, size=2.8, color = text_color, verticalalignment='center')
        ax.text(x_max_lim+text_x_diff_right,y, text, size=2.8, color = text_color, verticalalignment='center')
        #ax.text(min_year-text_x_diff + 0.01,y + classification_display_size/2 + 0.01, text, size=3.9, color = text_color)
        plt.axhline(y=y, linewidth=0.05, linestyle = ":", color = "black")
        ax.fill([x_min_lim, x_max_lim, x_max_lim, x_min_lim, x_min_lim], [y - y_width_class, y - y_width_class, y + y_width_class, y + y_width_class, y - y_width_class], color = class_color, edgecolor = class_color)
      """
    MOVE_X = 0.02
    last_iter_year = 0
    
    # vertical lines representing papers
    x_moved = 0.0
    for year in sorted(year_title_dict.keys()):
        article_nr_position_extra = 0
        title_list = year_title_dict[year]
        move_x = 1/len(title_list)
        for article_nr, article_title in enumerate(title_list):
            if last_iter_year != year:
                x_moved = 0.0
            else:
                x_moved = x_moved + move_x
       
            linewidth=0.04
            x = year + x_moved
            if x_moved == 0.0: # first line for year
                extra = 0.01
                linewidth = linewidth + extra*4
                x = x - extra
            linestyle = "-"
            if article_nr % 2 != 0:
                linestyle=":"
            plt.axvline(x=x, linewidth=linewidth, color="black", linestyle = linestyle)
            
            #ax.text(x, -1.0, article_title, size=0.00001, color = "darkgray", rotation=90, horizontalalignment='center', verticalalignment='bottom')
            
            # Small numbers on the line, in order to be able to retrieve the titles
            #y_extra = len(topics_reps) -0.5 + 0.15*(article_nr_position_extra)
            """
            for tr, top in enumerate(topics_reps):
                if tr == 0:
                    continue
                
                y_extra = tr - 0.4
                if article_nr % 2 != 0:
                    ax.text(x - 0.03, 0 + y_extra, str(article_nr + 1), size=0.0001, color = "darkgray", rotation=-90, horizontalalignment='center', verticalalignment='top')
            
            
            for ci, c in enumerate(classes):
                if ci % 2 != 0:
                    continue
                y_extra = len(topics_reps) + margin_to_topics + ci*classification_display_size + 0.2
                if article_nr % 2 != 0:
                    ax.text(x - 0.03, 0 + y_extra, str(article_nr + 1), size=0.0001, color = "darkgray", rotation=-90, horizontalalignment='center', verticalalignment='top')
            """
                
            #article_nr_position_extra = article_nr_position_extra + 1
            #if article_nr_position_extra == 3:
                #article_nr_position_extra = 0

            # Line indicating an article
            #ax.plot([x, x], [-0.5, len(topics_reps)-0.5], '.-', linewidth=linewidth, markersize=0, color = "black")
            # Indication of the classification
            #ax.plot([x, x], [len(topics_reps), len(topics_reps) + classification_display_size*len(classes)], '.-', linewidth=linewidth, markersize=0, color = "red")
            last_iter_year = year
    for era_year in [1988, 1993, 1999, 2005, 2011]:
        #ax.text(era_year, y_max_lim + 0.9, str(era_year), horizontalalignment='center', size=2.9)
        ax.text(era_year, -1.0, str(era_year), horizontalalignment='center', size=2.9)
    printed = []
    
    
    topic_strength_f = (y_width*2)/max_topic_confidence
    # Plot topics and manual labels
    
    for year, texts_for_year in topic_in_text_dict.items():
        
        extra_y_for_room_for_labels = 0
        
        for y, (topic_id, topic_repr) in enumerate(zip(manually_sorted_ids, topics_reps)):
        
            print_labels = False
            if y in at_which_y_to_print_labels:
                print_labels = True
                y_for_labels = y
                extra_y_for_room_for_labels = extra_y_for_room_for_labels + classification_display_size
                
            y = y + extra_y_for_room_for_labels
            
            topic_id = topic_id - 1 # Zero counting in scatter and plot, and 1 counting for topics
            move_x = 1/len(texts_for_year)
            x_moved = 0.0
            for (topic_in_text, label) in texts_for_year: # go through scatter-vector for each text for the year
                marker = markers.MarkerStyle(marker='|', fillstyle='none')
                if topic_in_text[topic_id] != 0: #if the text contains the topic
                    ax.plot([year + x_moved, year + x_moved], [y + topic_in_text[topic_id] * topic_strength_f/1.5, y - topic_in_text[topic_id] * topic_strength_f/1.5], '.-', linewidth=0.4, markersize=0, color = "black")
               
                # plot the class (= manual label) for the text
                if print_labels and label not in ["B_dominant_frame", "C_dominant_frame", "D_dominant_frame"]:
                    label_nr = label_list_filtered.index(label)
                    label_space_nr = at_which_y_to_print_labels.index(y_for_labels)
                    if label_nr == label_space_nr:
                        y_for_labels_to_plot = y_for_labels + extra_y_for_room_for_labels - classification_display_size
                        ax.plot([year + x_moved, year + x_moved], [y_for_labels_to_plot + classification_display_size/30, y_for_labels_to_plot + classification_display_size/30], 'o-', linewidth=1.5, markersize=0.60, color = color_map_label[label_space_nr], fillstyle='full')
                
                # Move the next text for the year a bit to the right
                x_moved = x_moved + move_x
        
    plt.xticks(ha='center')
    ax.set_title(title, fontsize=6, loc="right") # x=-0.41,y=0.92)# )rotation='vertical'
              
    #fig.tight_layout()
    


def create_scatter_dict_and_year_title_tuple(document_info):
    exit()
    scatter_dict = {}
    year_title_dict = {}
    most_typical_documents_for_topics = {}
    max_topic_confidence = 0
    nr_documents_to_scatter_dict = 0
    nr_documents_to_scatter_dict_with_topics_found = 0
    nr_documents_not_associated_with_topic_in_model = 0
    for el in editorial_data_list:
        id = el[0]
        topic_found = False
        year = int(el[1])
        label = el[3]
        label_index = label_list.index(label)
        class_name = classes[label_index]
        if year not in scatter_dict:
            scatter_dict[year] = []
        if year not in year_title_dict:
            year_title_dict[year] = []
        title = el[2]
        year_title_dict[year].append(title)
        
        # Create an empty vector
        scatter_for_editorial = [0]*len(topics.keys())
        
        # If there are topics found for the document, fill the
        # vector with information of how strong the topic is
        # for this document
        if id in document_info: # topic in document
            for topic_in_document in document_info[id]["document_topics"]:
                index_for_topic_in_scatter = sorted(topics.keys()).index(topic_in_document["topic_index"])
                scatter_for_editorial[index_for_topic_in_scatter] =      topic_in_document["topic_confidence"]
                if (topic_in_document["topic_confidence"] > max_topic_confidence):
                    max_topic_confidence = topic_in_document["topic_confidence"]
                topic_found = True
               
        else:
            nr_documents_not_associated_with_topic_in_model = nr_documents_not_associated_with_topic_in_model + 1
            
            
        scatter_dict[year].append((scatter_for_editorial, label))
        nr_documents_to_scatter_dict = nr_documents_to_scatter_dict + 1
        if topic_found:
            nr_documents_to_scatter_dict_with_topics_found = nr_documents_to_scatter_dict_with_topics_found + 1
        
        

    print("nr_documents_to_scatter_dict", nr_documents_to_scatter_dict)
    print("nr_documents_to_scatter_dict_with_topics_found", nr_documents_to_scatter_dict_with_topics_found)
    print("nr_documents_not_associated_with_topic_in_model", nr_documents_not_associated_with_topic_in_model)
    
    return scatter_dict, year_title_dict, max_topic_confidence
    
    
    
###
# Start
#####

obj = None
model_file = "/Users/marsk757/topics2themes/topics2themes/data_folder/framtidens-kultur_automatiskt/topics2themes_exports_folder_created_by_system/64307ccf714f076e957c9bea_model.json"
metadata_file_name = "/Users/marsk757/topics2themes/topics2themes/data_folder/framtidens-kultur_automatiskt/topics2themes_exports_folder_created_by_system/all_files.csv"
 
with open(model_file, 'r') as f:
    data = f.read()
    obj = json.loads(data)

document_info = {}
meta_data_dict = {}
max_topic_confidence = 0
min_time_stamp = math.inf
max_time_stamp = -math.inf

with open(metadata_file_name) as metadata_file:
    for line in metadata_file:
        sp = line.strip().split("\t")
        time_stamp = float(sp[1])
        if time_stamp not in meta_data_dict:
            meta_data_dict[time_stamp] = []
        base_name = os.path.basename(sp[0])
        meta_data_dict[time_stamp].append(base_name)


for el in obj["topic_model_output"]["documents"]:
    base_name = el["base_name"]
    if len(el["additional_labels"]) > 1:
        print("More than one timestamp", el)
        exit()
    if len(el["additional_labels"]) == 0:
        print("No timestamp", el)
        exit()
    time_stamp = float(el["additional_labels"][0])
    if time_stamp < min_time_stamp:
        min_time_stamp = time_stamp
    if time_stamp > max_time_stamp:
        max_time_stamp = time_stamp
    
    document_topics = []
    for t in el["document_topics"]:
        topic_info = {}
        topic_info["terms_found_in_text"] = t["terms_found_in_text"]
        topic_info["topic_index"] = t["topic_index"]
        topic_info["topic_confidence"] = t["topic_confidence"]
        #if len(topic_info["terms_found_in_text"]) > 1: # At least two terms included in text to include
        document_topics.append(topic_info)
        if t["topic_confidence"] > max_topic_confidence:
            max_topic_confidence = t["topic_confidence"]
            
    document_info[base_name] = document_topics



topic_names = []
topic_nrs = {}
for nr, el in enumerate(obj["topic_model_output"]["topics"]):
    topic_index = el["id"]
    topic_nrs[topic_index] = nr
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
    topic_name = ", ".join(repr_terms)[0:50].strip() +"..."
    topic_names.append(topic_name)



topic_sorted_for_id = sorted(obj["topic_model_output"]["topics"], key=lambda t: t["id"])


#scatter_dict_science, year_title_dict_science, max_topic_confidence_science = create_scatter_dict_and_year_title_tuple(document_info)

print("max_topic_confidence", max_topic_confidence)


fig, ax1 = plt.subplots()

ax1.set(xlim=(min_time_stamp, max_time_stamp))
plt.yticks([-y for y in range(0, len(topic_names))], topic_names)
ax1.yaxis.set_label_position("right")
ax1.yaxis.tick_right()
for y in range(0, len(topic_names)):
    plt.axhline(y=-y, linewidth=0.55, color='k')
    
for time_stamp, name_list in meta_data_dict.items():
    time_stamp = float(time_stamp)
    plt.axvline(x=time_stamp, linewidth=0.1, color='k')
    for name in name_list:
        if name in document_info:
            document = document_info[name]
            for topic_for_document in document:
                topic_nr = topic_nrs[topic_for_document['topic_index']]
                confidence = topic_for_document["topic_confidence"]
                ty = -topic_nr
                cw2 = confidence/max_topic_confidence/1.2
                if confidence > 0.1:
                    #plt.scatter(time_stamp, -topic_nr)
                    ax1.plot([time_stamp, time_stamp], [ty + cw2, ty - cw2], '.-', linewidth=0.6, markersize=0, color = "black")
                
plt.show()



#plot_topics_text(topic_names, scatter_dict_nature, manually_sorted_ids, "Nature", "nature", min_year, max_year, year_title_dict_nature, ax1, xlabels=True, color_map = color_map, max_topic_confidence = max_topic_confidence)



