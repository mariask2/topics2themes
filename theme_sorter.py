from mongo_connector import MongoConnector

class ThemeSorter:
    def __init__(self, mongo_connector):
        self.mongo_connector = mongo_connector

    def retrain_model(self, analysis_id):
        print("Retrain model for " + str(analysis_id))
        print(self.mongo_connector.get_saved_themes(analysis_id))
        print("model id",  self.mongo_connector.get_model_for_analysis(analysis_id))
        for key, item in self.mongo_connector.get_documents_for_analysis(analysis_id).items():
            print(key, item)
        return None

if __name__ == '__main__':
    mc = MongoConnector()
    ts = ThemeSorter(mc)
    ts.retrain_model("5ba3977599a029238042ecf3")
