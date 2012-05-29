"""
This module handles the selection, graph drawing, and other operations for the
basic groups.

__author__ = 'Chris Moghbel (cmoghbel@cs.ucla.edu)'
"""
import Util

from datetime import timedelta

import matplotlib
matplotlib.use("Agg")
from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt
import matplotlib.axis

from constants import _TIMEDELTAS_FILE_URL_INDEX
from constants import _TIMEDELTAS_FILE_USER_ID_INDEX
from constants import _TIMEDELTAS_FILE_DELTA_INDEX
from constants import _TIMEDELTAS_FILE_CATEGORY_INDEX
from constants import _TIMEDELTAS_FILE_SOURCE_INDEX
from constants import _USER_ACTIVITY_FILE_ID_INDEX

_GRAPH_DIR = Util.get_graph_output_dir('FolkWisdom/')


def draw_precision_groups(market_precisions, newsaholic_precisions,
                                 active_precisions, common_precisions,
                                 run_params_str):
  """Draws the precision recall graph for all the user groups and a given delta.

  Plots the given list of precisions against the number of top news that the
  precision value was calculated for.
  """
  plots = []
  figure = plt.figure()
  axs = figure.add_subplot(111)

  market_plot = axs.plot(market_precisions)
  plots.append(market_plot)

  newsaholic_plot = axs.plot(newsaholic_precisions, '--', linewidth=2)
  plots.append(newsaholic_plot)

  active_plot = axs.plot(active_precisions, ':', linewidth=2)
  plots.append(active_plot)

  common_plot = axs.plot(common_precisions, '-.', linewidth=2)
  plots.append(common_plot)


  labels = ['Market', 'News-addicted', 'Active Users', 'Common Users', ]
  plt.legend(plots, labels, loc=0, ncol=2, columnspacing=0, handletextpad=0)

  plt.grid(True, which='major', linewidth=1)

  axs.yaxis.set_minor_locator(MultipleLocator(5))
  plt.grid(True, which='minor')

  plt.xlabel('Num Top News Picked', fontsize='16')
  plt.ylabel('Precision (%)', fontsize='16')

  with open(_GRAPH_DIR + run_params_str + '/precision_groups_%s.png'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + run_params_str + '/precision_groups_%s.eps'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='eps')

  plt.close()


def draw_precision_recall_groups(market_precisions, market_recalls,
                                 newsaholic_precisions,
                                 newsaholic_recalls, active_precisions,
                                 active_recalls, common_precisions,
                                 common_recalls, run_params_str):
  """Draws the precision recall graph for all the user groups and a given delta.

  Keyword Arguments:
  Requires two lists, one of precision values and one of recal values, for each
  user group from the following: market, newsaholics, active users,
  common users, and experts (precision, F-score, confidence interval, super).
  This accounts for 8 user groups, meaning 16 lists in all.
  delta -- The number of hours of the time window in which votes were counted.
  category -- The category we are analyzing.
  """
  plots = []
  figure = plt.figure()
  axs = figure.add_subplot(111)

  market_plot = axs.plot(market_recalls, market_precisions)
  plots.append(market_plot)

  newsaholic_plot = axs.plot(newsaholic_recalls, newsaholic_precisions, '--',
                            linewidth=2)
  plots.append(newsaholic_plot)

  active_plot = axs.plot(active_recalls, active_precisions, ':',
                        linewidth=2)
  plots.append(active_plot)

  common_plot = axs.plot(common_recalls, common_precisions, '-.',
                        linewidth=2)
  plots.append(common_plot)


  labels = ['Market', 'News-addicted', 'Active Users', 'Common Users', ]
  plt.legend(plots, labels, loc=0, ncol=2, columnspacing=0, handletextpad=0)

  max_x = max([max(market_recalls), max(newsaholic_recalls),
               max(active_recalls), max(common_recalls)])
  plt.axis([0, max_x + 5, 0, 105])
  plt.grid(True, which='major', linewidth=1)

  axs.xaxis.set_minor_locator(MultipleLocator(5))
  axs.yaxis.set_minor_locator(MultipleLocator(5))
  plt.grid(True, which='minor')

  plt.xlabel('Recall (%)', fontsize='16')
  plt.ylabel('Precision (%)', fontsize='16')

  with open(_GRAPH_DIR + run_params_str + '/precision_recall_groups_%s.png'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + run_params_str + '/precision_recall_groups_%s.eps'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='eps')

  plt.close()


def gather_tweet_counts(hours, seeds, newsaholics, active, category=None):
  """Gathers the tweet counts for a given set of months.
  
  Only counts votes if they occur within the given time delta from the seed
  time (except for the ground truth rankings).
  
  Keyword Arguments:
  hours -- The number of hours from the seed time in which to accept votes.
  seeds -- A dictionary of url to the datetime of it first being seend
  Accepts a parameter for a set defining each of the following user groups:
  newsaholics, active users, experts (precision), experts (F-score),
  experts (confidence interval), and experts (super experts).
  category -- The category to gather tweets for, None if for all news.

  Returns:
  Dictionary of url to tweet count for all user groups. This includes:
  ground truth, market, newsaholic, active users, common users, and
  experts (precision, F-score, confidence interval, and super).
  """
  market_tweet_counts = {}
  newsaholic_tweet_counts = {}
  active_tweet_counts = {}
  common_tweet_counts = {}
  with open('../data/FolkWisdom/time_deltas.tsv') as input_file:
    for line in input_file:
      tokens = line.split('\t')
      source = tokens[_TIMEDELTAS_FILE_SOURCE_INDEX].strip()
      if source == 'twitterfeed':
        continue
      url = tokens[_TIMEDELTAS_FILE_URL_INDEX]
      user_id = tokens[_TIMEDELTAS_FILE_USER_ID_INDEX]
      time_delta = timedelta(seconds=int(tokens[_TIMEDELTAS_FILE_DELTA_INDEX]))
      max_delta = timedelta.max
      if hours:
        max_delta = timedelta(hours=hours)

      if url in seeds:
        (seed_tweet_id, seed_user_id, seed_time) = seeds[url]
        if Util.is_in_testing_set(seed_time):

          if time_delta < max_delta:

            category_matches = True
            if category:
              category_matches = False
              url_category = tokens[_TIMEDELTAS_FILE_CATEGORY_INDEX].strip()
              if url_category == category:
                category_matches = True
             
            if category_matches:

              # Market
              if url in market_tweet_counts:
                market_tweet_counts[url] += 1
              else:
                market_tweet_counts[url] = 1

              # Other groups
              if user_id in newsaholics:
                if url in newsaholic_tweet_counts:
                  newsaholic_tweet_counts[url] += 1
                else:
                  newsaholic_tweet_counts[url] = 1
              elif user_id in active:
                if url in active_tweet_counts:
                  active_tweet_counts[url] += 1
                else:
                  active_tweet_counts[url] = 1                
              else:
                if url in common_tweet_counts:
                  common_tweet_counts[url] += 1
                else:
                  common_tweet_counts[url] = 1                
              
                
  return (market_tweet_counts, newsaholic_tweet_counts, active_tweet_counts,
          common_tweet_counts)


def get_rankings(delta, seeds, newsaholics, active_users, category=None):
  """Gets the true rankings, and ranking as determined by various user groups.
  
  Keyword Arguments:
  delta -- The time window, in hours.
  seeds -- The url to first time seen dictionary.
  Accepts a user of user ids for each of the following user groups:
  newsaholics, active users, experts (precision, f-score, confidnce
  interval, and super).
  category -- The category to get rankings for, None for all news.
  
  Returns:
  Returns rankings for the following user groups:
  market, newsaholics, active users, common userse, experts (precision,
  f-score, confidence interval, super).
  """
  mtc, etc, atc, ctc  = gather_tweet_counts(delta, seeds, newsaholics,
                                            active_users,category)
  market_rankings = sorted(mtc.items(), key=lambda x: x[1], reverse=True)
  newsaholic_rankings = sorted(etc.items(), key=lambda x: x[1], reverse=True)
  active_rankings = sorted(atc.items(), key=lambda x: x[1], reverse=True)
  common_rankings = sorted(ctc.items(), key=lambda x: x[1], reverse=True)
  return market_rankings, newsaholic_rankings, active_rankings, common_rankings


def group_users(delta, category=None):
  """Groups users into 'newsaholic', 'active', and 'common' categories.
  
  Returns:
  num_users -- The overall total number of users.
  newsaholics -- A python set of user ids for newsaholic users, defined as
  users in top 2% of users as ranked by activity.
  active_users -- A python set of user ids for active users, defined as users
  in between 2% and 25% of users as ranked by activity.
  common_users -- A python set of user ids for common users, defined as users
  whose rank is lower the 25% as ranked by activity.
  """
  user_ids_sorted = []
  input_file = '../data/FolkWisdom/user_activity_%s_%s.tsv' % (delta, category)
  with open(input_file) as input_file:
    for line in input_file:
      tokens = line.split('\t')
      user_id = tokens[_USER_ACTIVITY_FILE_ID_INDEX]
      user_ids_sorted.append(user_id)
  num_users = len(user_ids_sorted)
  two_percent = int(num_users * .02)
  twenty_five_percent = int(num_users * .25)
  
  newsaholics = set()
  active_users = set()
  common_users = set()
  for i in range(num_users):
    user_id = user_ids_sorted[i]
    if i <= two_percent:
      newsaholics.add(user_id)
    elif i <= twenty_five_percent:
      active_users.add(user_id)
    else:
      common_users.add(user_id)
  return num_users, newsaholics, active_users, common_users
