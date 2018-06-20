import glob
import os

def get_document_files(dir_to_inv):
    working_dir = os.path.join(dir_to_inv, "*_documents_*.txt")
    print(working_dir)
    undecided = 0
    stance_taken = 0
    undecided_list = []
    stance_taken_list = []
    undecided_list_per = []
    result_summary = {}
    for file_name  in glob.glob(working_dir):
        f = open(file_name)
        print("Reading from file ", file_name)
        for nr, line in enumerate(f.readlines()):
            print(nr)
            if not nr in result_summary:
                result_summary[nr] = []
            sp = line.strip().split("\t")
            if sp[2] == "undecided":
                undecided = undecided + 1
            elif sp[2] == "for" or sp[2] == "against":
                stance_taken = stance_taken + 1
            else:
                print("Unkonwn: " + sp[2])
                exit(1)
            undecided_list.append(undecided)
            stance_taken_list.append(stance_taken)
            undecided_list_per.append(undecided/(undecided + stance_taken))
            result_summary[nr].append(undecided/(undecided + stance_taken))

        for undecided, stance_taken, per in zip(undecided_list, stance_taken_list, undecided_list_per):
            print(undecided, stance_taken, per)
        print("*******")
        print()
        for key in sorted(result_summary.keys()):
            print(key, sum(result_summary[key])/len(result_summary[key]), result_summary[key])
###
# Start
###
if __name__ == '__main__':
    DIRECTORY_TO_INVESTIGATE = "topic_model_evalutation/mumsnet_scikitformat/1529510050.402936"

    get_document_files(DIRECTORY_TO_INVESTIGATE)
