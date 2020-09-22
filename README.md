Note: The name of the repository was recently changed. It still works to clone from and push to the repository using the old name, but to avoid confusion, it can be good to do:

git remote set-url origin https://github.com/mariask2/topics2themes.git


Application of topic modelling functionality in Scikit-learn.

Given that you have a conda environment named topic_modelling where you have installed the following:

conda install numpy

conda install scipy

conda install scikit-learn

conda install gensim

conda install -c anaconda mongodb

conda install -c anaconda pymongo

conda install nltk

conda install joblib

pip install Flask

pip install -U flask-cors

If you want to plot extracted terms, you also need:

conda install matplotlib

When you run the code the first time, you'll get the following error message:

Resource punkt not found.
  Please use the NLTK Downloader to obtain the resource:
  >>> import nltk
  >>> nltk.download('punkt')

Follow the NLTK instructions to fix this

******
To run the code you need a mongdodb server to be running.

To achieve that, create the directory where the data is to be saved, e.g., “data/db
Then start the server giving that directory as a parameter:
mongod --dbpath data/db/
(mongodb listenes as default on port 27017. Currently that port is assumed to be the one used)

You write the following to run the code:

source activate topic_modelling



To create a new topic model for the data in the folders data_folder/vaccination_constructed_data
python make_topic_models.py --project data_folder.vaccination_constructed_data_marked
(This will not be save to the database, only written to a file)

To run the topic modell as a flask server, you write:

python restful_api_topic_modelling.py [port]

for instance:

python restful_api_topic_modelling.py 5000

***************
You will need a file in the same directory from the code it is run, which is called "approved_keys.txt".
Here you put the allowed keys that the user of the user interface need to input when promted (when the interface is started).
One allowed key per line, e.g.;
key1
key2
key3

****************
The text collections that are available to the user must be positioned in a folder named "data_folder".
Each text collection is positioned in a subfolder of "data_folder". This subfolder should, in turn, contain several subfolders for each of the dynamic labels of the data set. The example text collection "vaccination_constructed_data_marked" set  has three dynamic labels "for", "against" and "uncertain", and correspondingly three subfolders with these names. The actual text files, should be placed as ".txt"-files in these sub-folders. (only .txt-files will be used for topic modelling)

********
As a default, the "data_folder" is positioned as a subdirectory in the folder with the python code.
The variable "WORKSPACE_FOLDER" in the file "environment_configuration.py"  can, however, be changed to another location, and the "data_folder" can be positioned there.


Part of the code is inspired from:
https://medium.com/@aneesha/topic-modeling-with-scikit-learn-e80d33668730
