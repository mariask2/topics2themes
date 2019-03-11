import os
from sklearn.feature_extraction import text

"""
from topics2themes.topic_model_constants import *
from topics2themes.word2vec_term_similarity import *
from topics2themes.environment_configuration import *
"""
from topic_model_constants import *
from word2vec_term_similarity import *
from environment_configuration import *



"""
Nr of topics to retrieve
"""
NUMBER_OF_TOPICS = 10


"""
The topic modelling algorithm is rerun with a decrease number of requested topics
until the number of found stable topics are similar to the ones requested
The amont of similarity is set here.
"""
#PROPORTION_OF_LESS_TOPIC_TO_ALLOW = 0.3
PROPORTION_OF_LESS_TOPIC_TO_ALLOW = 0.25

"""
Nr of words to display for each topic
"""
#NR_OF_TOP_WORDS = 10
NR_OF_TOP_WORDS = 30

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
NUMBER_OF_RUNS = 3


"""
Mininimum overlap of retrieved terms to considered the retrieved topic as
the same topic of a another one
"""
OVERLAP_CUT_OFF = 0.70


"""
Whether to use pre-processing (collocation detection and synonym clustering)
"""
#PRE_PROCESS = True
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
Search path to the vector space
"""
SPACE_FOR_PATH = "/Users/maria/mariaskeppstedtdsv/post-doc/gavagai/googlespace/GoogleNews-vectors-negative300.bin"

"""
Minimum proportion of documents that are to contain a term sequence for it to be counted as a collocation
"""
SIM_CUT_OFF = 0.6

#word2vec_s = Word2vecSimilarity(SPACE_FOR_PATH, SIM_CUT_OFF)
#ARE_THESE_TWO_TERMS_CONSIDERED_TO_BE_THE_SAME = word2vec_s.use_word2vec_for_determining_term_similarity

"""
The stop word file of user-defined stopiwords to use (Scikit learn stop words are also used)
"""
#STOP_WORD_FILE = "english_added.txt"
#STOP_WORD_FILE = "english_topic_specific_added.txt"
#STOP_WORD_FILE = "english_only_vaccine_added.txt"
STOP_WORD_FILE = "english_only_vaccine_added_nguyen_argumentaion_words.txt"



"""
The directories in which data is to be found. The data is to be in files with the ".txt" extension
in these directories. For each directory, there should also be a stance-label and a color associated with
the data
"""

DATA_LABEL_LIST = [{DATA_LABEL : "Pos", DIRECTORY_NAME : "for", LABEL_COLOR : GREEN },\
                   {DATA_LABEL : "Und", DIRECTORY_NAME : "uncertain", LABEL_COLOR : "#ccad00"},\
                   {DATA_LABEL : "Neg", DIRECTORY_NAME : "against", LABEL_COLOR : RED}]


"""
DATA_LABEL_LIST = [{DATA_LABEL : "for", DIRECTORY_NAME : "vaccination_constructed_data/for"},\
                   {DATA_LABEL : "undecided", DIRECTORY_NAME : "vaccination_constructed_data/uncertain"},\
                   {DATA_LABEL : "against", DIRECTORY_NAME : "vaccination_constructed_data/against"}]

"""
TOPIC_MODEL_ALGORITHM = NMF_NAME
#TOPIC_MODEL_ALGORITHM = LDA_NAME

"""
    If an extracted term includes less than this among the documents that are extracted, this term is removed from the set of extracted terms
    Synonym clustering is performed before the counting is done, so a rare term with synonyms is retained
    """
MIN_FREQUENCY_IN_COLLECTION_TO_INCLUDE_AS_TERM = 4

MAX_NR_OF_FEATURES = 10000

#STOP_WORD_SET = set(["many", "child", "kids", "parent", "types"])
STOP_WORD_SET = text.ENGLISH_STOP_WORDS

#SHOW_ARGUMENTATION = True

def digits_in_doc_id(doc_id):
    # Just for testing
    to_return = []
    for s in str(doc_id):
        if s  in  ["4", "5"]:
            to_return.append("Und")
        if s == "1":
            to_return.append("Dec")
        if s == "2":
            to_return.append("Hyp")
        if s == "6":
            to_return.append("Pre")
        if s == "7":
            to_return.append("Vol")
        if s == "8":
            to_return.append("Sou")
        if s == "9":
            to_return.append("Agr")
        else:
            to_return.append("Dis")
    return list(set(to_return))



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


"""
NO_MATCH = set(["polio", "measles", "measle", "chickenpox", "flu", "meningitis", "mumps", "pertussis", "capable",\
                "incapable", "likely", "unlikely", "black", "white",\
                "increase", "increased", "increases", "increasing", "boy", "girl",\
                "man", "mothers", "parents", "teenager", "toddler", "woman", "andrew",\
                "robert", "female", "negative", "positive", "forget", "remember",\
                "australia", "nz", "uk", "easier", "harder",\
                "awful", "bad", "big", "bigger", "considerable", "decent", "excellent", "fantastic",\
                "good", "great", "hideous", "horrible", "horrid", "huge", "lovely", "massive", "nice",\
                "significant", "smaller", "substantial", "terrible", "tremendous", "wonderful", "cheaper", "expensive"\
                "luckily", "sadly", "thankfully", "unfortunately", "high", "low", "agree", "disagree",\
                "adulthood", "puberty", "don", "large", "boys", "girls", "child", "children",
                "ah", "awfully", "btw", "certainly", "comprehend", "definitely", "dont", "eh",\
                "enormously", "er", "explain", "extremely", "fairly", "guess", "hey", "hugely", "huh",\
                "im", "incredibly", "knew", "know", "lol", "massively", "maybe", "obviously", "oh", "pretty" ,\
                "probably", "quite", "really", "relatively", "suppose", "surely", "tell", "telling", \
                "think", "thought", "tremendously", "uh", "understand", "ur", "wont", "yeah","adults", "kid", "kids",\
                "higher", "lower", "men", "women", "doctor", "doctors", "patient", "patients", "physicians",\
                "chicken_pox", "whooping_cough", "older", "younger", "flu_vaccine", "flu_vaccines", "smallpox_vaccine",\
                "days", "decade", "decades", "hour", "hours", "minute", "minutes", "month", "months", "week", "weeks", "year", "years",\
                "brother", "brothers", "cousin", "dad", "daughter", "daughters", "father", "grandmother", "mother", "siblings", "sister", "son",\
                "arabs", "palestine", "clinton", "hillary", "gop", "mccain", "obama", "repubs", "republican", "republicans",\
                "alex", "charles", "david", "davis", "henry", "jeff", "jeremy", "jim", "johnson", "micheal", "paul", "ryan", "steve", "wilson",\
                "croatia", "kosovo", "macedonia", "russians", "everybody", "usa", "pakistan"])
"""
"""
    Manually defined clusters (The format is not very user friendly, and could be improved)
"""
"""
MANUAL_MADE_DICT = {"increase" : "increase__increased__increases__increasing",\
    "increases" : "increase__increased__increases__increasing",\
        "increasing" : "increase__increased__increases__increasing",\
            "increased" : "increase__increased__increases__increasing",\
                "clinton" : "clinton_hillary",\
                "hillary" : "clinton_hillary",\
                "repubs" : "repubs_republican_republicans",\
                "republican" : "repubs_republican_republicans",\
                "republicans" : "repubs_republican_republicans",\
                "anybody" : "anybody_somebody",\
                "somebody" : "anybody_somebody",\
                "guy" : "guy_guys",\
                "guys" : "guy_guys",\
                "christian" : "christian_christianity_christians",\
                "christianity" : "christian_christianity_christians", \
                "christians" : "christian_christianity_christians",\
                "islam" : "islam_islamic_muslim_muslims",\
                "islamic" : "islam_islamic_muslim_muslims",\
                "muslim" : "islam_islamic_muslim_muslims",\
                "muslims" : "islam_islamic_muslim_muslims",\
                "canada" : "canada_canadian", \
                "canadian" : "canada_canadian", \
                "india" : "india_indian" , \
                "indian" : "india_indian" , \
                #"child" : "child__children__kid__kids",\
                #"children" : "child__children__kid__kids",\
                #"kid" : "child__children__kid__kids",\
                #"kids" : "child__children__kid__kids",\
                "awful": "awful__bad__hideous__horrible__horrid__terrible",\
                "bad": "awful__bad__hideous__horrible__horrid__terrible",\
                "hideous": "awful__bad__hideous__horrible__horrid__terrible",\
                "horrible" : "awful__bad__hideous__horrible__horrid__terrible",\
                "horrid" :"awful__bad__hideous__horrible__horrid__terrible",\
                "terrible": "awful__bad__hideous__horrible__horrid__terrible",\
                "big": "bigger__considerable__big__significant__substantial__huge",\
                "bigger": "bigger__considerable__big__significant__substantial__huge",\
                "considerable": "bigger__considerable__big__significant__substantial__huge",\
                "significant": "bigger__considerable__big__significant__substantial__huge",\
                "substantial": "bigger__considerable__big__significant__substantial__huge",\
                "huge": "bigger__considerable__big__significant__substantial__huge",\
                #"decent":  "decent__excellent__fantastic__good__great__lovely__nice__tremendous__wonderful",\
                #"excellent" : "decent__excellent__fantastic__good__great__lovely__nice__tremendous__wonderful",\
                #"fantastic" : "decent__excellent__fantastic__good__great__lovely__nice__tremendous__wonderful",\
                #"good" : "decent__excellent__fantastic__good__great__lovely__nice__tremendous__wonderful",\
                #"great":  "decent__excellent__fantastic__good__great__lovely__nice__tremendous__wonderful",\
                #"lovely":  "decent__excellent__fantastic__good__great__lovely__nice__tremendous__wonderful",\
                #"nice"  :"decent__excellent__fantastic__good__great__lovely__nice__tremendous__wonderful",\
                #"tremendous" : "decent__excellent__fantastic__good__great__lovely__nice__tremendous__wonderful",\
                #"wonderful"  :"decent__excellent__fantastic__good__great__lovely__nice__tremendous__wonderful",\
                #"luckily": "luckily__thankfully",\
                #"thankfully": "luckily__thankfully",\
                #"sadly" : "sadly__unfortunately",\
                #"unfortunately" : "sadly__unfortunately",\
                "doctor":"doctor__doctors__physicians",\
                "doctors":"doctor__doctors__physicians",\
                "physicians":"doctor__doctors__physicians",\
                "patient":"patient__patients",\
                "patients":"patient__patients",\
            }
"""


