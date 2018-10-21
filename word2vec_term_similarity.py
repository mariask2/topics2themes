"""
For accessing word2vec, cluster vectors and replace terms with synonym clusters
"""

import gensim
from sklearn import preprocessing
import numpy as np
import gc
from sklearn.metrics.pairwise import cosine_similarity
from nltk import edit_distance
from topic_model_constants import *
########################
# To vectorize the data
#########################

class Word2vecSimilarity:
    """
    Word2vecWrapper 
    A class for storing the information regarding the distributional semantics space
    """

    def __init__(self, model_path, similar_cut_off):
        self.word2vec_model = None
        self.model_path = model_path
        self.similar_cut_off = similar_cut_off

    
    def load(self):
        """
        load the semantic space in the memory
        """
        if self.word2vec_model == None:
            print("Loading word2vec model, this might take a while ....")
            self.word2vec_model = gensim.models.KeyedVectors.load_word2vec_format(self.model_path, binary=True)
            print("Loaded word2vec model")


    def end(self):
        """
        remove the semantic space from the memory
        """
        self.word2vec_model = None
        gc.collect()

    def potential_abbr(self, x, y):
        return x[0] == y[0] and ((len(x) < 5 and len(y) > 10) or (len(y) < 5 and len(x) > 10))
    
    def use_word2vec_for_determining_term_similarity(self, x, y):
        no_collocations_div = self.determine_word_to_vec_sim_edit_dist_filtering(x, y)
        return no_collocations_div

    def determine_word_to_vec_sim_edit_dist_filtering(self, x, y):
        edit_dist = edit_distance(x.lower(), y.lower())
        mean_length = (len(x) + len(y))/2
        # Only keep candidates with some string simliarity, or only one long and one short (to cover for abbreviations)
        if edit_dist > mean_length/2 and not self.potential_abbr(x,y):
            return False
        return self.determine_word_to_vec_sim(x, y)
     
    def determine_word_to_vec_sim(self, x, y):
        try:
            x_vec = np.reshape(self.get_vector(x.lower()), (1, -1))
            y_vec = np.reshape(self.get_vector(y.lower()), (1, -1))
            dist = cosine_similarity(x_vec, y_vec)[0][0]

            if abs(dist) > self.similar_cut_off:
                #print(dist)
                #print(x,y)
                #print("\n")
                return True
            else:
                return False
        except KeyError:
                return False

    def get_vector(self, word):
        self.load()
        raw_vec = self.word2vec_model[word]
        return raw_vec

if __name__ == '__main__':
    ws = Word2vecSimilarity("/Users/maria/mariaskeppstedtdsv/post-doc/gavagai/googlespace/GoogleNews-vectors-negative300.bin", 0.7)
    ws.use_word2vec_for_determining_term_similarity("maria", "anna")
    ws.use_word2vec_for_determining_term_similarity("child", "children")
    ws.use_word2vec_for_determining_term_similarity("book", "books")
    ws.use_word2vec_for_determining_term_similarity("good", "bad")
    ws.use_word2vec_for_determining_term_similarity("Maria", "Anna")
