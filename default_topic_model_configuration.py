from topic_model_constants import *


"""
Nr of topics to retrieve
"""
NUMBER_OF_TOPICS = 10

"""
    The topic modelling algorithm is rerun with a decrease number of requested topics
    until the number of found stable topics are similar to the ones requested
    The amont of similarity is set here. 1 means that no re-runs to find the right amount of
    topics are carried out (resutling in that more and less stable topics are found). 0 means that the number of requested topics has to be the same as
    the number of found topics, and that the requested topics are increased until that happends (resulting in fewer and more stable topics).
    """
PROPORTION_OF_LESS_TOPIC_TO_ALLOW = 1

"""
Nr of words to display for each topic
"""
NR_OF_TOP_WORDS = 50


"""
Nr of most typical document to retrieve for each topic
"""
NR_OF_TOP_DOCUMENTS = 50

"""
Number of runs to check the stability of the retrieved topics.
Only topics that occur in all NUMBER_OF_RUNS runs will be
considered valid
"""
NUMBER_OF_RUNS = 10

"""
Mininimum overlap of retrieved terms to considered the retrieved topic as
the same topic of a another one
"""
OVERLAP_CUT_OFF = 0.7

"""
Whether to use pre-processing (collocation detection and synonym clustering)
"""
PRE_PROCESS = False


"""
Mininimum occurrence in the corpus for a term to be included in the topic modelling
"""
MIN_DOCUMENT_FREQUENCY = 3

"""
Maximum occurrence in the corpus for a term to be included in the topic modelling
"""
MAX_DOCUMENT_FREQUENCY = 0.95


"""
Minimum proportion of documents that are to contain a term sequence for it to be counted as a collocation
"""
COLLOCATION_CUT_OFF = 0.005


TOPIC_MODEL_ALGORITHM = NMF_NAME




def no_cleaning(text):

    return text


