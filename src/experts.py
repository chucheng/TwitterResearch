"""
This module handles selection of experts, as well as graph drawing and any other
operations involving the expert groups.

__author__ = 'Chris Moghbel (cmoghbel@cs.ucla.edu)'
"""
import Util

from datetime import timedelta
from math import sqrt

import matplotlib
matplotlib.use("Agg")
from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt
import matplotlib.axis

from constants import _TIMEDELTAS_FILE_URL_INDEX
from constants import _TIMEDELTAS_FILE_USER_ID_INDEX
from constants import _TIMEDELTAS_FILE_DELTA_INDEX
from constants import _TIMEDELTAS_FILE_CATEGORY_INDEX
from constants import _HITS_MISSES_FILE_USER_ID_INDEX
from constants import _HITS_MISSES_FILE_MISSES_INDEX
from constants import _HITS_MISSES_FILE_HITS_INDEX

_GRAPH_DIR = Util.get_graph_output_dir('FolkWisdom/')

_BETA = 2


def draw_precision_experts(market_precisions, expert_p_precisions,
                           expert_f_precisions, expert_c_precisions,
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

  expert_p_plot = axs.plot(expert_p_precisions, '--', linewidth=2)
  plots.append(expert_p_plot)
  expert_f_plot = axs.plot(expert_f_precisions, '-.', linewidth=2)
  plots.append(expert_f_plot)
  expert_c_plot = axs.plot(expert_c_precisions, ':', linewidth=2)
  plots.append(expert_c_plot)

  labels = ['Market', 'Experts (Precision)', 'Experts (F-score)',
            'Experts (CI)',]
  plt.legend(plots, labels, loc=0, ncol=2, columnspacing=0, handletextpad=0)

  plt.grid(True, which='major', linewidth=1)

  axs.yaxis.set_minor_locator(MultipleLocator(5))
  plt.grid(True, which='minor')

  plt.xlabel('Num Top News Picked')
  plt.ylabel('Precision (%)')

  with open(_GRAPH_DIR + run_params_str + '/precision_experts_%s.png'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + run_params_str + '/precision_experts_%s.eps'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='eps')

  plt.close()


def draw_precision_recall_experts(market_precisions, market_recalls,
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

  market_plot = axs.plot(market_recalls, market_precisions)
  plots.append(market_plot)

  expert_p_plot = axs.plot(expert_p_recalls, expert_p_precisions, '--',
                          linewidth=2)
  plots.append(expert_p_plot)
  expert_f_plot = axs.plot(expert_f_recalls, expert_f_precisions, '-.',
                          linewidth=2)
  plots.append(expert_f_plot)
  expert_c_plot = axs.plot(expert_c_recalls, expert_c_precisions, ':',
                          linewidth=2)
  plots.append(expert_c_plot)

  labels = ['Market', 'Experts (Precision)', 'Experts (F-score)',
            'Experts (CI)',]
  plt.legend(plots, labels, loc=0, ncol=2, columnspacing=0, handletextpad=0)

  max_x = max([max(market_recalls), max(expert_p_recalls),
               max(expert_f_recalls), max(expert_c_recalls),])
  plt.axis([0, max_x + 5, 0, 105])
  plt.grid(True, which='major', linewidth=1)

  axs.xaxis.set_minor_locator(MultipleLocator(5))
  axs.yaxis.set_minor_locator(MultipleLocator(5))
  plt.grid(True, which='minor')

  plt.xlabel('Recall (%)')
  plt.ylabel('Precision (%)')

  with open(_GRAPH_DIR + run_params_str + '/precision_recall_experts_%s.png'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + run_params_str + '/precision_recall_experts_%s.eps'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='eps')

  plt.close()


def gather_tweet_counts(hours, seeds, experts_precision, experts_fscore,
                        experts_ci, super_experts, category=None):
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
  experts_precision_tc = {}
  experts_fscore_tc = {}
  experts_ci_tc = {}
  experts_s_tc = {}
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
        if Util.is_in_testing_set(seed_time):

          if time_delta < max_delta:

            category_matches = True
            if category:
              category_matches = False
              url_category = tokens[_TIMEDELTAS_FILE_CATEGORY_INDEX].strip()
              if url_category == category:
                category_matches = True
             
            if category_matches:

              if user_id in experts_precision:
                if url in experts_precision_tc:
                  experts_precision_tc[url] += 1
                else:
                  experts_precision_tc[url] = 1

              if user_id in experts_fscore:
                if url in experts_fscore_tc:
                  experts_fscore_tc[url] += 1
                else:
                  experts_fscore_tc[url] = 1

              if user_id in experts_ci:
                if url in experts_ci_tc:
                  experts_ci_tc[url] += 1
                else:
                  experts_ci_tc[url] = 1

              if user_id in super_experts:
                if url in experts_s_tc:
                  experts_s_tc[url] += 1
                else:
                  experts_s_tc[url] = 1

                
  return experts_precision_tc, experts_fscore_tc, experts_ci_tc, experts_s_tc


def get_rankings(delta, seeds, experts_precision, experts_fscore, experts_ci,
                 super_experts, category=None):
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
  eptc, eftc, ecitc, setc = gather_tweet_counts(delta, seeds, experts_precision,
                                                experts_fscore, experts_ci,
                                                super_experts, category)
  expert_precision_rankings = sorted(eptc.items(), key=lambda x: x[1],
                                     reverse=True)
  expert_fscore_rankings = sorted(eftc.items(), key=lambda x: x[1],
                                  reverse=True)
  expert_ci_rankings = sorted(ecitc.items(), key=lambda x: x[1], reverse=True)
  expert_s_rankings = sorted(setc.items(), key=lambda x: x[1], reverse=True)
  return (expert_precision_rankings, expert_fscore_rankings,
          expert_ci_rankings, expert_s_rankings)


def select_experts_ci(num_users, delta, size_experts, category=None):
  """Selects a set of experts via confidence interval strategy.

  Keyword Arguments:
  num_users -- The size of the total number of users.
  category -- The category to find experts for, None if for all news.

  Returns:
  experts -- A set of experts chosen by confidence interval method
             for given category.
  """
  users = {}
  input_file = ('../data/FolkWisdom/user_hits_and_misses_%s_%s.tsv'
                % (delta, category))

  with open(input_file) as input_file:
    for line in input_file:
      tokens = line.split('\t')
      user_id = tokens[_HITS_MISSES_FILE_USER_ID_INDEX]
      # num_users += 1
      hits = int(tokens[_HITS_MISSES_FILE_HITS_INDEX])
      misses = int(tokens[_HITS_MISSES_FILE_MISSES_INDEX])
      trials = hits + misses
      p_val = float(hits + 2) / (trials + 4)
      error = 1.96 * sqrt((p_val * (1 - p_val)) / float(trials + 4))
      low = max(0.0, p_val - error)
      high = min(1.0, p_val + error)
      avg_of_ci = (low + high) / 2.0
      users[user_id] = avg_of_ci
  users_sorted = sorted(users.items(), key=lambda x: x[1], reverse=True)
  num_experts_to_select = int(num_users * size_experts)
  experts = set()
  for i in range(0, num_experts_to_select):
    user_id, _ = users_sorted[i]
    experts.add(user_id)
  return experts


def select_experts_fscore(size_target_news, num_users, delta, size_experts,
                          category=None):
  """Selects a set of experts via F-score strategy.

  Keyword Arguments:
  num_users -- The size of the total number of users.
  category -- The category to find experts for, None if for all news.

  Returns:
  experts -- A set of experts chosen by F-score method
             for given category.
  """
  users = {}
  input_file = ('../data/FolkWisdom/user_hits_and_misses_%s_%s.tsv'
                % (delta, category))

  with open(input_file) as input_file:
    for line in input_file:
      tokens = line.split('\t')
      user_id = tokens[_HITS_MISSES_FILE_USER_ID_INDEX]
      hits = int(tokens[_HITS_MISSES_FILE_HITS_INDEX])
      misses = int(tokens[_HITS_MISSES_FILE_MISSES_INDEX])
      precision = float(hits) / (hits + misses)
      recall = float(hits) / size_target_news
      f_score = (1 + _BETA**2)
      # Make sure to do this only if we will have a non-zero denominator.
      if not precision == 0 or not recall == 0:
        f_score *= ((precision * recall) / ((_BETA**2 * precision) + recall))
      else:
        f_score = 0.0
      users[user_id] = f_score
  users_sorted = sorted(users.items(), key=lambda x: x[1], reverse=True)
  num_experts_to_select = int(num_users * size_experts)
  experts = set()
  for i in range(0, num_experts_to_select):
    user_id, _ = users_sorted[i]
    experts.add(user_id)
  return experts


def select_experts_precision(valid_users, num_users, delta, size_experts,
                             category=None):
  """Selects a set of experts via precision strategy.

  Keyword Arguments:
  num_users -- The size of the total number of users.
  category -- The category to find experts for, None if for all news.

  Returns:
  experts -- A set of experts chosen by precision method
             for given category.
  """
  users = {}
  input_file = ('../data/FolkWisdom/user_hits_and_misses_%s_%s.tsv'
                % (delta, category))

  with open(input_file) as input_file:
    for line in input_file:
      tokens = line.split('\t')
      user_id = tokens[_HITS_MISSES_FILE_USER_ID_INDEX]
      # num_users += 1
      if user_id in valid_users:
        hits = int(tokens[_HITS_MISSES_FILE_HITS_INDEX])
        misses = int(tokens[_HITS_MISSES_FILE_MISSES_INDEX])
        precision = float(hits) / (hits + misses)
        users[user_id] = (precision, hits + misses)
  us_secondary = sorted(users.items(), key=lambda x: x[1][1], reverse=True)
  users_sorted = sorted(us_secondary, key=lambda x: x[1][0], reverse=True)
  num_experts_to_select = int(num_users * size_experts)
  experts = set()
  for i in range(0, num_experts_to_select):
    user_id, _ = users_sorted[i]
    experts.add(user_id)
  return experts


def select_super_experts(experts_precision, experts_fscore, experts_ci):
  """Selects super experts group.

  Keyword Arguments:
  experts_precision -- (Set) The precision based expert group.
  experts_fscore -- (Set) The fscore based expert group.
  experts_ci -- (Set) The confidence interval based expert group.
  """
  return experts_precision.intersection(experts_fscore).intersection(experts_ci)
