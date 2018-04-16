"""
For performing topic modelling. The main file of the package
"""

from pprint import pprint
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
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


TOPIC_NUMBER = "TOPIC_NUMBER"
TERM_LIST = "TERM_LIST"
DOCUMENT_LIST = "DOCUMENT_LIST"
DOCUMENT = "document"
TOPICS = "topics"
TERMS_IN_TOPIC = "terms_in_topic"
TOPIC_CONFIDENCE = "topic_confidence"
TOPIC_INDEX = "topic_index"
TEXT = "text"
LABEL = "label"
COLLOCATION_BINDER = "_"
SYNONYM_JSON_BINDER = " / "
DOC_ID =  "doc_id"
DOCUMENT_TOPIC_STRENGTH = "document_topic_strength"
ORIGINAL_DOCUMENT =  "original_document"
FOUND_TERMS = "found_terms"
FOUND_CONCEPTS = "found_concepts"
MARKED_DOCUMENT_TOK = "marked_document_tok"


#####
# Stop word list
######
class StopwordHandler():
    def __init__(self):
        self.stop_word_set = None
        self.user_stop_word_list = []
    
    def get_user_stop_word_list(self):
        return self.user_stop_word_list
    
    def get_stop_word_set(self, stop_word_file):
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

def run_make_topic_models(mongo_con, properties, path_slash_format, model_name):
    #initialise_dirs(properties.PATH_TOPIC_MODEL_OUTPUT, properties.PATH_USER_INPUT)
    data_set_name = os.path.basename(path_slash_format)
    
    file_list = read_discussion_documents(properties.DATA_LABEL_LIST, properties.CLEANING_METHOD, data_set_name)
    
    documents = [el[TEXT] for el in file_list]

    print("Make models for "+ str(len(documents)) + " documents.")
    
    #print("Will write topic modelling output to '" + get_current_file_name(properties.NAME, properties.TOPIC_MODEL_ALGORITHM)\
        #    + ".json' and '" + get_current_file_name(properties.NAME, properties.TOPIC_MODEL_ALGORITHM) + ".html'")
    #print("WARNING: If output files exists, content will be overwritten")
    
    if properties.TOPIC_MODEL_ALGORITHM == NMF_NAME:
        print()
        print("*************")
        print("scikit nmf")
        print()
        topic_info, scikit_nmf, tf_vectorizer = train_scikit_nmf_model(documents, properties.NUMBER_OF_TOPICS,\
                                                                       properties.NUMBER_OF_RUNS, properties.PRE_PROCESS,\
                                                                       properties.COLLOCATION_CUT_OFF,\
                                                                       properties.STOP_WORD_FILE,\
                                                                       properties.SPACE_FOR_PATH,\
                                                                       properties.VECTOR_LENGTH,\
                                                                       properties.MIN_DOCUMENT_FREQUENCY,\
                                                                       properties.MAX_DOCUMENT_FREQUENCY,\
                                                                       properties.NR_OF_TOP_WORDS,\
                                                                       properties.NR_OF_TOP_DOCUMENTS,\
                                                                       properties.OVERLAP_CUT_OFF,\
                                                                       properties.NO_MATCH,\
                                                                       properties.MANUAL_MADE_DICT)
        
        print("Found " + str(len(topic_info)) + " stable topics")
        
        result_dict, time, post_id = print_and_get_topic_info(topic_info, file_list, mongo_con,\
                                                              properties.TOPIC_MODEL_ALGORITHM,\
                                                              properties.get_properties_in_json(),\
                                                              data_set_name, model_name)
        
        print("\nMade models for "+ str(len(documents)) + " documents.")
        
        return result_dict, time, post_id


    if properties.TOPIC_MODEL_ALGORITHM == LDA_NAME:
    
        topic_info, scikit_lda, tf_vectorizer = train_scikit_lda_model(documents, properties.NUMBER_OF_TOPICS,\
                                                                       properties.NUMBER_OF_RUNS, properties.PRE_PROCESS,\
                                                                       properties.COLLOCATION_CUT_OFF,\
                                                                       properties.STOP_WORD_FILE,\
                                                                       properties.SPACE_FOR_PATH,\
                                                                       properties.VECTOR_LENGTH,\
                                                                       properties.MIN_DOCUMENT_FREQUENCY,\
                                                                       properties.MAX_DOCUMENT_FREQUENCY,\
                                                                       properties.NR_OF_TOP_WORDS,\
                                                                       properties.NR_OF_TOP_DOCUMENTS,\
                                                                       properties.OVERLAP_CUT_OFF,\
                                                                       properties.NO_MATCH,\
                                                                       properties.MANUAL_MADE_DICT)

        print("Found " + str(len(topic_info)) + " stable topics")
        result_dict, time, post_id = print_and_get_topic_info(topic_info, file_list, mongo_con,\
                                                              properties.TOPIC_MODEL_ALGORITHM,\
                                                              properties.get_properties_in_json(),\
                                                              data_set_name, model_name)
        return result_dict, time, post_id

    
def get_current_file_name(name, topic_model_algorithm):
    return os.path.join(PATH_TOPIC_MODEL_OUTPUT, name + "_" + topic_model_algorithm)

######
# Read documents from file
######
def read_discussion_documents(data_label_list, cleaning_method, data_set_name):
    file_list = []

    for data_info in data_label_list:
        data_dir = os.path.join(data_set_name, data_info[DIRECTORY_NAME])
        
        files = []

        files.extend(glob(os.path.join(data_dir, "*.txt")))

        for f in files:
            opened = open(f)
            text = opened.read()
            cleaned_text = cleaning_method(text)
            file_list.append({TEXT: cleaned_text, LABEL: data_info[DATA_LABEL]})
            opened.close()
        
    return file_list


    
###########
# Overall functionality for pre-processing, training models and printing output
############


# Copied (and modified) from
#https://medium.com/@aneesha/topic-modeling-with-scikit-learn-e80d33668730
def train_scikit_lda_model(documents, number_of_topics, number_of_runs, do_pre_process, collocation_cut_off, stop_word_file,\
                           space_for_path, vector_length, min_document_frequency, max_document_frequency,\
                           nr_of_top_words, nr_of_to_documents, overlap_cut_off, no_match, manual_made_dict):
    pre_processed_documents = pre_process(documents, do_pre_process, collocation_cut_off, stop_word_file,\
                                          space_for_path, vector_length, no_match, manual_made_dict)
    texts, tf_vectorizer, tf = get_scikit_bow(pre_processed_documents, CountVectorizer,\
                                              min_document_frequency, max_document_frequency, stop_word_file)
    model_list = []
    for i in range(0, number_of_runs):
        lda = LatentDirichletAllocation(n_components=number_of_topics, max_iter=10, learning_method='online', learning_offset=50.).fit(tf)
        model_list.append(lda)
    topic_info = get_scikit_topics(model_list, tf_vectorizer, tf, documents, nr_of_top_words, nr_of_to_documents, overlap_cut_off)
    return topic_info, lda, tf_vectorizer

# Copied (and modified) from
#https://medium.com/@aneesha/topic-modeling-with-scikit-learn-e80d33668730
def train_scikit_nmf_model(documents, number_of_topics, number_of_runs, do_pre_process, collocation_cut_off, stop_word_file,\
                           space_for_path, vector_length, min_document_frequency, max_document_frequency,\
                           nr_of_top_words, nr_of_to_documents, overlap_cut_off, no_match, manual_made_dict):
    pre_processed_documents = pre_process(documents, do_pre_process, collocation_cut_off, stop_word_file,\
                                          space_for_path, vector_length, no_match, manual_made_dict)
                                          
    
    texts, tfidf_vectorizer, tfidf = get_scikit_bow(pre_processed_documents, TfidfVectorizer,\
                                                    min_document_frequency, max_document_frequency, stop_word_file)
    model_list = []
    for i in range(0, number_of_runs):
        nmf = NMF(n_components=number_of_topics, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf)
        model_list.append(nmf)
    topic_info = get_scikit_topics(model_list, tfidf_vectorizer, tfidf, documents, nr_of_top_words, nr_of_to_documents, overlap_cut_off)
    return topic_info, nmf, tfidf_vectorizer


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
                no_match, manual_made_dict):
    if not do_pre_process:
        return raw_documents
    documents = find_frequent_n_grams(raw_documents, collocation_cut_off)
        
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
    return pre_processed_documents


def find_frequent_n_grams(documents, collocation_cut_off):
    """
    Frequent collocations are concatenated to one term in the corpus
    (For instance smallpox and small pox are both used, now small_pox will be
    created, which will then show up as a synonym).
    """
    new_documents = []
    ngram_vectorizer = CountVectorizer(binary = True, ngram_range = (2, 3), min_df=collocation_cut_off, stop_words='english')
    ngram_vectorizer.fit_transform(documents)
    for document in documents:
        new_document = document
        for el in ngram_vectorizer.get_feature_names():
            if el in document:
                new_document = new_document.replace(el, el.replace(" ", COLLOCATION_BINDER))
        new_documents.append(new_document)
    return new_documents

    

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
    
    previous_topic_list_list = []
    filtered_ret_list = [] # only include topics that have been stable in this
    for nr, model in enumerate(model_list):
        ret_list = get_scikit_topics_one_model(model, vectorizer, transformed, documents, nr_of_top_words, no_top_documents)    
        for el in ret_list:
            current_topic = [term for term, prob in el[TERM_LIST]]
            found_match = False
            for previous_topic_list in previous_topic_list_list:
                # current_topic and previous_topic_list contains a list of terms
                if is_overlap(current_topic, previous_topic_list, overlap_cut_off):
                     previous_topic_list.append(current_topic)
                     found_match = True
                     if nr == len(model_list) - 1: # last iteration in loop
                         if len(previous_topic_list) ==  len(model_list): # only add if this topic has occurred in all runs
                             filtered_ret_list.append(el) 
            if not found_match:
                previous_topic_list_list.append([current_topic])

    return filtered_ret_list # return results from the last run:


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
   
        doc_list = []
        doc_strength = sorted(W[:,topic_idx])[::-1]
        top_doc_indices = np.argsort( W[:,topic_idx] )[::-1][0:no_top_documents]

        for doc_i, strength in zip(top_doc_indices, doc_strength):
            found_concepts = []
            found_terms = []
            if strength > 0.000:
                simple_tokenised = get_very_simple_tokenised(documents[doc_i], lower = False)
                simple_tokenised_marked = []
                for el in simple_tokenised:
                    if el.lower() in term_list_replace:
                        simple_tokenised_marked.append("<b>" + el + "</b>")
                        found_concepts.extend(term_preprocessed_dict[el.lower()])
                        found_terms.append(el.lower())
                    else:
                        simple_tokenised_marked.append(el)
                if len(found_concepts) > 0 : # only include documents where at least on one of the terms is found
                    doc_list.append(\
                                    {DOC_ID: doc_i, \
                                    DOCUMENT_TOPIC_STRENGTH : strength,\
                                    ORIGINAL_DOCUMENT: documents[doc_i],\
                                    FOUND_CONCEPTS : set(found_concepts),\
                                    MARKED_DOCUMENT_TOK : untokenize(simple_tokenised_marked),\
                                    FOUND_TERMS: list(set(found_terms))})
        topic_dict = {TOPIC_NUMBER:topic_idx, TERM_LIST:term_list, DOCUMENT_LIST:doc_list}
        ret_list.append(topic_dict)
    return ret_list

def is_overlap(current_topic, previous_topic_list, overlap_cut_off):
    """
    Check if the term list for two model overlap, with a cutoff of 'overlap_cut_off'
    """
    current_set = Counter(current_topic)
    for previous_topic in previous_topic_list:
        previous_set = Counter(previous_topic)
        overlap = list((current_set & previous_set).elements())
        if overlap != []:
            overlap_figure = len(overlap)/((len(previous_topic) + len(current_topic))/2)
            if overlap_figure > overlap_cut_off:
                return True
    return False

#######
# Print output from the model
#######

def print_and_get_topic_info(topic_info, file_list, mongo_con, topic_model_algorithm, json_properties, data_set_name, model_name):
    document_dict = {}
    topic_info_list = []
    json_properties["STOP_WORDS"] = stopword_handler.get_user_stop_word_list()
    
    """
        Prints output from the topic model in html and json format, with topic terms in bold face
    
        """
    
    #f = open(get_current_file_name(name, topic_model_algorithm) + ".html", "w")
    #f_json = open(get_current_file_name(name, topic_model_algorithm) + ".json", "w")

    #f.write('<html><body><font face="times"><div style="width:400px;margin:40px;">\n')
    #f.write("<h1> Results for model type " + topic_model_algorithm + " </h1>\n")
    for nr, el in enumerate(topic_info):
        """
        term_list_sorted_on_score = sorted(el[TERM_LIST], key=lambda x: x[1], reverse=True)
        start_label = '"' + " - ".join([term.split(SYNONYM_BINDER)[0] for (term,score) in term_list_sorted_on_score[:3]]) + '"'
        topic_info_object = {}
        topic_info_object["id"] = el[TOPIC_NUMBER]
        topic_info_object["label"] = start_label
        topic_info_object["topic_terms"] = []
         
        f.write("<p>\n")
        f.write("<h2> Topic " + str(nr) + "</h2>\n")
        f.write("<p>\n")
        for term in el[TERM_LIST]:
            f.write(str(term).replace(SYNONYM_BINDER,SYNONYM_JSON_BINDER) + "<br>\n")
            term_object = {}
            term_object["term"] = term[0].replace(SYNONYM_BINDER,SYNONYM_JSON_BINDER).strip()
            term_object["score"] = term[1]
            topic_info_object["topic_terms"].append(term_object)
        f.write("<p>\n")
        f.write(", ".join([term[0].replace(SYNONYM_BINDER,SYNONYM_JSON_BINDER) for term in el[TERM_LIST]]))
        f.write("</p>\n")
        """
        
        for nr, document in enumerate(el[DOCUMENT_LIST]):

            if document[DOC_ID] not in document_dict:
                document_obj = {}
                document_obj["text"] = document[ORIGINAL_DOCUMENT]
                document_obj["id"] = int(str(document[DOC_ID]))
                document_obj["marked_text_tok"] = document[MARKED_DOCUMENT_TOK]
                document_obj["id_source"] = int(str(document[DOC_ID]))
                document_obj["timestamp"] = int(str(document[DOC_ID]))
                document_obj["document_topics"] = []
                document_obj["label"] = file_list[document[DOC_ID]][LABEL]
                document_dict[document[DOC_ID]] = document_obj
                if document_obj["text"] != file_list[document[DOC_ID]][TEXT]:
                    print("Warning, texts not macthing, \n" +  str(document_obj["original_text"]) + "\n" + str(file_list[document[DOC_ID]][TEXT]))
            document_topic_obj = {}
            document_topic_obj["topic_index"] = el[TOPIC_NUMBER]
            document_topic_obj["topic_confidence"] = document[DOCUMENT_TOPIC_STRENGTH]
            document_topic_obj["terms_found_in_text"] = document[FOUND_TERMS]
            

            # It is only the terms that are actually included in the document that are added here
            document_topic_obj["terms_in_topic"] = []
            for term in el[TERM_LIST]:
                if term[0] in document[FOUND_CONCEPTS]:
                    term_object = {}
                    term_object["term"] = term[0].replace(SYNONYM_BINDER,SYNONYM_JSON_BINDER).strip()
                    term_object["score"] = term[1]
                    document_topic_obj["terms_in_topic"].append(term_object)
            ###                

            document_dict[document[DOC_ID]]["document_topics"].append(document_topic_obj)
            """
            f.write("<p>\n")
            f.write("<br><p> Document number " + str(nr) + " Strength: " + str(document[DOCUMENT_TOPIC_STRENGTH]) + "</p>\n")
            f.write(document[MARKED_DOCUMENT_TOK])
            f.write("</p>\n")
        f.write("</p>\n")
        f.write("</p>\n")

        topic_info_list.append(topic_info_object)
    f.write("</div></font></body></html>\n")
    f.flush()
    f.close()
    """

    result_dict = {}
    result_dict["topics"] = topic_info_list
    #result_dict["themes"] = [{"id": 0, "label": "Click here to add theme label", "theme_topics": [], "theme_documents":[]}]
    result_dict["themes"] = []
    result_dict["documents"] = [value for value in document_dict.values()]
    result_dict[META_DATA] = {"creation_date" : str(datetime.datetime.now()),\
                                "configuration" : json_properties, \
                                    "user" : "dummy_user",\
                                    MODEL_NAME : model_name}
    #f_json.write(json.dumps(result_dict, indent=4, sort_keys=True))
    #f_json.flush()
    #f_json.close()
    time, post_id = mongo_con.insert_new_model(result_dict, data_set_name)
    
    return result_dict, time, post_id

def initialise_dirs(output_path, input_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    if not os.path.exists(input_path):
        os.makedirs(input_path)


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
    """
    file_name = get_current_file_name() + ".json"
    if not os.path.isfile(file_name):
        return "No saved model with name " + file_name
    f = open(file_name)
    data = f.read()
    f.close()
    json_data = json.loads(data)
    return json_data
    """


def make_model_for_collection(collection_name, model_name, mongo_con):
    properties, path_slash_format, path_dot_format = handle_properties.load_properties_from_parameters(DATA_FOLDER + "." + collection_name, DEFAULT_ROOT_DIRECTORY)
    result_dict, time, post_id = run_make_topic_models(mongo_con, properties, path_slash_format, model_name)
    return result_dict

###
# Start
###
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    properties, path_slash_format, path_dot_format = handle_properties.load_properties(parser)
    
    mongo_con = MongoConnector()
    result_dict, time, post_id = run_make_topic_models(mongo_con, properties, path_slash_format, datetime.datetime.now())
    print("Created model saved at " + str(time))
    print(get_cashed_topic_model(mongo_con).keys())
    mongo_con.close_connection()



