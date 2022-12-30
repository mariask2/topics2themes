"""
For accessing word2vec, cluster vectors and replace terms with synonym clusters
"""

import gensim
import os
from sklearn import preprocessing
import numpy as np
import gc
from sklearn.cluster import DBSCAN
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import euclidean_distances


# An import that should function both locally and when running an a remote server
try:
    from environment_configuration import *
except:
    from topics2themes.environment_configuration import *

if RUN_LOCALLY:
    from topic_model_constants import *
else:
    from topics2themes.topic_model_constants import *

########################
# To vectorize the data
#########################

class Word2vecWrapper:
    """
    Word2vecWrapper 
    A class for storing the information regarding the distributional semantics space
    """

    def __init__(self, model_path, semantic_vector_length, cluster_eps, no_match, manual_made_dict_file, binary, gensim_format, path_slash_format, clustering_type):

        self.manual_made_dict_file = manual_made_dict_file
        self.path_slash_format = path_slash_format
        self.word2vec_model = None
        self.model_path = model_path
        self.semantic_vector_length = semantic_vector_length
        self._vocabulary_list = None
        self.no_match = no_match
        self.manual_made_dict = None
        self.binary = binary
        self.gensim_format = gensim_format
        self.cluster_eps = cluster_eps
        self.clustering_type = clustering_type

        if semantic_vector_length is not None:
            self.default_vector = [0] * self.semantic_vector_length

        self.term_similar_dict = None
        
    def load_manual_dict(self, vocabulary):
        vocabulary_set = set([el.lower() for el in vocabulary])
        manual_made_cluster_dict = {}
        if self.manual_made_dict_file != None:
            if not os.path.isfile(os.path.join(self.path_slash_format, self.manual_made_dict_file)):
                raise FileNotFoundError("The file for specifying manually constructed words doesn't exist. Filename given in configuration is: " + \
                                         self.manual_made_dict_file)
            with open(os.path.join(self.path_slash_format, self.manual_made_dict_file)) as manual_cluster_file:
                for line in manual_cluster_file:
                    cluster_words = line.strip().split(" ") #TODO: Sort first
                    for word in cluster_words:
                        if word in vocabulary_set:
                            manual_made_cluster_dict[word] = SYNONYM_BINDER.join(cluster_words)
                        
        return manual_made_cluster_dict
        
    def load(self):
        """
        load the semantic space in the memory
        """
        if self.word2vec_model == None:
            print("Loading word2vec model, this might take a while ....")

            if self.gensim_format:
                self.word2vec_model = gensim.models.KeyedVectors.load(self.model_path)
            else:
                self.word2vec_model = gensim.models.KeyedVectors.load_word2vec_format(self.model_path, binary=self.binary, unicode_errors='strict')
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
            print("Vocabulary size included in clustering " + str(len(self._vocabulary_list)))

    def check_vector_length(self, raw_vec):
        if len(raw_vec) != self.semantic_vector_length:
            raise Exception("The true semantic vector has length "\
                            + str(len(raw_vec)) \
                            +"while the configuration file states that is should have length "\
                            + str(self.semantic_vector_length))


    # Very simple compound spitting, not really language independent, but also not very weell adapted to any language
    def get_compound_vector(self, word):
        return_vector = None
        for i in range(4, len(word) - 3):
            first = word[:i].lower()
            second = word[i:].lower()
            if first in self.word2vec_model and second in self.word2vec_model:
                first_v = self.word2vec_model[first]
                second_v = self.word2vec_model[second]
                return_vector = np.add(first_v, second_v)
                return return_vector
                
        for j in range(len(word)-1, 6, -1):
            first_alone = word[:j].lower()
            if first_alone in self.word2vec_model:
                return_vector = self.word2vec_model[first_alone]
                return return_vector
            second_alone = word[-j:].lower()
            if second_alone in self.word2vec_model:
                return_vector = self.word2vec_model[second_alone]
                return return_vector
        return return_vector
                
    def get_vector(self, word):
        if len(word) == 3 and word[1] == "_":
            word = word[0] # To cover for a bug in scikit learn, one char tokens have been transformed to longer. These are here transformed back
        
        self.load()
        if word in self.word2vec_model:
            raw_vec = self.word2vec_model[word]
            self.check_vector_length(raw_vec)
            return raw_vec
        elif word.lower() in self.word2vec_model:
            raw_vec = self.word2vec_model[word.lower()]
            self.check_vector_length(raw_vec)
            return raw_vec
        else:
            return self.get_compound_vector(word)
  

    def load_clustering(self, output_file, transformation, not_found_words_file_name, stopwords_for_word2vec):
        not_found_words_file = open(not_found_words_file_name, "w")
        nr_of_not_found = 0
        print("Clustering vectors, this might take a while ....")
        
        frequencies = transformation.toarray().sum(axis=0)
        
        if self._vocabulary_list is None:
            raise Exception("set_vocabulary is not yet run")

        word_freq_dict = {}
        for word, count in zip(self._vocabulary_list, frequencies):
            word_freq_dict[word] = count
        
        self.manual_made_dict = self.load_manual_dict(self._vocabulary_list)
        
        X_vectors = []
        cluster_words = []
        
        has_lower_set = set([])
        for word in self._vocabulary_list:
            if word.lower() == word:
                has_lower_set.add(word)
                
        for word in self._vocabulary_list:
            if word.lower() in stopwords_for_word2vec or word.lower() in self.manual_made_dict.keys():
                continue
            if word.lower() != word and word.lower() in has_lower_set: # if there is a non-cap version of the word use that one
                continue
            vector = self.get_vector(word)
            if type(vector) == np.ndarray:
                norm_vector = preprocessing.normalize(np.reshape(vector, newshape = (1, self.semantic_vector_length)), norm='l2') # normalize the vector (l2 = eucledian)  
                list_vector = norm_vector[0]
                X_vectors.append(list_vector)
                cluster_words.append(word.lower())
            else: #not in model
                # default vector
                nr_of_not_found = nr_of_not_found + 1
                if word not in set(self.manual_made_dict.keys()) and word.lower() not in set(self.manual_made_dict.keys()):
                    not_found_words_file.write(word.lower() + "\n")
                
        print("Number of words not found in vector space used: " + str(nr_of_not_found))
        not_found_words_file.close()
        
        
        # Compute DBSCAN
        X = np.matrix(X_vectors)
        self.cluster_dict = {}
        if self.clustering_type == "agglomerative":
            cluster_output = clustering = AgglomerativeClustering(linkage="ward",
                                distance_threshold = self.cluster_eps,
                                n_clusters=None).fit(X)
        else:
            cluster_output = DBSCAN(self.cluster_eps, min_samples=1).fit(X)
        labels = cluster_output.labels_

        for label, term, vector in zip(labels, cluster_words, X_vectors):
            term = term.lower()
            if term in self.no_match or term in self.manual_made_dict.keys(): # User defined to exclude from clustering or in a user-defined dict
                continue
            if label != -1:                
                if label not in self.cluster_dict:
                    self.cluster_dict[label] = []
                if term not in self.cluster_dict[label]: # to make sure the same is not added twice (when there are both upper and lower case)
                    self.cluster_dict[label].append(term)

        self.term_similar_dict = self.manual_made_dict
        for label, items in self.cluster_dict.items():
            if len(items) > 1: # only include clusters with at least 2 items
                for term in items:
                    self.term_similar_dict[term] = SYNONYM_BINDER.join(items)

        f = open(output_file, "w")
        for item in sorted(list(set(self.term_similar_dict.values()))):
            f.write(item.replace(SYNONYM_BINDER, " ") + "\n")
        f.close()   
        self.nr_of_clusters = len(set(labels)) 
        print("Clustered vectors")
        

    def get_similars(self, word):
        if self.term_similar_dict == None:
            raise Exception("load_clustering is not yet run")
        if word in self.manual_made_dict:
            return self.manual_made_dict[word]
        elif word in self.term_similar_dict:
            return self.term_similar_dict[word]
        else:
            return word
        
