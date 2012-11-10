import Util
import matplotlib
matplotlib.use("Agg")

from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt

from params import _SIZE_TOP_NEWS

import math
from math import sqrt

_GRAPH_DIR = Util.get_graph_output_dir('FolkWisdom/')

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
