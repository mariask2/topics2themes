import json
  
# Opening JSON file
f = open("/Users/marsk757/topic2themes/topics2themes/data_folder/climate-editorials-graph/topics2themes_exports_folder_created_by_system/602f89d39962f2a59e2653c4_theme.json")
  

data = json.load(f)

model_file = open("/Users/marsk757/topic2themes/topics2themes/data_folder/climate-editorials-graph/topics2themes_exports_folder_created_by_system/602f89d39962f2a59e2653c4_model.json")
model_data = json.load(model_file)


document_info = {}
for el in model_data["topic_model_output"]["documents"]:
    id = str(el["id"])
    base_name = el["base_name"]
    label = el["label"]
    document_strongest_topic = None
    for t in el["document_topics"]:
        topic_info = {}
        topic_info["terms_found_in_text"] = t["terms_found_in_text"]
        topic_info["topic_index"] = t["topic_index"]
        topic_info["topic_confidence"] = t["topic_confidence"]
        if not document_strongest_topic:
            document_strongest_topic = topic_info
        elif document_strongest_topic["topic_confidence"] < topic_info["topic_confidence"]:
            document_strongest_topic = topic_info
    document_info[id] = document_strongest_topic


frames = ["ECO", "DEV", "SEC", "ETH", "TEC", "GOV", "SCI", "COM"]

text_dict = {}
l = sorted([(len(i["document_ids"]), i["theme_name"], i["document_ids"]) for i in data], reverse=True)
for el in l:
    if el[0] > 1: # At least 2 occurrences of a theme
        topic_freq_dict = {}
        topic_list = []
        for id in el[2]:
            topic_id = int(document_info[id]["topic_index"])
            if topic_id not in topic_freq_dict:
                topic_freq_dict[topic_id] = 0
            topic_freq_dict[topic_id] = topic_freq_dict[topic_id] + 1
            topic_list.append(int(document_info[id]["topic_index"]))
        if len(topic_freq_dict.keys()) == 1:
            found_topics = "associated with \\underline{Topic~" + str(list(topic_freq_dict.keys())[0]) + "} "
        else:
            found_topics = "associated with "
            found_topics_list = []
            for key in sorted(topic_freq_dict.keys()):
                if topic_freq_dict[key] > 1:
                    found_topics_list.append("\\underline{Topic~" + str(key) + "} (" + str(topic_freq_dict[key]) + "~texts)")
                else:
                    found_topics_list.append("\\underline{Topic~" + str(key) + "} (" + str(topic_freq_dict[key]) + "~text)")
            found_topics = found_topics + ", ".join(found_topics_list)
                    
            #found_topics = found_topics + " " + ", ".join([str(e) for e in sorted(list(topic_list))])
        topic_string = "[" + found_topics  + "]"
      
        sp = el[1].split(":")
        frame = sp[0]
        if frame not in text_dict:
            text_dict[frame] = []
        
        text = ":".join(sp[1:])
        text = text.replace("e.g.", "e.g.\\")

        if "[NEW]" in text:
            text = text.replace("[NEW]", "")
            text = text.replace(". .", ".")
            text = text.replace(". .", ".")
            text = text.strip()
            if text[-1] == ".":
                text = text[0:-1]
            text = "{\\bf " + text + "}"
        
        if "[CHANGED]" in text:
            text = text.replace("[CHANGED]", "")
            text = text.replace(". .", ".")
            text = text.replace(". .", ".")
            text = text.strip()
            #print(text, text[-1])
            if text[-1] == ".":
                text = text[0:-1]
            text = "\\emph{" + text + "}"
        
        text = text.strip()
        if text[-1] == ".":
            text = text[0:-1]
        text_dict[frame].append(text.strip() + " [in " + str(el[0]) + "~texts] " + topic_string + ".")
        

        
for el in frames:
    if el in text_dict:
        el_print = el
        if el_print == "SCI":
            el_print = "SCI~"
        
        #if el_print == "ECO":
        #    el_print = "ECON"
        #if el_print == "TEC":
        #    el_print = "TECH"
        #TODO: more roman
        text_list_print = []
        #for s, nr in zip(text_dict[el], ["i", "ii", "iii", "iv", "v", "vi", "vii", "ix", "x"]):
        for s, nr in zip(text_dict[el], ["--"]*10):
            text_list_print.append(nr + " " + s)
        print("\item[" + el_print + "] " + " \\\\".join(text_list_print))

for t in text_dict["NEW"]:
    print("\item[" + "NEW" + "] " + "-- " + t)
# Closing file
f.close()
