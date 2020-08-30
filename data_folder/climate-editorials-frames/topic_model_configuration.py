import os
from sklearn.feature_extraction import text
from nltk.corpus import stopwords

# An import that should function both locally and when running an a remote server
try:
    from environment_configuration import *
except:
    from topics2themes.environment_configuration import *

if RUN_LOCALLY:
    from topic_model_constants import *
    from word2vec_term_similarity import *

else:
    from topics2themes.topic_model_constants import *
    from topics2themes.word2vec_term_similarity import *
    

"""
Nr of topics to retrieve
"""
NUMBER_OF_TOPICS = 20

"""
The topic modelling algorithm is rerun with a decrease number of requested topics
until the number of found stable topics are similar to the ones requested
The amont of similarity is set here.
"""

PROPORTION_OF_LESS_TOPIC_TO_ALLOW = 0.9

"""
Nr of words to display for each topic
"""
NR_OF_TOP_WORDS = 20

"""
Nr of most typical document to retrieve for each topic
"""
#NR_OF_TOP_DOCUMENTS = 490
NR_OF_TOP_DOCUMENTS = 30

"""
Number of runs to check the stability of the retrieved topics.
Only topics that occur in all NUMBER_OF_RUNS runs will be
considered valid
"""
NUMBER_OF_RUNS = 10


"""
Mininimum overlap of retrieved terms to considered the retrieved topic as
the same topic of a another one
"""
OVERLAP_CUT_OFF = 0.6

"""
Whether to use pre-processing (collocation detection and synonym clustering)
"""
PRE_PROCESS = True
VECTOR_LENGTH = 300
SPACE_FOR_PATH = "/Users/marsk757/wordspaces/GoogleNews-vectors-negative300.bin"
MAX_DIST_FOR_CLUSTERING = 0.8
WORDS_NOT_TO_INCLUDE_IN_CLUSTERING_FILE = "not_cluster.txt"
MANUAL_CLUSTER_FILE = "manual_clusters.txt"


"""
Mininimum occurrence in the corpus for a term to be included in the topic modelling
"""
MIN_DOCUMENT_FREQUENCY = 2

"""
Maximum occurrence in the corpus for a term to be included in the topic modelling
"""
MAX_DOCUMENT_FREQUENCY = 0.95

BINARY_TF = False


"""
Mininimum occurrence in the corpus for a term to be included in the clustering.
"""
MIN_DOCUMENT_FREQUENCY_TO_INCLUDE_IN_CLUSTERING = 2

"""
The stop word file of user-defined stopiwords to use (Scikit learn stop words are also used)
"""
STOP_WORD_FILE = "english_only_vaccine_added_nguyen_argumentaion_words_authors.txt"


"""
The directories in which data is to be found. The data is to be in files with the ".txt" extension
in these directories. For each directory, there should also be a stance-label and a color associated with
the data
"""

DATA_LABEL_LIST = [{DATA_LABEL : "ECON", DIRECTORY_NAME : "A_dominant_frame", LABEL_COLOR : "#58FAF4" },\
                    {DATA_LABEL : "DEV", DIRECTORY_NAME : "B_dominant_frame", LABEL_COLOR : "#FF8000" },\
                    {DATA_LABEL : "SEC", DIRECTORY_NAME : "C_dominant_frame", LABEL_COLOR : "#D8D8D8" },\
                    {DATA_LABEL : "ETH", DIRECTORY_NAME : "D_dominant_frame", LABEL_COLOR : "#ccad00" },\
                    {DATA_LABEL : "TECH", DIRECTORY_NAME : "E_dominant_frame", LABEL_COLOR : RED },\
                    {DATA_LABEL : "GOV", DIRECTORY_NAME : "F_dominant_frame", LABEL_COLOR : GREEN },\
                      {DATA_LABEL : "SCI", DIRECTORY_NAME : "G_dominant_frame", LABEL_COLOR : "#2E2EFE" },\
                        {DATA_LABEL : "COM", DIRECTORY_NAME : "H_dominant_frame", LABEL_COLOR : "#8A4B08" }]


TOPIC_MODEL_ALGORITHM = NMF_NAME
#TOPIC_MODEL_ALGORITHM = LDA_NAME

"""
    If an extracted term includes less than this among the documents that are extracted, this term is removed from the set of extracted terms
    Synonym clustering is performed before the counting is done, so a rare term with synonyms is retained
    """
MIN_FREQUENCY_IN_COLLECTION_TO_INCLUDE_AS_TERM = 1

MAX_NR_OF_FEATURES = 10000

STOP_WORD_SET = text.ENGLISH_STOP_WORDS

SHOW_ARGUMENTATION = False
SHOW_SENTIMENT = False

def get_journal(doc_id):
    id = str(doc_id).split("/")[-1]
    if id in NatureOCR:
        return ["Nature"]
    elif id in ScienceOCR:
        return ["Science"]
    else:
        return ["None"]
        

ADDITIONAL_LABELS_METHOD = get_journal


def corpus_specific_text_cleaning(text):
    text = text.replace(" ,", ",")\
    .replace("( ", " (")\
    .replace(" )", ") ")
    return text

CLEANING_METHOD = corpus_specific_text_cleaning

MANUAL_COLLOCATIONS = "manual_collocations.txt"

NatureOCR  = ['227646a0.ocr.txt', '338100a0.ocr.txt', '416567b.ocr.txt', '340489a0.ocr.txt', '439891a.ocr.txt', '514140a.ocr.txt', '530006a.ocr.txt', '462251a.ocr.txt', '357265a0.ocr.txt', '437295b.ocr.txt', '467751a.ocr.txt', '375091a0.ocr.txt', '457235a.ocr.txt', '37682.ocr.txt', '440128a.ocr.txt', '441549a.ocr.txt', '378322a0.ocr.txt', '522128a.ocr.txt', '479267b.ocr.txt', '4681001a.ocr.txt', '438396a.ocr.txt', '431613a.ocr.txt', '350541a0.ocr.txt', '347601a0.ocr.txt', '456546a.ocr.txt', '241489a0.ocr.txt', '430489b.ocr.txt', '439370a.ocr.txt', '534152a.ocr.txt', '450135a.ocr.txt', '471265b.ocr.txt', '363568a0.ocr.txt', '451001a.ocr.txt', '497288a.ocr.txt', '271695a0.ocr.txt', '339002a0.ocr.txt', '446949b.ocr.txt', '445125b.ocr.txt', '357097a0.ocr.txt', '453257a.ocr.txt', '451605a.ocr.txt', '363657a0.ocr.txt', '490445a.ocr.txt', '447507a.ocr.txt', '347409a0.ocr.txt', '446348a.ocr.txt', '441127b.ocr.txt', '523381a.ocr.txt', '332097a0.ocr.txt', '477509a.ocr.txt', '432131a.ocr.txt', '424861a.ocr.txt', '22820.ocr.txt', '482131b.ocr.txt', '446110a.ocr.txt', '323189a0.ocr.txt', '4581077a.ocr.txt', '4471032a.ocr.txt', '518456a.ocr.txt', '512347b.ocr.txt', '374749a0.ocr.txt', '446470a.ocr.txt', '486439b.ocr.txt', '372115a0.ocr.txt', '4501128a.ocr.txt', '305750a0.ocr.txt', '35079241.ocr.txt', '465525a.ocr.txt', '4571057a.ocr.txt', '35084333.ocr.txt', '493134a.ocr.txt', '510444b.ocr.txt', '435247a.ocr.txt', '463849a.ocr.txt', '4351003a.ocr.txt', '499005a.ocr.txt', '459483b.ocr.txt', '431001a.ocr.txt', '422001b.ocr.txt', '334457a0.ocr.txt', '357523a0.ocr.txt', '454368a.ocr.txt', '526293a.ocr.txt', '458679b.ocr.txt', '452387b.ocr.txt', '447115a.ocr.txt', '517244a.ocr.txt', '468133b.ocr.txt', '455263a.ocr.txt', '466007a.ocr.txt', '383745b0.ocr.txt', '467133a.ocr.txt', '345559a0.ocr.txt', '458126a.ocr.txt', '319708a0.ocr.txt', '486005a.ocr.txt', '430385a.ocr.txt', '4611027a.ocr.txt', '508150a.ocr.txt', '474128a.ocr.txt', '480005b.ocr.txt', '474541a.ocr.txt', '368571a0.ocr.txt', '444243a.ocr.txt', '439509b.ocr.txt', '468345a.ocr.txt', '466295b.ocr.txt', '530130b.ocr.txt', '468476a.ocr.txt', '419543a.ocr.txt', '502593a.ocr.txt', '455565a.ocr.txt', '347001a0.ocr.txt', '355752a0.ocr.txt', '418803a.ocr.txt', '349001b0.ocr.txt', '504331b.ocr.txt', '478428a.ocr.txt', '436890a.ocr.txt', '460436a.ocr.txt', '348181a0.ocr.txt', '516008a.ocr.txt', '445339b.ocr.txt', '445459a.ocr.txt', '489335b.ocr.txt', '457357b.ocr.txt', '441785a.ocr.txt', '491637b.ocr.txt', '323095a0.ocr.txt', '381451a0.ocr.txt', '528307a.ocr.txt', '526006a.ocr.txt', '527133a.ocr.txt', '339323a0.ocr.txt', '431001b.ocr.txt', '35050205.ocr.txt', '416771b.ocr.txt', '374199a0.ocr.txt', '508007a.ocr.txt', '435713b.ocr.txt', '452127b.ocr.txt', '503311a.ocr.txt', '441127a.ocr.txt', '4591033a.ocr.txt', '229514a0.ocr.txt', '452253a.ocr.txt', '530253a.ocr.txt', '482440b.ocr.txt', '495281a.ocr.txt', '529255b.ocr.txt', '497157b.ocr.txt', '387637a0.ocr.txt', '2241241a0.ocr.txt', '225885a0.ocr.txt', '490005b.ocr.txt', '457511b.ocr.txt', '321713a0.ocr.txt', '475140a.ocr.txt', '39118.ocr.txt', '335479a0.ocr.txt', '505585a.ocr.txt', '259517a0.ocr.txt', '374483a0.ocr.txt', '475423b.ocr.txt', '514005b.ocr.txt', '477131b.ocr.txt', '497287b.ocr.txt', '347410b0.ocr.txt', '527409a.ocr.txt', '453001b.ocr.txt', '230419a0.ocr.txt', '4351137a.ocr.txt', '489473a.ocr.txt', '36651.ocr.txt', '484005a.ocr.txt', '4611173b.ocr.txt', '440969a.ocr.txt', '441907b.ocr.txt', '432257a.ocr.txt', '327001a0.ocr.txt', '455137a.ocr.txt', '451499a.ocr.txt', '500501a.ocr.txt', '470435b.ocr.txt', '416461a.ocr.txt', '460012a.ocr.txt', '521006a.ocr.txt', '451865b.ocr.txt', '511383a.ocr.txt', '343101b0.ocr.txt', '356001a0.ocr.txt', '480292a.ocr.txt', '433785a.ocr.txt', '487005b.ocr.txt', '243485a0.ocr.txt', '4681002a.ocr.txt', '501281a.ocr.txt', '450319a.ocr.txt', '467883b.ocr.txt', '458008a.ocr.txt', '458945b.ocr.txt', '344179a0.ocr.txt', '516007a.ocr.txt', '462957a.ocr.txt', '454551b.ocr.txt', '505261b.ocr.txt', '465009b.ocr.txt', '35001194.ocr.txt', '4531144a.ocr.txt', '491301a.ocr.txt', '371269a0.ocr.txt', '453427a.ocr.txt', '451746a.ocr.txt', '427661a.ocr.txt', '458125b.ocr.txt', '522255b.ocr.txt', '424709b.ocr.txt', '456838a.ocr.txt', '365002a0.ocr.txt', '446701a.ocr.txt', '341266b0.ocr.txt', '342600a0.ocr.txt', '295178a0.ocr.txt', '459299b.ocr.txt', '528164a.ocr.txt', '480006a.ocr.txt', '438257b.ocr.txt', '459140a.ocr.txt', '432933a.ocr.txt', '452503b.ocr.txt', '460307b.ocr.txt', '467752a.ocr.txt', '465135b.ocr.txt', '444002a.ocr.txt', '335191a0.ocr.txt', '481005a.ocr.txt', '429001a.ocr.txt', '461146a.ocr.txt', '345371a0.ocr.txt', '530382a.ocr.txt', '357178a0.ocr.txt', '488429a.ocr.txt', '235184a0.ocr.txt', '520005b.ocr.txt', '332291a0.ocr.txt', '40208.ocr.txt', '455431a.ocr.txt', '344797a0.ocr.txt', '356461a0.ocr.txt', '35075206.ocr.txt', '4661023b.ocr.txt', '492153a.ocr.txt', '43718.ocr.txt', '445567a.ocr.txt', '442601b.ocr.txt', '35069194.ocr.txt', '436001a.ocr.txt', '446109a.ocr.txt', '356643a0.ocr.txt', '454805a.ocr.txt', '421195a.ocr.txt', '345189a0.ocr.txt', '449947a.ocr.txt', '472390a.ocr.txt', '515465a.ocr.txt', '494148a.ocr.txt', '338188a0.ocr.txt', '509007a.ocr.txt', '505585b.ocr.txt', '522391a.ocr.txt', '463269a.ocr.txt', '457764a.ocr.txt', '26549.ocr.txt', '497410a.ocr.txt', '452002a.ocr.txt', '538289a.ocr.txt', '436151b.ocr.txt', '497005a.ocr.txt', '444519a.ocr.txt', '479005b.ocr.txt', '367395a0.ocr.txt', '461447b.ocr.txt', '537585b.ocr.txt', '443724a.ocr.txt', '449755a.ocr.txt', '516288a.ocr.txt', '536125a.ocr.txt', '474127b.ocr.txt', '40210.ocr.txt', '449637a.ocr.txt', '444971a.ocr.txt', '462011a.ocr.txt', '462545a.ocr.txt', '520407b.ocr.txt', '485415a.ocr.txt', '531007b.ocr.txt', '460551b.ocr.txt', '279001a0.ocr.txt', '473005a.ocr.txt', '444654a.ocr.txt', '480413b.ocr.txt', '496137b.ocr.txt', '468599a.ocr.txt', '464141a.ocr.txt', '4541030b.ocr.txt', '460781a.ocr.txt', '237302a0.ocr.txt', '466667b.ocr.txt', '429327b.ocr.txt', '493577b.ocr.txt', '472260a.ocr.txt', '333381a0.ocr.txt', '449115b.ocr.txt', '4501127a.ocr.txt', '349441a0.ocr.txt', '381539a0.ocr.txt', '462957b.ocr.txt', '517527b.ocr.txt', '467883a.ocr.txt', '441384a.ocr.txt', '477249a.ocr.txt', '439244b.ocr.txt', '443001a.ocr.txt', '471136a.ocr.txt', '450761a.ocr.txt', '4571058a.ocr.txt', '4551008a.ocr.txt', '280179a0.ocr.txt', '519261a.ocr.txt', '461848a.ocr.txt', '473123b.ocr.txt', '511384a.ocr.txt', '35066684.ocr.txt']
ScienceOCR  = ['289.5483.1293.ocr.txt', '270.5241.1417.ocr.txt', '1137177.ocr.txt', '304.5671.649.ocr.txt', 'aaf1428.ocr.txt', '1200613.ocr.txt', '1159999.ocr.txt', 'aaf2138.ocr.txt', '256.5055.289.ocr.txt', '299.5614.1813.ocr.txt', '272.5259.177.ocr.txt', '1198075.ocr.txt', '1124886.ocr.txt', '298.5600.1847.ocr.txt', '299.5605.309.ocr.txt', 'aaa8493.ocr.txt', '1178591.ocr.txt', '290.5494.1091.ocr.txt', '216.4546.569.ocr.txt', '1140975.ocr.txt', '1259742.ocr.txt', '1147817.ocr.txt', '1185072.ocr.txt', '1187612.ocr.txt', '1148943.ocr.txt', '303.5663.1437.ocr.txt', '243.4893.873.ocr.txt', '243.4892.709.ocr.txt', 'aac8698.ocr.txt', '253.5016.117.ocr.txt', '155.3759.153.ocr.txt', '242.4885.1489.ocr.txt', '204.4398.1161.ocr.txt', '231.4743.1233.ocr.txt', '1169820.ocr.txt', '248.4962.1469.ocr.txt', '1133322.ocr.txt', '302.5652.1861.ocr.txt', '250.4986.1317.ocr.txt', '1123759.ocr.txt', '260.5105.143.ocr.txt', '170.3954.125.ocr.txt', '1238241.ocr.txt', '1115898.ocr.txt', '298.5599.1679.ocr.txt', '246.4929.429.ocr.txt', '1175097.ocr.txt', 'aaa7477.ocr.txt', '1148839.ocr.txt', '294.5548.1789.ocr.txt', '222.4626.879.ocr.txt', '292.5524.1965.ocr.txt', '152.3719.159.ocr.txt', '256.5060.1109.ocr.txt', '244.4902.273.ocr.txt', '248.4953.281.ocr.txt', '290.5493.931.ocr.txt', '1177070.ocr.txt', 'aab1106.ocr.txt', '287.5455.971.ocr.txt', '152.3723.703.ocr.txt', '1153230.ocr.txt', '1192996.ocr.txt', '244.4907.901.ocr.txt', '249.4973.1085.ocr.txt', '1146513.ocr.txt', '1190790.ocr.txt', '228.4696.133.ocr.txt', '243.4890.461.ocr.txt', '200.4337.9.ocr.txt', '1207012.ocr.txt', '292.5520.1261.ocr.txt', '1257423.ocr.txt', '1135210.ocr.txt', '1251932.ocr.txt', '1145963.ocr.txt', '1142978.ocr.txt', '191.4233.1221.ocr.txt', '1155011.ocr.txt', '278.5344.1691.ocr.txt', '1199255.ocr.txt', '245.4920.805.ocr.txt', '1194561.ocr.txt', '186.4160.205.ocr.txt', '195.4281.825.ocr.txt', '1129466.ocr.txt', '285.5428.662.ocr.txt', '1160329.ocr.txt', '257.5076.1459.ocr.txt', '241.4872.1405.ocr.txt', '234.4777.657.ocr.txt', 'aab1102.ocr.txt', '304.5672.795.ocr.txt', '293.5533.1221.ocr.txt', '1176998.ocr.txt', '199.4324.9.ocr.txt', '194.4260.15.ocr.txt', '304.5677.1565.ocr.txt', 'aal2558.ocr.txt', '175.4027.1197.ocr.txt', '299.5609.977.ocr.txt', 'aab3119.ocr.txt', '1179807.ocr.txt', '1124889.ocr.txt', '305.5692.1873.ocr.txt', '1132850.ocr.txt', '1154158.ocr.txt', '1155724.ocr.txt', '257.5066.9.ocr.txt', '1123757.ocr.txt', '1181637.ocr.txt', '1105134.ocr.txt', '297.5582.737.ocr.txt', 'aad7927.ocr.txt', '257.5067.143.ocr.txt', '278.5339.783.ocr.txt', '204.4395.797.ocr.txt', '294.5547.1617.ocr.txt', '1227898.ocr.txt', '1130034.ocr.txt', '1117863.ocr.txt', '187.4178.705.ocr.txt', '243.4889.281.ocr.txt', '1236756.ocr.txt', '296.5570.981.ocr.txt', '1183876.ocr.txt', '1140872.ocr.txt', '1183953.ocr.txt', '1135358.ocr.txt', '1195624.ocr.txt', '1163960.ocr.txt', 'aac5755.ocr.txt', '1119787.ocr.txt', '297.5581.477.ocr.txt', 'aad8954.ocr.txt', '1259026.ocr.txt', '197.4307.941.ocr.txt', '1242710.ocr.txt', '287.5462.2419.ocr.txt', '1248348.ocr.txt', '259.5097.875.ocr.txt', '1139394.ocr.txt', '1125749.ocr.txt', '241.4864.397.ocr.txt', '1243256.ocr.txt', '1143220.ocr.txt', '305.5686.917.ocr.txt', '277.5325.457.ocr.txt', '1139909.ocr.txt', '1226098.ocr.txt', '258.5089.1715.ocr.txt', '1258594.ocr.txt', '303.5657.433.ocr.txt', '1139792.ocr.txt', '268.5213.955.ocr.txt', '247.4950.1529.ocr.txt', '1127485.ocr.txt', '253.5024.1073.ocr.txt', '297.5584.1093.ocr.txt']
