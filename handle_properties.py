import importlib
import argparse
import os

from topic_model_constants import *

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

    data_directory = "."
    if not args.data_directory:
        print("The argument '--data_directory' not given. Will use the current directory")
    else:
        data_directory = args.data_directory
    
    print(args.project_path)
    return load_properties_from_parameters(args.project_path, data_directory)


def load_properties_from_parameters(project_path, start_dir = "."):
    if start_dir != ".":
        sys.path.append(start_dir)
    path_slash_format = ""
    for path_part in project_path.split("."):
        path_slash_format = os.path.join(path_slash_format, path_part)
    
    path_slash_format = os.path.join(start_dir, path_slash_format)

    print("path_slash_format", path_slash_format)
    if not os.path.exists(path_slash_format):
        raise FileNotFoundError("The directory '" + str(path_slash_format) + "' i.e., the directory matching the project path given '" + \
                            str(project_path) + "', does not exist")
        
        
    if not os.path.exists(os.path.join(path_slash_format, CONFIGURATION_FILE_NAME + ".py")):
        raise FileNotFoundError("The directory '" + str(path_slash_format) + "' does not have a " + CONFIGURATION_FILE_NAME + ".py file.")


    properties = importlib.import_module(project_path + "." + CONFIGURATION_FILE_NAME)

    #properties_container = PropertiesContainer(properties) # Copied from pal, perhaps this will be needed here also
    return properties, path_slash_format, project_path

