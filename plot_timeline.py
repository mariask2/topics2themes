

import numpy as np
import matplotlib.pyplot as plt
import json
import matplotlib.markers as markers
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
from matplotlib import cm
import math
import matplotlib.colors as colors
import os


plt.rcParams["font.family"] = "monospace"


###
# Start
#####

obj = None
"""
model_file = "/Users/marsk757/topics2themes/topics2themes/data_folder/framtidens-kultur_automatiskt/topics2themes_exports_folder_created_by_system/6435235bfa0b2425fb69e3bf_model.json"
metadata_file_name = "/Users/marsk757/topics2themes/topics2themes/data_folder/framtidens-kultur_automatiskt/topics2themes_exports_folder_created_by_system/all_files.csv"
"""

model_file = "/Users/marsk757/topics2themes/topics2themes/data_folder/climate-news/topics2themes_exports_folder_created_by_system/64392f5cdaa0df40b82d1773_model.json"
metadata_file_name = "/Users/marsk757/topics2themes/topics2themes/data_folder/climate-news/topics2themes_exports_folder_created_by_system/all_files.csv"

with open(model_file, 'r') as f:
    data = f.read()
    obj = json.loads(data)

document_info = {}
meta_data_dict = {}
max_topic_confidence = 0
min_time_stamp = np.datetime64('9999-01-02')
max_time_stamp = np.datetime64('0000-01-02')

with open(metadata_file_name) as metadata_file:
    for line in metadata_file:
        sp = line.strip().split("\t")
        time_stamp = np.datetime64(sp[1])
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
    time_stamp = np.datetime64(el["additional_labels"][0])
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
        """
        if t["topic_confidence"] > max_topic_confidence:
            max_topic_confidence = t["topic_confidence"]
        """
    document_info[base_name] = document_topics

min_time_stamp = min_time_stamp - (max_time_stamp - min_time_stamp)*0.05 #TODO: Make more generic
max_time_stamp = max_time_stamp + (max_time_stamp - min_time_stamp)*0.05  #TODO: Make more generic

timestamp_topics_dict = {}
max_texts = 0
for timestamp, base_names in meta_data_dict.items():
    timestamp_topics_dict[timestamp] = {}
    if len(base_names) > max_texts:
        max_texts = len(base_names)
    for base_name in base_names:
        if base_name in document_info:
            for document_topic in document_info[base_name]:
                topic_index = document_topic["topic_index"]
                if topic_index not in timestamp_topics_dict[timestamp]:
                    timestamp_topics_dict[timestamp][topic_index] = 0
                timestamp_topics_dict[timestamp][topic_index] = timestamp_topics_dict[timestamp][topic_index] + document_topic["topic_confidence"]
                if timestamp_topics_dict[timestamp][topic_index] > max_topic_confidence:
                    max_topic_confidence = timestamp_topics_dict[timestamp][topic_index]

print("max_texts", max_texts)

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
    topic_name = ", ".join(repr_terms)[0:70].strip() +"..."
    topic_names.append(topic_name)



topic_sorted_for_id = sorted(obj["topic_model_output"]["topics"], key=lambda t: t["id"])
timestamps_sorted = sorted(timestamp_topics_dict.keys())

#scatter_dict_science, year_title_dict_science, max_topic_confidence_science = create_scatter_dict_and_year_title_tuple(document_info)

print("max_topic_confidence", max_topic_confidence)

#plt.figure(figsize = (8.268, 11.693))
fig, ax1 = plt.subplots(figsize = (11.693, 8.268))

ax1.set(xlim=(min_time_stamp, max_time_stamp))
plt.yticks([-y for y in range(0, 2*len(topic_names), 2)], topic_names)
#plt.xticks(timestamps_sorted, [int(x) for x in timestamps_sorted]) # TODO: Make more general
ax1.set_xticklabels(ax1.xaxis.get_majorticklabels(), rotation=-90)

ax1.yaxis.set_label_position("right")
ax1.yaxis.tick_right()

current_color = "lavender"
current_edge_color = "lavender"
for y in range(0, 2*len(topic_names)-1, 2):
    ty = -y
    y_width = 0.8
    plt.axhline(y=ty, linewidth=0.5, color='black', zorder = -50)
    ax1.fill([min_time_stamp, max_time_stamp, max_time_stamp, min_time_stamp, min_time_stamp], [ty - y_width, ty - y_width, ty + y_width, ty + y_width, ty - y_width], color = current_color, edgecolor = current_edge_color, zorder = -10000)
    if current_color == "lavender":
        current_color = "honeydew"
        current_edge_color = "honeydew"
    else:
        current_color = "lavender"
        current_edge_color = "lavender"

        
for time_stamp, topic_dict in timestamp_topics_dict.items():
    bar_height = 1.5
    bar_width = 10
    bar_strength = 2
    nr_of_texts = len(meta_data_dict[time_stamp])
    plt.axvline(x=time_stamp, linewidth=0.0001, color='silver', zorder = -1000)
    for topic_index, confidence in topic_dict.items():
        topic_nr = topic_nrs[topic_index]
        ty = -topic_nr*2
        cw2 = bar_height*confidence/max_topic_confidence/2
        ax1.plot([time_stamp, time_stamp], [ty + cw2, ty - cw2], '-', markersize=0, color = "black", linewidth=bar_strength)

        #plt.axvline(x=time_stamp, linewidth=bar_width*nr_of_texts/max_texts, color='lightgrey', zorder = -1000)
        

#plt.subplots_adjust(wspace=20, hspace=20)
file_name = "temp_out"
plt.yticks(fontsize=9)
plt.tight_layout()

plt.savefig(file_name + ".pdf", dpi = 700, transparent=False, format="pdf")



#plot_topics_text(topic_names, scatter_dict_nature, manually_sorted_ids, "Nature", "nature", min_year, max_year, year_title_dict_nature, ax1, xlabels=True, color_map = color_map, max_topic_confidence = max_topic_confidence)



