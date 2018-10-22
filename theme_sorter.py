from mongo_connector import MongoConnector
from topic_model_constants import *
from environment_configuration import *
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib
from make_topic_models import StopwordHandler

import os
import handle_properties

MODEL_FOLDER = os.path.join(WORKSPACE_FOLDER, "trained_machine_learning_models")
MODEL_PREFIX = "model_"
VECTORIZER_PREFIX = "vectorizer_"
CLASS_LIST_PREFIX = "class_list_"

class ThemeSorter:
    def __init__(self, mongo_connector):
        self.mongo_connector = mongo_connector
        self.stopword_handler = StopwordHandler()
        
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
        document_dict, potential_theme_dict = self.mongo_connector.get_documents_for_analysis(analysis_id)
        
        if (len(themes)) < 2 or (len(document_dict.keys()) < 5):
            return # No point of training a model when there very little data

        text_collection_name = self.mongo_connector.get_collection_name_for_analysis(analysis_id)
        properties, path_slash_format, path_dot_format = handle_properties.load_properties_from_parameters(DATA_FOLDER + "." + text_collection_name)
        
        stop_word_file = os.path.join(path_slash_format, properties.STOP_WORD_FILE)
        stop_words=self.stopword_handler.get_stop_word_set(stop_word_file)
        
        data_list = []
        y = []
        categories_list = []
        for theme in themes:
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

        if len(categories_list) < 2:
            return # If the categories list is small, but nr of themes is >= 2, this means that the classifier only has one class to work with. No point training the classifier.
    
        vectorizer = CountVectorizer(min_df=2,\
                                     stop_words=stop_words,\
                                     ngram_range = (1, 1),\
                                     binary = True)
        try:
            transformed = vectorizer.fit_transform(data_list)
        except ValueError:
            print("Vectorization failed")
            return # If there is very little data, don't do any machine learning training
        
        feature_set = set()
        inversed = vectorizer.inverse_transform(transformed)
        for feature in inversed:
            for f in list(feature):
                feature_set.add(f)
        if len(feature_set) < 5:
            return # No point of training a model when there very features
        clf = LogisticRegression(C=10)
        clf.fit(transformed, y)
        
        res_on_training = clf.predict_proba(transformed)
        
        joblib.dump(clf, self.get_model_file(analysis_id))
        joblib.dump(vectorizer, self.get_vectorizer_file(analysis_id))
        joblib.dump(categories_list, self.get_class_list_file(analysis_id))

        # TODO: It might be possible to speed up the training by using a recently trained model to start with
        # investigate if training is slow
        return None
    
    def rank_according_to_topic_connection(self, document_id, sorted_themes, potential_theme_dict):
        # Get the themes which other documents that belong to the same topic as the current document belong to
        
        potiential_themes_given_topic_connections = set(potential_theme_dict[int(document_id)])
        #print("potiential_themes_given_topic_connections", potiential_themes_given_topic_connections)
        
        # Rank those which have a connection to other documents with the same topic first
        ranked_according_to_topic_connection = []
        ranked_only_machine_learning = []
        for theme in sorted_themes:
            if str(theme) in potiential_themes_given_topic_connections:
                ranked_according_to_topic_connection.append(theme)
            else:
                ranked_only_machine_learning.append(theme)
        #print("ranked_according_to_topic_connection", ranked_according_to_topic_connection)
        #print("ranked_only_machine_learning", ranked_only_machine_learning)
        sorted_themes_using_topic_connection = ranked_according_to_topic_connection + ranked_only_machine_learning

        print("sorted_themes", sorted_themes)
        print("sorted_themes_using_topic_connection", sorted_themes_using_topic_connection)
        return sorted_themes_using_topic_connection

    def rank_themes_for_document(self, analysis_id, document_id):
        themes = self.mongo_connector.get_saved_themes(analysis_id)
        all_theme_nrs = sorted([int(theme[THEME_NUMBER]) for theme in themes])
        
        document_dict, potential_theme_dict = self.mongo_connector.get_documents_for_analysis(analysis_id)
        
        # No trained model available, return themes sorted according to theme number
        if not os.path.exists(self.get_model_file(analysis_id)) or \
                not os.path.exists(self.get_vectorizer_file(analysis_id)) or \
                    not os.path.exists(self.get_class_list_file(analysis_id)):
            sorted_themes_using_topic_connection = self.rank_according_to_topic_connection(document_id, all_theme_nrs, potential_theme_dict)
            default_themes_str = [str(theme) for theme in sorted_themes_using_topic_connection]
            print("no classifier trained for " + str(analysis_id))
            return default_themes_str
        
        clf = joblib.load(self.get_model_file(analysis_id))
        vectorizer = joblib.load(self.get_vectorizer_file(analysis_id))
        classes = joblib.load(self.get_class_list_file(analysis_id))
    
        data = [document_dict[int(document_id)]]
        transformed = vectorizer.transform(data)
        classifications = clf.predict_proba(transformed)
        sorted_prob_themes = sorted([(prob, theme_nr) for prob, theme_nr in zip(classifications[0], classes)], reverse = True)
        sorted_themes = [int(theme_nr) for (prob, theme_nr) in sorted_prob_themes]
        
        sorted_themes_using_topic_connection = self.rank_according_to_topic_connection(document_id, sorted_themes, potential_theme_dict)

        for theme in all_theme_nrs: # themes that have no associate documents or description, and therefore aren't classifier ranked, are ranked as last
            if theme not in sorted_themes_using_topic_connection:
                sorted_themes_using_topic_connection.append(theme)
        themes_str = [str(theme) for theme in sorted_themes_using_topic_connection]
        return themes_str

if __name__ == '__main__':
    mc = MongoConnector()
    ts = ThemeSorter(mc)
    ts.retrain_model("5ba3977599a029238042ecf3")
    print(ts.rank_themes_for_document("5ba3977599a029238042ecf3", "682"))
    print(ts.rank_themes_for_document("5ba3977599a029238042ecf3", "480"))
    print(ts.rank_themes_for_document("5ba3977599a029238042ecf3", "1033"))
    print(ts.rank_themes_for_document("5ba3977599a029238042ecf3", "627"))
    print(ts.rank_themes_for_document("5ba3977599a029238042ecf3", "14"))
