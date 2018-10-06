from mongo_connector import MongoConnector
from topic_model_constants import *
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

class ThemeSorter:
    def __init__(self, mongo_connector):
        self.mongo_connector = mongo_connector

    def retrain_model(self, analysis_id):
        print("Retrain model for " + str(analysis_id))
        themes = self.mongo_connector.get_saved_themes(analysis_id)
        #print("model id",  self.mongo_connector.get_model_for_analysis(analysis_id))
        document_dict = self.mongo_connector.get_documents_for_analysis(analysis_id)

        data_list = []
        y = []
        categories_list = []
        for theme in themes:
            print(theme[THEME_NUMBER])
            print(theme[THEME_NAME])
            for doc in theme[DOCUMENT_ID]:
                data_list.append(document_dict[int(doc)])
                y.append(theme[THEME_NUMBER])
                if theme[THEME_NUMBER] not in categories_list:
                    categories_list.append(theme[THEME_NUMBER])
            if theme[THEME_NAME].strip() != "":
                # Also use the description of the theme as a training data point
                data_list.append(theme[THEME_NAME])
                y.append(theme[THEME_NUMBER])
                if theme[THEME_NUMBER] not in categories_list:
                    categories_list.append(theme[THEME_NUMBER])

        # TODO: Use stopwords
        vectorizer = CountVectorizer(min_df=2,\
                                     ngram_range = (1, 1),\
                                     binary = True)
        transformed = vectorizer.fit_transform(data_list)
        feature_set = set()
        inversed = vectorizer.inverse_transform(transformed)
        clf = LogisticRegression(C=10)
        clf.fit(transformed, y)
        res_on_training = clf.predict_proba(transformed)
        for res, gold in zip(y, res_on_training):
            print(res,gold, max(res))
        print(categories_list)
        return None

if __name__ == '__main__':
    mc = MongoConnector()
    ts = ThemeSorter(mc)
    ts.retrain_model("5ba3977599a029238042ecf3")
