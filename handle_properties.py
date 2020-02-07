import importlib
import argparse
import os
import sys

# An import that should function both locally and when running an a remote server
try:
    from environment_configuration import *
except:
    from topics2themes.environment_configuration import *



if RUN_LOCALLY:
    from topic_model_constants import *
    import default_topic_model_configuration
else:
    from topics2themes.topic_model_constants import *
    import topics2themes.default_topic_model_configuration as default_topic_model_configuration

#TODO: Test that default properties work

class PropertiesContainer:
    """
    PropertiesContainer

    A class containing the properties needed to make a topic model, 
    and for checking the that properties are given.
    """

    def __init__(self, properties):
        """
        :params properties: a python model including properties (retrieved by importlib.import_module(<PATH>))
        """
        
        try:
            self.NUMBER_OF_TOPICS = properties.NUMBER_OF_TOPICS
        except AttributeError:
            self.NUMBER_OF_TOPICS = default_topic_model_configuration.NUMBER_OF_TOPICS
            print("Using default NUMBER_OF_TOPICS")
        try:    
            self.NR_OF_TOP_WORDS = properties.NR_OF_TOP_WORDS
        except AttributeError:    
            self.NR_OF_TOP_WORDS = default_topic_model_configuration.NR_OF_TOP_WORDS
            print("Using default NR_OF_TOP_WORDS")

        try:    
            self.NR_OF_TOP_DOCUMENTS = properties.NR_OF_TOP_DOCUMENTS
        except AttributeError:
            self.NR_OF_TOP_DOCUMENTS = default_topic_model_configuration.NR_OF_TOP_DOCUMENTS
            print("Using default NR_OF_TOP_DOCUMENTS")

        try:    
            self.NUMBER_OF_RUNS = properties.NUMBER_OF_RUNS
        except AttributeError:
            self.NUMBER_OF_RUNS = default_topic_model_configuration.NUMBER_OF_RUNS
            print("Using default NUMBER_OF_RUNS")
        try:
            self.OVERLAP_CUT_OFF = properties.OVERLAP_CUT_OFF
        except AttributeError:
            self.OVERLAP_CUT_OFF = default_topic_model_configuration.OVERLAP_CUT_OFF
            print("Using default OVERLAP_CUT_OFF")

        try:    
            self.PRE_PROCESS = properties.PRE_PROCESS
        except AttributeError:
            self.PRE_PROCESS = default_topic_model_configuration.PRE_PROCESS
            print("Using default PRE_PROCESS")

        try:    
            self.MIN_DOCUMENT_FREQUENCY = properties.MIN_DOCUMENT_FREQUENCY
        except AttributeError:
            self.MIN_DOCUMENT_FREQUENCY = default_topic_model_configuration.MIN_DOCUMENT_FREQUENCY
            print("Using default MIN_DOCUMENT_FREQUENCY ")
            
        try:    
            self.MAX_DOCUMENT_FREQUENCY = properties.MAX_DOCUMENT_FREQUENCY
        except AttributeError:
            self.MAX_DOCUMENT_FREQUENCY = default_topic_model_configuration.MAX_DOCUMENT_FREQUENCY
            print("Using default MAX_DOCUMENT_FREQUENCY ")
        
        try:
            self.SPACE_FOR_PATH = properties.SPACE_FOR_PATH
        except AttributeError as a:
            if self.PRE_PROCESS:
                print("The configuration variable SPACE_FOR_PATH is not set. Either give the path to a word2vec space, or set PRE_PROCESS to false")
                logging.error("The configuration variable SPACE_FOR_PATH is not set. Either give the path to a word2vec space, or set PRE_PROCESS to false")
                raise(a)
        try:
            self.VECTOR_LENGTH = properties.VECTOR_LENGTH
        except AttributeError as a:
            if self.PRE_PROCESS:
                print("The configuration variable VECTOR_LENGTH is not set. Either give the a word2vec space vectorlengt, or set PRE_PROCESS to false")
                logging.error("The configuration variable VECTOR_LENGTH is not set. Either give the a word2vec space vectorlengt, or set PRE_PROCESS to false")
                raise(a)

        try:
            self.STOP_WORD_FILE = properties.STOP_WORD_FILE
        except AttributeError as a:
            print("No STOP_WORD_FILE is given in the configuration file.")
            logging.error("No STOP_WORD_FILE is given in the configuration file.")
            raise(a)

        try:
            self.DATA_LABEL_LIST = properties.DATA_LABEL_LIST
        except AttributeError as a:
            print("No DATA_LABEL_LIST is given in the configuration file.")
            logging.error("No DATA_LABEL_LIST is given in the configuration file.")
            raise(a)
            
        try:
            self.COLLOCATION_CUT_OFF = properties.COLLOCATION_CUT_OFF
        except AttributeError:
            self.COLLOCATION_CUT_OFF= default_topic_model_configuration.COLLOCATION_CUT_OFF
            print("Using default COLLOCATION_CUT_OFF")

        try:  
            self.TOPIC_MODEL_ALGORITHM = properties.TOPIC_MODEL_ALGORITHM
        except AttributeError: 
            self.TOPIC_MODEL_ALGORITHM = default_topic_model_configuration.TOPIC_MODEL_ALGORITHM
            print("Using default TOPIC_MODEL_ALGORITHM")

        try:  # TODO: incosistent notation, should use CLEANING_METHOD in properties file also
            self.CLEANING_METHOD = properties.CLEANING_METHOD
        except AttributeError: 
            self.CLEANING_METHOD = default_topic_model_configuration.CLEANING_METHOD
            print("Using default CLEANING_METHOD which removes HTML tags")

        try:
            self.PROPORTION_OF_LESS_TOPIC_TO_ALLOW = properties.PROPORTION_OF_LESS_TOPIC_TO_ALLOW
        except AttributeError:
            self.PROPORTION_OF_LESS_TOPIC_TO_ALLOW = default_topic_model_configuration.PROPORTION_OF_LESS_TOPIC_TO_ALLOW

        try:
            self.REMOVE_DUPLICATES = properties.REMOVE_DUPLICATES
        except AttributeError:
            self.REMOVE_DUPLICATES = default_topic_model_configuration.REMOVE_DUPLICATES

        # TODO: Make an int and float conversion for all propoerties, to get type control for user input properies
        try:
            self.MIN_NGRAM_LENGTH_FOR_DUPLICATE = int(properties.MIN_NGRAM_LENGTH_FOR_DUPLICATE)
        except AttributeError:
            self.MIN_NGRAM_LENGTH_FOR_DUPLICATE = int(default_topic_model_configuration.MIN_NGRAM_LENGTH_FOR_DUPLICATE)

        try:
            self.ARE_THESE_TWO_TERMS_CONSIDERED_TO_BE_THE_SAME = properties.ARE_THESE_TWO_TERMS_CONSIDERED_TO_BE_THE_SAME
        except AttributeError:
            self.ARE_THESE_TWO_TERMS_CONSIDERED_TO_BE_THE_SAME = default_topic_model_configuration.ARE_THESE_TWO_TERMS_CONSIDERED_TO_BE_THE_SAME

        try:
            self.ADDITIONAL_LABELS_METHOD = properties.ADDITIONAL_LABELS_METHOD
        except AttributeError:
            self.ADDITIONAL_LABELS_METHOD = default_topic_model_configuration.ADDITIONAL_LABELS_METHOD

        try:
            self.MAX_NR_OF_FEATURES = properties.MAX_NR_OF_FEATURES
        except AttributeError:
            self.MAX_NR_OF_FEATURES = default_topic_model_configuration.MAX_NR_OF_FEATURES
                
        try:
            self.SHOW_ARGUMENTATION = properties.SHOW_ARGUMENTATION
        except AttributeError:
            self.SHOW_ARGUMENTATION = default_topic_model_configuration.SHOW_ARGUMENTATION
        
        try:
            self.SHOW_SENTIMENT = properties.SHOW_SENTIMENT
        except AttributeError:
            self.SHOW_SENTIMENT = default_topic_model_configuration.SHOW_SENTIMENT


        try:
            self.STOP_WORD_SET = properties.STOP_WORD_SET
        except AttributeError:
            self.STOP_WORD_SET = default_topic_model_configuration.STOP_WORD_SET

        try:
            self.MAX_DIST_FOR_CLUSTERING = properties.MAX_DIST_FOR_CLUSTERING
        except AttributeError:
            self.MAX_DIST_FOR_CLUSTERING = default_topic_model_configuration.MAX_DIST_FOR_CLUSTERING
                
        try:
            self.WORDS_NOT_TO_INCLUDE_IN_CLUSTERING_FILE = properties.WORDS_NOT_TO_INCLUDE_IN_CLUSTERING_FILE
        except AttributeError:
            print("No file specified for cluster exceptions")
            self.WORDS_NOT_TO_INCLUDE_IN_CLUSTERING_FILE = None # Then all words are included in clustering
        try:
            self.MANUAL_CLUSTER_FILE = properties.MANUAL_CLUSTER_FILE
        except AttributeError:
            print("No file specified with manually constructed clusters")
            self.MANUAL_CLUSTER_FILE = None # Then no manually constructed clusters will be used

        try:
            self.BINARY_SPACE = properties.BINARY_SPACE
        except AttributeError:
            self.BINARY_SPACE = default_topic_model_configuration.BINARY_SPACE

        try:
            self.GENSIM_FORMAT = properties.GENSIM_FORMAT
        except AttributeError:
            self.GENSIM_FORMAT = default_topic_model_configuration.GENSIM_FORMAT


    def get_properties_in_json(self):
        """
        Returns properties in json format
        """
        dict = {}
        
        dict["NUMBER_OF_TOPICS"] = self.NUMBER_OF_TOPICS
        dict["NR_OF_TOP_WORDS"] = self.NR_OF_TOP_WORDS
        dict["NR_OF_TOP_DOCUMENTS"] = self.NR_OF_TOP_DOCUMENTS
        dict["NR_OF_TOP_DOCUMENTS"] = self.NR_OF_TOP_DOCUMENTS
        dict["NUMBER_OF_RUNS"] = self.NUMBER_OF_RUNS
        dict["OVERLAP_CUT_OFF"] = self.OVERLAP_CUT_OFF
        dict["PRE_PROCESS"] = self.PRE_PROCESS
        dict["MIN_DOCUMENT_FREQUENCY"] = self.MIN_DOCUMENT_FREQUENCY
        dict["MAX_DOCUMENT_FREQUENCY"] = self.MAX_DOCUMENT_FREQUENCY
        try:
            dict["SPACE_FOR_PATH"] = self.SPACE_FOR_PATH
        except AttributeError:
            pass
        try:
             dict["VECTOR_LENGTH"] = self.VECTOR_LENGTH
        except AttributeError:
            pass

        dict["DATA_LABEL_LIST"] = self.DATA_LABEL_LIST
            
        dict["COLLOCATION_CUT_OFF"] = self.COLLOCATION_CUT_OFF

        dict["TOPIC_MODEL_ALGORITHM"] = self.TOPIC_MODEL_ALGORITHM
        
        dict["CLEANING_METHOD"] = str(self.CLEANING_METHOD) 
        
        # TODO: This is not complete

        return dict
    
def load_properties(parser):
 
    
    parser.add_argument('--project', action='store', dest='project_path', \
                        help='The path, separated by dots, to where the project i located. For instance: data.example_project')
    parser.add_argument('--data_directory', action='store', dest='data_directory', \
                                            help="The path, separated by slash, for the root of the data "\
                                            + DATA_FOLDER + " is located.")
                        
    args = parser.parse_args()
    if not args.project_path:
        print("The argument '--project' with the path to the data needs to be given")
        exit(1)

    """
    data_directory = "."
    if not args.data_directory:
        print("The argument '--data_directory' not given. Will use the current directory")
    else:
        data_directory = args.data_directory
    """
    print(args.project_path)
    return load_properties_from_parameters(args.project_path)


def load_properties_from_parameters(project_path):
    
    sys.path.append(WORKSPACE_FOLDER)
    
    path_slash_format = ""
    for path_part in project_path.split("."):
        path_slash_format = os.path.join(path_slash_format, path_part)
    
    path_slash_format = os.path.join(WORKSPACE_FOLDER, path_slash_format)

    print("path_slash_format", path_slash_format)

    if not os.path.exists(path_slash_format):
        raise FileNotFoundError("The directory '" + str(path_slash_format) + "' i.e., the directory matching the project path given '" + \
                            str(project_path) + "', does not exist")
        
        
    if not os.path.exists(os.path.join(path_slash_format, CONFIGURATION_FILE_NAME + ".py")):
        raise FileNotFoundError("The directory '" + str(path_slash_format) + "' does not have a " + CONFIGURATION_FILE_NAME + ".py file.")


    properties = importlib.import_module(project_path + "." + CONFIGURATION_FILE_NAME)

    properties_container = PropertiesContainer(properties) # Copied from pal, perhaps this will be needed here also
    return properties_container, path_slash_format, project_path

