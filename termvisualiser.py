import json
import gensim
from sklearn import preprocessing
import numpy as np
import os
import math
import random
import sys

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE


TERM_FILE = "term_dump.txt"
ALL_TERMS_FILE = "all_terms_dump.txt"
OUTPUT_DIR = "visualisation_folder_created_by_system"
SAVED_FOUND_WORDS_NAME = "temp_saved_words"
TSNE_NAME = "temp_tsne_name"
#SPACE_FOR_PATH = "/Users/marsk757/wordspaces/69/model.bin"
SPACE_FOR_PATH = "/Users/marsk757/wordspaces/GoogleNews-vectors-negative300.bin"
SMALLEST_FONT_SIZE = 3
FIG_NAME = "terms_plot.png"
PREL_FIG_NAME = "prel_terms_plot.png"

class TermVisualiser:
    
    def __init__(self):
        self.termdict_dict = {}

    def set_vocabulary(self, terms_in_corpus, path_slash_format):
        self.terms_in_corpus = terms_in_corpus
        j = json.dumps(self.terms_in_corpus)
        file_name = os.path.join(self.get_working_dir(path_slash_format), ALL_TERMS_FILE)
        f = open(file_name, "w")
        f.write(j)
        f.close()
    
    def add_terms(self, term_dict, nr):
        self.termdict_dict[nr] = term_dict

    def get_working_dir(self, path_slash_format):
        dir = os.path.join(path_slash_format, OUTPUT_DIR)
        if not os.path.exists(dir):
            os.mkdir(dir)
        return dir
        
    def dump_term_dict(self, path_slash_format):
        j = json.dumps(self.termdict_dict)
        file_name = os.path.join(self.get_working_dir(path_slash_format), TERM_FILE)
        f = open(file_name, "w")
        f.write(j)
        f.close()
    
    def produce_term_visualisation(self, data_dir, terms_per_topic):
        
        from matplotlib.pyplot import plot, show, bar, grid, axis, savefig, clf
        import matplotlib.markers
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as mfm
        from mpl_toolkits import mplot3d
        import joblib
    
        file_name_all_terms = os.path.join(self.get_working_dir(data_dir), ALL_TERMS_FILE)
        all_f = open(file_name_all_terms)
        all_j = all_f.read().strip()
        all_terms_in_corpus = json.loads(all_j)
        print("Nr of terms in documents " + str(len(all_terms_in_corpus)))
        all_f.close()
        
        file_name = os.path.join(self.get_working_dir(data_dir), TERM_FILE)
        f = open(file_name)
        j = f.read().strip()
        
        loaded_term_dict = json.loads(j)
        
        # To position terms that occur several times with a little distance
        terms_several_occurrences_dict = {}
        for key, item in loaded_term_dict.items():
            print(key, item)
            item = item[:terms_per_topic]
            for i in item:
                if i["term"] not in terms_several_occurrences_dict:
                    terms_several_occurrences_dict[i["term"]] = [i["score"]]
                else:
                    terms_several_occurrences_dict[i["term"]].append(float(i["score"]))
                    terms_several_occurrences_dict[i["term"]].sort(reverse=True)
    
        # file paths
        final_file_name = os.path.join(self.get_working_dir(data_dir), FIG_NAME)
        prel_save_figure_file_name = os.path.join(self.get_working_dir(data_dir), PREL_FIG_NAME)
        tsne_path = os.path.join(self.get_working_dir(data_dir), TSNE_NAME)
        saved_found_words_name = os.path.join(self.get_working_dir(data_dir), SAVED_FOUND_WORDS_NAME)

        
        if os.path.exists(tsne_path) and os.path.exists(saved_found_words_name):
            print("Model already created")
            DX = joblib.load(tsne_path)
            found_words = joblib.load(saved_found_words_name)
        
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

            joblib.dump(DX, tsne_path, compress=9)
            joblib.dump(found_words, saved_found_words_name, compress=9)

        
        
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
            terms = terms[:terms_per_topic]
            max_score = max([float(el["score"]) for el in terms])
            
            for nr, term in enumerate(terms[::-1]):
                point = self.get_point_for_term(term["term"], word_vec_dict, min_x, max_x, min_y, max_y)
                
                if True:
                    strength = min(0.6, (float(term["score"])/(max_score*HOW_MUCH_TO_NORMALIZE_FOR_TERMS_HAVING_DIFFERENT_WEIGHT_IN_DIFFERENT_TOPICS))*1.5)
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

        
        plt.savefig(prel_save_figure_file_name, dpi = 700, orientation = "landscape", transparent=True) #, bbox_inches='tight')
        print("Saved plot in " + prel_save_figure_file_name)
    
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
            
            
            VERTICAL_STRETCH = 1.2
            x_room = fontsize*len(term)**1.2
            to_add = 0
            
            # Check double occurrence of the same term.
            if len(terms_several_occurrences_dict[term]) > 1:
                for s in terms_several_occurrences_dict[term]:
                    if s == score:
                        break
                    else:
                        extrax = extrax + (fontsize)*len(term)*0.0005
                        extray = extray + (fontsize)**VERTICAL_STRETCH
                to_add = extray
            if to_add == 0:
            #to_add = (fontsize)**VERTICAL_STRETCH
            
            
                # If there is space above the term, do an anti-strech instead
                to_add = -(fontsize)**VERTICAL_STRETCH
                current_min =  annotate_x
                current_max =  annotate_x + x_room
                for previous_x, previous_x_room, previous_y in zip(previous_x_list, prevoius_x_room_list, previous_y_list):
                    previous_min = previous_x
                    previous_max = previous_x + previous_x_room
                    y_diff = previous_y - annotate_y
                    if not(current_min > previous_max or current_max < previous_min) and y_diff < fontsize**VERTICAL_STRETCH: # if the previous is NOT far away horiontally, do an y-stretch
                        to_add = (fontsize)**VERTICAL_STRETCH
                        break
            
            y_added_so_far = y_added_so_far - to_add
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

        self.plot_topic_line_dict(topic_line_dict, file_name = final_file_name)

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
        #fig, axs = plt.subplots(len(topic_line_dict.items()))
        plt.tick_params(axis='both', left='off', top='off', right='off', bottom='off',\
                        labelleft='off', labeltop='off', labelright='off', labelbottom='off')
        
        for (topic, line_points), (nr, topic_color) in zip(topic_line_dict.items(), enumerate(matplotlib.cm.rainbow(np.linspace(0, 1, len(topic_line_dict.items()))))):
            SHADOWFACTOR = 0.0015
            MAX_LINEWIDTH = 0.3
            LINEWIDTH_FACTOR = 0.9
            print(topic_color)
            zorder = -10000
            line_points.sort(reverse = True)
           
            for point_a, point_b in zip(line_points[:-1], line_points[1:]):
                colored_linecolor = (topic_color[0], topic_color[1], topic_color[2], min(MAX_LINEWIDTH, point_b[3]*LINEWIDTH_FACTOR))
                gray_linecolor = (0.1, 0.1, 0.1, min(MAX_LINEWIDTH, point_b[3]*LINEWIDTH_FACTOR))
                plt.plot([point_a[1], point_b[1]], [point_a[2], point_b[2]], zorder = zorder,  color= colored_linecolor, linewidth=min(LINEWIDTH_FACTOR*point_a[0], MAX_LINEWIDTH))
                zorder = zorder - 1
                plt.plot([point_a[1] + SHADOWFACTOR, point_b[1] + SHADOWFACTOR], [point_a[2] + SHADOWFACTOR, point_b[2] + SHADOWFACTOR], zorder = zorder,  color=gray_linecolor , linewidth=min(point_b[0]*LINEWIDTH_FACTOR, MAX_LINEWIDTH))
                zorder = zorder - 1
        
        
            for (score, annotate_x, annotate_y, strength, term, fontsize, zorder) in line_points:
                colored_color = (topic_color[0], topic_color[1], topic_color[2], strength)
                gray_color = (0.1, 0.1, 0.1, strength)
                plt.scatter(annotate_x, annotate_y, zorder = -100000,  color = colored_color, marker = "o", s=strength)
                plt.scatter(annotate_x+SHADOWFACTOR, annotate_y+SHADOWFACTOR, zorder = -100001,  color = gray_color, marker = "o", s=strength)
                # Make a small black shadow for the texts
                # Make every other topic display in italics so that it is easier to distinguish the different topics
                if nr % 2 == 0:
                    term = "$\it{" + term  + "}$"
                plt.annotate(term, (annotate_x, annotate_y), xytext=(annotate_x, annotate_y), zorder = zorder-0.5, color=gray_color, fontsize=fontsize, weight="normal")
                plt.annotate(term, (annotate_x, annotate_y), xytext=(annotate_x+SHADOWFACTOR*fontsize, annotate_y+SHADOWFACTOR*fontsize), zorder = zorder, color = colored_color, fontsize=fontsize, weight="normal")

        plt.savefig(file_name, dpi = 700, orientation = "landscape", transparent=True) #, bbox_inches='tight')
        print("Saved plot in " + file_name)
        plt.close('all')

    def get_point_for_term(self, term, word_vec_dict, min_x, max_x, min_y, max_y):
        found_vector = False
        point = None
        if term in word_vec_dict:
            point = word_vec_dict[term]
            found_vector = True
        else:
            for w in term.split(" / "):
                if w in word_vec_dict:
                    point = word_vec_dict[w]
                    found_vector = True
        if not found_vector:
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
    tv.produce_term_visualisation(sys.argv[1], int(sys.argv[2]))



#https://www.w3schools.com/howto/howto_js_image_magnifier_glass.asp
