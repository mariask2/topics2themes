import json

TEMP_FILE = "temp_term_dump.txt"
class TermVisualiser:
    
    def __init__(self):
        self.termdict_dict = {}

    def add_terms(self, term_dict, nr):
        self.termdict_dict[nr] = term_dict

    def dump_term_dict(self):
        j = json.dumps(self.termdict_dict)
        f = open(TEMP_FILE, "w")
        f.write(j)
        f.close()
    
    def produce_term_visualisation(self):
        f = open(TEMP_FILE)
        j = f.read().strip()
        print("******")
        loaded_term_dict = json.loads(j)
        all_terms = []
        for key, item in loaded_term_dict.items():
            all_terms.extend([el["term"] for el in item])
        
        #print(loaded_term_dict)
        all_terms = sorted(list(set(all_terms)))
        #all_terms = set(all_terms)
        print(all_terms)
        print("********")

if __name__ == '__main__':
    tv = TermVisualiser()
    tv.produce_term_visualisation()
