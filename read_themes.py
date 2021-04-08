import json
  
# Opening JSON file
f = open("/Users/marsk757/topic2themes/topics2themes/data_folder/climate-editorials-graph/topics2themes_exports_folder_created_by_system/602f89d39962f2a59e2653c4_theme.json")
  

data = json.load(f)

model_file = open("/Users/marsk757/topic2themes/topics2themes/data_folder/climate-editorials-graph/topics2themes_exports_folder_created_by_system/602f89d39962f2a59e2653c4_model.json")
model_data = json.load(model_file)




frames = ["ECO", "DEV", "SEC", "ETH", "TEC", "GOV", "SCI", "COM"]

text_dict = {}
l = sorted([(len(i["document_ids"]), i["theme_name"]) for i in data], reverse=True)
for el in l:
    if el[0] > 1: # At least 2 occurrences of a theme
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
        text_dict[frame].append(text.strip() + " [in " + str(el[0]) + " texts].")
  
for el in frames:
    if el in text_dict:
        el_print = el
        if el_print == "ECO":
            el_print = "ECON"
        if el_print == "TEC":
            el_print = "TECH"
        print("\item[" + el_print + "] " + " ".join(text_dict[el]))

for t in text_dict["NEW"]:
    print("\item[" + "NEW" + "] " + t)
# Closing file
f.close()
