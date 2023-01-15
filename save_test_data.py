from sklearn.datasets import fetch_20newsgroups
import pandas as pd

TEXT = "text"
file_name = "newsgroups_test.pkl"
LARGE_SET_SIZE = 50

def get_data():
    newsgroups_train = fetch_20newsgroups()
    data = newsgroups_train.data
    text_list = []
    for el in data:
        el = el.replace("\n", " ")
        sentences = el.split(". ")
        for s in sentences:
            if s.strip() != "":
                text_list.append(s.strip())
                
    print("Nr of sentences: ", len(text_list))
    larger_list = []
    for i in range(0, LARGE_SET_SIZE):
        larger_list.extend(text_list)
    print("Nr of sentences in larger list: ", len(larger_list))
        
    text_dict = {TEXT: larger_list}
    df = pd.DataFrame(text_dict)
    print("Original dataframe: ")
    print(df)
    print()
    
    df.to_pickle(file_name)
    read_df = pd.read_pickle(file_name)
    print("Read dataframe: ")
    print(read_df)
    
    print("Back to list: ")
    read_list = read_df[TEXT].tolist()
    print("Now as: ", type(read_list))
    print("Nr of sentences: ", len(read_list))
    
    
    
    nr_of_new_york = 0
    for el in read_list:
        if "New York" in el:
            nr_of_new_york = nr_of_new_york + 1
    print("Nr of times New York is mentioned:", nr_of_new_york)

def read_documents(data_label_list, data_set_name, cleaning_method, n_gram_length_conf, remove_duplicates):
    meta_data_list = None # No metadata
    
    read_df = pd.read_pickle(file_name)
    print("Read dataframe: ")
    print(read_df)
    
    print("Back to list: ")
    read_list = read_df["text"].tolist()
    print("Now as: ", type(read_list))
    print("Nr of sentences: ", len(read_list))
    
    return read_list, meta_data_list
    
get_data()
read_list, meta_data_list = read_documents(None, None, None, None, False)
print("Nr of sentences: ", len(read_list))
# Creating from dict of list

