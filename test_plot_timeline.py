import plot_timeline

def test_allergy():
    model_file = "/Users/marsk757/topics2themes/topics2themes/data_folder/DMW_allergy/topics2themes_exports_folder_created_by_system/643ff13f28541561dc43bb88_model.json"
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
    model_file = "/Users/marsk757/topics2themes/topics2themes/data_folder/climate-news/topics2themes_exports_folder_created_by_system/643b17a648460386c298ed68_model.json"
    metadata_file_name = "/Users/marsk757/topics2themes/topics2themes/data_folder/climate-news/topics2themes_exports_folder_created_by_system/all_files.csv"
    outputdir = "plots"
    file_name = "climate-news.pdf"
    add_for_coliding_dates = False
    label_length = 30

    plot_timeline.make_plot(model_file, outputdir, metadata_file_name, file_name, add_for_coliding_dates, label_length)

def test_fc():

    model_file = "/Users/marsk757/topics2themes/topics2themes/data_folder/framtidens-kultur_automatiskt/topics2themes_exports_folder_created_by_system/6435235bfa0b2425fb69e3bf_model.json"
    metadata_file_name = "/Users/marsk757/topics2themes/topics2themes/data_folder/framtidens-kultur_automatiskt/topics2themes_exports_folder_created_by_system/all_files.csv"
    outputdir = "plots"
    add_for_coliding_dates = True
    label_length = 60
    label_translations = {"1995.5" : "1995-06"}
    
    #1
    file_name = "fc.pdf"
    plot_timeline.make_plot(model_file, outputdir, metadata_file_name, file_name, add_for_coliding_dates, label_length, label_translations, vertical_line_to_represent_nr_of_documents=False)
    
    #2
    file_name = "fc_normalized.pdf"
    normalise_for_nr_of_texts=True
    plot_timeline.make_plot(model_file, outputdir, metadata_file_name, file_name, add_for_coliding_dates, label_length, label_translations, normalise_for_nr_of_texts, vertical_line_to_represent_nr_of_documents=False)

#test_climate()
#test_fc()
#test_marknad()
test_allergy()
