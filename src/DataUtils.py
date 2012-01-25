"""
This module parses the date in the tweet files and outputs them in a fashion
more useful for repeated analysis.

__author__ = 'Chris Moghbel (cmoghbel@cs.ucla.edu)'
"""
import URLUtil
import os

from datetime import datetime

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


def add_tweet_counts(months, tweet_counts, cache):
  """Adds tweet counts from a new month to an existing set of urls.
  
  Keyword_arguments:
  months -- The months to add counts from.
  tweet_counts -- An existing set of tweet counts to update.
  cache -- Dictionary mapping short urls to long urls.
  """
  for month in months:
    log('Adding tweets for exisiting news from %s/%s' %(month, _YEAR))
    dir_name = get_data_dir_name_for(month) 
    for filename in os.listdir(dir_name):
      if '.tweet' in filename and 'http_nyti_ms' in filename:
        data_file = '%s/%s' % (dir_name, filename)
        with open(data_file) as f:
          for line in f:
            tokens = line.split('\t')
            tweet_text = tokens[_TWEETFILE_TWEET_TEXT_INDEX]
            urls = URLUtil.parse_urls(tweet_text, cache)
            for url in urls:
              if url in tweet_counts:
                tweet_counts[url] += 1


def eliminate_news(months, tweet_counts, cache):
  """Removes news stories that started in an earlier month(s).
  
  Keyword Argument:
  months -- The months to remove stories for.
  tweet_counts -- The dictionary of url to tweet counts to update.
  cache -- Dictionary mapping short urls to long urls.
  """
  for month in months:
    log('Removing news stories seen in %s/%s' %(month, _YEAR))
    dir_name = get_data_dir_name_for(month) 
    for filename in os.listdir(dir_name):
      if '.tweet' in filename and 'http_nyti_ms' in filename:
        data_file = '%s/%s' % (dir_name, filename)
        with open(data_file) as f:
          for line in f:
            tokens = line.split('\t')
            tweet_text = tokens[_TWEETFILE_TWEET_TEXT_INDEX]
            urls = URLUtil.parse_urls(tweet_text, cache)
            for url in urls:
              if url in tweet_counts:
                del tweet_counts[url]


def gather_tweet_counts(months, cache, experts, active):
  """Gathers the tweet counts for a given set of months.
  
  Gathers counts both in total, and for a set of user groups.
  
  Keyword Arguments:
  months -- The months to gather tweet counts for.
  cache -- Dictionary mapping short urls to long urls.
  experts -- A set containing the user ids of 'expert' users.
  active -- A set containing the user ids of 'active' users.
  
  Returns:
  gt_tweet_counts -- Dictionary of url to tweet count for all users.
  expert_tweet_counts -- Dictionary of url to tweet count for expert users.
  active_tweet_counts -- Dictionary of url to tweet count for active users.
  common_tweet_counts -- Dictionary of url to tweet count for common users.
  """
  gt_tweet_counts = {}
  expert_tweet_counts = {}
  active_tweet_counts = {}
  common_tweet_counts = {}
  for month in months:
    log('Loading counts for %s/%s for user groups (expert, active, common)'
        %(month, _YEAR))
    dir_name = get_data_dir_name_for(month) 
    for filename in os.listdir(dir_name):
      if '.tweet' in filename and 'http_nyti_ms' in filename:
        data_file = '%s/%s' % (dir_name, filename)
        with open(data_file) as f:
          for line in f:
            tokens = line.split('\t')
            tweet_text = tokens[_TWEETFILE_TWEET_TEXT_INDEX]
            urls = URLUtil.parse_urls(tweet_text, cache)
            user_id = tokens[_TWEETFILE_USER_ID_INDEX]
            for url in urls:
              if url in gt_tweet_counts:
                gt_tweet_counts[url] += 1
              else:
                gt_tweet_counts[url] = 1

              if user_id in experts:
                if url in expert_tweet_counts:
                  expert_tweet_counts[url] += 1
                else:
                  expert_tweet_counts[url] = 1
              elif user_id in active:
                if url in active_tweet_counts:
                  active_tweet_counts[url] += 1
                else:
                  active_tweet_counts[url] = 1                
              else:
                if url in common_tweet_counts:
                  common_tweet_counts[url] += 1
                else:
                  common_tweet_counts[url] = 1                
                
  return (gt_tweet_counts, expert_tweet_counts, active_tweet_counts,
          common_tweet_counts)


def get_data_dir_name_for(month):
  """Returns the data directory name for the given month."""
  return '%s/%s_%s' % (_DATA_DIR, _YEAR, month)


def get_users_sorted_by_tweet_count(months):
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
                
  user_id_sorted_by_tweet_count = sorted(user_id_to_tweet_count.items(),
                                         key=lambda x: x[1], reverse=True)
  
  log("Size of users (total): " + str(len(user_id_to_tweet_count.keys())))
  return user_id_sorted_by_tweet_count


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
  print '[%s] %s' % (datetime.now(), message)
