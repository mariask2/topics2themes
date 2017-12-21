from flask import Flask, jsonify, abort, make_response, request, json
import sys
import traceback
import linecache

app = Flask(__name__)

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
    return make_response(jsonify({'error' : str(e) + " " + more}), 400)

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

@app.route('/topic_modelling/api/v1.0/get_topic_model_results', methods=['GET'])
def get_topic_model_results():
    possible_dataset_names = ["vaccination_mumsnet"]
    try:
        authenticate()
        dataset_name = request.values.get("dataset_name")
        if dataset_name not in possible_dataset_names:
            raise ValueError('The dataset name ' +  str(dataset_name) + ') is unknown')
    
        result = {"test" : "test"}
        return jsonify({'result' : result})
    except Exception as e:
        return str(get_exception_info(e))


APPROVED_KEYS = []

if __name__ == '__main__':

    load_keys(APPROVED_KEYS, "approved_keys.txt")

    current_port = get_port()
    app.run(port=current_port)
