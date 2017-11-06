from pprint import pprint
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
import os
import numpy as np
import json
from collections import Counter
import word2vecwrapper


###########
# Internal help functions
###########

NR_OF_TOP_WORDS = 25
NR_OF_TOP_DOCUMENTS = 50
TOPIC_NUMBER = "TOPIC_NUMBER"
TERM_LIST = "TERM_LIST"
DOCUMENT_LIST = "DOCUMENT_LIST"
OVERLAP_CUT_OFF = 0.8
DOCUMENT = "document"
TOPICS = "topics"
TERMS_IN_TOPIC = "terms_in_topic"
TOPIC_CONFIDENCE = "topic_confidence"
TOPIC_INDEX = "topic_index"
NUMBER_OF_TOPICS = 10
N_GRAM_N = 2
NUMBER_OF_RUNS = 10
MIN_DOCUMENT_FREQUENCY = 3
SPACE_FOR_PATH = "/Users/maria/mariaskeppstedtdsv/post-doc/gavagai/googlespace/GoogleNews-vectors-negative300.bin"

# The bow that is used
def get_scikit_bow(documents, ngram_length, vectorizer):
    min_document_frequency = MIN_DOCUMENT_FREQUENCY
    max_document_frequency = 0.95
    if len(documents) < 3: # if there is only two documents these parameters are the only that work
        min_document_frequency = 1
        max_document_frequency = 1.0
    tf_vectorizer = vectorizer(max_df= max_document_frequency, min_df=min_document_frequency,\
                                   ngram_range = (1, ngram_length), stop_words='english')
    tf = tf_vectorizer.fit_transform(documents)
    inversed = tf_vectorizer.inverse_transform(tf)
    to_return = []
    for el in inversed:
        to_return.append(list(el))
    return to_return, tf_vectorizer, tf

"""
def display_topics(model, feature_names, no_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print ("Topic " +  str(topic_idx))
        print(" ".join([feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]]))

# Copied from: https://medium.com/towards-data-science/improving-the-interpretation-of-topic-models-87fd2ee3847d
def display_topics(H, W, feature_names, documents, no_top_words, no_top_documents):
    for topic_idx, topic in enumerate(H):
        print("Topic %d:" % (topic_idx))
        print(" ".join([feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]]))
        top_doc_indices = np.argsort( W[:,topic_idx] )[::-1][0:no_top_documents]
        for doc_index in top_doc_indices:
            print(documents[doc_index])
"""


def is_overlap(current_topic, previous_topic_list, overlap_cut_off):
    current_set = Counter(current_topic)
    for previous_topic in previous_topic_list:
        previous_set = Counter(previous_topic)
        overlap = list((current_set & previous_set).elements())
        if overlap != []:
            overlap_figure = len(overlap)/((len(previous_topic) + len(current_topic))/2)
            if overlap_figure > overlap_cut_off:
                #print(overlap_figure)
                return True
    return False
    
def get_scikit_topics(model_list, vectorizer, transformed, documents, nr_of_top_words, no_top_documents):
    previous_topic_list_list = []
    filtered_ret_list = [] # only include topics that have been stable in this
    for nr, model in enumerate(model_list):
        ret_list = get_scikit_topics_one_model(model, vectorizer, transformed, documents, nr_of_top_words, no_top_documents)    
        for el in ret_list:
            current_topic = [term for term, prob in el[TERM_LIST]]
            found_match = False
            for previous_topic_list in previous_topic_list_list:
                if is_overlap(current_topic, previous_topic_list, OVERLAP_CUT_OFF):
                     previous_topic_list.append(current_topic)
                     found_match = True
                     if nr == len(model_list) - 1: # last iteratio in loop
                         if len(previous_topic_list) ==  len(model_list): # only add if this topic has occurred in all runs
                             filtered_ret_list.append(el) 
            if not found_match:
                previous_topic_list_list.append([current_topic])

    return filtered_ret_list # return results from the last run:

def get_scikit_topics_one_model(model, vectorizer, transformed, documents, nr_of_top_words, no_top_documents):
    W = model.transform(transformed)
    H = model.components_
        
    ret_list = []
    feature_names = vectorizer.get_feature_names() 
    for topic_idx, topic in enumerate(H):
        # terms
        term_list = []
        term_list_replace = []
        for i in topic.argsort()[:-nr_of_top_words - 1:-1]:
            if topic[i] > 0.000:
                term_list.append((feature_names[i], topic[i]))
                for term in feature_names[i].split(" "):
                    for split_synonym in term.split("_"):
                        term_list_replace.append(split_synonym)
        term_list_replace = list(set(term_list_replace))
        term_list_replace.sort(key = len, reverse = True)
        
        doc_list = []
        doc_strength = sorted(W[:,topic_idx])[::-1]
        top_doc_indices = np.argsort( W[:,topic_idx] )[::-1][0:no_top_documents]
        for doc_i, strength in zip(top_doc_indices, doc_strength):
            if strength > 0.000:
                marked_document = documents[doc_i]
                found_term = False
                for term in term_list_replace:
                    if term in documents[doc_i] or term[0].upper() + term[1:] in documents[doc_i] :
                        found_term = True
                        before_changed = marked_document
                        marked_document = marked_document.replace(term, "<b>" + term + "</b>")
                        if  marked_document == before_changed:
                            marked_document = marked_document.replace(term[0].upper() + term[1:], "<b>" + term[0].upper() + term[1:] + "</b>")
                        if marked_document == before_changed:
                            marked_document = marked_document.replace(term.upper(), "<b>" + term.upper() + "</b>")
                if found_term:
                    doc_list.append((doc_i, marked_document, strength)) # only include documents where at least on one of the terms is found
        topic_dict = {TOPIC_NUMBER:topic_idx, TERM_LIST:term_list, DOCUMENT_LIST:doc_list}
        ret_list.append(topic_dict)
    return ret_list



#The strength not normalized. If that is to be done, see for instance:
# https://stackoverflow.com/questions/40597075/python-sklearn-latent-dirichlet-allocation-transform-v-fittransform#40637379
#doc_topic_distr contains the strength for each topic
"""
def get_scikit_topic_for_use(doc_topic_distr, model, tf_vectorizer, documents, no_top_words):
    return_list = []
    feature_names = tf_vectorizer.get_feature_names()
    for document, topic_strength_for_document in zip(documents, doc_topic_distr):        
        return_list_for_document = []
        topic_idx = 0
        for topic, topic_strength in zip(model.components_, topic_strength_for_document):
            term_list = []
            for i in topic.argsort()[:-no_top_words - 1:-1]:
                term_list.append((feature_names[i], topic[i]))
            topic_dict = {TOPIC_INDEX: topic_idx, TERMS_IN_TOPIC : term_list, TOPIC_CONFIDENCE : topic_strength}
            return_list_for_document.append(topic_dict)
            topic_idx = topic_idx + 1
        return_list.append({DOCUMENT: document, TOPICS:return_list_for_document})
    return return_list
"""
#############
# The public functions
#############

############
# Train models
############
# Copied (and modified) from
#https://medium.com/@aneesha/topic-modeling-with-scikit-learn-e80d33668730
def train_scikit_lda_model(documents, number_of_topics, ngram_length, number_of_runs):
    pre_processed_documents = pre_process_word2vec(documents)
    texts, tf_vectorizer, tf = get_scikit_bow(pre_processed_documents, ngram_length, CountVectorizer)
    model_list = []
    for i in range(0, number_of_runs):
        lda = LatentDirichletAllocation(n_components=number_of_topics, max_iter=10, learning_method='online', learning_offset=50.).fit(tf)
        model_list.append(lda)
    topic_info = get_scikit_topics(model_list, tf_vectorizer, tf, documents, NR_OF_TOP_WORDS, NR_OF_TOP_DOCUMENTS)
    return topic_info, lda, tf_vectorizer



# Copied (and modified) from
#https://medium.com/@aneesha/topic-modeling-with-scikit-learn-e80d33668730
def train_scikit_nmf_model(documents, number_of_topics, ngram_length, number_of_runs):
    pre_processed_documents = pre_process_word2vec(documents)
    texts, tfidf_vectorizer, tfidf = get_scikit_bow(pre_processed_documents, ngram_length, TfidfVectorizer)
    model_list = []
    for i in range(0, number_of_runs):
        nmf = NMF(n_components=number_of_topics, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf)
        model_list.append(nmf)
    topic_info = get_scikit_topics(model_list, tfidf_vectorizer, tfidf, documents, NR_OF_TOP_WORDS, NR_OF_TOP_DOCUMENTS)
    return topic_info, nmf, tfidf_vectorizer

def pre_process_word2vec(documents):
    word_vectorizer = CountVectorizer(binary = True, min_df=1, stop_words='english')
    word_vectorizer.fit_transform(documents)
    word2vec = word2vecwrapper.Word2vecWrapper(SPACE_FOR_PATH, 300)
    word2vec.set_vocabulary(word_vectorizer.get_feature_names())
    word2vec.load_clustering()

    pre_processed_documents = []
    for document in documents:
        pre_processed_document = []
        very_simple_tok = document.lower().replace(".", " .").replace(",", " ,").\
            replace(":", " :").replace(";", " ;").replace("!", " !").replace("?", " ?").replace("(", " ( ").replace(")", " ) ").split(" ")
        for token in very_simple_tok:
            pre_processed_document.append(word2vec.get_similars(token))
        pre_processed_documents.append(" ".join(pre_processed_document))

    
    return pre_processed_documents

def read_test_documents():
    lines = []
    f = open("vaccination-tweets-raw.json")
    text_lines = f.readlines()
    f.close()
    for el in text_lines:
        if '"full_text"' in el:
            cleaned = el.replace('"full_text" : ', "").strip().replace('"', '').replace('\\n*', ' ').replace('\\', ' ').replace('&amp', ' ').replace("'ve", ' have')
            cleande = cleaned.replace("don't", 'do not').replace("doesn't", 'does not').replace("Don't", 'Do not').replace("Doesn't", 'Does not')
            no_links = []
            for word in cleaned.split(" "):
                if "//" not in word and "http" not in word and "@" not in word:
                    no_links.append(word)
            lines.append(" ".join(no_links))
    return list(set(lines))

##########
# Test function
###########

def print_topic_info(topic_info, model_type):
    file_name = "testoutput_" + model_type  + ".html"
    
    f = open(file_name, "w")

    f.write('<html><body><font face="times"><div style="width:400px;margin:40px;">\n')
    f.write("<h1> Results for model type " +  model_type + " </h1>\n")
    for nr, el in enumerate(topic_info):
        f.write("<p>\n")
        f.write("<h2> Topic " + str(nr) + "</h2>\n")
        f.write("<p>\n")
        for term in el[TERM_LIST]:
            f.write(str(term) + "<br>\n")
        for document in el[DOCUMENT_LIST]:
            f.write("<p>\n")
            f.write(document[1])
            f.write("</p>\n")
        f.write("</p>\n")
        f.write("</p>\n")
    f.write("</div></font></body></html>\n")
    f.flush()
    f.close()
    
def run_main():
    documents = read_test_documents()

   
    
    #documents = ["Human machine interface for lab abc computer applications.",  "A survey of user opinion of computer system response time. System and human system engineering testing of EPS Relation of user perceived response time to error measurement"] *100

    print("Make models for "+ str(len(documents)) + " documents.")

    """
    print("*************")
    print("scikit lda")
    topic_info, scikit_lda, tf_vectorizer = train_scikit_lda_model(documents, NUMBER_OF_TOPICS, N_GRAM_N, NUMBER_OF_RUNS)
    for el in topic_info:
        pprint(el)
    print(len(topic_info))
    print_topic_info(topic_info, "lda")
    """
    
    print()
    print("*************")
    print("*************")
    print("*************")
    print("scikit nmf")
    topic_info, scikit_nmf, tf_vectorizer = train_scikit_nmf_model(documents, NUMBER_OF_TOPICS, N_GRAM_N, NUMBER_OF_RUNS)
    """
    for el in topic_info:
        pprint(el)
    """
    print("Found " + str(len(topic_info)) + " stable topics")
    print_topic_info(topic_info, "nmf")

    print("\nMade models for "+ str(len(documents)) + " documents.")
if __name__ == '__main__':
    run_main()
