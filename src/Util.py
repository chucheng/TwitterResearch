"""Util.py contains only function that can be reused many times"""
import Configuration
import pickle
import os
import sys
import smtplib
import datetime
from email.mime.text import MIMEText
from datetime import datetime

import FileLog

from constants import _DATA_DIR
from constants import _DATETIME_FORMAT
from constants import _CACHE_FILENAME


_LOG_FILE = 'Util.log'


def get_graph_output_dir(output_dir):
  """Assign an output path for the graph(s)."""
  cfg = Configuration.getConfig()
  graph_dir = cfg.get('Path', 'base-dir') + cfg.get('Path', 'graph-dir')
  graph_dir += output_dir
  ensure_dir_exist(graph_dir)
  return graph_dir


def get_data_dir_name_for(month):
  """Returns the data directory name for the given month."""
  year = '2011'
  if month == '01':
    year = '2012'
  return '%s/%s_%s' % (_DATA_DIR, year, month)


def load_cache():
  """Loads a mapping of short urls to long urls.
  
  Returns:
  cache -- A dictionary mapping short urls to long urls.
  """
  log('Loading cache...')
  cache = {}
  with open(_CACHE_FILENAME) as input_file:
    for line in input_file:
      tokens = line.split('\t')
      short_url = tokens[0]
      long_url = tokens[1]
      cache[short_url] = long_url
  return cache


def load_seeds():
  """Loads the set of seed times for urls from file."""
  log('Loading seeds.')
  seeds = {}
  with open('../data/FolkWisdom/seed_times.tsv') as input_file:
    for line in input_file:
      tokens = line.split('\t')
      seed_tweet_id = tokens[0]
      seed_user_id = tokens[1]
      seed_time = datetime.strptime(tokens[2], _DATETIME_FORMAT)
      url = tokens[3].strip()
      seeds[url] = (seed_tweet_id, seed_user_id, seed_time)
  return seeds


def load_pickle(input_pickle_filename):
    """Load a pickle and return"""
    inputfile = open(input_pickle_filename, 'r')
    data = pickle.load(inputfile)
    inputfile.close()
    return data

def dump_pickle(data, output_pickle_filename):
    """Dump an ojbect to a file"""
    ensure_dir_exist(output_pickle_filename)
    with open(output_pickle_filename, 'w') as outputfile:
        pickle.dump(data, outputfile)    

def ensure_dir_exist(full_path_name):
    """ Given a full path filename, make sure the dir it locates exists

    Example: ensure_dir_exist("../data/test/")
    """        
    d = os.path.dirname(full_path_name)
    if d and not os.path.exists(d):
        os.makedirs(d)
        
def time_delta_to_hours(timedetla_obj):
    '''Return the total number of hours given a time gap
    '''
    return timedetla_obj.days * 24 + timedetla_obj.seconds / (60.0*60) 

def email(subject, message):
    '''Send an email notification.    
    '''
    try:
            msg = MIMEText(message)
            me = 'twitter.news.project@gmail.com'
            you = "chucheng@gmail.com"
            cc_addresses = ['sjtufjh@gmail.com']
            
            msg['Subject'] = str(subject)
            msg['From'] = me
            msg['To'] = you
            msg['Cc'] = ', '.join(cc_addresses)
            
            
            # Send the message via our own SMTP server, but don't include the
            # envelope header.
            usename = 'twitter.news.project'
            password = 'trend@tweet'
            s = smtplib.SMTP('smtp.gmail.com:587')
            s.starttls()
            s.login(usename, password)    
            s.sendmail(me, you, msg.as_string())
            s.quit()
            print "end email successfully"
    except:
            s.quit()
            print "send email fail"
            

def load_time_stamp(state_filename, log=None):
    """Return a datetime object (time stamp) from reading the state file.
    
    Return None if something wrong.
    """
    try:
        file = open(state_filename,'r')
        timestamp = file.readline()
        file.close()
        time_format = "%Y-%m-%d %H:%M:%S"
        #you will see a ValueError if time data does not match the format.
        return datetime.datetime.strptime(timestamp, time_format)
    except Exception as e:
        if log:
            log("Error (load_time_stamp): " + str(e), sys.exc_traceback)
        else:
            print "Error (load_time_stamp): " + str(e)
        return None

def gen_log_sequence(max_number):
    """12 --> [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20]"""
    max_digit = len(str(max_number))
    num_list = []
    for p in range(0, max_digit):
        base = 10**p
        for i in range(1, 10):
            num = base * i
            num_list.append(num)
            if num > max_number:
                break
    return num_list
        
        
def log(message):
  """Helper method to modularize the format of log messages.
    
    Keyword Arguments:
    message -- A string to print.
  """  
  FileLog.log(_LOG_FILE, message)
