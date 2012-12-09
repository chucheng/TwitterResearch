import user_groups

from params import _SIZE_TOP_NEWS

import Util
import matplotlib
matplotlib.use("Agg")

from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt

_GRAPH_DIR = Util.get_graph_output_dir('FolkWisdom/')


def draw(precisions_list, recalls_list, labels, file_prefix, run_params_str, zoom=False):
  plots = []
  figure = plt.figure()
  axs = figure.add_subplot(111)

  line_types = ['-', '--']
  line_widths = [1, 2]

  max_x = 0
  for plot_num, (precisions, recalls) in enumerate(zip(precisions_list, recalls_list)):
    line_type = line_types[plot_num % len(line_types)]
    linewidth = line_widths[plot_num % len(line_widths)]
    plot = axs.plot(recalls, precisions, line_type, linewidth=linewidth)
    plots.append(plot)
    max_recall = max(recalls)
    if max_recall > max_x:
      max_x = max_recall

  plt.legend(plots, labels, loc=0, ncol=2, columnspacing=0, handletextpad=0)
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

  with open(_GRAPH_DIR + run_params_str + '/%s_%s.png'
            % (file_prefix, run_params_str), 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + run_params_str + '/%s_%s.eps'
            % (file_prefix, run_params_str), 'w') as graph:
    plt.savefig(graph, format='eps')

  plt.close()


def draw_with_markers(precisions_list, recalls_list, labels, file_prefix,
                      legend_location, run_params_str, zoom=False, ncol=1):
  plots = []
  figure = plt.figure()
  axs = figure.add_subplot(111)

  line_types = ['-']
  line_widths = [1]
  marker_types = ['bo', 'g^', 'rD', 'cs', 'm,', 'yv']
  marker_offsets = [0, 10, 20, 30]

  max_x = 0
  for plot_num, (precisions, recalls) in enumerate(zip(precisions_list, recalls_list)):
    precision_markers = []
    recall_markers = []
    marker_offset = marker_offsets[plot_num % len(marker_offsets)]
    for (i, (precision, recall)) in enumerate(zip(precisions, recalls)):
      if i % 40 == marker_offset:
        precision_markers.append(precision)
        recall_markers.append(recall)
    line_type = line_types[plot_num % len(line_types)]
    linewidth = line_widths[plot_num % len(line_widths)]
    plot = axs.plot(recalls, precisions, line_type, linewidth=linewidth)
    plots.append(plot)
    marker_type = marker_types[plot_num % len(marker_types)]
    markers_plot = axs.plot(recall_markers, precision_markers, marker_type)
    plots.append(markers_plot)
    max_recall = max(recalls)
    if max_recall > max_x:
      max_x = max_recall

  p = None
  for i, label in enumerate(labels):
    line_type = '-%s' % marker_types[i % len(marker_types)]
    p = axs.plot([0], [0], line_type, label=label)
  plots.append(p)

  plt.legend(loc=legend_location, ncol=ncol)
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

  with open(_GRAPH_DIR + run_params_str + '/%s_%s.png'
            % (file_prefix, run_params_str), 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + run_params_str + '/%s_%s.eps'
            % (file_prefix, run_params_str), 'w') as graph:
    plt.savefig(graph, format='eps')

  plt.close()


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


def get_precision_recalls(gt_rankings, rankings):
  precisions = user_groups.UserGroups()
  recalls = user_groups.UserGroups()

  precisions.population, recalls.population = calc_precision_recall(gt_rankings, rankings.population)
  precisions.newsaholics, recalls.newsaholics = calc_precision_recall(gt_rankings, rankings.newsaholics)
  precisions.active_users, recalls.active_users = calc_precision_recall(gt_rankings, rankings.active_users)
  precisions.common_users, recalls.common_users = calc_precision_recall(gt_rankings, rankings.common_users)
  precisions.precision, recalls.precision = calc_precision_recall(gt_rankings, rankings.precision)
  precisions.fscore, recalls.fscore = calc_precision_recall(gt_rankings, rankings.fscore)
  precisions.ci, recalls.ci = calc_precision_recall(gt_rankings, rankings.ci)
  precisions.ci_hi, recalls.ci_hi = calc_precision_recall(gt_rankings, rankings.ci_hi)
  precisions.ci_li, recalls.ci_li = calc_precision_recall(gt_rankings, rankings.ci_li)
  precisions.ci_1, recalls.ci_1 = calc_precision_recall(gt_rankings, rankings.ci_1)
  precisions.ci_2, recalls.ci_2 = calc_precision_recall(gt_rankings, rankings.ci_2)
  precisions.ci_3, recalls.ci_3 = calc_precision_recall(gt_rankings, rankings.ci_3)
  precisions.social_bias, recalls.social_bias = calc_precision_recall(gt_rankings, rankings.social_bias)
  precisions.non_experts, recalls.non_experts = calc_precision_recall(gt_rankings, rankings.non_experts)
  precisions.non_experts_sampled, recalls.non_experts_sampled = calc_precision_recall(gt_rankings, rankings.non_experts_sampled)
  precisions.non_experts_25, recalls.non_experts_25 = calc_precision_recall(gt_rankings, rankings.non_experts_25)
  precisions.non_experts_10, recalls.non_experts_10 = calc_precision_recall(gt_rankings, rankings.non_experts_10)
  precisions.non_experts_1, recalls.non_experts_1 = calc_precision_recall(gt_rankings, rankings.non_experts_1)
  precisions.super_experts, recalls.super_experts = calc_precision_recall(gt_rankings, rankings.super_experts)
  precisions.weighted_followers, recalls.weighted_followers = calc_precision_recall(gt_rankings, rankings.weighted_followers)
  precisions.ci_weighted, recalls.ci_weighted = calc_precision_recall(gt_rankings, rankings.ci_weighted)
  precisions.weighted, recalls.weighted = calc_precision_recall(gt_rankings, rankings.weighted)
  precisions.weighted_both, recalls.weighted_both = calc_precision_recall(gt_rankings, rankings.weighted_both)

  return precisions, recalls
