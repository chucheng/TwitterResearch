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

import experts
import basic_groups
import even_groups
import mixed_model
import ground_truths
from ground_truths import DataSet

import matplotlib
matplotlib.use("Agg")

from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt

import math
from math import sqrt

from constants import _DELTAS

_GRAPH_DIR = Util.get_graph_output_dir('FolkWisdom/')
_LOG_FILE = 'aFolkWisdom.log'

_SIZE_EXPERTS = .02
_SIZE_TOP_NEWS = .02 # This is reset at the beginning of run.

_NUM_GROUPS = 5
_SIZE_OF_GROUP_IN_PERCENT = .02

_CATEGORIES = []
# Comment categories in/out individually as needed.
_CATEGORIES.append(None)
# _CATEGORIES.append('world')
# _CATEGORIES.append('business')
# _CATEGORIES.append('opinion')
# _CATEGORIES.append('sports')
# _CATEGORIES.append('us')
# _CATEGORIES.append('technology')
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
                        expert_c_diffs, expert_s_diffs, run_params_str):
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
  axs = figure.add_subplot(111)

  market_plot = axs.plot([i for i in range(1, len(market_diffs) + 1)],
                         market_diffs)
  plots.append(market_plot)

  newsaholic_plot = axs.plot([i for i in range(1, len(newsaholic_diffs) + 1)],
                         newsaholic_diffs)
  plots.append(newsaholic_plot)

  active_plot = axs.plot([i for i in range(1, len(active_diffs) + 1)],
                         active_diffs)
  plots.append(active_plot)

  common_plot = axs.plot([i for i in range(1, len(common_diffs) + 1)],
                         common_diffs)
  plots.append(common_plot)

  expert_p_plot = axs.plot([i for i in range(1, len(expert_p_diffs) + 1)],
                           expert_p_diffs)
  plots.append(expert_p_plot)
  expert_f_plot = axs.plot([i for i in range(1, len(expert_f_diffs) + 1)],
                           expert_f_diffs)
  plots.append(expert_f_plot)
  expert_c_plot = axs.plot([i for i in range(1, len(expert_c_diffs) + 1)],
                           expert_c_diffs)
  plots.append(expert_c_plot)
  expert_s_plot = axs.plot([i for i in range(1, len(expert_s_diffs) + 1)],
                           expert_s_diffs, '--')
  plots.append(expert_s_plot)


  labels = ['Market', 'News-addicted', 'Active Users', 'Common Users',
            'Experts (Precision)', 'Experts (F-score)', 'Experts (CI)',
            'Super Experts']
  plt.legend(plots, labels, loc=0, ncol=2, columnspacing=0, handletextpad=0)

  max_y = max([max(market_diffs), max(newsaholic_diffs), max(active_diffs),
               max(common_diffs), max(expert_p_diffs), max(expert_f_diffs),
               max(expert_c_diffs), max(expert_s_diffs)])
  plt.axis([1, len(newsaholic_diffs) + 1, 0, max_y])
  plt.grid(True, which='major', linewidth=1)

  axs.xaxis.set_minor_locator(MultipleLocator(100))
  minor_locator = int(math.log(max_y))
  if minor_locator % 2 == 1:
    minor_locator += 1
  axs.yaxis.set_minor_locator(MultipleLocator(minor_locator))
  plt.grid(True, which='minor')

  plt.xlabel('Top X Stories Compared')
  plt.ylabel('Average Differnce in Ranking')

  with open(_GRAPH_DIR + run_params_str + '/ranking_performance_%s.png'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + run_params_str + '/ranking_performance_%s.eps'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='eps')

  plt.close()


def draw_precision_graph(newsaholic_precisions,
                         active_precisions, common_precisions,
                         expert_p_precisions, expert_f_precisions,
                         expert_c_precisions, expert_s_precisions,
                         run_params_str):
  """Draws the precision recall graph for all the user groups and a given delta.

  Plots the given list of precisions against the number of top news that the
  precision value was calculated for.
  """
  plots = []
  figure = plt.figure()
  axs = figure.add_subplot(111)

  # Groups
  newsaholic_plot = axs.plot(newsaholic_precisions, '--', linewidth=2)
  plots.append(newsaholic_plot)
  active_plot = axs.plot(active_precisions, ':', linewidth=2)
  plots.append(active_plot)
  common_plot = axs.plot(common_precisions, '-.', linewidth=2)
  plots.append(common_plot)

  # Experts
  expert_p_plot = axs.plot(expert_p_precisions, '--', linewidth=2)
  plots.append(expert_p_plot)
  expert_f_plot = axs.plot(expert_f_precisions, '-.', linewidth=2)
  plots.append(expert_f_plot)
  expert_c_plot = axs.plot(expert_c_precisions, ':', linewidth=2)
  plots.append(expert_c_plot)
  expert_s_plot = axs.plot(expert_s_precisions, ':', linewidth=2)
  plots.append(expert_s_plot)

  labels = ['News-addicted', 'Active Users', 'Common Users',
            'Experts (Precision)', 'Experts (F-score)', 'Experts (CI)',
            'Super Experts']
  plt.legend(plots, labels, loc=0, ncol=2, columnspacing=0, handletextpad=0)

  plt.grid(True, which='major', linewidth=1)

  axs.yaxis.set_minor_locator(MultipleLocator(5))
  plt.grid(True, which='minor')

  plt.xlabel('Recall (%)')
  plt.ylabel('Num Top News Picked')

  with open(_GRAPH_DIR + run_params_str + '/precision_all_%s.png'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + run_params_str + '/precision_all_%s.eps'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='eps')

  plt.close()


def draw_precision_recall_graph(newsaholic_precisions, newsaholic_recalls,
                                active_precisions, active_recalls,
                                common_precisions, common_recalls,
                                expert_p_precisions, expert_p_recalls,
                                expert_f_precisions, expert_f_recalls,
                                expert_c_precisions, expert_c_recalls,
                                expert_s_precisions, expert_s_recalls,
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

  # Groups
  newsaholic_plot = axs.plot(newsaholic_recalls, newsaholic_precisions, '--',
                             linewidth=2)
  plots.append(newsaholic_plot)
  active_plot = axs.plot(active_recalls, active_precisions, ':',
                         linewidth=2)
  plots.append(active_plot)
  common_plot = axs.plot(common_recalls, common_precisions, '-.',
                         linewidth=2)
  plots.append(common_plot)

  # Experts
  expert_p_plot = axs.plot(expert_p_recalls, expert_p_precisions, '--',
                           linewidth=2)
  plots.append(expert_p_plot)
  expert_f_plot = axs.plot(expert_f_recalls, expert_f_precisions, '-.',
                           linewidth=2)
  plots.append(expert_f_plot)
  expert_c_plot = axs.plot(expert_c_recalls, expert_c_precisions, ':',
                           linewidth=2)
  plots.append(expert_c_plot)
  expert_s_plot = axs.plot(expert_s_recalls, expert_s_precisions, ':',
                           linewidth=2)
  plots.append(expert_s_plot)

  labels = ['News-addicted', 'Active Users', 'Common Users',
            'Experts (Precision)', 'Experts (F-score)', 'Experts (CI)',
            'Super Experts']
  plt.legend(plots, labels, loc=0, ncol=2, columnspacing=0, handletextpad=0)

  max_x = max([max(newsaholic_recalls), max(active_recalls),
               max(common_recalls), max(expert_p_recalls),
               max(expert_f_recalls), max(expert_c_recalls),
               max(expert_s_recalls)])
  plt.axis([0, max_x + 5, 0, 105])
  plt.grid(True, which='major', linewidth=1)

  axs.xaxis.set_minor_locator(MultipleLocator(5))
  axs.yaxis.set_minor_locator(MultipleLocator(5))
  plt.grid(True, which='minor')

  plt.xlabel('Recall (%)')
  plt.ylabel('Precision (%)')

  with open(_GRAPH_DIR + run_params_str + '/precision_recall_all_%s.png'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + run_params_str + '/precision_recall_all_%s.eps'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='eps')

  plt.close()


def run():
  """Contains the main logic for this analysis."""
  global _SIZE_TOP_NEWS
  FileLog.set_log_dir()

  seeds = Util.load_seeds()
  for category in _CATEGORIES:
    log('Preforming analysis for category: %s' % category)
    if category:
      _SIZE_TOP_NEWS = .10
    else:
      _SIZE_TOP_NEWS = .02

    gt_rankings = ground_truths.get_gt_rankings(seeds, DataSet.TESTING,
                                                category)
    log('Num ground_truth_rankings: %s' % len(gt_rankings))

    # Format for use later.
    ground_truth_url_to_rank = {}
    for rank, (url, count) in enumerate(gt_rankings):
      ground_truth_url_to_rank[url] = rank


    target_news = ground_truths.find_target_news(gt_rankings, _SIZE_TOP_NEWS)
    log('Size target_news: %s' % len(target_news))

    # for delta in _DELTAS:
    for delta in [4]:
      run_params_str = 'd%s_t%s_e%s_%s' % (delta, int(_SIZE_TOP_NEWS * 100),
                                           int(_SIZE_EXPERTS * 100), category)
      info_output_dir = '../graph/FolkWisdom/%s/info/' % run_params_str
      Util.ensure_dir_exist(info_output_dir)

      (num_users, newsaholics,
       active_users, common_users) = basic_groups.group_users(delta, category)
      log('Num newsaholics: %s' % len(newsaholics))
      log('Num active: %s' % len(active_users))
      log('Num common: %s' % len(common_users))

      num_users_eg, groups = even_groups.group_users(delta,
                                                     _NUM_GROUPS,
                                                     _SIZE_OF_GROUP_IN_PERCENT,
                                                     category)
      log('Num users in evenly distributed groups: %s' % len(groups[0]))

      experts_precision = experts.select_experts_precision(
          newsaholics.union(active_users), num_users, delta, _SIZE_EXPERTS,
          category)
      experts_fscore = experts.select_experts_fscore(len(target_news),
                                                     num_users,
                                                     delta, _SIZE_EXPERTS,
                                                     category)
      experts_ci = experts.select_experts_ci(num_users, delta, _SIZE_EXPERTS,
                                             category)
      super_experts = experts.select_super_experts(experts_precision,
                                                   experts_fscore,
                                                   experts_ci)

      log('Num experts (precision): %s' % len(experts_precision))
      log('Num experts (fscore): %s' % len(experts_fscore))
      log('Num experts (ci): %s' % len(experts_ci))
      log('Num Super Experts: %s' %len(super_experts))

      log('Finding rankings with an %s hour delta.' % delta)
      (market_rankings, newsaholic_rankings,
       active_rankings,
       common_rankings) = basic_groups.get_rankings(delta, seeds, newsaholics,
                                                    active_users, category)
      (expert_precision_rankings, expert_fscore_rankings,
       expert_ci_rankings,
       expert_s_rankings) = experts.get_rankings(delta, seeds,
                                                 experts_precision,
                                                 experts_fscore,
                                                 experts_ci,
                                                 super_experts,
                                                 category)

      groups_rankings = even_groups.get_rankings(delta, seeds, groups,
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

      for group_rankings in groups_rankings:
        num_votes_group = 0
        for url, count in group_rankings:
          num_votes_group += count
        log('Num rankings group: %s' % len(group_rankings))
        log('Num votes group: %s' % num_votes_group)


      size_market_unfiltered = '0'
      with open('../data/FolkWisdom/size_of_market_unfiltered.txt') as in_file:
        size_market_unfiltered = in_file.readline().strip()

      with open('%suser_demographics_%s.txt'
                % (info_output_dir, run_params_str), 'w') as output_file:
        output_file.write('Number of Newsaholics: %s\n' % len(newsaholics))
        output_file.write('Number of Active Users: %s\n' % len(active_users))
        output_file.write('Number of Common Users: %s\n' % len(common_users))
        output_file.write('\n');
        output_file.write('Number of Precision Experts: %s\n' % len(experts_precision))
        output_file.write('Number of F-Score Experts: %s\n' % len(experts_fscore))
        output_file.write('Number of CI Experts: %s\n' % len(experts_ci))
        output_file.write('Number of Precision and F-Score Experts: %s\n'
                          % len(experts_precision.intersection(experts_fscore)))
        output_file.write('Number of Precision and CI Experts: %s\n'
                          % len(experts_precision.intersection(experts_ci)))
        output_file.write('Number of F-Score and CI Experts: %s\n'
                          % len(experts_fscore.intersection(experts_ci)))
        output_file.write('Number of Super Experts: %s\n' % len(super_experts))
        output_file.write('\n');
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
        output_file.write('\n');
        output_file.write('Number of votes by Expert (Precision) Users: %s\n'
                % num_votes_expert_precision) 
        output_file.write('Number of votes by Expert (fscore) Users: %s\n'
                % num_votes_expert_fscore) 
        output_file.write('Number of votes by Expert (ci) Users: %s\n'
                % num_votes_expert_ci) 
        output_file.write('Number of votes by Super Experts: %s\n'
                          % num_votes_expert_s)
        output_file.write('\n')
        output_file.write('Total Number of votes cast: %s\n'
                          % (num_votes_newsaholics + num_votes_active
                             + num_votes_common))
        output_file.write('\n')
        output_file.write('Total Number of Good News: %s\n' % len(target_news))

      log('Ground Truth Top 5')
      for i in range(min(len(gt_rankings), 5)):
        url, count = gt_rankings[i]
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

      for group_rankings in groups_rankings:
        for i in range(min(len(group_rankings), 5)):
          url, count = group_rankings[i]
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

      mixed_rankings = mixed_model.get_mixed_rankings(market_url_to_rank,
                                                      market_precisions,
                                                      precision_url_to_rank,
                                                      expert_p_precisions,
                                                      fscore_url_to_rank,
                                                      expert_f_precisions,
                                                      ci_url_to_rank,
                                                      expert_c_precisions,
                                                      ground_truth_url_to_rank)

      mixed_precisions, mixed_recalls = calc_precision_recall(gt_rankings, 
                                                              mixed_rankings)

      groups_precisions = []
      groups_recalls = []
      for group_rankings in groups_rankings:
        group_precisions, group_recalls = calc_precision_recall(gt_rankings,
                                                                group_rankings)
        groups_precisions.append(group_precisions)
        groups_recalls.append(group_recalls)

      log('-----------------------------------')
      log('Mixed (min) Top 5')
      for i in range(min(len(mixed_rankings), 5)):
        url, count = mixed_rankings[i]
        log('[%s] %s\t%s' %(i + 1, url, count))
      log('-----------------------------------')

      # TODO: Add group rankings to this?
      with open('%sranking_comparisons_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as out_file:
        for gt_rank, (gt_url, _) in enumerate(gt_rankings):
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
        for rank, (url, count) in enumerate(common_rankings):
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
      with open('%smixed_rankings_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as output_file:
        for rank, (url, count) in enumerate(mixed_rankings):
          output_file.write('%s\t%s\t(%s,%s)\n'
                            % (url.strip(), count, rank,
                            ground_truth_url_to_rank[url]))
      
      for i, group_rankings in enumerate(groups_rankings):
        with open('%sgroup_%s_rankings_%s.tsv'
                  % (info_output_dir, i, run_params_str), 'w') as output_file:
          output_file.write('%s\t%s\t(%s,%s)\n'
                            % (url.strip(), count, rank,
                            ground_truth_url_to_rank[url]))


      with open('../data/FolkWisdom/market_precisions_%s.txt'
                % run_params_str, 'w') as out_file:
        for precision in common_precisions:
          out_file.write('%s\n' % precision)

      with open('../data/FolkWisdom/expert_p_precisions_%s.txt'
                % run_params_str, 'w') as out_file:
        for precision in expert_p_precisions:
          out_file.write('%s\n' % precision)

      with open('../data/FolkWisdom/expert_f_precisions_%s.txt'
                % run_params_str, 'w') as out_file:
        for precision in expert_f_precisions:
          out_file.write('%s\n' % precision)

      with open('../data/FolkWisdom/expert_c_precisions_%s.txt'
                % run_params_str, 'w') as out_file:
        for precision in expert_c_precisions:
          out_file.write('%s\n' % precision)

      log('Drawing summary precision-recall graphs...')
      # draw_precision_recall_graph(market_precisions, market_recalls,
      draw_precision_recall_graph(newsaholic_precisions,
                                  newsaholic_recalls,
                                  active_precisions, active_recalls,
                                  common_precisions, common_recalls,
                                  expert_p_precisions, expert_p_recalls,
                                  expert_f_precisions, expert_f_recalls,
                                  expert_c_precisions, expert_c_recalls,
                                  expert_s_precisions, expert_s_recalls,
                                  run_params_str)

      log('Drawing summary precision-topnews graphs...')
      # draw_precision_graph(market_precisions, newsaholic_precisions,
      draw_precision_graph(newsaholic_precisions,
                           active_precisions, common_precisions,
                           expert_p_precisions, expert_f_precisions,
                           expert_c_precisions, expert_s_precisions,
                           run_params_str)

      log('Drawing experts precision-recall graph...')
      # experts.draw_precision_recall_experts(market_precisions, market_recalls,
      experts.draw_precision_recall_experts(common_precisions, common_recalls,
                                            expert_p_precisions,
                                            expert_p_recalls,
                                            expert_f_precisions,
                                            expert_f_recalls,
                                            expert_c_precisions,
                                            expert_c_recalls,
                                            run_params_str)

      log('Drawing experts precision-topnews graph...')
      # experts.draw_precision_experts(market_precisions, expert_p_precisions,
      experts.draw_precision_experts(common_precisions, expert_p_precisions,
                                     expert_f_precisions, expert_c_precisions,
                                     run_params_str)

      log('Drawing basic groups precision-recall graph...')
      # basic_groups.draw_precision_recall_groups(market_precisions,
      #                                           market_recalls,
      basic_groups.draw_precision_recall_groups(newsaholic_precisions,
                                                newsaholic_recalls,
                                                active_precisions,
                                                active_recalls,
                                                common_precisions,
                                                common_recalls,
                                                run_params_str)

      log('Drawing basic groups precision-topnews graph...')
      # basic_groups.draw_precision_groups(market_precisions,
      basic_groups.draw_precision_groups(newsaholic_precisions,
                                         active_precisions,
                                         common_precisions,
                                         run_params_str)

      log('Drawing mixed model precision-recall graph...')
      # mixed_model.draw_precision_recall_mixed(market_precisions, market_recalls,
      mixed_model.draw_precision_recall_mixed(common_precisions, common_recalls,
                                              mixed_precisions, mixed_recalls,
                                              run_params_str)

      log('Drawing mixed model precision-topnews graph...')
      # mixed_model.draw_precision_mixed(market_precisions, mixed_precisions,
      mixed_model.draw_precision_mixed(common_precisions, mixed_precisions,
                                       run_params_str)

      log('Drawing even group model precision-recall graph...')
      # even_groups.draw_precision_recall(market_precisions, market_recalls,
      even_groups.draw_precision_recall(common_precisions, common_recalls,
                                        groups_precisions, groups_recalls,
                                        run_params_str)

      log('Drawing even group model precision graph...')
      # even_groups.draw_precision(market_precisions, groups_precisions,
      even_groups.draw_precision(common_precisions, groups_precisions,
                                 run_params_str)


def log(message):
  """Helper method to modularize the format of log messages.
  
  Keyword Arguments:
  message -- A string to log.
  """
  FileLog.log(_LOG_FILE, message)
  

if __name__ == "__main__":
  run()
