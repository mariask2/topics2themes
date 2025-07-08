import plot_timeline_from_files
import os
import json

    
def do_plot():
    outputdir = "diabetiker_transformers"
    add_for_coliding_dates = False
    label_length = 100
    use_date_format = True
    
    
    #"goldenrod", "purple",
    # Clinics, glocous monitoring, injections, other medical, food, organisational, other, noise
    order_colors = ["blue", "green", "red", "cyan", "violet", "olive", "limegreen", "brown", "navy",   "orange", "teal",  "mediumslateblue", "darkturquoise", "tan", "royalblue", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse", "chocolate", "chartreuse"]
    print("Start plotting")
    
    
    
    file_name_diabetiker = "faire_face_transformers_1945_1946"
    
    label_file_diabetiker = "/Users/marsk757/actdisease/actdisease-code/sentence_transformers/faire_face_1945_1946/faire_face_1945_1946_cluster_labels.txt"
    texts_topics_file_diabetiker = "/Users/marsk757/actdisease/actdisease-code/sentence_transformers/faire_face_1945_1946/faire_face_1945_1946_clustered.txt"
    order_mapping_file_diabetiker = "/Users/marsk757/actdisease/actdisease-code/sentence_transformers/faire_face_1945_1946/faire_face_1945_1946_high_level_clusters.txt"

    hours_between_label_dates_bda_g = 2
    hours_between_label_dates_adf_g = 2
    
    start_1 = "1935-01-01"
    end_1 = "1946-12-31"
    
    start_2 = "1947-01-01"
    end_2 = "1959-12-31"
    
    start_3 = "1960-01-01"
    end_3 = "1969-12-31"
    
    start_4 = "1970-01-01"
    end_4 = "1979-12-31"
    
    start_5 = "1980-01-01"
    end_5 = "1990-12-31"

    dates = [(start_2, end_2, hours_between_label_dates_bda_g, hours_between_label_dates_adf_g), (start_3, end_3, hours_between_label_dates_bda_g, hours_between_label_dates_adf_g), (start_4, end_4, 1, 1), (start_5, end_5, 1, hours_between_label_dates_adf_g)]
    """
    timestamp_topics_dict = plot_timeline_from_files.make_plot_from_files(label_file_bda, texts_topics_file_bda, outputdir,  file_name_beast_bda, label_length=label_length, hours_between_label_dates=hours_between_label_dates_bda, width_vertical_line=0.01, bar_transparency=0.3, bar_width=0.1, fontsize=7, link_mapping_func=bda_link_mapping, popup_link=True, use_separate_max_confidence_for_each_topic=True, circle_scale_factor=300, order_mapping_file = order_mapping_file_bda, order_colors=order_colors, user_defined_min_timestamp=start_1, user_defined_max_timestamp=end_1)
    """
    """
    for (start, end, hours_between_label_dates_bda, hours_between_label_dates_adf) in dates:
        print(start, end, hours_between_label_dates_bda, hours_between_label_dates_adf)
        print("bda")
        timestamp_topics_dict = plot_timeline_from_files.make_plot_from_files(label_file_bda, texts_topics_file_bda, outputdir,  file_name_beast_bda, label_length=label_length, hours_between_label_dates=hours_between_label_dates_bda, width_vertical_line=0.01, bar_transparency=0.3, bar_width=0.1, fontsize=7, link_mapping_func=bda_link_mapping, popup_link=True, use_separate_max_confidence_for_each_topic=True, circle_scale_factor=300, order_mapping_file = order_mapping_file_bda, order_colors=order_colors, user_defined_min_timestamp=start, user_defined_max_timestamp=end)
    
        print(start, end, hours_between_label_dates_bda, hours_between_label_dates_adf)
        print("afd")
        timestamp_topics_dict = plot_timeline_from_files.make_plot_from_files(label_file_adf, texts_topics_file_adf, outputdir,  file_name_beast_adf, label_length=label_length, hours_between_label_dates=hours_between_label_dates_adf, width_vertical_line=0.01, bar_transparency=0.3, bar_width=0.1, fontsize=7, link_mapping_func=adf_link_mapping, popup_link=True, use_separate_max_confidence_for_each_topic=True, circle_scale_factor=300, order_mapping_file = order_mapping_file_adf, order_colors=order_colors, user_defined_min_timestamp=start, user_defined_max_timestamp=end)
    """
        
    """
    timestamp_topics_dict = plot_timeline_from_files.make_plot_from_files(label_file_bda, texts_topics_file_bda, outputdir,  file_name_beast_bda, label_length=label_length, hours_between_label_dates=1, width_vertical_line=0.01, bar_transparency=0.3, bar_width=0.1, fontsize=7, link_mapping_func=bda_link_mapping, popup_link=True, use_separate_max_confidence_for_each_topic=True, circle_scale_factor=300, order_mapping_file = order_mapping_file_bda, order_colors=order_colors, user_defined_min_timestamp="1947-01-01", user_defined_max_timestamp="1979-12-31")
    """
    
    timestamp_topics_dict = plot_timeline_from_files.make_plot_from_files(label_file_diabetiker, texts_topics_file_diabetiker, outputdir,  file_name_diabetiker, label_length=label_length, hours_between_label_dates=30, width_vertical_line=0.1, bar_transparency=0.3, bar_width=0.1, fontsize=7,  use_separate_max_confidence_for_each_topic=True, circle_scale_factor=300, order_mapping_file = order_mapping_file_diabetiker, order_colors=order_colors)
   
    
#link_mapping_func=bda_link_mapping
do_plot()
