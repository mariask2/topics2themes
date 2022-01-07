import os
import json

def convert_to_csv(json_topic_names, json_model):
    print(json_model)
    print(json_topic_names)


if __name__ == '__main__':
    folder = "/Users/marsk757/topic2themes/topics2themes/data_folder/språk-tilltal-delat/topics2themes_exports_folder_created_by_system"
    model_nr = "61d78098fb849a1ac4d873a2"
    
    
    topic_names = open(os.path.join(folder, model_nr + "_topic_name.json"), "r")
    
    model = open(os.path.join(folder, model_nr + "_model.json"), "r")
    
    json_topic_names = json.loads(topic_names.read())
    json_model = json.loads(model.read())

    topic_names.close()
    model.close()
    convert_to_csv(json_topic_names, json_model)
