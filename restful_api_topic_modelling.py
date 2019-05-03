from flask import Flask, jsonify, abort, make_response, request, json, request, current_app
import sys
import os
import traceback
import linecache
import logging
from datetime import timedelta
from functools import update_wrapper
from flask import send_from_directory

# An import that should function both locally and when running an a remote server
try:
    from environment_configuration import *
except:
    from topics2themes.environment_configuration import *


if RUN_LOCALLY:
    from flask_cors import CORS
    import make_topic_models
    from mongo_connector import MongoConnector
    from theme_sorter import ThemeSorter
    from topic_model_constants import *
else:
    import topics2themes.make_topic_models as make_topic_models
    from topics2themes.mongo_connector import MongoConnector
    from topics2themes.theme_sorter import ThemeSorter
    from topics2themes.environment_configuration import *
    from topics2themes.topic_model_constants import *


app = Flask(__name__)

if RUN_LOCALLY:
    CORS(app)
else:
    app.config['MONGO_CONNECT'] = False

try:
    mongo_con = MongoConnector()
except:
    e = sys.exc_info()
    print("The following error occurred: ")
    print(e)
    print("The pymongo database might not be running")
    mongo_con = MongoConnector()
    exit(1)

theme_sort = ThemeSorter(mongo_con)

# To not have a lot of space in the output
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

def get_more_exception_info():
    trace_back = traceback.format_exc()
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    all_info = str(exc_obj) + str(trace_back)
    return 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), all_info)

def get_exception_info(e, extra_log_file = None):
    more = get_more_exception_info()
    logging.error("\nTOPICS2THEMES ERROR: " + str(e))
    logging.error("TOPICS2THEMES ERROR: " + more)
    print(e)
    print(more)
    resp = make_response(jsonify({'error' : str(e) + " " + more}), 400)
    return resp

def get_port():
    if len(sys.argv) < 2:
        sys.exit("As an argument to the script, you need to give the port at which you are listening,"\
                 + " for instance 5000")
    current_port = int(sys.argv[1])
    print("Will start up server to listen at port " + str(current_port))
    return current_port


def load_keys(approved_keys, key_file_name):
    try:
        f = open(os.path.join(WORKSPACE_FOLDER, key_file_name))
        lines = f.readlines()
        f.close()
        
        if len(lines) == 0 or (len(lines) == 1 and lines[0].strip() == ""):
            print("\nYour file '" + key_file_name + " in your WORKSPACE_FOLDER, i.e. in " + WORKSPACE_FOLDER + "\nis empty. This file should contain user keys (that you choose), one line for each approved key. When the user then uses the web interface, the user will be prompted to provide a key file, and the user needs to give a key that it contained in your " + key_file_name + " to be allowed to use the tool.\n")
            raise LookupError()
        
        for line in lines:
            approved_keys.append(line.strip())

    except FileNotFoundError as e:
        print("\nYou need to create a file called '" + key_file_name + " in your WORKSPACE_FOLDER, i.e. in " + WORKSPACE_FOLDER + "\nThis file should contain user keys (that you choose), one line for each approved key. When the user then uses the web interface, the user will be prompted to provide a key file, and the user needs to give a key that it contained in your " + key_file_name + " to be allowed to use the tool.\n")
        raise(e)

def authenticate():
    key = request.values.get("authentication_key")
    if key not in APPROVED_KEYS:
        abort(403)

@app.route('/topics2themes/api/v1.0/can_model_be_created', methods=['GET', 'POST'])
def can_model_be_created():
    try:
        authenticate()
        can_be_created = make_topic_models.can_model_be_created()
        resp = make_response(jsonify({"result" : can_be_created}))
        return resp
    except Exception as e:
        return get_exception_info(e)


@app.route('/topics2themes/api/v1.0/get_data_sets', methods=['GET', 'POST'])
def get_data_sets():
    try:
        authenticate()
        data_sets = make_topic_models.get_sets_in_data_folder()
        resp = make_response(jsonify({"result" : data_sets}))
        return resp
    except Exception as e:
        return get_exception_info(e)


@app.route('/topics2themes/api/v1.0/get_all_models_for_collection_with_name', methods=['GET', 'POST'])
def get_all_models_for_collection_with_name():
    try:
        authenticate()
        collection_name = request.values.get("collection_name")
        all_models_for_collection_with_name = mongo_con.get_all_models_for_collection_with_name(collection_name)
        resp = make_response(jsonify({"result" : all_models_for_collection_with_name}))
        return resp
    except Exception as e:
        return get_exception_info(e)

@app.route('/topics2themes/api/v1.0/make_model_for_collection', methods=['GET', 'POST'])
def make_model_for_collection():
    try:
        authenticate()
        collection_name = request.values.get("collection_name")
        model_name = request.values.get("model_name")
        if ALLOWED_TO_CREATE_MODEL:
            model_result = make_topic_models.make_model_for_collection(collection_name, model_name, mongo_con)
        else:
            model_result = mongo_con.load_model_from_file(model_name, collection_name)
        
        resp = make_response(jsonify({"result" : model_result}))
        return resp
    except Exception as e:
        return get_exception_info(e)


@app.route('/topics2themes/api/v1.0/update_topic_name', methods=['GET', 'POST'])
def update_topic_name():
    try:
        authenticate()
        topic_id = request.values.get("topic_id")
        topic_name = request.values.get("topic_name")
        analysis_id = request.values.get("analysis_id")
        topic_name_update_result =  mongo_con.save_or_update_topic_name(topic_id, topic_name, analysis_id)
        resp = make_response(jsonify({"result" : "topic name updated"}))
        return resp
    except Exception as e:
        return get_exception_info(e)


@app.route('/topics2themes/api/v1.0/update_user_defined_label', methods=['GET', 'POST'])
def update_user_defined_label():
    try:
        authenticate()
        text_id = request.values.get("text_id")
        user_defined_label = request.values.get("user_defined_label")
        analysis_id = request.values.get("analysis_id")
        user_defined_label_result =  mongo_con.save_or_update_user_defined_label(text_id, user_defined_label, analysis_id)
        resp = make_response(jsonify({"result" : user_defined_label_result}))
        return resp
    except Exception as e:
        return get_exception_info(e)



@app.route('/topics2themes/api/v1.0/get_model_for_model_id', methods=['GET', 'POST'])
def get_model_for_model_id():
    try:
        authenticate()
        model_id = request.values.get("model_id")
        model =  mongo_con.get_model_for_model_id(model_id)
        resp = make_response(jsonify({"result" : model}))
        return resp
    except Exception as e:
        return get_exception_info(e)



@app.route('/topics2themes/api/v1.0/get_all_topic_names', methods=['GET', 'POST'])
def get_all_topic_names():
    try:
        authenticate()
        analysis_id = request.values.get("analysis_id")
        all_topic_names =  mongo_con.get_all_topic_names(analysis_id)
        resp = make_response(jsonify({"result" : all_topic_names}))
        return resp
    except Exception as e:
        return get_exception_info(e)


@app.route('/topics2themes/api/v1.0/get_all_user_defined_labels', methods=['GET', 'POST'])
def get_all_user_defined_labels():
    try:
        authenticate()
        analysis_id = request.values.get("analysis_id")
        all_user_defined_labels =  mongo_con.get_all_user_defined_labels(analysis_id)
        resp = make_response(jsonify({"result" : all_user_defined_labels}))
        return resp
    except Exception as e:
        return get_exception_info(e)




@app.route('/topics2themes/api/v1.0/create_new_analysis', methods=['GET', 'POST'])
def create_new_analysis():
    try:
        authenticate()
        model_id = request.values.get("model_id")
        analysis_name = request.values.get("analysis_name")
        created_analysis =  mongo_con.create_new_analysis(model_id, analysis_name)
        resp = make_response(jsonify({"result" : created_analysis}))
        return resp
    except Exception as e:
        return get_exception_info(e)


@app.route('/topics2themes/api/v1.0/get_all_analyses_for_model', methods=['GET', 'POST'])
def get_all_analyses_for_model():
    try:
        authenticate()
        model_id = request.values.get("model_id")
        analyses =  mongo_con.get_all_analyses_for_model(model_id)
        resp = make_response(jsonify({"result" : analyses}))
        return resp
    except Exception as e:
        return get_exception_info(e)


@app.route('/topics2themes/api/v1.0/create_new_theme', methods=['GET', 'POST'])
def create_new_theme():
    try:
        authenticate()
        analysis_id = request.values.get("analysis_id")
        new_theme_id =  mongo_con.create_new_theme(analysis_id)
        resp = make_response(jsonify({"result" : new_theme_id}))
        return resp
    except Exception as e:
        return get_exception_info(e)


@app.route('/topics2themes/api/v1.0/delete_theme', methods=['GET', 'POST'])
def delete_theme():
    try:
        authenticate()
        analysis_id = request.values.get("analysis_id")
        theme_number = request.values.get("theme_number")
        nr_of_deleted_themes =  mongo_con.delete_theme(analysis_id, theme_number)
        resp = make_response(jsonify({"result" : nr_of_deleted_themes}))
        return resp
    except Exception as e:
        return get_exception_info(e)


@app.route('/topics2themes/api/v1.0/get_saved_themes', methods=['GET', 'POST'])
def get_saved_themes():
    try:
        authenticate()
        analysis_id = request.values.get("analysis_id")
        new_theme_id =  mongo_con.get_saved_themes(analysis_id)
        resp = make_response(jsonify({"result" : new_theme_id}))
        return resp
    except Exception as e:
        return get_exception_info(e)


@app.route('/topics2themes/api/v1.0/update_theme_name', methods=['GET', 'POST'])
def update_theme_name():
    try:
        authenticate()
        theme_id = request.values.get("theme_number")
        theme_name = request.values.get("theme_name")
        analysis_id = request.values.get("analysis_id")
        theme_name_update_result =  mongo_con.update_theme_name(theme_id, theme_name, analysis_id)
        resp = make_response(jsonify({"result" : theme_name_update_result}))
        return resp
    except Exception as e:
        return get_exception_info(e)


@app.route('/topics2themes/api/v1.0/add_theme_document_connection', methods=['GET', 'POST'])
def add_theme_document_connection():
    try:
        authenticate()
        theme_id = request.values.get("theme_number")
        document_id = request.values.get("document_id")
        analysis_id = request.values.get("analysis_id")
        theme_document_connection_result =  mongo_con.add_theme_document_connection(theme_id, document_id, analysis_id)
        theme_sort.retrain_model(analysis_id)
        resp = make_response(jsonify({"result" : theme_document_connection_result}))
        return resp
    except Exception as e:
        return get_exception_info(e)


@app.route('/topics2themes/api/v1.0/delete_theme_document_connection', methods=['GET', 'POST'])
def delete_theme_document_connection():
    try:
        authenticate()
        theme_id = request.values.get("theme_number")
        document_id = request.values.get("document_id")
        analysis_id = request.values.get("analysis_id")
        theme_document_connection_result =  mongo_con.delete_theme_document_connection(theme_id, document_id, analysis_id)
        theme_sort.retrain_model(analysis_id)
        resp = make_response(jsonify({"result" : theme_document_connection_result}))
        return resp
    except Exception as e:
        return get_exception_info(e)


@app.route('/topics2themes/api/v1.0/get_theme_ranking_for_document', methods=['GET', 'POST'])
def get_theme_ranking_for_document():
    try:
        authenticate()
        document_id = request.values.get("document_id")
        analysis_id = request.values.get("analysis_id")
        ranked_themes = theme_sort.rank_themes_for_document(analysis_id, document_id)
        resp = make_response(jsonify({"result" : ranked_themes}))
        return resp
    except Exception as e:
        return get_exception_info(e)


@app.route('/topics2themes/api/v1.0/export_analysis', methods=['GET', 'POST'])
def export_analysis():
    try:
        authenticate()
        analysis_id = request.values.get("analysis_id")
        data_dir =  mongo_con.save_analysis_to_file_for_analysis_id(analysis_id)
        saved_data = {"analysis_id": analysis_id, "data_dir" : data_dir}
        resp = make_response(jsonify({"result" : saved_data}))
        return resp
    except Exception as e:
        return get_exception_info(e)



@app.route('/topics2themes/')
def start_page():
    return send_from_directory("user_interface", "index.html")

@app.route('/topics2themes/js/<filename>')
def js_files(filename):
    return send_from_directory("user_interface/js", filename)

@app.route('/topics2themes/css/<filename>')
def css_files(filename):
    return send_from_directory("user_interface/css", filename)

@app.route('/topics2themes/fonts/<filename>')
def fonts_files(filename):
    return send_from_directory("user_interface/fonts", filename)



APPROVED_KEYS = []
FILE = open("log_file.txt", "w")
load_keys(APPROVED_KEYS, KEY_FILE_NAME)

if __name__ == '__main__':
    logging_level_to_use = None
    try:
        if LOGGING_LEVEL not in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]:
            logging_level_to_use = logging.DEBUG
            print("Using default logging level " + str(logging.DEBUG))
        else:
            logging_level_to_use = LOGGING_LEVEL
    except:
        logging_level_to_use = logging.DEBUG
        print("Using default logging level " + str(logging.DEBUG))

    logging.basicConfig(filename=os.path.join(WORKSPACE_FOLDER, 'topics2themes_log.log'),level=logging_level_to_use)
    logging.info("TOPICS2THEMES: ******** Starting Topics2Themes server ***************")
    current_port = get_port()
    logging.info("TOPICS2THEMES: ******** Listning to port " + str(current_port) + " ***************")

    if RUN_LOCALLY:
        print("You have specified in 'environment_configuration.py' to run Topics2Themes on your local computer. That means you can access Topics2Themes from your browser at:")
        print("http://127.0.0.1:" + str(current_port) + "/topics2themes/")
    applogger = app.logger
    applogger.setLevel(logging_level_to_use)
    app.run(port=current_port)
    
    # When the server is stopped
    print("Closes database connection")
    mongo_con.close_connection()
