####
## Calculate the ceiling for the argument ranking experiment
####
import os

def count_data(filename):
    print("-----")
    print(filename)
    category_dict = {}
    
    f = open(filename)
    lines  = f.readlines()
    f.close()

    #the number of incorrect classifications are equal to c-n if c > n

    for rank in range(1,7):
        #print("\n=========")
        #print("rank", rank)
        total_correct = 0
        total_incorrect = 0
        total_classifications = 0
        for line in lines:

            found_classifications_for_text = 0
            csv = line.replace(u'\xa0', u' ').strip().split("\t")
            text = csv[0]
            if len(csv) > 1:
                for cat in csv[1:]:
                    if cat.strip() != "":
                        found_classifications_for_text = found_classifications_for_text + 1
                if found_classifications_for_text > rank:
                    incorrect_classifications = found_classifications_for_text - rank
                else:
                    incorrect_classifications = 0
                correct_classifications = found_classifications_for_text - incorrect_classifications
                total_correct = total_correct + correct_classifications
                total_incorrect = total_incorrect + incorrect_classifications
                total_classifications = total_classifications + found_classifications_for_text

        #print("total_classifications", total_classifications)
        #print("total_correct", total_correct)
        #print("total_incorrect", total_incorrect)
        #print("prop correct", total_correct/total_classifications)
        print("% correct", (round((total_correct/total_classifications)*100)), "&")
#print("correct:", correct_classifications, "incorrect:", incorrect_classifications)

if __name__ == '__main__':
   
    count_data(os.path.join("classification_data", "for_classification_topic0_annotated.txt"))
    
    count_data(os.path.join("classification_data", "for_classification_topic1_annotated.txt"))
    
    count_data(os.path.join("classification_data", "for_classification_topic2_annotated.txt"))

    count_data(os.path.join("classification_data", "for_classification_topic3_annotated.txt"))
    
    count_data(os.path.join("classification_data", "for_classification_topic4_annotated.txt"))

    count_data(os.path.join("classification_data", "for_classification_topic5_annotated.txt"))
    
    count_data(os.path.join("classification_data", "for_classification_all_topics_combined_annotated.txt"))

