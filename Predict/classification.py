# @Wishcome  2017 
# Reach the author by Email:wxkdesky@hotmail.com
# class Classification aims to predict test samples
# class VisualizeResult aims to give the classification report

# -*- coding:utf-8 -*-
from sklearn.externals import joblib
from Training.train import BuildModel
from Training.train import Train
from PrepareDataset.readcsv import ParseCSV
from sklearn import metrics
import numpy as np
import re


class Classification:
    model=[]
    suffix='.model'
    predict_result_proba=[]
    predict_result_lable=[]
    raw_data=[]
    def __init__(self):
        self.raw_data=[]
        self.model=[]
        self.predict_result_lable=[]
        self.predict_result_proba=[]
        try:
            for item in BuildModel.model_name:
                self.model.append(joblib.load(item+self.suffix)) 
        except:
            self.model=[]
            print('loading model falied!')

    def Predict(self,sample):
        if self.model==[]:
            print('No trained model found!')
            return
        else:
            for item in self.model:
                self.predict_result_proba.append(item.predict_proba(sample))
                self.predict_result_lable.append(item.predict(sample))

class VisualizeResult:
    test_data_lable=[]
    test_lable_name=['people_test_lable.txt','story_test_lable.txt','picture_test_lable.txt','emotion_test_lable.txt']
    test_data=[]
    test_data_path='test_data.txt'
    def __init__(self):
        try:
            for item in self.test_lable_name:
                tmp=ParseCSV.load_file(item)
                if tmp!=None:
                    self.test_data_lable.append(tmp)
                else:
                    raise Exception('error')           
        except:
            self.test_data_lable=[]
            print('loading test data lable failed!')
    
    def build_test_data(self):
        # raw_data=[]
        self.raw_data=ParseCSV.load_file(self.test_data_path,parse=False)
        if raw_data==[]:
            print('loading test data falied!Stop build_test_data()...')
            return False
        processed_data=[]
        for item in self.raw_data:
            processed_data.append(ParseCSV.tokenize(self.raw_data))
        tf_idf=ParseCSV.feature_extraction_ex(processed_data)
        feature_matrix=Train.build_test_data(tf_idf)
        self.test_data=feature_matrix
        return True

    def set_default_test_data(self,default_data):
        self.test_data=default_data
    
    @classmethod
    def split_lables(cls,file,train=False):
        test_data_lable=[]
        try:
            people_lable=[]
            story_lable=[]
            picture_lable=[]
            emotion_lable=[]
            for line in open(file,'r',encoding='utf-8'):
                people,story,picture,emotion=map(int,line.split(','))
                people_lable.append(people)
                story_lable.append(story)
                picture_lable.append(picture)
                emotion_lable.append(emotion)
            test_data_lable.append(people_lable)
            test_data_lable.append(story_lable)
            test_data_lable.append(picture_lable)
            test_data_lable.append(emotion_lable)
        except:
            print('loading lable file ['+file+'] failed!')
            return []
        if train:
            for item in range(len(test_data_lable)):
                path=''
                if item==0:
                    path='./Data/people.txt'
                elif item==1:
                    path='./Data/story.txt'
                elif item==2:
                    path='./Data/picture.txt'
                elif item==3:
                    path='./Data/emotion.txt'
                f=open(path,'w',encoding='utf-8')
                length=len(test_data_lable[item])
                for i in range(length):
                    if i<length-1:
                        f.write(str(test_data_lable[item][i])+'\n')
                    else:
                        f.write(str(test_data_lable[item][i]))
                f.close()
        return test_data_lable

    def visualize(self):
        if self.test_data==[]:
            print('please specify test_data!')
            return
        pat=re.compile(r'_.*')
        cls_model=Classification()
        if cls_model.model!=[]:
            cls_model.Predict(self.test_data)
        for i in range(len(cls_model.model)):
            print('Model:'+pat.sub('',self.test_lable_name[i]))
            print(metrics.classification_report(self.test_data_lable[i],cls_model.predict_result_lable[i]))
            print(metrics.confusion_matrix(self.test_data_lable[i],cls_model.predict_result_lable[i]))
        print('Now we see the ranking for each movie review...\nMovie Review(No.)   Ranking(People)  Ranking(Story)  Ranking(Picture)  Ranking(Emotion)')
        rank=[]
        sample_length=len(self.test_data)
        for item in cls_model.predict_result_proba:
            tmp=[]
            for item2 in item.tolist():
                tmp.append(int(item2[1]*10))
            rank.append(tmp)
        for i in range(sample_length):
            print('%d                 %d                 %d                 %d                 %d'%(i,rank[0][i],rank[1][i],rank[2][i],rank[3][i]))

