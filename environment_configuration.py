import logging

WORKSPACE_FOLDER = "."
#Here, give a path to the folder where you have the directory 'data_folder', which contains your data
#For instance:
#WORKSPACE_FOLDER = "/Users/maria/mariaskeppstedtdsv/potsdam/visulizationideas/topic_modelling"

# The logging level
# Can be any of logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL
# If it's not given, logging.DEBUG will be used
LOGGING_LEVEL = logging.DEBUG

# The name of the database
# If it is not given, a default name will be used
DATABASE_NAME = "database_1"

# Whether it should be allowed to create new models
# If no value is given, the default value is that a model
# can be created

ALLOWED_TO_CREATE_MODEL = True


