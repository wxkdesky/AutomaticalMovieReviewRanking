# Automatical Movie Review Ranking System
This is a project aims to `automatically rank the movie reviews`.For now,the training dataset is fetched from [imdb](http://www.imdb.com)
This project mainly depends on the context word vector tool published by `Xukang Wu` on github called [ContextWordVector](https://github.com/wxkdesky/ContextWordVectors)
All the code of this project are written in Python3.4
#Prerequisite
* Python3.4 is installed in your system(Windows or Linux/unix). Anaconda3 is highly recommended
* Python packages including `numpy`,`nltk`,`gensim`,`beautifulsoup4`,`scikit-learn` must be installed. Other dependencies are normally satisfied as they are built-in modules
* make sure the word vectors are built via `ContextWordVector` and name it `wordvectors.bin`.In addition, put this file in the root dir of the project
* In the dir `./PrepareDataset/dataset`, place the csv files fetched from imdb to make sure dataset is well provided. The movie review files can be downloaded from [this onedrive link](https://1drv.ms/f/s!AoNNtfHIv_BvpN0Y1pLBH0yPU426HA) either.
#Usage
The entrance is `here_we_go.py`. This file accepts 1 argument atmost. The argument provided by user is to specify the dir in which the movie review files are placed.
If the Prerequisite above are satisfied, please run in your terminal`(cmd in windows and terminal in linux/unix)`
`python here_we_go.py`
else do
`python here_we_go.py your_dataset_dir`
Then the system will run to the end.
#Package Instruction
all the packages in the project are described below
##Movie_Review
It is a crawler to fetch movie reviews from imdb
###Files It creates during running
* csv files in the dir `./PrepareDataset/dataset`. Each csv file is named by the corresponding movie title
##ParseCSV
It is a parser to load csvfiles and combine word vectors to build raw features for each movie review.
###Files It creates during running
Files below are generated in the dir `./Data`
* `raw_data.pkl` movie reviews are purified from csv file into this file
* `vocab.pkl` vocabulary made after searching the whole dataset
* `doc_freq.pkl` frequency of each word in every document is kept in this file
* `tf_idf.pkl` tf_idf of each word in every document is kept in this file
* `sorted_tf_idf.pkl` sort each word in v=every document by the value of `tf_idf`
* `word_vec_feature.pkl` word vector of each word in every document.`This file is large`
##Train,BuildModel
It aims to split data into training/testing and build input features for any testing samples and then do `self-training`
Files below are requested in the dir `./Data`
`Specially, this package needs some extra files which are listed below:`
###Files It depends on before running
* `people.txt`
* `story.txt`
* `picture.txt`
* `emotion.txt`
Files mentioned above are training lables for each class. Each line is 0 or 1 for one sample.
Files below are generated in the root dir `./`
###Files It creates during running
* `people.model`
* `story.model`
* `picture.model`
* `emotion.model`
Models mentioned above is four different kinds of classifiers. The classification method is `LR with L2 penalty`.
`BuildModel` is just a wrapper of `Train`
##Classification
It aims to predict testing samples.
`Specially, this package needs some extra files which are listed below:`
###Files It depends on before running
* `people.model`
* `story.model`
* `picture.model`
* `emotion.model`
Yes, it needs to load well trained models.
##VisualizeResult
It aims to visualize prediction results using Precise/Recall/F1-Score
Files below are requested in the dir `./Data`
`Specially, this package needs some extra files which are listed below:`
###Files It depends on before running
* `people_test_lable.txt`
* `story_test_lable.txt`
* `picture_test_lable.txt`
* `emotion_test_lable.txt`
Files mentioned above are lables of testing samples.


If met with any problem, please contact me:`wxkdesky@hotmail.com`
Good luck!