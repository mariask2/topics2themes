import plot_timeline

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
    model_file_1 = "/Users/marsk757/topics2themes/topics2themes/data_folder/diabetes_parsed/topics2themes_exports_folder_created_by_system/651f552510a4ba2e273dd361_model.json"
    metadata_file_name = "/Users/marsk757/topics2themes/topics2themes/data_folder/diabetes_parsed/topics2themes_exports_folder_created_by_system/all_files.csv"
    outputdir = "plots"
    file_name_1 = "diabetes-no-clusters.pdf"
    add_for_coliding_dates = False
    label_length = 30
    use_date_format = True
    #dont_show_list = [17]

    plot_timeline.make_plot(model_file_1, outputdir, metadata_file_name, file_name_1, add_for_coliding_dates, label_length, use_date_format=use_date_format, log=False, hours_between_label_dates=720, width_vertical_line=0.000000001)
    
    file_name_2 = "diabetes-with-clusters.pdf"
    model_file_2 = "/Users/marsk757/topics2themes/topics2themes/data_folder/diabetes_parsed/topics2themes_exports_folder_created_by_system/651f41f53e4d4d368911a9b7_model.json"
    plot_timeline.make_plot(model_file_2, outputdir, metadata_file_name, file_name_2, add_for_coliding_dates, label_length, use_date_format=use_date_format, log=False, hours_between_label_dates=720, width_vertical_line=0.000000001)
#test_climate()
#test_fc()
#test_marknad()
#test_allergy()
test_diabetes()
