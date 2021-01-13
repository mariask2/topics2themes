

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


def plot_topics_text(topics_reps,  topic_in_text_dict, title, file_name, min_year, max_year, year_title_dict, ax, xlabels):


    #if not xlabels:
    #    ax.set(xticklabels=[])
    colors_map = ["blue", "orange", "green", "red", "purple", "blue", "deeppink", "olive", "darkturquoise"]
    
    
    ax.set_xlim(min_year -1 , max_year + 1)
    ax.yaxis.set_ticks(range(0, len(topics_reps)))
        
    ax.yaxis.set_ticklabels(["Topic " + str(el) for el in range(1, len(topics_reps) + 1)])
        
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    
    color = "black"
    for y, topic_repr in enumerate(topics_reps):
        plt.axhline(y=y, linewidth=0.2, color = color)
  
    #for ticklabel in plt.gca().get_yticklabels():
     #   ticklabel.set_color(color)
    
    MOVE_X = 0.02
    last_iter_year = 0
    color='black'
    for year in sorted(year_title_dict.keys()):
        title_list = year_title_dict[year]
        move_x = 1/len(title_list)
        for titles in title_list:
            if last_iter_year != year:
                x_moved = 0.0
            else:
                x_moved = x_moved + move_x
       
            linewidth=0.009
            x = year + x_moved
            if x_moved == 0.0: # first line for year
                extra = 0.01
                linewidth = linewidth + extra*4
                x = x - extra
            plt.axvline(x=x, linewidth=linewidth, color="black")
            last_iter_year = year
            
    
    for year, texts_for_year in topic_in_text_dict.items():
        for y, topic_repr in enumerate(topics_reps):
            move_x = 1/len(texts_for_year)
            x_moved = 0.0
            for topic_in_text in texts_for_year: # go through scatter-vector for each text for the year
                marker = markers.MarkerStyle(marker='|', fillstyle='none')
                if topic_in_text[y] != 0: #if the text contains the topic
                    #ax.plot([year + x_moved, year + x_moved], [y + topic_in_text[y]/10, y - topic_in_text[y]/10], '+-', linewidth=0.3, markersize=1, color = "red")
                    ax.plot([year + x_moved, year + x_moved], [y + topic_in_text[y]/10, y - topic_in_text[y]/10], '+-', linewidth=0.4, markersize=topic_in_text[y]/10, color = "red")
                x_moved = x_moved + move_x
            

                    
    plt.xticks(fontsize=6)#, rotation=90)
    plt.yticks(fontsize=4)

        
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
        if year not in scatter_dict:
            scatter_dict[year] = []
        if year not in year_title_dict:
            year_title_dict[year] = []
        title = el[2]
        year_title_dict[year].append(title)
        scatter_for_editorial = [0]*len(topics.keys())
        if id in document_info: # topic in document
            #print(document_info[el[0]])
            for topic_in_document in document_info[id]["document_topics"]:
               index_for_topic_in_scatter = sorted(topics.keys()).index(topic_in_document["topic_index"])
               scatter_for_editorial[index_for_topic_in_scatter] = topic_in_document["topic_confidence"]
               topic_found = True
        else:
            nr_documents_not_associated_with_topic_in_model = nr_documents_not_associated_with_topic_in_model + 1
            
        scatter_dict[year].append(scatter_for_editorial)
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

        if year > max_year:
            max_year = year
        if year < min_year:
            min_year = year
            
        if sp[1] == "Science":
            id = sp[5].replace("10.1126/science.", "").strip()
            id = id + ".ocr.txt"
            editorial_data = (id, sp[2], sp[3])
            editorial_data_list_science.append(editorial_data)
        else:
            id = sp[6].replace(".txt", "")
            id = id + ".ocr.txt"
            editorial_data = (id, sp[2], sp[3])
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
            if len(s) < len(term_to_pick_as_rep):
                term_to_pick_as_rep = s
        repr_terms.append(term_to_pick_as_rep.strip())
        
    third_length = int(len(repr_terms)/3)
    #topic_name = ", ".join(repr_terms[0: third_length]).strip() + "\n" + ", ".join(repr_terms[third_length:2*third_length]).strip() + "\n" + ", ".join(repr_terms[2*third_length:]).strip()
    topic_name = ", ".join(repr_terms)[0:50].strip() +"..."
    topics[el["id"]] = topic_name


topic_names = [topics[key] for key in sorted(topics.keys())]

scatter_dict_science, year_title_dict_science = create_scatter_dict_and_year_title_tuple(editorial_data_list_science, document_info)

scatter_dict_nature, year_title_dict_nature = create_scatter_dict_and_year_title_tuple(editorial_data_list_nature, document_info)


ax3 = plt.subplot(311)
plt.axis('off')
x_jump = 0.115
y_jump = 0.16
current_x = 0.02
ax3.set_xlim(0 , 1)

for index, el in enumerate(sorted(obj["topic_model_output"]["topics"], key=lambda t: t["id"])):
    current_y = 1
    ax3.text(current_x - 0.015, current_y, "Topic " + str(index + 1), verticalalignment='top', fontsize=6)
    current_y = current_y - 0.07
    for term in el['topic_terms']:
        #print(term["score"], term["term"])
        term_to_pick_as_rep = "123456789123456789123456789123456789123456789123456789"
        for s in term["term"].split("/"):
            if len(s) < len(term_to_pick_as_rep):
                term_to_pick_as_rep = s.strip()
        current_y = current_y - y_jump
        ax3.text(current_x, current_y, term_to_pick_as_rep, verticalalignment='top', fontsize=4.5)
        
        score = term["score"]
        ax3.plot([current_x-0.01, current_x-0.01], [current_y - y_jump/5 - score/30, current_y - y_jump/5 + score/30], '.-', linewidth=0.9, markersize=0, color = "red", marker=".")
        
    current_x = current_x + x_jump
    
ax1 = plt.subplot(312)

plot_topics_text(topic_names, scatter_dict_science, "Science", "science", min_year, max_year, year_title_dict_science, ax1, xlabels=False)

ax2 = plt.subplot(313)
plot_topics_text(topic_names, scatter_dict_nature, "Nature", "nature", min_year, max_year, year_title_dict_nature, ax2, xlabels=True)



#ax3.text(0.5, 0.5, 'matplotlib', horizontalalignment='center', , transform=ax3.transAxes)
#plt.tight_layout()
#plt.gcf().subplots_adjust(wspace = 0.0, hspace = 0.12, left = 0.32, right = 1.00)
plt.gcf().subplots_adjust(hspace = 0.40)

file_name = "name"
plt.savefig(file_name, dpi = 700, transparent=False, orientation = "landscape")
#, bbox_inches='tight', , )
print("Saved plot in " + file_name)
plt.close('all')
