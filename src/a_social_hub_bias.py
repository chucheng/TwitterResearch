"""This analysis attempts to determine the impact of social hub bias.

__author__ = 'Chris Moghbel (cmoghbel@cs.ucla.edu)
"""
import FileLog
import Util
import crawl_users
import ground_truths
import basic_groups
import experts
import os
import tweepy

from ground_truths import DataSet

_RECRAWL_USER_INFO = True
_DEBUG = False

_DELTA = 4
_SAMPLE_SIZE = .02

_LOG_FILE = 'a_social_hub_bias.log'
_OUTPUT_DIR = '../data/SocialHubBias/'


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


def get_user_groups(delta, category=None):
  seeds = Util.load_seeds()

  log('Finding basic user groups for delta %s and category %s...' % (delta, category))
  (num_users, newsaholics, active_users, common_users) = basic_groups.group_users(delta, category)

  log('Finding precision experts for delta %s and category %s...' % (delta, category))
  experts_p = experts.select_experts_precision(newsaholics.union(active_users),
                                               num_users, delta, .02, category)

  log('Finding ground truths...')
  gt_rankings = ground_truths.get_gt_rankings(seeds, DataSet.TESTING, category)
  log('Finding target news...')
  target_news = ground_truths.find_target_news(gt_rankings, .02)
  size_target_news = len(target_news)

  log('Finding fscore experts for delta %s and category %s...' % (delta, category))
  experts_f = experts.select_experts_fscore(size_target_news, num_users,
                                            delta, .02, category)

  log('Finding ci experts for delta %s and category %s...' % (delta, category))
  experts_ci = experts.select_experts_ci(num_users, delta, .02, category)

  experts_all = experts_p.union(experts_f).union(experts_ci)

  return experts_all, newsaholics, active_users, common_users


def sample_user_group(group, sample_size):
  log('Sampling group, sample size %s...' % sample_size)
  while len(group) > sample_size:
    group.pop()
  return group


def find_users_to_crawl():
  user_info = crawl_users.load_user_info()
  user_ids_already_crawled = user_info.keys()
  bad_users = load_bad_users()
  experts, newsaholics, active_users, common_users = get_user_groups(_DELTA)

  sample_size = round(len(newsaholics.union(active_users).union(common_users)) * _SAMPLE_SIZE)

  newsaholics_sample = sample_user_group(newsaholics, sample_size)
  active_users_sample = sample_user_group(active_users, sample_size)
  common_users_sample = sample_user_group(common_users, sample_size)

  users_to_crawl = experts.union(newsaholics_sample).union(active_users_sample).union(common_users_sample)
  users_to_crawl = users_to_crawl.difference(bad_users).difference(user_ids_already_crawled)

  return users_to_crawl


def run():
  """The main logic of this analysis."""
  global _OUTPUT_DIR # pylint: disable-msg=W0603
  if _DEBUG:
    log('DEBUG: Changing output dir to .../debug/')
    _OUTPUT_DIR += 'debug/'
    crawl_users._OUTPUT_DIR += 'debug/'

  if _RECRAWL_USER_INFO:
    users_to_crawl = find_users_to_crawl()
    if _DEBUG:
      log('DEBUG: Reducing users to crawl to 10...')
      while len(users_to_crawl) > 10:
        users_to_crawl.pop()

    api = tweepy.API()
    log('Crawling %s users...' % len(users_to_crawl))
    crawl_users.get_user_info(api, users_to_crawl)

  log('Analysis done!')
  

def log(message):
  """Helper method to modularize the format of log messages.
    
    Keyword Arguments:
    message -- A string to print.
  """  
  FileLog.log(_LOG_FILE, message)


if __name__ == "__main__":
  run()
