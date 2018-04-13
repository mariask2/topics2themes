import urllib.request
import urllib.parse
import urllib
import json
import sys
import linecache
from urllib.error import HTTPError

url_before_port = "http://127.0.0.1:"
url_after_port = "/topic_modelling/api/v1.0/"

def get_exception_info():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    return 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)


def test_get_data_sets(urlbase):
    url_method = "get_data_sets"
    try:
        url = urlbase + url_method
        with urllib.request.urlopen(url) as f:
            c = f.read().decode('utf-8')
            return c
    except HTTPError as e:
        print(str(e) + " " + get_exception_info())
        print(e.__class__)
        return "No classification"

"""
def test_get_all_model_document_name_date_id(urlbase):
    params_url = urllib.parse.urlencode({"collection_name": "vaccination_constructed_data_NMF"})
    url_method = "get_all_models_for_collection_with_name"
    try:
        url = urlbase + url_method + "?%s" % params_url
        with urllib.request.urlopen(url) as f:
            c = f.read().decode('utf-8')
            return c
    except HTTPError as e:
        print(str(e) + " " + get_exception_info())
        print(e.__class__)
        return "No classification"
"""

def test_get_all_model_document_name_date_id(urlbase):
    params_text = urllib.parse.urlencode({"collection_name": "vaccination_constructed_data_NMF"})
    text_method = "get_all_models_for_collection_with_name"
    try:
        url = urlbase + text_method + "?%s" % params_text
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

    #print(test_get_data_sets(urlbase))
    print(test_get_all_model_document_name_date_id(urlbase))

