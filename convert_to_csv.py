import os
import json
import csv

def convert_to_csv(json_topic_names, json_model):
    #print(json_model)
    topic_names_sorted = sorted(json_topic_names, key=lambda k: 'topic_id')
    header_list = []
    
    header_list.append("Keywords")
    header_list.append("Text")
    header_list.append("Your comments")
    header_list.append("Most common theme")
    header_list.append("2nd most common theme")
    header_list.append("Rest of themes")
    index_start_topics = len(header_list)
    
    id_index_dict = {}
    for nr, el in enumerate(topic_names_sorted):
        header_list.append(str(el['topic_id']) + ": " + el['topic_name'].strip())
        id_index_dict[int(el['topic_id'])] = nr
    
    index_end_topics = len(header_list)
    header_list.append("Filename")
    
    """
    with open('test_output.txt', 'w') as csvfile:
        csvwriter = csv.writer(csvfile, dialect='excel', delimiter="\t",
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(header_list)
    """
    
    outputfile = open('test_output.txt', 'w')
    to_write = "\t".join(header_list) + "\n"
    outputfile.write(to_write)
        
    for document in json_model["topic_model_output"]["documents"]:
        row_list = [""]*len(header_list)
        key_words = []
        for document_topic in document["document_topics"]:
            key_words.extend(document_topic['terms_found_in_text'])
            id_index = id_index_dict[document_topic['topic_index']]
            row_list[index_start_topics + id_index] = str(round(document_topic['topic_confidence'], 2)).replace(".",",") # Swedish Excel
        
        key_words = list(set(key_words))
        repr_terms = []
        for key_word in key_words:
            terms_to_pick_as_rep = []
            splitted_key_word = sorted(key_word.split("__"), key=len)
            terms_to_pick_as_rep.append(splitted_key_word[0])
            for splitted in splitted_key_word[1:]:
                add_splitted = True
                for existing_reps in terms_to_pick_as_rep[:]:
                    if (len(existing_reps) > 1 and existing_reps in splitted) or (len(existing_reps) > 3 and existing_reps[:-2] in splitted): # Adapted to only to suffixing lang.
                        add_splitted = False # Don't add a longer form of a word
                if add_splitted or "_" in splitted:
                    terms_to_pick_as_rep.append(splitted)
                 
            repr_terms.append("/".join(terms_to_pick_as_rep))
        
        row_list[0] = ", ".join(repr_terms)
        row_list[1] = document['text'].replace("\t", " ").replace("\n", " ").strip()
        row_list[index_end_topics] = document['base_name']
        
        to_write_row = "\t".join(row_list) + "\n"
        outputfile.write(to_write_row)
        
    outputfile.close()
        
if __name__ == '__main__':
    folder = "/Users/marsk757/topic2themes/topics2themes/data_folder/språk-tilltal-delat/topics2themes_exports_folder_created_by_system"
    model_nr = "61d9bbb060423d19911efd8a"
    
    
    topic_names = open(os.path.join(folder, model_nr + "_topic_name.json"), "r")
    
    model = open(os.path.join(folder, model_nr + "_model.json"), "r")
    
    json_topic_names = json.loads(topic_names.read())
    json_model = json.loads(model.read())

    topic_names.close()
    model.close()
    convert_to_csv(json_topic_names, json_model)
