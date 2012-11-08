
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
from constants import _USER_ACTIVITY_FILE_ID_INDEX

from params import _EXCLUDE_RETWEETS
from params import _SWITCHED

_GRAPH_DIR = Util.get_graph_output_dir('FolkWisdom/')
_IN_DIR = '../data/FolkWisdom/'


def draw_precision(market_precisions, groups_precisions,
                   run_params_str):
  """Draws the precision recall graph for all the user groups and a given delta.

  Plots the given list of precisions against the number of top news that the
  precision value was calculated for.
  """
  plots = []
  figure = plt.figure()
  axs = figure.add_subplot(111)

  labels = ['Market']

  market_plot = axs.plot(market_precisions)
  plots.append(market_plot)

  for i, group_precisions in enumerate(groups_precisions):
    group_plot = axs.plot(group_precisions)
    plots.append(group_plot)
    labels.append('Group %s' % i)

  plt.legend(plots, labels, loc=0, ncol=2, columnspacing=0, handletextpad=0)

  plt.grid(True, which='major', linewidth=1)

  axs.yaxis.set_minor_locator(MultipleLocator(5))
  plt.grid(True, which='minor')

  plt.xlabel('Num Top News Picked', fontsize='16')
  plt.ylabel('Precision (%)', fontsize='16')

  with open(_GRAPH_DIR + run_params_str + '/precision_even_groups_%s.png'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + run_params_str + '/precision_even_groups_%s.eps'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='eps')

  plt.close()


def draw_precision_recall(market_precisions, market_recalls,
                          groups_precisions, groups_recalls,
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

  labels = ['Market']

  market_plot = axs.plot(market_recalls, market_precisions)
  plots.append(market_plot)

  for i, (group_precisions, group_recalls) in enumerate(zip(groups_precisions, groups_recalls)):
    group_plot = axs.plot(group_recalls, group_precisions)
    plots.append(group_plot)
    labels.append("Group %s" % i)

  plt.legend(plots, labels, loc=0, ncol=2, columnspacing=0, handletextpad=0)

  max_x = max(market_recalls)
  plt.axis([0, max_x + 5, 0, 105])
  plt.grid(True, which='major', linewidth=1)

  axs.xaxis.set_minor_locator(MultipleLocator(5))
  axs.yaxis.set_minor_locator(MultipleLocator(5))
  plt.grid(True, which='minor')

  plt.xlabel('Recall (%)', fontsize='16')
  plt.ylabel('Precision (%)', fontsize='16')

  with open(_GRAPH_DIR + run_params_str + '/precision_recall_even_groups_%s.png'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + run_params_str + '/precision_recall_even_groups_%s.eps'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='eps')

  plt.close()


def gather_tweet_counts(hours, seeds, groups, category=None):
  """Gathers the tweet counts for a given set of months.
  
  Only counts votes if they occur within the given time delta from the seed
  time (except for the ground truth rankings).
  
  Keyword Arguments:
  hours -- The number of hours from the seed time in which to accept votes.
  seeds -- A dictionary of url to the datetime of it first being seen
  Accepts a parameter for a set defining each of the following user groups:
  newsaholics, active users, experts (precision), experts (F-score),
  experts (confidence interval), and experts (super experts).
  category -- The category to gather tweets for, None if for all news.

  Returns:
  Dictionary of url to tweet count for all user groups. This includes:
  ground truth, market, newsaholic, active users, common users, and
  experts (precision, F-score, confidence interval, and super).
  """
  groups_tweet_counts = [{} for i in range(len(groups))]
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

              for i, group in enumerate(groups):
                if user_id in group:
                  group_tweet_counts = groups_tweet_counts[i] 
                  if url in group_tweet_counts:
                    group_tweet_counts[url] += 1
                  else:
                    group_tweet_counts[url] = 1
                
  return groups_tweet_counts 


def get_rankings(delta, seeds, groups, category=None):
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
  gtcs = gather_tweet_counts(delta, seeds, groups, category)
  groups_rankings = []
  for gtc in gtcs:
    group_rankings = sorted(gtc.items(), key=lambda x: x[1], reverse=True)
    groups_rankings.append(group_rankings)
  return groups_rankings 


def group_users(delta, num_groups, group_size_in_percent, category=None):
  """Splits users into a number of evenly sized groups.

  Keyword Arguments:
  delta -- The time window, in hours.
  num_groups -- The number of groups to have.
  group_size_in_percent -- The size of the groups, given as a percentage.
  category -- The category we are considering, None for all.

  Returns:
  num_users -- The total number of users.
  groups -- A List of Sets of group ids, one for each group.
  """
  user_ids_sorted = []
  in_dir = _IN_DIR
  if _SWITCHED:
    in_dir += 'switched/'
  if _EXCLUDE_RETWEETS:
    in_dir += 'no_retweets/'
  input_file = in_dir + 'user_activity_%s_%s.tsv' % (delta, category)
  with open(input_file) as input_file:
    for line in input_file:
      tokens = line.split('\t')
      user_id = tokens[_USER_ACTIVITY_FILE_ID_INDEX]
      user_ids_sorted.append(user_id)
  num_users = len(user_ids_sorted)
  group_size = int(num_users * group_size_in_percent)
  
  groups = []
  count = 0
  group_index = 0
  for i in range(num_users):
    if group_index == num_groups:
      break
    if count is 0:
      groups.append(set())
    user_id = user_ids_sorted[i]
    group = groups[group_index]
    group.add(user_id)
    count += 1
    if count == group_size:
      group_index += 1
      count = 0
  return num_users, groups 

