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
  Dictionary of source device string to total count.
  """
  device_counts = {}
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
              if source_device in device_counts:
                device_counts[source_device] += 1
              else:
                device_counts[source_device] = 1
  return device_counts


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
  device_counts = find_device_counts()
  sorted_counts = sorted(device_counts.items(), key=lambda x: x[1],
                         reverse=True)

  Util.ensure_dir_exist(_OUTPUT_DIR)
  with open(_OUTPUT_DIR + 'source_device.tsv', 'w') as out_file:
    for device, count in sorted_counts:
      out_file.write('%s\t%s\n' % (device, count))
  log('Analysis complete.')
  

if __name__ == "__main__":
  run()
