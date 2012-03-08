"""This analysis attempts to determine the impact of social hub bias.

__author__ = 'Chris Moghbel (cmoghbel@cs.ucla.edu)
"""
import FileLog
import Util
import URLUtil
import crawl_users
import ground_truths
from ground_truths import DataSet

import os
from datetime import datetime
from datetime import timedelta

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

import tweepy

from constants import _TWEETFILE_TWEET_TEXT_INDEX
from constants import _TWEETFILE_USER_ID_INDEX
from constants import _TWEETFILE_CREATED_AT_INDEX

from constants import _RATES_FILE_USER_ID_INDEX
from constants import _RATES_FILE_RATE_INDEX

from constants import _WINDOW_MONTHS 
from constants import _DATETIME_FORMAT

_DRAW_GRAPH = True
_REGENERATE_RATES = False
_RECRAWL_USER_INFO = False
_DEBUG = False

_DELTA = 4
_SIZE_TOP_NEWS = .02
_MAX_USERS = 20000

_LOG_FILE = 'a_social_hub_bias.log'
_OUTPUT_DIR = '../data/SocialHubBias/'
_GRAPH_DIR = Util.get_graph_output_dir('SocialHubBias/')


class Participant:
  """Contains information regarding a participant in a news story."""

  def __init__(self, user_id, delta, time):
    """Initialize a Participant instance.

    Keyword Arguments:
    user_id -- (str) The users twitter id.
    delta -- (int) The number of hours after this user becomes a participant
             we should keep counting tweets.
    """
    self.user_id = user_id
    self.deltatime = timedelta(hours=delta)
    self.time_tweeted = time
    self.count = 0

  def notify_tweet_found(self, time):
    """Notifies this user that the news story was tweeted.

    Keyword Arguments:
    time -- (datetime) The time the tweet was tweeted.
    """
    if time - self.time_tweeted < self.deltatime:
      self.count += 1


class NewsParticipants:
  """Keeps a list of participants, or listeners. Broadcasts
     new tweet information to all participants."""

  def __init__(self, delta):
    """Initialize a NewsParticipants instance.
    
    Keyword Arguments:
    delta -- (int) Window time, in hours.
    """
    self.delta = delta
    self.participants = []

  def broadcast(self, user_id, time):
    """Broadcasts new tweet information to all participants.
    
    Keyword Arguments:
    user_id -- (str) The twitter id of the tweet's author.
    time -- (datetime) The time at which the tweet was tweeted.
    """
    new_participant = True
    for participant in self.participants:
      if participant.user_id == user_id:
        new_participant = False
      else:
        participant.notify_tweet_found(time)
    if new_participant:
      self.participants.append(Participant(user_id, self.delta, time))


def draw_graph(rates, num_followers):
  """Draws a scatter plot.

  Keyword Arugments:
  rates -- (List<float>) the rates
  num_followers -- (List<int>) the matching num followers
  """
  figure = plt.figure()
  axs = figure.add_subplot(111)

  axs.scatter(num_followers, rates)

  plt.xlabel('Num Followers')
  plt.ylabel('Rate')

  plt.axis([0, max(num_followers), 0, max(rates)])

  with open(_GRAPH_DIR + 'social_hub_bias.png', 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + 'social_hub_bias.eps', 'w') as graph:
    plt.savefig(graph, format='eps')

  plt.close()



def gather_rates(seeds, cache, top_news, months, delta):
  """Aggregates information accross every tweet.

  For every url found, the authors twitter id, the url, and the time at
  which it was tweeted is broadcast to a set of listeners for that url.
  Each listener, or participant, can than decide if that tweet fits
  within their window.

  Keyword Arguments:
  seeds -- Dict<str, (_, _, datetime) url -> _, _, seed_time
  cache -- Dict<str, str> short_url -> long_url
  months -- (List<str>) months, as 2-digit number strings
  delta -- (int) in hours

  Returns:
  participants -- (Dict<str, NewsParticipants>) url -> NewsParticipants
  """
  participants = {}
  for month in months:
    log('Parsing tweets from month %s with delta %s...' % (month, delta))
    dir_name = Util.get_data_dir_name_for(month) 
    for filename in os.listdir(dir_name):
      if '.tweet' in filename and 'http_nyti_ms' in filename:
        data_file = '%s/%s' % (dir_name, filename)
        with open(data_file) as input_file:
          for line in input_file:
            tokens = line.split('\t')
            tweet_text = tokens[_TWEETFILE_TWEET_TEXT_INDEX]
            urls = URLUtil.parse_urls(tweet_text, cache)
            for url in urls:
              if url in top_news:
                _, _, seed_time = seeds[url]
                if Util.is_in_dataset(seed_time, DataSet.ALL):
                  user_id = tokens[_TWEETFILE_USER_ID_INDEX]
                  created = datetime.strptime(
                      tokens[_TWEETFILE_CREATED_AT_INDEX],
                      _DATETIME_FORMAT)
                  if not url in participants:
                    participants[url] = NewsParticipants(delta)
                  participants[url].broadcast(user_id, created)
  return participants


def calc_rates(news_to_participants):
  """Calculates the rates for each user.

  Iterates over all news stories, then all participants for that story.

  Keyword Arguments:
  news_to_participants -- (Dict<str, NewsParticipants>) url -> NewsParticipants

  Returns:
  Dict<str, (int, int)> user_id -> rate
  """
  log('Calculating rates...')
  user_to_rate = {}
  for news_participants in news_to_participants.values():
    for participant in news_participants.participants:
      user_id = participant.user_id
      if user_id in user_to_rate:
        sum_counts, total_num_stories = user_to_rate[user_id]
        user_to_rate[user_id] = (sum_counts + participant.count,
                                 total_num_stories + 1.)
      else:
        user_to_rate[user_id] = (participant.count, 1.)

  # Do division here so output method matches load method.
  for user_id, (count, num_stories) in user_to_rate.items():
    user_to_rate[user_id] = count / num_stories
  return user_to_rate


def load_rates():
  """Loads rates from disk."""
  log('Loading rates...')
  user_to_rate = {}
  with open(_OUTPUT_DIR + 'user_rates.tsv') as in_file:
    for line in in_file:
      tokens = line.split('\t')
      user_id = tokens[_RATES_FILE_USER_ID_INDEX]
      rate = float(tokens[_RATES_FILE_RATE_INDEX])
      user_to_rate[user_id] = rate
  return user_to_rate


def load_bad_users():
  """Loads a set of 'blacklisted' user ids from disk."""
  log('Loading bad users...')
  Util.ensure_dir_exist(_OUTPUT_DIR)
  bad_users = set()
  if not os.path.exists(_OUTPUT_DIR + 'bad_users.tsv'):
    return bad_users
  with open(_OUTPUT_DIR + 'bad_users.tsv') as in_file:
    for line in in_file:
      user_id = line.strip()
      bad_users.add(user_id)
  return user_id


def output_data(user_to_rate):
  """Outputs intermediary rate data to disk.

  Keyword Arguments:
  user_to_rate -- (Dict<str, (int, int)) user_id -> (count, num_stories)
                  Contains the info to calculate the rate for each user.
  """
  log('Outputting rate data to disk...')
  Util.ensure_dir_exist(_OUTPUT_DIR)
  with open(_OUTPUT_DIR + 'user_rates.tsv', 'w') as out_file:
    for user_id, rate in user_to_rate.items():
      out_file.write('%s\t%s\n' % (user_id, rate))


def get_missing_user_info(user_to_rate):
  """Get user info for any users not already crawled.

  Keyword Arguments:
  user_to_rate -- (Dict<str, float>) user_id -> rate

  Returns:
  user_info -- (Set<crawl_users.User>) new users
  """
  log('Updating user info...')
  user_info = crawl_users.load_user_info()
  users_without_info = set()
  for user_id in user_to_rate:
    if not user_id in user_info:
      users_without_info.add(user_id)
  crawl_users.get_user_info(tweepy.API(), users_without_info)


def remove_rates_for_missing_users():
  """Removes rate info for any users for whom info could not be found."""
  log('Removing rates for users who could not be found...')
  user_to_rate = load_rates()
  user_info = crawl_users.load_user_info()
  user_ids_to_remove = set()
  for user_id in user_to_rate:
    if user_id not in user_info:
      user_ids_to_remove.add(user_id)

  for user_id in user_ids_to_remove:
    del user_to_rate[user_id]

  output_data(user_to_rate)


def remove_bad_users(user_to_rate):
  """Removes 'blacklisted' users from loaded rate info."""
  log('Removing rates for blacklisted users...')
  bad_users = load_bad_users()
  for user_id in bad_users:
    if user_id in user_to_rate:
      del user_to_rate[user_id]


def run():
  """The main logic of this analysis."""
  global _OUTPUT_DIR # pylint: disable-msg=W0603
  if _DEBUG:
    _OUTPUT_DIR += 'debug/'
    crawl_users._OUTPUT_DIR += 'debug/'

  if _REGENERATE_RATES:
    cache = Util.load_cache()
    seeds = Util.load_seeds()

    gt_rankings = ground_truths.get_gt_rankings(seeds, DataSet.ALL)
    target_news = ground_truths.find_target_news(gt_rankings, _SIZE_TOP_NEWS)

    news_to_participants = gather_rates(seeds, cache, target_news,
                                        _WINDOW_MONTHS, _DELTA)
    user_to_rate = calc_rates(news_to_participants)
    output_data(user_to_rate)

  if _RECRAWL_USER_INFO:
    user_to_rate = load_rates()
    remove_bad_users(user_to_rate)
    if _DEBUG:
      user_to_rate = dict(user_to_rate.items()[:10])
    get_missing_user_info(user_to_rate)
    remove_rates_for_missing_users()

  if _DRAW_GRAPH:
    user_to_rate = load_rates()
    user_info = crawl_users.load_user_info()
    rates = []
    num_followers = []
    for user_id in user_to_rate:
      if user_id in user_info:
        rates.append(user_to_rate[user_id])
        num_followers.append(user_info[user_id].followers_count)
    log('Outputting Graph...')
    draw_graph(rates, num_followers)
  log('Analysis done!')
  

def log(message):
  """Helper method to modularize the format of log messages.
    
    Keyword Arguments:
    message -- A string to print.
  """  
  FileLog.log(_LOG_FILE, message)


if __name__ == "__main__":
  run()
