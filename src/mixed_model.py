"""
This module handles operations and graph drawing for the mixed model approach.

__author = 'Chris Moghbel (cmoghbel@cs.ucla.edu)
"""
import Util

import sys

import matplotlib
matplotlib.use("Agg")
from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt
import matplotlib.axis

_GRAPH_DIR = Util.get_graph_output_dir('FolkWisdom/')


def draw_precision_recall_mixed(market_precisions, market_recalls,
                                mixed_precisions, mixed_recalls,
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

  market_plot = axs.plot(market_recalls, market_precisions, '--')
  plots.append(market_plot)

  mixed_plot = axs.plot(mixed_recalls, mixed_precisions)
  plots.append(mixed_plot)


  labels = ['Market', 'Mixed (Min)', ]
  plt.legend(plots, labels, loc=0)

  max_x = max([max(market_recalls), max(mixed_recalls), ])
  plt.axis([0, max_x + 5, 0, 105])
  plt.grid(True, which='major', linewidth=1)

  axs.xaxis.set_minor_locator(MultipleLocator(5))
  axs.yaxis.set_minor_locator(MultipleLocator(5))
  plt.grid(True, which='minor')

  plt.xlabel('Recall (%)')
  plt.ylabel('Precision (%)')

  with open(_GRAPH_DIR + run_params_str + '/precision_recall_mixed_%s.png'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + run_params_str + '/precision_recall_mixed_%s.eps'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='eps')

  plt.close()


def get_mixed_rankings(market_url_to_rank, precision_url_to_rank,
                       fscore_url_to_rank, ci_url_to_rank, gt_url_to_rank):
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

  mixed_rank_to_url_list = {}
  for url in urls:
    market_rank = sys.maxint
    precision_rank = sys.maxint
    fscore_rank = sys.maxint
    ci_rank = sys.maxint
    if url in market_url_to_rank:
      market_rank = market_url_to_rank[url]
    if url in precision_url_to_rank:
      precision_rank = precision_url_to_rank[url]
    if url in fscore_url_to_rank:
      fscore_rank = fscore_url_to_rank[url]
    if url in ci_url_to_rank:
      ci_rank = ci_url_to_rank[url]
    mixed_rank = min(market_rank, precision_rank, fscore_rank, ci_rank)
    gt_rank = gt_url_to_rank[url]
    if mixed_rank in mixed_rank_to_url_list:
      mixed_rank_to_url_list[mixed_rank].append((url, gt_rank))
    else:
      mixed_rank_to_url_list[mixed_rank] = [(url, gt_rank), ]

  rankings = break_ties(mixed_rank_to_url_list)
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
