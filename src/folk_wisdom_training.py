"""
This module does some analysis on the training sets, and outputs relevant
date for later use.

__author__ = 'Chris Moghbel (cmoghbel@cs.ucla.edu)'
"""
import Util
import URLUtil
import FileLog
import ground_truths
from ground_truths import DataSet

import os
from datetime import datetime
from datetime import timedelta

from constants import _TWEETFILE_USER_ID_INDEX
from constants import _TWEETFILE_CREATED_AT_INDEX
from constants import _TWEETFILE_TWEET_TEXT_INDEX
from constants import _DATETIME_FORMAT

from params import _DELTAS
from params import _CATEGORIES
from params import _SIZE_TOP_NEWS
from params import _TRAINING_SET_MONTHS
from params import _TESTING_SET_MONTHS
from params import _EXCLUDE_RETWEETS
from params import _EXCLUDE_TWEETS_WITHIN_DELTA
from params import _SWITCHED

_LOG_FILE = 'folk_wisdom_training.log'
_OUT_DIR = '../data/FolkWisdom/'


def find_hits_and_mises(months, target_news, seeds, cache, delta,
                        category=None):
  """Finds the hit and miss count for each user.

  Keyword Arguments:
  months -- The months over which to calculate hit and misses.
  target_news -- A set of urls that is the set of known target news.
  cache -- A dictionary of short url to long url.
  category -- The category to find hits and misses for, None for all news.
  """
  hits_and_misses = {}
  for month in months:
    log('Finding hits and misses for users from %s for delta %s and category %s'
        % (month, delta, category))
    dir_name = Util.get_data_dir_name_for(month)
    for filename in os.listdir(dir_name):
      if '.tweet' in filename and 'http_nyti_ms' in filename:
        data_file = '%s/%s' % (dir_name, filename)
        with open(data_file) as input_file:
          for line in input_file:
            tokens = line.split('\t')
            user_id = tokens[_TWEETFILE_USER_ID_INDEX]
            tweet_text = tokens[_TWEETFILE_TWEET_TEXT_INDEX]
            urls = URLUtil.parse_urls(tweet_text, cache)
            for url in urls:
              _, _, seed_time = seeds[url]
              created = datetime.strptime(tokens[_TWEETFILE_CREATED_AT_INDEX],
                                          _DATETIME_FORMAT)
              time_delta = created - seed_time
              if time_delta < timedelta(hours=delta):
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

  output_file = (_OUT_DIR + 'user_hits_and_misses_%s_%s.tsv'
                 % (delta, category))
  with open(output_file, 'w') as out_file:
    for user_id, (hits, misses) in hits_and_misses.items():
      out_file.write('%s\t%s\t%s\n' % (user_id, hits, misses))
  log('Wrote hits and misses to disk.')


def sort_users_by_tweet_count(months, seeds, cache, delta, category=None):
  """Sorts users by their tweet activity.
  
  Keyword Arguments:
  months -- The months for which to sort the users on.
  cache -- Dictionary of short url to long url.
  category -- The category to go by, None for all news.
  """
  user_id_to_tweet_count = {}
  for month in months:
    log('Gathering count information for users from %s for delta %s '
        'and category %s' % (month, delta, category))
    dir_name = Util.get_data_dir_name_for(month)
    for filename in os.listdir(dir_name):
      if '.tweet' in filename and 'http_nyti_ms' in filename:
        data_file = '%s/%s' % (dir_name, filename)
        with open(data_file) as input_file:
          for line in input_file:
            tokens = line.split('\t')
            user_id = tokens[_TWEETFILE_USER_ID_INDEX]
            tweet_text = tokens[_TWEETFILE_TWEET_TEXT_INDEX]
            urls = URLUtil.parse_urls(tweet_text, cache)
            for url in urls:
              _, _, seed_time = seeds[url]
              created = datetime.strptime(tokens[_TWEETFILE_CREATED_AT_INDEX],
                                          _DATETIME_FORMAT)
              time_delta = created - seed_time
              if time_delta < timedelta(hours=delta):
                if category:
                  url_category = URLUtil.extract_category(url)
                  if url_category == category:
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

  output_file = _OUT_DIR + 'user_activity_%s_%s.tsv' % (delta, category)
  with open(output_file, 'w') as out_file:
    for user_id, count in user_ids_sorted_by_tweet_count:
      out_file.write('%s\t%s\n' % (user_id, count))
  log('Wrote users (sorted by activity) to disk') 


def run():
  """Main logic. Outputs data in format for further analysis."""
  global _OUT_DIR
  cache = Util.load_cache()
  seeds = Util.load_seeds()

  # Set up params appropriately.
  data_set = DataSet.TRAINING
  months = _TRAINING_SET_MONTHS
  if _SWITCHED:
    data_set = DataSet.TESTING
    months = _TESTING_SET_MONTHS
    _OUT_DIR += 'switched/'
  retweets = set()
  if _EXCLUDE_RETWEETS:
    retweets = ground_truths.find_retweets(months)
    _OUT_DIR += 'no_retweets/'

  Util.ensure_dir_exist(_OUT_DIR)
  log('Output dir: %s' % _OUT_DIR)

  for delta in _DELTAS:
    for category in _CATEGORIES:
      gt_rankings = ground_truths.get_gt_rankings(seeds, data_set, category,
                                                  exclude_tweets_within_delta=_EXCLUDE_TWEETS_WITHIN_DELTA,
                                                  retweets=retweets)
      sort_users_by_tweet_count(months, seeds, cache, delta, category)
      target_news = ground_truths.find_target_news(gt_rankings, _SIZE_TOP_NEWS)
      find_hits_and_mises(months, target_news, seeds, cache,
                          delta, category)
#      if _SWITCHED:
#        gt_rankings = ground_truths.get_gt_rankings(seeds, DataSet.TESTING,
#                                                    category)
#        sort_users_by_tweet_count(_TESTING_SET_MONTHS, seeds, cache,
#                                  delta, category)
#        target_news = ground_truths.find_target_news(gt_rankings, .02)
#        find_hits_and_mises(_TESTING_SET_MONTHS, target_news, seeds, cache,
#                            delta, category)
#      else:
#        gt_rankings = ground_truths.get_gt_rankings(seeds, DataSet.TRAINING,
#                                                    category)
#        sort_users_by_tweet_count(_TRAINING_SET_MONTHS, seeds, cache,
#                                  delta, category)
#        target_news = ground_truths.find_target_news(gt_rankings, .02)
#        find_hits_and_mises(_TRAINING_SET_MONTHS, target_news, seeds, cache,
#                            delta, category)

  log('Finished outputting data!')


def log(message):
  """Helper method to modularize the format of log messages.
    
    Keyword Arguments:
    message -- A string to print.
  """  
  FileLog.log(_LOG_FILE, message)


if __name__ == "__main__":
  run()
