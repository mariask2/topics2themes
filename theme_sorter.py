from mongo_connector import MongoConnector
from topic_model_constants import *
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib

import os

MODEL_FOLDER = "trained_machine_learning_models"
MODEL_PREFIX = "model_"
VECTORIZER_PREFIX = "vectorizer_"
CLASS_LIST_PREFIX = "class_list_"

class ThemeSorter:
    def __init__(self, mongo_connector):
        self.mongo_connector = mongo_connector
    
        if not os.path.isdir(MODEL_FOLDER):
            os.mkdir(MODEL_FOLDER)

    def get_model_file(self, analysis_id):
        return os.path.join(MODEL_FOLDER, MODEL_PREFIX + analysis_id)
    
    def get_vectorizer_file(self, analysis_id):
        return os.path.join(MODEL_FOLDER, VECTORIZER_PREFIX + analysis_id)
    
    def get_class_list_file(self, analysis_id):
        return os.path.join(MODEL_FOLDER, CLASS_LIST_PREFIX + analysis_id)
    
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
        
        joblib.dump(clf, self.get_model_file(analysis_id))
        joblib.dump(vectorizer, self.get_vectorizer_file(analysis_id))
        joblib.dump(categories_list, self.get_class_list_file(analysis_id))
        #for res, gold in zip(y, res_on_training):
        #print(res,gold, max(res))
        print(categories_list)
        return None

    def rank_themes_for_document(self, analysis_id, document_id):
        themes = self.mongo_connector.get_saved_themes(analysis_id)
        all_theme_nrs = sorted([int(theme[THEME_NUMBER]) for theme in themes])
        
        # No trained model available, return themes sorted according to theme number
        if not os.path.exists(self.get_model_file(analysis_id)) or \
                not os.path.exists(self.get_vectorizer_file(analysis_id)) or \
                    not os.path.exists(self.get_class_list_file(analysis_id)):
            default_themes_str = [str(theme) for theme in all_theme_nrs]
            print("no classifier trained for " + str(analysis_id))
            return default_themes_str
        
        clf = joblib.load(self.get_model_file(analysis_id))
        vectorizer = joblib.load(self.get_vectorizer_file(analysis_id))
        classes = joblib.load(self.get_class_list_file(analysis_id))

        document_dict = self.mongo_connector.get_documents_for_analysis(analysis_id)
        data = [document_dict[int(document_id)]]
        transformed = vectorizer.transform(data)
        classifications = clf.predict_proba(transformed)
        sorted_prob_themes = sorted([(prob, theme_nr) for prob, theme_nr in zip(classifications[0], classes)], reverse = True)
        sorted_themes = [int(theme_nr) for (prob, theme_nr) in sorted_prob_themes]
        
        for theme in all_theme_nrs: # themes that have no associate documents or description, and therefore aren't classifier ranked, are ranked as last
            if theme not in sorted_themes:
                sorted_themes.append(theme)
        themes_str = [str(theme) for theme in sorted_themes]
        return themes_str

if __name__ == '__main__':
    mc = MongoConnector()
    ts = ThemeSorter(mc)
    ts.retrain_model("5ba3977599a029238042ecf3")
    print(ts.rank_themes_for_document("5ba3977599a029238042ecf3", "682"))

