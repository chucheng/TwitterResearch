"""
This module handles operations and graph drawing for the mixed model approach.

__author = 'Chris Moghbel (cmoghbel@cs.ucla.edu)
"""
import Util

import matplotlib
matplotlib.use("Agg")
from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt
import matplotlib.axis

_GRAPH_DIR = Util.get_graph_output_dir('FolkWisdom/')


def draw_precision_mixed(market_precisions, mixed_precisions, run_params_str):
  """Draws the precision recall graph for all the user groups and a given delta.

  Plots the given list of precisions against the number of top news that the
  precision value was calculated for.
  """
  plots = []
  figure = plt.figure()
  axs = figure.add_subplot(111)

  market_plot = axs.plot(market_precisions, '--')
  plots.append(market_plot)

  mixed_plot = axs.plot(mixed_precisions)
  plots.append(mixed_plot)


  labels = ['Market', 'Mixed', ]
  plt.legend(plots, labels, loc=0)

  plt.grid(True, which='major', linewidth=1)

  axs.yaxis.set_minor_locator(MultipleLocator(5))
  plt.grid(True, which='minor')

  plt.xlabel('Num Top News Picked', fontsize='16')
  plt.ylabel('Precision (%)', fontsize='16')

  with open(_GRAPH_DIR + run_params_str + '/precision_mixed_%s.png'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + run_params_str + '/precision_mixed_%s.eps'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='eps')

  plt.close()


def draw_precision_recall_mixed(market_precisions, market_recalls,
                                mixed_precisions, mixed_recalls,
                                run_params_str, zoom=False):
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

  market_plot = axs.plot(market_recalls, market_precisions, label='Crowd')
  plots.append(market_plot)

  mixed_recalls_m = []
  mixed_precisions_m = []
  for (i, (precision, recall)) in enumerate(zip(mixed_precisions,
                                                mixed_recalls)):
    if i % 40 == 0:
      mixed_precisions_m.append(precision)
      mixed_recalls_m.append(recall)

  mixed_plot = axs.plot(mixed_recalls, mixed_precisions)
  plots.append(mixed_plot)

  mixed_plot_m = axs.plot(mixed_recalls_m, mixed_precisions_m, 'go')
  plots.append(mixed_plot_m)

  p = axs.plot([0], [0], '-go', label='Mixed')
  plots.append(p)

  labels = ['Market', 'Mixed (Min)', ]
  # plt.legend(plots, labels, loc=0)
  plt.legend(loc=3)

  max_x = max([max(market_recalls), max(mixed_recalls), ])
  if zoom:
    plt.axis([0, max_x + 5, 40, 105])
  else:
    plt.axis([0, max_x + 5, 0, 105])
  plt.grid(True, which='major', linewidth=1)

  axs.xaxis.set_minor_locator(MultipleLocator(5))
  axs.yaxis.set_minor_locator(MultipleLocator(5))
  plt.grid(True, which='minor')

  plt.xlabel('Recall (%)', fontsize='16')
  plt.ylabel('Precision (%)', fontsize='16')

  with open(_GRAPH_DIR + run_params_str + '/precision_recall_mixed_%s.png'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + run_params_str + '/precision_recall_mixed_%s.eps'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='eps')
  with open(_GRAPH_DIR + run_params_str + '/precision_recall_mixed_%s.tsv'
            % run_params_str, 'w') as out_file:
    for i in range(len(market_recalls)):
      market_r = market_recalls[i]
      market_p = market_precisions[i]
      mixed_r = mixed_recalls[i]
      mixed_p = mixed_precisions[i]
      out_file.write('%s\t%s\t%s\t%s\t%s\n' % (i + 1, market_r, market_p,
                                               mixed_r, mixed_p))

  plt.close()


def get_mixed_rankings(market_url_to_rank, market_precisions,
                       precision_url_to_rank, expert_p_precisions,
                       fscore_url_to_rank, expert_f_precisions,
                       ci_url_to_rank, expert_c_precisions,
                       gt_url_to_rank):
  """Finds ranking based on min ranking of 4 rankings sets.

  Ground truths rankings are used to break ties.

  Keyword Arguments:
  market_url_to_rank -- Dictionary from url to market ranking.
  precision_url_to_rank -- Dictionary from url to precision expert rankings.
  fscore_url_to_rank -- Dictionary from url to fscore expert rankings.
  ci_url_to_rank -- Dictionary from url to ci expert rankings.
  gt_url_to_rank -- Dictionary from url to ground truth ranking.

  Returns:
  mixed_rankings -- A list of (url, count) pairs representing the rankings.
  """
  urls = set()
  urls = urls.union(market_url_to_rank.keys())
  urls = urls.union(precision_url_to_rank.keys())
  urls = urls.union(fscore_url_to_rank.keys())
  urls = urls.union(ci_url_to_rank.keys())

  mixed_error_to_url_list = {}
  for url in urls:
    market_error = 100.0
    precision_error = 100.0
    fscore_error = 100.0
    ci_error = 100.0
    if url in market_url_to_rank:
      market_rank = market_url_to_rank[url]
      if market_rank <= len(market_precisions):
        market_error = 100.0 - market_precisions[market_rank - 1]
    if url in precision_url_to_rank:
      precision_rank = precision_url_to_rank[url]
      if precision_rank <= len(expert_p_precisions):
        precision_error = 100.0 - expert_p_precisions[precision_rank - 1]
    if url in fscore_url_to_rank:
      fscore_rank = fscore_url_to_rank[url]
      if fscore_rank <= len(expert_f_precisions):
        fscore_error = 100.0 - expert_f_precisions[fscore_rank - 1]
    if url in ci_url_to_rank:
      ci_rank = ci_url_to_rank[url]
      if ci_rank <= len(expert_c_precisions):
        ci_error = 100.0 - expert_c_precisions[ci_rank - 1]
    mixed_error = min(market_error, precision_error, fscore_error, ci_error)
    if url in gt_url_to_rank:
      gt_rank = gt_url_to_rank[url]
      if mixed_error in mixed_error_to_url_list:
        mixed_error_to_url_list[mixed_error].append((url, gt_rank))
      else:
        mixed_error_to_url_list[mixed_error] = [(url, gt_rank), ]

  rankings = break_ties(mixed_error_to_url_list)
  return rankings


def break_ties(mixed_rank_to_url_list):
  """Breaks ties in rank when finding rankings for mixed model.

  Keyword Argument:
  mixed_rank_to_url_list -- A dictionary from rank to a list of
                            (url, count) pairs for that rank.

  Returns:
  rankings - A list of (url, count) pairs representing the ranking w/ ties
             broken.
  """
  prelim_rankings = sorted(mixed_rank_to_url_list.items(), key=lambda x: x[0])
  rankings = []
  for _, urls in prelim_rankings:
    urls_sorted = sorted(urls, key=lambda x: x[1])
    for url in urls_sorted:
      rankings.append(url)
  return rankings
