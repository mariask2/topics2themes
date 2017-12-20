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
from sklearn.feature_extraction import text
from topic_model_configuration import *


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
DOC_ID =  "doc_id"
DOCUMENT_TOPIC_STRENGTH = "document_topic_strength"
ORIGINAL_DOCUMENT =  "original_document"
FOUND_TERMS = "found_terms"
FOUND_CONCEPTS = "found_concepts"
MARKED_DOCUMENT_TOK = "marked_document_tok"

#####
# Stop word list
######

f = open(STOP_WORD_FILE)
additional_stop_words = [word.strip() for word in f.readlines()]
f.close()
stop_words_set = text.ENGLISH_STOP_WORDS.union(additional_stop_words)

####
# Main 
####

def run_main():
    file_list = read_discussion_documents()
    
    documents = [el[TEXT] for el in file_list]

    print("Make models for "+ str(len(documents)) + " documents.")

    """
    # Did not return any sensible topics on the test corpus
    # Therefore, it is commented out, but the code is retained
    # as it might work on another corpus
    print("*************")
    print("scikit lda")
    file_name_lda = "testoutput_lda.html"
    print("Will write topic modelling output to '" + file_name_lda + "'")
    print("WARNING: If output file exists, content will be overwritten")
    print()
    topic_info, scikit_lda, tf_vectorizer = train_scikit_lda_model(documents, NUMBER_OF_TOPICS, NUMBER_OF_RUNS)

    print("Found " + str(len(topic_info)) + " stable topics")
    print_topic_info(topic_info, file_name_lda, "lda")
    """
    
    print()
    print("*************")
    print("scikit nmf")
    
    file_name_nmf = "testoutput_nmf.html"
    print("Will write topic modelling output to '" + file_name_nmf + "'")
    print("WARNING: If output file exists, content will be overwritten")
    print()
    topic_info, scikit_nmf, tf_vectorizer = train_scikit_nmf_model(documents, NUMBER_OF_TOPICS,  NUMBER_OF_RUNS)

    print("Found " + str(len(topic_info)) + " stable topics")

    print_topic_info(topic_info, file_list, file_name_nmf, "nmf")

    print("\nMade models for "+ str(len(documents)) + " documents.")


######
# Read documents from file
######
def read_discussion_documents():
    file_list = []

    for data_info in DATA_LABEL_LIST:
        data_dir = data_info[DIRECTORY_NAME]
        
        files = []

        files.extend(glob(os.path.join(data_dir, "*.txt")))

        for f in files:
            opened = open(f)
            text = opened.read()
            cleaned_text = corpus_specific_text_cleaning(text)
            file_list.append({TEXT: cleaned_text, LABEL: data_info[DATA_LABEL]})
            opened.close()
        
    return file_list


    
###########
# Overall functionality for pre-processing, training models and printing output
############


# Copied (and modified) from
#https://medium.com/@aneesha/topic-modeling-with-scikit-learn-e80d33668730
def train_scikit_lda_model(documents, number_of_topics, number_of_runs):
    pre_processed_documents = pre_process(documents)
    texts, tf_vectorizer, tf = get_scikit_bow(pre_processed_documents, CountVectorizer)
    model_list = []
    for i in range(0, number_of_runs):
        lda = LatentDirichletAllocation(n_components=number_of_topics, max_iter=10, learning_method='online', learning_offset=50.).fit(tf)
        model_list.append(lda)
    topic_info = get_scikit_topics(model_list, tf_vectorizer, tf, documents, NR_OF_TOP_WORDS, NR_OF_TOP_DOCUMENTS)
    return topic_info, lda, tf_vectorizer

# Copied (and modified) from
#https://medium.com/@aneesha/topic-modeling-with-scikit-learn-e80d33668730
def train_scikit_nmf_model(documents, number_of_topics, number_of_runs):
    pre_processed_documents = pre_process(documents)
    texts, tfidf_vectorizer, tfidf = get_scikit_bow(pre_processed_documents, TfidfVectorizer)
    model_list = []
    for i in range(0, number_of_runs):
        nmf = NMF(n_components=number_of_topics, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf)
        model_list.append(nmf)
    topic_info = get_scikit_topics(model_list, tfidf_vectorizer, tfidf, documents, NR_OF_TOP_WORDS, NR_OF_TOP_DOCUMENTS)
    return topic_info, nmf, tfidf_vectorizer


def get_very_simple_tokenised(document, lower = True):
    if lower:
        document = document.lower()
    very_simple_tok = document.replace(".", " .").replace(",", " ,").\
        replace(":", " :").replace("\t", ".\t").replace("..", ".").replace("...", ".").replace("\t", " ").replace(";", " ;").replace("!", " !").replace("?", " ?").replace("(", " ( ").replace(")", " ) ").replace("  ", " ").replace("   ", " ").split(" ")
    return very_simple_tok

def untokenize(simple_tokenised):
    return " ".join(simple_tokenised).replace(" .", ".").replace(" ,", ",").\
        replace(" :", ":").replace(" ;", ";").replace(" !", "!").replace(" ?", "?").replace(" ( ", "(").replace(" ) ", ")")
#####
# Pre-process and turn the documents into lists of terms to feed to the topic models
#####

def pre_process(raw_documents):
    if not PRE_PROCESS:
        return raw_documents
    documents = find_frequent_n_grams(raw_documents)
        
    word_vectorizer = CountVectorizer(binary = True, min_df=2, stop_words=stop_words_set)
    word_vectorizer.fit_transform(documents)

    cluster_output = "cluster_output.txt"
    print("The output of word clustering will be written to '"  + cluster_output + "'")
    word2vec = word2vecwrapper.Word2vecWrapper(SPACE_FOR_PATH, VECTOR_LENGTH)
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


def find_frequent_n_grams(documents):
    """
    Frequent collocations are concatenated to one term in the corpus
    (For instance smallpox and small pox are both used, now small_pox will be
    created, which will then show up as a synonym).
    """
    new_documents = []
    ngram_vectorizer = CountVectorizer(binary = True, ngram_range = (2, 3), min_df=COLLOCATION_CUT_OFF, stop_words='english')
    ngram_vectorizer.fit_transform(documents)
    for document in documents:
        new_document = document
        for el in ngram_vectorizer.get_feature_names():
            if el in document:
                new_document = new_document.replace(el, el.replace(" ", COLLOCATION_BINDER))
        new_documents.append(new_document)
    return new_documents

    

def get_scikit_bow(documents, vectorizer):
    """
    Will tranform the list of documents that are given as input, to a list of terms
    that occurr in these documents

    The vectorizer that is given as input is the type of scikit learn vectorizer that is to be used

    The list of terms will be a result of the pre-processed documents, and might, for instance
    look as follows for the on of the documents:

    ['vaccination_programmes', 'cease__ceased', 'prefer']

    vaccination_programmes is a collocation and cease__ceased is one word
    """
    
    min_document_frequency = MIN_DOCUMENT_FREQUENCY
    max_document_frequency = MAX_DOCUMENT_FREQUENCY
    if len(documents) < 3: # if there is only two documents these parameters are the only that work
                           # but just for debugging, no point of running with only two documents
        min_document_frequency = 1
        max_document_frequency = 1.0

    ngram_length = 1
    tf_vectorizer = vectorizer(max_df= max_document_frequency, min_df=min_document_frequency,\
                                   ngram_range = (1, ngram_length), stop_words=stop_words_set)
    tf = tf_vectorizer.fit_transform(documents)
    inversed = tf_vectorizer.inverse_transform(tf)
    to_return = []
    for el in inversed:
        to_return.append(list(el))

    return to_return, tf_vectorizer, tf



######
# Train the topic models and retrieve info from them
######

def get_scikit_topics(model_list, vectorizer, transformed, documents, nr_of_top_words, no_top_documents):
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
                if is_overlap(current_topic, previous_topic_list, OVERLAP_CUT_OFF):
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
        found_concepts = []
        found_terms = []
        for doc_i, strength in zip(top_doc_indices, doc_strength):
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

def print_topic_info(topic_info, file_list, file_name, model_type):
    document_dict = {}
    topic_info_list = []
    
    """
    Prints output from the topic model in html format, with topic terms in bold face
    """
    f = open(file_name, "w")
    f_json = open(file_name + ".json", "w")

    f.write('<html><body><font face="times"><div style="width:400px;margin:40px;">\n')
    f.write("<h1> Results for model type " +  model_type + " </h1>\n")
    for nr, el in enumerate(topic_info):
        topic_info_object = {}
        topic_info_object["id"] = el[TOPIC_NUMBER]
        topic_info_object["label"] = ""
        topic_info_object["topic_terms"] = []
         
        f.write("<p>\n")
        f.write("<h2> Topic " + str(nr) + "</h2>\n")
        f.write("<p>\n")
        for term in el[TERM_LIST]:
            f.write(str(term).replace("__","/") + "<br>\n")
            term_object = {}
            term_object["term"] = term[0].replace("__","/")
            term_object["score"] = term[1]
            topic_info_object["topic_terms"].append(term_object)
        f.write("<p>\n")
        f.write(", ".join([term[0].replace("__","/") for term in el[TERM_LIST]]))
        f.write("</p>\n")
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
                    term_object["term"] = term[0].replace("__"," / ")
                    term_object["score"] = term[1]
                    document_topic_obj["terms_in_topic"].append(term_object)
            ###                

            document_dict[document[DOC_ID]]["document_topics"].append(document_topic_obj)
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

    result_dict = {}
    result_dict["topics"] = topic_info_list
    result_dict["themes"] = [{"id": 0, "label": "Click here to add theme label", "theme_topics": [], "theme_documents":[]}]
    result_dict["documents"] = [value for value in document_dict.values()]
    f_json.write(json.dumps(result_dict, indent=4, sort_keys=True))
    f_json.flush()
    f_json.close()
    
###
# Start
###
if __name__ == '__main__':
    run_main()


