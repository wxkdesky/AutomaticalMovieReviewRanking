# @Wishcome  2017 
# Reach the author by Email:wxkdesky@hotmail.com
# class Train aims to build the final model
# class BuildModel is a wrapper for Train

# -*- coding:utf-8 -*-
from PrepareDataset.readcsv import ParseCSV
from sklearn.externals import joblib
# from sklearn import svm
from sklearn.linear_model import SGDClassifier
import numpy as np

class Train:
    #cls_name
    cls_name=''
    #label name
    lable_name=''
    #labled data   
    labled=[]
    #labled data with lables
    labled_lable=[]
    #unlabled data
    unlabled=[]
    #test data
    test=[]
    #the largest confidence samples
    __K=5

    def __init__(self,classifier_name):
        self.cls_name=classifier_name
        self.lable_name=classifier_name+'.txt'
        self.labled=[]
        self.labled_lable=[]
        self.unlabled=[]
        self.test=[]

    def split_data(self,lable=100,unlable=18862,test=0):
        feature_matrix=[]
        raw_feature=ParseCSV.load_pickle_data(ParseCSV.word_vec_doc_pickle)
        if raw_feature==None:
            return False      
        length=len(raw_feature[0][0][1])  
        max_v=0
        for doc in raw_feature:
            tmp=[]
            tmp=np.array([0 for i in range(length)])
            for word in doc:
                tmp=tmp+word[1]
            # tmp=tmp/np.linalg.norm(tmp)
            i_max=np.max(np.abs(tmp))
            if i_max>max_v:
                max_v=i_max
            feature_matrix.append(tmp)
        feature_matrix=feature_matrix/max_v
        feature_matrix=feature_matrix.tolist()
        self.labled=feature_matrix[0:lable]
        self.unlabled=feature_matrix[lable:unlable+lable]
        if test==0:
            self.test=feature_matrix[lable+unlable:]
        else:
            self.test=feature_matrix[lable+unlable:lable+unlable+test]
        self.labled_lable=[]
        print('split data finished...')
        return True
    

    def split_data_ex(self,lable=[[0,6],[6,40],[135,152],[840,844],[1440,1449],[1562,1592]],unlable=18862,test=0):
        feature_matrix=[]
        raw_feature=ParseCSV.load_pickle_data(ParseCSV.word_vec_doc_pickle)
        if raw_feature==None:
            return False      
        length=len(raw_feature[0][0][1])  
        max_v=0
        for doc in raw_feature:
            tmp=[]
            tmp=np.array([0 for i in range(length)])
            for word in doc:
                tmp=tmp+word[1]
            # tmp=tmp/np.linalg.norm(tmp)
            i_max=np.max(np.abs(tmp))
            if i_max>max_v:
                max_v=i_max
            feature_matrix.append(tmp)
        feature_matrix=feature_matrix/max_v
        feature_matrix=feature_matrix.tolist()
        for item in lable:
            for i in range(item[0],item[1]):
                self.labled.append(feature_matrix[i])
                feature_matrix[i]=[]
        ind=0
        for i in range(len(feature_matrix)):
            if ind <unlable:
                if feature_matrix[i]!=[]:
                    self.unlabled.append(feature_matrix[i])
                    feature_matrix[i]=[]
                    ind+=1
        if test==0:
            for j in range(len(feature_matrix)):
                if feature_matrix[j]!=[]:
                    self.test.append(feature_matrix[j])
                    feature_matrix[j]=[]
        else:
            if test<=len(feature_matrix)-len(self.labled)-len(self.unlabled):
                ind1=0
                for j in range(len(feature_matrix)):
                    if ind1<test:
                        if feature_matrix[j]!=[]:
                            self.test.append(feature_matrix[i])
                            feature_matrix[j]=[]
                            ind1+=1
            else:
                return False
        self.labled_lable=[]
        print('split data finished...')
        return True
    
    @classmethod
    def build_test_data(self,tf_idf):
        feature_matrix=[]
        length=len(tf_idf[0][0][1])
        max_v=0
        for doc in tf_idf:
            tmp=[]
            tmp=np.array([0 for i in range(length)])
            for word in doc:
                tmp=tmp+word[1]
            # tmp=tmp/np.linalg.norm(tmp)
            i_max=np.max(np.abs(tmp))
            if i_max>max_v:
                max_v=i_max
            feature_matrix.append(tmp)
        feature_matrix=feature_matrix/max_v
        feature_matrix=feature_matrix.tolist()
        return feature_matrix

    def load_labled_lable(self):
        file=self.lable_name
        if len(self.labled)==0:
            print('Please call split_data() first!')
            return False
        total_lable=ParseCSV.load_file(file)
        if(len(total_lable)<len(self.labled)):
            print('Labled data has size of '+str(len(total_lable))+'...But you set the lable data size to '+str(len(self.labled))+'!please make your lable data size smaller in split_data()..')
            return False
        for i in range(len(self.labled)):
            self.labled_lable.append(total_lable[i])
        print('loading lable file succeed...')
        return True


    def __self_training(self):
        lr=SGDClassifier(loss='log', penalty='l2',alpha=1e-3, n_iter=5, random_state=42,n_jobs=-1)#loss=hinge become a linear svm;loss=log become a logistic regression     
        print('begin to self training...')  
        while len(self.unlabled)>0:
            lr.fit(self.labled,self.labled_lable)
            predicted_unlabled_prob=lr.predict_proba(self.unlabled)
            predicted_unlabled=[]
            for i in range(len(predicted_unlabled_prob)):
                if  predicted_unlabled_prob[i][0]>predicted_unlabled_prob[i][1]:
                    predicted_unlabled.append((i,0,predicted_unlabled_prob[i][0]))
                else:
                    predicted_unlabled.append((i,1,predicted_unlabled_prob[i][1]))
            predicted_unlabled_sorted=sorted(predicted_unlabled,key=lambda x:x[2],reverse=True)
            for i in range(self.__K):
                if i<len(predicted_unlabled_sorted):
                    self.labled.append(self.unlabled[predicted_unlabled_sorted[i][0]])
                    self.labled_lable.append(predicted_unlabled_sorted[i][1])
                    self.unlabled[predicted_unlabled_sorted[i][0]]=[]
            unlabled_tmp=[]
            for item in self.unlabled:
                if item!=[]:
                    unlabled_tmp.append(item)
            self.unlabled=unlabled_tmp
        joblib.dump(lr,self.cls_name+'.model')  
        print(self.cls_name+'.model has been successfully dumped!') 
    
    def train(self):
        if self.split_data_ex()==True:    
            if self.load_labled_lable()==True:
                self.__self_training()

#models:People,Story,Emotion
class BuildModel:
    model=[]
    model_name=['people','story','picture','emotion']
    def __init__(self):
        for item in self.model_name:
            self.model.append(Train(item))

    def build_models(self):
        for item in self.model:
            item.train()
    
    @classmethod
    def get_split_data(self):
        sd=Train('people')
        sd.split_data_ex()
        return sd

