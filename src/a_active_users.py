"""
This module performs an analysis on active and inactive users. It attempts to
shed more light on which users are active vs inactive, and help set a boundary
condition for determining active vs. inactive users. It outputs three things:

    1. The first graph examines the average number of tweets for users per month
       in each percentile.
    2. The second graph examines the percentage change in avg number of tweets
       for users per month for each percentile.
    3. The third item is a tsv file that contains the top 100 active users, in
       descending order.

For more information, see:
http://cedar.cs.ucla.edu/wiki/index.php/Identify_Experts

Functions:
calculate_avg_changes_in_activity -- Calculates the avg changes in activity for
                                     the second graph.
calculate_avg_num_tweets -- Calculates the average numner of tweets per month.
calculate_user_percentile -- Calculates the percentile to which each user
                             belonds.
draw_active_users_graph -- Draws the active users graph (graph #1).
draw_percentage_change_graph -- Draws the percentage change graph (graph #2).
gather_tweet_counts -- Parses total tweet counts per users from data files.
output_top_users -- Outputs the top 100 users to tsv file in descending order.
run -- Main logic.

__author__ = 'Chris Moghbel (cmoghbel@cs.ucla.edu)'
"""
import os

import Configuration
import Util

import matplotlib
matplotlib.use("Agg")

from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt

_DATA_DIR = '/dfs/birch/tsv'
_YEAR = 2011
_MONTHS = ['09', '10', '11', '12']

_NUM_TOP_USERS_TO_OUTPUT = 100

_GRAPH_DIR = None # defined right after _get_graph_output_dir

_TWEETFILE_TWEET_ID_INDEX = 0
_TWEETFILE_USER_ID_INDEX = 1
_TWEETFILE_TWEET_TEXT_INDEX = 2
_TWEETFILE_CREATED_AT_INDEX = 3
_TWEETFILE_RETWEETED_INDEX = 4
_TWEETFILE_RETWEET_COUNT_INDEX = 5
_TWEETFILE_ORIGIN_USER_ID_INDEX = 6
_TWEETFILE_ORIGIN_TWEET_ID_INDEX = 7
_TWEETFILE_SOURCE_INDEX = 8
_TWEETFILE_FILTER_WORDS_INDEX = 9
_TWEETFILE_INSERT_TIMESTAMP_INDEX = 10


def _get_graph_output_dir():
  """Assign an output path for the graph(s)."""
  cfg = Configuration.getConfig()
  graph_dir = cfg.get('Path', 'base-dir') + cfg.get('Path', 'graph-dir')
  graph_dir += 'ActiveUsers/'
  Util.ensure_dir_exist(graph_dir)
  return graph_dir


_GRAPH_DIR = _get_graph_output_dir()


def calculate_avg_num_tweets(user_id_sorted_by_tweet_count):
  """Calculates the avg num of tweets per month for users in each percentile.

  Keyword Arguments:
  user_id_sorted_by_tweet_count - A sorted list of tuples, with the
                                  first element the user id, and the second
                                  element the number of tweets, sorted by
                                  number of tweets.

  Returns:
  avg_num_tweets -- A list of avg number of tweets for each percentile
                    (ie 1%, 2%, 3%, etc.)
  """
  avg_num_tweets = []
  bucket_size = len(user_id_sorted_by_tweet_count) / 100
  accum = 0
  for i in range(len(user_id_sorted_by_tweet_count)):
    user_id, tweet_count = user_id_sorted_by_tweet_count[i]
    accum += tweet_count
    if i is not 0 and i % bucket_size is 0:
      # Need to remember to divide by number of months.
      avg_num_tweets.append((accum / bucket_size) / (len(_MONTHS) * 1.0))
      accum = 0

  return avg_num_tweets


def calculate_avg_change_activity(id_to_count_training, id_to_count_testing,
                                  id_to_percentile):
  """Calculates the avg change in activity for each percentile.

  Keyword Arguments:
  id_to_count_training -- A dictionary mapping user id's to total number tweets
                          during the training set.
  id_to_count_testing -- A dictionary mapping user id's to total number tweets
                         during the testing set.
  id_to_percentile -- A dictionary mapping user id's to the percentile to which
                      they belong.

  Returns:
  avg_change -- A list of avg_changes in decreasing order of percentile.
                (ie 1st value is for 1%, 2nd value for 2nd %, etc.)
  """
  num_tweets_training = [0 for i in range(100)]
  num_tweets_testing = [0 for i in range(100)]
  num_users_training = [0 for i in range(100)]
  num_users_testing = [0 for i in range(100)]
  avg_change = [0 for i in range(100)]

  for user_id, percentile in id_to_percentile.items():
    if id_to_count_training.has_key(user_id):
      num_tweets_training[percentile - 1] += id_to_count_training.get(user_id)
      num_users_training[percentile - 1] += 1
    if id_to_count_testing.has_key(user_id):
      num_tweets_testing[percentile - 1] += id_to_count_testing.get(user_id)
      num_users_testing[percentile - 1] += 1

  for i in range(100):
    num_tweets_training[i] /= (num_users_training[i] * 1.0)
    num_tweets_testing[i] /= (num_users_testing[i] * 1.0)
    num_tweets_training[i] /= (len(_MONTHS) * 1.0)
    num_tweets_testing[i] /= (len(_MONTHS) * 1.0) 

    training = num_tweets_training[i] 
    testing = num_tweets_testing[i] 
    change = (abs(testing - training) / (training * 1.0)) * 100
    avg_change[i] = change
  
  return avg_change


def calculate_user_percentile(user_id_sorted_by_tweet_count):
  """Calculates the percentile each user belonds to.

  Keyword Arguments:
  user_id_sorted_by_tweet_count - A sorted list of tuples, with the
                                  first element the user id, and the second
                                  element the number of tweets, sorted by
                                  number of tweets.

  Returns:
  user_id_to_percentile -- A dictionary mapping user id's to percenticles.
  """
  num_users = len(user_id_sorted_by_tweet_count)
  bucket_size = num_users / 100
  user_id_to_percentile = {}
  current_percentile = 1
  for i in range(num_users):
    user_id, tweet_count = user_id_sorted_by_tweet_count[i]
    user_id_to_percentile[user_id] = current_percentile
    if i is not 0 and i % bucket_size is 0:
      # Dont increase percentile past 100. We need to do this because we need
      # bucket size to be a integer, but to have 100 even buckets we would need
      # decimal bucket sizes. This takes care of this "rounding issue".
      if current_percentile < 100:
        current_percentile += 1
  return user_id_to_percentile
    

def draw_active_users_graph(avg_num_tweets):
  """Plots avg number of tweets per month graph using matplotlib.

  This graph shows the average number of tweets per month by percentile.
  The data comes in the format of a list with 100 elements, the first being
  the avg number for the top 1% of users, the second being the 2nd %, etc.

  Keyword Arguments:
  avg_num_tweets -- The data for this graph, as described above.
  """
  figure = plt.figure()
  axs = figure.add_subplot(111)
  axs.plot([i for i in range(1, 101)], avg_num_tweets)
  plt.axis([0, 101, 0, avg_num_tweets[0] + 1])
  plt.grid(True, which='major', linewidth=2)
  axs.xaxis.set_minor_locator(MultipleLocator(5))
  axs.yaxis.set_minor_locator(MultipleLocator(5))
  plt.grid(True, which='minor')
  plt.xlabel('Users Sorted by Activeness (%)', fontsize='16')
  plt.ylabel('Average Number Tweets per Month', fontsize='16')

  with open(_GRAPH_DIR + 'num_avg_tweets.png', 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + 'num_avg_tweets.eps', 'w') as graph:
    plt.savefig(graph, format='eps')

  print 'Outputted graph: Average Number Tweets per Month by Percentile'


def draw_percentage_change_graph(avg_change):
  """Plots avg percentage change graph using matplotlib.

  This graph shows the average percentage change in avg numner of tweets per
  user by percentile.

  The data comes in the format of a list with 100 elements, the first being
  the avg change for the top 1% of users, the second being the 2nd %, etc.

  Keyword Arguments:
  avg_num_tweets -- The data for this graph, as described above.
  """
  figure = plt.figure()
  axs = figure.add_subplot(111)
  axs.plot([i for i in range(1, 101)], avg_change)
  plt.axis([0, 101, 0, avg_change[0] + .25])
  plt.grid(True, which='major', linewidth=2)
  axs.xaxis.set_minor_locator(MultipleLocator(5))
  axs.yaxis.set_minor_locator(MultipleLocator(1))
  plt.grid(True, which='minor')
  plt.xlabel('percentile')
  plt.ylabel('Average Percentage Change')

  with open(_GRAPH_DIR + 'percentage_change.png', 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + 'percentage_change.eps', 'w') as graph:
    plt.savefig(graph, format='eps')

  print 'Outputted Graph: Average Percentage Change in Activity by Percentile'  


def gather_tweet_counts():
  """Gathers the num tweets per user.

  This function looks at the tweet files over the period of
  the month in question, and returns a dictionary of user id
  to number of tweets. It also returns a similiar dictionary
  for both a training set and a testing set. The training set is defined
  as the first two months, with the testing set being the second two months.

  Returns:
  user_id_to_tweet_count -- A dictionary mapping user id's to tweet
                            count.
  id_to_count_training -- A dictionary mapping user id's to tweet count for the
                          training set.
  id_to_count_testing -- A dictionary mapping user id's to tweet count for the
                         testing set.
  """
  user_id_to_tweet_count = {}
  id_to_count_training = {}
  id_to_count_testing = {}
  for month in _MONTHS:
    print 'Parsing %s/%s' % (month, _YEAR)
    training_dir = '%s/%s_%s' % (_DATA_DIR, _YEAR, month)
    for filename in os.listdir(training_dir):
      if '.tweet' in filename and 'http_nyti_ms' in filename:
        data_file = '%s/%s' % (training_dir, filename)
        with open(data_file) as in_file:
          for line in in_file:
            tokens = line.split('\t')
            user_id = tokens[_TWEETFILE_USER_ID_INDEX]
            if user_id_to_tweet_count.has_key(user_id):
              user_id_to_tweet_count[user_id] += 1
            else:
              user_id_to_tweet_count[user_id] = 1
            if month is _MONTHS[0] or month is _MONTHS[1]:
              if id_to_count_training.has_key(user_id):
                id_to_count_training[user_id] += 1
              else:
                id_to_count_training[user_id] = 1
            else:
              if id_to_count_testing.has_key(user_id):
                id_to_count_testing[user_id] += 1
              else:
                id_to_count_testing[user_id] = 1
                
  print "Size of users (total): " + str(len(user_id_to_tweet_count.keys()))
  return user_id_to_tweet_count, id_to_count_training, id_to_count_testing


def output_top_users(user_id_sorted_by_tweet_count):
  """Outputs the top X users to a tsv file.
  
  Keyword Arguments:
  user_id_sorted_by_tweet_count -- A list of user_id, tweet count tuples
                                   sorted by tweet counts.
  """
  filename = '%stop_%s_active_users.tsv' % (_GRAPH_DIR,
                                            _NUM_TOP_USERS_TO_OUTPUT)
  with open(filename, 'w') as out_file:
    for i in range(_NUM_TOP_USERS_TO_OUTPUT):
      user_id, tweet_count = user_id_sorted_by_tweet_count[i]
      line = '%s\t%s\n' % (user_id, tweet_count / (len(_MONTHS) * 1.0))
      out_file.write(line)


def run():
  """Main logic of this analysis.

  A high level overview of the logic follows:

  1. Gathers the tweet counts for each user over the months in question.
  2. Sorts the users by highest number of tweets.
  3. Outputs the top X number of users to disk.
  4. Caclulates the average number of tweets per month for each percent.
  5. Outputs this avg number by percent in graph form.
  6. Calculates the avg change between testing and training for each percentile.
  7. Outputs this avg change by percentile in graph form.
  """
  (user_id_to_tweet_count, id_to_count_testing,
                           id_to_count_training) = gather_tweet_counts()

  user_id_sorted_by_tweet_count = sorted(user_id_to_tweet_count.items(),
                                         key=lambda x: x[1], reverse=True)

  output_top_users(user_id_sorted_by_tweet_count)
  
  avg_num_tweets = calculate_avg_num_tweets(user_id_sorted_by_tweet_count)

  draw_active_users_graph(avg_num_tweets)
  
  id_to_percentile = calculate_user_percentile(user_id_sorted_by_tweet_count)
  
  avg_changes = calculate_avg_change_activity(id_to_count_training,
                                              id_to_count_testing,
                                              id_to_percentile)
  
  draw_percentage_change_graph(avg_changes)
  

if __name__ == "__main__":
  run()
