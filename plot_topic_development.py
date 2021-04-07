

#https://matplotlib.org/3.1.3/gallery/subplots_axes_and_figures/align_labels_demo.html#sphx-glr-gallery-subplots-axes-and-figures-align-labels-demo-py

#        for tick in ax.get_xticklabels():
#    tick.set_rotation(55)

#https://matplotlib.org/3.1.3/gallery/lines_bars_and_markers/linestyles.html#sphx-glr-gallery-lines-bars-and-markers-linestyles-py
#     ax.set(xticks=[], ylim=(-0.5, len(linestyles)-0.5),
 #      yticks=np.arange(len(linestyles)), yticklabels=yticklabels)

#https://matplotlib.org/3.1.3/gallery/lines_bars_and_markers/horizontal_barchart_distribution.html#sphx-glr-gallery-lines-bars-and-markers-horizontal-barchart-distribution-py

#https://matplotlib.org/3.1.3/gallery/lines_bars_and_markers/marker_fillstyle_reference.html#sphx-glr-gallery-lines-bars-and-markers-marker-fillstyle-reference-py

import numpy as np
import matplotlib.pyplot as plt
import json
import matplotlib.markers as markers
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
from matplotlib import cm
import math

# Different names in paper and in data, but same classes
label_list = ["A_dominant_frame", "B_dominant_frame", "C_dominant_frame", "D_dominant_frame", "E_dominant_frame", "F_dominant_frame", "G_dominant_frame", "H_dominant_frame"]
classes = ["eco", "dev", "sec","eth", "tec", "gov", "sci", "com"]
 
def plot_topics_text(topics_reps,  topic_in_text_dict, title, file_name, min_year, max_year, year_title_dict, ax, xlabels, color_map, max_topic_confidence):

    margin_to_topics = 0.20
    
    # To
    #plot_right_margin = 0.0
    
    classification_display_size = 0.55

    y_max_lim = len(topics_reps) + classification_display_size*len(classes) - 0.1 + margin_to_topics
    ax.set_ylim(y_max_lim, -0.5)
    x_min_lim = min_year - 0.4
    x_max_lim = max_year + 1.1
    ax.set_xlim(x_min_lim , x_max_lim)
    #ax.yaxis.set_ticks(range(0, len(topics_reps) + 1))
 
    
    
    
    ax.yaxis.set_ticklabels([])
    #ax.yaxis.set_ticklabels(y_ticks)
    #ax.yaxis.tick_right()
    ax.yaxis.set_ticks_position('none')
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    #ax.tick_params(axis="x", top=True, which="both")
    plt.xticks(fontsize=6)#, rotation=90)
    plt.yticks(fontsize=5.5)
    #ax.xaxis.set_label_position('top')
    
 
    ax.spines["left"].set_color("silver")
    ax.spines["right"].set_color("silver")
    ax.spines["top"].set_color("silver")
    ax.spines["bottom"].set_color("silver")
    
 
    # The tick labels for the topics (y axis), and horisontal color bars
    TOPIC_DESCRIPTION_LENGTH = 20
    y_width = 0.35
    y_ticks = [el[:20].replace("_", " ") + "..." for el in topics_reps] + [""]
    for y, topic_repr in enumerate(topics_reps):
        line_color = [color_map[y][0], color_map[y][1], color_map[y][2], 0.20]
        text_color = [color_map[y][0], color_map[y][1], color_map[y][2], 1.0]
        plt.axhline(y=y, linewidth=0.55, color = line_color)
        ax.text(x_min_lim-3,y, "Topic " + str(y + 1), size=5.0, color = "black", verticalalignment='center')
        ax.text(x_min_lim-3,y, "Topic ", size=5.0, color = text_color, verticalalignment='center')
        ax.text(x_max_lim + 0.25, y, y_ticks[y], size=3.5, color = text_color, verticalalignment='center')
        #ax.text(x_max_lim + 0.1 - plot_right_margin, y+0.3, "(", size=4.0, color = "black")
        ax.fill([x_min_lim, x_max_lim, x_max_lim, x_min_lim, x_min_lim], [y - y_width, y - y_width, y + y_width, y + y_width, y - y_width], color = color_map[y], edgecolor = color_map[y])
    for c, t in zip(color_map, ax.yaxis.get_ticklabels()):
        text_color = [c[0], c[1], c[2], 1.0]
        t.set_color(text_color)
        
    # The tick labels for the labelled classes
    for c_nr, class_name in enumerate(classes):
        y = len(topics_reps) + margin_to_topics + c_nr*classification_display_size
        
        y_width_class = classification_display_size/3
        class_color = "white"
        text_color = "darkgray"
        text_x_diff = 1.5
        text_x_diff_right = 0.15
        text = class_name
        if c_nr % 2 == 0:
            class_color = "whitesmoke"
            text_color = "dimgray"
            text_x_diff = 1.0
            text_x_diff_right = 0.65
            text = class_name
        ax.text(x_min_lim-text_x_diff,y, text, size=3.5, color = text_color, verticalalignment='center')
        ax.text(x_max_lim+text_x_diff_right,y, text, size=3.5, color = text_color, verticalalignment='center')
        #ax.text(min_year-text_x_diff + 0.01,y + classification_display_size/2 + 0.01, text, size=3.9, color = text_color)
        plt.axhline(y=y, linewidth=0.05, linestyle = ":", color = "black")
        ax.fill([x_min_lim, x_max_lim, x_max_lim, x_min_lim, x_min_lim], [y - y_width_class, y - y_width_class, y + y_width_class, y + y_width_class, y - y_width_class], color = class_color, edgecolor = class_color)
        
    MOVE_X = 0.02
    last_iter_year = 0
    
    # vertical lines representing papers
    x_moved = 0.0
    for year in sorted(year_title_dict.keys()):
        article_nr_position_extra = 0
        title_list = year_title_dict[year]
        move_x = 1/len(title_list)
        for article_nr, article_title in enumerate(title_list):
            #print(article_title)
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
            for tr, top in enumerate(topics_reps):
                if tr == 0:
                    continue
                #y_extra = len(topics_reps) - 0.5
                y_extra = tr - 0.4
                if article_nr % 2 != 0:
                    ax.text(x - 0.03, 0 + y_extra, str(article_nr + 1), size=0.0001, color = "darkgray", rotation=-90, horizontalalignment='center', verticalalignment='top')
            
            for ci, c in enumerate(classes):
                if ci % 2 != 0:
                    continue
                y_extra = len(topics_reps) + margin_to_topics + ci*classification_display_size + 0.2
                if article_nr % 2 != 0:
                    ax.text(x - 0.03, 0 + y_extra, str(article_nr + 1), size=0.0001, color = "darkgray", rotation=-90, horizontalalignment='center', verticalalignment='top')
                
            #article_nr_position_extra = article_nr_position_extra + 1
            #if article_nr_position_extra == 3:
                #article_nr_position_extra = 0

            # Line indicating an article
            #ax.plot([x, x], [-0.5, len(topics_reps)-0.5], '.-', linewidth=linewidth, markersize=0, color = "black")
            # Indication of the classification
            #ax.plot([x, x], [len(topics_reps), len(topics_reps) + classification_display_size*len(classes)], '.-', linewidth=linewidth, markersize=0, color = "red")
            last_iter_year = year
            

    
    printed = []
    
    topic_strength_f = (y_width*2)/max_topic_confidence
    print("topic_strength_f", topic_strength_f)
    # Plot topics and manual labels
    for year, texts_for_year in topic_in_text_dict.items():
        for y, topic_repr in enumerate(topics_reps):
            move_x = 1/len(texts_for_year)
            x_moved = 0.0
            for (topic_in_text, label) in texts_for_year: # go through scatter-vector for each text for the year
                marker = markers.MarkerStyle(marker='|', fillstyle='none')
                if topic_in_text[y] != 0: #if the text contains the topic
                    ax.plot([year + x_moved, year + x_moved], [y + topic_in_text[y] * topic_strength_f/2, y - topic_in_text[y] * topic_strength_f/2], '.-', linewidth=0.4, markersize=0, color = "black")
               
                # plot the class (= manual label) for the text
                label_nr = label_list.index(label)
                label_start = len(topics_reps) + label_nr * classification_display_size + margin_to_topics
                if (label_nr, label_start) not in printed:
                    printed.append((label_nr, label_start))
                ax.plot([year + x_moved, year + x_moved], [label_start, label_start], 'o-', linewidth=0.04, markersize=0.03, color = "black")
                
                # Move the next text for the year a bit to the right
                x_moved = x_moved + move_x
        
    plt.xticks(ha='center')
    ax.set_title(title, fontsize=6, loc="right") # x=-0.41,y=0.92)# )rotation='vertical'
              
    #fig.tight_layout()
    


def create_scatter_dict_and_year_title_tuple(editorial_data_list, document_info):
    scatter_dict = {}
    year_title_dict = {}
    most_typical_documents_for_topics = {}
    most_typical_documents_for_topics_top_5 = {}
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
            #print(document_info[el[0]])
            for topic_in_document in document_info[id]["document_topics"]:
                index_for_topic_in_scatter = sorted(topics.keys()).index(topic_in_document["topic_index"])
                scatter_for_editorial[index_for_topic_in_scatter] =      topic_in_document["topic_confidence"]
                if (topic_in_document["topic_confidence"] > max_topic_confidence):
                    max_topic_confidence = topic_in_document["topic_confidence"]
                topic_found = True
               
                # For listing the five most typical titles for each topic
                if topic_in_document["topic_index"] not in most_typical_documents_for_topics:
                    most_typical_documents_for_topics[topic_in_document["topic_index"]] = []
                most_typical_documents_for_topics[topic_in_document["topic_index"]].append((topic_in_document["topic_confidence"], title, class_name))
        else:
            nr_documents_not_associated_with_topic_in_model = nr_documents_not_associated_with_topic_in_model + 1
            
            
        scatter_dict[year].append((scatter_for_editorial, label))
        nr_documents_to_scatter_dict = nr_documents_to_scatter_dict + 1
        if topic_found:
            nr_documents_to_scatter_dict_with_topics_found = nr_documents_to_scatter_dict_with_topics_found + 1
        
        

    print("nr_documents_to_scatter_dict", nr_documents_to_scatter_dict)
    print("nr_documents_to_scatter_dict_with_topics_found", nr_documents_to_scatter_dict_with_topics_found)
    print("nr_documents_not_associated_with_topic_in_model", nr_documents_not_associated_with_topic_in_model)
    
    for key, items in most_typical_documents_for_topics.items():
        top_five = sorted(items, reverse=True)[:5]
        most_typical_documents_for_topics_top_5[key] = top_five
    
    return scatter_dict, year_title_dict, max_topic_confidence, most_typical_documents_for_topics_top_5
    

editorial_data_list_science = []
editorial_data_list_nature = []
max_year = 0
min_year = 200000
with open("../klimat/master_table.tsv") as master:
    for line in master:
        sp = line.split("\t")
        try:
            year = int(sp[2])
        except ValueError:
            continue
        id = ""

        dominant = sp[-2]
        
        if year > max_year:
            max_year = year
        if year < min_year:
            min_year = year
            
        if sp[1] == "Science":
            id = sp[5].replace("10.1126/science.", "").strip()
            id = id + ".ocr.txt"
            editorial_data = (id, sp[2], sp[3], dominant)
            editorial_data_list_science.append(editorial_data)
        else:
            id = sp[6].replace(".txt", "")
            id = id + ".ocr.txt"
            editorial_data = (id, sp[2], sp[3], dominant)
            editorial_data_list_nature.append(editorial_data)


obj = None
model_file = "/Users/marsk757/topic2themes/topics2themes/data_folder/climate-editorials-graph/topics2themes_exports_folder_created_by_system/602f89d39962f2a59e2653c4_model.json"

 #"/Users/marsk757/topic2themes/topics2themes/data_folder/climate-editorials-graph/topics2themes_exports_folder_created_by_system/6025902c414336b264581333_model.json" #"/Users/marsk757/topic2themes/topics2themes/data_folder/climate-editorials-graph/topics2themes_exports_folder_created_by_system/5ff8fd96dede69ec1ede953a_model.json"
# read file
with open(model_file, 'r') as f:
    data = f.read()
    obj = json.loads(data)

document_info = {}
for el in obj["topic_model_output"]["documents"]:
    base_name = el["base_name"]
    label = el["label"]
    document_topics = []
    for t in el["document_topics"]:
        topic_info = {}
        topic_info["terms_found_in_text"] = t["terms_found_in_text"]
        topic_info["topic_index"] = t["topic_index"]
        topic_info["topic_confidence"] = t["topic_confidence"]
        if len(topic_info["terms_found_in_text"]) > 1: # At least two terms included in text to include
            document_topics.append(topic_info)
    document_info[base_name] = {"document_topics" : document_topics, "label": label}
    #print(json.dumps(el, indent = 1))
    #print(base_name, label)




topics = {}
#topics = []
for el in obj["topic_model_output"]["topics"]:
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
    #topic_name = ", ".join(repr_terms[0: third_length]).strip() + "\n" + ", ".join(repr_terms[third_length:2*third_length]).strip() + "\n" + ", ".join(repr_terms[2*third_length:]).strip()
    topic_name = ", ".join(repr_terms)[0:50].strip() +"..."
    topics[el["id"]] = topic_name


topic_names = [topics[key] for key in sorted(topics.keys())]


topic_description_file = "/Users/marsk757/topic2themes/topics2themes/data_folder/climate-editorials-graph/topics2themes_exports_folder_created_by_system/602f89d39962f2a59e2653c4_topic_name.json"

topic_name_dict = {}
with open(topic_description_file, 'r') as f:
    data = f.read()
    topic_name_obj = json.loads(data)
    for el in topic_name_obj:
        topic_name_dict[el["topic_id"]] = el["topic_name"]

print("Creating data for science")
scatter_dict_science, year_title_dict_science, max_topic_confidence_science, most_typical_documents_for_topics_top_5_science = create_scatter_dict_and_year_title_tuple(editorial_data_list_science, document_info)

print("Creating data for nature")
scatter_dict_nature, year_title_dict_nature, max_topic_confidence_nature, most_typical_documents_for_topics_top_5_nature = create_scatter_dict_and_year_title_tuple(editorial_data_list_nature, document_info)

max_topic_confidence = max(max_topic_confidence_science, max_topic_confidence_nature)
print("max_topic_confidence", max_topic_confidence)
color_map_orig = cm.get_cmap('tab20b', len(topic_names)).colors
color_map = []
for c in color_map_orig:
    color_map.append([c[0], c[1], c[2], 0.15])


########################################
# Plot the terms for each of the topics
#######################################
nr_of_topics = len(obj["topic_model_output"]["topics"])
TOPICS_PER_ROW = 5
rows = math.ceil(nr_of_topics / TOPICS_PER_ROW)
rows = rows + 0.7 # To make it closer to a4
current_row = 0

nr_of_terms = len(obj["topic_model_output"]["topics"][0]["topic_terms"])
y_lim = 1.0
x_lim = 1.0
y_heading_margin = 0.07/rows
x_jump = x_lim/TOPICS_PER_ROW
row_height = y_lim/rows

heading_space = 0.24/rows
nr_of_texts = 5
title_height_part = 1.1
y_jump = (row_height - heading_space-y_heading_margin/2)/(nr_of_terms + 1 + nr_of_texts*title_height_part )
plt.axis('off')


for index, el in enumerate(sorted(obj["topic_model_output"]["topics"], key=lambda t: t["id"])):
    combined_typical_document_list = most_typical_documents_for_topics_top_5_science[index + 1] + most_typical_documents_for_topics_top_5_nature[index + 1]
    combined_typical_document_list_top_5 = sorted(combined_typical_document_list, reverse = True)[:5]
    print(combined_typical_document_list_top_5)
    
    
    if (index) % TOPICS_PER_ROW == 0:
        #jump to next row
        current_row = current_row + 1
        #ax3 = plt.subplot(rows,1,current_row)
        ax3 = plt.subplot(1,1,1)
        ax3.set_xlim(0, x_lim)
        ax3.set_ylim(0, y_lim)
        current_x = 0.03
        plt.axis('off')
        if index == 0: # only for first row
            ax3.set_title("The most typical texts (i.e. text titles and the manual classification of the texts) and the most typical terms, for the topics detected", fontsize=5, loc="left")
    current_y = y_lim - (current_row - 1)*row_height
    heading_x = current_x + x_jump/2 #- 0.015
    background_x_start = current_x - 0.015*2
    background_x_end = background_x_start + x_jump - 0.005
    background_y_start = current_y  - row_height*0.98
    background_y_end = current_y   # the top of the rectangle
    ax3.fill([background_x_start, background_x_end, background_x_end, background_x_start, background_x_start], [background_y_start, background_y_start, background_y_end, background_y_end, background_y_start], color = color_map[index])

    topic_description_font_size = 3.3
    topic_description_extra_jump = 1.2
    MAX_DESC_LEN = 37
    topic_desc = topic_name_dict[str(index + 1)]
    string_list = []
    current_string = ""
    for chunk in topic_desc.split(" "):
        if len(current_string.strip()) + len(chunk.strip()) > MAX_DESC_LEN:
            string_list.append(current_string)
            current_string = ""
        current_string = current_string.strip() + " " + chunk.strip()
    string_list.append(current_string)
    print(string_list)
    current_y = current_y - y_heading_margin
    description_x = current_x - 0.022
    for nr, str_el in enumerate(string_list):
        ax3.text(description_x, current_y - y_jump*topic_description_extra_jump*nr, str_el.strip(), verticalalignment='bottom', fontsize=topic_description_font_size)
    
    ax3.text(current_x + x_jump*0.75, current_y - row_height + 2.6*y_jump, "Topic " + str(index + 1), verticalalignment='bottom', fontsize=4.1, rotation='vertical')
    #ax3.text(current_x + x_jump*0.735, current_y - y_jump*nr_of_terms, "Topic " + str(index + 1), verticalalignment='bottom', fontsize=3.8, rotation='vertical')

    current_y = current_y - heading_space + y_heading_margin

    for (strength, title, cls) in combined_typical_document_list_top_5:
        current_y = current_y - y_jump*title_height_part
        MAX_TITLE_LENGTH = 33
        if len(title) > MAX_TITLE_LENGTH:
            title = title[:MAX_TITLE_LENGTH-2] + "..."
        ax3.text(current_x-0.022, current_y, '"' + title + '"', verticalalignment='center', fontsize=3.0)
        ax3.text(current_x + x_jump-0.057, current_y, cls, verticalalignment='center', fontsize=3.3)

    current_y = current_y - y_jump*title_height_part/3
    for term in el['topic_terms']:
        # Construct the term representation to use
        terms_to_keep = set()
        for s_not_stripped in term["term"].split("/"):
            s = s_not_stripped.strip()
            add_term = True
            term_to_remove = None
            for kept in terms_to_keep:
                if len(s) < len(kept) and s[:3] in kept:
                    term_to_remove = kept #if longer, similiar exists remove this one
                elif kept[:3] in s:
                    add_term = False # if shorter, similar already exists don't add new one
            if add_term:
                terms_to_keep.add(s)
            if term_to_remove:
                terms_to_keep.remove(term_to_remove)
        terms_to_keep_list = sorted(list(terms_to_keep), key = lambda t: len(t))
        string_rep_terms = " / ".join([el.replace("_", " ") for el in (terms_to_keep_list)])
        MAX_STRING_LENGTH = 30
        if len(string_rep_terms) > MAX_STRING_LENGTH:
            string_rep_terms = string_rep_terms[:MAX_STRING_LENGTH] + "..."
        current_y = current_y - y_jump
        term_to_pick_as_rep = term_to_pick_as_rep.replace("_", " ")
        ax3.text(current_x, current_y, string_rep_terms, verticalalignment='center', fontsize=2.9)
        
        # The bar showing the term weight
        score = term["score"]
        bar_adjust = 0 #y_jump/2.8
        bar_height_divider = 150
        #ax3.plot([current_x-0.01, current_x-0.01], [current_y + bar_adjust, current_y + bar_adjust + score/bar_height_divider], '-', linewidth=2.5, markersize=0, color = "silver")
        ax3.plot([current_x-0.008, current_x-0.008 - score/bar_height_divider], [current_y + bar_adjust, current_y + bar_adjust], '-', linewidth=2.0, markersize=0, color = "silver")
        

        
    current_x = current_x + x_jump
   


file_name_topics = "topics_terms"
plt.savefig(file_name_topics, dpi = 700, transparent=False, orientation = "landscape")
   #, bbox_inches='tight', , )
print("Saved plot in " + file_name_topics)
plt.close('all')
 
 ############################
 # Plot the topics over time
 ############################
nr_of_topics = len(obj["topic_model_output"]["topics"])
ax1 = plt.subplot(211)

plot_topics_text(topic_names, scatter_dict_science, "Science", "science", min_year, max_year, year_title_dict_science, ax1, xlabels=False, color_map = color_map, max_topic_confidence = max_topic_confidence)

ax2 = plt.subplot(212)
plot_topics_text(topic_names, scatter_dict_nature, "Nature", "nature", min_year, max_year, year_title_dict_nature, ax2, xlabels=True, color_map = color_map, max_topic_confidence = max_topic_confidence)



#ax3.text(0.5, 0.5, 'matplotlib', horizontalalignment='center', , transform=ax3.transAxes)
#plt.tight_layout()
#plt.gcf().subplots_adjust(wspace = 0.0, hspace = 0.12, left = 0.32, right = 1.00)
plt.gcf().subplots_adjust(hspace = 0.2, wspace = 0.2, left = 0.06, bottom = 0.1)

file_name = "name"
plt.savefig(file_name, dpi = 700, transparent=False, orientation = "landscape")
#, bbox_inches='tight', , )
print("Saved plot in " + file_name)
plt.close('all')
