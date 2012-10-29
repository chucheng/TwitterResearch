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

_LOG_FILE = 'a_tweet_popularity.log'
_GRAPH_DIR = Util.get_graph_output_dir('TweetPopularity/')
_DATA_DIR = '../data/'


def draw_graph(num_tweets_in_log, count_tweets_bin_log):
  """Draws the tweet popularity graph.

  Keyword Arguments:
  """
  plots = []
  figure = plt.figure()
  axs = figure.add_subplot(111)

  # plot = axs.plot(num_tweets_in_log, count_tweets_bin_log)
  # plot = axs.scatter(num_tweets_in_log, count_tweets_bin_log, s=5)
  plot = axs.loglog(num_tweets_in_log, count_tweets_bin_log)
  # plot = axs.semilogx(num_tweets_in_log, count_tweets_bin_log)
  plots.append(plot)

  # top_plot = axs.semilogx(_AGGREGATE_HOURS, aggregates_top, 'r--', linewidth=3)
  # plots.append(top_plot)

  # labels = ['All News', 'Top 2% in Popularity']
  # plt.legend(plots, labels, loc=4, ncol=1, columnspacing=0, handletextpad=0)

  plt.grid(True, which='major', linewidth=2)

  plt.xlabel('% of news articles with given popularity', fontsize=16)
  plt.ylabel('Popularity (Number of tweets in a news-tweet thread)', fontsize=16)

  with open(_GRAPH_DIR + 'tweet_popularity.png', 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + 'tweet_popularity.eps', 'w') as graph:
    plt.savefig(graph, format='eps')

  log('Outputted graph!')
  plt.close()


def log(message):
  """Helper method to modularize the format of log messages.
  
  Keyword Arguments:
  message -- A string to log.
  """
  FileLog.log(_LOG_FILE, message)


def run():
  """Contains the main logic for this analysis."""
  FileLog.set_log_dir()

  num_tweets_in_log = []
  count_tweets_bin_log = []

  with open(_DATA_DIR + 'popularity.graph.data.100bins') as in_file:
    for line in in_file.readlines():
      tokens = line.split('\t')
      num_tweets_log = float(tokens[1])
      count_tweets_in_bin = float(tokens[4]) * 100.0
      num_tweets_in_log.append(num_tweets_log)
      count_tweets_bin_log.append(count_tweets_in_bin)

  log('x: %s' % num_tweets_in_log)
  log('y: %s' % count_tweets_bin_log)

  draw_graph(num_tweets_in_log, count_tweets_bin_log)


if __name__ == "__main__":
  run()
