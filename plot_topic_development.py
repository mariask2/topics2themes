

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


def plot_topics_text(topics_reps, texts_reps, topic_in_text_dict, title, file_name, min_year, max_year, year_title_tuple_list):
    #marker_style = dict(color='tab:blue', linestyle=None, marker='o',
    #                markersize=10, markerfacecoloralt='tab:red')

    fig, ax = plt.subplots()
    
    ax.set_xlim(min_year -1 , max_year + 1)
    ax.yaxis.set_ticks(range(0, len(topics_reps)))
    #ax.xaxis.set_ticks(range(0, len(texts_reps)))
    
    ax.yaxis.set_ticklabels(topics_reps)
    #ax.xaxis.set_ticklabels(texts_reps)
    
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    
    for y, topic_repr in enumerate(topics_reps):
        plt.axhline(y=y, linewidth=0.1, color='black')
    
    MOVE_X = 0.07
    last_iter_year = 0
    for year, t in year_title_tuple_list:
        if last_iter_year != year:
            x_moved = 0.0
        else:
            x_moved = x_moved + MOVE_X
       
        linewidth=0.02
        x = year + x_moved
        color='black'
        if x_moved == 0.0: # first line for year
            extra = 0.01
            linewidth = linewidth + extra*4
            x = x - extra
        plt.axvline(x=x, linewidth=linewidth, color=color)
        last_iter_year = year
            
    
    for year, texts_for_year in topic_in_text_dict.items():
        for y, topic_repr in enumerate(topics_reps):
            y_moved = 0.0
            x_moved = 0.0
            for topic_in_text in texts_for_year:
            
            #ax.text(-0.5, y, repr(topic_repr),
             #   horizontalalignment='center', verticalalignment='center')
                marker = markers.MarkerStyle(marker='|', fillstyle='none')
                #ax.scatter(year+ x_moved, y + y_moved, s = topic_in_text[y]*10, edgecolors = "face", c="grey", alpha = 0.7, linewidths = 0.05, marker='o')
                if topic_in_text[y] != 0:
                    ax.plot([year + x_moved, year + x_moved], [y + topic_in_text[y]/10, y - topic_in_text[y]/10], 'r+-', linewidth=0.4, markersize=topic_in_text[y]/5)
                #edgecolors="black"
                y_moved = y_moved - 0.07
                x_moved = x_moved + MOVE_X
    plt.xticks(fontsize=5, rotation=90)
    plt.yticks(fontsize=5)
    #for tick in ax.get_xticklabels():
    #    tick.set_rotation(90)
        
    plt.xticks(ha='center')
    ax.set_title(title)
    #fig.tight_layout()
    
    plt.gcf().subplots_adjust(bottom=0.2, wspace = 0.0, hspace = 0.0, left = 0.2, right = 1.0)
    
    plt.savefig(file_name, dpi = 700, transparent=True, figsize=(500, 20))
    #, bbox_inches='tight', orientation = "landscape", )
    print("Saved plot in " + file_name)
    plt.close('all')


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
        document_topics.append(topic_info)
        if len(topic_info["terms_found_in_text"]) > 1: # At least two terms included in text to include
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
    topic_name = ", ".join(repr_terms[0: third_length]).strip() + "\n" + ", ".join(repr_terms[third_length:2*third_length]).strip() + "\n" + ", ".join(repr_terms[2*third_length:]).strip()
    
    topics[el["id"]] = topic_name




scatter_dict = {}
year_title_tuple_list = []
x_labels = []
for el in editorial_data_list_science:
    id = el[0]
    topic_found = False
    year = int(el[1])
    if year not in scatter_dict:
        scatter_dict[year] = []
    title = el[2]
    year_title_tuple_list.append((year, title))
    #x_labels.append("(" + el[2] + ") " + str(year))
    x_labels.append(str(year))
    scatter_for_editorial = [0]*len(topics.keys())
    if id in document_info: # topic in document
        #print(document_info[el[0]])
        for topic_in_document in document_info[el[0]]["document_topics"]:
           index_for_topic_in_scatter = sorted(topics.keys()).index(topic_in_document["topic_index"])
           scatter_for_editorial[index_for_topic_in_scatter] = topic_in_document["topic_confidence"]
        pass
    else:
        #print(el[0], "missing")
        pass
    scatter_dict[year].append(scatter_for_editorial)


#print(x_labels)

#plot_topics_text(["tax, forrest, tree", "bush, obama, administration, word4, word5", "oceans, pollution", "media, science"], ["(Article nr 1) 1988", "(Article nr 1) 1989", "(Article nr 1) 1990"], [[2, 0, 5, 7], [0, 3, 4, 5], [2, 4, 0, 7]], "test2", "test2")

topic_names = [topics[key] for key in sorted(topics.keys())]
plot_topics_text(topic_names, x_labels, scatter_dict, "Science", "science", min_year, max_year, year_title_tuple_list)
