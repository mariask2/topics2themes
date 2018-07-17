import glob
import os
import json
import ast

def get_document_files(dir_to_inv):
    terms_doc = glob.glob(os.path.join(dir_to_inv, "*terms.txt"))
    terms_file = open(terms_doc[0])
    topic_strength_list = []
    current_topic_nr = -1
    for line in terms_file:
        line = line.strip()
        if line == "" or line == "----" or line == "********":
            continue
        if not line[0] == "[":
            current_topic_nr = int(line)
        else:
            line_as_list = eval(line)
            total_weight = 0
            for weight, el in line_as_list:
                total_weight = total_weight + float(weight)

            topic_strength_list.append((total_weight, current_topic_nr))

    topic_strength_list = sorted(topic_strength_list, reverse = True)
    print("topic_strength_list", topic_strength_list)


    working_dir = os.path.join(dir_to_inv, "*_documents_*.txt")


    topic_stance_taken_dict = {}
    for file_name  in glob.glob(working_dir):
        print()
        undecided = 0
        stance_taken = 0
        f = open(file_name)
        print("Reading from file ", file_name)
        topic_nr = int(file_name.split("_")[-1].replace(".txt", ""))
        print("topic_nr", topic_nr)
        for line in f.readlines()[:20]: # Only investigate the top 20 documents
            sp = line.strip().split("\t")
            if sp[2] == "undecided":
                undecided = undecided + 1
            elif sp[2] == "for" or sp[2] == "against":
                stance_taken = stance_taken + 1
            else:
                print("Unkonwn: " + sp[2])
                exit(1)
        print("nr of undecided",  undecided)
        print("nr of stance taken", stance_taken)
        percentage_stance = stance_taken/(undecided + stance_taken )
        print("percentage of stance taken", percentage_stance)
        topic_stance_taken_dict[topic_nr] = percentage_stance

    print(topic_stance_taken_dict)

    for strength_nr, (strength, orig_topic_nr) in enumerate(topic_strength_list):
        print(strength_nr, (strength, orig_topic_nr), topic_stance_taken_dict[orig_topic_nr])

    print("Topic & Stance (\\%) \\\\ \hline")
    for strength_nr, (strength, orig_topic_nr) in enumerate(topic_strength_list):
        print(str(strength_nr) + "&" +  str(int(100* topic_stance_taken_dict[orig_topic_nr])) + "\\\\")

###
# Start
###
if __name__ == '__main__':
    #DIRECTORY_TO_INVESTIGATE = "topic_model_evalutation/duetaltopicmodellingformat/1531055938.824244_standardstopwords"
    DIRECTORY_TO_INVESTIGATE = "topic_model_evalutation/mumsnet_scikitformat/1531055600.957539_standardstopwords"
    

    get_document_files(DIRECTORY_TO_INVESTIGATE)
