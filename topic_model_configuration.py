


"""
Nr of topics to retrieve
"""
NUMBER_OF_TOPICS = 10


"""
Nr of words to display for each topic
"""
#NR_OF_TOP_WORDS = 50
NR_OF_TOP_WORDS = 10

"""
Nr of most typical document to retrieve for each topic
"""
#NR_OF_TOP_DOCUMENTS = 50
NR_OF_TOP_DOCUMENTS = 20

"""
Number of runs to check the stability of the retrieved topics.
Only topics that occur in all NUMBER_OF_RUNS runs will be
considered valid
"""
NUMBER_OF_RUNS = 2

"""
Mininimum overlap of retrieved terms to considered the retrieved topic as
the same topic of a another one
"""
OVERLAP_CUT_OFF = 0.7

"""
Whether to use pre-processing (collocation detection and synonym clustering)
"""
PRE_PROCESS = True

"""
Mininimum occurrence in the corpus for a term to be included in the topic modelling
"""
MIN_DOCUMENT_FREQUENCY = 3

"""
Maximum occurrence in the corpus for a term to be included in the topic modelling
"""
MAX_DOCUMENT_FREQUENCY = 0.95

"""
Search path to the vector space
"""
SPACE_FOR_PATH = "/Users/maria/mariaskeppstedtdsv/post-doc/gavagai/googlespace/GoogleNews-vectors-negative300.bin"


"""
Minimum proportion of documents that are to contain a term sequence for it to be counted as a collocation
"""
COLLOCATION_CUT_OFF = 0.005

"""
Length of the word2vec vectors
"""
VECTOR_LENGTH = 300

"""
The stop word file of user-defined stopiwords to use (Scikit learn stop words are also used)
"""
STOP_WORD_FILE = "english_added.txt"

"""
The directories in which data is to be found. The data is to be in files with the ".txt" extension 
in these directories. For each directory, there should also be a stance-label associated with
the data
"""
DATA_LABEL = "data_label"
DIRECTORY_NAME = "directory_name"

DATA_LABEL_LIST = [{DATA_LABEL : "for", DIRECTORY_NAME : "mumsnet_scikitformat/for"},\
                   {DATA_LABEL : "undecided", DIRECTORY_NAME : "mumsnet_scikitformat/uncertain"},\
                   {DATA_LABEL : "against", DIRECTORY_NAME : "mumsnet_scikitformat/against"}]


def corpus_specific_text_cleaning(text):
    """
    For performing corpus specific cleaning. Added to this file, since it needs to be adapted to the corpus and therefore a kind of configuration
    """
    text = text.replace('"full_text" : ', "").strip().replace('"', '').replace('\\n*', ' ').replace('\\', ' ').replace('&amp', ' ').replace("'ve", ' have')
    text = text.replace("don't", 'do not').replace("doesn't", 'does not').replace("Don't", 'Do not').replace("Doesn't", 'Does not')
    text = text.replace("_NEWLINE_", " ").replace("_CITATION_PREVIOUS_POST_PARAGRAPH", " ").replace("_CITATION_PREVIOUS_POST_", " ").replace("_POSTER_", " ")
    no_links = []
    for word in text.split(" "):
        if "//" not in word and "http" not in word and "@" not in word:
            no_links.append(word)
    cleaned_text = " ".join(no_links)
    return cleaned_text
