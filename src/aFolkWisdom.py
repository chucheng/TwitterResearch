import Configuration
import DataUtils
import Util

import matplotlib
matplotlib.use("Agg")

from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt
import matplotlib.axis

import os
from datetime import datetime 
from math import sqrt


_GRAPH_DIR = Util.get_graph_output_dir('FolkWisdom/')


def calculate_diff_avg(ground_truth_url_to_rank, other_rank_to_url):
  max_num_news_to_consider = int(len(ground_truth_url_to_rank.keys()) * .02)
  avg_diffs = []
  for i in range(1, max_num_news_to_consider + 1):
    diff_sum = 0
    for j in range(1, i + 1):
      other_rank = j
      url = other_rank_to_url[j]
      gt_rank = ground_truth_url_to_rank[url]
      diff = (other_rank - gt_rank)**2 
      diff_sum += diff
    diff_avg = sqrt(diff_sum) / i
    avg_diffs.append(diff_avg)
  
  return avg_diffs


def draw_graph(expert_diffs, active_diffs, common_diffs):
  plots = []
  figure = plt.figure()
  ax = figure.add_subplot(111)

  expert_plot = ax.plot([i for i in range(1, len(expert_diffs) + 1)], expert_diffs)
  plots.append(expert_plot)

  active_plot = ax.plot([i for i in range(1, len(active_diffs) + 1)], active_diffs)
  plots.append(active_plot)

  common_plot = ax.plot([i for i in range(1, len(common_diffs) + 1)], common_diffs)
  plots.append(common_plot)

  plt.legend(plots, ['Experts', 'Active Users', 'Common Users'])

  plt.axis([1, len(expert_diffs) + 1, 0, 20])
  plt.grid(True, which='major', linewidth=1)

  ax.xaxis.set_minor_locator(MultipleLocator(50))
  ax.yaxis.set_minor_locator(MultipleLocator(1))
  plt.grid(True, which='minor')

  plt.xlabel('Top X Stories Compared')
  plt.ylabel('Average Differnce in Ranking')
  plt.title('Ranking Performance by User Group')

  with open(_GRAPH_DIR + 'ranking_performance.png', 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + 'ranking_performance.eps', 'w') as graph:
    plt.savefig(graph, format='eps')

  print 'Outputted graph: Ranking Performance by User Group'
  plt.close()
  

def get_rankings(cache, experts, active_users):
  gtc, etc, atc, ctc = DataUtils.gather_tweet_counts(['09', '10', '11'], cache, experts, active_users)
  DataUtils.eliminate_news(['08'], gtc, cache)
  DataUtils.eliminate_news(['08'], etc, cache)
  DataUtils.eliminate_news(['08'], atc, cache)
  DataUtils.eliminate_news(['08'], ctc, cache)
  DataUtils.add_tweet_counts(['12'], gtc, cache)
  DataUtils.add_tweet_counts(['12'], etc, cache)
  DataUtils.add_tweet_counts(['12'], atc, cache)
  DataUtils.add_tweet_counts(['12'], ctc, cache)
  gt_rankings = sorted(gtc.items(), key=lambda x: x[1], reverse=True)
  expert_rankings = sorted(etc.items(), key=lambda x: x[1], reverse=True)
  active_rankings = sorted(atc.items(), key=lambda x: x[1], reverse=True)
  common_rankings = sorted(ctc.items(), key=lambda x: x[1], reverse=True)
  return gt_rankings, expert_rankings, active_rankings, common_rankings


def group_users():
  """Groups users into 'expert', 'active', and 'common' categories.
  
  Keyword Arguments:
  user_id_sorted_by_tweet_count -- A list of (user_id, tweet_count) pairs in 
  ranked (sorted by count) order.
  
  Returns:
  experts -- A python set of user ids for expert users, defined as users in top
  2% of users as ranked by activity.
  active_users -- A python set of user ids for active users, defined as users
  in between 2% and 25% of users as ranked by activity.
  common_users -- A python set of user ids for common users, defined as users
  whose rank is lower the 25% as ranked by activity.
  """
  user_id_sorted_by_tweet_count = DataUtils.get_users_sorted_by_tweet_count(['09', '10', '11'])
  num_users = len(user_id_sorted_by_tweet_count)
  bucket_size = num_users / 100
  
  user_id_to_percentile = {}
  experts = set()
  active_users = set()
  common_users = set()
  current_percentile = 1
  for i in range(num_users):
    user_id, tweet_count = user_id_sorted_by_tweet_count[i]
    if current_percentile < 3:
      experts.add(user_id)
    elif current_percentile < 26:
      active_users.add(user_id)
    else:
      common_users.add(user_id)
    if i is not 0 and i % bucket_size is 0:
      # Dont increase percentile past 100. We need to do this because we need
      # bucket size to be a integer, but to have 100 even buckets we would need
      # decimal bucket sizes. This takes care of this "rounding issue".
      if current_percentile < 100:
        current_percentile += 1
  return experts, active_users, common_users


def run():
  """Contains the main logic for this analysis.
  
  A high level overview of the logic is as follows:
  
  1. Load a cache of short urls to long urls
  2. Gather the ground truth counts, defined as the number of tweets a url
  received in month 09, 10, 11, and 12.
  3. Gather the tweet counts for each user.
  4. Group users in expert, active, and common categories based on activity.
  5. Get the rankings for urls as determined by each of the three user groups.
  6. Compare these rankings against the ground truth rankings.
  """
  cache = DataUtils.load_cache()

  experts, active_users, common_users = group_users()
  log('Num experts: %s' % len(experts))
  log('Num active: %s' % len(active_users))
  log('Num common: %s' % len(common_users))

  gt_rankings, expert_rankings, active_rankings, common_rankings = get_rankings(cache, experts, active_users)
  log('Num ground_truth_rankings: %s' % len(gt_rankings))
  num_votes_experts = 0
  for url, count in expert_rankings:
    num_votes_experts += count
  log('Num expert rankings: %s' % len(expert_rankings))
  log('Num expert votes: %s' % num_votes_experts)
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

  log('Ground Truth Top 10')
  for i in range(10):
    url, count = gt_rankings[i]
    log('[%s] %s\t%s' %(i, url, count))
  log('-----------------------------------')
  log('Expert Top 10')
  for i in range(10):
    url, count = expert_rankings[i]
    log('[%s] %s\t%s' %(i, url, count))
  log('-----------------------------------')
  log('Active Top 10')
  for i in range(10):
    url, count = active_rankings[i]
    log('[%s] %s\t%s' %(i, url, count))
  log('-----------------------------------')
  log('Common Top 10')
  for i in range(10):
    url, count = common_rankings[i]
    log('[%s] %s\t%s' %(i, url, count))
    
  ground_truth_url_to_rank = {}
  for rank, (url, count) in enumerate(gt_rankings):
    ground_truth_url_to_rank[url] = rank
  experts_rank_to_url = {}
  active_rank_to_url = {}
  common_rank_to_url = {}
  for rank, (url, count) in enumerate(expert_rankings):
    experts_rank_to_url[rank] = url
  for rank, (url, count) in enumerate(active_rankings):
    active_rank_to_url[rank] = url
  for rank, (url, count) in enumerate(common_rankings):
    common_rank_to_url[rank] = url
  avg_diffs_expert = calculate_diff_avg(ground_truth_url_to_rank, experts_rank_to_url)
  avg_diffs_active = calculate_diff_avg(ground_truth_url_to_rank, active_rank_to_url)
  avg_diffs_common = calculate_diff_avg(ground_truth_url_to_rank, common_rank_to_url)

  draw_graph(avg_diffs_expert, avg_diffs_active, avg_diffs_common)


def log(message):
  """Helper method to modularize the format of log messages.
  
  Keyword Arguments:
  message -- A string to print.
  """
  print '[%s] %s' %(datetime.now(), message)
  

if __name__ == "__main__":
    run()
