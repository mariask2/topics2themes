

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

def plot_topics_text(topics_reps, texts_reps, topic_in_text_matrix, title, file_name):
    #marker_style = dict(color='tab:blue', linestyle=None, marker='o',
    #                markersize=10, markerfacecoloralt='tab:red')

    fig, ax = plt.subplots()
    ax.yaxis.set_ticks(range(0, len(topics_reps)))
    ax.xaxis.set_ticks(range(0, len(texts_reps)))
    
    ax.yaxis.set_ticklabels(topics_reps)
    ax.xaxis.set_ticklabels(texts_reps)
    
    for x, topic_in_text in enumerate(topic_in_text_matrix):
        for y, topic_repr in enumerate(topics_reps):
            #ax.text(-0.5, y, repr(topic_repr),
             #   horizontalalignment='center', verticalalignment='center')
                
            ax.scatter(x, y, s = topic_in_text[y]*10)
          

    for tick in ax.get_xticklabels():
        tick.set_rotation(90)
    plt.xticks(ha='center')
    ax.set_title(title)
    fig.tight_layout()
    
    plt.savefig(file_name, dpi = 700, orientation = "landscape", transparent=True) #, bbox_inches='tight')
    print("Saved plot in " + file_name)
    plt.close('all')


editorial_data_list = []
with open("../klimat/master_table.tsv") as master:
    for line in master:
        sp = line.split("\t")
        try:
            int(sp[2]) # First row with titles
        except ValueError:
            continue
        id = ""

        if sp[1] == "Science":
            id = sp[5].replace("10.1126/science.", "").strip()
        else:
            id = sp[6].replace(".txt", "")

        id = id + ".ocr.txt"
        editorial_data = (id, sp[2], sp[3])
        editorial_data_list.append(editorial_data)


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




topics = []
for el in obj["topic_model_output"]["topics"]:
    terms = [t['term'] for t in el['topic_terms']]
    repr_terms = []
    for t in terms:
        term_to_pick_as_rep = "123456789123456789123456789123456789123456789123456789"
        for s in t.split("/"):
            if "_" in s:
                term_to_pick_as_rep = s
        if term_to_pick_as_rep == "123456789123456789123456789123456789123456789123456789":
            for s in t.split("/"):
                if len(s) < len(term_to_pick_as_rep):
                    term_to_pick_as_rep = s
        repr_terms.append(term_to_pick_as_rep.strip())
        
    topics.append(", ".join(repr_terms).strip())
  
    

scatter_matrix = []
x_labels = []
for el in editorial_data_list:
    x_labels.append("(" + el[2] + ") " + el[1])
    print(el)
    scatter_for_editorial = [0]*len(topics)
    if el[0] in document_info:
        print(document_info[el[0]])
        pass
    else:
        #print(el[0], "missing")
        pass
    scatter_matrix.append(scatter_for_editorial)

print(scatter_matrix)
print(x_labels)

#plot_topics_text(["tax, forrest, tree", "bush, obama, administration, word4, word5", "oceans, pollution", "media, science"], ["(Article nr 1) 1988", "(Article nr 1) 1989", "(Article nr 1) 1990"], [[2, 0, 5, 7], [0, 3, 4, 5], [2, 4, 0, 7]], "test2", "test2")

plot_topics_text(topics, x_labels, scatter_matrix, "test3", "test3")
