"""
This module performs an analysis on determining which group can perform better
at ranking when compared to the ground truth. Some definitions which apply
throughout this analysis:

ground_truth -- Determined as the ranking after summing up the tweet counts for
all four months.

market -- Defined as all users.

newsaholics -- Defined as the top 2% of active users when ranked by the rate at
which they tweet.

active_users -- Defined as users between 2% and 25% when ranked by the rate at
which they tweet.

common_users -- Defined as users ranked more than 25% when ranked by the rate
at which they tweet.

There are also 4 groups of experts, selected by precision, F-score, and
confidence interval methods described in wiki and in paper. The fourth expert
group, super experts, is defined as the intersection of the other 3.

Tweet counts for the user groups (market, newsaholics, active users, and common
users) are counted if they occur within a certain time delta of the original
introduction of that url.

__author__ = 'Chris Moghbel (cmoghbel@cs.ucla.edu)'
"""
import FileLog
import Util

import matplotlib
matplotlib.use("Agg")

from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt
import matplotlib.axis

from datetime import datetime
from datetime import timedelta
import math
from math import sqrt


_BETA = 2

_SIZE_EXPERTS = .10
_SIZE_TOP_NEWS = .02 # This is reset at the beginning of run.

_HITS_MISSES_FILE_USER_ID_INDEX = 0
_HITS_MISSES_FILE_HITS_INDEX = 1
_HITS_MISSES_FILE_MISSES_INDEX = 2

_USER_ACTIVITY_FILE_ID_INDEX = 0
_USER_ACTIVITY_FILE_COUNT_INDEX = 1

_TIMEDELTAS_FILE_TWEET_ID_INDEX = 0
_TIMEDELTAS_FILE_USER_ID_INDEX = 1 
_TIMEDELTAS_FILE_DELTA_INDEX = 2
_TIMEDELTAS_FILE_URL_INDEX = 3
_TIMEDELTAS_FILE_CATEGORY_INDEX = 4

_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

_GRAPH_DIR = Util.get_graph_output_dir('FolkWisdom/')
_LOG_FILE = 'aFolkWisdom.log'

_DELTAS = [] # Given in hours.
_DELTAS.append(1)
_DELTAS.append(4)
_DELTAS.append(8)

_CATEGORIES = []
# Comment categories in/out individually as needed.
_CATEGORIES.append(None)
_CATEGORIES.append('world')
# _CATEGORIES.append('business')
# _CATEGORIES.append('opinion')
_CATEGORIES.append('sports')
# _CATEGORIES.append('us')
_CATEGORIES.append('technology')
# _CATEGORIES.append('movies')


def calculate_diff_avg(ground_truth_url_to_rank, other_rank_to_url):
  """Calculates the average of the difference in rank from the truth.
  
  Keyword Arguments:
  ground_truth_url_to_rank -- Dictionary mapping url to true rank.
  other_rank_to_url -- Dictionary mapping some non-truth ranking to url.
  
  Returns:
  avg_diffs: A list of avg_diff, for each number of news chosen.
  """
  num_gt = len(ground_truth_url_to_rank.keys())
  num_other = len(other_rank_to_url.keys())
  max_num_news_to_consider = min(int(num_gt * _SIZE_TOP_NEWS), num_other)
  avg_diffs = []
  for i in range(1, max_num_news_to_consider):
    diff_sum = 0
    for j in range(0, i):
      other_rank = j + 1
      url = other_rank_to_url[other_rank]
      gt_rank = ground_truth_url_to_rank[url]
      diff = (other_rank - gt_rank)**2 
      diff_sum += diff
    diff_avg = sqrt(diff_sum) / i
    avg_diffs.append(diff_avg)
  
  return avg_diffs


def calc_precision_recall(gt_rankings, other_rankings):
  """Calculates the precision recall scores for a set of rankings against truth.

  Keyword Arguments:
  gt_rankings -- A list of (url, count) pairs representing the ground truth
                 rankings.
  other_rankings -- A list of (url, count) pairs representing the other
                    rankings.

  Returns:
  precisions -- A list of precisions, with the index equal to the number of
                'guesses'.
  recalls -- A list of recalls, with the index equal to the number of 'guesses'.
  """
  size_target_news = int(len(gt_rankings) * _SIZE_TOP_NEWS)
  max_num_news_to_consider = min(len(other_rankings),
                                 int(len(gt_rankings) * _SIZE_TOP_NEWS))
  target_news = set()
  for i in range(size_target_news):
    (url, _) = gt_rankings[i]
    target_news.add(url)

  precisions = []
  recalls = []
  # Increase # guesses from 1 to max_number
  for num_guesses in range(1, max_num_news_to_consider + 1):
    # for each guess, check if it's a hit
    hits = 0.0
    misses = 0.0
    for j in range(0, num_guesses):
      (url, _) = other_rankings[j]
      if url in target_news:
        hits += 1
      else:
        misses += 1
    precision = (hits / (hits + misses)) * 100.0
    recall = (hits / len(target_news)) * 100.0
    precisions.append(precision)
    recalls.append(recall)
  return precisions, recalls


def draw_avg_diff_graph(newsaholic_diffs, market_diffs, active_diffs,
                        common_diffs, expert_p_diffs, expert_f_diffs,
                        expert_c_diffs, expert_s_diffs, delta, category):
  """Draws the graph for avg diffs.
  
  Keyword Arguments:
  Accepts a list of diffs for each of the following user groups:
  newsaholics, market, active users, common_users, and experts
  (precision, F-score, confidence interval, and super) for 8 lists
  in total.
  delta -- The delta timewindow for voting that was used.
  category -- The category we are analysing.
  """
  plots = []
  figure = plt.figure()
  ax = figure.add_subplot(111)

  market_plot = ax.plot([i for i in range(1, len(market_diffs) + 1)],
                        market_diffs)
  plots.append(market_plot)

  newsaholic_plot = ax.plot([i for i in range(1, len(newsaholic_diffs) + 1)],
                        newsaholic_diffs)
  plots.append(newsaholic_plot)

  active_plot = ax.plot([i for i in range(1, len(active_diffs) + 1)],
                        active_diffs)
  plots.append(active_plot)

  common_plot = ax.plot([i for i in range(1, len(common_diffs) + 1)],
                        common_diffs)
  plots.append(common_plot)

  expert_p_plot = ax.plot([i for i in range(1, len(expert_p_diffs) + 1)],
                          expert_p_diffs)
  plots.append(expert_p_plot)
  expert_f_plot = ax.plot([i for i in range(1, len(expert_f_diffs) + 1)],
                          expert_f_diffs)
  plots.append(expert_f_plot)
  expert_c_plot = ax.plot([i for i in range(1, len(expert_c_diffs) + 1)],
                          expert_c_diffs)
  plots.append(expert_c_plot)
  expert_s_plot = ax.plot([i for i in range(1, len(expert_s_diffs) + 1)],
                          expert_s_diffs, '--')
  plots.append(expert_s_plot)


  labels = ['Market', 'News-aholics', 'Active Users', 'Common Users',
            'Experts (Precision)', 'Experts (F-score)', 'Experts (CI)',
            'Super Experts']
  plt.legend(plots, labels, loc=0, ncol=2, columnspacing=0, handletextpad=0)

  max_y = max([max(market_diffs), max(newsaholic_diffs), max(active_diffs),
               max(common_diffs), max(expert_p_diffs), max(expert_f_diffs),
               max(expert_c_diffs), max(expert_s_diffs)])
  plt.axis([1, len(newsaholic_diffs) + 1, 0, max_y])
  plt.grid(True, which='major', linewidth=1)

  ax.xaxis.set_minor_locator(MultipleLocator(100))
  minor_locator = int(math.log(max_y))
  if minor_locator % 2 == 1:
    minor_locator += 1
  ax.yaxis.set_minor_locator(MultipleLocator(minor_locator))
  plt.grid(True, which='minor')

  plt.xlabel('Top X Stories Compared')
  plt.ylabel('Average Differnce in Ranking')
  plt.title('Ranking Performance by User Group with %s Hour Delta (%s)'
             % (delta, category))

  run_params_str = 'd%s_t%s_e%s_%s' % (delta, int(_SIZE_TOP_NEWS * 100),
                                       int(_SIZE_EXPERTS * 100), category)
  with open(_GRAPH_DIR + run_params_str + '/ranking_performance_%s.png'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + run_params_str + '/ranking_performance_%s.eps'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='eps')

  log('Outputted graph: Ranking Performance by User Group with '
      '%s Hour Delta (%s)' % (delta, category))
  plt.close()


def draw_precision_recall_graph(market_precisions, market_recalls,
                                newsaholic_precisions, newsaholic_recalls,
                                active_precisions, active_recalls,
                                common_precisions, common_recalls,
                                expert_p_precisions, expert_p_recalls,
                                expert_f_precisions, expert_f_recalls,
                                expert_c_precisions, expert_c_recalls,
                                expert_s_precisions, expert_s_recalls,
                                delta, category):
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
  ax = figure.add_subplot(111)

  market_plot = ax.plot(market_recalls, market_precisions)
  plots.append(market_plot)

  # Groups
  newsaholic_plot = ax.plot(newsaholic_recalls, newsaholic_precisions, '--',
                            linewidth=2)
  plots.append(newsaholic_plot)
  active_plot = ax.plot(active_recalls, active_precisions, ':',
                        linewidth=2)
  plots.append(active_plot)
  common_plot = ax.plot(common_recalls, common_precisions, '-.',
                        linewidth=2)
  plots.append(common_plot)

  # Experts
  expert_p_plot = ax.plot(expert_p_recalls, expert_p_precisions, '--',
                          linewidth=2)
  plots.append(expert_p_plot)
  expert_f_plot = ax.plot(expert_f_recalls, expert_f_precisions, '-.',
                          linewidth=2)
  plots.append(expert_f_plot)
  expert_c_plot = ax.plot(expert_c_recalls, expert_c_precisions, ':',
                          linewidth=2)
  plots.append(expert_c_plot)
  expert_s_plot = ax.plot(expert_s_recalls, expert_s_precisions, ':',
                          linewidth=2)
  plots.append(expert_s_plot)

  labels = ['Market',
            'News-aholics', 'Active Users', 'Common Users',
            'Experts (Precision)', 'Experts (F-score)', 'Experts (CI)',
            'Super Experts']
  plt.legend(plots, labels, loc=0, ncol=2, columnspacing=0, handletextpad=0)

  max_x = max([max(market_recalls),
               max(newsaholic_recalls), max(active_recalls),
               max(common_recalls), max(expert_p_recalls),
               max(expert_f_recalls), max(expert_c_recalls),
               max(expert_s_recalls)])
  plt.axis([0, max_x + 5, 0, 105])
  plt.grid(True, which='major', linewidth=1)

  ax.xaxis.set_minor_locator(MultipleLocator(5))
  ax.yaxis.set_minor_locator(MultipleLocator(5))
  plt.grid(True, which='minor')

  plt.xlabel('Recall (%)')
  plt.ylabel('Precision (%)')

  run_params_str = 'd%s_t%s_e%s_%s' % (delta, int(_SIZE_TOP_NEWS * 100),
                                       int(_SIZE_EXPERTS * 100), category)
  with open(_GRAPH_DIR + run_params_str + '/precision_recall_all_%s.png'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + run_params_str + '/precision_recall_all_%s.eps'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='eps')

  log('Outputted graph: Precision vs Recall for Groups and Experts with '
      '%s Hour Delta (%s)' % (delta, category))
  plt.close()


def draw_precision_recall_graph_experts(market_precisions, market_recalls,
                                        expert_p_precisions, expert_p_recalls,
                                        expert_f_precisions, expert_f_recalls,
                                        expert_c_precisions, expert_c_recalls,
                                        delta, category):
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
  ax = figure.add_subplot(111)

  market_plot = ax.plot(market_recalls, market_precisions)
  plots.append(market_plot)

  expert_p_plot = ax.plot(expert_p_recalls, expert_p_precisions, '--',
                          linewidth=2)
  plots.append(expert_p_plot)
  expert_f_plot = ax.plot(expert_f_recalls, expert_f_precisions, '-.',
                          linewidth=2)
  plots.append(expert_f_plot)
  expert_c_plot = ax.plot(expert_c_recalls, expert_c_precisions, ':',
                          linewidth=2)
  plots.append(expert_c_plot)

  labels = ['Market', 'Experts (Precision)', 'Experts (F-score)',
            'Experts (CI)',]
  plt.legend(plots, labels, loc=0, ncol=2, columnspacing=0, handletextpad=0)

  max_x = max([max(market_recalls), max(expert_p_recalls),
               max(expert_f_recalls), max(expert_c_recalls),])
  plt.axis([0, max_x + 5, 0, 105])
  plt.grid(True, which='major', linewidth=1)

  ax.xaxis.set_minor_locator(MultipleLocator(5))
  ax.yaxis.set_minor_locator(MultipleLocator(5))
  plt.grid(True, which='minor')

  plt.xlabel('Recall (%)')
  plt.ylabel('Precision (%)')

  run_params_str = 'd%s_t%s_e%s_%s' % (delta, int(_SIZE_TOP_NEWS * 100),
                                       int(_SIZE_EXPERTS * 100), category)
  with open(_GRAPH_DIR + run_params_str + '/precision_recall_experts_%s.png'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + run_params_str + '/precision_recall_experts_%s.eps'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='eps')

  log('Outputted graph: Precision vs Recall by Expert Group with '
      '%s Hour Delta (%s)' % (delta, category))
  plt.close()


def draw_precision_recall_graph_groups(market_precisions, market_recalls,
                                       newsaholic_precisions,
                                       newsaholic_recalls, active_precisions,
                                       active_recalls, common_precisions,
                                       common_recalls, delta, category):
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
  ax = figure.add_subplot(111)

  market_plot = ax.plot(market_recalls, market_precisions)
  plots.append(market_plot)

  newsaholic_plot = ax.plot(newsaholic_recalls, newsaholic_precisions, '--',
                            linewidth=2)
  plots.append(newsaholic_plot)

  active_plot = ax.plot(active_recalls, active_precisions, ':',
                        linewidth=2)
  plots.append(active_plot)

  common_plot = ax.plot(common_recalls, common_precisions, '-.',
                        linewidth=2)
  plots.append(common_plot)


  labels = ['Market', 'News-aholics', 'Active Users', 'Common Users',]
  plt.legend(plots, labels, loc=0, ncol=2, columnspacing=0, handletextpad=0)

  max_x = max([max(market_recalls), max(newsaholic_recalls),
               max(active_recalls), max(common_recalls)])
  plt.axis([0, max_x + 5, 0, 105])
  plt.grid(True, which='major', linewidth=1)

  ax.xaxis.set_minor_locator(MultipleLocator(5))
  ax.yaxis.set_minor_locator(MultipleLocator(5))
  plt.grid(True, which='minor')

  plt.xlabel('Recall (%)')
  plt.ylabel('Precision (%)')

  run_params_str = 'd%s_t%s_e%s_%s' % (delta, int(_SIZE_TOP_NEWS * 100),
                                       int(_SIZE_EXPERTS * 100), category)
  with open(_GRAPH_DIR + run_params_str + '/precision_recall_groups_%s.png'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + run_params_str + '/precision_recall_groups_%s.eps'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='eps')

  log('Outputted graph: Precision vs Recall by User Group with '
      '%s Hour Delta (%s)' % (delta, category))
  plt.close()


def gather_tweet_counts(hours, seeds, newsaholics, active, experts_precision,
                        experts_fscore, experts_ci, super_experts,
                        category=None):
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
        seed_time = seeds[url]
        if is_in_testing_set(seed_time):


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

                
  return (market_tweet_counts, newsaholic_tweet_counts, active_tweet_counts,
          common_tweet_counts, experts_precision_tc, experts_fscore_tc,
          experts_ci_tc, experts_s_tc)


def get_rankings(delta, seeds, newsaholics, active_users, experts_precision,
                 experts_fscore, experts_ci, super_experts, category=None):
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
  log('Getting Rankings')
  (mtc, etc, atc, ctc,
   eptc, eftc, ecitc, setc) = gather_tweet_counts(delta, seeds, newsaholics,
                                                  active_users,
                                                  experts_precision,
                                                  experts_fscore,
                                                  experts_ci, super_experts,
                                                  category)
  market_rankings = sorted(mtc.items(), key=lambda x: x[1], reverse=True)
  newsaholic_rankings = sorted(etc.items(), key=lambda x: x[1], reverse=True)
  active_rankings = sorted(atc.items(), key=lambda x: x[1], reverse=True)
  common_rankings = sorted(ctc.items(), key=lambda x: x[1], reverse=True)
  expert_precision_rankings = sorted(eptc.items(), key=lambda x: x[1],
                                     reverse=True)
  expert_fscore_rankings = sorted(eftc.items(), key=lambda x: x[1],
                                  reverse=True)
  expert_ci_rankings = sorted(ecitc.items(), key=lambda x: x[1], reverse=True)
  expert_s_rankings = sorted(setc.items(), key=lambda x: x[1], reverse=True)
  return (market_rankings, newsaholic_rankings, active_rankings,
          common_rankings, expert_precision_rankings, expert_fscore_rankings,
          expert_ci_rankings, expert_s_rankings)


def get_gt_rankings(seeds, category=None):
  """Generate the ground truth rankings.
  
  Keyword Arguments:
  seeds -- Dictionary of url to first time seen.
  category -- Category to generate ground truths for, None for all news.

  Returns:
  gt_rankings -- A list of (url, count) pairs in ranked order.
  """
  log('Getting ground truth rankings.')
  gt_tweet_counts = {}
  with open('../data/FolkWisdom/time_deltas.tsv') as input_file:
    for line in input_file:
      tokens = line.split('\t')
      url = tokens[_TIMEDELTAS_FILE_URL_INDEX]
      if url in seeds:
        seed_time = seeds[url]
        if is_in_testing_set(seed_time):
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


def select_experts_confidence_interval(num_users, delta, category=None):
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
    log('Selecting experts via CI method for delta %s and cateogry %s.'
        % (delta, category))
    for line in input_file:
      tokens = line.split('\t')
      user_id = tokens[_HITS_MISSES_FILE_USER_ID_INDEX]
      # num_users += 1
      hits = int(tokens[_HITS_MISSES_FILE_HITS_INDEX])
      misses = int(tokens[_HITS_MISSES_FILE_MISSES_INDEX])
      trials = hits + misses
      p = float(hits + 2) / (trials + 4)
      error = 1.96 * sqrt((p * (1 - p)) / float(trials + 4))
      low = max(0.0, p - error)
      high = min(1.0, p + error)
      avg_of_ci = (low + high) / 2.0
      users[user_id] = avg_of_ci
  users_sorted = sorted(users.items(), key=lambda x: x[1], reverse=True)
  num_experts_to_select = int(num_users * _SIZE_EXPERTS)
  experts = set()
  for i in range(0, num_experts_to_select):
    user_id, _ = users_sorted[i]
    experts.add(user_id)
  return experts


def select_experts_fscore(size_target_news, num_users, delta, category=None):
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
    log('Selecting experts via F_score method for delta %s and category %s.'
        % (delta, category))
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
  num_experts_to_select = int(num_users * _SIZE_EXPERTS)
  experts = set()
  for i in range(0, num_experts_to_select):
    user_id, _ = users_sorted[i]
    experts.add(user_id)
  return experts


def select_experts_precision(valid_users, num_users, delta, category=None):
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
    log('Selecting experts via precision method for delta %s and category %s.'
        % (delta, category))
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
  log('Num Users (2): %s' % len(users_sorted))
  num_experts_to_select = int(num_users * _SIZE_EXPERTS)
  experts = set()
  for i in range(0, num_experts_to_select):
    user_id, _ = users_sorted[i]
    experts.add(user_id)
  return experts


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
  log('Grouping Users')
  user_ids_sorted = []
  input_file = '../data/FolkWisdom/user_activity_%s_%s.tsv' % (delta, category)
  with open(input_file) as input_file:
    for line in input_file:
      tokens = line.split('\t')
      user_id = tokens[_USER_ACTIVITY_FILE_ID_INDEX]
      user_ids_sorted.append(user_id)
  num_users = len(user_ids_sorted)
  log('Num users (grouping): %s' % num_users)
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


def load_seeds():
  """Loads the set of seed times for urls from file."""
  log('Loading seeds.')
  seeds = {}
  with open('../data/FolkWisdom/seed_times.tsv') as input_file:
    for line in input_file:
      tokens = line.split('\t')
      url = tokens[3].strip()
      seed_time = datetime.strptime(tokens[2], _DATETIME_FORMAT)
      seeds[url] = seed_time
  return seeds


def is_in_testing_set(date_time):
  """Checks where a datetime is within the testing set.

  Keyword Arguments:
  date_time: A datetime object.

  Returns:
  True if the datetime object is within the testing set window, False otherwise.
  """
  if (date_time >= datetime(year=2011, month=11, day=1)
      and date_time < datetime(year=2012, month=1, day=1)):
    return True
  return False


def run():
  """Contains the main logic for this analysis."""
  global _SIZE_TOP_NEWS
  FileLog.set_log_dir()

  seeds = load_seeds()
  for category in _CATEGORIES:
    if category:
      _SIZE_TOP_NEWS = .10
    else:
      _SIZE_TOP_NEWS = .02

    log('Preforming analysis for category: %s' % category)
    gt_rankings = get_gt_rankings(seeds, category)
    log('Num ground_truth_rankings: %s' % len(gt_rankings))
    ground_truth_url_to_rank = {}
    for rank, (url, count) in enumerate(gt_rankings):
      ground_truth_url_to_rank[url] = rank
    size_target_news = int(len(gt_rankings) * _SIZE_TOP_NEWS)
    log('Size target_news: %s' % size_target_news)

    for delta in _DELTAS:
      num_users, newsaholics, active_users, common_users = group_users(delta,
                                                                       category)
      log('Num newsaholics: %s' % len(newsaholics))
      log('Num active: %s' % len(active_users))
      log('Num common: %s' % len(common_users))

      experts_precision = select_experts_precision(
          newsaholics.union(active_users), num_users, delta, category)
      experts_fscore = select_experts_fscore(size_target_news, num_users,
                                             delta, category)
      experts_ci = select_experts_confidence_interval(num_users, delta,
                                                      category)
      super_experts = experts_precision.intersection(
          experts_fscore).intersection(experts_ci)

      log('Num experts (precision): %s' % len(experts_precision))
      log('Num experts (fscore): %s' % len(experts_fscore))
      log('Num experts (ci): %s' % len(experts_ci))
      log('Num Super Experts: %s' %len(super_experts))

      run_params_str = 'd%s_t%s_e%s_%s' % (delta, int(_SIZE_TOP_NEWS * 100),
                                           int(_SIZE_EXPERTS * 100), category)
      info_output_dir = '../graph/FolkWisdom/%s/info/' % run_params_str
      Util.ensure_dir_exist(info_output_dir)

      log('Finding rankings with an %s hour delta.' % delta)
      (market_rankings, newsaholic_rankings, active_rankings,
      common_rankings, expert_precision_rankings, expert_fscore_rankings,
      expert_ci_rankings, expert_s_rankings) = get_rankings(delta, seeds, 
                                                            newsaholics,
                                                            active_users,
                                                            experts_precision,
                                                            experts_fscore,
                                                            experts_ci,
                                                            super_experts,
                                                            category)

      num_votes_market = 0
      for url, count in market_rankings:
        num_votes_market += count
      log('Num market rankings: %s' % len(market_rankings))
      log('Num market votes: %s' % num_votes_market)
      num_votes_newsaholics = 0
      for url, count in newsaholic_rankings:
        num_votes_newsaholics += count
      log('Num newsaholic rankings: %s' % len(newsaholic_rankings))
      log('Num newsaholic votes: %s' % num_votes_newsaholics)
      num_votes_active = 0
      for url, count in active_rankings:
        num_votes_active += count
      log('Num active_rankings: %s' % len(active_rankings))
      log('Num active votes: %s' % num_votes_active)
      num_votes_common = 0
      for url, count in common_rankings:
        num_votes_common += count
      log('Num common_rankings: %s' % len(common_rankings))
      log('Num common votes: %s' % num_votes_common)
      num_votes_expert_precision = 0
      for url, count in expert_precision_rankings:
        num_votes_expert_precision += count
      log('Num expert_precision rankings: %s' % len(expert_precision_rankings))
      log('Num expert_precision votes: %s' % num_votes_expert_precision)
      num_votes_expert_fscore = 0
      for url, count in expert_fscore_rankings:
        num_votes_expert_fscore += count
      log('Num expert_fscore rankings: %s' % len(expert_fscore_rankings))
      log('Num expert_fscore votes: %s' % num_votes_expert_fscore)
      num_votes_expert_ci = 0
      for url, count in expert_ci_rankings:
        num_votes_expert_ci += count
      log('Num expert_ci rankings: %s' % len(expert_ci_rankings))
      log('Num expert_ci votes: %s' % num_votes_expert_ci)
      num_votes_expert_s = 0
      for url, count in expert_s_rankings:
        num_votes_expert_s += count
      log('Num expert_s rankings: %s' % len(expert_s_rankings))
      log('Num expert_s votes: %s' % num_votes_expert_s)


      size_market_unfiltered = '0'
      with open('../data/FolkWisdom/size_of_market_unfiltered.txt') as in_file:
        size_market_unfiltered = in_file.readline().strip()

      with open('%suser_demographics_%s.txt'
                % (info_output_dir, run_params_str), 'w') as output_file:
        output_file.write('Number of Newsaholics: %s\n' % len(newsaholics))
        output_file.write('Number of Active Users: %s\n' % len(active_users))
        output_file.write('Number of Common Users: %s\n' % len(common_users))
        output_file.write('Number of Experts: %s\n' % len(experts_precision))
        output_file.write('Number of Super Experts: %s\n' % len(super_experts))
        output_file.write('Number of Users (Total): %s\n'
                          % (len(newsaholics) + len(active_users)
                             + len(common_users)))
        output_file.write('Size of market (unfiltered): %s\n'
                          % size_market_unfiltered)
        output_file.write('\n')
        output_file.write('Number of votes by Newsaholics: %s\n'
                          % num_votes_newsaholics)
        output_file.write('Number of votes by Market: %s\n' % num_votes_market)
        output_file.write('Number of votes by Active Users: %s\n'
                          % num_votes_active)
        output_file.write('Number of votes by Common Users: %s\n'
                          % num_votes_common)
        output_file.write('Number of votes by Expert (Precision) Users: %s\n'
                % num_votes_expert_precision) 
        output_file.write('Number of votes by Expert (fscore) Users: %s\n'
                % num_votes_expert_fscore) 
        output_file.write('Number of votes by Expert (ci) Users: %s\n'
                % num_votes_expert_ci) 
        output_file.write('Number of votes by Super Experts: %s\n'
                          % num_votes_expert_s)
        output_file.write('Total Number of votes cast: %s\n'
                          % (num_votes_newsaholics + num_votes_active
                             + num_votes_common))
        output_file.write('\n')
        output_file.write('Total Number of Good News: %s\n' % size_target_news)

      log('Ground Truth Top 5')
      for i in range(min(len(gt_rankings), 5)):
        url, count = gt_rankings[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
      log('-----------------------------------')
      log('Market Top 5')
      for i in range(min(len(market_rankings), 5)):
        url, count = market_rankings[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
      log('-----------------------------------')
      log('Newsaholic Top 5')
      for i in range(min(len(newsaholic_rankings), 5)):
        url, count = newsaholic_rankings[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
      log('-----------------------------------')
      log('Active Top 5')
      for i in range(min(len(active_rankings), 5)):
        url, count = active_rankings[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
      log('-----------------------------------')
      log('Common Top 5')
      for i in range(min(len(common_rankings), 5)):
        url, count = common_rankings[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
      log('-----------------------------------')
      log('Expert (Precision) Top 5')
      for i in range(min(len(expert_precision_rankings), 5)):
        url, count = expert_precision_rankings[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
      log('-----------------------------------')
      log('Expert (fscore) Top 5')
      for i in range(min(len(expert_fscore_rankings), 5)):
        url, count = expert_fscore_rankings[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
      log('-----------------------------------')
      log('Expert (ci) Top 5')
      for i in range(min(len(expert_ci_rankings), 5)):
        url, count = expert_ci_rankings[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
      log('-----------------------------------')
      log('Super Expert Top 5')
      for i in range(min(len(expert_s_rankings), 5)):
        url, count = expert_s_rankings[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
        
      market_rank_to_url = {}
      newsaholic_rank_to_url = {}
      active_rank_to_url = {}
      common_rank_to_url = {}
      expert_p_rank_to_url = {}
      expert_f_rank_to_url = {}
      expert_c_rank_to_url = {}
      expert_s_rank_to_url = {}
      for rank, (url, count) in enumerate(newsaholic_rankings):
        newsaholic_rank_to_url[rank] = url
      for rank, (url, count) in enumerate(market_rankings):
        market_rank_to_url[rank] = url
      for rank, (url, count) in enumerate(active_rankings):
        active_rank_to_url[rank] = url
      for rank, (url, count) in enumerate(common_rankings):
        common_rank_to_url[rank] = url
      for rank, (url, count) in enumerate(expert_precision_rankings):
        expert_p_rank_to_url[rank] = url
      for rank, (url, count) in enumerate(expert_fscore_rankings):
        expert_f_rank_to_url[rank] = url
      for rank, (url, count) in enumerate(expert_ci_rankings):
        expert_c_rank_to_url[rank] = url
      for rank, (url, count) in enumerate(expert_s_rankings):
        expert_s_rank_to_url[rank] = url

      avg_diffs_newsaholic = calculate_diff_avg(ground_truth_url_to_rank,
                                            newsaholic_rank_to_url)
      avg_diffs_market = calculate_diff_avg(ground_truth_url_to_rank,
                                            market_rank_to_url)
      avg_diffs_active = calculate_diff_avg(ground_truth_url_to_rank,
                                            active_rank_to_url)
      avg_diffs_common = calculate_diff_avg(ground_truth_url_to_rank,
                                            common_rank_to_url)

      avg_diffs_expert_p = calculate_diff_avg(ground_truth_url_to_rank,
                                              expert_p_rank_to_url)
      avg_diffs_expert_f = calculate_diff_avg(ground_truth_url_to_rank,
                                              expert_f_rank_to_url)
      avg_diffs_expert_c = calculate_diff_avg(ground_truth_url_to_rank,
                                              expert_c_rank_to_url)
      avg_diffs_expert_s = calculate_diff_avg(ground_truth_url_to_rank,
                                              expert_s_rank_to_url)

      draw_avg_diff_graph(avg_diffs_newsaholic, avg_diffs_market,
                          avg_diffs_active, avg_diffs_common,
                          avg_diffs_expert_p, avg_diffs_expert_f,
                          avg_diffs_expert_c, avg_diffs_expert_s, delta,
                          category)

      market_url_to_rank = {}
      precision_url_to_rank = {}
      fscore_url_to_rank = {}
      ci_url_to_rank = {}
      for rank, (url, count) in enumerate(market_rankings):
        market_url_to_rank[url] = rank
      for rank, (url, count) in enumerate(expert_precision_rankings):
        precision_url_to_rank[url] = rank
      for rank, (url, count) in enumerate(expert_fscore_rankings):
        fscore_url_to_rank[url] = rank
      for rank, (url, count) in enumerate(expert_ci_rankings):
        ci_url_to_rank[url] = rank
      with open('%sranking_comparisons_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as out_file:
        for gt_rank, (gt_url, gt_count) in enumerate(gt_rankings):
          market_rank = 0
          precision_rank = 0
          ci_rank = 0
          fscore_rank = 0
          if gt_url in market_url_to_rank:
            market_rank = market_url_to_rank[gt_url] + 1
          if gt_url in precision_url_to_rank:
            precision_rank = precision_url_to_rank[gt_url] + 1
          if gt_url in ci_url_to_rank:
            ci_rank = ci_url_to_rank[gt_url] + 1
          if gt_url in fscore_url_to_rank:
            fscore_rank = fscore_url_to_rank[gt_url] + 1
          line = '%s\t%s\t%s\t%s\t%s\t%s\n' % (gt_url, gt_rank + 1, market_rank,
                                               precision_rank, ci_rank,
                                               fscore_rank)
          out_file.write(line)


      with open('%sground_truth_rankings_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as output_file:
        for url, count in gt_rankings:
          output_file.write('%s\t%s\n' % (url.strip(), count))
      with open('%smarket_rankings_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as output_file:
        for rank, (url, count) in enumerate(market_rankings):
          output_file.write('%s\t%s\t(%s,%s)\n'
                            % (url.strip(), count, rank,
                               ground_truth_url_to_rank[url]))
      with open('%snewsaholic_rankings_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as output_file:
        for rank, (url, count) in enumerate(newsaholic_rankings):
          output_file.write('%s\t%s\t(%s,%s)\n'
                            % (url.strip(), count, rank,
                               ground_truth_url_to_rank[url]))
      with open('%sactive_user_rankings_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as output_file:
        for rank, (url, count) in enumerate(active_rankings):
          output_file.write('%s\t%s\t(%s,%s)\n'
                            % (url.strip(), count, rank,
                               ground_truth_url_to_rank[url]))
      with open('%scommon_user_rankings_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as output_file:
        for rank, (url, count) in enumerate(common_rankings):
          output_file.write('%s\t%s\t(%s,%s)\n'
                            % (url.strip(), count, rank,
                               ground_truth_url_to_rank[url]))
      with open('%sexpert_p_user_rankings_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as output_file:
        for rank, (url, count) in enumerate(expert_precision_rankings):
          output_file.write('%s\t%s\t(%s,%s)\n'
                            % (url.strip(), count, rank,
                               ground_truth_url_to_rank[url]))
      with open('%sexpert_f_user_rankings_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as output_file:
        for rank, (url, count) in enumerate(expert_fscore_rankings):
          output_file.write('%s\t%s\t(%s,%s)\n'
                            % (url.strip(), count, rank,
                               ground_truth_url_to_rank[url]))
      with open('%sexpert_c_user_rankings_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as output_file:
        for rank, (url, count) in enumerate(expert_ci_rankings):
          output_file.write('%s\t%s\t(%s,%s)\n'
                            % (url.strip(), count, rank,
                               ground_truth_url_to_rank[url]))
      with open('%sexpert_s_user_rankings_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as output_file:
        for rank, (url, count) in enumerate(expert_s_rankings):
          output_file.write('%s\t%s\t(%s,%s)\n'
                            % (url.strip(), count, rank,
                            ground_truth_url_to_rank[url]))

      market_precisions, market_recalls = calc_precision_recall(gt_rankings,
                                                                market_rankings)
      (newsaholic_precisions,
       newsaholic_recalls) = calc_precision_recall(gt_rankings,
                                                   newsaholic_rankings)
      active_precisions, active_recalls = calc_precision_recall(gt_rankings,
                                                                active_rankings)
      common_precisions, common_recalls = calc_precision_recall(gt_rankings,
                                                                common_rankings)
      (expert_p_precisions,
       expert_p_recalls) = calc_precision_recall(gt_rankings,
                                                 expert_precision_rankings)
      (expert_f_precisions,
       expert_f_recalls) = calc_precision_recall(gt_rankings,
                                                 expert_fscore_rankings)
      (expert_c_precisions,
       expert_c_recalls) = calc_precision_recall(gt_rankings,
                                                 expert_ci_rankings)
      (expert_s_precisions,
       expert_s_recalls) = calc_precision_recall(gt_rankings,
                                                 expert_s_rankings)

      draw_precision_recall_graph(market_precisions, market_recalls,
                                         newsaholic_precisions,
                                         newsaholic_recalls,
                                         active_precisions, active_recalls,
                                         common_precisions, common_recalls,
                                         expert_p_precisions, expert_p_recalls,
                                         expert_f_precisions, expert_f_recalls,
                                         expert_c_precisions, expert_c_recalls,
                                         expert_s_precisions, expert_s_recalls,
                                         delta, category)

      draw_precision_recall_graph_experts(market_precisions, market_recalls,
                                          expert_p_precisions, expert_p_recalls,
                                          expert_f_precisions, expert_f_recalls,
                                          expert_c_precisions, expert_c_recalls,
                                          delta, category)

      draw_precision_recall_graph_groups(market_precisions, market_recalls,
                                         newsaholic_precisions,
                                         newsaholic_recalls,
                                         active_precisions, active_recalls,
                                         common_precisions, common_recalls,
                                         delta, category)


def log(message):
  """Helper method to modularize the format of log messages.
  
  Keyword Arguments:
  message -- A string to log.
  """
  FileLog.log(_LOG_FILE, message)
  

if __name__ == "__main__":
  run()
