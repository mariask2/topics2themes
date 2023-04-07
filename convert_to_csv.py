import os
import json
import csv
import glob

# An import that should function both locally and when running an a remote server
try:
    from environment_configuration import *
except:
    from topics2themes.environment_configuration import *

if RUN_LOCALLY:
    from topic_model_constants import *
else:
    from topics2themes.topic_model_constants import *
    
def fill_zero(str):
    while len(str) < 4:
        str = "0" + str
    return str

def convert_to_csv(json_topic_names, json_model, json_themes, folder, model_nr, convert_not_covered = False, files_folder = None):

    all_found_terms = set()
    
    document_theme_dict = {}
    for theme_el in json_themes:
        for document_id in theme_el['document_ids']:
            if document_id not in document_theme_dict:
                document_theme_dict[document_id] = []
            document_theme_dict[document_id].append(theme_el)
            
    topic_names_sorted = sorted(json_topic_names, key=lambda k: 'topic_id')
    header_list = []
    
    header_list.append("Keywords")
    header_list.append("Text")
    header_list.append("Your theme")
    header_list.append("Most common theme")
    header_list.append("2nd most common theme")
    header_list.append("3rd most common theme")
    header_list.append("Rest of themes")
    index_start_topics = len(header_list)
    
    id_index_dict = {}
    for nr, el in enumerate(json_model["topic_model_output"]["topics"]):

        id_index_dict[int(el["id"])] = nr
        header_list.append(str(el["label"]))

    # TODO: Perhaps put user-defined names back
    """
    for nr, el in enumerate(topic_names_sorted):
        print(nr, el)
        header_list.append(el['topic_name'].strip())
        id_index_dict[int(el['topic_id'])] = nr
    """
    
    index_end_topics = len(header_list)
    header_list.append("Filename")
    header_list.append("Additional labels")
    result_matrix = []
    result_matrix.append(header_list)
    #    to_write = "\t".join(header_list) + "\n"
    #result_write.writerows(
    #outputfile.write(to_write)
        
    included_file_names = set()
    for document in json_model["topic_model_output"]["documents"]:
        
        row_list = [""]*len(header_list)
        
        #themes
        if str(document['id']) in document_theme_dict:
            themes_sorted = sorted(document_theme_dict[str(document['id'])], key=lambda x: len((x['document_ids'])), reverse = True)
            row_list[3] = fill_zero(str(len(themes_sorted[0]['document_ids']))) + " occ: " +  themes_sorted[0]['theme_name']
            if len(themes_sorted) > 1:
                row_list[4] = fill_zero(str(len(themes_sorted[1]['document_ids']))) + " occ: " + themes_sorted[1]['theme_name']
            if len(themes_sorted) > 2:
                row_list[5] = fill_zero(str(len(themes_sorted[2]['document_ids']))) + " occ: " + themes_sorted[2]['theme_name']
            if len(themes_sorted) > 3:
                row_list[6] = " / ".join([fill_zero(str(len(t['document_ids']))) + " occ: " + t['theme_name'] for t in themes_sorted[3:]])
        #key words and topics
        key_words = []
        for document_topic in document["document_topics"]:
            key_words.extend(document_topic['terms_found_in_text'])
            id_index = id_index_dict[document_topic["topic_index"]]
            row_list[index_start_topics + id_index] = str(round(document_topic['topic_confidence'], 2)).replace(".",",") # Swedish Excel
        
        additonals = [additional for additional in document["additional_labels"]]
        row_list.extend(additonals)
        
        key_words = list(set(key_words))
        repr_terms = []
        for key_word in key_words:
            terms_to_pick_as_rep = []
            splitted_key_word = sorted(key_word.split("__"), key=len, reverse=True)
            for splitted in splitted_key_word:
                if splitted.replace("_", " ") in document['text'].lower() or splitted in document['text'].lower():
                    if len(terms_to_pick_as_rep) == 0:
                        terms_to_pick_as_rep.append(splitted)
                    else:
                        add_splitted = True
                        for existing_reps in terms_to_pick_as_rep[:]:
                            if splitted in existing_reps and " " + splitted + " " not in " " + document['text'].lower().replace(",", " ,").replace(".", " ."):
                                add_splitted = False
                        if add_splitted:
                            terms_to_pick_as_rep.append(splitted)
                        
            if len(terms_to_pick_as_rep) == 0:
                # If no keywords found, add all words
                print("No keywords found in document", splitted_key_word, document['text'].lower())
                terms_to_pick_as_rep = splitted_key_word
                     
            for stat_term in terms_to_pick_as_rep:
                all_found_terms.add(stat_term)
            repr_terms.append("/".join(terms_to_pick_as_rep))
        
        row_list[0] = ", ".join(sorted(repr_terms))
        
        #text
        row_list[1] = document['text'].replace("\t", " ").replace("\n", " ").strip()
        
        #name of text
        row_list[index_end_topics] = document['base_name'].replace(".txt", "")
        
        #to_write_row = "\t".join(row_list) + "\n"
        #outputfile.write(to_write_row)
        result_matrix.append(row_list)
        
        included_file_names.add(document['base_name'])
    
    output_file_name = os.path.join(folder, model_nr + "_tab_separated.csv")
    print("To access the output files write: ")
    print("open " + output_file_name)
    outputfile = open(output_file_name, 'w')
    result_writer = csv.writer(outputfile, dialect="excel-tab")
    result_writer.writerows(result_matrix)
    
    # TODO: Check if this works
    if convert_not_covered:
        file_names = glob.glob(os.path.join(files_folder, "*.txt"))
        file_name_text_dict = {}
        for file_name in file_names:
            with open(file_name) as f:
                file_name_text_dict[os.path.basename(file_name)] = f.read()
            
        not_covered = set(file_name_text_dict.keys()) - included_file_names
        for file_name in list(not_covered):
            row_list = [""]*len(header_list)
            row_list[index_end_topics] = file_name.replace(".txt", "")
            row_list[1] = file_name_text_dict[file_name].replace("\t", " ").replace("\n", " ").strip()
            to_write_row = "\t".join(row_list) + "\n"
            outputfile.write(to_write_row)
    
    outputfile.close()
    return all_found_terms
        
def convert_topics_to_csv(json_model, folder, model_nr, all_terms_found_in_texts):
    output_file_name_terms = os.path.join(folder, model_nr + "_topic_terms.csv")
    outputfile_terms = open(output_file_name_terms, 'w')
    
    term_result_matrix = []
    for nr, topic in enumerate(json_model["topic_model_output"]["topics"]):
        term_result_matrix.append(["Topic-nr:-" + str(nr) + "-Topic-id:-" + str(topic["id"])])
        term_result_matrix.append([])
        for term in topic["topic_terms"]:
            terms_to_keep = []
            ind_terms = term["term"].split(" / ")
            for ind_term in ind_terms:
                if ind_term in all_terms_found_in_texts:
                    terms_to_keep.append(ind_term)
                    if "_" in ind_term:
                        print(ind_term)
            term_result_matrix.append([" / ".join(terms_to_keep), term["score"]])
        term_result_matrix.append([])
        term_result_matrix.append([])
    terms_writer = csv.writer(outputfile_terms, dialect="excel-tab")
    terms_writer.writerows(term_result_matrix)
    
    print("open " + output_file_name_terms)
    outputfile_terms.close()
    
def do_csv_export(folder_base, model_nr, convert_not_covered = False, files_folder = None):

    folder = os.path.join(folder_base, EXPORT_DIR)
    
    topic_names = open(os.path.join(folder, model_nr + "_topic_name.json"), "r")
    
    model = open(os.path.join(folder, model_nr + "_model.json"), "r")
    
    themes = open(os.path.join(folder, model_nr + "_theme.json"), "r")
    
    json_topic_names = json.loads(topic_names.read())
    json_model = json.loads(model.read())
    json_themes = json.loads(themes.read())
    
    topic_names.close()
    model.close()
    themes.close()
    all_terms_found_in_texts = convert_to_csv(json_topic_names, json_model, json_themes, folder, model_nr, convert_not_covered, files_folder)
    
    print("Found collocations: ")
    for t in list(all_terms_found_in_texts):
        if "_" in t:
            print(t)
            
    convert_topics_to_csv(json_model, folder, model_nr, all_terms_found_in_texts)

if __name__ == '__main__':
    folder="/Users/marsk757/topics2themes/topics2themes/data_folder/framtidens-kultur_automatiskt/"
    model_nr = "63f800a8e74686ed89f702f6"
    
    do_csv_export(folder, model_nr)
