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

_TIMEDELTAS_FILE_TWEET_ID_INDEX = 0
_TIMEDELTAS_FILE_USER_ID_INDEX = 1 
_TIMEDELTAS_FILE_DELTA_INDEX = 2
_TIMEDELTAS_FILE_URL_INDEX = 3

_DATA_DIR = '/dfs/birch/tsv'
_CACHE_FILENAME = '/dfs/birch/tsv/URLExapnd.cache.txt'
_YEAR = '2011'
_LOG_FILE = 'DataUtils.log'
_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

_TRAINING_SET_MONTHS = ['09', '10']
_TESTING_SET_MONTHS = ['11']
_FULL_SET_MONTHS = ['08', '09', '10', '11', '12']

_CATEGORIES = ['technology', 'sports', 'business']


def get_gt_rankings(seeds, category=None):
  """Generate the ground truth rankings.
  
  Returns:
    gt_rankings -- A list of (url, count) pairs in ranked order.
  """
  gt_tweet_counts = {}
  with open('../data/FolkWisdom/time_deltas.tsv') as f:
    for line in f:
      tokens = line.split('\t')
      url = tokens[_TIMEDELTAS_FILE_URL_INDEX]
      if url in seeds:
        seed_tweet_id, seed_user_id, seed_time = seeds[url]
        if (seed_time >= datetime(year=2011, month=9, day=1)
            and seed_time < datetime(year=2011, month=11, day=1)):
          category_matches = True
          if category:
            category_matches = False
            url_category = URLUtil.extract_category(url)
            if url_category == category:
              category_matches = True
          if category_matches:
            if url in gt_tweet_counts:
              gt_tweet_counts[url] += 1
            else:
              gt_tweet_counts[url] = 1

  gt_rankings = sorted(gt_tweet_counts.items(), key=lambda x: x[1],
                       reverse=True)
  return gt_rankings


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
              category = URLUtil.extract_category(url)
              if tweet_id == seed_tweet_id:
                time_deltas[tweet_id] = (user_id, 0, url, category)
              else:
                created = datetime.strptime(tokens[_TWEETFILE_CREATED_AT_INDEX],
                                            _DATETIME_FORMAT)
                time_delta = created - seed_time
                # Convert time delta to seconds to make it easy to read from
                # file later.
                time_delta_in_seconds = (time_delta.days * 86400
                                         + time_delta.seconds)
                time_deltas[tweet_id] = (user_id, time_delta_in_seconds, url,
                                         category)
  sorted_deltas = sorted(time_deltas.items(), key=lambda x: x[1][1],
                         reverse=False)
  with open('../data/FolkWisdom/time_deltas.tsv', 'w') as f:
    for (tweet_id, (user_id, time_delta, url, category)) in sorted_deltas:
      f.write('%s\t%s\t%s\t%s\t%s\n' % (tweet_id, user_id, time_delta, url,
                                      category))
  log('Wrote time deltas to disk')
  

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


def find_hits_and_mises(months, target_news, cache, category=None):
  """Finds the hit and miss count for each user.

  Keyword Arguments:
  months -- The months over which to calculate hit and misses.
  seeds -- The seed times, or first occurances of each url.
  target_news -- A set of urls that is the set of known target news.
  delta -- The number of hours of the time windows.
  cache -- A dictionary of short url to long url.

  Returns:
  hits_and_misses -- A dictionary of user id to (hits, misses) pairs.
  """
  hits_and_misses = {}
  for month in months:
    log('Finding hits and misses for users from %s/%s for category %s'
        % (month, _YEAR, category))
    dir_name = '%s/%s_%s' %(_DATA_DIR, _YEAR, month)
    for filename in os.listdir(dir_name):
      if '.tweet' in filename and 'http_nyti_ms' in filename:
        data_file = '%s/%s' % (dir_name, filename)
        with open(data_file) as f:
          for line in f:
            tokens = line.split('\t')
            user_id = tokens[_TWEETFILE_USER_ID_INDEX]
            tweet_text= tokens[_TWEETFILE_TWEET_TEXT_INDEX]
            urls = URLUtil.parse_urls(tweet_text, cache)
            for url in urls:
              category_matches = True
              if category:
                category_matches = False
                url_category = URLUtil.extract_category(url)
                if category == url_category:
                  category_matches = True
              if url in target_news and category_matches:
                if user_id in hits_and_misses:
                  (user_hits, user_misses) = hits_and_misses[user_id]
                  hits_and_misses[user_id] = (user_hits + 1, user_misses)
                else:
                  hits_and_misses[user_id] = (1, 0)
              elif category_matches:
                if user_id in hits_and_misses:
                  (user_hits, user_misses) = hits_and_misses[user_id]
                  hits_and_misses[user_id] = (user_hits, user_misses + 1)
                else:
                  hits_and_misses[user_id] = (0, 1)

  output_file = '../data/FolkWisdom/user_hits_and_misses'
  if category:
    output_file += '_%s.tsv' % category
  else:
    output_file = '.tsv'
  with open(output_file, 'w') as f:
    for user_id, (hits, misses) in hits_and_misses.items():
      f.write('%s\t%s\t%s\n' % (user_id, hits, misses))
  log('Wrote hits and misses to disk.')


def sort_users_by_tweet_count(months, cache=None, category=None):
  """Sorts users by their tweet activity.
  
  Keyword Arguments:
  months -- The months for which to sort the users on.
  
  Returns:
  user_id_sorted_by_tweet_count -- A list of (user id, count) pairs, in sorted
  order by count.
  """
  user_id_to_tweet_count = {}
  for month in months:
    log('Gathering count information for users from %s/%s for category %s'
        % (month, _YEAR, category))
    dir_name = '%s/%s_%s' %(_DATA_DIR, _YEAR, month)
    for filename in os.listdir(dir_name):
      if '.tweet' in filename and 'http_nyti_ms' in filename:
        data_file = '%s/%s' % (dir_name, filename)
        with open(data_file) as f:
          for line in f:
            tokens = line.split('\t')
            user_id = tokens[_TWEETFILE_USER_ID_INDEX]
            if category:
              tweet_text = tokens[_TWEETFILE_TWEET_TEXT_INDEX]
              urls = URLUtil.parse_urls(tweet_text, cache)
              correct_category = False
              for url in urls:
                url_category = URLUtil.extract_category(url)
                if url_category == category:
                  correct_category = True
              if correct_category:
                if user_id_to_tweet_count.has_key(user_id):
                  user_id_to_tweet_count[user_id] += 1
                else:
                  user_id_to_tweet_count[user_id] = 1
            else:
              if user_id_to_tweet_count.has_key(user_id):
                user_id_to_tweet_count[user_id] += 1
              else:
                user_id_to_tweet_count[user_id] = 1
                
  user_ids_sorted_by_tweet_count = sorted(user_id_to_tweet_count.items(),
                                          key=lambda x: x[1], reverse=True)
  
  log("Size of users for category %s (total): %s"
      % (str(len(user_id_to_tweet_count.keys())), category))

  output_file = '../data/FolkWisdom/user_activity'
  if category:
    output_file += '_%s.tsv' % category
  else:
    output_file += '.tsv'
  with open(output_file, 'w') as f:
    for user_id, count in user_ids_sorted_by_tweet_count:
      f.write('%s\t%s\n' % (user_id, count))
  log('Wrote users (sorted by activity) to disk') 


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


def find_target_news(seeds, category=None):
  gt_rankings = get_gt_rankings(seeds, category)
  num_news = int(len(gt_rankings) * .02)
  target_news = set()
  for i in range(0, num_news):
    url, count = gt_rankings[i]
    target_news.add(url)
  return target_news


def run():
  cache = load_cache()
  sort_users_by_tweet_count(_TRAINING_SET_MONTHS)
  for category in _CATEGORIES:
    sort_users_by_tweet_count(_TRAINING_SET_MONTHS, cache,
                                                category)
  seeds = find_seed_times(_FULL_SET_MONTHS, cache)
  find_delta_times(_FULL_SET_MONTHS, seeds, cache)
  target_news = find_target_news(seeds)
  find_hits_and_mises(_TRAINING_SET_MONTHS, target_news, cache)
  for category in _CATEGORIES:
    target_news = find_target_news(seeds, category)
    find_hits_and_mises(_TRAINING_SET_MONTHS, target_news, cache, category)
  log('Finished outputting data!')


if __name__ == "__main__":
    run()
