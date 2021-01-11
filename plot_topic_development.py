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


plot_topics_text(["tax, forrest, tree", "bush, obama, administration, word4, word5", "oceans, pollution", "media, science"], ["(Article nr 1) 1988", "(Article nr 1) 1989", "(Article nr 1) 1990"], [[2, 0, 5, 7], [0, 3, 4, 5], [2, 4, 0, 7]], "test2", "test2")

