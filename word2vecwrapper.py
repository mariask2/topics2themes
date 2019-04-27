"""
For accessing word2vec, cluster vectors and replace terms with synonym clusters
"""

import gensim
from sklearn import preprocessing
import numpy as np
import gc
from sklearn.cluster import DBSCAN
from sklearn.neighbors.nearest_centroid import NearestCentroid
from sklearn.metrics.pairwise import euclidean_distances
from topic_model_constants import *
#from domain_synonym_dictionary import MANUAL_MADE_DICT
#from domain_synonym_dictionary import NO_MATCH

########################
# To vectorize the data
#########################

class Word2vecWrapper:
    """
    Word2vecWrapper 
    A class for storing the information regarding the distributional semantics space
    """

    def __init__(self, model_path, semantic_vector_length, cluster_eps, no_match, manual_made_dict, binary, gensim_format):
        self.word2vec_model = None
        self.model_path = model_path
        self.semantic_vector_length = semantic_vector_length
        self._vocabulary_list = None
        self.no_match = no_match
        self.manual_made_dict = manual_made_dict
        self.binary = binary
        self.gensim_format = gensim_format
        self.cluster_eps = cluster_eps

        if semantic_vector_length is not None:
            self.default_vector = [0] * self.semantic_vector_length

        self.term_similar_dict = None
            
    def load(self):
        """
        load the semantic space in the memory
        """
        if self.word2vec_model == None:
            print("Loading word2vec model, this might take a while ....")

            if self.gensim_format:
                self.word2vec_model = gensim.models.KeyedVectors.load(self.model_path)
            else:
                self.word2vec_model = gensim.models.KeyedVectors.load_word2vec_format(self.model_path, binary=self.binary, unicode_errors='ignore')
            print("Loaded word2vec model")

    def get_semantic_vector_length(self):
        return self.semantic_vector_length

    def end(self):
        """
        remove the semantic space from the memory
        """
        self.word2vec_model = None
        gc.collect()


    def set_vocabulary(self, vocabulary_list):
        """
        Set the vocabulary that is to be included in the clustering
        """
        if self._vocabulary_list is None:
            self._vocabulary_list = []            
            for el in vocabulary_list:
                if len(el) == 3 and el[1] == "_":
                    self._vocabulary_list.append(el[0])
                else:
                    self._vocabulary_list.append(el)
            print("Vocabulary list length " + str(len(self._vocabulary_list)))

    def get_vector(self, word):
        if len(word) == 3 and word[1] == "_":
            word = word[0] # To cover for a bug in scikit learn, one char tokens have been transformed to longer. These are here transformed back
        try:
            self.load()
            raw_vec = self.word2vec_model[word]
            if len(raw_vec) != self.semantic_vector_length:
               raise Exception("The true semantic vector has length "\
                            + str(len(raw_vec)) \
                            +"while the configuration file states that is should have length "\
                            + str(self.semantic_vector_length))
            return raw_vec
        except KeyError:
            return self.default_vector
        
    def load_clustering(self, output_file):
        print("Clustering vectors, this might take a while ....")
        
        if self._vocabulary_list is None:
            raise Exception("set_vocabulary is not yet run")

        X_vectors = []
        cluster_words = []
        for word in self._vocabulary_list:
            vector = self.get_vector(word)
            if not all([el1 == el2 for el1, el2 in zip(vector, self.default_vector)]):
                norm_vector = preprocessing.normalize(np.reshape(vector, newshape = (1, self.semantic_vector_length)), norm='l2') # normalize the vector (l2 = eucledian)  
                list_vector = norm_vector[0]
                X_vectors.append(list_vector)
                cluster_words.append(word)

        # Compute DBSCAN
        X = np.matrix(X_vectors)
        self.cluster_dict = {}
        db = DBSCAN(self.cluster_eps, min_samples=1).fit(X)
        labels = db.labels_

        for label, term, vector in zip(labels, cluster_words, X_vectors):
            if term in self.no_match: # User defined to exclude from clustering
                continue
            if label != -1:                
                if label not in self.cluster_dict:
                    self.cluster_dict[label] = []
                self.cluster_dict[label].append(term)

        self.term_similar_dict = self.manual_made_dict
        for label, items in self.cluster_dict.items():
            if len(items) > 1:
                for term in items:
                    self.term_similar_dict[term] = SYNONYM_BINDER.join(items)

        f = open(output_file, "w")
        for item in list(set(self.term_similar_dict.values())):
            f.write(item + "\n")
        f.close()   
        self.nr_of_clusters = len(set(labels)) 
        print("Clustered vectors")
        

    def get_similars(self, word):
        if self.term_similar_dict == None:
            raise Exception("load_clustering is not yet run")
        try: # TODO: Check that all is initialised here
            similars = self.term_similar_dict[word]
            return similars
        except KeyError:
            return word
        
