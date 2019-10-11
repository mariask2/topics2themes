import json
import gensim
from sklearn import preprocessing
import numpy as np

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE



TEMP_FILE = "temp_term_dump.txt"
TEMP_ALL_TERMS_FILE = "temp_all_terms_dump.txt"
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
    
        all_f = open(TEMP_ALL_TERMS_FILE)
        all_j = all_f.read().strip()
        all_terms_in_corpus = json.loads(all_j)
        print("Nr of terms in documents " + str(all_terms_in_corpus))
        all_f.close()
        
        f = open(TEMP_FILE)
        j = f.read().strip()
        print("******")
        loaded_term_dict = json.loads(j)
        all_terms = []
        for key, item in loaded_term_dict.items():
            all_terms.extend([el["term"] for el in item])
        
        #print(loaded_term_dict)
        all_terms = sorted(list(set(all_terms))) # sort just for printing
        #all_terms = set(all_terms)
        print(all_terms)
        print("********")
        all_terms = set(all_terms)

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
        print(DX)
        main_fig = plt.figure()
        main_fig.set_size_inches(15, 7)

        for point, found_word in zip(DX, found_words):
            if found_word in all_terms:
                plt.scatter(point[0], point[1], color = "red", marker = "o", s=2)
                plt.annotate(found_word, (point[0], point[1]), xytext=(point[0], point[1]), color = "black", fontsize=9)

        save_figure_file_name = "temp_figure.png"
        plt.savefig(save_figure_file_name, dpi = 300, orientation = "landscape") #, bbox_inches='tight')
        print("Saved plot in " + save_figure_file_name)
    
        plt.close('all')


if __name__ == '__main__':
    tv = TermVisualiser()
    tv.produce_term_visualisation()
