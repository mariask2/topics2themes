"""
Constanst to use in general
"""


"""
Note: Don't use NMF (instead of NMF_NAME, since it will be name conflicts)
"""

NMF_NAME = "NMF"
LDA_NAME = "LDA"

"""
    Keys for data label and directory name corresponding to the data label
    """
DATA_LABEL = "data_label"
DIRECTORY_NAME = "directory_name"

# Where to look for the data sets
DATA_FOLDER = "data_folder"

# Where to start looking for the data
# TODO: Make this better configurable
DEFAULT_ROOT_DIRECTORY = "."

# Where to save the constructed models (shouldn't be used anymore)
PATH_TOPIC_MODEL_OUTPUT = "topic_modelling_data"

# The name of the file where the configuration is saved
CONFIGURATION_FILE_NAME = "topic_model_configuration"

# How to signal that two words are synoyms
SYNONYM_BINDER = "__"

####
## Database dictionary keys
####
META_DATA = "meta_data"
MODEL_NAME = "model_name"
DOCUMENTS = "documents"
TOPICS    = "topics"
TEXT = "text"
ID_SOURCE = "id_source"

###
# To display the labels
####
LABEL_COLOR = "label_color"

RED = "#8A0808"
GREEN = "#0B6121"
SILVER = "#C0C0C0"

