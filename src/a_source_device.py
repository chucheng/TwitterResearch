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
_DELTA_FOR_GRAPH = 8

_REGENERATE_DATA = False
_REDRAW_GRAPH = True

_LOG_FILE = 'a_source_device.log'
_OUTPUT_DIR = '../data/SourceDevice/'
_GRAPH_DIR = Util.get_graph_output_dir('SourceDevice/')


def draw_graph(nf_all, top_dict, delta_dict, param_str):
  """Draws a graphical representation of this analysis.

  Draws three bars for each of the top 5 sources, as determined by
  sorting w/ no filter, all, filter by top news, and filter by time
  delta.

  Keyword Arguments:
  nf_all -- A list of (device, percent) pairs in sorted order, no filtering.
  top_dict -- (Dictionary) Maps device to percent, filter by top news.
  delta_dict -- (Dictionary) Maps device to percent, filter by delta.
  """
  devices = []
  no_filter = []
  top = []
  delta = []

  for i in range(0, 5):
    device, percent = nf_all[i]
    devices.append(device)
    no_filter.append(percent)

  for device in devices:
    percent_top = top_dict[device]
    percent_delta = delta_dict[device]
    top.append(percent_top)
    delta.append(percent_delta)

  fig = plt.figure()
  axs = fig.add_subplot(111)
  ind = npy.arange(5)
  width = .15

  rects1 = axs.bar(ind, no_filter, width, color='w', hatch='\\')
  rects2 = axs.bar(ind + width, top, width, color='w', hatch='--')
  rects3 = axs.bar(ind + 2. * width, delta, width, color='w', hatch='/')

  axs.set_ylabel('Percentage', fontsize='16')
  axs.set_xticks(ind + width)
  axs.set_xticklabels(devices, rotation='10')

  axs.legend((rects1[0], rects2[0], rects3[0]),
             ('All Tweets', 'Top Tweets',
              'Tweets within %s hour delta' % _DELTA_FOR_GRAPH))

  with open(_GRAPH_DIR + '/source_device_%s.png' % param_str, 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + '/source_device_%s.eps' % param_str, 'w') as graph:
    plt.savefig(graph, format='eps')

  plt.close()


def find_device_counts(max_delta, deltas, top_news=None, cache=None):
  """Finds the number of tweets by each source device.

  * To achieve no filtering by delta, pass in sys.maxint.
  * To filter for top news, pass top_news (Set), and cache (Dict)
    mapping short_url to long_url.

  Returns:
  Dictionary of source device string to pair of (count, percentage).
  e.g. {'Twitter for iPhone': (1100, 10.0) ...}
  """
  if top_news and not cache:
    log('If top news is given, cache must be provided so we can parse urls')
    exit()
  device_counts = {}
  all_count = 0
  device_counts_original = {}
  original_count = 0
  device_counts_retweets = {}
  retweet_count = 0
  for month in _WINDOW_MONTHS:
    log('Finding device counts for month %s and delta %s.' % (month, max_delta))
    if top_news:
      log('Limiting device counts to tweets with urls in top %s percent of '
          'ground truths' % int(_SIZE_TOP_NEWS * 100))
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
              # If we don't see the tweet_id in the timedeltas file, we weren't
              # able to parse a url from the tweet text, so lets ignore it by
              # setting default delta to sys.maxint
              delta = sys.maxint
              if tweet_id in deltas:
                delta = deltas[tweet_id]
              if delta < max_delta: 
                # Check if url is in top news set. If no top news is given,
                # then it defaults to yes.
                in_top_news = True
                if top_news:
                  in_top_news = False
                  tweet_text = tokens[_TWEETFILE_TWEET_TEXT_INDEX]
                  urls = URLUtil.parse_urls(tweet_text, cache)
                  for url in urls:
                    if url in top_news:
                      in_top_news = True

                if in_top_news:
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
    

def load_data(grouping):
  """Loads the data from disk.

  Keyword Arguments:
  grouping -- (String) Valid values are 'all', 'original', 'retweets'.

  Returns:
  nf_all -- (List) (device, percent) tuples in sorted order.
  top_dict -- (Dict) Maps device to percent, filtered by top news.
  delta_dict -- (Dict) Maps device to percent, filtered by delta.
  """
  log('Loading data for %s...' % grouping)
  nf_all = []
  top_dict = {}
  delta_dict = {}
  with open('../data/SourceDevice/source_device_%s.tsv' % grouping) as in_file:
    for line in in_file:
      tokens = line.split('\t')
      device = tokens[_DEVICE_FILE_DEVICE_INDEX].strip()
      percent = float(tokens[_DEVICE_FILE_PERCENT1_INDEX].strip())
      nf_all.append((device, percent))
  with open('../data/SourceDevice/source_device_%s_t%s.tsv'
            % (grouping, int(_SIZE_TOP_NEWS * 100))) as in_file:
    for line in in_file:
      tokens = line.split('\t')
      device = tokens[_DEVICE_FILE_DEVICE_INDEX].strip()
      percent = float(tokens[_DEVICE_FILE_PERCENT1_INDEX].strip())
      top_dict[device] = percent
  with open('../data/SourceDevice/source_device_%s_%s.tsv'
            % (grouping, _DELTA_FOR_GRAPH)) as in_file:
    for line in in_file:
      tokens = line.split('\t')
      device = tokens[_DEVICE_FILE_DEVICE_INDEX].strip()
      percent = float(tokens[_DEVICE_FILE_PERCENT1_INDEX].strip())
      delta_dict[device] = percent
  return nf_all, top_dict, delta_dict


def output_data(sorted_all_counts, sorted_original_counts,
                sorted_retweet_counts, param_str):
  """Outputs the data to disk.

  Keyword Arguments:
  sorted_all_counts -- (List) (device, (count, percent1)) tuples,
                       sorted, all tweets
  sorted_original_counts -- (List) (device, (count, percent1, percent2)) tuples,
                            sorted, original tweets only
  sorted_retweet_counts -- (List) (device, (count, percent1, percent2)) tuples,
                           sorted, retweets only
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


def sort_data(all_counts, original_counts, retweet_counts):
  """Sorts the data.

  Keyword Arguments:
  all_counts -- (Dict<String, Int>) device -> count, all tweets.
  original_counts -- (Dict<String, Int>) device -> count, original tweets only.
  retweet_counts -- (Dict<String, Int>) device -> count, retweet tweets only.

  Returns:
  sorted_all_counts -- (List) (device, (count, percent)) tuples, all tweets.
  sorted_original_counts -- (List) (device, (count, percet1, percent2)) tuples,
                            original tweets only
  sorted_retweet_counts -- (List) (device, (count, percet1, percent2)) tuples,
                            retweet tweets only
  """
  sorted_all_counts = sorted(all_counts.items(), key=lambda x: x[1][0],
                             reverse=True)
  sorted_original_counts = sorted(original_counts.items(),
                                  key=lambda x: x[1][0], reverse=True)
  sorted_retweet_counts = sorted(retweet_counts.items(),
                                 key=lambda x: x[1][0],
                                 reverse=True)
  return sorted_all_counts, sorted_original_counts, sorted_retweet_counts


def log(message):
  """Helper method to modularize the format of log messages.
  
  Keyword Arguments:
  message -- A string to log.
  """
  FileLog.log(_LOG_FILE, message)


def run():
  """Main logic for this analysis."""
  FileLog.set_log_dir()
  Util.ensure_dir_exist(_OUTPUT_DIR)
  if _REGENERATE_DATA:
    deltas = find_deltas()
    cache = Util.load_cache()
    seeds = Util.load_seeds()

    # Do analysis only for stories in top news.
    param_str = '_t%s' % (int(_SIZE_TOP_NEWS * 100))
    gts = ground_truths.get_gt_rankings(seeds, DataSet.ALL)
    top_news = ground_truths.find_target_news(gts, _SIZE_TOP_NEWS)

    (all_counts, original_counts,
     retweet_counts) = find_device_counts(sys.maxint, deltas, top_news, cache)

    (sorted_all_counts, sorted_original_counts,
     sorted_retweet_counts) = sort_data(all_counts, original_counts,
                                        retweet_counts)

    output_data(sorted_all_counts, sorted_original_counts,
                sorted_retweet_counts, param_str)

    # Do analysis w/ delta, including sys.max to do analysis with no delta.
    for delta in [sys.maxint] + _DELTAS:
      param_str = '_%s' % delta
      if delta == sys.maxint:
        param_str = ''

      (all_counts, original_counts,
       retweet_counts) = find_device_counts(delta, deltas)

      (sorted_all_counts, sorted_original_counts,
       sorted_retweet_counts) = sort_data(all_counts, original_counts,
                                          retweet_counts)

      output_data(sorted_all_counts, sorted_original_counts,
                  sorted_retweet_counts, param_str)

  if _REDRAW_GRAPH:
    (nf_all, top_dict_all, delta_dict_all) = load_data('all')
    (nf_original, top_dict_original,
     delta_dict_original) = load_data('original')
    (nf_retweet, top_dict_retweet, delta_dict_retweet) = load_data('retweets')
    log('Drawing all graph...')
    draw_graph(nf_all, top_dict_all, delta_dict_all,
               'all_%s' % _DELTA_FOR_GRAPH)
    log('Drawing original graph...')
    draw_graph(nf_original, top_dict_original, delta_dict_original,
               'original_%s' % _DELTA_FOR_GRAPH)
    log('Drawing retweets graph...')
    draw_graph(nf_retweet, top_dict_retweet, delta_dict_retweet,
               'retweets_%s' %_DELTA_FOR_GRAPH)

  log('Analysis complete.')
  

if __name__ == "__main__":
  run()
