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


"""
Whether to remove document duplicates (and near-duplicates) in the data.
Recommended to do that, otherwise there is a risk that the topic modelling algorithm will find
these as topics
"""

REMOVE_DUPLICATES = True

"""
If two documents have a series of MIN_NGRAM_LENGTH_FOR_DUPLICATE tokens that are identical, these
documents are then cosidered as duplicates, and the longest one of these two documents is removed
"""
MIN_NGRAM_LENGTH_FOR_DUPLICATE = 8

def no_term_clustering(x, y):
    return False

def dummy(x, y): #only for debugging
    if x[0] == y[0]:
        return True
    else:
        return False

def simple_english_are_these_two_terms_considered_to_be_the_same(x, y):
    if (x[:-1] == y[:-1] or x[:-1] == y or x == y[:-1]) and len(x) > 3 and len(y) > 3:
        return True
    elif ((x[:-2] == y[:-2] and len(x) > 4 and len(y) > 4) or (x[:-2] == y and len(x) > 4) or (x == y[:-2]) and len(y) > 4) :
        return True
    else:
        return False

ARE_THESE_TWO_TERMS_CONSIDERED_TO_BE_THE_SAME = simple_english_are_these_two_terms_considered_to_be_the_same



def no_cleaning(text):

    return text

###
# Testing the default functionality
###
if __name__ == '__main__':
    print('simple_english_are_these_two_terms_considered_to_be_the_same("boat", "boats")', simple_english_are_these_two_terms_considered_to_be_the_same("boat", "boats"))
    print('simple_english_are_these_two_terms_considered_to_be_the_same("boats", "boat")', simple_english_are_these_two_terms_considered_to_be_the_same("boats", "boat"))
    print('simple_english_are_these_two_terms_considered_to_be_the_same("coats", "boat")', simple_english_are_these_two_terms_considered_to_be_the_same("coats", "boat"))
    print('simple_english_are_these_two_terms_considered_to_be_the_same("oat", "oats")', simple_english_are_these_two_terms_considered_to_be_the_same("oat", "oats"))
    print('simple_english_are_these_two_terms_considered_to_be_the_same("oats", "oat")', simple_english_are_these_two_terms_considered_to_be_the_same("oats", "oat"))
    print('simple_english_are_these_two_terms_considered_to_be_the_same("box", "boxes")', simple_english_are_these_two_terms_considered_to_be_the_same("box", "boxes"))
    print('simple_english_are_these_two_terms_considered_to_be_the_same("boxes", "box")', simple_english_are_these_two_terms_considered_to_be_the_same("boxes", "box"))

