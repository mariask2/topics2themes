from sklearn.feature_extraction.text import CountVectorizer
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

def replace_with_synonym(line):
    line = line.replace("(", " ( ").replace(")", " ) ")
    words = line.split(" ")
    to_return = []
    for word in words:
        if word.lower() in synonym_dict:
            to_return.append(synonym_dict[word.lower()])
        else:
            to_return.append(word)
    return " ".join(to_return)
    
def run_classifier(filename):
    category_dict = {}
    
    f = open(filename)
    lines  = f.readlines()
    f.close()

    data_lines = []
    categories = set()
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
        categories.add(csv[0].strip())

    data_list = list(data_set)
    data_list_preprocessed = []
    for el in data_list:
        preprocessed = replace_with_synonym(el)
        data_list_preprocessed.append(preprocessed)


    vectorizer = CountVectorizer(min_df=2,\
        ngram_range = (1, 3),\
        stop_words=stop_words_set,\
        binary = True)

    transformed = vectorizer.fit_transform(data_list_preprocessed)
    
    inversed = vectorizer.inverse_transform(transformed)
    """
    for el in inversed:
        print(el)
    """

    category_dict = {}
    category_dict_inversed = {}
    for (nr, el) in enumerate(sorted(list(categories))):
        category_dict[nr] = el
        category_dict_inversed[el] = nr


    found = 0
    not_found = 0

    found_baseline = 0
    not_found_baseline = 0
    for current_el in range(0, len(data_lines)):
        print(current_el)
        unknown_str = data_lines[current_el][1]
        unknown_classification = data_lines[current_el][0]
        training_data_y_x = data_lines[0 : current_el] + data_lines[current_el + 1:]
        if len(training_data_y_x) != len(data_lines) -1:
            print("splitting of data incorrect")
            exit(1)
        was_classification_correct = \
            classify_data(unknown_str, unknown_classification, training_data_y_x, vectorizer, category_dict, category_dict_inversed, sorted(list(categories)))
        if  was_classification_correct:
            found = found + 1
        else:
            not_found = not_found + 1
    print("found: " + str(found))
    print("not found: " + str(not_found))

    
def classify_data(unknown_str, unknown_classification, training_data_y_x, vectorizer, category_dict, category_dict_inversed, categories):

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

    if unknown_str in training_data_x_filtered_for_included:
        print( unknown_str + "included")
        exit(1)
        
    transformed = vectorizer.transform([replace_with_synonym(el) for el in training_data_x_filtered_for_included])

    """
    inversed = vectorizer.inverse_transform(transformed)
    for el in inversed:
        print(el)
    """
    
    clf = KNeighborsClassifier(weights="distance")
    clf.fit(transformed, training_data_y_filtered_for_included)

    transformed_test = vectorizer.transform([replace_with_synonym(unknown_str)])
    probs = clf.predict_proba(transformed_test)[0]
    print("*********")
    print(unknown_str)
    print("-------")
    most_likely = sorted([(prob, category_dict[nr]) for (nr, prob) in enumerate(probs)], reverse = True)[:NR_TOP_ELEMENTS]
    if unknown_classification in [likely for (prob, likely) in most_likely]:
        print(unknown_classification + " found in " + str( [likely for (prob, likely) in most_likely]))
        print("*****")
        return True
    else:
        print("INCORRECT CLASSIFICATION")
        print(unknown_classification + " should have been " + str( [likely for (prob, likely) in most_likely]))
        print("*****")
        return False

    
if __name__ == '__main__':
    run_classifier("classification_data/output_for_classification_topic1_annotated.txt")
    pass
