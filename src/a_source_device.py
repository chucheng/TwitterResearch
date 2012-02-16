"""
This module is an analysis for finding the number of tweets from each source
device.

__author__ = 'Chris Moghbel (cmoghbel@cs.ucla.edu)'
"""
import FileLog
import Util

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
_LOG_FILE = 'a_source_device.log'
_OUTPUT_DIR = '../data/SourceDevice/'
_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
_FULL_SET_MONTHS = ['08', '09', '10', '11', '12', '01']


def find_device_counts():
  """Finds the number of tweets by each source device.

  Returns:
  Dictionary of source device string to pair of (count, percentage).
  e.g. {'Twitter for iPhone': (1100, 10.0) ...}
  """
  device_counts = {}
  all_count = 0
  device_counts_original = {}
  original_count = 0
  device_counts_retweets = {}
  retweet_count = 0
  for month in _FULL_SET_MONTHS:
    log('Finding device counts for month %s.' % month)
    dir_name = get_data_dir_name_for(month) 
    for filename in os.listdir(dir_name):
      if '.tweet' in filename and 'http_nyti_ms' in filename:
        data_file = '%s/%s' % (dir_name, filename)
        with open(data_file) as input_file:
          for line in input_file:
            tokens = line.split('\t')
            created = datetime.strptime(tokens[_TWEETFILE_CREATED_AT_INDEX],
                                        _DATETIME_FORMAT)
            if is_in_window(created):
              source_device = tokens[_TWEETFILE_SOURCE_INDEX]
              retweet = bool(int(tokens[_TWEETFILE_RETWEET_COUNT_INDEX]))
              all_count += 1
              if source_device in device_counts:
                device_counts[source_device] += 1
              else:
                device_counts[source_device] = 1
              if retweet:
                retweet_count += 1
                if source_device in device_counts_retweets:
                  device_counts_retweets[source_device] += 1
                else:
                  device_counts_retweets[source_device] = 1
              else:
                original_count += 1
                if source_device in device_counts_original:
                  device_counts_original[source_device] += 1
                else:
                  device_counts_original[source_device] = 1

  for device, count in device_counts_original.items():
    device_total = device_counts[device]
    device_counts_original[device] = (count,
                                      (float(count) / original_count) * 100,
                                      (float(count) / device_total) * 100)
  for device, count in device_counts_retweets.items():
    device_total = device_counts[device]
    device_counts_retweets[device] = (count,
                                      (float(count) / retweet_count) * 100,
                                      (float(count) / device_total) * 100)
  for device, count in device_counts.items():
    device_counts[device] = (count, (float(count) / all_count) * 100)

  return device_counts, device_counts_original, device_counts_retweets


def get_data_dir_name_for(month):
  """Returns the data directory name for the given month."""
  year = '2011'
  if month == '01':
    year = '2012'
  return '%s/%s_%s' % (_DATA_DIR, year, month)


def is_in_window(date_time):
  """Checks if the given datetime is within the desired window.

  Keyword Arguments:
  date_time -- The datetime object to take.
  
  Returns:
  True if within the window, False otherwise.
  """
  if (date_time > datetime(year=2011, month=9, day=1) and
      date_time < datetime(year=2012, month=1, day=1)):
    return True
  return False


def log(message):
  """Helper method to modularize the format of log messages.
  
  Keyword Arguments:
  message -- A string to log.
  """
  FileLog.log(_LOG_FILE, message)


def run():
  """Main logic for this analysis."""
  FileLog.set_log_dir()
  all_counts, original_counts, retweet_counts = find_device_counts()
  sorted_all_counts = sorted(all_counts.items(), key=lambda x: x[1][0],
                             reverse=True)
  sorted_original_counts = sorted(original_counts.items(),
                                  key=lambda x: x[1][0], reverse=True)
  sorted_retweet_counts = sorted(retweet_counts.items(), key=lambda x: x[1][0],
                                 reverse=True)

  Util.ensure_dir_exist(_OUTPUT_DIR)
  with open(_OUTPUT_DIR + 'source_device_all.tsv', 'w') as out_file:
    for device, (count, percentage) in sorted_all_counts:
      out_file.write('%s\t%s\t%s\n' % (device, count, percentage))
  with open(_OUTPUT_DIR + 'source_device_original.tsv', 'w') as out_file:
    for device, (count, percent_of_originals,
                 percent_tweets_original) in sorted_original_counts:
      out_file.write('%s\t%s\t%s\t%s\n' % (device, count, percent_of_originals,
                                           percent_tweets_original))
  with open(_OUTPUT_DIR + 'source_device_retweets.tsv', 'w') as out_file:
    for device, (count, percent_of_retweets,
                 percent_tweets_retweets) in sorted_retweet_counts:
      out_file.write('%s\t%s\t%s\t%s\n' % (device, count, percent_of_retweets,
                                           percent_tweets_retweets))
  log('Analysis complete.')
  

if __name__ == "__main__":
  run()
