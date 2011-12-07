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

def Evaluate():
    pass

if __name__ == '__main__':
    if len(sys.argv)<4:
        print "syntax: " + sys.argv[0] + "<a_wait_period_file> <target_files> <stable_period file>"
    else:
        wait_period_fn = sys.argv[1]
        news_fns = sys.argv[2:len(sys.argv)-1]
        future_fn = sys.argv[len(sys.argv)-1]
        print "Loading the wait period file: " + wait_period_fn        
        print "Loading target period file(s): " + str(news_fns)
        print "Loading the future period file: " + future_fn
        