# @Wishcome  2017 
# Reach the author by Email:wxkdesky@hotmail.com
# This is the main funcion for the whole project
# It will fetch data from imdb and parse the data for training
#After training, it will predict test samples
#please read README.md carefully before running code.

# -*- coding:utf-8 -*-
from PrepareDataset.readcsv import ParseCSV
from PrepareDataset.movie_review import Movie_Review
from Training.train import BuildModel
from Predict.classification import VisualizeResult
import sys
data_is_fetched=True
train=False

if __name__=='__main__':
    if not data_is_fetched:
        mr=Movie_Review()
        mr.search_existed_movie('./')
        mr.movie_ranking_page()
        mr.movie_rough_review_page()
        mr.movie_detail_review_page()
        print('imdb movie review fetching finished...')
    pcsv=ParseCSV()
    if(not pcsv.load_raw_data('raw_data.pkl')):
        dataset='./PrepareDataset/dataset'
        if len(sys.argv)==2:
            dataset=sys.argv[1]   
        pcsv.list_csv(dataset)
        pcsv.arrange_csv()
    pcsv.tf_idf()
    pcsv.sort_tf_idf()
    pcsv.feature_extraction()
    if train:
        bm=BuildModel()
        bm.build_models()
    sd=BuildModel.get_split_data()
    vr=VisualizeResult()
    vr.set_default_test_data(sd.test)
    vr.visualize()
