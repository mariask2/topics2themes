"""
For performing topic modelling. The main file of the package
"""

from pprint import pprint
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from nltk.tokenize import sent_tokenize
from html.parser import HTMLParser
from pathlib import Path

import os
import numpy as np
import json
from collections import Counter
from glob import glob
import datetime
import argparse
import datetime
import time
import math



# An import that should function both locally and when running an a remote server
try:
    from environment_configuration import *
except:
    from topics2themes.environment_configuration import *

if RUN_LOCALLY:
    from topic_model_constants import *
    import handle_properties
    from mongo_connector import MongoConnector
    from word2vecwrapper import Word2vecWrapper
    from termvisualiser import TermVisualiser
else:
    from topics2themes.topic_model_constants import *
    import topics2themes.handle_properties as handle_properties
    from topics2themes.mongo_connector import MongoConnector
    from topics2themes.word2vecwrapper import Word2vecWrapper
    from topics2themes.termvisualiser import TermVisualiser
try:
    sent_tokenize("Check if punkt is imported")
except:
    print("Download punkt tokenizer")
    import nltk
    nltk.download('punkt')


TOPIC_NUMBER = "TOPIC_NUMBER"
TERM_LIST = "TERM_LIST"
DOCUMENT_LIST = "DOCUMENT_LIST"
DOCUMENT = "document"
TERMS_IN_TOPIC = "terms_in_topic"
TOPIC_CONFIDENCE = "topic_confidence"
TOPIC_INDEX = "topic_index"
TEXT = "text"
LABEL = "label"
BASE_NAME = "base_name"
FULL_NAME = "full_name"
#COLLOCATION_JSON_BINDER = " _ "
SYNONYM_JSON_BINDER = " / "
PAR_START = "["
PAR_END = "]"
DOC_ID =  "doc_id"
DOCUMENT_TOPIC_STRENGTH = "document_topic_strength"
ORIGINAL_DOCUMENT =  "original_document"
FOUND_CONCEPTS = "found_concepts"
MARKED_DOCUMENT_TOK = "marked_document_tok"
MODEL_INFO = "MODEL_INFO"
MODEL = "MODEL"
PRE_PROCESS_COLLOCATION_MARKER = "PREPROCESSCOLLOCATIONMARKER"
NO_TOPIC_CHOSEN = "NOTOPIC"
SHOW_ARGUMENTATION = "SHOW_ARGUMENTATION"
SHOW_SENTIMENT = "SHOW_SENTIMENT"


#####
# Stop word list
######
class StopwordHandler():
    def __init__(self):
        self.stop_word_set = None
        self.user_stop_word_list = []
    
    def get_user_stop_word_list(self):
        return self.user_stop_word_list
    
    def get_entire_used_stop_word_list(self):
        return self.stop_word_set
    
    def get_stop_word_set(self, stop_word_file, stop_words_from_configuration_file, path_slash_format):
        if stop_word_file == None:
            return None
        if self.stop_word_set == None:
            f = open(os.path.join(path_slash_format, stop_word_file))
            additional_stop_words = [word.strip() for word in f.readlines()]
            self.user_stop_word_list = additional_stop_words
            f.close()
            self.stop_word_set = set(stop_words_from_configuration_file).union(additional_stop_words)
        return self.stop_word_set



term_visualiser = TermVisualiser()

####
# Main 
####

def can_model_be_created():
    can_model_be_created = True
    try:
        if not ALLOWED_TO_CREATE_MODEL:
            can_model_be_created = False
    except: # Default if nothing is given in environment configuration
        can_model_be_created = True

    return str(can_model_be_created)



def get_min_score_for_collocation_part(synonym, original_term_dict):
    for syn in synonym.split(COLLOCATION_BINDER):
        if syn not in original_term_dict:
            return False # if not all subparts are in the dictionary, return False
    scores = [original_term_dict[collocation_part] for collocation_part in synonym.split(COLLOCATION_BINDER)]
    return min(scores)


def run_make_topic_models(mongo_con, properties, path_slash_format, model_name, save_in_database = True):
    
    stopword_handler = StopwordHandler()
    
    words_not_to_include_in_clustering = []
    if properties.WORDS_NOT_TO_INCLUDE_IN_CLUSTERING_FILE != None:
        if not os.path.isfile(os.path.join(path_slash_format, properties.WORDS_NOT_TO_INCLUDE_IN_CLUSTERING_FILE)):
            raise FileNotFoundError("The file for specifying words not to include in clustering doesn't exist. Filename given in configuration is: " + \
                                    properties.WORDS_NOT_TO_INCLUDE_IN_CLUSTERING_FILE)
        with open(os.path.join(path_slash_format, properties.WORDS_NOT_TO_INCLUDE_IN_CLUSTERING_FILE)) as words_not_to_include_in_clustering_file:
            for word in words_not_to_include_in_clustering_file.readlines():
                words_not_to_include_in_clustering.append(word.strip())

    # TODO: Move to other
    manual_made_cluster_dict = {}
    if properties.MANUAL_CLUSTER_FILE != None:
        if not os.path.isfile(os.path.join(path_slash_format, properties.MANUAL_CLUSTER_FILE)):
            raise FileNotFoundError("The file for specifying manually constructed words doesn't exist. Filename given in configuration is: " + \
                                    properties.MANUAL_CLUSTER_FILE)
        with open(os.path.join(path_slash_format, properties.MANUAL_CLUSTER_FILE)) as manual_cluster_file:
            for line in manual_cluster_file:
                cluster_words = line.strip().split(" ") #TODO: Sort first
                for word in cluster_words:
                    manual_made_cluster_dict[word] = SYNONYM_BINDER.join(cluster_words)


    word2vecwrapper = None
    if properties.PRE_PROCESS:
        word2vecwrapper = Word2vecWrapper(properties.SPACE_FOR_PATH, properties.VECTOR_LENGTH, properties.MAX_DIST_FOR_CLUSTERING,\
                                      words_not_to_include_in_clustering, manual_made_cluster_dict, properties.BINARY_SPACE, properties.GENSIM_FORMAT)
    
    data_set_name = os.path.basename(path_slash_format)
 
    #stop_word_file = os.path.join(path_slash_format, properties.STOP_WORD_FILE)
    
    if save_in_database:
        print("Model will be saved in database as: " + data_set_name)
    else:
        print("Model will not be saved in database")
    
    manual_collocations = []
    if properties.MANUAL_COLLOCATIONS != None:
          if not os.path.isfile(os.path.join(path_slash_format, properties.MANUAL_COLLOCATIONS)):
              raise FileNotFoundError("The file for specifying manual collocations doesn't exist. Filename given in configuration is: " + \
                                      properties.MANUAL_COLLOCATIONS)
          with open(os.path.join(path_slash_format, properties.MANUAL_COLLOCATIONS)) as manual_collocations_file:
              for word in manual_collocations_file.readlines():
                  manual_collocations.append(word.strip())
                  
    
    file_list = read_discussion_documents(properties.DATA_LABEL_LIST,
                                            data_set_name,
                                          properties.REMOVE_DUPLICATES, properties.MIN_NGRAM_LENGTH_FOR_DUPLICATE, properties.CLEANING_METHOD,
                                          manual_collocations)

    documents = [el[TEXT] for el in file_list]


    print("Make models for "+ str(len(documents)) + " documents.")

    MAX_NR_OF_MODEL_SIZE_RERUNS = 50


    if properties.TOPIC_MODEL_ALGORITHM == NMF_NAME:
        print()
        print("*************")
        print("scikit nmf")
        print()
        
        number_of_topics = properties.NUMBER_OF_TOPICS
        
        for rerun_nr in range(0, MAX_NR_OF_MODEL_SIZE_RERUNS):
            max_less_than_requested_models_returned = number_of_topics*properties.PROPORTION_OF_LESS_TOPIC_TO_ALLOW
            print("max_less_than_requested_models_returned", max_less_than_requested_models_returned)
            
            print("Training model with " + str(number_of_topics) + " requested topics")
            topic_info, most_typical_model, tf_vectorizer =\
                train_scikit_nmf_model(properties, documents, word2vecwrapper, path_slash_format, model_name, stopword_handler)

            print("Found " + str(len(topic_info)) + " stable topics in re-run number " + str(rerun_nr))
            if (number_of_topics - len(topic_info) <= max_less_than_requested_models_returned) or len(topic_info) < 3: #Assume there is at least two topics
                break # This topic is okay, use it
            else:
                # Try again, with a requested number of topic that is more similar to the number of topics
                # found in previous run
                number_of_topics = int(len(topic_info) + max_less_than_requested_models_returned)

        print("Using model with " + str(len(topic_info)) + " stable topics")
        
        result_dict, time, post_id = \
            print_and_get_topic_info(properties, topic_info, file_list, mongo_con, data_set_name, model_name, save_in_database,\
                                                              most_typical_model, tf_vectorizer, stopword_handler, path_slash_format)
        
        print("\nMade models for "+ str(len(documents)) + " documents.")
        
        return result_dict, time, post_id, most_typical_model


    if properties.TOPIC_MODEL_ALGORITHM == LDA_NAME:
        number_of_topics = properties.NUMBER_OF_TOPICS
        
        for rerun_nr in range(0, MAX_NR_OF_MODEL_SIZE_RERUNS):
            max_less_than_requested_models_returned = number_of_topics*properties.PROPORTION_OF_LESS_TOPIC_TO_ALLOW
            print("max_less_than_requested_models_returned", max_less_than_requested_models_returned)
            
            print("Training model with " + str(number_of_topics) + " requested topics")
            topic_info, most_typical_model, tf_vectorizer = \
                train_scikit_lda_model(properties, documents, word2vecwrapper, path_slash_format, model_name, stopword_handler)
            

            print("Found " + str(len(topic_info)) + " stable topics in re-run number " + str(rerun_nr))
            if number_of_topics - len(topic_info) <= max_less_than_requested_models_returned:
                break # This topic is okay, use it
            else:
                # Try again, with a requested number of topic that is more similar to the number of topics
                # found in previous run
                number_of_topics = int(len(topic_info) + max_less_than_requested_models_returned)
        
        
        print("Using model with " + str(len(topic_info)) + " stable topics")
        result_dict, time, post_id = \
            print_and_get_topic_info(properties, topic_info, file_list, mongo_con, data_set_name, model_name, save_in_database,\
                                                          most_typical_model, tf_vectorizer, stopword_handler, path_slash_format)
        return result_dict, time, post_id, most_typical_model

    
def get_current_file_name(name, topic_model_algorithm):
    return os.path.join(PATH_TOPIC_MODEL_OUTPUT, name + "_" + topic_model_algorithm)

######
# Read documents from file
######
def read_discussion_documents(data_label_list, data_set_name, whether_to_remove_duplicates, n_gram_length_conf, cleaning_method, manual_collocations):
    file_list = []

    print("data_label_list", data_label_list)
    for data_info in data_label_list:
        data_dir = os.path.join(WORKSPACE_FOLDER, DATA_FOLDER, data_set_name, data_info[DIRECTORY_NAME])
        if not os.path.isdir(data_dir):
            print(os.path.abspath(data_dir), " does not exist")
        files = Path(data_dir).rglob("*.txt")

        print("Reading", os.path.join(data_dir))

        for f in files:
            base_name = os.path.basename(f)
            opened = open(f)
            text = opened.read()
            text.replace("  ", " ")
            
            for collocation in sorted(manual_collocations, reverse=True):
                if collocation in text:
                    to_replace = collocation.replace(" ", COLLOCATION_BINDER)
                    text = text.replace(collocation, to_replace)
                elif collocation in text.lower():
                    to_replace = collocation.replace(" ", COLLOCATION_BINDER)
                    text = text.replace(collocation, to_replace)
                
            file_list.append({TEXT: text, LABEL: data_info[DATA_LABEL], BASE_NAME: base_name, FULL_NAME: f})
            opened.close()

    #remove duplicates. Just keep the first occurrence, and remove the once comming after
    previous_texts = set()
    filtered_file_list = []
    
    previous_sub_texts = set()
    
    nr_of_removed_files = 0
    file_list_len_sorted = sorted(file_list, key=lambda x: len(x[TEXT]))
    for file in file_list_len_sorted:
        filtered_text = []
        for ch in cleaning_method(file[TEXT]).strip():
            if ch.isalpha() or (ch == " " and (len(filtered_text) > 0 and filtered_text[-1] != " ")): #don't add several white space in a row
                filtered_text.append(ch.lower())
        filtered_text_text = "".join(filtered_text).strip()
        
        if whether_to_remove_duplicates:
            sp = filtered_text_text.split(" ")
            add_this_file, found_duplicate = is_duplicate(filtered_text_text, sp, n_gram_length_conf, previous_sub_texts)
    
            # For short texts, also check with other n-gram length than configured by n_gram_lenth
            if add_this_file and len(sp) <= n_gram_length_conf + 2:
                n_gram_length_short = int(len(sp) - len(sp)/4)
                add_this_file_exact = is_duplicate(filtered_text_text, sp, n_gram_length_short, previous_sub_texts)
                for j in range(n_gram_length_short, len(sp) + 1):
                    add_this_file, found_duplicate = is_duplicate(filtered_text_text, sp, j, previous_sub_texts)
                    if not add_this_file:
                        break
            if add_this_file:
                filtered_file_list.append(file)
            else:
                nr_of_removed_files = nr_of_removed_files + 1
        else: # no dupblicate_remove
            filtered_file_list.append(file)

    print("The number of removed files is: ", nr_of_removed_files, " Adjust the parameter 'MIN_NGRAM_LENGTH_FOR_DUPLICATE' for more or less strict duplicate removal." )
    return filtered_file_list

def is_duplicate(filtered_text_text, sp, n_gram_length_conf, previous_sub_texts):
    found_duplicate = None
    n_gram_length = n_gram_length_conf
        
    add_this_file = True
    sub_tokens = []
    for token in sp:
        if token.strip() == "":
            continue
        sub_tokens.append(token)
        if len(sub_tokens) > n_gram_length:
            del sub_tokens[0]
            sub_text = "".join(sub_tokens)
            if sub_text not in previous_sub_texts:
                previous_sub_texts.add(sub_text)
            else: # this subtext has appeared before
                add_this_file = False
                found_duplicate = sub_text
                break
    return add_this_file, found_duplicate
    
###########
# Overall functionality for pre-processing, training models and printing output
############


# Copied (and modified) from
#https://medium.com/@aneesha/topic-modeling-with-scikit-learn-e80d33668730
def train_scikit_lda_model(properties, documents, word2vecwrapper, path_slash_format, model_name, stopword_handler):
    
    pre_processed_documents = pre_process(properties, documents, word2vecwrapper, path_slash_format, model_name, stopword_handler)
    texts, tf_vectorizer, tf = get_scikit_bow(properties, pre_processed_documents, CountVectorizer, stopword_handler, path_slash_format)
    
    model_list = []
    for i in range(0, properties.NUMBER_OF_RUNS):
        lda = LatentDirichletAllocation(n_components= properties.NUMBER_OF_TOPICS, max_iter=10, learning_method='online', learning_offset=50.).fit(tf)
        model_list.append(lda)
    
    topic_info, most_typical_model = get_scikit_topics(properties, model_list, tf_vectorizer, tf, documents)
    return topic_info, most_typical_model, tf_vectorizer

# Copied (and modified) from
#https://medium.com/@aneesha/topic-modeling-with-scikit-learn-e80d33668730

def train_scikit_nmf_model(properties, documents, word2vecwrapper, path_slash_format, model_name, stopword_handler):
                           
    pre_processed_documents = pre_process(properties, documents, word2vecwrapper, path_slash_format, model_name, stopword_handler)
    texts, tfidf_vectorizer, tfidf = get_scikit_bow(properties, pre_processed_documents, TfidfVectorizer, stopword_handler, path_slash_format)
    
    model_list = []
    for i in range(0, properties.NUMBER_OF_RUNS):
        print("Running topic model nr " + str(i))
        #nmf = NMF(n_components=number_of_topics, alpha=.1, l1_ratio=.5, init='random').fit(tfidf)
        nmf = NMF(n_components= properties.NUMBER_OF_TOPICS, alpha=.1, l1_ratio=.5, init='nndsvd', shuffle = True).fit(tfidf)
        model_list.append(nmf)
    print("Start getting topic model info")
    topic_info, most_typical_model = get_scikit_topics(properties, model_list, tfidf_vectorizer, tfidf, documents)
    return topic_info, most_typical_model, tfidf_vectorizer


def get_very_simple_tokenised(document, lower = True):
    if lower:
        document = document.lower()
    very_simple_tok = document.replace(".", " .").replace('"', ' " ').replace(",", " ,").\
        replace(":", " :").replace("\t", ".\t").replace("..", ".").replace("...", ".").replace("\t", " ").replace(";", " ;").replace("!", " !").replace("?", " ?").replace("(", " ( ").replace(")", " ) ").replace(">", "> ").replace("<", " <").replace("  ", " ").replace("   ", " ").split(" ")
    return very_simple_tok

def untokenize(simple_tokenised):
    text =  " ".join(simple_tokenised)
    return replace_spaces(text)

def replace_spaces(text):
    return text.replace(" .", ".").replace(' " ', '"').replace(" ,", ",").\
        replace(" :", ":").replace(" ;", ";").replace(" !", "!").replace(" ?", "?").replace(" ( ", "(").replace(" ) ", ")")


#####
# Pre-process and turn the documents into lists of terms to feed to the topic models
#####


def pre_process(properties, raw_documents, word2vecwrapper, path_slash_format, model_name, stopword_handler):

    documents = []
    for d in raw_documents:
        documents.append(properties.CLEANING_METHOD (d))
    
    if not properties.PRE_PROCESS:
        return documents
    
    #documents, n_grams, final_features = find_frequent_n_grams(raw_documents, collocation_cut_off,\
    #                                                         max_occurrence_outside_collocation=min_document_frequency,\
    #                                                          collocation_marker = PRE_PROCESS_COLLOCATION_MARKER)


    #vectorizer = CountVectorizer(binary = True, min_df=collocation_cut_off, max_features = max_features)
    #vectorizer.fit_transform(raw_documents)
    #features = vectorizer.get_feature_names()
    #print(features)



    pre_processed_documents = pre_process_word2vec(properties, documents, word2vecwrapper, path_slash_format, model_name, stopword_handler)

    print("***************")
    return pre_processed_documents

def pre_process_word2vec(properties, documents, word2vecwrapper, path_slash_format, model_name, stopword_handler):

    synonym_output_dir = os.path.join(path_slash_format, SYNONYM_FOLDER_NAME)
    if not os.path.exists(synonym_output_dir):
        os.makedirs(synonym_output_dir)
    synonym_file = os.path.join(synonym_output_dir, model_name + "_synonyms.txt")
        
    #word_vectorizer = CountVectorizer(binary = True, stop_words=stopword_handler.get_stop_word_set(stop_word_file, stop_word_set), min_df= 0.005)
    word_vectorizer = CountVectorizer(binary = True, stop_words=stopword_handler.get_stop_word_set(properties.STOP_WORD_FILE, properties.STOP_WORD_SET, path_slash_format),\
        min_df = properties.MIN_DOCUMENT_FREQUENCY_TO_INCLUDE_IN_CLUSTERING)
    transformation = word_vectorizer.fit_transform(documents)
    word2vecwrapper.set_vocabulary(word_vectorizer.get_feature_names())
    word2vecwrapper.load_clustering(synonym_file, transformation)
    
    term_visualiser.set_vocabulary(word_vectorizer.get_feature_names(), path_slash_format)
    
    print("Start replacing with similars")
    pre_processed_documents = []
    vectorizer = CountVectorizer(binary = True, lowercase=True)
    word_tokenizer = vectorizer.build_tokenizer()
    for document in documents:
        document = document.replace("\n", " ")
        pre_processed_document = []
        #very_simple_tok = document.lower().replace(".", " .").replace(",", " ,").\
        #    replace(":", " :").replace(";", " ;").replace("!", " !").replace("?", " ?").replace("(", " ( ").replace(")", " ) ").split(" ")
        scikit_tok = [w.lower() for w in word_tokenizer(document)]
 
        for token in scikit_tok:
            pre_processed_document.append(word2vecwrapper.get_similars(token))
        pre_processed_documents.append(" ".join(pre_processed_document))
    
    print("End replacing with similars")
    return pre_processed_documents


def find_frequent_n_grams(documents, collocation_cut_off, nr_of_words_that_have_occurred_outside_n_gram_cutoff = None,\
                          allowed_n_gram_components = None, max_occurrence_outside_collocation=1, collocation_marker=COLLOCATION_BINDER):
    """
    Frequent collocations are concatenated to one term in the corpus
    (For instance if smallpox and small pox are both used, now small_pox will be
    created, which will then show up as a synonym).
    """
    
    
    new_documents = []
    
    # Construct a list of potential n-grams
    ngram_vectorizer = CountVectorizer(binary = True, ngram_range = (2, 4), min_df=collocation_cut_off)
    ngram_vectorizer.fit_transform(documents)
    
    if allowed_n_gram_components == None:
        allowed_ngrams = ngram_vectorizer.get_feature_names()
    else:
        allowed_ngrams = []
        for el in ngram_vectorizer.get_feature_names():
            sp = el.split(" ")
            add_ngram = True
            for gram in sp:
                if gram not in allowed_n_gram_components:
                    add_ngram = False
            if add_ngram:
                allowed_ngrams.append(el)

    # Mark these potential n-grams in the documents
    allowed_ngrams.sort(key = lambda s: len(s.split(" ")), reverse = True)
    for document in documents:
        new_document = document.lower()
        #new_document = document.replace(collocation_marker, " ") # If there are words already in the corpus containing "_" remove this so the are not interpreted as an n-gram
        for el in allowed_ngrams:
            if el in new_document:
                #new_document = new_document.replace(el, el.replace(" ", collocation_marker))
                new_document = new_document.replace(el, " ")
        new_documents.append(new_document)


    token_vectorizer = CountVectorizer(binary = True, ngram_range = (1, 1), min_df= 1 + max_occurrence_outside_collocation)
    token_vectorizer.fit_transform(new_documents)
    no_ngrams_features = set([token for token in token_vectorizer.get_feature_names() if " " not in token])



    filtered_ngram_list = [] # Only ngrams where the constituent ouccrs a maximum of nr_of_words_that_have_occurred_outside_n_gram_cutoff_to_use time outside the ngram
    for ngram in allowed_ngrams:
        sp = ngram.split(" ")
        if nr_of_words_that_have_occurred_outside_n_gram_cutoff != None:
            nr_of_words_that_have_occurred_outside_n_gram_cutoff_to_use = nr_of_words_that_have_occurred_outside_n_gram_cutoff
        else:
            nr_of_words_that_have_occurred_outside_n_gram_cutoff_to_use = len(sp)
            # Default is that none of the words is allowed to occur outside the n-gram

        nr_of_words_that_have_occurred_outside_n_gram = 0
        for word in sp:
            if word in no_ngrams_features:
                nr_of_words_that_have_occurred_outside_n_gram = nr_of_words_that_have_occurred_outside_n_gram + 1

        if nr_of_words_that_have_occurred_outside_n_gram <= len(sp) - nr_of_words_that_have_occurred_outside_n_gram_cutoff_to_use: # at least one of the words most not have occurred in another context than the ngram
            filtered_ngram_list.append(ngram)

    new_filtered_documents = []
    for document in documents:
        new_document = document.lower()
        new_document = new_document.replace(collocation_marker, " ") # If there are words already in the corpus containing "_" remove this so the are not interpreted as an n-gram
        for el in filtered_ngram_list:
            if el in new_document:
                new_document = new_document.replace(el, el.replace(" ", collocation_marker))
        new_filtered_documents.append(new_document)

    final_documents_vectorizer = CountVectorizer(binary = True, ngram_range = (1, 1), min_df = 1)
    final_documents_vectorizer.fit_transform(new_filtered_documents)
    final_features = set(final_documents_vectorizer.get_feature_names())

    # remove e.g. bigrams that only occur in the context of a three-gram
    if allowed_n_gram_components == None:
        filtered_final_feautures = set(final_documents_vectorizer.get_feature_names())
    else:
        filtered_final_feautures = []
        # Add n-grams and the terms in the documents that are not included in the n-grams
        for el in final_documents_vectorizer.get_feature_names():
            add = True
            for sub_part in el.split(collocation_marker):
                if sub_part not in allowed_n_gram_components:
                    add = False
            if add:
                filtered_final_feautures.append(el)

    filtered_ngram_list_that_occurs_as_feature = [f for f in filtered_ngram_list if f.replace(" ", collocation_marker) in filtered_final_feautures]

    removed_ngrams = [f.replace(" ", collocation_marker) for f in filtered_ngram_list if f not in filtered_final_feautures]
    return new_filtered_documents, filtered_ngram_list_that_occurs_as_feature, filtered_final_feautures

    

def get_scikit_bow(properties, documents, vectorizer, stopword_handler, path_slash_format):
    """
    Will tranform the list of documents that are given as input, to a list of terms
    that occurr in these documents

    The vectorizer that is given as input is the type of scikit learn vectorizer that is to be used

    The list of terms will be a result of the pre-processed documents, and might, for instance
    look as follows for the on of the documents:

    ['vaccination_programmes', 'cease__ceased', 'prefer']

    vaccination_programmes is a collocation and cease__ceased is one word
    """
    
    if len(documents) < 3: # if there is only two documents these parameters are the only that work
                           # but just for debugging, no point of running with only two documents
        min_document_frequency = 1
        max_document_frequency = 1.0

    ngram_length = 1
    
    stop_words=stopword_handler.get_stop_word_set(properties.STOP_WORD_FILE, properties.STOP_WORD_SET, path_slash_format)
    max_document_frequency = properties.MAX_DOCUMENT_FREQUENCY
    min_document_frequency = properties.MIN_DOCUMENT_FREQUENCY
    max_features = properties.MAX_NR_OF_FEATURES
    binary = properties.BINARY_TF
    
    if type(vectorizer) == TfidfVectorizer:
        # Use sublinear_tf, which used log(tf), to lower the advantage for long documents
        tf_vectorizer = vectorizer(sublinear_tf = True, max_df= max_document_frequency, min_df=min_document_frequency,\
                                   ngram_range = (1, ngram_length), stop_words = stop_words, max_features = max_features, binary = binary, use_idf=False)
    else:
        tf_vectorizer = vectorizer(max_df= max_document_frequency, min_df=min_document_frequency,\
                                   ngram_range = (1, ngram_length), stop_words=stop_words,
                               max_features = max_features, binary = binary)
        
    tf = tf_vectorizer.fit_transform(documents)
    inversed = tf_vectorizer.inverse_transform(tf)
    to_return = []
    for el in inversed:
        to_return.append(list(el))

    return to_return, tf_vectorizer, tf



######
# Train the topic models and retrieve info from them
######


def get_scikit_topics(properties, model_list, vectorizer, transformed, documents):
    
    """
    Return info from topics that were stable enough to appear in all models in model_list
    """
    #print(properties)
    nr_of_top_words = properties.NR_OF_TOP_WORDS
    no_top_documents = properties.NR_OF_TOP_DOCUMENTS
    overlap_cut_off = properties.OVERLAP_CUT_OFF
    percentage_none_outliers = properties.PERCENTATE_NONE_OUTLIERS
    
    previous_topic_list_list = [] # list in which each element when the code is run will
    #consist of a list containing the topics that are similar from the different runs
    #[ [{topic with dog words from fold 1}, {topic with dog words from fold 2} .. ]  [] ]
    # The following code performs this matching between the different topics created in each run
    
    model_results = []
    for nr, model in enumerate(model_list):
        ret_list = get_scikit_topics_one_model(model, vectorizer, transformed, documents, nr_of_top_words, no_top_documents)
        model_results.append(ret_list)

    print("Original nr of models: ", str(len(model_results)))
    # Code for removing the model re-runs with an output with the smallest overlap with other model re-runs
    # Keep the properties.PERCENTATE_NONE_OUTLIERS of the re-runs
    term_results = []
    for ret_list in model_results:
        term_set = set()
        for el in ret_list:
            for term, prob in el[TERM_LIST]:
                term_set.add(term)

        term_results.append(term_set)

    overlap_averages = []
    for nr, terms in enumerate(term_results):
        set_size = len(terms)
        overlap_prop_sum = 0
        for inner_nr, inner_terms in enumerate(term_results):
            if nr != inner_nr:
                overlap_prop = len(terms & inner_terms)/set_size
                overlap_prop_sum = overlap_prop_sum + overlap_prop
        overlap_prop_avg = overlap_prop_sum/len(term_results)
        overlap_averages.append((overlap_prop_avg, nr))
    overlap_averages_sorted = sorted(overlap_averages, reverse=True)
    overlap_averages_sorted_removed_outliers = [nr for (overl, nr) in overlap_averages_sorted[:math.ceil(len(overlap_averages_sorted)*percentage_none_outliers)]]

    most_typical_model = None
    model_results_filtered = []

    for nr, el in enumerate(model_results):
        if nr in overlap_averages_sorted_removed_outliers:
            model_results_filtered.append(el)
        if nr == overlap_averages_sorted_removed_outliers[0]:
            most_typical_model = model_list[nr]


    for nr, ret_list in enumerate(model_results_filtered):
        print("Analysing output from fold nr: ", nr)
        for el in ret_list:
            current_topic = {}
            current_topic[TERM_LIST] = {}
            for term, prob in el[TERM_LIST]:
                current_topic[TERM_LIST][term] = prob
            current_topic[MODEL_INFO] = el

            found_match = False
            for previous_topic_list in previous_topic_list_list:
                # current_topic and previous_topic_list are compared on their included terms
                if is_overlap(current_topic, previous_topic_list, overlap_cut_off):
                    previous_topic_list.append(current_topic) # if an existing similar topic is found, attach to this one
                    break
            if not found_match: # if there is no existing topic to which to assign the currently searched topic result, create a new one
                previous_topic_list_list.append([current_topic])


    # When the matching between differnt folds has been carried out. Go through the result
    # and decide which topics to keep
    
    minimum_found_for_a_topic_to_be_kept = round(len(model_results_filtered))
    # A topic has to occurr in all folds to be included, therefore 'minimum_found_for_a_topic_to_be_kept' is equal to the number of folds
    
    average_list = [] # only include topics that have been stable in this, and average the information from each run
    # that is, only include the terms that have occurred in many of the folds and the documents that have occurred in many of the folds
    
    #####
    for nr, previous_topic_list in enumerate(previous_topic_list_list):
        
        if len(previous_topic_list) >= minimum_found_for_a_topic_to_be_kept: # the topic is to be kept
            average_info = {}
            
            #TERM
            #minimum_topics_for_a_term_to_be_kept = round(len(previous_topic_list) * overlap_cut_off)
            final_terms_for_topic = []
            only_terms = [list(el[TERM_LIST].keys()) for el in previous_topic_list]
            flattened_uniqe = list(set(np.concatenate(only_terms)))
            for term in flattened_uniqe:
                nr_of_models_the_term_occurred_in = 0
                sum_score_for_term = 0
                for previous_topic in previous_topic_list:
                    if term in previous_topic[TERM_LIST]:
                        nr_of_models_the_term_occurred_in = nr_of_models_the_term_occurred_in + 1
                        sum_score_for_term = sum_score_for_term + previous_topic[TERM_LIST][term]
                #if nr_of_models_the_term_occurred_in >= #minimum_topics_for_a_term_to_be_kept:
                final_terms_for_topic.append((term, sum_score_for_term / nr_of_models_the_term_occurred_in))
        

            #DOCUMENTS
            selected_documents_strength = []
            docs = [el[MODEL_INFO][DOCUMENT_LIST] for el in previous_topic_list]
            doc_id_occ = {}
            for doc_list in docs:
                doc_ids = [doc[DOC_ID] for doc in doc_list]
                doc_strengths = [doc[DOCUMENT_TOPIC_STRENGTH] for doc in doc_list]
                for doc_id, doc_strength in zip(doc_ids, doc_strengths):
                    if doc_id not in doc_id_occ:
                        doc_id_occ[doc_id] = []
                    doc_id_occ[doc_id].append(doc_strength)

            # Keept the no_top_documents have the larged summed topic-document association
            sum_association = sorted([(sum(occ_list), doc_id) for (doc_id, occ_list) in doc_id_occ.items()], reverse = True)[:no_top_documents]
            for (sumstr, doc_id) in sum_association:
                selected_documents_strength.append({DOC_ID : doc_id,\
                                           DOCUMENT_TOPIC_STRENGTH : sumstr})
            
            document_info, final_terms_for_topic_filtered_for_document_occurrence = \
                construct_document_info_average(documents, selected_documents_strength, final_terms_for_topic)
            average_info[DOCUMENT_LIST] = document_info

            average_info[TERM_LIST] = final_terms_for_topic_filtered_for_document_occurrence[:nr_of_top_words]

            average_info[TOPIC_NUMBER] = nr + 1
            average_list.append(average_info)
            

    return average_list, most_typical_model


def get_scikit_topics_one_model(model, vectorizer, transformed, documents, nr_of_top_words, no_top_documents):
    """
    Returns a list of dictionaries, where the dictionary contains topic number
    , term list and document list for the model {TOPIC_NUMBER:topic_idx, TERM_LIST:term_list, DOCUMENT_LIST:doc_list}
    The document list in turn, contains a four tuple with (document index, marked document, document strength, original document), where doc_i is the index in of
    the documents as given as input to the model)
    """
    W = model.transform(transformed)
    H = model.components_
        
    ret_list = []
    feature_names = vectorizer.get_feature_names() 
    for topic_idx, topic in enumerate(H):
        # terms
        term_list = []
        term_preprocessed_dict = {} # map collocation/synonym-cluster to the word that is found in the text
        term_list_replace = []
        for i in topic.argsort()[:-nr_of_top_words - 1:-1]:
            if topic[i] > 0.000:
                term_list.append((feature_names[i], topic[i]))
                term = feature_names[i]
                
                for split_synonym in term.split(SYNONYM_BINDER):
                    for split_collocation in split_synonym.split(COLLOCATION_BINDER):
                        term_list_replace.append(split_collocation)
                        if split_collocation not in term_preprocessed_dict:
                            term_preprocessed_dict[split_collocation] = []
                        term_preprocessed_dict[split_collocation].append(term)
        term_list_replace = list(set(term_list_replace))
        term_list_replace.sort(key = len, reverse = True)
   

        doc_strength = sorted(W[:,topic_idx])[::-1]
        top_doc_indices = np.argsort( W[:,topic_idx] )[::-1][0:no_top_documents]
        doc_list= [{DOC_ID: doc_i, DOCUMENT_TOPIC_STRENGTH : strength} for doc_i, strength in zip(top_doc_indices, doc_strength)]
        topic_dict = {TOPIC_NUMBER:topic_idx, TERM_LIST:term_list, DOCUMENT_LIST:doc_list}
        ret_list.append(topic_dict)
    return ret_list


def construct_document_info_average(documents, selected_documents_strength, terms_strength):
    
    # Only retain terms that are found in any of the selected documents
    terms_strength_filtered = set()
    
  
    ###
    term_list = []
    term_preprocessed_dict = {} # map collocation/synonym-cluster to the word that is found in the text
    term_strength_dict = {} # map the term to its stength, so that a new terms_strength list can be created with the terms found in the documents
    term_list_replace = []
    for term, strength in terms_strength:
        term_strength_dict[term] = strength
        for split_synonym in term.split(SYNONYM_BINDER):
            for split_collocation in split_synonym.split(COLLOCATION_BINDER):
                term_list_replace.append(split_collocation)
                if split_collocation not in term_preprocessed_dict:
                    term_preprocessed_dict[split_collocation] = []
                term_preprocessed_dict[split_collocation].append(term)

    term_list_replace = list(set(term_list_replace))
    term_list_replace.sort(key = len, reverse = True)

    ###

    doc_list = []
    for selected in selected_documents_strength:
        doc_i = selected[DOC_ID]
        strength = selected[DOCUMENT_TOPIC_STRENGTH]
        found_concepts = []
        if strength > 0.000:
            simple_tokenised = get_very_simple_tokenised(documents[doc_i], lower = False)
            for el in simple_tokenised:
                if el.lower() in term_list_replace:
                    found_concepts.extend(term_preprocessed_dict[el.lower()])


            if len(found_concepts) > 0 : # only include documents where at least on one of the terms is found
                doc_list.append(\
                                {DOC_ID: doc_i, \
                                DOCUMENT_TOPIC_STRENGTH : strength,\
                                ORIGINAL_DOCUMENT: documents[doc_i],\
                                FOUND_CONCEPTS : list(set(found_concepts))})

        for t in set(found_concepts):
            ts = (term_strength_dict[t], t)
            if ts not in terms_strength_filtered:
                terms_strength_filtered.add(ts)


    terms_strength_filtered_sorted = [(t,s) for (s,t) in sorted(terms_strength_filtered, reverse = True)]

    
    return  doc_list, terms_strength_filtered_sorted




def is_overlap(current_topic, previous_topic_list, overlap_cut_off):
    """
    Check if the term list for two model overlap, with a cutoff of 'overlap_cut_off'
    """

    current_set = Counter(current_topic[TERM_LIST].keys())

    # It need to match with all of the previous similar topics found in
    # previous runs
    for previous_topic in previous_topic_list:
        previous_set = Counter(previous_topic[TERM_LIST].keys())
        overlap = list((current_set & previous_set).elements())
        if overlap == []:
            return False
        
        overlap_figure = len(overlap)/((len(previous_topic[TERM_LIST].keys()) + len(current_topic[TERM_LIST].keys()))/2)
        if overlap_figure < overlap_cut_off:
            return False
    return True

#######
# Print output from the model
#######

# All collocation subparts must be found in the doucment
def is_collocation_in_document(synonym_sub_part, document):
    splitted = synonym_sub_part.split(COLLOCATION_BINDER)
    for collocation in splitted:
        if collocation not in document[FOUND_CONCEPTS]:
            return False
    return True

def is_term_combination_in_document(comb_term, document):
    parts_syn = comb_term.split(SYNONYM_JSON_BINDER)
    for synonym_sub_part in parts_syn:
        if is_collocation_in_document(synonym_sub_part, document):
            return True
    return False
"""
Filelist is a list of document-info-dict, with the same order as for the documents sent to the topic modelling
"""
def print_and_get_topic_info(properties, topic_info, file_list, mongo_con, data_set_name, model_name, save_in_database,\
    most_typical_model, tf_vectorizer, stopword_handler, path_slash_format):

#def print_and_get_topic_info(topic_info, file_list, mongo_con, topic_model_algorithm,\
#                             json_properties, data_set_name, model_name, save_in_database,\
#                             are_these_two_terms_to_be_considered_the_same,\
#                             most_typical_model, tf_vectorizer, additional_labels_method,\
#                             show_argumentation, show_sentiment, stopword_handler):
    """
        Prints output/returns from the topic model in txt and json format (depending on whether it is run as server or as a program)
        
        """
  
    json_properties = properties.get_properties_in_json()
    
    document_dict = {}
    topic_info_list = []
    json_properties["STOP_WORDS"] = stopword_handler.get_user_stop_word_list()
    
    # Get the max_weights for the terms (if a term would be included in several topics)
    max_weight_dict = {}
    for nr, el in enumerate(topic_info):
        for term, score in el[TERM_LIST]:
            if term not in max_weight_dict:
                max_weight_dict[term] = 0
            if score > max_weight_dict[term]:
                max_weight_dict[term] = score

    
    for nr, el in enumerate(topic_info):
        
        
        term_list_sorted_on_score = sorted(el[TERM_LIST], key=lambda x: x[1], reverse=True)
        start_label = '"' + " - ".join([term.split(SYNONYM_BINDER)[0] for (term,score) in term_list_sorted_on_score[:3]]) + '"'
        topic_info_object = {}
        topic_info_object["id"] = el[TOPIC_NUMBER]
        topic_info_object["label"] = start_label
        topic_info_object["topic_terms_previous"] = []
        topic_info_object["topic_terms"] = []
        
        topic_texts = [doc[ORIGINAL_DOCUMENT] for doc in el[DOCUMENT_LIST]]
        

        topic_terms_score_dict = {}
        for term in el[TERM_LIST]:
            topic_terms_score_dict[term[0]] = term[1]


        for key, item in topic_terms_score_dict.items():
            term_object = {}
            term_object["term"] = key.replace(SYNONYM_BINDER,SYNONYM_JSON_BINDER).strip()
            term_object["score"] = item
            topic_info_object["topic_terms"].append(term_object)
        
        term_visualiser.add_terms(topic_info_object["topic_terms"], nr)


        # The same document can appear in several topic_infos
        terms_found_in_processed_documents_so_far = set()
        for nr, document in enumerate(el[DOCUMENT_LIST]):
            
            if document[DOC_ID] not in document_dict:
                #marked_document_for_snippet, terms_found_in_document = add_markings_for_terms(document[ORIGINAL_DOCUMENT],\
                    #                                                             el[TERM_LIST], NO_TOPIC_CHOSEN, original_terms_with_combined_dict, new_terms_with_score_dict, max_weight_dict)

                marked_document, terms_found_in_document = add_markings_for_terms(document[ORIGINAL_DOCUMENT],\
                                                                  el[TERM_LIST], el[TOPIC_NUMBER], max_weight_dict)
                for tfid in terms_found_in_document:
                    terms_found_in_processed_documents_so_far.add(tfid)
            

                #snippet_text = get_snippet_text(marked_document_for_snippet, most_typical_model, tf_vectorizer)

            else:
                marked_document, terms_found_in_document = add_markings_for_terms(document_dict[document[DOC_ID]]["marked_text_tok"],\
                                                                                  el[TERM_LIST], el[TOPIC_NUMBER], max_weight_dict)
              
                for tfid in terms_found_in_document:
                    terms_found_in_processed_documents_so_far.add(tfid)
                    
            
            
            if document[DOC_ID] not in document_dict:
                document_obj = {}
                document_obj["text"] = document[ORIGINAL_DOCUMENT]
                document_obj["snippet"] = get_snippet_text(marked_document, terms_found_in_processed_documents_so_far, properties)
                document_obj["id"] = int(str(document[DOC_ID]))
                document_obj["marked_text_tok"] = marked_document
                document_obj["id_source"] = int(str(document[DOC_ID]))
                document_obj["timestamp"] = int(str(document[DOC_ID]))
                document_obj["document_topics"] = []
                document_obj["label"] = file_list[document[DOC_ID]][LABEL]
                document_obj["base_name"] = file_list[document[DOC_ID]][BASE_NAME]
                document_obj["additional_labels"] = sorted(properties.ADDITIONAL_LABELS_METHOD(file_list[document[DOC_ID]][FULL_NAME]))
                document_dict[document[DOC_ID]] = document_obj
                if document_obj["text"] != file_list[document[DOC_ID]][TEXT]:
                    print("Warning, texts not macthing, \n" +  str(document_obj["original_text"]) + "\n" + str(file_list[document[DOC_ID]][TEXT]))

            else:
                document_dict[document[DOC_ID]]["marked_text_tok"] = marked_document
                document_dict[document[DOC_ID]]["snippet"] = get_snippet_text(marked_document, terms_found_in_processed_documents_so_far, properties)


            document_topic_obj = {}
            document_topic_obj["topic_index"] = el[TOPIC_NUMBER]
            document_topic_obj["topic_confidence"] = document[DOCUMENT_TOPIC_STRENGTH]
            document_topic_obj["terms_found_in_text"] = document[FOUND_CONCEPTS]

            # It is only the terms that are actually included in the document that are added here
            document_topic_obj["terms_in_topic"] = []

            # Only include terms that have occurred in the document
            for term, score in topic_terms_score_dict.items():
                if term in terms_found_in_document:
                    term_object = {}
                    term_object["term"] = term.replace(SYNONYM_BINDER, SYNONYM_JSON_BINDER).strip()
                    term_object["score"] = score
                    document_topic_obj["terms_in_topic"].append(term_object)

            document_dict[document[DOC_ID]]["document_topics"].append(document_topic_obj)


        topic_info_list.append(topic_info_object)



    result_dict = {}
    result_dict[TOPICS] = topic_info_list

    result_dict["themes"] = []
    result_dict[DOCUMENTS] = [value for value in document_dict.values()]
    result_dict[META_DATA] = {"creation_date" : str(datetime.datetime.now()),\
                                "configuration" : json_properties, \
                                    "user" : "dummy_user",\
                                    MODEL_NAME : model_name,\
                                    SHOW_ARGUMENTATION : str(properties.SHOW_ARGUMENTATION),\
                                    SHOW_SENTIMENT : str(properties.SHOW_SENTIMENT)
    }


    if save_in_database:
        saved_time, post_id = mongo_con.insert_new_model(result_dict, data_set_name)
    else:
        print("Don't save in database (for debugging)")

    term_visualiser.dump_term_dict(path_slash_format)

    return result_dict, saved_time, post_id


def get_snippet_text(marked_document, terms_found_in_processed_documents_so_far, properties):
     # TODO: Snippet text processing is not language independent
    NORMAL_MAX_SENTENCES = properties.NUMBER_OF_SENTENCES_IN_SUMMARY
    
    MARKED_TERM_CLASS = "term-to-mark"
    terms_represented_in_summary = set()
    # Keep sentences which include a term marking
    sentences_to_keep = []
   
    sentence_list = sent_tokenize(marked_document)
    kept_sentences = 0
    for sent in sentence_list:
        
        # Default choice, if sentence doesn't contain relevant content
        keep_sentence = False
        
        #only keep sentence with a marked word
        # Also, make sure the summary isn't too long
        if MARKED_TERM_CLASS in sent and kept_sentences < NORMAL_MAX_SENTENCES:
            keep_sentence = True
        # If the summary is too long, but some of the terms found for the topic has not
        # yet been present in the summary, include it anyway
        elif MARKED_TERM_CLASS in sent: #and len(sentence_list) >= NORMAL_MAX_SENTENCE_LENGTH:
            for term in terms_found_in_processed_documents_so_far:
                for sub_term in term.split(SYNONYM_BINDER):
                    for sub_sub_term in sub_term.split(COLLOCATION_BINDER):
                        if sub_sub_term in sent.lower() and sub_sub_term not in terms_represented_in_summary:
                            keep_sentence = True
          
        if keep_sentence:
            # Record which terms that have been represented in the summary
            for term in terms_found_in_processed_documents_so_far:
                for sub_term in term.split(SYNONYM_BINDER):
                    for sub_sub_term in sub_term.split(COLLOCATION_BINDER):
                        if sub_sub_term in sent.lower():
                            terms_represented_in_summary.add(sub_sub_term)
                    
            sentences_to_keep.append(sent)
            kept_sentences = kept_sentences + 1
        else:
            sentences_to_keep.append("MARKING[..]MARKING")
        
    if kept_sentences < 1:
        pass
        #print("******")
        #print(terms_found_in_processed_documents_so_far)
        #print(sentences_to_keep)
        #print(marked_document)
        
    snippet_str = " ".join(sentences_to_keep).replace("]MARKING MARKING[", "").replace("MARKING[","[").replace("]MARKING","]")
    while ".........." in snippet_str:
        snippet_str = snippet_str.replace("..........","....") # Don't make it too loong

   
    return snippet_str

# This is not used in the moment, but could be useful in the future if short summaries are to be created
def get_snippet_text_short_snippet(text, most_typical_model, tf_vectorizer):
    MAX_SNIPPET_SENTENCE_LENGTH = 360
    SENTENCE_HIDDEN_MARKER = "."

    # TODO: This is not language independent
    sentence_list = sent_tokenize(text)

    
    transformed_sentences, result = apply_trained_model_on_sentences(sentence_list, most_typical_model, tf_vectorizer)
    
    inversed = tf_vectorizer.inverse_transform(transformed_sentences)
    inversed_transformed_sentences = []
    for el in inversed:
        inversed_transformed_sentences.append(list(el))
    
    # TODO: Now a topic-independent socring of sentences is performed, so sentences are ranked according to the topic
    # for which they are most typical. Perhaps a topic-specific ranking ought to be carried out as well in the future
    
    # Decide which sentences to keep for the snippet
    max_scores_for_sentences = []
    for nr, (sent, scored) in enumerate(zip(sentence_list, result)):
        max_scores_for_sentences.append((max(scored), nr))
    max_scores_for_sentences.sort(reverse = True)
    sorted_indices_according_to_sentence_importance = [index for (score, index) in max_scores_for_sentences]
    indices_to_keep = []
    chars_used_so_far = 0
    for nr, i in enumerate(sorted_indices_according_to_sentence_importance):
        chars_used_before_this_round = chars_used_so_far
        chars_used_so_far = chars_used_so_far + len((sentence_list[i]))
        # Always keep the most important sentence, but otherwise, break if the snippet gets too long
        # If the text alreday added to the snippet before this round was very short, also add the text
        if chars_used_so_far > MAX_SNIPPET_SENTENCE_LENGTH and nr > 0 and chars_used_before_this_round > MAX_SNIPPET_SENTENCE_LENGTH/2:
            break
        else:
            indices_to_keep.append(i)


    text_snippet = []

    for nr, sent in enumerate(sentence_list):
        if nr in indices_to_keep:
            if nr - 1 not in indices_to_keep and nr != 0: # Going from hidden to shown text and it is not first sentence
                text_snippet.append("] ")
            text_snippet.append(sent + " ")
        else:
            if nr - 1 in indices_to_keep or nr == 0: # Going from shown to hidden (or being the first sentence)
                text_snippet.append("[")
            text_snippet.append(SENTENCE_HIDDEN_MARKER)
            if nr == len(sentence_list) - 1: # the last sentence
                text_snippet.append("] ")
    text_snippet_text = "".join(text_snippet).strip().replace(".]", "..]") # Add one extra dot to make it clearer
    return text_snippet_text


def apply_trained_model_on_sentences(sentence_list, model, tf_vectorizer):
    transformed_sentences = tf_vectorizer.transform(sentence_list)
    result = model.inverse_transform(model.transform(transformed_sentences))
    return transformed_sentences, result


def get_hex_for_term(score, max_score):
    # B scales so that terms with very low score still get some marking. If this can be changed if more marking want to be given to those with very low score
    b = 0.3
    normalizer = 1/(max_score + b)
    dec_score = (score + b)*normalizer
    h =  str(hex(int(dec_score*238)))[2:]
    if len(h) < 2:
        h = h + "0"
    return h.upper()

def add_markings_for_terms(text, term_list, topic_number, max_weight_dict):

    text = text.replace(COLLOCATION_BINDER, " ")
    
    all_scores = list(set([score for key, score in max_weight_dict.items()]))

    max_score = max(all_scores)
    
    found_terms = []
    term_list_replace = [t[0] for t in term_list]
    
    term_list_splitted_synonyms_dict = {}
    for word in term_list_replace:
        for sub_word in word.split(SYNONYM_BINDER):
            for sub_sub_word in sub_word.split(COLLOCATION_BINDER):
                term_list_splitted_synonyms_dict[sub_sub_word] = word

    simple_tokenised = get_tokenised(text)
    simple_tokenised_marked = []
    inside_htlm_tag = False
    for (el, token_contains_data) in simple_tokenised:
        if token_contains_data:
            if el.lower() in term_list_splitted_synonyms_dict.keys():
                best_score_for_el = max_weight_dict[term_list_splitted_synonyms_dict[el.lower()]]
                transparancy = get_hex_for_term(best_score_for_el, max_score)
                color = '#D7E9FF'

                simple_tokenised_marked.append('<span class="term-to-mark topic_' + str(topic_number) + \
                                           '"  style="background-color:' + color + str(transparancy) + ';font-weight: 500; color: black;">' + " " + el + " </span>")
                found_terms.append(term_list_splitted_synonyms_dict[el.lower()])
            else:
                simple_tokenised_marked.append(el)
        else:
            simple_tokenised_marked.append(el)
                
    marked_document = untokenize(simple_tokenised_marked)
   
    
    # TODO Perhpas concatnating with lists is faster
    marked_text_transformed = replace_spaces(marked_document.replace(" </span>","</span> "))
    marked_text_inserted_spaces = ""
    ch_nr = 0
    for c in marked_text_transformed:
        if c == "." and ch_nr < len(marked_text_transformed) - 1 and marked_text_transformed[ch_nr + 1] != " ":
            if marked_text_transformed[ch_nr + 1].isupper():
                marked_text_inserted_spaces = marked_text_inserted_spaces + c + " "
            else:
                marked_text_inserted_spaces = marked_text_inserted_spaces + c
        else:
            marked_text_inserted_spaces = marked_text_inserted_spaces + c
        ch_nr = ch_nr + 1

    return marked_text_inserted_spaces, found_terms

# Part html, and make a very simple tokenisation
class HTMLParserTokenise(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.acc_lst = []
        self.global_acc_str = ""
    
    
    def handle_starttag(self, tag, attrs):
        if tag:
            acc_str = ""
            acc_str = acc_str + "<" + tag + " "
            for attr in attrs:
                if attr[0] and attr[1]:
                    acc_str = acc_str + attr[0] + '="' + attr[1] + '" '
            acc_str = acc_str + ">"
            self.acc_lst.append((acc_str, False))
    
    def handle_endtag(self, tag):
        self.acc_lst.append(("</" + tag + ">", False))
    
    def handle_data(self, data):
        data_list = data.replace(".", " .").replace('"', ' " ').replace(",", " ,").\
        replace(":", " :").replace("\t", ".\t").replace("..", ".").replace("...", ".").replace("\t", " ").replace(";", " ;").replace("!", " !").replace("?", " ?").replace("(", " ( ").replace(")", " ) ").replace("  ", " ").replace("   ", " ").split(" ")
        
        self.acc_lst.extend([(data, True) for data in data_list])

def get_tokenised(html_str):
    parser = HTMLParserTokenise()
    parser.feed(html_str)
    return parser.acc_lst


def get_first_in_tuple(item):
    return item[0]


def get_sets_in_data_folder():
    return [el for el in os.listdir(os.path.join(WORKSPACE_FOLDER, DATA_FOLDER)) if (not el.startswith(".")) and os.path.isdir(os.path.join(os.path.join(WORKSPACE_FOLDER, DATA_FOLDER), el))]


def make_model_for_collection(collection_name, model_name, mongo_con):
    properties, path_slash_format, path_dot_format = handle_properties.load_properties_from_parameters(DATA_FOLDER + "." + collection_name)
    result_dict, time, post_id, most_typical_model = run_make_topic_models(mongo_con, properties, path_slash_format, model_name)
    
    return result_dict

###
# Start
###
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    properties, path_slash_format, path_dot_format = handle_properties.load_properties(parser)
    
    mongo_con = None #MongoConnector()
    result_dict, time, post_id, most_typical_model = run_make_topic_models(mongo_con, properties, path_slash_format,\
                                                       datetime.datetime.now(), save_in_database = False)


    print("created " + str(len(result_dict["topics"])) + " topics.")
    print("Created model saved at " + str(time))

    #mongo_con.close_connection()



