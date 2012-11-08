"""
Handles operations involving finding ground truths and top news sets.

__author__ = 'Chris Moghbel (cmoghbel@cs.ucla.edu)
"""
import os
import Util
import URLUtil

from constants import _TWEETFILE_TWEET_ID_INDEX
from constants import _TWEETFILE_RETWEETED_INDEX
from constants import _TIMEDELTAS_FILE_URL_INDEX
from constants import _TIMEDELTAS_FILE_SOURCE_INDEX
from constants import _TIMEDELTAS_FILE_DELTA_INDEX
from constants import _TIMEDELTAS_FILE_TWEET_ID_INDEX


def find_retweets(months):
  retweets = set()
  for month in months:
    print 'Finding retweets from %s'
    dir_name = Util.get_data_dir_name_for(month) 
    for filename in os.listdir(dir_name):
      if '.tweet' in filename and 'http_nyti_ms' in filename:
        data_file = '%s/%s' % (dir_name, filename)
        with open(data_file) as input_file:
          for line in input_file:
            tokens = line.split('\t')
            retweet = bool(tokens[_TWEETFILE_RETWEETED_INDEX])
            if retweet:
              tweet_id = tokens[_TWEETFILE_TWEET_ID_INDEX]
              retweets.add(tweet_id)
  return retweets


def find_target_news(gt_rankings, size_top_news):
  """Find the target news, which is top 2% of ground truth.
  
  Keyword Arguments:
  seeds -- The first time each url was seen.
  category -- The category to generate target news for, None if for all news.

  Returns:
  target_news -- A set of target news for the given category.
  """
  num_news = int(len(gt_rankings) * size_top_news)
  target_news = set()
  for i in range(0, num_news):
    url, _ = gt_rankings[i]
    target_news.add(url)
  return target_news


def get_gt_rankings(seeds, dataset, category=None, delta=4,
                    exclude_tweets_within_delta=False, retweets=set()):
  """Generate the ground truth rankings.
  
  Keyword Arguments:
  seeds -- A dictionary of url to first time seen.
  training -- Boolean to indicate if we want training window. False specifies
              testing window.
  category -- The category to get gt's for, None for all news.

  Returns:
  gt_rankings -- A list of (url, count) pairs in ranked order.
  """
  gt_tweet_counts = {}
  with open('../data/FolkWisdom/time_deltas.tsv') as input_file:
    for line in input_file:
      tokens = line.split('\t')
      source = tokens[_TIMEDELTAS_FILE_SOURCE_INDEX].strip()
      url = tokens[_TIMEDELTAS_FILE_URL_INDEX]
      tweet_id = tokens[_TIMEDELTAS_FILE_TWEET_ID_INDEX]
      tweet_delta = float(tokens[_TIMEDELTAS_FILE_DELTA_INDEX]) / 3600
      include_tweet = True
      if exclude_tweets_within_delta:
        if tweet_delta > delta:
          include_tweet = False
      if url in seeds and include_tweet and not tweet_id in retweets:
        _, _, seed_time = seeds[url]
        is_in_window = False
        if dataset == DataSet.TRAINING:
          is_in_window = Util.is_in_training_set(seed_time)
        elif dataset == DataSet.TESTING:
          is_in_window = Util.is_in_testing_set(seed_time)
        else:
          is_in_window = True
        if is_in_window:
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

class DataSet:
  """Enum for data set values."""

  def __init__(self):
    """Do nothing."""
    pass

  ALL = 0
  TRAINING = 1
  TESTING = 2
