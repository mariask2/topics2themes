import pymongo
import datetime
import os
import json
import re
from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps

# An import that should function both locally and when running an a remote server
try:
    from environment_configuration import *
except:
    from topics2themes.environment_configuration import *

if RUN_LOCALLY:
    from topic_model_constants import *
else:
    from topics2themes.topic_model_constants import *

DEFAULT_DATABASE_NAME = "default_database_name"

class MongoConnector:
    def __init__(self):
        self.TOPIC_MODEL_DATABASE = DEFAULT_DATABASE_NAME
        try:
            self.TOPIC_MODEL_DATABASE = DATABASE_NAME
        except:
            self.TOPIC_MODEL_DATABASE = DEFAULT_DATABASE_NAME
       
        self.client = None
        self.DATE = "date"
        self.ID = "_id"
        self.TOPIC_ID = "topic_id"
        self.TOPIC_NAME = "topic_name"
        self.MODEL_ID = "model_id"
        self.TOPIC_MODEL_OUTPUT = "topic_model_output"
        self.TEXT_COLLECTION_NAME = "text_collection_name"
        self.THEME_NUMBER = "theme_number"
        self.DOCUMENT_IDS = "document_ids"
        self.THEME_NAME = "theme_name"
        self.THEME_INDEX = "theme_index"
        self.ANALYSIS_NAME = "analysis_name"
        self.ANALYSIS_ID = "analysis_id"
        self.TEXT_ID = "text_id"
        self.USER_DEFINED_LABEL = "user_defined_label"
        
        self.MODEL_FILE_NAME = "_model.json"
        self.THEMES_FILE_NAME = "_theme.json"
        self.ANALYSIS_FILE_NAME = "_analysis.json"
        self.TOPIC_NAME_FILE_NAME = "_topic_name.json"
        self.USER_DEFINED_LABEL_FILE_NAME = "_user_defined_label.json"

        self.theme_index_created = False
        
    
    def get_connection(self):
        
        if not self.theme_index_created:
            self.theme_index_created = True # Make sur sure to set to true here, so that when running to get theme collection doesn't cause an indefinite loop
            self.get_theme_collection().create_index(\
                                                 [(self.THEME_NUMBER, pymongo.ASCENDING),\
                                                  (self.ANALYSIS_ID, pymongo.ASCENDING)], unique=True)
        
        maxSevSelDelay = 5 #Check that the server is listening, wait max 5 sec
        if not self.client:
            self.client = MongoClient(serverSelectionTimeoutMS=maxSevSelDelay)
        #self.client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=maxSevSelDelay)
        #self.server_info = self.client.server_info()
        return self.client

    def close_connection(self):
        if self.client:
            self.client.close()
            self.client = None

    def get_database(self):
        con = self.get_connection()
        db = con[self.TOPIC_MODEL_DATABASE]
        return db

    ### Storing and fetching the output of models
    def get_model_collection(self):
        db = self.get_database()
        model_collection = db["MODEL_COLLECTION"]
        return model_collection
    
    
    def get_model_for_model_id(self, id):
        document = self.get_model_collection().find_one({'_id' : ObjectId(id)})
        document_spec = {self.TOPIC_MODEL_OUTPUT: document[self.TOPIC_MODEL_OUTPUT],\
                        self.TEXT_COLLECTION_NAME: document[self.TEXT_COLLECTION_NAME],\
                        self.ID : str(document[self.ID])}
        return document_spec
        
    def get_analysis_for_analysis_id(self, id):
        analysis =  self.get_analyses_collection().find_one({'_id' : ObjectId(id)})
        return_analysis = {self.MODEL_ID : analysis[self.MODEL_ID],\
            self.ANALYSIS_NAME : analysis[self.ANALYSIS_NAME],\
            self.ID : str(analysis[self.ID])
        }
        return return_analysis




    """
        Help methods for storing data in file
        """
    def save_analysis_data_to_folder(self, analysis_id, data_dir, file_name, data):
        save_to = os.path.join(data_dir, str(analysis_id) + file_name)
        
        with open(save_to, 'w') as outfile:
            json.dump(data, outfile, sort_keys = True, indent = 4, ensure_ascii = False)

    def is_analysis_id_valid(self, analysis_id):
        valid = re.compile(r"^[A-Za-z0-9]{24}$")
        if valid.match(analysis_id) is None:
            return False
        else:
            return True

    def save_analysis_to_file_for_analysis_id(self, analysis_id):
        if not self.is_analysis_id_valid(analysis_id):
            raise ValueError("Format of analysis_id incorrect: " + str(analysis_id))
        model_id = self.get_model_for_analysis(analysis_id)
        model = self.get_model_for_model_id(model_id)
        data_dir = os.path.join(WORKSPACE_FOLDER, DATA_FOLDER, model[self.TEXT_COLLECTION_NAME], EXPORT_DIR)
        
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        self.save_analysis_data_to_folder(analysis_id, data_dir, self.MODEL_FILE_NAME, model)
        
        self.save_analysis_data_to_folder(analysis_id, data_dir, self.THEMES_FILE_NAME, self.get_saved_themes(analysis_id))

        self.save_analysis_data_to_folder(analysis_id, data_dir, self.ANALYSIS_FILE_NAME, self.get_analysis_for_analysis_id(analysis_id))

        self.save_analysis_data_to_folder(analysis_id, data_dir, self.TOPIC_NAME_FILE_NAME, self.get_all_topic_names(analysis_id))
        
        self.save_analysis_data_to_folder(analysis_id, data_dir, self.USER_DEFINED_LABEL_FILE_NAME, self.get_all_user_defined_labels(analysis_id))

        return data_dir

    """
        Right now, it only possible to write analyses. When this is done, it's model is also saved with the id of the analysis. Therefore, the saved analysisid is given
        """
    def load_model_from_file(self, saved_analysis_id, data_collection_name):
        if not self.is_analysis_id_valid(saved_analysis_id):
            raise ValueError("Format of analysis_id incorrect: " + str(saved_analysis_id))
        
        data_collection_path = os.path.join(WORKSPACE_FOLDER, DATA_FOLDER, data_collection_name)
        if not os.path.isdir(data_collection_path):
            raise ValueError("The specified data folder does not exist: " + str(data_collection_path))

        saved_file = open(os.path.join(data_collection_path, EXPORT_DIR, saved_analysis_id + self.MODEL_FILE_NAME))
        saved_model = json.load(saved_file)
        saved_model[self.TOPIC_MODEL_OUTPUT][META_DATA][MODEL_NAME] = str(datetime.datetime.utcnow()) \
            + "_loaded_" + saved_analysis_id + "_" + saved_model[self.TOPIC_MODEL_OUTPUT][META_DATA][MODEL_NAME]
        self.insert_new_model(saved_model[self.TOPIC_MODEL_OUTPUT], saved_model[self.TEXT_COLLECTION_NAME])
 
    # TODO: Check that it is correct to turn str(document[self.ID]) to a string, to make it serializable
    # If it is not turned to a string it will not be accepted for http
    def get_all_models_for_collection_with_name(self, text_collection_name):
  
        documents = self.get_model_collection().find({self.TEXT_COLLECTION_NAME: text_collection_name})
        
        document_spec = [{self.DATE: str(document['_id'].generation_time),\
                         self.TEXT_COLLECTION_NAME: document[self.TEXT_COLLECTION_NAME],\
                         self.ID : str(document[self.ID]),\
                         MODEL_NAME : document[self.TOPIC_MODEL_OUTPUT][META_DATA][MODEL_NAME]}\
                         for document in documents]
   
        return document_spec
    

    def get_all_collections(self):
        return self.get_database().collection_names()

    def insert_new_model(self, topic_model_output, text_collection_name):
        time = datetime.datetime.utcnow()
        post = {self.TEXT_COLLECTION_NAME : text_collection_name,\
                self.TOPIC_MODEL_OUTPUT: topic_model_output}
        post_id = self.get_model_collection().insert_one(post).inserted_id
        return time, post_id
    
    
    ### Storing and fetching analyses
    def get_analyses_collection(self):
        db = self.get_database()
        model_collection = db["ANALYSIS_COLLECTION"]
        return model_collection

    def create_new_analysis(self, model_id, analysis_name):
        print(str(datetime.datetime.now()) + " Creating new analysis for model_id ", model_id)
        name_with_time = analysis_name + " " + str(datetime.datetime.now())
        post = {self.MODEL_ID : model_id, self.ANALYSIS_NAME : name_with_time}
        post_id = self.get_analyses_collection().insert_one(post).inserted_id
        print(str(datetime.datetime.now()) + " Inserted post. New post-id: " + str(post_id))
        return {self.ID : str(post_id), self.ANALYSIS_NAME : name_with_time}

    def get_all_analyses_for_model(self, model_id):
        analyses = self.get_analyses_collection().find({self.MODEL_ID : model_id})
        analyses_to_return = [{self.MODEL_ID: post[self.MODEL_ID], self.ID : str(post[self.ID]),\
         self.ANALYSIS_NAME : post[self.ANALYSIS_NAME]} for post in analyses]
        print(str(datetime.datetime.now()) + " Found " + str(len(analyses_to_return)) + " number of analysis for model " + str(model_id))
        return analyses_to_return

    def get_model_for_analysis(self, analysis_id):
        analysis = self.get_analyses_collection().find_one({self.ID : ObjectId(analysis_id)})
        return analysis[self.MODEL_ID]
    
    ### Storing and fetching names of topics

    def get_topic_name_collection(self):
        db = self.get_database()
        topic_name_collection = db["TOPIC_NAME_COLLECTION"]
        return topic_name_collection

    def save_or_update_topic_name(self, topic_id, new_name, analysis_id):
        self.get_topic_name_collection().update_one(\
                    {self.TOPIC_ID : topic_id, self.ANALYSIS_ID : analysis_id},\
                    {"$set": { self.TOPIC_NAME : new_name }},\
                    upsert = True)
        return self.get_topic_name_collection().find_one({self.TOPIC_ID : topic_id,\
                                                        self.ANALYSIS_ID : analysis_id})
    
                                                
    def get_all_topic_names(self, analysis_id):
        topic_names = self.get_topic_name_collection().find({self.ANALYSIS_ID : analysis_id})
        all_topic_names = []
        for post in topic_names:
            return_post = {self.TOPIC_ID : post[self.TOPIC_ID], self.TOPIC_NAME : post[self.TOPIC_NAME]}
            all_topic_names.append(return_post)
    
        return all_topic_names

    ### Storing and fetching user-defined text labels
    
    def get_user_defined_label_collection(self):
        db = self.get_database()
        user_defined_label_collection = db["USER_DEFINED_LABEL_COLLECTION"]
        return user_defined_label_collection
    
    def save_or_update_user_defined_label(self, text_id, user_defined_label, analysis_id):
        self.get_user_defined_label_collection().update_one(\
                            {self.TEXT_ID : text_id, self.ANALYSIS_ID : analysis_id},\
                            {"$set": { self.USER_DEFINED_LABEL : user_defined_label}},\
                            upsert = True)
        post = self.get_user_defined_label_collection().find_one({self.TEXT_ID : text_id,\
                                                                self.ANALYSIS_ID : analysis_id})
    
        print(post)
        return_post = {self.TEXT_ID : post[self.TEXT_ID], self.USER_DEFINED_LABEL : post[self.USER_DEFINED_LABEL]}
        return return_post

    def get_all_user_defined_labels(self, analysis_id):
        user_defined_labels = self.get_user_defined_label_collection().find({self.ANALYSIS_ID : analysis_id})
        all_user_defined_labels = []
        for post in user_defined_labels:
            return_post = {self.TEXT_ID : post[self.TEXT_ID], self.USER_DEFINED_LABEL : post[self.USER_DEFINED_LABEL]}
            all_user_defined_labels.append(return_post)
        
        return all_user_defined_labels
    
    ### Storing and fetching information related to themes

    def get_theme_collection(self):
        db = self.get_database()
        theme_collection = db["THEME_COLLECTION"]
        return theme_collection

    def get_theme_index_collection(self):
        db = self.get_database()
        theme_index_collection = db["THEME_INDEX_COLLECTION"]
        return theme_index_collection


    def create_new_theme(self, analysis_id):
        # Index for themes are stored in a separate collection
        print(str(datetime.datetime.now()) + " Started proces of creating theme for " + str(analysis_id))
        post_id = self.get_theme_index_collection().update_one({self.ANALYSIS_ID : analysis_id},\
            {"$inc": {self.THEME_INDEX : 1 }}, upsert=True)

        new_index = self.get_theme_index_collection().find_one({self.ANALYSIS_ID : analysis_id})[self.THEME_INDEX]


        # TODO: To allow for several users, this must be updated
        post = {self.THEME_NUMBER : new_index, self.ANALYSIS_ID : analysis_id, self.DOCUMENT_IDS : [], self.THEME_NAME : ""}
        
        self.get_theme_collection().insert_one(post)
        print(str(datetime.datetime.now()) + " Inserted post " + str(post))
        return(new_index)


    def get_saved_themes(self, analysis_id):
        themes = self.get_theme_collection().find({self.ANALYSIS_ID : analysis_id})
        all_themes = []
        for post in themes:
            return_post = {self.THEME_NUMBER : str(post[self.THEME_NUMBER]), self.DOCUMENT_IDS : post[self.DOCUMENT_IDS], self.THEME_NAME : post[self.THEME_NAME]}
            all_themes.append(return_post)
        
        print(str(datetime.datetime.now()) + " Found " + str(len(all_themes)) + " number of themes for analysis " + str(analysis_id))

        return all_themes

    def delete_theme(self, analysis_id, theme_number):
        theme_number_int = int(theme_number)
        # TODO: Check that there are no documents associated with the theme before removing
        number_of_deleted = self.get_theme_collection().delete_one({self.ANALYSIS_ID : analysis_id,\
                                                  self.THEME_NUMBER : theme_number_int}).deleted_count
        return number_of_deleted

    def update_theme_name(self, theme_number_str, new_name, analysis_id):
        theme_number_int = int(theme_number_str)
        current_post = self.get_theme_collection().find_one({self.THEME_NUMBER : theme_number_int, self.ANALYSIS_ID : analysis_id})
        if not current_post:
            print("post not found") # TODO: Better error handling
            return None
        document_ids = current_post[self.DOCUMENT_IDS]
        print("id", document_ids)
        self.get_theme_collection().update_one(\
                                                {self.THEME_NUMBER : theme_number_int, self.ANALYSIS_ID : analysis_id},\
                                               {"$set": { self.THEME_NAME : new_name, self.DOCUMENT_IDS : document_ids}},\
                                                upsert = True)
        updated_theme =  self.get_theme_collection().find_one({self.THEME_NUMBER : theme_number_int,\
                                                         self.ANALYSIS_ID : analysis_id})
        print(updated_theme)
        new_name = updated_theme[self.THEME_NAME]
        print("*********", new_name)
        return new_name

    def add_theme_document_connection(self, theme_number_str, document_id, analysis_id):
        theme_number_int = int(theme_number_str)
        current_post = self.get_theme_collection().find_one({self.THEME_NUMBER : theme_number_int, self.ANALYSIS_ID : analysis_id})
        if not current_post:
            print("post not found") # TODO: Better error handling
            return None
        document_ids = current_post[self.DOCUMENT_IDS]
        if document_id in document_ids:
            return None # don't add a connection that is already there
        document_ids.append(document_id)
        self.get_theme_collection().update_one(\
                {self.THEME_NUMBER : theme_number_int, self.ANALYSIS_ID : analysis_id},\
                {"$set": { self.DOCUMENT_IDS : document_ids}})
                                               
        new_document_ids = self.get_theme_collection().\
            find_one({self.THEME_NUMBER : theme_number_int, self.ANALYSIS_ID : analysis_id})[self.DOCUMENT_IDS]
        return new_document_ids


    def delete_theme_document_connection(self, theme_number_str, document_id, analysis_id):
        theme_number_int = int(theme_number_str)
        current_post = self.get_theme_collection().find_one({self.THEME_NUMBER : theme_number_int, self.ANALYSIS_ID : analysis_id})
        if not current_post:
            print("post not found") # TODO: Better error handling
            return None
        document_ids = current_post[self.DOCUMENT_IDS]
        to_delete = document_ids.index(document_id)
        del document_ids[to_delete]
        self.get_theme_collection().update_one(\
                    {self.THEME_NUMBER : theme_number_int, self.ANALYSIS_ID : analysis_id},\
                    {"$set": { self.DOCUMENT_IDS : document_ids}})
            
        new_document_ids = self.get_theme_collection().\
                find_one({self.THEME_NUMBER : theme_number_int, self.ANALYSIS_ID : analysis_id})[self.DOCUMENT_IDS]
        return new_document_ids

    ## For retrieving theme document connections
    def get_documents_for_analysis(self, analysis_id):
        model_id = self.get_model_for_analysis(analysis_id)
        topic_model_output = self.get_model_for_model_id(model_id)[self.TOPIC_MODEL_OUTPUT]
        text_dict = {}
        document_theme_dict = {}
        document_topic_dict = {}
        topic_theme_dict = {}
        document__themes_that_other_documents_with_the_same_topic_has__dict = {}
        
        for el in topic_model_output[DOCUMENTS]:
            topics = [topic[TOPIC_INDEX] for topic in el[DOCUMENT_TOPICS]]
            document_topic_dict[el[ID_SOURCE]] = topics
            text_dict[el[ID_SOURCE]] = el[TEXT]
            
        themes_for_analysis = self.get_saved_themes(analysis_id)
        
        for theme in themes_for_analysis:
            topics_associated_with_theme = []
            for document_id in theme[DOCUMENT_ID]:
                document_id = int(document_id)
                topics_associated_with_document = document_topic_dict[document_id]
                topics_associated_with_theme.extend(topics_associated_with_document)
            for topic in topics_associated_with_theme:
                if topic not in topic_theme_dict:
                    topic_theme_dict[topic] = []
                topic_theme_dict[topic].append(theme[THEME_NUMBER])


        for document, topics in document_topic_dict.items():
            potential_themes_for_document = []
            for topic in topics:
                if topic in topic_theme_dict:
                    potential_themes_for_document.extend(topic_theme_dict[topic])
            potential_themes_for_document = list(set(potential_themes_for_document))
            document__themes_that_other_documents_with_the_same_topic_has__dict[document] = sorted(potential_themes_for_document)
        
        return text_dict, document__themes_that_other_documents_with_the_same_topic_has__dict

    def get_collection_name_for_analysis(self, analysis_id):
        model_id = self.get_model_for_analysis(analysis_id)
        text_collection_name = self.get_model_for_model_id(model_id)[self.TEXT_COLLECTION_NAME]
        return text_collection_name

###
###

###
# Start
###
if __name__ == '__main__':
    mc = MongoConnector()
    print(mc.get_connection())
    print(mc.get_database())
    print(mc.get_all_collections())
    #print(mc.get_all_analyses_for_model("5cc9d78999a02903400717af"))
    #mc.save_analysis_to_file_for_analysis_id("5ccad37e99a029092cb79fea")
    #print(mc.get_analysis_for_analysis_id("5ccad37e99a029092cb79fea"))
    
    #constructed_col = mc.get_all_models_for_collection_with_name("vaccination_constructed_data_marked")
    #one_model_output = mc.get_model_for_model_id("5cc9d78999a02903400717af")
    #print(one_model_output)
    #print(mc.get_all_model_document_name_date_id())
    #print(mc.get_all_models_for_collection_with_name("vaccination_constructed_data"))
    #print(mc.create_new_theme("5adb865599a029323a4599c1"))
    #print(mc.get_saved_themes("5adb995c99a029323d4b2b7d"))
    #print(mc.get_all_analyses_for_model("5adb84c199a02931a1eb1dd5"))

    mc.load_model_from_file("5cca9d0f99a029086822ccd3", "vaccination_constructed_data_marked")
    """
    print(mc.create_new_analysis("5adb84c199a02931a1eb1dd5", "test_name"))
    an = mc.get_all_analyses_for_model("5adb84c199a02931a1eb1dd5")
    for el in an:
        print(el)
    """
    """
    res = mc.get_model_for_model_id("5ad4fb3b99a029a0b5d37c0c")["topic_model_output"]
    print(res["documents"])
    print(res["topics"])
    """
    """
    els = mc.get_all_model_document_name_date_id()
    for el in els:
        print("****************")
        print(el)
        print(str(el[mc.DATE]))
        print(mc.get_topic_model_output_with_id(el[mc.ID]))
        print()
     """
    
    
    """
    print(mc.save_or_update_topic_name("topc id test", "new name text", "model id test 2"))
    print(mc.save_or_update_topic_name("topc id test", "updated name text", "model id test 2"))


    print("*******", mc.get_all_topic_names("model id test"))

    print(mc.create_new_theme("test_theme_2_4"))
    print(mc.create_new_theme("test_theme_2_4"))
    
    print(mc.get_saved_themes("test_theme_2_4"))
    
    #
    
    print(mc.update_theme_name(6, "new_name", "test_theme_2_4"))
    print(mc.update_theme_name(6, "old_name", "test_theme_2_4"))
    print(mc.update_theme_name(6, "new_name", "test_theme_2_4"))
    
    print("deleted", mc.delete_theme("test_theme_2_4", "5"))
    
    print(mc.add_theme_document_connection("6", "1", "test_theme_2_4"))
    print(mc.add_theme_document_connection("6", "2", "test_theme_2_4"))
    print(mc.delete_theme_document_connection(6, "1", "test_theme_2_4"))
    print(mc.delete_theme_document_connection(6, "2", "test_theme_2_4"))
    
    print(mc.get_saved_themes("test_theme_2_4"))
    mc.close_connection()
    print(mc.get_all_collections())
    """
