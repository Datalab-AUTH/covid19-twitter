#!/usr/bin/env python3

import pymongo
from pymongo import MongoClient
import datetime
import pandas as pd
import pickle
from bs4 import BeautifulSoup
import requests
import os
import time
import sys

mongoURL = os.environ['MONGOURL']
mongoDB = os.environ['MONGODB']
mongoCollection = os.environ['MONGOCOLLECTION']
twitter_init = int(os.environ.get('TWITTER_INIT', default = '2'))

client = MongoClient(mongoURL)
db = client[mongoDB]
coll = db[mongoCollection]

def get_tweets_per_day_csv():
    d={}
    today =  datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    yesterday = today - datetime.timedelta(days=1)
    iterator = coll.find({'created_at':{'$lte': yesterday}})
    for i in iterator:
        if i['created_at'].date() in d:
            d[i['created_at'].date()]+=1
        else:
            d[i['created_at'].date()]=1
    pickle.dump(d,open('data/tweets','wb'))

def get_tags_per_day_csv():
    d={}
    tags={}
    today =  datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    print (today)
    yesterday = today - datetime.timedelta(days=1)
    print (yesterday)
    iterator = coll.find({'created_at':{'$lte': yesterday}})
    for i in iterator:
        if 'entities' in i:
            if 'hashtags' in i['entities']:
                for h in i['entities']['hashtags']:
                    if i['created_at'].date() in d:
                        if h['text'] in d[i['created_at'].date()]:
                            d[i['created_at'].date()][h['text']]+=1
                        else:
                            d[i['created_at'].date()][h['text']]=1
                    else:
                        d[i['created_at'].date()]={h['text']:1}
    pickle.dump(d,open('data/tags','wb'))

def get_urls_per_day_csv():
    d={}
    today =  datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    yesterday = today - datetime.timedelta(days=1)
    iterator = coll.find({'created_at':{'$lte': yesterday}})
    for i in iterator:
        if 'entities' in i:
            if 'urls' in i['entities']:
                for h in i['entities']['urls']:
                    if i['created_at'].date() in d:
                        if h['expanded_url'] in d[i['created_at'].date()]:
                            d[i['created_at'].date()][h['expanded_url']]+=1
                        else:
                            d[i['created_at'].date()][h['expanded_url']]=1
                    else:
                        d[i['created_at'].date()]={h['expanded_url']:1}
    pickle.dump(d,open('data/urls','wb'))

def get_page_title(url):
    r = requests.get(url)
    html_content = r.text
    soup = BeautifulSoup(html_content, 'html.parser')
    if '403' in soup.title.string:
        return url
    else:
        return soup.title.string

def convert_to_csv():
    tweets = pickle.load(open('data/tweets','rb'))
    tags = pickle.load(open('data/tags','rb'))
    urls = pickle.load(open('data/urls','rb'))
    dfTweets = pd.DataFrame(tweets.items(), columns=['Date', 'DateValue'])
    dfTweets.to_csv('data/dateTweets.csv',index=False)
    dfTags = pd.DataFrame(tags)
    dfTags.index.names = ['Hashtags']
    dfTags = dfTags.fillna(0)
    dfTags['total'] = dfTags.sum(axis=1)
    dfTags = dfTags.sort_values(by='total',ascending=False)
    dfTags.to_csv('data/dateTags.csv')
    dfUrls = pd.DataFrame(urls)
    dfUrls.index.names = ['Urls']
    dfUrls = dfUrls.fillna(0)
    dfUrls['total'] = dfUrls.sum(axis=1)
    dfUrls = dfUrls.sort_values(by='total',ascending=False)
    dfUrls.to_csv('data/dateUrls.csv')


def update_results():
    tweets = pd.read_csv('data/dateTags.csv')
    tags = pd.read_csv('data/dateTags.csv')
    urls = pd.read_csv('data/dateUrls.csv')
    dates =  (tags.columns)
    last_date = dates[-2]
    today =  datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    start =  (datetime.datetime.strptime(last_date, "%Y-%m-%d").date())
    start = datetime.datetime.combine(start, datetime.time.min)
    tweets = pickle.load(open('data/tweets','rb'))
    tags = pickle.load(open('data/tags','rb'))
    urls = pickle.load(open('data/urls','rb'))
    iterator = coll.find({'created_at':{'$gt': start, '$lt':today}})
    for i in iterator:
        if i['created_at'].date() in tweets:
            tweets[i['created_at'].date()]+=1
        else:
            tweets[i['created_at'].date()]=1
        if 'entities' in i:
            if 'hashtags' in i['entities']:
                for h in i['entities']['hashtags']:
                    if i['created_at'].date() in tags:
                        if h['text'] in tags[i['created_at'].date()]:
                            tags[i['created_at'].date()][h['text']]+=1
                        else:
                            tags[i['created_at'].date()][h['text']]=1
                    else:
                        tags[i['created_at'].date()]={h['text']:1}
            if 'urls' in i['entities']:
                for h in i['entities']['urls']:
                    if i['created_at'].date() in urls:
                        if h['expanded_url'] in urls[i['created_at'].date()]:
                            urls[i['created_at'].date()][h['expanded_url']]+=1
                        else:
                            urls[i['created_at'].date()][h['expanded_url']]=1
                    else:
                        urls[i['created_at'].date()]={h['expanded_url']:1}
    pickle.dump(tweets,open('data/tweets','wb'))
    pickle.dump(tags,open('data/tags','wb'))
    pickle.dump(urls,open('data/urls','wb'))

def get_link_titles_to_csv():
    df = pd.read_csv('data/dateUrls.csv')
    df=df[:10]
    df=df[['Urls','total']]
    linkTitles = []
    for i in df['Urls']:
        title = get_page_title(i)
        if title!='error':
            linkTitles.append(title)
    df['title']=linkTitles
    df.to_csv('data/links_total.csv',index=False)

if twitter_init == 1:
    # Run once
    print("Initializing on " + time.strftime("%Y-%m-%d %H:%M"))
    get_tags_per_day_csv()
    get_tweets_per_day_csv()
    get_urls_per_day_csv()
    convert_to_csv()
    print("Done initializing on " + time.strftime("%Y-%m-%d %H:%M"))
else:
    # Run daily
    print("Updating on " + time.strftime("%Y-%m-%d %H:%M"))
    update_results()
    convert_to_csv()
    get_link_titles_to_csv()
    print("Update finished on " + time.strftime("%Y-%m-%d %H:%M"))

