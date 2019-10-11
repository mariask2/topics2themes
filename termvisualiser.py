import json
import gensim
from sklearn import preprocessing
import numpy as np
import os
import joblib
import math

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE



TEMP_FILE = "temp_term_dump.txt"
TEMP_ALL_TERMS_FILE = "temp_all_terms_dump.txt"
SAVED_FOUND_WORDS_NAME = "temp_saved_words"
TSNE_NAME = "temp_tsne_name"
SPACE_FOR_PATH = "/Users/maria/mariaskeppstedtdsv/post-doc/gavagai/googlespace/GoogleNews-vectors-negative300.bin"


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
    
        all_f = open(TEMP_ALL_TERMS_FILE)
        all_j = all_f.read().strip()
        all_terms_in_corpus = json.loads(all_j)
        print("Nr of terms in documents " + str(all_terms_in_corpus))
        all_f.close()
        
        f = open(TEMP_FILE)
        j = f.read().strip()
        print("******")
        loaded_term_dict = json.loads(j)
        print(loaded_term_dict)
        all_terms = []
        for key, item in loaded_term_dict.items():
            all_terms.extend([el["term"] for el in item])
        
        #print(loaded_term_dict)
        all_terms = sorted(list(set(all_terms))) # sort just for printing
        #all_terms = set(all_terms)
        #print(all_terms)
        print("********")
        all_terms = set(all_terms)

        if os.path.exists(TSNE_NAME) and os.path.exists(SAVED_FOUND_WORDS_NAME):
            print("Model already created")
            DX = joblib.load(TSNE_NAME)
            found_words = joblib.load(SAVED_FOUND_WORDS_NAME)
        
        else:
            all_vectors_list = []
            found_words = []
            word2vec_model = gensim.models.KeyedVectors.load_word2vec_format(SPACE_FOR_PATH, binary=True, unicode_errors='ignore')
            for word in all_terms_in_corpus:
                try:
                    vec_raw  = word2vec_model[word]
                    norm_vector = list(preprocessing.normalize(np.reshape(vec_raw, newshape = (1, 300)), norm='l2')[0])
                    all_vectors_list.append(norm_vector)
                    found_words.append(word)
                except KeyError:
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

        word_vec_dict = {}
        for point, found_word in zip(DX, found_words):
            word_vec_dict[found_word] = point

        nr_of_occurrences_for_term = {}
        total_nr_of_topics = len(loaded_term_dict.items()) + 1
        for nr, (topic, terms) in enumerate(loaded_term_dict.items()):
            #fig = main_fig.add_subplot(1, total_nr_of_topics, nr +1)
            print(topic)
            max_score = max([float(el["score"]) for el in terms])
            print(max_score)
            for nr, term in enumerate(terms[::-1]):
                print(term)
                if term["term"] in word_vec_dict:
                    strength = min(1, (float(term["score"])/max_score)*1.5 + 0.2)
                    point = word_vec_dict[term["term"]]
                    extra = 0.1
                    if term["term"] in nr_of_occurrences_for_term:
                        extra = extra + nr_of_occurrences_for_term[term["term"]] * 1
                    plt.scatter(point[0], point[1], zorder = -100,  color = "red", marker = "o", s=0.1)
                    #print(point[0], point[1], -1*(nr+1)/100)
                    #ax.text(point[0], point[1], -1*(nr+1)/100,  '%s' % (term["term"]), size=20, zorder=1, color='k')
                    plt.annotate(term["term"], (point[0], point[1]), xytext=(point[0]+extra, point[1]+extra), zorder = -1*nr, color = (0, 0, 0, strength), fontsize=10 + term["score"]*7)
                
                    if term["term"] not in nr_of_occurrences_for_term:
                        nr_of_occurrences_for_term[term["term"]]  =  1
                    else:
                        nr_of_occurrences_for_term[term["term"]]  =  nr_of_occurrences_for_term[term["term"]] + 1
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


if __name__ == '__main__':
    tv = TermVisualiser()
    tv.produce_term_visualisation()
