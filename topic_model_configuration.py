


"""
Nr of topics to retrieve
"""
NUMBER_OF_TOPICS = 10

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
NUMBER_OF_RUNS = 2

"""
Mininimum overlap of retrieved terms to considered the retrieved topic as
the same topic of a another one
"""
OVERLAP_CUT_OFF = 0.7


"""
Mininimum occurrence in the corpus for a term to be included in the topic modelling
"""
MIN_DOCUMENT_FREQUENCY = 3

"""
Search path to the vector space
"""
SPACE_FOR_PATH = "/Users/maria/mariaskeppstedtdsv/post-doc/gavagai/googlespace/GoogleNews-vectors-negative300.bin"


"""
The stop word file of user-defined stopiwords to use (Scikit learn stop words are also used)
"""
STOP_WORD_FILE = "english_added.txt"
