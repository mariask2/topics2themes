import urllib.request
import urllib.parse
import urllib
import json
import sys
import traceback
import linecache
from urllib.error import HTTPError


def get_exception_info():
    trace_back = traceback.format_exc()
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    all_info = str(exc_obj) + str(trace_back)
    return 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), all_info)

APPROVED_KEYS = []
f = open("approved_keys.txt")
for line in f:
    APPROVED_KEYS.append(line.strip())

url_before_port = "http://127.0.0.1:"
url_after_port = "/topic_modelling/api/v1.0/"


def get_test_model(urlbase, method):
    dataset_name = "vaccination_mumsnet"
    params_text = urllib.parse.urlencode({"apiKey": APPROVED_KEYS[0], "dataset_name": dataset_name})
    try:
        url = urlbase + method + "?%s" % params_text
        print(url)
        with urllib.request.urlopen(url) as f:
            c = f.read().decode('utf-8')
            return c
    except HTTPError as e:
        print(str(e) + " " + get_exception_info())
        print(e.__class__)
        return "No classification"

if __name__ == '__main__':
    
    if len(sys.argv) < 2:
        sys.exit("As an argument to the script, you need to give the port at which you are listening,"\
                 + " for instance 5000")
    port = sys.argv[1]
    
    urlbase = url_before_port + port + url_after_port
    for method in ["get_topic_model_results", "get_cashed_topic_model_results"]:
        print(get_test_model(urlbase, method))




