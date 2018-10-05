from mongo_connector import MongoConnector

class ThemeSorter:
    def __init__(self, mongo_connector):
        self.mongo_connector = mongo_connector

    def retrain_model(self, analysis_id):
        print("Retrain model for " + str(analysis_id))
        return None

if __name__ == '__main__':
    mc = MongoConnector()
    ts = ThemeSorter(mc)
    print(ts.retrain_model("Retrain model for 5ba3977599a029238042ecf3"))
