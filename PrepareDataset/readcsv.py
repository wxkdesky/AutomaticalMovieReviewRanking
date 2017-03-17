# @Wishcome  2017 
# Reach the author by Email:wxkdesky@hotmail.com
# class ParseCSV aims to parse the review data crawlled from imdb
# and arrange them in oder to be ready for training

# -*- coding:utf-8 -*-
import csv
import os
import sys
import nltk
import string
import pickle
import gensim
import numpy as np
from nltk.probability import FreqDist
# No stemming here
class ParseCSV:
    prefix='Data/'
    csv_list=[]
    field_list=['title','rank','review_rank','review_title','review','reviewer','reviewer_from','review_time']
    stop_words=['i','a','about','an','as','are','at','be','by','com','de','en','for','from','how','in','is','it','you','la','of','on','or','and','that','the','this','to','was','what','when','where','who','will','with',"'m","'s",'`','``',"''",'$','~','@','&','(',')','{','}','[',']','/','\\','1','2','3','4','5','6','7','8','9','0']
    raw_data=[]
    document=[]
    tf_idf_by_doc=[]
    vacab=dict()
    word_vec_doc=[]
    word_vec_binary_doc=[]
    doc_cnt=0
    vacab_cnt=0
    vocab_pickle='vocab.pkl'
    raw_pickle='raw_data.pkl'
    doc_freq_pickle='doc_freq.pkl'
    tf_idf_pickle='tf_idf.pkl'
    sorted_tf_idf_pickle='sorted_tf_idf.pkl'
    word_vec_doc_pickle='word_vec_feature.pkl'
    word_vec_binary_doc_pickle='word_vec_binary.pkl'
    csv_is_parsed=False
    tf_idf_computed=False
    def list_csv(self,path):
        for item in os.listdir(path):
            new_path=path+'/'+item
            if not os.path.isdir(new_path):
                if '.csv' in item:
                    self.csv_list.append(new_path)
    # def show_csv(self):
    #     for item in self.csv_list:
    #         with open(item,'r') as csvfile:
    #             reader=csv.DictReader(csvfile)
    #             rows=[row for row in reader]
    #             print(rows)
    def arrange_csv(self):
        if len(self.csv_list)==0:
            print('no csv file found!')
            return
        for item in self.csv_list:
            with open(item,'r',encoding='utf-8') as csvfile:
                reader=csv.DictReader(csvfile)
                for row in reader:
                    tmp=dict()
                    tmp[self.field_list[1]]=float(row[self.field_list[1]])
                    tmp[self.field_list[2]]=int(row[self.field_list[2]])
                    tmp[self.field_list[3]]=self.tokenize(str(row[self.field_list[3]]).lower())
                    if self.field_list[4]=='none':
                        continue
                    tmp[self.field_list[4]]=self.tokenize(str(row[self.field_list[4]]).lower())
                    self.raw_data.append(tmp)
            print('finish arranging movie '+item.replace('.csv',''))
        self.doc_cnt=len(self.raw_data)
        print('finish arrangement!total reviews are '+str(self.doc_cnt))#19062
        self.pickle_dump(self.raw_pickle,self.raw_data)
        self.csv_is_parsed=True
    @classmethod
    def pickle_dump(self,path,data):
        raw_data_pickle=open(self.prefix+path,'wb')
        pickle.dump(data,raw_data_pickle,-1)
        raw_data_pickle.close()
    @classmethod
    # remove stop_words and tokenize
    def tokenize(self,msg):
        punc_include=nltk.word_tokenize(str(msg).lower())
        punc_exclude=[]
        for i in range(len(punc_include)):
            if punc_include[i] not in string.punctuation and punc_include[i] not in self.stop_words:
                punc_exclude.append(punc_include[i])
        return punc_exclude
    # feature
    #1.tf_idf combined word vector
    #2.binary word_vector
    def feature_extraction(self):
        if os.path.exists(self.prefix+self.word_vec_doc_pickle):
            print('word vector feature has already been generated!')
            return
        if not os.path.exists(self.prefix+self.sorted_tf_idf_pickle) or not os.path.exists(self.prefix+self.vocab_pickle):
            print('can not find sort_tf_idf.pkl or vocab.pkl!you must call sort_tf_idf() first')
        else:
            sort_tfidf=self.load_pickle_data(self.sorted_tf_idf_pickle)
            model=gensim.models.Word2Vec.load_word2vec_format('wordvectors.bin',binary=True)
            all_vocab=list(model.vocab.keys())
            all_data_vocab=list(self.load_pickle_data(self.vocab_pickle).keys())
            self.doc_cnt=len(all_data_vocab)
            print('begin to process word_vector...')
            for doc in sort_tfidf:
                tmp=[]
                # bi_tmp=[]
                for word in doc:
                    if word[0] in all_vocab:
                        tmp.append((word[0],word[1]*np.array(model[word[0]])))
                    # index=-1
                    # try:
                    #     index=all_data_vocab.index(word[0])
                    # except:
                    #     pass
                    # if index!=-1:
                    #     xtmp=[x for x in range(self.doc_cnt)]
                    #     xtmp[index]=1
                    #     bi_tmp.append((word[0],xtmp))
                self.word_vec_doc.append(tmp)
                # self.word_vec_binary_doc.append(bi_tmp)
            print('finish processing word_vector...begin to dump')
            self.pickle_dump(self.word_vec_doc_pickle,self.word_vec_doc)
            # self.pickle_dump(self.word_vec_binary_doc_pickle,self.word_vec_binary_doc)
        print('feature extraction finished!')
    # tf-idf=freq(word)*(log(n/N(word))+1)
    # where n is the total number of words in the dictionary ->self.vacab.keys()
    # and N is a function giving the total number of documents the keyword appears in ->self.vacab
    # freq(word) is the frequency that keyword appears in the specific document ->self.document
    def tf_idf(self):
        if os.path.exists(self.prefix+self.tf_idf_pickle) or os.path.exists(self.prefix+self.sorted_tf_idf_pickle):
            print('tf_idf file already exists...function begin to exit...')
            self.tf_idf_computed=True
            return
        if self.csv_is_parsed:
            cnt=0
            for item in self.raw_data:
                cnt+=1
                print('organizing '+str(cnt)+' document......')
                tmp=FreqDist(item[self.field_list[4]])
                doc_keys_list=list(tmp.keys())
                for word in doc_keys_list:
                    if word not in self.vacab.keys():
                        self.vacab[word]=1
                    else:
                        self.vacab[word]+=1
                self.document.append(tmp)
            self.pickle_dump(self.doc_freq_pickle,self.document)
            self.pickle_dump(self.vocab_pickle,self.vacab)
            self.vacab_cnt=len(list(self.vacab.keys()))
            print('Statistics done....vocab has size of '+str(self.vacab_cnt))
            cnt=0
            for doc in self.document:
                cnt+=1
                print('computing '+'tf_idf for '+str(cnt)+' document')
                tmp=[]
                for key in list(doc.keys()):
                    fw=doc[key]
                    n=self.vacab_cnt
                    N=self.vacab[key]
                    tf_idf=fw*(np.log10(n/N)+1)
                    tmp.append((key,tf_idf))
                self.tf_idf_by_doc.append(tmp)
            print('Finish computing td_idf.Begin to dump data')
            self.pickle_dump(self.tf_idf_pickle,self.tf_idf_by_doc)
            self.tf_idf_computed=True
        else:
            print('you must call arrange_csv() or load_raw_dara() first!')
    
    def sort_tf_idf(self):
        if self.tf_idf_computed:
            self.tf_idf_by_doc=self.load_pickle_data(self.tf_idf_pickle)
            sorted_tf_idf=self.load_pickle_data(self.sorted_tf_idf_pickle)
            if self.tf_idf_by_doc==None:
                print('sort_tf_idf() exits without modification...')
                return
            if sorted_tf_idf!=None:
                print('sort_tf_idf() exits without modification...')
                return
            new_tf_idf=[]
            print('begin to sort tf_idf...')
            for item in self.tf_idf_by_doc:
                tmp=sorted(item,key=lambda x_tuple:x_tuple[1],reverse=True)
                new_tf_idf.append(tmp)           
            self.pickle_dump(self.sorted_tf_idf_pickle,new_tf_idf)
            print('tf_idf has been successfully decendingly sorted')
            return new_tf_idf
        else:
            print('you must call tf_idf() first!')
            return None

    def load_raw_data(self,path):
        try:
            pickl_data=open(self.prefix+path,'rb')        
            self.raw_data=pickle.load(pickl_data)
            pickl_data.close()
            self.csv_is_parsed=True
        except:
            print('can not find file ['+path+']!load raw_data failed!')
            return False
        return True
    #convert str to int if parse=True
    @classmethod
    def load_file(self,path,parse=True):
        data=[]
        try:
            for line in open(self.prefix+path,'r',encoding='utf-8'):
                if parse:
                    data.append(int(line.replace('\n','')))
                else:
                    data.append(line.replace('\n',''))
        except:
            return None
        return data

    @classmethod
    def load_pickle_data(self,path):
        try:
            pickle_data=open(self.prefix+path,'rb')
            data=pickle.load(pickle_data)
            return data
        except:
            print('load pickle data failed!')
            return None
    @classmethod
    def feature_extraction_ex(self,raw_data_out):
        vacab=dict()
        document=[]
        tf_idf_by_doc=[]
        length=0
        cnt=0
        for item in raw_data_out:
            cnt+=1
            print('organizing '+str(cnt)+' document......')
            tmp=FreqDist(item)
            doc_keys_list=list(tmp.keys())
            for word in doc_keys_list:
                if word not in vacab.keys():
                    vacab[word]=1
                else:
                    vacab[word]+=1
            document.append(tmp)
        length=len(list(vacab.keys()))
        for doc in document:
            tmp=[]
            for key in list(doc.keys()):
                fw=doc[key]
                n=length
                N=vacab[key]
                tf_idf=fw*(np.log10(n/N)+1)
                tmp.append((key,tf_idf))
            tf_idf_by_doc.append(tmp)
        new_tf_idf=[]
        print('begin to sort tf_idf...')
        for item in tf_idf_by_doc:
            tmp=sorted(item,key=lambda x_tuple:x_tuple[1],reverse=True)
            new_tf_idf.append(tmp) 
        model=gensim.models.Word2Vec.load_word2vec_format('wordvectors.bin',binary=True)
        all_vocab=list(model.vocab.keys())
        all_data_vocab=list(vacab.keys())
        print('begin to process word_vector...')
        word_vec_doc=[]
        for doc in new_tf_idf:
            tmp=[]
            for word in doc:
                if word[0] in all_vocab:
                    tmp.append((word[0],word[1]*np.array(model[word[0]])))
            word_vec_doc.append(tmp)
        print('finish processing word_vector...')
        return word_vec_doc
