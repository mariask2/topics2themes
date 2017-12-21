Application of topic modelling functionality in Scikit-learn to extract arguments related to vaccination. 

The code was written for the specific task of using topic modelling to extract arguments for and against vaccination from Internet forums on vaccination. No efforts have been made to make the package generally usable.

There are, for instance, domain specific vocabularies for the pre-processing. If the package is to be applied on other domains, that vocabulary needs to be changed.

Given that you have a conda environment named topic_modelling where you have installed the following:

conda install numpy
conda install scipy
conda install scikit-learn
conda install gensim

If you want to use the functionality of running the topic modelling as a flask server, you also need to have the following installed:

pip install Flask

You write the following to run the code:

source activate topic_modelling
python make_topic_models.py


Part of the code is inspired from:
https://medium.com/@aneesha/topic-modeling-with-scikit-learn-e80d33668730
