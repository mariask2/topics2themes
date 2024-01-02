import plot_timeline
import os

def test_allergy():
    model_file = "/Users/marsk757/topics2themes/topics2themes/data_folder/DMW_allergy/topics2themes_exports_folder_created_by_system/6457fd84ed221bd819d9710c_model.json"
    metadata_file_name = "/Users/marsk757/topics2themes/topics2themes/data_folder/DMW_allergy/topics2themes_exports_folder_created_by_system/all_files.csv"
    outputdir = "plots"
    file_name = "allergy.pdf"
    add_for_coliding_dates = False
    label_length = 20
    use_date_format = True

    plot_timeline.make_plot(model_file, outputdir, metadata_file_name, file_name, add_for_coliding_dates, label_length, use_date_format=use_date_format, log=True)


def test_marknad():
    model_file = "/Users/marsk757/topics2themes/topics2themes/data_folder/marknad-titel/topics2themes_exports_folder_created_by_system/643e4468a2b68a9a97bc0cd0_model.json"
    metadata_file_name = "/Users/marsk757/topics2themes/topics2themes/data_folder/marknad-titel/topics2themes_exports_folder_created_by_system/all_files.csv"
    outputdir = "plots"
    file_name = "marknad.pdf"
    add_for_coliding_dates = True
    label_length = 30
    use_date_format = False
    dont_show_list = [17]

    plot_timeline.make_plot(model_file, outputdir, metadata_file_name, file_name, add_for_coliding_dates, label_length, use_date_format=use_date_format, log=True)
    
    model_file_clustered = "/Users/marsk757/topics2themes/topics2themes/data_folder/marknad-titel/topics2themes_exports_folder_created_by_system/643eacd7e0ab745868812cb5_model.json"
    file_name_clustered = "marknad-clustered.pdf"
    plot_timeline.make_plot(model_file_clustered, outputdir, metadata_file_name, file_name_clustered, add_for_coliding_dates, label_length, use_date_format=use_date_format, log=True)
    
def test_climate():
    model_file = "/Users/marsk757/topics2themes/topics2themes/data_folder/climate-news/topics2themes_exports_folder_created_by_system/644aca8c54cac60d53accbd7_model.json"
    #643b17a648460386c298ed68_model.json"
    metadata_file_name = "/Users/marsk757/topics2themes/topics2themes/data_folder/climate-news/topics2themes_exports_folder_created_by_system/all_files.csv"
    outputdir = "plots"
    file_name = "climate-news.pdf"
    add_for_coliding_dates = False
    label_length = 20
    log = True

    plot_timeline.make_plot(model_file, outputdir, metadata_file_name, file_name, add_for_coliding_dates, label_length, log=log)

def test_fc():
    model_file = "/Users/marsk757/topics2themes/topics2themes/data_folder/framtidens-kultur_automatiskt/topics2themes_exports_folder_created_by_system/"
    metadata_file_name = "/Users/marsk757/topics2themes/topics2themes/data_folder/framtidens-kultur_automatiskt/topics2themes_exports_folder_created_by_system/all_files.csv"
    outputdir = "plots"
    add_for_coliding_dates = True
    label_length = 20
    #label_translations = {"1995.5" : "1995-06"}
    log = True
    use_date_format = False
    
    #1
    file_name = "fc.pdf"
    plot_timeline.make_plot(model_file, outputdir, metadata_file_name, file_name, add_for_coliding_dates, label_length, vertical_line_to_represent_nr_of_documents=False, log = log, use_date_format=use_date_format)
    
    #2
    file_name = "fc_normalized.pdf"
    normalise_for_nr_of_texts=True
    plot_timeline.make_plot(model_file, outputdir, metadata_file_name, file_name, add_for_coliding_dates, label_length, normalise_for_nr_of_texts, vertical_line_to_represent_nr_of_documents=False, log = log, use_date_format=use_date_format)

def test_diabetes():

    outputdir = "plots"
    add_for_coliding_dates = False
    label_length = 80
    use_date_format = True
    metadata_file_name = "/Users/marsk757/topics2themes/topics2themes/data_folder/diabetes_parsed/topics2themes_exports_folder_created_by_system/all_files.csv"
        
        
    """ # Just commented out, since no need to run again
    # 23-10-06 00:30:28
    model_file_1 = "/Users/marsk757/topics2themes/topics2themes/data_folder/diabetes_parsed/topics2themes_exports_folder_created_by_system/651f552510a4ba2e273dd361_model.json"
    file_name_1 = "diabetes-no-clusters.pdf"
    plot_timeline.make_plot(model_file_1, outputdir, metadata_file_name, file_name_1, add_for_coliding_dates, label_length, use_date_format=use_date_format, log=False, hours_between_label_dates=720, width_vertical_line=0.000000001, extra_x_length=0.001)
    """
    
    
    # 23-10-08 04:16:23
    file_name_2 = "diabetes-with-clusters.pdf"
    model_file_2 = "/Users/marsk757/topics2themes/topics2themes/data_folder/diabetes_parsed/topics2themes_exports_folder_created_by_system/65222d18b8c0c1b7fbe2978b_model.json"
    plot_timeline.make_plot(model_file_2, outputdir, metadata_file_name, file_name_2, add_for_coliding_dates, label_length, use_date_format=use_date_format, log=False, hours_between_label_dates=720, width_vertical_line=0.000000001, extra_x_length=0.001)
    
def diabetes_link_mapping(name, dict=None):
    acc_str = "http://127.0.0.1:9080/files/diabetes/pdf/"
    name_parts = name.split("_")
    year = name_parts[1]
    acc_str = acc_str + year + "/" + name.replace(".txt", ".pdf")
    return acc_str
    
def test_diabetes_lemmatised():

    outputdir = "plots"
    add_for_coliding_dates = False
    label_length = 40
    use_date_format = True
    metadata_file_name = "/Users/marsk757/topics2themes/topics2themes/data_folder/diabetes_lemmas/topics2themes_exports_folder_created_by_system/all_files.csv"
        
    order_mapping = [[1, 8, 15, 21, 29, 31, 41], [2, 3, 6, 9, 10, 12, 13, 22, 23, 25, 28, 38, 46, 48], [4, 5, 7, 11, 14, 17, 18, 24, 26, 30, 32, 33, 34, 36, 39, 47, 49, 50, 51], [16, 19, 35, 40, 42,], [27, 37, 43, 44], 20, 45]
    #order_mapping = [1, [2, 3, 4], 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, [33, 34, 35], 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, [47, 48, 49], 50, 51]
    # 23-10-08 04:16:23
    file_name_2 = "diabetes-with-clusters-lemmas"
    model_file_2 = "/Users/marsk757/topics2themes/topics2themes/data_folder/diabetes_lemmas/topics2themes_exports_folder_created_by_system/654817afb0e85021c547b821_model.json"
    plot_timeline.make_plot(model_file_2, outputdir, metadata_file_name, file_name_2, add_for_coliding_dates, label_length, use_date_format=use_date_format, log=False, hours_between_label_dates=480, width_vertical_line=0.01, extra_x_length=0.001, order_mapping=order_mapping, link_mapping_func=diabetes_link_mapping, bar_transparency=0.1)

def get_url_marknad(doc_path, dict=None):
    base_name = os.path.basename(doc_path)
    sp = base_name.split("_")
    url =  "https://data.riksdagen.se/dokument/" + sp[2] + ".html"
    return url
    
def test_marknad_agenda2030():

    outputdir = "plots"
    add_for_coliding_dates = False
    label_length = 60
    use_date_format = True
    metadata_file_name = "/Users/marsk757/topics2themes/topics2themes/data_folder/marknad-titel_agenda2030/topics2themes_exports_folder_created_by_system/all_files.csv"
        
    order_mapping = [[1, 10, 16, 19, 25, 26], 2, 3, [4, 8], [5, 7, 28], [6, 9, 14], 11, 12, 13,  15, [17, 24], [18, 21],  20, 22, 23, 27]
    file_name_2 = "marknad-titel_agenda2030"
    model_file_2 = "/Users/marsk757/topics2themes/topics2themes/data_folder/marknad-titel_agenda2030/topics2themes_exports_folder_created_by_system/65931a29dae79880c480b92b_model.json"
    plot_timeline.make_plot(model_file_2, outputdir, metadata_file_name, file_name_2, add_for_coliding_dates, label_length, use_date_format=use_date_format, log=False, hours_between_label_dates=0.001, width_vertical_line=0.01, order_mapping=order_mapping, link_mapping_func=get_url_marknad, bar_transparency=0.05)
#test_climate()
#test_fc()
#test_marknad()
#test_allergy()
#test_diabetes()
test_diabetes_lemmatised()
#test_marknad_agenda2030()
