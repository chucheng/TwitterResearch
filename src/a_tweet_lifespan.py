"""
This module performs an analysis about the lifespan of tweets. That is, it
attempts to determine how long it takes, in general, for a tweet to obtain
the majority of its votes, or retweets.

In this analysis, the majority is defined as 90%.

__author__ = 'Chris Moghbel (cmoghbel@cs.ucla.edu)'
"""
import FileLog
import Util

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.axis

from datetime import datetime

_LOG_FILE = 'a_top_tweets.log'
_GRAPH_DIR = Util.get_graph_output_dir('TweetLifespan/')

_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

_TIMEDELTAS_FILE_TWEET_ID_INDEX = 0
_TIMEDELTAS_FILE_USER_ID_INDEX = 1 
_TIMEDELTAS_FILE_DELTA_INDEX = 2
_TIMEDELTAS_FILE_URL_INDEX = 3
_TIMEDELTAS_FILE_CATEGORY_INDEX = 4

_SIZE_TOP_NEWS = .02


def _determine_hours(low, high, step_percent):
  """Calculates the x range for this analysis.

  Keyword Arguments:
  low -- The lower exponent to start at.
  high -- The high exponent to end at.
  step_percent -- The percent of the current power of 10 to step by.

  Returns:
  hours -- The hours used as the x range.
  """
  hours = []
  for i in range(low, high):
    hours += range(10**i, 10**(i+1), max(1, int(10**(i+1) * step_percent)))
  return hours

_AGGREGATE_HOURS = _determine_hours(-5, 6, .01)


def aggr_by_hour(time_of_90s, top_news):
  """Finds the percentage of inactive news at each time period.

  Calculates for both all news and top news.

  Keyword Arguments:
  time_of_90s -- The time at which 90% of tweets occured.
  top_news -- A set of urls representing the top news.

  Returns:
  aggregates -- A list of percentages of all news that is inactive.
  aggregates_top -- List of percentages of top news that is inactive.
  """
  log('Aggregating number dead stories by hours...')
  aggregates = []
  aggregates_top = []
  for aggregate_hour in _AGGREGATE_HOURS:
    num_dead_stories = 0
    num_dead_stories_top = 0
    for url, delta in time_of_90s:
      if delta < aggregate_hour:
        num_dead_stories += 1
        if url in top_news:
          num_dead_stories_top += 1
    aggregates.append(num_dead_stories)
    aggregates_top.append(num_dead_stories_top)
  aggregates = [int((float(aggregate) / len(time_of_90s)) * 100)
                for aggregate in aggregates]
  aggregates_top = [int((float(aggregate) / len(top_news)) * 100)
                    for aggregate in aggregates_top]
  return aggregates, aggregates_top


def calc_90_percent_count(counts):
  """Updates dictionary of 100% counts to 90% counts.

  NOTE: This method updates the argument in place.

  Keyword Arguments:
  counts -- Dictionary to update in place.
  """
  log('Calculating 90% counts...')
  for url, count in counts.items():
    counts[url] = round(.9 * count)


def draw_graph(aggregates, aggregates_top):
  """Draws the tweet lifespan graph.

  Keyword Arguments:
  aggregates -- List of percentages of inactive news.
  aggregates_top -- List of percentages of inactive news for top news.
  """
  plots = []
  figure = plt.figure()
  axs = figure.add_subplot(111)

  all_plot = axs.semilogx(_AGGREGATE_HOURS, aggregates)
  plots.append(all_plot)

  top_plot = axs.semilogx(_AGGREGATE_HOURS, aggregates_top, 'r--', linewidth=3)
  plots.append(top_plot)

  labels = ['All News', 'Top 2% in Popularity']
  plt.legend(plots, labels, loc=4, ncol=1, columnspacing=0, handletextpad=0)

  plt.grid(True, which='major', linewidth=2)

  plt.xlabel('Passing Hours', fontsize=16)
  plt.ylabel('Inactive News Stories (%)', fontsize=16)

  with open(_GRAPH_DIR + 'tweet_lifespan.png', 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + 'tweet_lifespan.eps', 'w') as graph:
    plt.savefig(graph, format='eps')

  log('Outputted graph!')
  plt.close()


def find_total_tweet_count(seeds):
  """Finds the total tweet count (100%) for each url.

  Finds only for urls whose seed times are within the desired window.

  Keyword Arguments:
  seeds -- Seeds times for every url.

  Returns:
  counts -- A dictionary of url to tweet count.
  """
  log('Finding total tweet counts...')
  counts = {}
  with open('../data/FolkWisdom/time_deltas.tsv') as in_file:
    for line in in_file:
      tokens = line.split('\t')
      url = tokens[_TIMEDELTAS_FILE_URL_INDEX]
      seed_time = seeds[url]
      if is_in_window(seed_time):
        if url in counts:
          counts[url] += 1
        else:
          counts[url] = 1
  return counts


def find_90_times(counts_90):
  """Finds the times at which 90% of tweets have occured.

  Keyword Arguments:
  counts_90 -- A dictionary of url to 90% tweet count.

  Returns:
  times_sorted -- A list of (url, datetime) pairs, sorted by earliest time.
  """
  log('Finding times at which death (90%) occurs...')
  times = {}
  counts = {}
  with open('../data/FolkWisdom/time_deltas.tsv') as in_file:
    for line in in_file:
      tokens = line.split('\t')
      url = tokens[_TIMEDELTAS_FILE_URL_INDEX].strip()
      if url in counts_90: # Need to make sure its in the right window.
        if url in counts:
          counts[url] += 1
        else:
          counts[url] = 1
        if counts[url] == counts_90[url]:
          seconds_delta = int(tokens[_TIMEDELTAS_FILE_DELTA_INDEX])
          time_of_90 = seconds_delta / 3600.0
          times[url] = time_of_90

  times_sorted = sorted(times.items(), key=lambda x: x[1])
  return times_sorted


def get_gt_rankings(seeds, category=None):
  """Generate the ground truth rankings.
  
  Keyword Arguments:
  seeds -- Dictionary of url to first time seen.
  category -- Category to generate ground truths for, None for all news.

  Returns:
  gt_rankings -- A list of (url, count) pairs in ranked order.
  """
  log('Getting ground truth rankings...')
  gt_tweet_counts = {}
  with open('../data/FolkWisdom/time_deltas.tsv') as input_file:
    for line in input_file:
      tokens = line.split('\t')
      url = tokens[_TIMEDELTAS_FILE_URL_INDEX]
      if url in seeds:
        seed_time = seeds[url]
        if is_in_window(seed_time):
          if category:
            url_category = tokens[_TIMEDELTAS_FILE_CATEGORY_INDEX].strip()
            if url_category == category:
              if url in gt_tweet_counts:
                gt_tweet_counts[url] += 1
              else:
                gt_tweet_counts[url] = 1
          else:
            if url in gt_tweet_counts:
              gt_tweet_counts[url] += 1
            else:
              gt_tweet_counts[url] = 1

  gt_rankings = sorted(gt_tweet_counts.items(), key=lambda x: x[1],
                       reverse=True)
  return gt_rankings


def get_top_news(truths, percentage):
  """Generates a set of top news.

  Keyword Arguments:
  truths -- Dictionary of rank to url and count representing ground truths.
  percentage -- Percentage of total news to make top news, as a float.

  Returns:
  top_news -- A set of urls representing the top news.
  """
  log('Getting top news at %s percent...' % int(percentage * 100))
  num_top_news = int(len(truths) * percentage)
  top_news = set()
  for i in range(num_top_news):
    url, _ = truths[i]
    top_news.add(url)
  return top_news


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


def load_seeds():
  """Loads the set of seed times for urls from file."""
  log('Loading seeds...')
  seeds = {}
  with open('../data/FolkWisdom/seed_times.tsv') as input_file:
    for line in input_file:
      tokens = line.split('\t')
      url = tokens[3].strip()
      seed_time = datetime.strptime(tokens[2], _DATETIME_FORMAT)
      seeds[url] = seed_time
  return seeds


def log(message):
  """Helper method to modularize the format of log messages.
  
  Keyword Arguments:
  message -- A string to log.
  """
  FileLog.log(_LOG_FILE, message)


def run():
  """Contains the main logic for this analysis."""
  FileLog.set_log_dir()
  seeds = load_seeds()
  counts = find_total_tweet_count(seeds)
  calc_90_percent_count(counts)
  time_of_90s = find_90_times(counts)
  truths = get_gt_rankings(seeds)
  top_news = get_top_news(truths, _SIZE_TOP_NEWS)
  aggregates, aggregates_top = aggr_by_hour(time_of_90s, top_news)
  draw_graph(aggregates, aggregates_top)


if __name__ == "__main__":
  run()
