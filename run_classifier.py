from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.feature_extraction import text
from topic_model_configuration import *
import os

TOP_ELEMENTS_RANGE = [1, 2, 3, 4, 5, 6]

f = open(STOP_WORD_FILE)
additional_stop_words = [word.strip() for word in f.readlines()]
f.close()
stop_words_set = text.ENGLISH_STOP_WORDS.union(additional_stop_words)

synonym_dict = {}
synonyms = open("clustered_words_machine_learning.txt")
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
    
def run_classifier(filename, use_synonyms, output_path):    
    f = open(filename)
    lines  = f.readlines()
    f.close()

    output_filename_base =  "synonyms_" + str(use_synonyms) + "_" + os.path.basename(filename) 
    output_filename = os.path.join(output_path, output_filename_base)
    output_file = open(output_filename, "w")

    output_filename_base_detailed =  "detailed_" + output_filename_base
    output_filename_detailed = output_filename = os.path.join(output_path, output_filename_base_detailed)
    output_file_detailed = open(output_filename, "w")
    
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

    feature_set = set()
    inversed = vectorizer.inverse_transform(transformed)
    output_file.write("Features used: \n")
    for el in inversed:
        output_file.write(str(el) + "\n" )

    output_file.write("\n Number of features: " + str(len(vectorizer.get_feature_names())) + "\n")
    output_file.write("\n Number of stop words used: " + str(len(set(stop_words_set))) + "\n")
    
    
    category_dict = {}
    category_dict_inversed = {}
    for (nr, el) in enumerate(sorted(list(count_categories_dict.keys()))):
        category_dict[nr] = el
        category_dict_inversed[el] = nr

    found_logr = {}
    not_found_logr = {}
    found_baseline = {}
    not_found_baseline = {}

    for el in TOP_ELEMENTS_RANGE:
        found_logr[el] = 0
        not_found_logr[el] = 0
        found_baseline[el] = 0
        not_found_baseline[el] = 0

    for current_el in range(0, len(data_lines)):
        count_categories_dict_training_data_specific = {}
        unknown_str = data_lines[current_el][1]
        gold_standard_classification = data_lines[current_el][0]
        if count_categories_dict[gold_standard_classification] < 2:
        # The categories that only occur once can not be included in the evaluation (but still as a category among which to chose from)
            continue
        before_current = data_lines[0 : current_el]
        after_current = data_lines[current_el + 1:]
        training_data_y_x_unfiltered = before_current + after_current
        training_data_y_x = []
        for [y,x] in training_data_y_x_unfiltered:            
            if x != unknown_str: # Don't use the classifications from the current text in the training.
                training_data_y_x.append([y,x])
                if y not in count_categories_dict_training_data_specific:
                    count_categories_dict_training_data_specific[y] = 0
                count_categories_dict_training_data_specific[y] = count_categories_dict_training_data_specific[y] + 1
                
        most_likely_logr =  classify_data_logisticregression(unknown_str, gold_standard_classification, training_data_y_x, vectorizer, category_dict, category_dict_inversed, count_categories_dict, use_synonyms)

        most_likely_baseline = baseline_classify(gold_standard_classification, count_categories_dict_training_data_specific)

        for top_nr in TOP_ELEMENTS_RANGE:
            was_logr_classification_correct = is_clossification_correct(most_likely_logr[:top_nr],\
                gold_standard_classification,\
                top_nr,\
                unknown_str,\
                count_categories_dict,\
                output_file_detailed,\
                "logistic regression")
            if was_logr_classification_correct:
                found_logr[top_nr] = found_logr[top_nr] + 1
            else:
                not_found_logr[top_nr] = not_found_logr[top_nr] + 1

            was_baseline_correct = is_clossification_correct(most_likely_baseline[:top_nr],\
                gold_standard_classification,\
                top_nr,\
                unknown_str,\
                count_categories_dict,\
                output_file_detailed,\
                "baseline") 
            if  was_baseline_correct:
                found_baseline[top_nr] = found_baseline[top_nr] + 1
            else:
                not_found_baseline[top_nr] =  not_found_baseline[top_nr] + 1

                
    output_file.write("\nfilename: " + " " +  filename  + " " +   "use_synonyms:"  + " " +   str(use_synonyms) + " " + "nr of cat:" +\
                     " " + str(len(count_categories_dict.keys())) + " " + str(count_categories_dict) + "\n")
    output_file.write("************\n")
    output_file.write("Top nr of elements. \t")
    print_found("found_logr", "not_found_logr", "logistic regression", "top_nr", "use_synonyms_" + str(use_synonyms), output_file)
    print_found("found_base", "not_found_base", "baseline", "top_nr", "use_synonyms_"  + str(use_synonyms) , output_file)
    output_file.write("\n----------------------------\n")
    for top_nr in TOP_ELEMENTS_RANGE:
        output_file.write("Top " + str(top_nr) + " elements. \t")
        #print_found(found[top_nr], not_found[top_nr], "knearest", top_nr, output_file)
        print_found(found_logr[top_nr], not_found_logr[top_nr], "logistic", top_nr,  use_synonyms, output_file)
        print_found(found_baseline[top_nr], not_found_baseline[top_nr], "baseline",  use_synonyms, top_nr, output_file)
        output_file.write("\n\n")
        
    output_file.close()
    output_file_detailed.close()
        
def print_found(found, not_found, name, top_nr, use_synonyms, output_file):
    try:
        per_found = found/(found + not_found)
    except TypeError:
        per_found = "% found " + name + " " + str(use_synonyms)
    output_file.write(name + "\t" + "    found:" + "\t" + str(found)  + "\t")
    output_file.write(name + "\t" + "not found:" +  "\t"  + str(not_found) + "\t")
    output_file.write(name + "\t" + "% found:" +  "\t"  + str(per_found) + "\t")
    
    
def baseline_classify(gold_standard_classification, count_categories_dict_training_data_specific):
    most_common_training_data_specific = sorted([(value,key) for (key, value) in count_categories_dict_training_data_specific.items()], reverse=True)
    return most_common_training_data_specific

    
def classify_data_logisticregression(unknown_str,  gold_standard_classification, training_data_y_x, vectorizer, category_dict, category_dict_inversed, count_categories_dict, use_synonyms):
    transformed, training_data_y_filtered_for_included, transformed_test, categories = \
        get_transformed_data(unknown_str, training_data_y_x, vectorizer, count_categories_dict, category_dict_inversed, use_synonyms)

    clf = LogisticRegression(C=10.0)
    clf.fit(transformed, training_data_y_filtered_for_included)

    probs = clf.predict_proba(transformed_test)[0]
    #print("-------")
    #print(probs)
    most_likely = sorted([(prob, category_dict[nr]) for (nr, prob) in enumerate(probs)], reverse = True)
    return most_likely


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
    
    print(unknown_str)
"""

    transformed_test = vectorizer.transform([replace_with_synonym(unknown_str, use_synonyms)])
    
    return transformed, training_data_y_filtered_for_included, transformed_test, categories


def is_clossification_correct(most_likely, gold_standard_classification, top_nr, unknown_str, count_categories_dict, output_file, classification_type = None):
    if gold_standard_classification in [likely for (prob, likely) in most_likely]:
        if classification_type:
            output_file.write("CORRECT"  + "\t" +  gold_standard_classification + "\t" + classification_type + "\t"\
                              + str(count_categories_dict[gold_standard_classification]) + "\t" + str(top_nr)   + "\t" + str(most_likely) + "\t" + unknown_str + "\n")
        return True
    else:
        if classification_type:
            output_file.write("INCORRECT"  + "\t" +  gold_standard_classification + "\t" + classification_type + "\t"\
                              +  str(count_categories_dict[gold_standard_classification]) + "\t" + str(top_nr)   + "\t" + str(most_likely) + "\t" + unknown_str + "\n")
        return False    

def start_classification():
    output_path_base = "machine_learning_results"
    if not os.path.exists(output_path_base):
        os.makedirs(output_path_base)
    for topic_nr in range(0,6):
        for min_occ in range(1, 2):
            output_path = os.path.join(output_path_base, "min_occ_" + str(min_occ))
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            for include_clusters in [True, False]:
                run_classifier("classification_data/output_" + str(min_occ) + "_for_classification_topic" + str(topic_nr) + "_annotated.txt",\
                               include_clusters, output_path)



if __name__ == '__main__':
    start_classification()
    

    
