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

Tweet counts for the user groups (market, newsaholics, active users, and common
users) are counted if they occur within a certain time delta of the original
introduction of that url.

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
from datetime import timedelta
import math
from math import sqrt


_USER_ACTIVITY_FILE_ID_INDEX = 0
_USER_ACTIVITY_FILE_COUNT_INDEX = 1

_TIMEDELTAS_FILE_TWEET_ID_INDEX = 0
_TIMEDELTAS_FILE_USER_ID_INDEX = 1 
_TIMEDELTAS_FILE_DELTA_INDEX = 2
_TIMEDELTAS_FILE_URL_INDEX = 3

_GRAPH_DIR = Util.get_graph_output_dir('FolkWisdom/')
_LOG_FILE = 'aFolkWisdom.log'
_DELTAS = [1, 4, 8] # Given in hours.


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


def draw_graph(newsaholic_diffs, market_diffs, active_diffs, common_diffs,
               delta):
  """Draws the graph for avg diffs.
  
  Keyword Arguments:
  newsaholics_diffs -- The diffs in raking between newsaholics and truth.
  market_diffs -- The diffs in raking between the market and the truth.
  active_diffs -- The diffs in ranking between active users and truth.
  common_diffs -- The diffs in ranking between common users and truth.
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

  plt.legend(plots, ['Market', 'News-aholics', 'Active Users', 'Common Users'],
             loc=0)

  max_y = max([max(market_diffs), max(newsaholic_diffs), max(active_diffs),
               max(common_diffs)])
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
  plt.title('Ranking Performance by User Group with %s Hour Delta' % delta)

  with open(_GRAPH_DIR + 'ranking_performance_%s.png' % delta, 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + 'ranking_performance_%s.eps' % delta, 'w') as graph:
    plt.savefig(graph, format='eps')

  log('Outputted graph: Ranking Performance by User Group with %s Hour Delta'
      % delta)
  plt.close()


def gather_tweet_counts(newsaholics, active, hours=None):
  """Gathers the tweet counts for a given set of months.
  
  Only counts votes if they occur within the given time delta from the seed
  time (except for the ground truth rankings).
  
  Keyword Arguments:
  newsaholics -- A set containing the user ids of 'newsaholic' users.
  active -- A set containing the user ids of 'active' users.
  hours -- The desired time delta, given in hours.
  
  Returns:
  gt_tweet_counts -- Dictionary of url to tweet count for all users.
  market_tweet_counts -- Dictionary of url to tweet count for the market.
  newsaholic_tweet_counts -- Dictionary of url to tweet count for newsaholics.
  active_tweet_counts -- Dictionary of url to tweet count for active users.
  common_tweet_counts -- Dictionary of url to tweet count for common users.
  """
  gt_tweet_counts = {}
  market_tweet_counts = {}
  newsaholic_tweet_counts = {}
  active_tweet_counts = {}
  common_tweet_counts = {}
  with open('../data/FolkWisdom/time_deltas.tsv') as f:
    for line in f:
      tokens = line.split('\t')
      url = tokens[_TIMEDELTAS_FILE_URL_INDEX]
      user_id = tokens[_TIMEDELTAS_FILE_USER_ID_INDEX]
      time_delta = timedelta(seconds=int(tokens[_TIMEDELTAS_FILE_DELTA_INDEX]))
      max_delta = timedelta.max
      if hours:
        max_delta = timedelta(hours=hours)
      if url in gt_tweet_counts:
        gt_tweet_counts[url] += 1
      else:
        gt_tweet_counts[url] = 1

      if time_delta < max_delta:
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
                
  return (gt_tweet_counts, market_tweet_counts, newsaholic_tweet_counts,
          active_tweet_counts, common_tweet_counts)


def get_rankings(delta, newsaholics, active_users):
  """Gets the true rankings, and ranking as determined by various user groups.
  
  Keyword Arguments:
  delta -- The time window, in hours.
  newsaholics -- A set of user ids representing newsaholic users.
  active_users -- A set of user ids representing active users.
  
  Returns:
  gt_rankings -- The ground truth rankings as a list of (url, count) pairs.
  market_rankings -- The rankings as given by the market, as a list of
  (url, count) pairs.
  newsaholic_rankings -- The rankings as given by newsaholic users, as a list
  of (url, count) pairs.
  active_rankings -- The rankings as given by active users, as a list of
  (url, count) pairs.
  common_rankings -- The rankings as given by common users, as a list of
  (url, count) pairs.
  """
  log('Getting Rankings')
  gtc, mtc, etc, atc, ctc = gather_tweet_counts(newsaholics, active_users,
                                                delta)
  gt_rankings = sorted(gtc.items(), key=lambda x: x[1], reverse=True)
  market_rankings = sorted(mtc.items(), key=lambda x: x[1], reverse=True)
  newsaholic_rankings = sorted(etc.items(), key=lambda x: x[1], reverse=True)
  active_rankings = sorted(atc.items(), key=lambda x: x[1], reverse=True)
  common_rankings = sorted(ctc.items(), key=lambda x: x[1], reverse=True)
  return (gt_rankings, market_rankings, newsaholic_rankings, active_rankings,
          common_rankings)


def group_users():
  """Groups users into 'newsaholic', 'active', and 'common' categories.
  
  Returns:
  newsaholics -- A python set of user ids for newsaholic users, defined as
  users in top 2% of users as ranked by activity.
  active_users -- A python set of user ids for active users, defined as users
  in between 2% and 25% of users as ranked by activity.
  common_users -- A python set of user ids for common users, defined as users
  whose rank is lower the 25% as ranked by activity.
  """
  log('Grouping Users')
  user_ids_sorted = []
  with open('../data/FolkWisdom/user_activity.tsv') as f:
    for line in f:
      tokens = line.split('\t')
      user_id = tokens[_USER_ACTIVITY_FILE_ID_INDEX]
      user_ids_sorted.append(user_id)
  num_users = len(user_ids_sorted)
  bucket_size = num_users / 100
  
  newsaholics = set()
  active_users = set()
  common_users = set()
  current_percentile = 1
  for i in range(num_users):
    user_id = user_ids_sorted[i]
    if current_percentile < 3:
      newsaholics.add(user_id)
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
  return newsaholics, active_users, common_users


def run():
  """Contains the main logic for this analysis.
  
  A high level overview of the logic is as follows:
  
  1. Load a cache of short urls to long urls
  2. Group users into newsaholic, active, and common groups.
  3. Get both the true rankings, and the rankings as given by each group.
  4. Compare group rankings against the ground truth rankings.
  5. Draw graph.
  """
  FileLog.set_log_dir()

  newsaholics, active_users, common_users = group_users()
  log('Num newsaholics: %s' % len(newsaholics))
  log('Num active: %s' % len(active_users))
  log('Num common: %s' % len(common_users))

  for delta in _DELTAS:
    log('Finding rankings with an %s hour delta.' % delta)
    (gt_rankings, market_rankings, newsaholic_rankings,
     active_rankings, common_rankings) = get_rankings(delta, newsaholics,
                                                      active_users)

    with open('../data/report/ground_truth_rankings_%s.tsv' % delta, 'w') as f:
      for url, count in gt_rankings:
        f.write('%s\t%s\n' % (url.strip(), count))
    with open('../data/report/market_rankings_%s.tsv' % delta, 'w') as f:
      for url, count in market_rankings:
        f.write('%s\t%s\n' % (url.strip(), count))
    with open('../data/report/newsaholic_rankings_%s.tsv' % delta, 'w') as f:
      for url, count in newsaholic_rankings:
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

    with open('../data/report/user_demographics_%s.txt' % delta, 'w') as f:
      f.write('Number of Newsaholics: %s\n' % len(newsaholics))
      f.write('Number of Active Users: %s\n' % len(active_users))
      f.write('Number of Common Users: %s\n' % len(common_users))
      f.write('Number of Users (Total): %s\n' % (len(newsaholics)
                                                 + len(active_users)
                                                 + len(common_users)))
      f.write('\n')
      f.write('Number of votes by Newsaholics: %s\n' % num_votes_newsaholics)
      f.write('Number of votes by Market: %s\n' % num_votes_market)
      f.write('Number of votes by Active Users: %s\n'  % num_votes_active)
      f.write('Number of votes by Common Users: %s\n' % num_votes_common)
      f.write('Total Number of votes cast: %s\n' % (num_votes_newsaholics
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
    log('Newsaholic Top 10')
    for i in range(10):
      url, count = newsaholic_rankings[i]
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
    newsaholic_rank_to_url = {}
    active_rank_to_url = {}
    common_rank_to_url = {}
    for rank, (url, count) in enumerate(newsaholic_rankings):
      newsaholic_rank_to_url[rank] = url
    for rank, (url, count) in enumerate(market_rankings):
      market_rank_to_url[rank] = url
    for rank, (url, count) in enumerate(active_rankings):
      active_rank_to_url[rank] = url
    for rank, (url, count) in enumerate(common_rankings):
      common_rank_to_url[rank] = url
    avg_diffs_newsaholic = calculate_diff_avg(ground_truth_url_to_rank,
                                          newsaholic_rank_to_url)
    avg_diffs_market = calculate_diff_avg(ground_truth_url_to_rank,
                                          market_rank_to_url)
    avg_diffs_active = calculate_diff_avg(ground_truth_url_to_rank,
                                          active_rank_to_url)
    avg_diffs_common = calculate_diff_avg(ground_truth_url_to_rank,
                                          common_rank_to_url)

    draw_graph(avg_diffs_newsaholic, avg_diffs_market, avg_diffs_active,
               avg_diffs_common, delta)


def log(message):
  """Helper method to modularize the format of log messages.
  
  Keyword Arguments:
  message -- A string to log.
  """
  FileLog.log(_LOG_FILE, message)
  

if __name__ == "__main__":
    run()
