import plot_timeline

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
    file_name = "fc.pdf"
    add_for_coliding_dates = True
    label_length = 60
    label_translations = {"1995.5" : "1995-06"}
    plot_timeline.make_plot(model_file, outputdir, metadata_file_name, file_name, add_for_coliding_dates, label_length, label_translations)

#test_climate()
test_fc()
