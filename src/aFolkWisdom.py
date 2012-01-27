"""
This module performs an analysis on determining which group can perform better
at ranking when compared to the ground truth. Some definitions which apply
throughout this analysis:

ground_truth -- Determined as the ranking after summing up the tweet counts for
all four months.

experts -- Defined as the top 2% of active users when ranked by the rate at
which they tweet.

active_users -- Defined as users between 2% and 25% when ranked by the rate at
which they tweet.

common_users -- Defined as users ranked more than 25% when ranked by the rate
at which they tweet.

__author__ = 'Chris Moghbel (cmoghbel@cs.ucla.edu)'
"""
import DataUtils
import FileLog
import Util

import matplotlib
matplotlib.use("Agg")

from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt
import matplotlib.axis

from datetime import datetime 
import math
from math import sqrt


_GRAPH_DIR = Util.get_graph_output_dir('FolkWisdom/')
_LOG_FILE = 'aFolkWisdom.log'
_DELTAS = [1, 4, 8]


def calculate_diff_avg(ground_truth_url_to_rank, other_rank_to_url):
  """Calculates the average of the difference in rank from the truth.
  
  Keyword Arguments:
  ground_truth_url_to_rank -- Dictionary mapping url to true rank.
  other_rank_to_url -- Dictionary mapping some non-truth ranking to url.
  
  Returns:
  avg_diffs: A list of avg_diff, for each number of news chosen.
  """
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


def draw_graph(expert_diffs, market_diffs, active_diffs, common_diffs, delta):
  """Draws the graph for avg diffs.
  
  Keyword Arguments:
  expert_diffs -- The diffs in raking between experts and truth.
  active_diffs -- The diffs in ranking between active users and truth.
  common_diffs -- The diffs in ranking between common users and truth.
  """
  plots = []
  figure = plt.figure()
  ax = figure.add_subplot(111)

  market_plot = ax.plot([i for i in range(1, len(market_diffs) + 1)],
                        market_diffs)
  plots.append(market_plot)

  expert_plot = ax.plot([i for i in range(1, len(expert_diffs) + 1)],
                        expert_diffs)
  plots.append(expert_plot)

  active_plot = ax.plot([i for i in range(1, len(active_diffs) + 1)],
                        active_diffs)
  plots.append(active_plot)

  common_plot = ax.plot([i for i in range(1, len(common_diffs) + 1)],
                        common_diffs)
  plots.append(common_plot)

  plt.legend(plots, ['Market', 'News-aholics', 'Active Users', 'Common Users'],
             loc=0)

  max_y = max([max(market_diffs), max(expert_diffs), max(active_diffs),
               max(common_diffs)])
  plt.axis([1, len(expert_diffs) + 1, 0, max_y])
  plt.grid(True, which='major', linewidth=1)

  ax.xaxis.set_minor_locator(MultipleLocator(100))
  minor_locator = int(math.log(max_y))
  if minor_locator % 2 == 1:
    minor_locator += 1
  ax.yaxis.set_minor_locator(MultipleLocator(minor_locator))
  plt.grid(True, which='minor')

  plt.xlabel('Top X Stories Compared')
  plt.ylabel('Average Differnce in Ranking')
  plt.title('Ranking Performance by User Group with %s Hour Delta' % delta)

  with open(_GRAPH_DIR + 'ranking_performance_%s.png' % delta, 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + 'ranking_performance_%s.eps' % delta, 'w') as graph:
    plt.savefig(graph, format='eps')

  log('Outputted graph: Ranking Performance by User Group with %s Hour Delta'
      % delta)
  plt.close()
  

def get_rankings(delta, cache, experts, active_users):
  """Gets the true rankings, and ranking returned by expert, active, and common.
  
  Keyword Arguments:
  cache -- Dictionary mapping short url to long url.
  experts -- A set of user ids representing expert users.
  active_users -- A set of user ids representing active users.
  
  Returns:
  gt_rankings -- The ground truth rankings as a list of (url, count) pairs.
  expert_rankings -- The rankings as given by expert users, as a list of
  (url, count) pairs.
  active_rankings -- The rankings as given by active users, as a list of
  (url, count) pairs.
  common_rankings -- The rankings as given by common users, as a list of
  (url, count) pairs.
  """
  gtc, mtc, etc, atc, ctc = DataUtils.gather_tweet_counts(cache, experts,
                                                          active_users, delta)
  # DataUtils.eliminate_news(['08'], gtc, cache)
  # DataUtils.eliminate_news(['08'], etc, cache)
  # DataUtils.eliminate_news(['08'], atc, cache)
  # DataUtils.eliminate_news(['08'], ctc, cache)
  # DataUtils.add_tweet_counts(['12'], gtc, cache)
  # DataUtils.add_tweet_counts(['12'], etc, cache)
  # DataUtils.add_tweet_counts(['12'], atc, cache)
  # DataUtils.add_tweet_counts(['12'], ctc, cache)
  gt_rankings = sorted(gtc.items(), key=lambda x: x[1], reverse=True)
  market_rankings = sorted(mtc.items(), key=lambda x: x[1], reverse=True)
  expert_rankings = sorted(etc.items(), key=lambda x: x[1], reverse=True)
  active_rankings = sorted(atc.items(), key=lambda x: x[1], reverse=True)
  common_rankings = sorted(ctc.items(), key=lambda x: x[1], reverse=True)
  return (gt_rankings, market_rankings, expert_rankings, active_rankings,
         common_rankings)


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
  user_id_sorted = DataUtils.get_users_sorted_by_tweet_count(['08', '09', '10', '11', '12'])
  num_users = len(user_id_sorted)
  bucket_size = num_users / 100
  
  experts = set()
  active_users = set()
  common_users = set()
  current_percentile = 1
  for i in range(num_users):
    (user_id, _) = user_id_sorted[i]
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
  2. Group users into expert, active, and common groups.
  3. Get both the true rankings, and the rankings as given by each group.
  4. Compare group rankings against the ground truth rankings.
  5. Draw graph.
  """
  FileLog.set_log_dir()
  cache = DataUtils.load_cache()

  experts, active_users, common_users = group_users()
  log('Num experts: %s' % len(experts))
  log('Num active: %s' % len(active_users))
  log('Num common: %s' % len(common_users))

  for delta in _DELTAS:
    log('Finding rankings with an %s hour delta.' % delta)
    (gt_rankings, market_rankings, expert_rankings,
     active_rankings, common_rankings) = get_rankings(delta, cache, experts,
                                                      active_users)

    with open('../data/report/ground_truth_rankings_%s.tsv' % delta, 'w') as f:
      for url, count in gt_rankings:
        f.write('%s\t%s\n' % (url.strip(), count))
    with open('../data/report/market_rankings_%s.tsv' % delta, 'w') as f:
      for url, count in market_rankings:
        f.write('%s\t%s\n' % (url.strip(), count))
    with open('../data/report/newsaholic_rankings_%s.tsv' % delta, 'w') as f:
      for url, count in expert_rankings:
        f.write('%s\t%s\n' % (url.strip(), count))
    with open('../data/report/active_user_rankings_%s.tsv' % delta, 'w') as f:
      for url, count in active_rankings:
        f.write('%s\t%s\n' % (url.strip(), count))
    with open('../data/report/common_user_rankings_%s.tsv' % delta, 'w') as f:
      for url, count in common_rankings:
        f.write('%s\t%s\n' % (url.strip(), count))

    log('Num ground_truth_rankings: %s' % len(gt_rankings))
    num_votes_market = 0
    for url, count in market_rankings:
      num_votes_market += count
    log('Num market rankings: %s' % len(market_rankings))
    log('Num market votes: %s' % num_votes_market)
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

    with open('../data/report/user_demographics_%s.txt' % delta, 'w') as f:
      f.write('Number of Newsaholics: %s\n' % len(experts))
      f.write('Number of Active Users: %s\n' % len(active_users))
      f.write('Number of Common Users: %s\n' % len(common_users))
      f.write('Number of Users (Total): %s\n' % (len(experts) + len(active_users)
                                               + len(common_users)))
      f.write('\n')
      f.write('Number of votes by Newsaholics: %s\n' % num_votes_experts)
      f.write('Number of votes by Market: %s\n' % num_votes_market)
      f.write('Number of votes by Active Users: %s\n'  % num_votes_active)
      f.write('Number of votes by Common Users: %s\n' % num_votes_common)
      f.write('Total Number of votes cast: %s\n' % (num_votes_experts
                                                    + num_votes_active
                                                    + num_votes_common))

    log('Ground Truth Top 10')
    for i in range(10):
      url, count = gt_rankings[i]
      log('[%s] %s\t%s' %(i, url.strip(), count))
    log('-----------------------------------')
    log('Market Top 10')
    for i in range(10):
      url, count = market_rankings[i]
      log('[%s] %s\t%s' %(i, url.strip(), count))
    log('-----------------------------------')
    log('Expert Top 10')
    for i in range(10):
      url, count = expert_rankings[i]
      log('[%s] %s\t%s' %(i, url.strip(), count))
    log('-----------------------------------')
    log('Active Top 10')
    for i in range(10):
      url, count = active_rankings[i]
      log('[%s] %s\t%s' %(i, url.strip(), count))
    log('-----------------------------------')
    log('Common Top 10')
    for i in range(10):
      url, count = common_rankings[i]
      log('[%s] %s\t%s' %(i, url.strip(), count))
      
    ground_truth_url_to_rank = {}
    for rank, (url, count) in enumerate(gt_rankings):
      ground_truth_url_to_rank[url] = rank
    market_rank_to_url = {}
    experts_rank_to_url = {}
    active_rank_to_url = {}
    common_rank_to_url = {}
    for rank, (url, count) in enumerate(expert_rankings):
      experts_rank_to_url[rank] = url
    for rank, (url, count) in enumerate(market_rankings):
      market_rank_to_url[rank] = url
    for rank, (url, count) in enumerate(active_rankings):
      active_rank_to_url[rank] = url
    for rank, (url, count) in enumerate(common_rankings):
      common_rank_to_url[rank] = url
    avg_diffs_expert = calculate_diff_avg(ground_truth_url_to_rank,
                                          experts_rank_to_url)
    avg_diffs_market = calculate_diff_avg(ground_truth_url_to_rank,
                                          market_rank_to_url)
    avg_diffs_active = calculate_diff_avg(ground_truth_url_to_rank,
                                          active_rank_to_url)
    avg_diffs_common = calculate_diff_avg(ground_truth_url_to_rank,
                                          common_rank_to_url)

    draw_graph(avg_diffs_expert, avg_diffs_market, avg_diffs_active,
               avg_diffs_common, delta)


def log(message):
  """Helper method to modularize the format of log messages.
  
  Keyword Arguments:
  message -- A string to log.
  """
  FileLog.log(_LOG_FILE, message)
  

if __name__ == "__main__":
    run()
