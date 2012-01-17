import os

import Configuration
import Util

import matplotlib
matplotlib.use("Agg")

from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt
import matplotlib.axis

_DATA_DIR = '/dfs/birch/tsv'
_YEAR = 2011
_MONTHS = ['08', '09', '10', '11']

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


def draw_active_users_graph(avg_num_tweets):
  """Plots avg number of tweets per month graph using matplotlib.

  This graph shows the average number of tweets per month by percentile.
  The date comes in the format of a list with 100 elements, the first being
  the avg number for the top 1% of users, the second being the 2nd %, etc.

  Keyword Arguments:
  avg_num_tweets -- The data for this graph, as described above.
  """
  figure = plt.figure()
  ax = figure.add_subplot(111)
  myplt = ax.plot(avg_num_tweets)
  plt.axis([1, 101, 0, avg_num_tweets[0]])
  plt.grid(True, which='major', linewidth=2)
  ax.xaxis.set_minor_locator(MultipleLocator(5))
  ax.yaxis.set_minor_locator(MultipleLocator(5))
  plt.grid(True, which='minor')
  plt.xlabel('percentile')
  plt.ylabel('Average Number Tweets per Month')
  plt.title('Average Number Tweets per Month by Percentile')

  with open(_GRAPH_DIR + 'num_avg_tweets.png', 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + 'num_avg_tweets.eps', 'w') as graph:
    plt.savefig(graph, format='eps')

  print 'Outputted graph: Average Numer Tweets per Month by Percentile'


def gather_tweet_counts():
  """Gathers the num tweets per user.

  This function looks at the tweet files over the period of
  the month in question, and returns a dictionary of user id
  to number of tweets.

  Returns:
  user_id_to_tweet_count -- A dictionary mapping user id's to tweet
                            count.
  """
  user_id_to_tweet_count = {}
  for month in _MONTHS:
    print 'Parsing %s/%s' %(month, _YEAR)
    training_dir = '%s/%s_%s' %(_DATA_DIR, _YEAR, month)
    for filename in os.listdir(training_dir):
      if '.tweet' in filename:
        data_file = '%s/%s' %(training_dir, filename)
        with open(data_file) as f:
          for line in f:
            tokens = line.split('\t')
            user_id = tokens[_TWEETFILE_USER_ID_INDEX]
            if user_id_to_tweet_count.has_key(user_id):
              user_id_to_tweet_count[user_id] += 1
            else:
              user_id_to_tweet_count[user_id] = 1

  return user_id_to_tweet_count


def output_top_users(user_id_sorted_by_tweet_count):
  """Outputs the top X users to a tsv file.
  
  Keyword Arguments:
  user_id_sorted_by_tweet_count -- A list of user_id, tweet count tuples
                                   sorted by tweet counts.
  """
  filename = '%stop_%s_active_users.tsv' %(_GRAPH_DIR, _NUM_TOP_USERS_TO_OUTPUT)
  with open(filename, 'w') as f:
    for i in range(_NUM_TOP_USERS_TO_OUTPUT):
      user_id, tweet_count = user_id_sorted_by_tweet_count[i]
      line = '%s\t%s\n' %(user_id, tweet_count / (len(_MONTHS) * 1.0))
      f.write(line)


def run():
  """Main logic of this analysis.

  A high level overview of the logic follows:

  1. Gathers the tweet counts for each user over the months in question.
  2. Sorts the users by highest number of tweets.
  3. Outputs the top X number of users to disk.
  4. Caclulates the average number of tweets per month for each percent.
  5. Outputs this avg number by percent in graph form.
  """
  user_id_to_tweet_count = gather_tweet_counts()

  user_id_sorted_by_tweet_count = sorted(user_id_to_tweet_count.items(),
                                         key=lambda x: x[1], reverse=True)

  output_top_users(user_id_sorted_by_tweet_count)
  
  avg_num_tweets = calculate_avg_num_tweets(user_id_sorted_by_tweet_count)

  draw_active_users_graph(avg_num_tweets)


if __name__ == "__main__":
    run()
