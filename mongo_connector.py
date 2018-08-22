import pymongo
import datetime
import os
from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient
from bson.objectid import ObjectId
from topic_model_constants import *



class MongoConnector:
    def __init__(self):
        #self.TOPIC_MODEL_DATABASE = "topic_model_database"
        #self.TOPIC_MODEL_DATABASE = "text_database"
        self.TOPIC_MODEL_DATABASE = "text_database_5"
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
    
        self.get_theme_collection().create_index(\
                        [(self.THEME_NUMBER, pymongo.ASCENDING),\
                         (self.ANALYSIS_ID, pymongo.ASCENDING)], unique=True)
    
        
    
    def get_connection(self):
        maxSevSelDelay = 5 #Check that the server is listening, wait max 5 sec
        if not self.client:
            self.client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=maxSevSelDelay)
        self.server_info = self.client.server_info()
        return self.client

    def close_connection(self):
        if self.client:
            self.client.close()
            self.client = None

    def get_database(self):
        con = self.get_connection()
        db = con[self.TOPIC_MODEL_DATABASE]
        print("Accessing ", self.TOPIC_MODEL_DATABASE)
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
    
    def get_topic_model_output_with_id(self, id):
        document = self.get_model_collection().find_one({ self.ID : id})
        return document[self.TOPIC_MODEL_OUTPUT]
    
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
        print("model_id", model_id)
        name_with_time = analysis_name + " " + str(datetime.datetime.now())
        post = {self.MODEL_ID : model_id, self.ANALYSIS_NAME : name_with_time}
        print("post")
        post_id = self.get_analyses_collection().insert_one(post).inserted_id
        return {self.ID : str(post_id), self.ANALYSIS_NAME : name_with_time}

    def get_all_analyses_for_model(self, model_id):
        analyses = self.get_analyses_collection().find({self.MODEL_ID : model_id})
        analyses_to_return = [{self.MODEL_ID: post[self.MODEL_ID], self.ID : str(post[self.ID]),\
         self.ANALYSIS_NAME : post[self.ANALYSIS_NAME]} for post in analyses]
        return analyses_to_return



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
        print("analysis_id", analysis_id)
        topic_names = self.get_topic_name_collection().find({self.ANALYSIS_ID : analysis_id})
        all_topic_names = []
        for post in topic_names:
            return_post = {self.TOPIC_ID : post[self.TOPIC_ID], self.TOPIC_NAME : post[self.TOPIC_NAME]}
            all_topic_names.append(return_post)
    
        return all_topic_names

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
        print("*****")
        post_id = self.get_theme_index_collection().update_one({self.ANALYSIS_ID : analysis_id},\
            {"$inc": {self.THEME_INDEX : 1 }}, upsert=True)
        print("post_id", post_id)
        new_index = self.get_theme_index_collection().find_one({self.ANALYSIS_ID : analysis_id})[self.THEME_INDEX]
        print("created theme nr", new_index)

        # TODO: To allow for several users, this must be updated
        post = {self.THEME_NUMBER : new_index, self.ANALYSIS_ID : analysis_id, self.DOCUMENT_IDS : [], self.THEME_NAME : ""}
        
        self.get_theme_collection().insert_one(post)
        return(new_index)


    def get_saved_themes(self, analysis_id):
        themes = self.get_theme_collection().find({self.ANALYSIS_ID : analysis_id})
        all_themes = []
        for post in themes:
            print(post)
            return_post = {self.THEME_NUMBER : str(post[self.THEME_NUMBER]), self.DOCUMENT_IDS : post[self.DOCUMENT_IDS], self.THEME_NAME : post[self.THEME_NAME]}
            all_themes.append(return_post)

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


###

###
# Start
###
if __name__ == '__main__':
    mc = MongoConnector()
    print(mc.get_connection())
    print(mc.get_database())
    print(mc.get_all_collections())
    
    #print(mc.get_all_model_document_name_date_id())
    #print(mc.get_all_models_for_collection_with_name("vaccination_constructed_data"))
    print(mc.create_new_theme("5adb865599a029323a4599c1"))
    #print(mc.get_saved_themes("5adb995c99a029323d4b2b7d"))
    #print(mc.get_all_analyses_for_model("5adb84c199a02931a1eb1dd5"))

    
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
