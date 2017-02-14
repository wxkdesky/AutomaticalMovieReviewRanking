# @Wishcome  2017 
# Reach the author by Email:wxkdesky@hotmail.com
# class Moive_Review aims to fetch data from imdb
# and offer some utility function for other class

# -*- coding:utf-8 -*-
import requests
import re
import csv
import random
import time
import socket
import http.client
import urllib
import datetime
import os
from bs4 import BeautifulSoup

class Movie_Review:
    title_url=[]
    review_detail_url=[]
    pat=re.compile('(.*?)[?]')
    max_item_cnt=600
    #########
    server=['http://www.imdb.com']
    existed_movie=[]
    dir_name='PrepareDataset/dataset'
    #########

    def search_existed_movie(slef,path):
        try:
            os.mkdir(self.dir_name)
        except:
            print('makedir '+self.dir_name+' failed')
        for item in os.listdir(path+self.dir_name):
            if not os.path.isdir(path+self.dir_name+'/'+item):
                if 'csv' in item:
                    self.existed_movie.append(item)


    def printEx(func_name):
        print(func_name)
        def wrap(func):
            def wrap2(*args):
                func(*args)
            return wrap2
        return wrap


    def get_content(self,url , data = None):
        header={
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.235'
        }
        timeout = random.choice(range(80, 180))
        cnt=0
        while True:
            try:
                cnt+=1
                if cnt>=5:
                    return ''
                rep = requests.get(url,headers = header,timeout = timeout)
                rep.encoding = 'utf-8'
                break
            except socket.timeout as e:
                print( '3:', e)
                time.sleep(random.choice(range(8,15)))

            except socket.error as e:
                print( '4:', e)
                time.sleep(random.choice(range(20, 60)))

            except http.client.BadStatusLine as e:
                print( '5:', e)
                time.sleep(random.choice(range(30, 80)))

            except http.client.IncompleteRead as e:
                print( '6:', e)
                time.sleep(random.choice(range(5, 15)))
        return rep.text
    def get_data(self,data):
        html_data=BeautifulSoup(data,'html.parser')
        bd=html_data.body
        return bd

    def save_img(self,img_url,img_name):
        path_pref='movie_pic/'
        path_suf='.jpg'
        if img_url=='none':
            return
        else:
            urllib.request.urlretrieve(img_url,path_pref+img_name+path_suf)

    @printEx('movie_ranking_page')
    def movie_ranking_page(self):
        url='http://www.imdb.com/chart/moviemeter?ref_=nv_mv_mpm_8'
        data=get_content(url)
        bd=get_data(data)
        most_pop_movies=[]
        most_pop=bd.find('tbody')
        items=most_pop.find_all('tr')
        for i in items:
            can_go_on=True
            title_body=i.find('td',{'class':'titleColumn'})
            title=title_body.find('a').string
            title+=title_body.find('span').string
            relative_url=str(title_body.find('a')['href'])#relative url of movie title
            m1=self.pat.match(relative_url)#get the prefix of the url
            self.server.append(m1.group(1))# the 2nd prefix for next review url
            rank_body=i.find('td',{'class':'ratingColumn imdbRating'})#ranking
            img_url_body=i.find('td',{'class':'posterColumn'})#post img of movie
            img_url=''
            rank=''
            try:
                rank=rank_body.find('strong').string
                img_url=img_url_body.find('img')['src']
            except:
                rank='0'
                img_url='none'
            for mov in self.existed_movie:
                if title in mov:
                    print(title+' already existed in current folder['+self.dir_name+']')
                    can_go_on=False
                    break
            if can_go_on:
                self.title_url.append((rank,title,self.server[0]+relative_url))#absolute url of movie title
                movie_rough_review_page()
                self.title_url.clear()
                self.server.pop()

            # save_img(img_url,title)
            # log.write(title+' '+rank+'\n')
            # print(title.string+' '+rank)
        # log.close()

    @printEx('movie_rough_review_page')
    def movie_rough_review_page(self):
        for (rank,title,url) in self.title_url:
            data=get_data(get_content(url))
            div=None
            span=None
            try:
                div=data.find('div',{'class':'titleReviewbarItemBorder'})
                span=div.find('span')
            except:
                print('can not find matching reviews in rough review page')
                continue
            users=''
            relative_url=''
            for ob in span.children:
                if ob=='\n':
                    continue
                relative_url=ob['href']
                users=ob.string           
                break
            print(users+'--'+relative_url)
            self.review_detail_url.append((rank,title,self.server[0]+self.server[1]+relative_url))#relative url:reviews?ref_=tt_ov_rt
            movie_detail_review_page()
            self.review_detail_url.clear()

    def save_csv(self,data,name):
        with open(name,'w',encoding='utf-8') as f:
            f_csv=csv.writer(f,dialect='excel')
            first_line=['title','rank','review_rank','review_title','review','reviewer','reviewer_from','review_time']
            f_csv.writerow(first_line)
            for item in data:
                f_csv.writerow(item)

    @printEx('movie_detail_review_page')
    def movie_detail_review_page(self):
        final_detail_review_item=[]
        for (rank,title,url) in self.review_detail_url:
            cnt=0
            data=get_data(get_content(url))
            review_rank=''
            review_title=''
            reviewer=''
            reviewer_from=''
            review_time=''
            main_review=''
            final_detail_review_item.clear()
            can_go_on=True
            review_cn=0
            try:
                while can_go_on:
                    div=data.find('div',{'id':'tn15content'})
                    div_yn=div.find_all('div',{'class':'yn'})
                    for item in div_yn:
                        review_cn+=1
                        print(title+'--'+str(review_cn)+' item')
                        if review_cn>self.max_item_cnt:
                            break
                        tmp=[]
                        main=item.find_previous_sibling('p')
                        main_review=main.contents[0]
                        short_div=main.find_previous_sibling('div')
                        h2=short_div.find('h2')
                        review_title=h2.string# br is as follows, thus sibling can not work
                        try:
                            review_rank_img=h2.find_next_sibling('img')
                            review_rank=str(review_rank_img['alt']).replace('/10','')
                        except:
                            review_rank='0'
                        author_b=short_div.find('b')
                        author_a=author_b.find_next_sibling('a')
                        reviewer=author_a.string
                        from_place=author_a.find_next_sibling('small')
                        if from_place==None:
                            reviewer_from='none'
                        else:
                            reviewer_from=from_place.string# br is as follows, thus sibling can not work
                        time_small=short_div.find_all('small')
                        review_time=time_small[len(time_small)-1].string
                        tmp.append(title)
                        tmp.append(rank)  
                        tmp.append(review_rank)         
                        tmp.append(review_title)
                        tmp.append(main_review.replace('\n',''))
                        tmp.append(reviewer)
                        tmp.append(reviewer_from)
                        tmp.append(review_time)
                        final_detail_review_item.append(tmp)
                    cnt+=1
                    # print(title+'**'+str(cnt)+' movie')
                    try:
                        td1=data.find('td',{'nowrap':'1'})
                        td2=td1.find_next_sibling('td')
                        next_page_a=td2.find_all('a')
                        last_page=next_page_a[len(next_page_a)-1]
                        next_page=last_page['href']
                        img_page=last_page.find('img')
                        next_img=img_page['alt']
                        data=get_data(get_content(self.server[0]+self.server[1]+next_page))
                    except:
                        break
            except:
                tmp=[]
                tmp.append(title)
                tmp.append(rank)
                tmp.append('0')
                tmp.append('none') 
                tmp.append('none')
                tmp.append('none')
                tmp.append('none')
                tmp.append('none') 
                final_detail_review_item.append(tmp)
            save_csv(final_detail_review_item,self.dir_name+'/'+title+'.csv')       

