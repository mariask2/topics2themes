Application of topic modelling functionality in Scikit-learn.

The code was originally written for the specific task of using topic modelling to extract arguments "for" and "against" vaccination from Internet forums on vaccination in English. There code, therefore, currently uses domain specific vocabularies for the pre-processing. If the package is to be applied on other domains, that vocabulary needs to be changed.

Given that you have a conda environment named topic_modelling where you have installed the following:

conda install numpy

conda install scipy

conda install scikit-learn

conda install gensim

conda install -c anaconda mongodb

conda install -c anaconda pymongo

If you want to use the functionality of running the topic modelling as a flask server, you also need to have the following installed:

pip install Flask

pip install -U flask-cors


To run the code you need a mongdodb server to be running.

To achieve that, create the directory where the data is to be saved, e.g., “data/db
Then start the server giving that directory as a parameter:
mongod --dbpath data/db/
(mongodb listenes as default on port 27017. Currently that port is assumed to be the one used)

You write the following to run the code:

source activate topic_modelling

To create a new topic model:

python make_topic_models.py

To create a new topic model for the data in the folders data_folder/vaccination_constructed_data
python make_topic_models.py --project data_folder.vaccination_constructed_data


To run the topic modell as a flask server, you write:

python restful_api_topic_modelling.py [port]

for instance:

python restful_api_topic_modelling.py 5000



Part of the code is inspired from:
https://medium.com/@aneesha/topic-modeling-with-scikit-learn-e80d33668730
