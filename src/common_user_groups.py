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

from constants import _TIMEDELTAS_FILE_URL_INDEX
from constants import _TIMEDELTAS_FILE_USER_ID_INDEX
from constants import _TIMEDELTAS_FILE_DELTA_INDEX
from constants import _TIMEDELTAS_FILE_CATEGORY_INDEX
from params import _SWITCHED

_GRAPH_DIR = Util.get_graph_output_dir('CrowdWisdomDef/')


def draw_precision(common_group_ps, expert_p_precisions,
                   expert_f_precisions, expert_c_precisions,
                   run_params_str):
  """Draws the precision recall graph for all the user groups and a given delta.

  Plots the given list of precisions against the number of top news that the
  precision value was calculated for.
  """
  plots = []
  figure = plt.figure()
  axs = figure.add_subplot(111)

  labels = []

  for i, common_group_p in enumerate(common_group_ps):
    group_plot = axs.plot(common_group_p, '--')
    plots.append(group_plot)
    labels.append('Common Users %s Buckets' % (i + 1))

  expert_p_plot = axs.plot(expert_p_precisions)
  plots.append(expert_p_plot)
  labels.append('Precision Experts')

  expert_f_plot = axs.plot(expert_f_precisions)
  plots.append(expert_f_plot)
  labels.append('Fscore Experts')

  expert_c_plot = axs.plot(expert_c_precisions)
  plots.append(expert_c_plot)
  labels.append('CI Experts')

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


def draw_precision_recall(common_group_ps, common_group_rs,
                          expert_p_precisions, expert_p_recalls,
                          expert_f_precisions, expert_f_recalls,
                          expert_c_precisions, expert_c_recalls,
                          run_params_str):
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

  labels = []

  max_x = 0

  for i, (common_group_p, common_group_r) in enumerate(zip(common_group_ps, common_group_rs)):
    group_plot = axs.plot(common_group_r, common_group_p, '--')
    plots.append(group_plot)
    labels.append('Common Users %s Buckets' % (i + 1))
    if max(common_group_r) > max_x:
      max_x = max(common_group_r)

  expert_p_plot = axs.plot(expert_p_recalls, expert_p_precisions)
  plots.append(expert_p_plot)
  labels.append('Precision Experts')

  expert_f_plot = axs.plot(expert_f_recalls, expert_f_precisions)
  plots.append(expert_f_plot)
  labels.append('Fscore Experts')

  expert_c_plot = axs.plot(expert_c_recalls, expert_p_precisions)
  plots.append(expert_c_plot)
  labels.append('CI Experts')

  max_x_experts = max([max(expert_p_recalls), max(expert_f_recalls),
                       max(expert_c_recalls)])
  if max_x_experts > max_x:
    max_x = max_x_experts

  plt.legend(plots, labels, loc=0, ncol=2, columnspacing=0, handletextpad=0)

  print 'max_x: %s' % max_x
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


def gather_tweet_counts(hours, seeds, group, category=None):
  """Gathers the tweet counts for a given set of months.
  
  Only counts votes if they occur within the given time delta from the seed
  time (except for the ground truth rankings).
  
  Keyword Arguments:
  hours -- The number of hours from the seed time in which to accept votes.
  seeds -- A dictionary of url to the datetime of it first being seend
  category -- The category to gather tweets for, None if for all news.

  Returns:
  Dictionary of url to tweet count for all user groups. This includes:
  ground truth, market, newsaholic, active users, common users, and
  experts (precision, F-score, confidence interval, and super).
  """
  group_tweet_counts = {}
  print 'num users in group: %s' % len(group)
  with open('../data/FolkWisdom/time_deltas.tsv') as input_file:
    for line in input_file:
      tokens = line.split('\t')
      url = tokens[_TIMEDELTAS_FILE_URL_INDEX]
      user_id = tokens[_TIMEDELTAS_FILE_USER_ID_INDEX]
      time_delta = timedelta(seconds=int(tokens[_TIMEDELTAS_FILE_DELTA_INDEX]))
      max_delta = timedelta.max
      if hours:
        max_delta = timedelta(hours=hours)

      if url in seeds:
        (seed_tweet_id, seed_user_id, seed_time) = seeds[url]
        in_correct_set = Util.is_in_testing_set(seed_time)
        if _SWITCHED:
          in_correct_set = Util.is_in_training_set(seed_time)
        if in_correct_set:

          if time_delta < max_delta:

            category_matches = True
            if category:
              category_matches = False
              url_category = tokens[_TIMEDELTAS_FILE_CATEGORY_INDEX].strip()
              if url_category == category:
                category_matches = True
             
            if category_matches:

              if user_id in group:
                if url in group_tweet_counts:
                  group_tweet_counts[url] += 1
                else:
                  group_tweet_counts[url] = 1
              
  return group_tweet_counts


def get_rankings_for_group(delta, seeds, group, category=None):
  """Gets the true rankings, and ranking as determined by various user groups.
  
  Keyword Arguments:
  delta -- The time window, in hours.
  seeds -- The url to first time seen dictionary.
  category -- The category to get rankings for, None for all news.
  
  Returns:
  Returns rankings for the following user groups:
  market, newsaholics, active users, common userse, experts (precision,
  f-score, confidence interval, super).
  """
  gtc  = gather_tweet_counts(delta, seeds, group, category)
  group_rankings = sorted(gtc.items(), key=lambda x: x[1], reverse=True)
  return group_rankings


def get_rankings(delta, seeds, groups, category=None):
  rankings = []
  aggregate_group = set()
  for group in groups:
    aggregate_group = aggregate_group.union(group)
    print 'aggregate group num users: %s' % len(aggregate_group)
    group_rankings = get_rankings_for_group(delta, seeds, aggregate_group, category)
    rankings.append(group_rankings)
  return rankings


def group_users(common_users, num_groups):
  """Groups users into 'newsaholic', 'active', and 'common' categories.
  
  Returns:
  """
  groups = [set() for i in range(num_groups)]
  copy_common_users = set(common_users)
  count = 0
  while len(copy_common_users) > 0:
    group = groups[count % num_groups]
    group.add(copy_common_users.pop())
    count += 1
  return groups
