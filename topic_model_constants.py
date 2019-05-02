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

# Where to save the constructed models (shouldn't be used anymore)
PATH_TOPIC_MODEL_OUTPUT = "topic_modelling_data"

# The name of the file where the configuration is saved
CONFIGURATION_FILE_NAME = "topic_model_configuration"

# How to signal that two words are synoyms
SYNONYM_BINDER = "__"

COLLOCATION_BINDER = "_"

# Export and import data

EXPORT_DIR = "topics2themes_exports_folder_created_by_system"
####
## Database dictionary keys
####
META_DATA = "meta_data"
MODEL_NAME = "model_name"
DOCUMENTS = "documents"
TOPICS    = "topics"
TEXT = "text"
ID_SOURCE = "id_source"
THEME_NAME = "theme_name"
DOCUMENT_ID = "document_ids"
THEME_NUMBER = "theme_number"
DOCUMENT_TOPICS = "document_topics"
TOPIC_INDEX = "topic_index"
###
# To display the labels
####
LABEL_COLOR = "label_color"

RED = "#8A0808"
GREEN = "#0B6121"
SILVER = "#C0C0C0"

KEY_FILE_NAME = "approved_keys.txt"
