"""Evaluate the market precision at a given time limit.

This code is aim to answer the following question:
    How quickly can the market sense the breaking news?
    
Input: contains at least three file
    * The first file: news in this file should not be considered in the future 
                      analysis.
    * The last file:  news in this file are used for determing the "true" good 
                      news.
Ouput: ../graph/MarketPrecision/MarketPrecision.*                      
                      
                      
Every news is represented as a url
    

"""
from __future__ import with_statement
import matplotlib
matplotlib.use('Agg') #This resolve the issue to draw a graph remotely
import sys

from datetime import datetime, timedelta
from operator import itemgetter

def un_wanted_news_url(fns):    
    unwanted = set()
    for fn in fns:
        print "processing unwanted..." + fn
        f = open(fn)
        for line in f.readlines():
            (news_url, time) = line[:-1].split('\t')
            unwanted.add(news_url)
        f.close()
    return unwanted

def time_delta_in_secs(s_t1, s_t2, dt_format="%Y-%m-%d %H:%M:%S"):
    """Given two time string, if s_t1 is the base time, return diff in seconds.
    """
    dt_obj1 = datetime.strptime(s_t1, dt_format)
    dt_obj2 = datetime.strptime(s_t2, dt_format)
    t_diff = (dt_obj2 - dt_obj1).seconds
    return t_diff        

def update_news_rt_count(idx, news_rt_count, news_url):
    for i in range(idx, len(news_rt_count)):
        dict_news_count = news_rt_count[i]
        dict_news_count[news_url] = dict_news_count.get(news_url, 0) + 1
    


def Evaluate(wait_period_fns, news_fns, future_fns, max_hours_track=10):
    """
    News in the wait period files 
    """
    news_init_time = dict() # (news_url, first_time_you_see_it)
    news_seen = set()
    
    news_rt_count = list() # the 0 index is (url, dt_obj_first_seen)
    news_rt_count.append(news_init_time)
    
    news_final_count = dict() # the true count at the end of day
    
    for i in range(1, max_hours_track+1): #1-100
        news_rt_count.append(dict())    
    
    
    unwanted_news_set = un_wanted_news_url(wait_period_fns)
    
    for fn in news_fns + future_fns:
        print "processing" + fn
        future = False
        if fn in future_fns: 
            future = True
        
        f = open(fn)
        for line in f.readlines():
            (news_url, time) = line[:-1].split('\t')
            if news_url in unwanted_news_set:
                continue #skip because these are old news
            first_seen = news_url not in news_seen
            if(first_seen): 
                if future: #we don't add news_url in the future
                    unwanted_news_set.add(news_url)
                    continue
                else:
                    news_seen.add(news_url)
                    news_init_time[news_url] = time
                    update_news_rt_count(1, news_rt_count, news_url)
                    news_final_count[news_url] = 1
            else: #not first_seen
                news_final_count[news_url] = news_final_count[news_url] + 1
                hours_diff = time_delta_in_secs(news_init_time.get(news_url),
                                                time) / 60
                if(hours_diff + 1 > len(news_rt_count)):
                    continue #we don't store such data
                
                update_news_rt_count(hours_diff+1, #+1 because 0~1 we update 1 and after
                                     news_rt_count,
                                     news_url)
        
        f.close()
    return (news_rt_count, news_final_count)

def output(news_rt_count, news_final_count):
    output_prefix = "../tmp/MarketDecision"
    
    fn = "_init_time.txt"
    print "writing..." + output_prefix + fn
    f = open(output_prefix + fn, 'w')
    out_dict = news_rt_count[0]
    out_list = sorted(out_dict.items())
    for (k, v) in out_list:
        f.write(str(k) + '\t' + str(v) + '\n')
    f.close()
    
    for i in range(1, len(news_rt_count)):
        si = str(i)
        if(i<10): 
            si = '00' + si
        elif(i<100): 
            si = '0' + si
        else: 
            pass
        
        fn = "_" + si + "_hrs.txt"
        print "writing..." + output_prefix + fn
        f = open(output_prefix + fn, 'w')
        out_dict = news_rt_count[i]
        out_list = sorted(out_dict.items(), key=itemgetter(1), reverse=True)
        for (k, v) in out_list:
            f.write(str(k) + '\t' + str(v) + '\n')
        f.close()
        
    fn = "_true_count.txt"
    print "writing..." + output_prefix + fn
    f = open(output_prefix + fn, 'w')    
    out_dict = news_final_count
    out_list = sorted(out_dict.items(), key=itemgetter(1), reverse=True)
    for (k, v) in out_list:
        f.write(str(k) + '\t' + str(v) + '\n')
    f.close()
    
    
    
    

if __name__ == '__main__':
    if len(sys.argv)<4:
        print "syntax: " + sys.argv[0] + "<a_wait_period_file> <target_files> <stable_period file>"
    else:
        wait_period_fns = sys.argv[1:2]
        news_fns = sys.argv[2:len(sys.argv)-1]
        future_fns = sys.argv[len(sys.argv)-1:len(sys.argv)]
        print "Loading the wait period file: " + str(wait_period_fns)
        print "Loading target period file(s): " + str(news_fns)
        print "Loading the future period file: " + str(future_fns)
        (news_rt_count, news_final_count) = \
            Evaluate(wait_period_fns, news_fns, future_fns, max_hours_track=100)
        output(news_rt_count, news_final_count)
        