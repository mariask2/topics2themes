

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

 
def plot_topics_text(topics_reps,  topic_in_text_dict, title, file_name, min_year, max_year, year_title_dict, ax, xlabels, color_map):


    #if not xlabels:
    #    ax.set(xticklabels=[])
    colors_map = ["blue", "orange", "green", "red", "purple", "blue", "deeppink", "olive", "darkturquoise"]
    
    classification_display_size = 0.6
    classes = ["Eco", "Dev", "Sec","Eth", "Tec", "Gov", "Sci", "Com"]
    ax.set_ylim(len(topics_reps) + classification_display_size*len(classes) -0.1, -0.5)
    ax.set_xlim(min_year -1 , max_year + 1)
    ax.yaxis.set_ticks(range(0, len(topics_reps) + 1))
    #ax.tick_params(axis='x', colors='silver')
    #ax.tick_params(axis='y', colors='silver')
    #ax.yaxis.label.set_color('black')
    #ax.xaxis.label.set_color('black')
    
    y_ticks = ["(" + el.split(",")[0][:7] + "..." for el in topics_reps] + [""]
    ax.yaxis.set_ticklabels(y_ticks)
    ax.yaxis.tick_right()
    ax.yaxis.set_ticks_position('none')
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.tick_params(axis="x", top=True, which="both")
    plt.xticks(fontsize=6)#, rotation=90)
    plt.yticks(fontsize=5.5)
    
    #y_width = 1/len(topics_reps)/2
    # The tick labels to the left are added manually
    y_width = 0.4
    for y, topic_repr in enumerate(topics_reps):
        line_color = [color_map[y][0], color_map[y][1], color_map[y][2], 0.20]
        text_color = [color_map[y][0], color_map[y][1], color_map[y][2], 1.0]
        plt.axhline(y=y, linewidth=0.55, color = line_color)
        ax.text(min_year-4.1,y+0.3, "Topic " + str(y + 1), size=5.0, color = "black")
        ax.text(min_year-4.1,y+0.3, "Topic ", size=5.0, color = text_color)
        ax.fill([min_year - 1, max_year + 1, max_year + 1, min_year - 1, min_year - 1], [y - y_width, y - y_width, y + y_width, y + y_width, y - y_width], color = color_map[y], edgecolor = color_map[y])

    margin_to_topics = 0

    for c_nr, class_name in enumerate(classes):
        y = len(topics_reps) + margin_to_topics + c_nr*classification_display_size
        
        print(class_name, y)
        y_width_class = classification_display_size/3
        class_color = "whitesmoke"
        text_color = "gray"
        text_x_diff = 4.0
        text = class_name
        if c_nr % 2 == 0:
            class_color = "gainsboro"
            text_color = "black"
            text_x_diff = 2.5
            text = class_name
        ax.text(min_year-text_x_diff,y + classification_display_size/3, text, size=4.0, color = text_color)
        #ax.text(min_year-text_x_diff + 0.01,y + classification_display_size/2 + 0.01, text, size=3.9, color = text_color)
        plt.axhline(y=y, linewidth=0.05, linestyle = ":", color = "black")
        ax.fill([min_year - 1, max_year + 1, max_year + 1, min_year - 1, min_year - 1], [y - y_width_class, y - y_width_class, y + y_width_class, y + y_width_class, y - y_width_class], color = class_color, edgecolor = class_color)
        
    MOVE_X = 0.02
    last_iter_year = 0
    
    for year in sorted(year_title_dict.keys()):
        title_list = year_title_dict[year]
        move_x = 1/len(title_list)
        for titles in title_list:
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
            plt.axvline(x=x, linewidth=linewidth, color="black")
            # Line indicating an article
            #ax.plot([x, x], [-0.5, len(topics_reps)-0.5], '.-', linewidth=linewidth, markersize=0, color = "black")
            # Indication of the classification
            #ax.plot([x, x], [len(topics_reps), len(topics_reps) + classification_display_size*len(classes)], '.-', linewidth=linewidth, markersize=0, color = "red")
            last_iter_year = year
            
    # Different names in paper and in data, but same classes
    label_list = ["A_dominant_frame", "B_dominant_frame", "C_dominant_frame", "D_dominant_frame", "E_dominant_frame", "F_dominant_frame", "G_dominant_frame", "H_dominant_frame"]
    printed = []
    for year, texts_for_year in topic_in_text_dict.items():
        for y, topic_repr in enumerate(topics_reps):
            move_x = 1/len(texts_for_year)
            x_moved = 0.0
            for (topic_in_text, label) in texts_for_year: # go through scatter-vector for each text for the year
                marker = markers.MarkerStyle(marker='|', fillstyle='none')
                if topic_in_text[y] != 0: #if the text contains the topic
                    ax.plot([year + x_moved, year + x_moved], [y + topic_in_text[y]/10, y - topic_in_text[y]/10], '.-', linewidth=0.8, markersize=0, color = "black")
               
                # plot the class (= manual label) for the text
                label_nr = label_list.index(label)
                label_start = len(topics_reps) + label_nr * classification_display_size - margin_to_topics
                if (label_nr, label_start) not in printed:
                    printed.append((label_nr, label_start))
                ax.plot([year + x_moved, year + x_moved], [label_start, label_start], '*-', linewidth=0.04, markersize=0.05, color = "black")
                
                # Move the next text for the year a bit to the right
                x_moved = x_moved + move_x
    for el in sorted(printed):
        print(el)

        
    plt.xticks(ha='center')
    ax.set_title(title, fontsize=6, loc="right") # x=-0.41,y=0.92)# )rotation='vertical'
    #fig.tight_layout()
    


def create_scatter_dict_and_year_title_tuple(editorial_data_list, document_info):
    scatter_dict = {}
    year_title_dict = {}
    nr_documents_to_scatter_dict = 0
    nr_documents_to_scatter_dict_with_topics_found = 0
    nr_documents_not_associated_with_topic_in_model = 0
    for el in editorial_data_list:
        id = el[0]
        topic_found = False
        year = int(el[1])
        label = el[3]
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
               scatter_for_editorial[index_for_topic_in_scatter] = topic_in_document["topic_confidence"]
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
    
    return scatter_dict, year_title_dict
    

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
model_file =  "/Users/marsk757/topic2themes/topics2themes/data_folder/climate-editorials-graph/topics2themes_exports_folder_created_by_system/5ff8fd96dede69ec1ede953a_model.json"
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

scatter_dict_science, year_title_dict_science = create_scatter_dict_and_year_title_tuple(editorial_data_list_science, document_info)

scatter_dict_nature, year_title_dict_nature = create_scatter_dict_and_year_title_tuple(editorial_data_list_nature, document_info)

color_map_orig = cm.get_cmap('tab20b', len(topic_names)).colors
color_map = []
for c in color_map_orig:
    color_map.append([c[0], c[1], c[2], 0.15])

ax3 = plt.subplot(311)
plt.axis('off')
x_jump = 0.110
y_jump = 0.115
current_x = 0.03

ax3.set_xlim(0 , 1)
ax3.set_ylim(0, 1)

for index, el in enumerate(sorted(obj["topic_model_output"]["topics"], key=lambda t: t["id"])):
    current_y = 0.96
    heading_x = current_x - 0.015
    background_x_start = heading_x - 0.005
    background_x_end = background_x_start + x_jump - 0.005
    background_y_start = current_y + 0.04
    background_y_end = background_y_start - y_jump*(len(el['topic_terms'])+1) - 0.18
    ax3.fill([background_x_start, background_x_end, background_x_end, background_x_start, background_x_start], [background_y_start, background_y_start, background_y_end, background_y_end, background_y_start], color = color_map[index])
    ax3.text(heading_x, current_y, "Topic " + str(index + 1), verticalalignment='top', fontsize=6)
    current_y = current_y - 0.05
    for term in el['topic_terms']:
        #print(term["score"], term["term"])
        term_to_pick_as_rep = "123456789123456789123456789123456789123456789123456789"
        for s in term["term"].split("/"):
            if len(s.strip()) < len(term_to_pick_as_rep):
                term_to_pick_as_rep = s.strip()
        current_y = current_y - y_jump
        ax3.text(current_x, current_y, term_to_pick_as_rep, verticalalignment='top', fontsize=4)
        
        score = term["score"]
        bar_adjust = 0.025
        
        ax3.plot([current_x-0.01, current_x-0.01], [current_y - bar_adjust - score/40, current_y - bar_adjust + score/40], '-', linewidth=2.5, markersize=0, color = "silver")
        
    current_x = current_x + x_jump
    
nr_of_topics = len(obj["topic_model_output"]["topics"])
ax3.set_title("Most typical terms", fontsize=6, loc="right")
   
 
ax1 = plt.subplot(312)

plot_topics_text(topic_names, scatter_dict_science, "Science", "science", min_year, max_year, year_title_dict_science, ax1, xlabels=False, color_map = color_map)

ax2 = plt.subplot(313)
plot_topics_text(topic_names, scatter_dict_nature, "Nature", "nature", min_year, max_year, year_title_dict_nature, ax2, xlabels=True, color_map = color_map)



#ax3.text(0.5, 0.5, 'matplotlib', horizontalalignment='center', , transform=ax3.transAxes)
#plt.tight_layout()
#plt.gcf().subplots_adjust(wspace = 0.0, hspace = 0.12, left = 0.32, right = 1.00)
plt.gcf().subplots_adjust(hspace = 0.40)

file_name = "name"
plt.savefig(file_name, dpi = 700, transparent=False, orientation = "landscape")
#, bbox_inches='tight', , )
print("Saved plot in " + file_name)
plt.close('all')
