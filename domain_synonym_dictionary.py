# Are not allowed to be in synonym clusters
NO_MATCH = set(["polio", "measles", "measle", "chickenpox", "flu", "meningitis", "mumps", "pertussis", "capable",\
                "incapable", "likely", "unlikely", "black", "white",\
    "increase", "increased", "increases", "increasing", "boy", "girl",\
    "man", "mothers", "parents", "teenager", "toddler", "woman", "andrew",\
    "robert", "female", "negative", "positive", "forget", "remember",\
    "australia", "nz", "uk", "easier", "harder",\
    "awful", "bad", "big", "bigger", "considerable", "decent", "excellent", "fantastic",\
    "good", "great", "hideous", "horrible", "horrid", "huge", "lovely", "massive", "nice",\
    "significant", "smaller", "substantial", "terrible", "tremendous", "wonderful", "cheaper", "expensive"\
    "luckily", "sadly", "thankfully", "unfortunately", "high", "low", "agree", "disagree",\
    "adulthood", "puberty", "don", "large", "boys", "girls", "child", "children",
    "ah", "awfully", "btw", "certainly", "comprehend", "definitely", "dont", "eh",\
    "enormously", "er", "explain", "extremely", "fairly", "guess", "hey", "hugely", "huh",\
    "im", "incredibly", "knew", "know", "lol", "massively", "maybe", "obviously", "oh", "pretty" ,\
    "probably", "quite", "really", "relatively", "suppose", "surely", "tell", "telling", \
    "think", "thought", "tremendously", "uh", "understand", "ur", "wont", "yeah","adults", "kid", "kids",\
    "higher", "lower", "men", "women", "doctor", "doctors", "patient", "patients", "physicians",\
    "chicken_pox", "whooping_cough", "older", "younger", "flu_vaccine", "flu_vaccines", "smallpox_vaccine",\
    "days", "decade", "decades", "hour", "hours", "minute", "minutes", "month", "months", "week", "weeks", "year", "years",\
    "brother", "brothers", "cousin", "dad", "daughter", "daughters", "father", "grandmother", "mother", "siblings", "sister", "son",\
    ])


MANUAL_MADE_DICT = {"increase" : "increase__increased__increases__increasing",\
                    "increases" : "increase__increased__increases__increasing",\
                    "increasing" : "increase__increased__increases__increasing",\
                    "increased" : "increase__increased__increases__increasing",\
                    #                    "child" : "child__children__kid__kids",\
                    #"children" : "child__children__kid__kids",\
                    #"kid" : "child__children__kid__kids",\
                    #"kids" : "child__children__kid__kids",\
                    "awful": "awful__bad__hideous__horrible__horrid__terrible",\
                    "bad": "awful__bad__hideous__horrible__horrid__terrible",\
                    "hideous": "awful__bad__hideous__horrible__horrid__terrible",\
                    "horrible" : "awful__bad__hideous__horrible__horrid__terrible",\
                    "horrid" :"awful__bad__hideous__horrible__horrid__terrible",\
                    "terrible": "awful__bad__hideous__horrible__horrid__terrible",\
                    "big": "bigger__considerable__big__significant__substantial__huge",\
                    "bigger": "bigger__considerable__big__significant__substantial__huge",\
                    "considerable": "bigger__considerable__big__significant__substantial__huge",\
                    "significant": "bigger__considerable__big__significant__substantial__huge",\
                    "substantial": "bigger__considerable__big__significant__substantial__huge",\
                    "huge": "bigger__considerable__big__significant__substantial__huge",\
                    #"decent":  "decent__excellent__fantastic__good__great__lovely__nice__tremendous__wonderful",\
                    #"excellent" : "decent__excellent__fantastic__good__great__lovely__nice__tremendous__wonderful",\
                    #"fantastic" : "decent__excellent__fantastic__good__great__lovely__nice__tremendous__wonderful",\
                    #"good" : "decent__excellent__fantastic__good__great__lovely__nice__tremendous__wonderful",\
                    #"great":  "decent__excellent__fantastic__good__great__lovely__nice__tremendous__wonderful",\
                    #"lovely":  "decent__excellent__fantastic__good__great__lovely__nice__tremendous__wonderful",\
                    #"nice"  :"decent__excellent__fantastic__good__great__lovely__nice__tremendous__wonderful",\
                    #"tremendous" : "decent__excellent__fantastic__good__great__lovely__nice__tremendous__wonderful",\
                    #"wonderful"  :"decent__excellent__fantastic__good__great__lovely__nice__tremendous__wonderful",\
                    #"luckily": "luckily__thankfully",\
                    #"thankfully": "luckily__thankfully",\
                    #"sadly" : "sadly__unfortunately",\
                    "unfortunately" : "sadly__unfortunately",\
                    "doctor":"doctor__doctors__physicians",\
                    "doctors":"doctor__doctors__physicians",\
                    "physicians":"doctor__doctors__physicians",\
                    "patient":"patient__patients",\
                    "patients":"patient__patients",\
                    }
