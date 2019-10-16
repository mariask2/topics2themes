import json
import gensim
from sklearn import preprocessing
import numpy as np
import os
import math
import random

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE



TEMP_FILE = "temp_term_dump.txt"
TEMP_ALL_TERMS_FILE = "temp_all_terms_dump.txt"
SAVED_FOUND_WORDS_NAME = "temp_saved_words"
TSNE_NAME = "temp_tsne_name"
SPACE_FOR_PATH = "/Users/maria/mariaskeppstedtdsv/post-doc/gavagai/googlespace/GoogleNews-vectors-negative300.bin"

SMALLEST_FONT_SIZE = 3

class TermVisualiser:
    
    def __init__(self):
        self.termdict_dict = {}

    def set_vocabulary(self, terms_in_corpus):
        self.terms_in_corpus = terms_in_corpus
        j = json.dumps(self.terms_in_corpus)
        f = open(TEMP_ALL_TERMS_FILE, "w")
        f.write(j)
        f.close()
    
    def add_terms(self, term_dict, nr):
        self.termdict_dict[nr] = term_dict

    def dump_term_dict(self):
        j = json.dumps(self.termdict_dict)
        f = open(TEMP_FILE, "w")
        f.write(j)
        f.close()
    
    def produce_term_visualisation(self):
        
        from matplotlib.pyplot import plot, show, bar, grid, axis, savefig, clf
        import matplotlib.markers
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as mfm
        from mpl_toolkits import mplot3d
        import joblib
    
        all_f = open(TEMP_ALL_TERMS_FILE)
        all_j = all_f.read().strip()
        all_terms_in_corpus = json.loads(all_j)
        print("Nr of terms in documents " + str(all_terms_in_corpus))
        all_f.close()
        
        f = open(TEMP_FILE)
        j = f.read().strip()
        
        loaded_term_dict = json.loads(j)
        
        # To position terms that occur several times with a little distance
        terms_several_occurrences_dict = {}
        for key, item in loaded_term_dict.items():
            for i in item:
                if i["term"] not in terms_several_occurrences_dict:
                    terms_several_occurrences_dict[i["term"]] = [i["score"]]
                else:
                    terms_several_occurrences_dict[i["term"]].append(float(i["score"]))
                    terms_several_occurrences_dict[i["term"]].sort(reverse=True)
    

        if os.path.exists(TSNE_NAME) and os.path.exists(SAVED_FOUND_WORDS_NAME):
            print("Model already created")
            DX = joblib.load(TSNE_NAME)
            found_words = joblib.load(SAVED_FOUND_WORDS_NAME)
        
        else:
            all_vectors_list = []
            found_words = []
            word2vec_model = gensim.models.KeyedVectors.load_word2vec_format(SPACE_FOR_PATH, binary=True, unicode_errors='ignore')
            for word in all_terms_in_corpus:
                if word in word2vec_model:
                    vec_raw  = word2vec_model[word]
                    norm_vector = list(preprocessing.normalize(np.reshape(vec_raw, newshape = (1, 300)), norm='l2')[0])
                    all_vectors_list.append(norm_vector)
                    found_words.append(word)
                else:
                    print(word + " not found")

            all_vectors_np = np.array(all_vectors_list)
            pca_model = PCA(n_components=50)
            tsne_model = TSNE(n_components=2, random_state=0)
            DX_pca = pca_model.fit_transform(all_vectors_np)
            DX = tsne_model.fit_transform(DX_pca)

            joblib.dump(DX, TSNE_NAME, compress=9)
            joblib.dump(found_words, SAVED_FOUND_WORDS_NAME, compress=9)

        
        
        main_fig = plt.figure()
        main_fig.set_size_inches(15, 7)
        #ax = plt.axes(projection='3d')
        plt.axis('off')
        plt.tick_params(axis='both', left='off', top='off', right='off', bottom='off',\
                            labelleft='off', labeltop='off', labelright='off', labelbottom='off')
        
        word_vec_dict = {}
        min_x = 100
        min_y = 100
        max_x = -100
        max_y = -100
        for point, found_word in zip(DX, found_words):
            word_vec_dict[found_word] = point
            if point[0] < min_x:
                min_x = point[0]
            if point[0] > max_x:
                max_x = point[0]
            if point[1] < min_y:
                min_y = point[1]
            if point[1] > max_y:
                max_y = point[1]

        print(min_x, max_x, min_y, max_y)

        FONTSIZE_FACTOR = 7
        HOW_MUCH_TO_NORMALIZE_FOR_TERMS_HAVING_DIFFERENT_WEIGHT_IN_DIFFERENT_TOPICS = 0.6
        all_points_with_original_position_info = []
        total_nr_of_topics = len(loaded_term_dict.items()) + 1
        for nr, (topic, terms) in enumerate(loaded_term_dict.items()):
            print(topic)
            max_score = max([float(el["score"]) for el in terms])
            
            for nr, term in enumerate(terms[::-1]):
                point = self.get_point_for_term(term["term"], word_vec_dict, min_x, max_x, min_y, max_y)
                
                if point != None:
                    strength = min(0.6, (float(term["score"])/(max_score*HOW_MUCH_TO_NORMALIZE_FOR_TERMS_HAVING_DIFFERENT_WEIGHT_IN_DIFFERENT_TOPICS))*1.5)
                    extra = 0.01
                    fontsize=SMALLEST_FONT_SIZE + term["score"]/(max_score*HOW_MUCH_TO_NORMALIZE_FOR_TERMS_HAVING_DIFFERENT_WEIGHT_IN_DIFFERENT_TOPICS)*FONTSIZE_FACTOR
                   
                    plt.scatter(point[0], point[1], zorder = -100,  color = "red", marker = "o", s=0.001)

                    #ax.text(point[0], point[1], -1*(nr+1)/100,  '%s' % (term["term"]), size=20, zorder=1, color='k')
                    zorder = -1*nr
                    annotate_y = point[1]
                    annotate_x = point[0]
                    plt.annotate(term["term"], (point[0], point[1]), xytext=(annotate_x, annotate_y), zorder = zorder, color = (0, 0, 0, strength), fontsize=fontsize)
                
                
                    all_points_with_original_position_info.append((annotate_y, float(term["score"]), annotate_x, zorder, strength, fontsize, term["term"], nr, topic))
                else:
                    print(term["term"] + " not found")

        save_figure_file_name = "temp_figure.png"
        plt.savefig(save_figure_file_name, dpi = 700, orientation = "landscape", transparent=True) #, bbox_inches='tight')
        print("Saved plot in " + save_figure_file_name)
    
        plt.close('all')

        # Process to avoid to close

        all_points_with_original_position_info.sort(reverse=True)
        all_points_processed_position_info = []
        y_added_so_far = 0
        previous_x_list = []
        prevoius_x_room_list = []
        previous_y_list = []
        previous_term = ""
        for (annotate_y, score, annotate_x, zorder, strength, fontsize, term, nr, topic) in all_points_with_original_position_info:
            extrax = 0
            extray = 0
            
            x_room = 0.005*fontsize*len(term)
            VERTICAL_STRETCH = 1.5
            if len(terms_several_occurrences_dict[term]) > 1:
                for s in terms_several_occurrences_dict[term]:
                    if s == score:
                        break
                    else:
                        extrax = extrax + (fontsize)*len(term)*0.0005
                        extray = extray + (fontsize)**VERTICAL_STRETCH

            if extray == 0: # No double occurrence of the same term. Add to y both before and after the term.
                to_add = (fontsize)**VERTICAL_STRETCH
            else: # Double occurrence of the same term. Add more both before and after the term
                to_add = extray

            # If there is space above the term, do an anti-strech instead
            to_add_to_use = -to_add
            current_min =  annotate_x
            current_max =  annotate_x + x_room
            for previous_x, previous_x_room, previous_y in zip(previous_x_list, prevoius_x_room_list, previous_y_list):
                previous_min = previous_x
                previous_max = previous_x + previous_x_room
                y_diff = previous_y - annotate_y
                if not(current_min > previous_max or current_max < previous_min) and y_diff < fontsize*10: # if the previous is NOT far away horiontally, do an y-stretch
                    to_add_to_use = to_add
                    break
 
            y_added_so_far = y_added_so_far - to_add_to_use
            all_points_processed_position_info.append((annotate_y + y_added_so_far, score, annotate_x - extrax, zorder, strength, fontsize, term, nr, topic))

            previous_x_list.append(annotate_x)
            prevoius_x_room_list.append(x_room)
            previous_y_list.append(annotate_y)
            previous_term = term


        # Sort points with the new co-ordinates according to their topic
        topic_line_dict = {}
        for annotate_y, score, annotate_x, zorder, strength, fontsize, term, nr, topic in all_points_processed_position_info:
            if topic not in topic_line_dict:
                topic_line_dict[topic] = []
            topic_line_dict[topic].append((score, annotate_x, annotate_y, strength, term, fontsize, zorder))

        self.plot_topic_line_dict(topic_line_dict, file_name = "processed_figure_all.png")

        """
        for topic, line_points in topic_line_dict.items():
            file_name = "processed_figure_" + str(topic)
            self.plot_topic_line_dict(topic_line_dict, file_name, current_topic=topic)
            break
             """
    def plot_topic_line_dict(self, topic_line_dict, file_name, current_topic=None):
        from matplotlib.pyplot import plot, show, bar, grid, axis, savefig, clf
        import matplotlib.markers
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as mfm
        from mpl_toolkits import mplot3d
        import joblib
        
        main_fig_processed = plt.figure()
        main_fig_processed.set_size_inches(15, 7)
        plt.axis('off')
        plt.tick_params(axis='both', left='off', top='off', right='off', bottom='off',\
                        labelleft='off', labeltop='off', labelright='off', labelbottom='off')
        for (topic, line_points), topic_color in zip(topic_line_dict.items(), matplotlib.cm.rainbow(np.linspace(0, 1, len(topic_line_dict.items())))):
            print(topic_color)
            zorder = -10000
            line_points.sort(reverse = True)
            if current_topic == None or topic == current_topic: #only print lines when the general is generated and for the current topic
                for point_a, point_b in zip(line_points[:-1], line_points[1:]):
                    if topic == current_topic:
                        linecolor = (0.2, 0.2, 0.8, min(1, point_b[3]*1.5))
                    else:
                        linecolor = (0.2, 0.2, 0.2, max(0.3, point_b[3]*0.3))
                            #linecolor = (topic_color[0], topic_color[1], topic_color[2], point_b[3])
                    plt.plot([point_a[1], point_b[1]], [point_a[2], point_b[2]], zorder = zorder,  color= linecolor, linewidth=min(point_b[0], 0.5))
                    zorder = zorder - 1
        
            for (score, annotate_x, annotate_y, strength, term, fontsize, zorder) in line_points:
                if current_topic != None and topic !=current_topic: # draw the other terms in the back and with a weak colour
                    zorder = -100000
                    strength = 0.2
                
                if topic == current_topic:
                    strenth = 1.0
                    weight = 'bold'
                else:
                    weight = 'normal'
                plt.scatter(annotate_x, annotate_y, zorder = -100000,  color = (0.2, 0.2, 0.8, strength), marker = "o", s=0.1)
                plt.annotate(term, (annotate_x, annotate_y), xytext=(annotate_x, annotate_y), zorder = zorder, color=(topic_color[0], topic_color[1], topic_color[2], strength), fontsize=fontsize, weight=weight)
        plt.savefig(file_name, dpi = 700, orientation = "landscape", transparent=True) #, bbox_inches='tight')
        print("Saved plot in " + file_name)
        plt.close('all')

    def get_point_for_term(self, term, word_vec_dict, min_x, max_x, min_y, max_y):
        point = None
        if term in word_vec_dict:
            point = word_vec_dict[term]
        else:
            for w in term.split(" / "):
                if w in word_vec_dict:
                    point = word_vec_dict[w]
        if point == None:
            if self.has_number(term):
                point = (min_x + 10*random.random(), max_y - 10*random.random())
            else:
                point = (min_x + 10*random.random(), min_y + 10*random.random())
        return point

    def has_number(self, term):
        for el in range(0,9):
            if str(el) in term:
                return True
        return False

if __name__ == '__main__':
    tv = TermVisualiser()
    tv.produce_term_visualisation()



#https://www.w3schools.com/howto/howto_js_image_magnifier_glass.asp
