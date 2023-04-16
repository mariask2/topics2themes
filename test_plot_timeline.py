import plot_timeline

def test_climate():
    model_file = "/Users/marsk757/topics2themes/topics2themes/data_folder/climate-news/topics2themes_exports_folder_created_by_system/643b17a648460386c298ed68_model.json"
    metadata_file_name = "/Users/marsk757/topics2themes/topics2themes/data_folder/climate-news/topics2themes_exports_folder_created_by_system/all_files.csv"
    outputdir = "plots"
    file_name = "climate-news.pdf"

    plot_timeline.make_plot(model_file, outputdir, metadata_file_name, file_name)

test_climate()
