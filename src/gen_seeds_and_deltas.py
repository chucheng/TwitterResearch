"""
This module parses the tweet files and generates two output files:

1. Seed file (data/FolkWisdom/seed_times.tsv) -- This file maps url
   to it's seed time, or first time seen.
2. Deltas file (data/FolkWisdom/time_deltas.tsv) -- The file maps a tweet
   to the amount of seconds it happened after it's seed time.

__author__ = 'Chris Moghbel (cmoghbel@cs.ucla.edu)
"""
import FileLog
import Util
import URLUtil

from constants import _TWEETFILE_USER_ID_INDEX
from constants import _TWEETFILE_TWEET_ID_INDEX
from constants import _TWEETFILE_CREATED_AT_INDEX
from constants import _TWEETFILE_TWEET_TEXT_INDEX
from constants import _DATETIME_FORMAT
from constants import _TRAINING_SET_MONTHS
from constants import _FULL_SET_MONTHS

import os
from datetime import datetime

_LOG_FILE = 'gen_seeds_and_deltas.log'
_REGENERATE_SEEDS = True


def find_delta_times(months, seeds, cache):
  """Finds the delta times for every url.
  
  Looks at every url, and calculates the time delta from previously calculated
  seed times.
  
  Keyword Arguments:
  months -- The months over which to look at urls.
  seeds -- A set of seed times, given as a dictionary of url to timedelta.
  cache -- Dictionary mapping short-url to long-url.
  """
  time_deltas = {}
  for month in months:
    log('Finding delta times from %s' % month)
    dir_name = Util.get_data_dir_name_for(month) 
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
              seed_tweet_id, _, seed_time = seeds[url]
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
  with open('../data/FolkWisdom/time_deltas.tsv', 'w') as output_file:
    for (tweet_id, (user_id, time_delta, url, category)) in sorted_deltas:
      output_file.write('%s\t%s\t%s\t%s\t%s\n' % (tweet_id, user_id, time_delta,
                                                  url, category))
  log('Wrote time deltas to disk')


def find_seed_times(months, cache):
  """Finds the time at which each url was seen.
  
  Keyword Arguments:
  months -- The months over which to look at urls.
  cache -- Dictionary mapping short-url to long-url.
  """
  seed_times = {}
  for month in months:
    log('Finding seed times from %s' % month)
    dir_name = Util.get_data_dir_name_for(month) 
    for filename in os.listdir(dir_name):
      if '.tweet' in filename and 'http_nyti_ms' in filename:
        data_file = '%s/%s' % (dir_name, filename)
        with open(data_file) as input_file:
          for line in input_file:
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
  with open('../data/FolkWisdom/seed_times.tsv', 'w') as output_file:
    for url, (tweet_id, user_id, seed_time) in seed_times.items():
      output_file.write('%s\t%s\t%s\t%s\n' %(tweet_id, user_id, seed_time, url))
  log('Wrote seed times to disk')


def find_size_of_market(months):
  """Outputs the size of the market (total number of users) for reference.

  Keyword Arguments:
  months -- The months to consider.
  """
  user_ids = set()
  for month in months:
    log('Finding size of unfiltered market...')
    dir_name = Util.get_data_dir_name_for(month)
    for filename in os.listdir(dir_name):
      if '.tweet' in filename and 'http_nyti_ms' in filename:
        data_file = '%s/%s' % (dir_name, filename)
        with open(data_file) as input_file:
          for line in input_file:
            tokens = line.split('\t')
            user_id = tokens[_TWEETFILE_USER_ID_INDEX]
            if not user_id in user_ids:
              user_ids.add(user_id)

  with open('../data/FolkWisdom/size_of_market_unfiltered.txt', 'w') as out_f:
    out_f.write('%s' % len(user_ids))


def run():
  """Main logic for this analysis."""
  cache = Util.load_cache()

  if _REGENERATE_SEEDS:
    find_seed_times(_FULL_SET_MONTHS, cache)
  
  seeds = Util.load_seeds()

  find_delta_times(_FULL_SET_MONTHS, seeds, cache)
  find_size_of_market(_TRAINING_SET_MONTHS)


def log(message):
  """Helper method to modularize the format of log messages.
    
    Keyword Arguments:
    message -- A string to print.
  """  
  FileLog.log(_LOG_FILE, message)


if __name__ == "__main__":
  run()
