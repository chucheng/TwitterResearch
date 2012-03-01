"""
This module is an analysis for finding the number of tweets from each source
device.

__author__ = 'Chris Moghbel (cmoghbel@cs.ucla.edu)'
"""
import FileLog
import Util
import URLUtil
import ground_truths
from ground_truths import DataSet

import os
import sys
import re

from datetime import datetime

import numpy as npy

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from constants import _TIMEDELTAS_FILE_TWEET_ID_INDEX
from constants import _TIMEDELTAS_FILE_DELTA_INDEX

from constants import _TWEETFILE_TWEET_ID_INDEX
from constants import _TWEETFILE_CREATED_AT_INDEX
from constants import _TWEETFILE_RETWEET_COUNT_INDEX
from constants import _TWEETFILE_SOURCE_INDEX
from constants import _TWEETFILE_TWEET_TEXT_INDEX

from constants import _DEVICE_FILE_DEVICE_INDEX
from constants import _DEVICE_FILE_PERCENT1_INDEX

from constants import _DATETIME_FORMAT
from constants import _WINDOW_MONTHS
from constants import _DELTAS

_SIZE_TOP_NEWS = .02
_NUM_DEVICES = 7

_REGENERATE_DATA = False
_REDRAW_GRAPH = True

_LOG_FILE = 'a_source_device.log'
_OUTPUT_DIR = '../data/SourceDevice/'
_GRAPH_DIR = Util.get_graph_output_dir('SourceDevice/')


def draw_graph(top_sorted, original_dict, retweet_dict, param_str):
  """Draws a graphical representation of this analysis.

  Draws three bars for each of the top 5 sources, as determined by
  sorting w/ no filter, all, filter by top news, and filter by time
  delta.

  Keyword Arguments:
  top_sorted -- (List) (device, percent) pairs in sorted order, top tweets.
  original_dict -- (Dictionary) Maps device to percent, filter by origin tweets.
  retweet_dict -- (Dictionary) Maps device to percent, filter by retweets.
  """
  devices = []
  top = []
  original = []
  retweet = []

  for i in range(0, _NUM_DEVICES):
    device, percent = top_sorted[i]
    devices.append(device)
    top.append(percent)

  for device in devices:
    percent_original = 0.0
    percent_retweet = 0.0
    if device in original_dict:
      percent_original = original_dict[device]
    if device in retweet_dict:
      percent_retweet = retweet_dict[device]
    original .append(percent_original)
    retweet.append(percent_retweet)

  devices = [re.sub(r'[^a-zA-Z0-9_\s]', '', device) for device in devices]

  fig = plt.figure()
  axs = fig.add_subplot(111)
  ind = npy.arange(_NUM_DEVICES)
  width = .15

  rects1 = axs.bar(ind, top, width, color='w', hatch='\\', edgecolor='red')
  rects2 = axs.bar(ind + width, original, width, color='w',
                   hatch='--', edgecolor='blue')
  rects3 = axs.bar(ind + 2. * width, retweet, width, color='w',
                   hatch='/', edgecolor='green')

  axs.set_ylabel('Percentage', fontsize='16')
  axs.set_xticks(ind + width)
  axs.set_xticklabels(devices, rotation='12')

  axs.legend((rects1[0], rects2[0], rects3[0]),
             ('Popular News', 'Origin Tweets', 'Retweets'))

  with open(_GRAPH_DIR + '/source_device%s.png' % param_str, 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + '/source_device%s.eps' % param_str, 'w') as graph:
    plt.savefig(graph, format='eps')

  plt.close()


def find_device_counts(max_delta, deltas, top_news, cache):
  """Finds the number of tweets by each source device.

  * To achieve no filtering by delta, pass in sys.maxint.

  Returns:
  Dictionary of source device string to pair of (count, percentage).
  e.g. {'Twitter for iPhone': (1100, 10.0) ...} for all, top, origin,
  and retweets.
  """
  device_counts = {}
  all_count = 0
  device_counts_top = {}
  top_count = 0
  device_counts_original = {}
  original_count = 0
  device_counts_retweets = {}
  retweet_count = 0
  for month in _WINDOW_MONTHS:
    log('Finding device counts for month %s and delta %s.' % (month, max_delta))
    dir_name = Util.get_data_dir_name_for(month) 
    for filename in os.listdir(dir_name):
      if '.tweet' in filename and 'http_nyti_ms' in filename:
        data_file = '%s/%s' % (dir_name, filename)
        with open(data_file) as input_file:
          for line in input_file:
            tokens = line.split('\t')
            created = datetime.strptime(tokens[_TWEETFILE_CREATED_AT_INDEX],
                                        _DATETIME_FORMAT)
            if Util.is_in_window(created):
              tweet_id = tokens[_TWEETFILE_TWEET_ID_INDEX]
              source_device = tokens[_TWEETFILE_SOURCE_INDEX]
              retweet = bool(int(tokens[_TWEETFILE_RETWEET_COUNT_INDEX]))

              # If the url is in the top news, increment the count. Note
              # we do not limit this by delta.
              tweet_text = tokens[_TWEETFILE_TWEET_TEXT_INDEX]
              urls = URLUtil.parse_urls(tweet_text, cache)
              for url in urls:
                if url in top_news:
                  top_count += 1
                  if source_device in device_counts_top:
                    device_counts_top[source_device] += 1
                  else:
                    device_counts_top[source_device] = 1

              # If we don't see the tweet_id in the timedeltas file, we weren't
              # able to parse a url from the tweet text, so lets ignore it by
              # setting default delta to sys.maxint
              delta = sys.maxint
              if tweet_id in deltas:
                delta = deltas[tweet_id]
              if delta < max_delta: 
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
  for device, count in device_counts_top.items():
    device_counts_top[device] = (count, (float(count) / top_count) * 100)

  return (device_counts, device_counts_original, device_counts_retweets,
          device_counts_top)


def find_deltas():
  """Loads a map of tweet_id to delta values."""
  log('Finding deltas...')
  tweet_id_to_delta = {}
  with open('../data/FolkWisdom/time_deltas.tsv') as in_file:
    for line in in_file:
      tokens = line.split('\t')
      tweet_id = tokens[_TIMEDELTAS_FILE_TWEET_ID_INDEX]
      # Need to convert to hours
      delta = int(tokens[_TIMEDELTAS_FILE_DELTA_INDEX]) / 3600
      tweet_id_to_delta[tweet_id] = delta 
  return tweet_id_to_delta
    

def load_data(param_str):
  """Loads the data from disk.

  Keyword Arguments:
  param_str -- (String) the parameters, e.g. _top_4

  Returns:
  top -- (List) (device, percent) tuples in sorted order, top tweets.
  original_dict -- (Dict) Maps device to percent, filtered by origin tweets.
  retweet_dict -- (Dict) Maps device to percent, filtered by retweets.
  """
  log('Loading data for %s...' % param_str)
  top = []
  original_dict = {}
  retweet_dict = {}
  with open('../data/SourceDevice/source_device_top%s.tsv'
            % param_str) as in_file:
    for line in in_file:
      tokens = line.split('\t')
      device = tokens[_DEVICE_FILE_DEVICE_INDEX].strip()
      percent = float(tokens[_DEVICE_FILE_PERCENT1_INDEX].strip())
      top.append((device, percent))
  with open('../data/SourceDevice/source_device_original%s.tsv'
            % param_str) as in_file:
    for line in in_file:
      tokens = line.split('\t')
      device = tokens[_DEVICE_FILE_DEVICE_INDEX].strip()
      percent = float(tokens[_DEVICE_FILE_PERCENT1_INDEX].strip())
      original_dict[device] = percent
  with open('../data/SourceDevice/source_device_retweet%s.tsv'
            % param_str) as in_file:
    for line in in_file:
      tokens = line.split('\t')
      device = tokens[_DEVICE_FILE_DEVICE_INDEX].strip()
      percent = float(tokens[_DEVICE_FILE_PERCENT1_INDEX].strip())
      retweet_dict[device] = percent
  return top, original_dict, retweet_dict 


def output_data(sorted_all_counts, sorted_original_counts,
                sorted_retweet_counts, sorted_top_counts, param_str):
  """Outputs the data to disk.

  Keyword Arguments:
  sorted_all_counts -- (List) (device, (count, percent1)) tuples,
                       sorted, all tweets
  sorted_original_counts -- (List) (device, (count, percent1, percent2)) tuples,
                            sorted, original tweets only
  sorted_retweet_counts -- (List) (device, (count, percent1, percent2)) tuples,
                           sorted, retweets only
  sorted_top_counts -- (List, (device, (count, percent)) tuples sorted,
                       top tweets only.
  """
  with open(_OUTPUT_DIR + 'source_device_all%s.tsv' % param_str,
            'w') as out_file:
    for device, (count, percentage) in sorted_all_counts:
      out_file.write('%s\t%s\t%s\n' % (device, count, percentage))
  with open(_OUTPUT_DIR + 'source_device_original%s.tsv' % param_str,
            'w') as out_file:
    for device, (count, percent_of_originals,
                 percent_tweets_original) in sorted_original_counts:
      out_file.write('%s\t%s\t%s\t%s\n' % (device, count,
                                           percent_of_originals,
                                           percent_tweets_original))
  with open(_OUTPUT_DIR + 'source_device_retweet%s.tsv' % param_str,
            'w') as out_file:
    for device, (count, percent_of_retweets,
                 percent_tweets_retweets) in sorted_retweet_counts:
      out_file.write('%s\t%s\t%s\t%s\n' % (device, count, percent_of_retweets,
                                             percent_tweets_retweets))
  with open(_OUTPUT_DIR + 'source_device_top%s.tsv' % param_str,
            'w') as out_file:
    for device, (count, percentage) in sorted_top_counts:
      out_file.write('%s\t%s\t%s\n' % (device, count, percentage))


def sort_data(all_counts, original_counts, retweet_counts, top_counts):
  """Sorts the data.

  Keyword Arguments:
  all_counts -- (Dict<String, Int>) device -> count, all tweets.
  original_counts -- (Dict<String, Int>) device -> count, original tweets only.
  retweet_counts -- (Dict<String, Int>) device -> count, retweet tweets only.
  top_counts -- (Dict<String, Int>) device -> count, top tweets only.

  Returns:
  sorted_all_counts -- (List) (device, (count, percent)) tuples, all tweets.
  sorted_original_counts -- (List) (device, (count, percet1, percent2)) tuples,
                            original tweets only
  sorted_retweet_counts -- (List) (device, (count, percet1, percent2)) tuples,
                           retweet tweets only
  sorted_top_counts -- (List) (device, (count, percent)) tuples,
                       top tweets only.
  """
  sorted_all_counts = sorted(all_counts.items(), key=lambda x: x[1][0],
                             reverse=True)
  sorted_original_counts = sorted(original_counts.items(),
                                  key=lambda x: x[1][0], reverse=True)
  sorted_retweet_counts = sorted(retweet_counts.items(),
                                 key=lambda x: x[1][0],
                                 reverse=True)
  sorted_top_counts = sorted(top_counts.items(), key=lambda x: x[1][0],
                             reverse=True)
  return (sorted_all_counts, sorted_original_counts, sorted_retweet_counts,
          sorted_top_counts)


def log(message):
  """Helper method to modularize the format of log messages.
  
  Keyword Arguments:
  message -- A string to log.
  """
  FileLog.log(_LOG_FILE, message)


def _get_param_str(delta):
  """Returns the correct param string."""
  if delta == sys.maxint:
    return ''
  return '_%s' % delta


def run():
  """Main logic for this analysis."""
  FileLog.set_log_dir()
  Util.ensure_dir_exist(_OUTPUT_DIR)
  if _REGENERATE_DATA:
    deltas = find_deltas()
    cache = Util.load_cache()
    seeds = Util.load_seeds()

    # Find top news
    param_str = '_t%s' % (int(_SIZE_TOP_NEWS * 100))
    gts = ground_truths.get_gt_rankings(seeds, DataSet.ALL)
    top_news = ground_truths.find_target_news(gts, _SIZE_TOP_NEWS)

    # Do analysis for all delta, including sys.max to do analysis with no delta.
    for delta in [sys.maxint] + _DELTAS:
      param_str = _get_param_str(delta) 

      (all_counts, original_counts,
       retweet_counts, top_counts) = find_device_counts(delta, deltas, top_news,
                                                        cache)

      (sorted_all_counts, sorted_original_counts,
       sorted_retweet_counts, sorted_top_counts) = sort_data(all_counts,
                                                             original_counts,
                                                             retweet_counts,
                                                             top_counts)

      output_data(sorted_all_counts, sorted_original_counts,
                  sorted_retweet_counts, sorted_top_counts, param_str)

  if _REDRAW_GRAPH:
    for delta in [sys.maxint] + _DELTAS:
      param_str = _get_param_str(delta) 

      (top, original_dict, retweet_dict) = load_data(param_str)
      log('Drawing graph for delta %s...' % delta)
      draw_graph(top, original_dict, retweet_dict, param_str)

  log('Analysis complete.')
  

if __name__ == "__main__":
  run()
