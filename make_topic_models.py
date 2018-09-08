"""
For performing topic modelling. The main file of the package
"""

from pprint import pprint
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from nltk.tokenize import sent_tokenize

import os
import numpy as np
import json
from collections import Counter
import word2vecwrapper
from glob import glob
import datetime
from sklearn.feature_extraction import text
#from topic_model_configuration import *
from topic_model_constants import *
import handle_properties
from mongo_connector import MongoConnector
import argparse
import datetime
import time
import math


TOPIC_NUMBER = "TOPIC_NUMBER"
TERM_LIST = "TERM_LIST"
DOCUMENT_LIST = "DOCUMENT_LIST"
DOCUMENT = "document"
TERMS_IN_TOPIC = "terms_in_topic"
TOPIC_CONFIDENCE = "topic_confidence"
TOPIC_INDEX = "topic_index"
TEXT = "text"
LABEL = "label"
COLLOCATION_BINDER = "_"
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
    
    def get_stop_word_set(self, stop_word_file):
        if stop_word_file == None:
            return None
        if self.stop_word_set == None:
            f = open(stop_word_file)
            additional_stop_words = [word.strip() for word in f.readlines()]
            self.user_stop_word_list = additional_stop_words
            f.close()
            self.stop_word_set = text.ENGLISH_STOP_WORDS.union(additional_stop_words)
        return self.stop_word_set

stopword_handler = StopwordHandler()

####
# Main 
####


# This function is only kept for the writing to file functionality. Should perhaps be removed in the future
def get_collocations_from_documents(documents, term_set, are_these_two_terms_to_be_considered_the_same):
    collocation_features, original_term_weigth_dict =  get_collocations_from_documents_before_synonyms(documents, term_set)

    collocation_features_list_list = [collocation_features, collocation_features]
    original_term_weigth_dict_list = [original_term_weigth_dict, original_term_weigth_dict]

    return find_synonyms_from_collocation_features(collocation_features_list_list, original_term_weigth_dict_list, are_these_two_terms_to_be_considered_the_same)

def get_collocations_from_documents_before_synonyms(documents, term_set):
    original_term_dict = {}
    for t in term_set:
        original_term_dict[t[0]] = t[1]
    extracted_term_set = original_term_dict.keys() #  set([t[0] for t in term_set])
    cutoff = 2

    documents_with_collocation_marked, ngrams, all_features = find_frequent_n_grams(documents, collocation_cut_off=cutoff,\
                                                                      nr_of_words_that_have_occurred_outside_n_gram_cutoff = 1,\
                                                                      allowed_n_gram_components = extracted_term_set,\
                                                                      max_occurrence_outside_collocation = 0,\
                                                                                    collocation_marker = COLLOCATION_BINDER)
    return all_features, original_term_dict


def find_synonyms_from_collocation_features(collocation_features_list, original_term_dict_list, are_these_two_terms_to_be_considered_the_same):
    
    collocation_features = set() # Features are combined from each element in collocation_features_list
    for feature_list in  collocation_features_list:
        for feature in feature_list:
            collocation_features.add(feature)

    original_term_dict = {}
    for dict in original_term_dict_list:
        for term_key, term_score in dict.items():
            if term_key not in original_term_dict:
                original_term_dict[term_key] = term_score
            else:
                if term_score > original_term_dict[term_key]:
                    original_term_dict[term_key] = term_score


    final_features = set()

    for c in collocation_features:
        add = True
        c = c.replace(SYNONYM_BINDER, ",")
        for already_added in final_features:
            if should_this_be_added_to_synonyms_cluster(already_added, c, are_these_two_terms_to_be_considered_the_same) and add:
                final_features.remove(already_added)
                already_added_modified = already_added + SYNONYM_JSON_BINDER + c
                final_features.add(already_added_modified)
                add = False
        if add:
            final_features.add(c)

    new_terms_with_score = []
    new_terms_with_score_dict = {}
    original_terms_with_combined_dict = {}

    for term in final_features:
        best_score = 0
        original_terms_for_combined_term = []
        for synonym in term.split(SYNONYM_JSON_BINDER):
            score_for_synonoym = get_min_score_for_collocation_part(synonym, original_term_dict) # If the synonym is a collocation, use the lowest score for the collocation component
            for collocation_part in synonym.split(COLLOCATION_BINDER):
                original_terms_for_combined_term.append(collocation_part)
            # but use the highest score for the synonym
            if score_for_synonoym > best_score:
                best_score = score_for_synonoym # use the highest score among its included parts
        new_terms_with_score.append((term, best_score))
        new_terms_with_score_dict[term] = best_score

        for original in original_terms_for_combined_term:
            if original not in original_terms_with_combined_dict:
                original_terms_with_combined_dict[original] = [term]
            else:
                original_terms_with_combined_dict[original].append(term)
    return new_terms_with_score, original_terms_with_combined_dict, new_terms_with_score_dict

def should_this_be_added_to_synonyms_cluster(already_added, c, are_these_two_terms_to_be_considered_the_same):
    for syn in already_added.split(SYNONYM_JSON_BINDER):
        if are_these_two_terms_to_be_considered_the_same(syn, c):
            return True
    return False

def get_min_score_for_collocation_part(synonym, original_term_dict):
    for syn in synonym.split(COLLOCATION_BINDER):
        if syn not in original_term_dict:
            return False # if not all subparts are in the dictionary, return False
    scores = [original_term_dict[collocation_part] for collocation_part in synonym.split(COLLOCATION_BINDER)]
    return min(scores)


def run_make_topic_models(mongo_con, properties, path_slash_format, model_name, save_in_database = True):

    data_set_name = os.path.basename(path_slash_format)
 
    stop_word_file = os.path.join(path_slash_format, properties.STOP_WORD_FILE)
    
    if save_in_database:
        print("Model will be saved in database as: " + data_set_name)
    else:
        print("Model will not be saved in database")
    
    file_list = read_discussion_documents(properties.DATA_LABEL_LIST, properties.CLEANING_METHOD, data_set_name, \
                                          properties.REMOVE_DUPLICATES, properties.MIN_NGRAM_LENGTH_FOR_DUPLICATE)

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
            topic_info, most_typical_model, tf_vectorizer = train_scikit_nmf_model(documents, number_of_topics,\
                                                                       properties.NUMBER_OF_RUNS, properties.PRE_PROCESS,\
                                                                       properties.COLLOCATION_CUT_OFF,\
                                                                       stop_word_file,\
                                                                       properties.SPACE_FOR_PATH,\
                                                                       properties.VECTOR_LENGTH,\
                                                                       properties.MIN_DOCUMENT_FREQUENCY,\
                                                                       properties.MAX_DOCUMENT_FREQUENCY,\
                                                                       properties.NR_OF_TOP_WORDS,\
                                                                       properties.NR_OF_TOP_DOCUMENTS,\
                                                                       properties.OVERLAP_CUT_OFF,\
                                                                       properties.NO_MATCH,\
                                                                       properties.MANUAL_MADE_DICT)

            print("Found " + str(len(topic_info)) + " stable topics in re-run number " + str(rerun_nr))
            if number_of_topics - len(topic_info) <= max_less_than_requested_models_returned:
                break # This topic is okay, use it
            else:
                # Try again, with a requested number of topic that is more similar to the number of topics
                # found in previous run
                number_of_topics = int(len(topic_info) + max_less_than_requested_models_returned)

        print("Using model with " + str(len(topic_info)) + " stable topics")
        
        result_dict, time, post_id = print_and_get_topic_info(topic_info, file_list, mongo_con,\
                                                              properties.TOPIC_MODEL_ALGORITHM,\
                                                              properties.get_properties_in_json(),\
                                                              data_set_name, model_name, save_in_database,\
                                                              properties.ARE_THESE_TWO_TERMS_CONSIDERED_TO_BE_THE_SAME,\
                                                              most_typical_model,\
                                                              tf_vectorizer)
        
        print("\nMade models for "+ str(len(documents)) + " documents.")
        
        return result_dict, time, post_id, most_typical_model


    if properties.TOPIC_MODEL_ALGORITHM == LDA_NAME:
        number_of_topics = properties.NUMBER_OF_TOPICS
        
        for rerun_nr in range(0, MAX_NR_OF_MODEL_SIZE_RERUNS):
            max_less_than_requested_models_returned = number_of_topics*properties.PROPORTION_OF_LESS_TOPIC_TO_ALLOW
            print("max_less_than_requested_models_returned", max_less_than_requested_models_returned)
            
            print("Training model with " + str(number_of_topics) + " requested topics")
            topic_info, most_typical_model, tf_vectorizer = train_scikit_lda_model(documents, properties.NUMBER_OF_TOPICS,\
                                                                       properties.NUMBER_OF_RUNS, properties.PRE_PROCESS,\
                                                                       properties.COLLOCATION_CUT_OFF,\
                                                                       stop_word_file,\
                                                                       properties.SPACE_FOR_PATH,\
                                                                       properties.VECTOR_LENGTH,\
                                                                       properties.MIN_DOCUMENT_FREQUENCY,\
                                                                       properties.MAX_DOCUMENT_FREQUENCY,\
                                                                       properties.NR_OF_TOP_WORDS,\
                                                                       properties.NR_OF_TOP_DOCUMENTS,\
                                                                       properties.OVERLAP_CUT_OFF,\
                                                                       properties.NO_MATCH,\
                                                                       properties.MANUAL_MADE_DICT)

            print("Found " + str(len(topic_info)) + " stable topics in re-run number " + str(rerun_nr))
            if number_of_topics - len(topic_info) <= max_less_than_requested_models_returned:
                break # This topic is okay, use it
            else:
                # Try again, with a requested number of topic that is more similar to the number of topics
                # found in previous run
                number_of_topics = int(len(topic_info) + max_less_than_requested_models_returned)
        
        
        print("Using model with " + str(len(topic_info)) + " stable topics")
        result_dict, time, post_id = print_and_get_topic_info(topic_info, file_list, mongo_con,\
                                                              properties.TOPIC_MODEL_ALGORITHM,\
                                                              properties.get_properties_in_json(),\
                                                              data_set_name, model_name, save_in_database,\
                                                              properties.ARE_THESE_TWO_TERMS_CONSIDERED_TO_BE_THE_SAME,\
                                                              most_typical_model, \
                                                              tf_vectorizer)
        return result_dict, time, post_id, most_typical_model

    
def get_current_file_name(name, topic_model_algorithm):
    return os.path.join(PATH_TOPIC_MODEL_OUTPUT, name + "_" + topic_model_algorithm)

######
# Read documents from file
######
def read_discussion_documents(data_label_list, cleaning_method, data_set_name, whether_to_remove_duplicates, n_gram_length_conf):
    file_list = []

    print("data_label_list", data_label_list)
    for data_info in data_label_list:
        data_dir = os.path.join(DATA_FOLDER, data_set_name, data_info[DIRECTORY_NAME])
        if not os.path.isdir(data_dir):
            print(os.path.abspath(data_dir), " does not exist")
        files = []

        files.extend(glob(os.path.join(data_dir, "*.txt")))

        print("Reading", os.path.join(data_dir))

        for f in files:
            opened = open(f)
            text = opened.read()
            cleaned_text = cleaning_method(text)
            file_list.append({TEXT: cleaned_text, LABEL: data_info[DATA_LABEL]})
            opened.close()

    #remove duplicates. Just keep the first occurrence, and remove the once comming after
    previous_texts = set()
    filtered_file_list = []
    
    previous_sub_texts = set()
    
    nr_of_removed_files = 0
    file_list_len_sorted = sorted(file_list, key=lambda x: len(x[TEXT]))
    for file in file_list_len_sorted:
        filtered_text = []
        for ch in file[TEXT].strip():
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
def train_scikit_lda_model(documents, number_of_topics, number_of_runs, do_pre_process, collocation_cut_off, stop_word_file,\
                           space_for_path, vector_length, min_document_frequency, max_document_frequency,\
                           nr_of_top_words, nr_of_to_documents, overlap_cut_off, no_match, manual_made_dict):
    pre_processed_documents = pre_process(documents, do_pre_process, collocation_cut_off, stop_word_file,\
                                          space_for_path, vector_length, no_match, manual_made_dict, min_document_frequency)
    texts, tf_vectorizer, tf = get_scikit_bow(pre_processed_documents, CountVectorizer,\
                                              min_document_frequency, max_document_frequency, stop_word_file)
    model_list = []
    for i in range(0, number_of_runs):
        lda = LatentDirichletAllocation(n_components=number_of_topics, max_iter=10, learning_method='online', learning_offset=50.).fit(tf)
        model_list.append(lda)
    topic_info, most_typical_model = get_scikit_topics(model_list, tf_vectorizer, tf, documents, nr_of_top_words, nr_of_to_documents, overlap_cut_off)
    return topic_info, most_typical_model, tf_vectorizer

# Copied (and modified) from
#https://medium.com/@aneesha/topic-modeling-with-scikit-learn-e80d33668730
def train_scikit_nmf_model(documents, number_of_topics, number_of_runs, do_pre_process, collocation_cut_off, stop_word_file,\
                           space_for_path, vector_length, min_document_frequency, max_document_frequency,\
                           nr_of_top_words, nr_of_to_documents, overlap_cut_off, no_match, manual_made_dict):
    pre_processed_documents = pre_process(documents, do_pre_process, collocation_cut_off, stop_word_file,\
                                          space_for_path, vector_length, no_match, manual_made_dict, min_document_frequency)
                                          
    
    texts, tfidf_vectorizer, tfidf = get_scikit_bow(pre_processed_documents, TfidfVectorizer,\
                                                    min_document_frequency, max_document_frequency, stop_word_file)
    model_list = []
    for i in range(0, number_of_runs):
        nmf = NMF(n_components=number_of_topics, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf)
        model_list.append(nmf)
    topic_info, most_typical_model = get_scikit_topics(model_list, tfidf_vectorizer, tfidf, documents, nr_of_top_words, nr_of_to_documents, overlap_cut_off)
    return topic_info, most_typical_model, tfidf_vectorizer


def get_very_simple_tokenised(document, lower = True):
    if lower:
        document = document.lower()
    very_simple_tok = document.replace(".", " .").replace('"', ' " ').replace(",", " ,").\
        replace(":", " :").replace("\t", ".\t").replace("..", ".").replace("...", ".").replace("\t", " ").replace(";", " ;").replace("!", " !").replace("?", " ?").replace("(", " ( ").replace(")", " ) ").replace("  ", " ").replace("   ", " ").split(" ")
    return very_simple_tok

def untokenize(simple_tokenised):
    return " ".join(simple_tokenised).replace(" .", ".").replace(' " ', '"').replace(" ,", ",").\
        replace(" :", ":").replace(" ;", ";").replace(" !", "!").replace(" ?", "?").replace(" ( ", "(").replace(" ) ", ")")
#####
# Pre-process and turn the documents into lists of terms to feed to the topic models
#####

def pre_process(raw_documents, do_pre_process, collocation_cut_off, stop_word_file, space_for_path, vector_length,\
                no_match, manual_made_dict, min_document_frequency):
    if not do_pre_process:
        return raw_documents
    documents, n_grams, final_features = find_frequent_n_grams(raw_documents, collocation_cut_off,\
                                                               max_occurrence_outside_collocation=min_document_frequency,\
                                                               collocation_marker = PRE_PROCESS_COLLOCATION_MARKER)

    pre_processed_documents = documents


    """
    word_vectorizer = CountVectorizer(binary = True, min_df=2, stop_words=stopword_handler.get_stop_word_set(stop_word_file))
    word_vectorizer.fit_transform(documents)

    cluster_output = "cluster_output.txt"
    print("The output of word clustering will be written to '"  + cluster_output + "'")
    word2vec = word2vecwrapper.Word2vecWrapper(space_for_path, vector_length, no_match, manual_made_dict)
    word2vec.set_vocabulary(word_vectorizer.get_feature_names())
    word2vec.load_clustering(cluster_output)

    pre_processed_documents = []
    for document in documents:
        pre_processed_document = []
        very_simple_tok = get_very_simple_tokenised(document)
        for token in very_simple_tok:
            pre_processed_document.append(word2vec.get_similars(token))
        pre_processed_documents.append(" ".join(pre_processed_document))

    word2vec.end()
    """
    return pre_processed_documents


def find_frequent_n_grams(documents, collocation_cut_off, nr_of_words_that_have_occurred_outside_n_gram_cutoff = None,\
                          allowed_n_gram_components = None, max_occurrence_outside_collocation=1, collocation_marker=COLLOCATION_BINDER):
    """
    Frequent collocations are concatenated to one term in the corpus
    (For instance smallpox and small pox are both used, now small_pox will be
    created, which will then show up as a synonym).
    """
    new_documents = []
    

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

    allowed_ngrams.sort(key = lambda s: len(s.split(" ")), reverse = True)
    for document in documents:
        new_document = document.replace(collocation_marker, " ") # If there are words already in the corpus containing "_" remove this so the are not interpreted as an n-gram
        for el in allowed_ngrams:
            if el in document:
                new_document = new_document.replace(el, el.replace(" ", collocation_marker))
        new_documents.append(new_document)

    token_vectorizer = CountVectorizer(binary = True, ngram_range = (1, 1), min_df= 1 + max_occurrence_outside_collocation)
    token_vectorizer.fit_transform(new_documents)
    no_ngrams_features = set([token for token in token_vectorizer.get_feature_names() if " " not in token])
    filtered_ngram_list = [] # Only ngrams where the constituent ouccrs a maximum of one time outside the ngram
    for ngram in allowed_ngrams:
        sp = ngram.split(" ")
        if nr_of_words_that_have_occurred_outside_n_gram_cutoff != None:
            nr_of_words_that_have_occurred_outside_n_gram_cutoff_to_use = nr_of_words_that_have_occurred_outside_n_gram_cutoff
        else:
            nr_of_words_that_have_occurred_outside_n_gram_cutoff_to_use = len(sp)

        nr_of_words_that_have_occurred_outside_n_gram = 0
        for word in sp:
            if word in no_ngrams_features:
                nr_of_words_that_have_occurred_outside_n_gram = nr_of_words_that_have_occurred_outside_n_gram + 1
        if nr_of_words_that_have_occurred_outside_n_gram <= len(sp) - nr_of_words_that_have_occurred_outside_n_gram_cutoff_to_use: # at least one of the words most not have occurred in another context than the ngram
            filtered_ngram_list.append(ngram)



    new_filtered_documents = []
    for document in documents:
        new_document = document.replace(collocation_marker, " ") # If there are words already in the corpus containing "_" remove this so the are not interpreted as an n-gram
        for el in filtered_ngram_list:
            if el in document:
                new_document = new_document.replace(el, el.replace(" ", collocation_marker))
        new_filtered_documents.append(new_document)

    final_documents_vectorizer = CountVectorizer(binary = True, ngram_range = (1, 1), min_df = 1)
    final_documents_vectorizer.fit_transform(new_filtered_documents)
    final_features = set(final_documents_vectorizer.get_feature_names())

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
    # remove e.g. bigrams that only occur in the context of a three-gram
    filtered_ngram_list_that_occurs_as_feature = [f for f in filtered_ngram_list if f in filtered_final_feautures]
    removed_ngrams = [f.replace(" ", collocation_marker) for f in filtered_ngram_list if f not in filtered_final_feautures]
    return new_filtered_documents, filtered_ngram_list_that_occurs_as_feature, filtered_final_feautures

    

def get_scikit_bow(documents, vectorizer, min_document_frequency, max_document_frequency, stop_word_file):
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
    tf_vectorizer = vectorizer(max_df= max_document_frequency, min_df=min_document_frequency,\
                                   ngram_range = (1, ngram_length), stop_words=stopword_handler.get_stop_word_set(stop_word_file))
    tf = tf_vectorizer.fit_transform(documents)
    inversed = tf_vectorizer.inverse_transform(tf)
    to_return = []
    for el in inversed:
        to_return.append(list(el))

    return to_return, tf_vectorizer, tf



######
# Train the topic models and retrieve info from them
######


    
def get_scikit_topics(model_list, vectorizer, transformed, documents, nr_of_top_words, no_top_documents, overlap_cut_off):
    
    """
    Return info from topics that were stable enough to appear in all models in model_list
    """
    
    previous_topic_list_list = [] # list in which each element when the code is run will
    #consist of a list containing the topics that are similar from the different runs
    #[ [{topic with dog words from fold 1}, {topic with dog words from fold 2} .. ]  [] ]
    # The following code performs this matching between the different topics created in each run
    
    model_results = []
    for nr, model in enumerate(model_list):
        ret_list = get_scikit_topics_one_model(model, vectorizer, transformed, documents, nr_of_top_words, no_top_documents)
        model_results.append(ret_list)

    # Code for removing the model re-runs with an output with the smallest overlap with other model re-runs
    # Remove the 10% most outlier re-runs
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
    overlap_averages_sorted_removed_outliers = [nr for (overl, nr) in overlap_averages_sorted[:int(len(overlap_averages_sorted)*0.90)]]

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
            #print(ret_list)
            #print("ret_list")
            current_topic = {}
            current_topic[TERM_LIST] = {}
            for term, prob in el[TERM_LIST]:
                current_topic[TERM_LIST][term] = prob
            current_topic[MODEL_INFO] = el
            #print("current_topic", current_topic)
            #print("*******")
            found_match = False
            for previous_topic_list in previous_topic_list_list:
                # current_topic and previous_topic_list contains a list of terms
                if is_overlap(current_topic, previous_topic_list, overlap_cut_off):
                    previous_topic_list.append(current_topic) # if an existing similar topic is found, attach to this one
            if not found_match: # if there is no existing topic to which to assign the currently searched topic result, create a new one
                previous_topic_list_list.append([current_topic])


    # When the matching between differnt folds has been carried out. Go through the result
    # and decide which topics to keep
    
    minimum_found_for_a_topic_to_be_kept = round(len(model_results_filtered))
    # A topic has to occurr in all folds to be included
    
    average_list = [] # only include topics that have been stable in this, and average the information from each run
    # that is, only include the terms that have occurred in many of the folds and the documents that have occurred in many of the folds
    
    #####
    for nr, previous_topic_list in enumerate(previous_topic_list_list):
        
        if len(previous_topic_list) >= minimum_found_for_a_topic_to_be_kept: # the topic is to be kept
            average_info = {}
            
            #TERM
            minimum_topics_for_a_term_to_be_kept = round(len(previous_topic_list) * overlap_cut_off)
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
                if nr_of_models_the_term_occurred_in >= minimum_topics_for_a_term_to_be_kept:
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


            average_info[TERM_LIST] = final_terms_for_topic_filtered_for_document_occurrence

            average_info[TOPIC_NUMBER] = nr + 1
            average_list.append(average_info)
            

    """
    print("***********")
    for el in average_list:
        print(sorted([term for (term, s) in el[TERM_LIST]]))
        print("----")
    print(len(average_list))
    print("***********")

    """
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
                
                for split_synonym in term.split(word2vecwrapper.SYNONYM_BINDER):
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
        for split_synonym in term.split(word2vecwrapper.SYNONYM_BINDER):
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


def print_and_get_topic_info(topic_info, file_list, mongo_con, topic_model_algorithm,\
                             json_properties, data_set_name, model_name, save_in_database,\
                             are_these_two_terms_to_be_considered_the_same,\
                             most_typical_model, tf_vectorizer):
    """
        Prints output/returns from the topic model in txt and json format (depending on whether it is run as server or as a program), with topic terms in bold face
        
        """
    
    document_dict = {}
    topic_info_list = []
    json_properties["STOP_WORDS"] = stopword_handler.get_user_stop_word_list()
    
    collocation_features_list_list = []
    original_term_weight_dict_list = []
    
    # Construct collocation lists for all topics
    # And find out the max weight (for the different topics, if a term would be included in several topics) for each term
    max_weight_dict = {}
    for nr, el in enumerate(topic_info):
        topic_texts = [doc[ORIGINAL_DOCUMENT] for doc in el[DOCUMENT_LIST]]
        collocation_features, original_term_weight_dict =  get_collocations_from_documents_before_synonyms(topic_texts, el[TERM_LIST])
        collocation_features_list_list.append(collocation_features)
        original_term_weight_dict_list.append(original_term_weight_dict)
        for term, score in el[TERM_LIST]:
            if term not in max_weight_dict:
                max_weight_dict[term] = 0
            if score > max_weight_dict[term]:
                   max_weight_dict[term] = score



    # Combine the collocation lists from different topics, and also collapse into synonym clusters
    terms_scores_with_colloctations, original_terms_with_combined_dict, new_terms_with_score_dict = find_synonyms_from_collocation_features(collocation_features_list_list, original_term_weight_dict_list, are_these_two_terms_to_be_considered_the_same)

    #print("terms_scores_with_colloctations, original_terms_with_combined_dict", terms_scores_with_colloctations, original_terms_with_combined_dict)
    


    for nr, el in enumerate(topic_info):
        
        term_list_sorted_on_score = sorted(el[TERM_LIST], key=lambda x: x[1], reverse=True)
        start_label = '"' + " - ".join([term.split(SYNONYM_BINDER)[0] for (term,score) in term_list_sorted_on_score[:3]]) + '"'
        topic_info_object = {}
        topic_info_object["id"] = el[TOPIC_NUMBER]
        topic_info_object["label"] = start_label
        topic_info_object["topic_terms_previous"] = []
        topic_info_object["topic_terms"] = []
        
        topic_texts = [doc[ORIGINAL_DOCUMENT] for doc in el[DOCUMENT_LIST]]
        
        # Here it is a term-topic object that is constucted, so it's important to use the term strength that the terms have for the topic,
        # not the max term strength from

        topic_terms_score_dict = {}
        for term in el[TERM_LIST]:
            topic_terms_score_dict[term[0]] = term[1]

        print(topic_terms_score_dict)
        term_combination_score_dict = {}
        for term_combo in [t[0] for t in terms_scores_with_colloctations]:
            best_score = 0
        
            for synonym in term_combo.split(SYNONYM_JSON_BINDER):
                # Returns None is the subpart is not a term for this topic
                score_for_synonoym = get_min_score_for_collocation_part(synonym, topic_terms_score_dict) # If the synonym is a collocation, use the lowest score for the collocation component
            # but use the highest score for the synonym
                if score_for_synonoym:
                    if score_for_synonoym > best_score:
                        best_score = score_for_synonoym # use the highest score among its included parts

            if best_score != 0:
                term_combination_score_dict[term_combo] = best_score

    #print(term_combination_score_dict)


        for key, item in term_combination_score_dict.items():
            term_object = {}
            term_object["term"] = key.replace(SYNONYM_BINDER,SYNONYM_JSON_BINDER).strip()
            term_object["score"] = item
            topic_info_object["topic_terms"].append(term_object)
        
        
        # TODO: Perhaps add some strength indication to the marking
        for nr, document in enumerate(el[DOCUMENT_LIST]):
            if document[DOC_ID] not in document_dict:
                marked_document_for_snippet, terms_found_in_document = add_markings_for_terms(document[ORIGINAL_DOCUMENT],\
                                                                                  el[TERM_LIST], NO_TOPIC_CHOSEN, original_terms_with_combined_dict, new_terms_with_score_dict, max_weight_dict)

                marked_document, terms_found_in_document = add_markings_for_terms(document[ORIGINAL_DOCUMENT],\
                                                                  el[TERM_LIST], el[TOPIC_NUMBER], original_terms_with_combined_dict, new_terms_with_score_dict, topic_terms_score_dict)
            
                snippet_text = get_snippet_text(marked_document_for_snippet, most_typical_model, tf_vectorizer)

            else:
                marked_document, terms_found_in_document = add_markings_for_terms(document_dict[document[DOC_ID]]["marked_text_tok"],\
                                                                                  el[TERM_LIST], NO_TOPIC_CHOSEN,\
                                                                                  original_terms_with_combined_dict, \
                                                                                  new_terms_with_score_dict, max_weight_dict)

                

            

            
            if document[DOC_ID] not in document_dict:
                document_obj = {}
                document_obj["text"] = document[ORIGINAL_DOCUMENT]
                document_obj["snippet"] = snippet_text
                document_obj["id"] = int(str(document[DOC_ID]))
                document_obj["marked_text_tok"] = marked_document
                document_obj["id_source"] = int(str(document[DOC_ID]))
                document_obj["timestamp"] = int(str(document[DOC_ID]))
                document_obj["document_topics"] = []
                document_obj["label"] = file_list[document[DOC_ID]][LABEL]
                document_dict[document[DOC_ID]] = document_obj
                if document_obj["text"] != file_list[document[DOC_ID]][TEXT]:
                    print("Warning, texts not macthing, \n" +  str(document_obj["original_text"]) + "\n" + str(file_list[document[DOC_ID]][TEXT]))

            else:
                document_dict[document[DOC_ID]]["marked_text_tok"] = marked_document

            #print(document_dict[document[DOC_ID]]["marked_text_tok"])
            
            document_topic_obj = {}
            document_topic_obj["topic_index"] = el[TOPIC_NUMBER]
            document_topic_obj["topic_confidence"] = document[DOCUMENT_TOPIC_STRENGTH]
            document_topic_obj["terms_found_in_text"] = document[FOUND_CONCEPTS]
            
            # It is only the terms that are actually included in the document that are added here
            document_topic_obj["terms_in_topic"] = []

            # The document-term association score is based on the max score among the terms that belong to that concept
            for term in terms_scores_with_colloctations:
            
                add_term = False
                for synonym_sub_part in term[0].split(SYNONYM_JSON_BINDER):
                    if is_collocation_in_document(synonym_sub_part, document):
                        add_term = True
                if add_term:
                    term_object = {}
                    term_object["term"] = term[0].replace(SYNONYM_BINDER, SYNONYM_JSON_BINDER).strip()
                    term_object["score"] = term[1]
                    document_topic_obj["terms_in_topic"].append(term_object)
            ###

            document_dict[document[DOC_ID]]["document_topics"].append(document_topic_obj)


        topic_info_list.append(topic_info_object)



    result_dict = {}
    result_dict[TOPICS] = topic_info_list

    result_dict["themes"] = []
    result_dict[DOCUMENTS] = [value for value in document_dict.values()]
    result_dict[META_DATA] = {"creation_date" : str(datetime.datetime.now()),\
                                "configuration" : json_properties, \
                                    "user" : "dummy_user",\
                                    MODEL_NAME : model_name}



    if save_in_database:
        saved_time, post_id = mongo_con.insert_new_model(result_dict, data_set_name)
    else:
        saved_time, post_id = None, None

        # If results are not saved in a database, save to a folder instead
        # Make a subfolder from folderwhere the program was run:
        TOPIC_MODEL_EVALUATION_FOLDER_BASE = "topic_model_evalutation"
        if not os.path.exists(TOPIC_MODEL_EVALUATION_FOLDER_BASE):
            os.mkdir(TOPIC_MODEL_EVALUATION_FOLDER_BASE)

        data_set_results_folder = os.path.join(TOPIC_MODEL_EVALUATION_FOLDER_BASE, data_set_name)

        if not os.path.exists(data_set_results_folder):
            os.mkdir(data_set_results_folder)

        TOPIC_MODEL_EVALUATION_FOLDER = os.path.join(data_set_results_folder, str(time.time()))
        if not os.path.exists(TOPIC_MODEL_EVALUATION_FOLDER):
            os.mkdir(TOPIC_MODEL_EVALUATION_FOLDER)
        else:
            print(TOPIC_MODEL_EVALUATION_FOLDER  + " already exists. Exists without saving models")
            exit(1)

        label_dict = {}
        for l in [el[LABEL] for el in file_list]:
            if l not in label_dict:
                label_dict[l] = 0
            label_dict[l] = label_dict[l] + 1

        result_file_labels = os.path.join(TOPIC_MODEL_EVALUATION_FOLDER, data_set_name + "_label_info.txt")
        result_file_labels_file = open(result_file_labels, "w")
        result_file_labels_file.write(str(label_dict))
        result_file_labels_file.close()

        result_file_terms = os.path.join(TOPIC_MODEL_EVALUATION_FOLDER, data_set_name + "_terms.txt")

        terms_open = open(result_file_terms, "w")


        for el in topic_info:
            result_file_csv = os.path.join(TOPIC_MODEL_EVALUATION_FOLDER, data_set_name + "_documents_" + str(el[TOPIC_NUMBER]) + ".txt")
            result_file_csv_no_classification = os.path.join(TOPIC_MODEL_EVALUATION_FOLDER, "no_class_" + data_set_name + "_documents_" + str(el[TOPIC_NUMBER]) + ".txt")
            
            csv_open = open(result_file_csv, "w")
            csv_open_no_class = open(result_file_csv_no_classification, "w")
            
            topic_texts_write_to_file = [doc[ORIGINAL_DOCUMENT] for doc in el[DOCUMENT_LIST]]
            terms_scores_with_colloctations_write_to_file, original_terms_with_combined, new_terms_with_score_dict = \
                get_collocations_from_documents(topic_texts_write_to_file, el[TERM_LIST], are_these_two_terms_to_be_considered_the_same)
            terms_open.write(str(el[TOPIC_NUMBER]) + "\n")
            terms_open.write("----\n")
            terms_open.write(str(sorted([(strength, term) for (term, strength) in terms_scores_with_colloctations_write_to_file])[::-1]) + "\n")
            terms_open.write("********\n\n")

            for (strength, document) in sorted([(doc[DOCUMENT_TOPIC_STRENGTH], doc) for doc in el[DOCUMENT_LIST]], key=get_first_in_tuple)[::-1]:
                output = [document[DOC_ID], strength, document_dict[document[DOC_ID]][LABEL], document[FOUND_CONCEPTS], document[ORIGINAL_DOCUMENT]]
                csv_open.write("\t".join([str(el) for el in output]) + "\n")
            
                output_no_class = [document[DOC_ID], strength, document[FOUND_CONCEPTS], document[ORIGINAL_DOCUMENT]]
                csv_open_no_class.write("\t".join([str(el) for el in output_no_class]) + "\n")
            
            csv_open.flush()
            csv_open.close()

            csv_open_no_class.flush()
            csv_open_no_class.close()

        terms_open.flush()
        terms_open.close()
        print("Written to folder " + TOPIC_MODEL_EVALUATION_FOLDER)

    return result_dict, saved_time, post_id



def get_snippet_text(text, most_typical_model, tf_vectorizer):
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

def add_markings_for_terms(text, term_list, topic_number, original_terms_with_combined_dict,\
                           new_terms_with_score_dict, max_weight_dict):
    
    
    all_scores = list(set([score for key, score in max_weight_dict.items()]))

    max_score = max(all_scores)


    #print([str(hex(int(l/max_score*100))) for l in all_scores])
    #print([get_hex_for_term(term, original_terms_with_combined, new_terms_with_score, max_score) for l in all_scores)])
    #exit(1)
    
    found_terms = []
    term_list_replace = [t[0] for t in term_list]
    
    simple_tokenised = get_very_simple_tokenised(text, lower = False)
    simple_tokenised_marked = []
    for el in simple_tokenised:
        if el.lower() in term_list_replace:

            best_score_for_el = max_weight_dict[el.lower()]
            transparancy = get_hex_for_term(best_score_for_el, max_score)
            #color = '#E6F3FF'
            color = '#D7E9FF'
            #color = '#A6B3EF'
            """
            if topic_number == 2:
                color = '#A2B3EF'
            if topic_number == 3:
                color = '#A1B3EF'
            if topic_number == 4:
                color = '#A0B3EF'
            """
            simple_tokenised_marked.append('<span class="topic_' + str(topic_number) + \
                                           '"  style="background-color:' + color + str(transparancy) + ';font-weight: 500; color: black;">' + " " + el + " </span>")
            found_terms.append(el.lower())
        else:
            simple_tokenised_marked.append(el)

    marked_document = untokenize(simple_tokenised_marked)
    
    # TODO Perhpas concatnating with lists is faster
    marked_text_transformed = marked_document.replace("!", "! ").replace("?", "? ").replace(":", ": ").replace(";", "; ").replace("(", " (")
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

def get_first_in_tuple(item):
    return item[0]



def get_sets_in_data_folder():
    return [el.replace(" ", "_") for el in os.listdir(DATA_FOLDER) if not el.startswith(".")]

def get_cashed_topic_model(mongo_con):
    els = mongo_con.get_all_model_document_name_date_id()
    
    # For now, just take the last of the created models. Add the selection later.
    id_to_use = els[-1][mongo_con.ID]
    date_to_use = els[-1][mongo_con.DATE]
    print("Use model saved at " + str(date_to_use))
    saved_model = mongo_con.get_topic_model_output_with_id(id_to_use)
    result_with_id = {}
    result_with_id["id"] = str(id_to_use)
    result_with_id["saved_model"] = saved_model
    return result_with_id



def make_model_for_collection(collection_name, model_name, mongo_con):
    properties, path_slash_format, path_dot_format = handle_properties.load_properties_from_parameters(DATA_FOLDER + "." + collection_name, DEFAULT_ROOT_DIRECTORY)
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



