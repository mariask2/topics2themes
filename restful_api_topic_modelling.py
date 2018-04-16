from flask import Flask, jsonify, abort, make_response, request, json, request, current_app
import sys
import traceback
import linecache
from datetime import timedelta
from functools import update_wrapper
import make_topic_models
from flask_cors import CORS, cross_origin
from mongo_connector import MongoConnector

import make_topic_models

app = Flask(__name__)
CORS(app)

mongo_con = MongoConnector()
# To not have a lot of space in the output
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# TODO: Sloppy error handling. This should be logged
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
    f = open(key_file_name)
    for line in f:
        approved_keys.append(line.strip())

def authenticate():
    key = request.values.get("apiKey")
    if key not in APPROVED_KEYS:
        abort(403)

VACCINATION_MUMSNET = "vaccination_mumsnet"

@app.route('/topic_modelling/api/v1.0/get_data_sets', methods=['GET', 'POST'])
def get_data_sets():
    data_sets = make_topic_models.get_sets_in_data_folder()
    resp = make_response(jsonify({"result" : data_sets}))
    return resp

@app.route('/topic_modelling/api/v1.0/get_all_models_for_collection_with_name', methods=['GET', 'POST'])
def get_all_models_for_collection_with_name():
    collection_name = request.values.get("collection_name")
    all_models_for_collection_with_name = mongo_con.get_all_models_for_collection_with_name(collection_name)
    resp = make_response(jsonify({"result" : all_models_for_collection_with_name}))
    return resp

@app.route('/topic_modelling/api/v1.0/make_model_for_collection', methods=['GET', 'POST'])
def make_model_for_collection():
    collection_name = request.values.get("collection_name")
    model_name = request.values.get("model_name")
    model_result = make_topic_models.make_model_for_collection(collection_name, model_name, mongo_con)
    resp = make_response(jsonify({"result" : model_result}))
    return resp


"""
@app.route('/topic_modelling/api/v1.0/get_topic_model_results', methods=['GET', 'POST'])
def get_new_topic_model_results():
    res = get_topic_model_results(make_topic_models.run_make_topic_models())
    print("*******")
    #print(res.headers)
    print("********")
    FILE.write(str(res) + "\n")
    return res
"""

"""
@app.route('/topic_modelling/api/v1.0/get_topic_model_results', methods=['OPTIONS'])
def get_new_topic_model_results_options():
    print("starting")
    resp = make_response(jsonify({"result" : "test"}))
    resp.headers["Access-Control-Allow-Origin"] = "*"

    #res = get_topic_model_results(make_topic_models.run_make_topic_models())
    print("******* options")
    print(res.headers)
    print("********")
    return res
"""



@app.route('/topic_modelling/api/v1.0/get_cashed_topic_model_results', methods=['GET', 'POST'])
def get_cashed_topic_model_results():
    return get_topic_model_results(make_topic_models.get_cashed_topic_model(mongo_con))

@app.route('/topic_modelling/api/v1.0/update_topic_name', methods=['GET', 'POST'])
def update_topic_name():
    topic_id = request.values.get("topic_id")
    topic_name = request.values.get("topic_name")
    model_id = request.values.get("model_id")
    topic_name_update_result =  mongo_con.save_or_update_topic_name(topic_id, topic_name, model_id)
    resp = make_response(jsonify({"result" : "topic name updated"}))
    return resp


@app.route('/topic_modelling/api/v1.0/get_all_topic_names', methods=['GET', 'POST'])
def get_all_topic_names():
    model_id = request.values.get("model_id")
    print(model_id)
    all_topic_names =  mongo_con.get_all_topic_names(model_id)
    resp = make_response(jsonify({"result" : all_topic_names}))
    return resp


@app.route('/topic_modelling/api/v1.0/create_new_theme', methods=['GET', 'POST'])
def create_new_theme():
    model_id = request.values.get("model_id")
    new_theme_id =  mongo_con.create_new_theme(model_id)
    resp = make_response(jsonify({"result" : new_theme_id}))
    print("Created new theme for", model_id)
    return resp

@app.route('/topic_modelling/api/v1.0/delete_theme', methods=['GET', 'POST'])
def delete_theme():
    model_id = request.values.get("model_id")
    theme_number = request.values.get("theme_number")
    nr_of_deleted_themes =  mongo_con.delete_theme(model_id, theme_number)
    resp = make_response(jsonify({"result" : nr_of_deleted_themes}))
    return resp

@app.route('/topic_modelling/api/v1.0/get_saved_themes', methods=['GET', 'POST'])
def get_saved_themes():
    model_id = request.values.get("model_id")
    new_theme_id =  mongo_con.get_saved_themes(model_id)
    resp = make_response(jsonify({"result" : new_theme_id}))
    print("Get saved themes for", model_id)
    return resp

@app.route('/topic_modelling/api/v1.0/update_theme_name', methods=['GET', 'POST'])
def update_theme_name():
    theme_id = request.values.get("theme_number")
    theme_name = request.values.get("theme_name")
    model_id = request.values.get("model_id")
    theme_name_update_result =  mongo_con.update_theme_name(theme_id, theme_name, model_id)
    resp = make_response(jsonify({"result" : theme_name_update_result}))
    return resp

@app.route('/topic_modelling/api/v1.0/add_theme_document_connection', methods=['GET', 'POST'])
def add_theme_document_connection():
    theme_id = request.values.get("theme_number")
    document_id = request.values.get("document_id")
    model_id = request.values.get("model_id")
    theme_document_connection_result =  mongo_con.add_theme_document_connection(theme_id, document_id, model_id)
    resp = make_response(jsonify({"result" : theme_document_connection_result}))
    return resp

@app.route('/topic_modelling/api/v1.0/delete_theme_document_connection', methods=['GET', 'POST'])
def delete_theme_document_connection():
    theme_id = request.values.get("theme_number")
    document_id = request.values.get("document_id")
    model_id = request.values.get("model_id")
    theme_document_connection_result =  mongo_con.delete_theme_document_connection(theme_id, document_id, model_id)
    resp = make_response(jsonify({"result" : theme_document_connection_result}))
    return resp



def get_topic_model_results(topic_model_method):
    possible_dataset_names = [VACCINATION_MUMSNET]
    try:
        #authenticate() # TODO: No authentication is carried out. If the code is going to be
        # used in a production environment, this should be added
        dataset_name = request.values.get("dataset_name")
        if dataset_name not in possible_dataset_names:
            raise ValueError('The dataset name ' +  str(dataset_name) + ') is unknown')
        
        # TODO: With this code, only one dataset can be run
        # Make it configurable
        topic_model_results = jsonify({"result" : "no matching model"})
        if dataset_name == VACCINATION_MUMSNET:
            topic_model_results = topic_model_method
        
        FILE.write("*****\n")
        FILE.write(str(topic_model_results))
        FILE.flush()
        resp = make_response(jsonify({"result" : topic_model_results}))
        print(resp)
        #resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp
    except Exception as e:
        return get_exception_info(e)



APPROVED_KEYS = []
FILE = open("log_file.txt", "w")

if __name__ == '__main__':


    load_keys(APPROVED_KEYS, "approved_keys.txt")

    current_port = get_port()
    app.run(port=current_port)
    print("Closes database connection")
    mongo_con.close_connection()
