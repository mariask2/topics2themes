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
                    terms_several_occurrences_dict[i["term"]].append(i["score"])
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

        all_points_with_original_position_info = []
        total_nr_of_topics = len(loaded_term_dict.items()) + 1
        for nr, (topic, terms) in enumerate(loaded_term_dict.items()):
            #fig = main_fig.add_subplot(1, total_nr_of_topics, nr +1)
            print(topic)
            max_score = max([float(el["score"]) for el in terms])
            
            for nr, term in enumerate(terms[::-1]):
                point = self.get_point_for_term(term["term"], word_vec_dict, min_x, max_x, min_y, max_y)
                
                if point != None:
                    strength = min(0.6, (float(term["score"])/max_score)*1.5 + 0.1)
                    extra = 0.01
                    fontsize=SMALLEST_FONT_SIZE + term["score"]*6
                    
                    # The position in the list, shows how much to move the term (the lower score, the further from original point is it to be positioned).
                    extrax = 0
                    extray = 0
                    for s in terms_several_occurrences_dict[term["term"]]:
                        if s == term["score"]:
                            break
                        else:
                            extrax = extrax + (10 + s*7)*0.04 #
                            extray = extray + (13 + s*7)*0.04 #


                    plt.scatter(point[0], point[1], zorder = -100,  color = "red", marker = "o", s=0.001)

                    #ax.text(point[0], point[1], -1*(nr+1)/100,  '%s' % (term["term"]), size=20, zorder=1, color='k')
                    zorder = -1*nr
                    annotate_y = point[1]+extray
                    annotate_x = point[0] - extrax
                    plt.annotate(term["term"], (point[0], point[1]), xytext=(annotate_x, annotate_y), zorder = zorder, color = (0, 0, 0, strength), fontsize=fontsize)
                
                
                    all_points_with_original_position_info.append((annotate_y, annotate_x, zorder, strength, fontsize, term["term"], nr, topic))
                else:
                    print(term["term"] + " not found")
        """
        for point, found_word in zip(DX, found_words):
            if found_word in all_terms:
                plt.scatter(point[0], point[1], color = "red", marker = "o", s=2)
                plt.annotate(found_word, (point[0], point[1]), xytext=(point[0], point[1]), color = "black", fontsize=9)
           """
        save_figure_file_name = "temp_figure.png"
        plt.savefig(save_figure_file_name, dpi = 700, orientation = "landscape", transparent=True) #, bbox_inches='tight')
        print("Saved plot in " + save_figure_file_name)
    
        plt.close('all')

        # Process to avoid to close

        all_points_with_original_position_info.sort(reverse=True)
        all_points_processed_position_info = []
        y_added_so_far = 0
        for (annotate_y, annotate_x, zorder, strength, fontsize, term, nr, topic) in all_points_with_original_position_info:
            to_add = (fontsize - SMALLEST_FONT_SIZE)**1.5
            y_added_so_far = y_added_so_far - to_add
            all_points_processed_position_info.append((annotate_y + y_added_so_far, annotate_x, zorder, strength, fontsize, term, nr, topic))
            y_added_so_far = y_added_so_far - to_add/2
            print(y_added_so_far)


        main_fig_processed = plt.figure()
        main_fig_processed.set_size_inches(15, 7)
        plt.axis('off')
        plt.tick_params(axis='both', left='off', top='off', right='off', bottom='off',\
                        labelleft='off', labeltop='off', labelright='off', labelbottom='off')

        for point_info in all_points_processed_position_info:
            plt.scatter(point_info[1], point_info[0], zorder = -100,  color = "red", marker = "o", s=0.001)
            plt.annotate(point_info[5], (point_info[1], point_info[0]), xytext=(point_info[1], point_info[0]), zorder = point_info[2], color = (0, 0, 0, point_info[3]), fontsize=point_info[4])
            
        save_figure_file_name_processed = "processed_figure.png"
        plt.savefig(save_figure_file_name_processed, dpi = 700, orientation = "landscape", transparent=True) #, bbox_inches='tight')
        print("Saved plot in " + save_figure_file_name_processed)
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
