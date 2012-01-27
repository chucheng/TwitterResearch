"""
This module parses the data in the tweet files and outputs them in a fashion
more useful for repeated analysis.

__author__ = 'Chris Moghbel (cmoghbel@cs.ucla.edu)'
"""
import URLUtil
import FileLog
import os

from datetime import datetime
from datetime import timedelta

_TWEETFILE_TWEET_ID_INDEX = 0
_TWEETFILE_USER_ID_INDEX = 1
_TWEETFILE_TWEET_TEXT_INDEX = 2
_TWEETFILE_CREATED_AT_INDEX = 3
_TWEETFILE_RETWEETED_INDEX = 4
_TWEETFILE_RETWEET_COUNT_INDEX = 5
_TWEETFILE_ORIGIN_USER_ID_INDEX = 6
_TWEETFILE_ORIGIN_TWEET_ID_INDEX = 7
_TWEETFILE_SOURCE_INDEX = 8
_TWEETFILE_FILTER_WORDS_INDEX = 9
_TWEETFILE_INSERT_TIMESTAMP_INDEX = 10

_DATA_DIR = '/dfs/birch/tsv'
_CACHE_FILENAME = '/dfs/birch/tsv/URLExapnd.cache.txt'
_YEAR = '2011'
_LOG_FILE = 'DataUtils.log'
_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

_TRAINING_SET_MONTHS = ['08', '09']
_TESTING_SET_MONTHS = ['10', '11']
_FULL_SET_MONTHS = ['08', '09', '10', '11', '12']


def find_delta_times(months, seeds, cache):
  """Finds the delta times for every url.
  
  Looks at every url, and calculates the time delta from previously calculated
  seed times.
  
  Keyword Arguments:
  months -- The months over which to look at urls.
  seeds -- A set of seed times, given as a dictionary of url to timedelta.
  cache -- Dictionary mapping short-url to long-url.
  
  Return:
  sorted_deltas -- A list of (tweet_id, (user_id, time_delta, url)) pairs
  sorted in increasing order.
  """
  time_deltas = {}
  for month in months:
    log('Finding delta times from %s/%s' %(month, _YEAR))
    dir_name = get_data_dir_name_for(month) 
    for filename in os.listdir(dir_name):
      if '.tweet' in filename and 'http_nyti_ms' in filename:
        data_file = '%s/%s' % (dir_name, filename)
        with open(data_file) as input_file:
          for line in input_file:
            tokens = line.split('\t')
            user_id = tokens[_TWEETFILE_USER_ID_INDEX]
            tweet_id = tokens[_TWEETFILE_TWEET_ID_INDEX]
            tweet_text = tokens[_TWEETFILE_TWEET_TEXT_INDEX]
            urls = URLUtil.parse_urls(tweet_text, cache)
            for url in urls:
              seed_tweet_id, seed_user_id, seed_time = seeds[url]
              if tweet_id == seed_tweet_id:
                time_deltas[tweet_id] = (user_id, 0, url)
              else:
                created = datetime.strptime(tokens[_TWEETFILE_CREATED_AT_INDEX],
                                            _DATETIME_FORMAT)
                time_delta = created - seed_time
                # Convert time delta to seconds to make it easy to read from
                # file later.
                time_delta_in_seconds = (time_delta.days * 86400
                                         + time_delta.seconds)
                time_deltas[tweet_id] = (user_id, time_delta_in_seconds, url)
  sorted_deltas = sorted(time_deltas.items(), key=lambda x: x[1][1],
                         reverse=False)
  with open('../data/FolkWisdom/time_deltas.tsv', 'w') as f:
    for (tweet_id, (user_id, time_delta, url)) in sorted_deltas:
      f.write('%s\t%s\t%s\t%s' % (tweet_id, user_id, time_delta, url))
  log('Wrote time deltas to disk')
  return sorted_deltas
  

def find_seed_times(months, cache):
  """Finds the time at which each url was seen.
  
  Keyword Arguments:
  months -- The months over which to look at urls.
  cache -- Dictionary mapping short-url to long-url.
  
  Returns:
  seed_time -- Dictionary of url to datetime object.
  """
  seed_times = {}
  for month in months:
    log('Finding seed times from %s/%s' %(month, _YEAR))
    dir_name = get_data_dir_name_for(month) 
    for filename in os.listdir(dir_name):
      if '.tweet' in filename and 'http_nyti_ms' in filename:
        data_file = '%s/%s' % (dir_name, filename)
        with open(data_file) as f:
          for line in f:
            tokens = line.split('\t')
            user_id = tokens[_TWEETFILE_USER_ID_INDEX]
            tweet_id = tokens[_TWEETFILE_TWEET_ID_INDEX]
            seed_time = datetime.strptime(tokens[_TWEETFILE_CREATED_AT_INDEX],
                                          _DATETIME_FORMAT)
            tweet_text = tokens[_TWEETFILE_TWEET_TEXT_INDEX]
            urls = URLUtil.parse_urls(tweet_text, cache)
            for url in urls:
              if not url in seed_times:
                seed_times[url] = (tweet_id, user_id, seed_time)
              else:
                (_, _, previous_seed_time) = seed_times[url]
                if seed_time < previous_seed_time:
                  seed_times[url] = (tweet_id, user_id, seed_time) 
  with open('../data/FolkWisdom/seed_times.tsv', 'w') as f:
    for url, (tweet_id, user_id, seed_time) in seed_times.items():
      f.write('%s\t%s\t%s\t%s' %(tweet_id, user_id, seed_time, url))
  log('Wrote seed times to disk')
  return seed_times


def get_data_dir_name_for(month):
  """Returns the data directory name for the given month."""
  return '%s/%s_%s' % (_DATA_DIR, _YEAR, month)


def sort_users_by_tweet_count(months):
  """Sorts users by their tweet activity.
  
  Keyword Arguments:
  months -- The months for which to sort the users on.
  
  Returns:
  user_id_sorted_by_tweet_count -- A list of (user id, count) pairs, in sorted
  order by count.
  """
  user_id_to_tweet_count = {}
  for month in months:
    log('Gathering count information for users from %s/%s' % (month, _YEAR))
    dir_name = '%s/%s_%s' %(_DATA_DIR, _YEAR, month)
    for filename in os.listdir(dir_name):
      if '.tweet' in filename and 'http_nyti_ms' in filename:
        data_file = '%s/%s' % (dir_name, filename)
        with open(data_file) as f:
          for line in f:
            tokens = line.split('\t')
            user_id = tokens[_TWEETFILE_USER_ID_INDEX]
            if user_id_to_tweet_count.has_key(user_id):
              user_id_to_tweet_count[user_id] += 1
            else:
              user_id_to_tweet_count[user_id] = 1
                
  user_ids_sorted_by_tweet_count = sorted(user_id_to_tweet_count.items(),
                                          key=lambda x: x[1], reverse=True)
  
  log("Size of users (total): " + str(len(user_id_to_tweet_count.keys())))
  with open('../data/FolkWisdom/user_activity.tsv', 'w') as f:
    for user_id, count in user_ids_sorted_by_tweet_count:
      f.write('%s\t%s\n' % (user_id, count))
  log('Wrote users (sorted by activity) to disk') 
  return user_ids_sorted_by_tweet_count


def load_cache():
  """Loads a mapping of short urls to long urls.
  
  Returns:
  cache -- A dictionary mapping short urls to long urls.
  """
  log('Loading cache...')
  cache = {}
  with open(_CACHE_FILENAME) as f:
    for line in f:
      tokens = line.split('\t')
      short_url = tokens[0]
      long_url = tokens[1]
      cache[short_url] = long_url
  return cache


def log(message):
  """Helper method to modularize the format of log messages.
    
    Keyword Arguments:
    message -- A string to print.
  """  
  FileLog.log(_LOG_FILE, message)


def run():
  cache = load_cache()
  user_ids_sorted = sort_users_by_tweet_count(_FULL_SET_MONTHS)
  seeds = find_seed_times(_FULL_SET_MONTHS, cache)
  time_deltas = find_delta_times(_FULL_SET_MONTHS, seeds, cache)


if __name__ == "__main__":
    run()
