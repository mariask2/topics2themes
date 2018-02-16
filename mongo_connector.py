import pymongo
import datetime
from pymongo import MongoClient



class MongoConnector:
    def __init__(self):
        #self.TOPIC_MODEL_DATABASE = "topic_model_database"
        self.TOPIC_MODEL_DATABASE = "text_database"
        self.client = None
        self.DATE = "date"
        self.ID = "_id"
        self.TOPIC_MODEL_OUTPUT = "topic_model_output"
        self.TEXT_COLLECTION_NAME = "text_collection_name"
    
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
        return db

    def get_model_collection(self):
        db = self.get_database()
        model_collection = db["MODEL_COLLECTION"]
        return model_collection
    
    def get_all_model_document_name_date(self):
        documents = self.get_model_collection().find()
        document_spec = [{self.DATE: document['_id'].generation_time,\
                         self.TEXT_COLLECTION_NAME: document[self.TEXT_COLLECTION_NAME],\
                         self.ID : document[self.ID]}\
                         for document in documents]
        return document_spec, self.DATE, self.TEXT_COLLECTION_NAME, self.ID
    
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

###
# Start
###
if __name__ == '__main__':
    mc = MongoConnector()
    print(mc.get_connection())
    print(mc.get_database())
    print(mc.get_all_collections())
    #print(mc.insert_new_model("test", "name"))
    #print(mc.get_all_collections())

    els, date, name, id = mc.get_all_model_document_name_date()
    for el in els:
        print("****************")
        print(el)
        print(str(el[date]))
        print(mc.get_topic_model_output_with_id(el[id]))
        print()
        
        """
        print(p["text_collection_name"])
        print()
        print(p["date"])
        print()
        """
#print(p["topic_model_output"])


    mc.close_connection()
    print(mc.get_all_collections())
