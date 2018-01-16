from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.feature_extraction import text
from topic_model_configuration import *

NR_TOP_ELEMENTS = 3

f = open(STOP_WORD_FILE)
additional_stop_words = [word.strip() for word in f.readlines()]
f.close()
stop_words_set = text.ENGLISH_STOP_WORDS.union(additional_stop_words)

synonym_dict = {}
synonyms = open("clustered_word_7.txt")
for line in synonyms.readlines():
    for word in line.strip().split("__"):
        synonym_dict[word] = line.strip()

#print(synonym_dict)
    
synonyms.close()

def replace_with_synonym(line, use_synonyms):
    line = line.replace("(", " ( ").replace(")", " ) ")
    if use_synonyms:
        words = line.split(" ")
        to_return = []
        for word in words:
            if word.lower() in synonym_dict:
                to_return.append(synonym_dict[word.lower()])
            else:
                to_return.append(word)
        return " ".join(to_return)
    return line
    
def run_classifier(filename, use_synonyms):    
    f = open(filename)
    lines  = f.readlines()
    f.close()

    output_file = open("tempfile.txt", "w")

    data_lines = []

    count_categories_dict = {}
    data_set = set()
    for line in lines:
        csv = line.replace(u'\xa0', u' ').strip().split("\t")
        data_lines.append(csv)
        if len(csv) != 2:
            print("Wrong format")
            exit(1)
        for cat in csv:
            element = cat.strip()
            data_set.add(element)

        category = csv[0].strip()
        if category not in count_categories_dict:
            count_categories_dict[category] = 1
        else:
            count_categories_dict[category] = count_categories_dict[category] + 1

    data_list = list(data_set)
    data_list_preprocessed = []
    for el in data_list:
        preprocessed = replace_with_synonym(el, use_synonyms)
        data_list_preprocessed.append(preprocessed)

    vectorizer = CountVectorizer(min_df=2,\
        ngram_range = (1, 1),\
        stop_words=stop_words_set,\
        binary = True)

    transformed = vectorizer.fit_transform(data_list_preprocessed)
    
    inversed = vectorizer.inverse_transform(transformed)
    output_file.write("Features used: \n")
    for el in inversed:
        output_file.write(str(el) + "\n" )

    category_dict = {}
    category_dict_inversed = {}
    for (nr, el) in enumerate(sorted(list(count_categories_dict.keys()))):
        category_dict[nr] = el
        category_dict_inversed[el] = nr


    found = 0
    not_found = 0

    found_logr = 0
    not_found_logr = 0


    found_baseline = 0
    not_found_baseline = 0
    
    for current_el in range(0, len(data_lines)):
        unknown_str = data_lines[current_el][1]
        gold_standard_classification = data_lines[current_el][0]
        training_data_y_x = data_lines[0 : current_el] + data_lines[current_el + 1:]
        if len(training_data_y_x) != len(data_lines) -1:
            print("splitting of data incorrect")
            exit(1)
        was_logr_classification_correct = \
            classify_data_logisticregression(unknown_str, gold_standard_classification, training_data_y_x, vectorizer, category_dict, category_dict_inversed, count_categories_dict, use_synonyms)
        if was_logr_classification_correct:
            found_logr = found_logr + 1
        else:
            not_found_logr = not_found_logr + 1
            
        was_classification_correct = \
            classify_data_nearest_k(unknown_str, gold_standard_classification, training_data_y_x, vectorizer, category_dict, category_dict_inversed, count_categories_dict, use_synonyms)
        if  was_classification_correct:
            found = found + 1
        else:
            not_found = not_found + 1

        was_baseline_correct = \
             baseline_classify(gold_standard_classification, count_categories_dict)
        if  was_baseline_correct:
            found_baseline = found_baseline + 1
        else:
             not_found_baseline =  not_found_baseline + 1

    print_found(found, not_found, "knearest")
    print_found(found_logr, not_found_logr, "logistic")
    print_found(found_baseline, not_found_baseline, "baseline")
    
def print_found(found, not_found, name):
    per_found = found/(found + not_found)
    print("---")
    print(name + "\t" + "    found:" + "\t" + str(found))
    print(name + "\t" + "not found:" +  "\t"  + str(not_found))
    print(name + "\t" + "% found:" +  "\t"  + str(per_found))
    
    
def baseline_classify(gold_standard_classification, count_categories_dict):
    most_common = sorted([(item, key) for (key, item) in count_categories_dict.items()], reverse=True)[:NR_TOP_ELEMENTS]
    return is_clossification_correct(most_common, gold_standard_classification)

    
def classify_data_nearest_k(unknown_str,  gold_standard_classification, training_data_y_x, vectorizer, category_dict, category_dict_inversed, count_categories_dict, use_synonyms):
    transformed, training_data_y_filtered_for_included, transformed_test, categories = \
        get_transformed_data(unknown_str, training_data_y_x, vectorizer, count_categories_dict, category_dict_inversed, use_synonyms)

    most_likely = None
    for k in range(2, 10):
        most_likely =  classify_kneighbor(vectorizer, transformed, training_data_y_filtered_for_included, transformed_test, category_dict, k)
        for prob, likely in most_likely:
            if count_categories_dict[likely] < k:
                print(k)
                return is_clossification_correct(most_likely, gold_standard_classification)
    print("outside of loop")
    return is_clossification_correct(most_likely, gold_standard_classification)

def classify_data_logisticregression(unknown_str,  gold_standard_classification, training_data_y_x, vectorizer, category_dict, category_dict_inversed, count_categories_dict, use_synonyms):
    transformed, training_data_y_filtered_for_included, transformed_test, categories = \
        get_transformed_data(unknown_str, training_data_y_x, vectorizer, count_categories_dict, category_dict_inversed, use_synonyms)

    clf = LogisticRegression(C=10.0)
    clf.fit(transformed, training_data_y_filtered_for_included)

    probs = clf.predict_proba(transformed_test)[0]
    print("-------")
    print(probs)
    most_likely = sorted([(prob, category_dict[nr]) for (nr, prob) in enumerate(probs)], reverse = True)[:NR_TOP_ELEMENTS]
    print(most_likely)
    return is_clossification_correct(most_likely, gold_standard_classification)


def get_transformed_data(unknown_str, training_data_y_x, vectorizer, count_categories_dict, category_dict_inversed, use_synonyms):
    categories = sorted(list(count_categories_dict.keys()))
    # Add the description of categories to the training data, as these give a clue what the category is about as well
    training_data_x = [x for (y, x) in training_data_y_x] + categories 
    training_data_y = [category_dict_inversed[y] for (y, x) in training_data_y_x] + [category_dict_inversed[el] for el in categories]

    training_data_x_filtered_for_included = []
    training_data_y_filtered_for_included = []

    for x, y in zip(training_data_x, training_data_y):
        if x == unknown_str: # Some have several classifications. Don't include these in the training data.
            pass
        else:
            training_data_x_filtered_for_included.append(x)
            training_data_y_filtered_for_included.append(y)
       
    transformed = vectorizer.transform([replace_with_synonym(el, use_synonyms) for el in training_data_x_filtered_for_included])

    """
    inversed = vectorizer.inverse_transform(transformed)
    for el in inversed:
        print(el)
    """
    print("*********")
    print(unknown_str)
    transformed_test = vectorizer.transform([replace_with_synonym(unknown_str, use_synonyms)])
    
    return transformed, training_data_y_filtered_for_included, transformed_test, categories

def classify_kneighbor(vectorizer, transformed, training_data_y_filtered_for_included, transformed_test, category_dict, n_neighbors):
    clf = KNeighborsClassifier(weights="distance")
    clf.fit(transformed, training_data_y_filtered_for_included)

    #print(inversed_test)
    probs = clf.predict_proba(transformed_test)[0]
    print("-------")
    most_likely = sorted([(prob, category_dict[nr]) for (nr, prob) in enumerate(probs)], reverse = True)[:NR_TOP_ELEMENTS]
    return most_likely

def is_clossification_correct(most_likely, gold_standard_classification):
    if gold_standard_classification in [likely for (prob, likely) in most_likely]:
        print(gold_standard_classification + " found in " + str( [likely for (prob, likely) in most_likely]))
        print("*****")
        return True
    else:
        print("INCORRECT CLASSIFICATION")
        print(gold_standard_classification + " should have been " + str( [likely for (prob, likely) in most_likely]))
        print("*****")
        return False    
    
if __name__ == '__main__':
    run_classifier("classification_data/output_2_for_classification_topic1_annotated.txt", True)
    #run_classifier("classification_data/output_for_classification_topic2_annotated.txt")
    
