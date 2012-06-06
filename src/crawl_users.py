"""
This module contains a method for finding user infomation for a given set of
users.

Queries Twitter REST api via tweepy.

__author__ = 'Chris Moghbel (cmoghbel@cs.ucla.edu)'
"""
import FileLog
import Util

import os
import codecs
import time
import pprint
from datetime import datetime

import tweepy

from constants import _USER_INFO_FILE_ID_INDEX
from constants import _USER_INFO_FILE_SCREEN_NAME_INDEX
from constants import _USER_INFO_FILE_NAME_INDEX
from constants import _USER_INFO_FILE_FOLLOWERS_COUNT_INDEX
from constants import _USER_INFO_FILE_STATUSES_COUNT_INDEX
from constants import _USER_INFO_FILE_FRIENDS_COUNT_INDEX
from constants import _USER_INFO_FILE_CREATED_AT_INDEX
from constants import _USER_INFO_FILE_LISTED_COUNT_INDEX
from constants import _USER_INFO_FILE_VERIFIED_INDEX
from constants import _USER_INFO_FILE_UTC_INDEX
from constants import _USER_INFO_FILE_TIME_ZONE_INDEX
from constants import _USER_INFO_FILE_LANG_INDEX
from constants import _USER_INFO_FILE_TIMESTAMP_CRAWLED_INDEX

from constants import _DATETIME_FORMAT

_LOG_FILE = 'crawl_users.log'
_OUTPUT_DIR = '../data/SocialHubBias/'


def check_rate_limit_and_wait_if_needed(api): # pylint: disable-msg=C0103
  """Waits if twitter rate limit is about to be exceeded.
  
  Keyword Argument:
  api -- (tweepy.API) api instance being used to make calls.
  """
  while True:
    try:
      hits_remaining = api.rate_limit_status()['remaining_hits']
      if hits_remaining < 100:
        log('Rate limit status low, waiting for 15 min...')
        time.sleep(10 * 60)
      else:
        return
    except tweepy.error.TweepError, err: # pylint: disable-msg=E1101
      log('%s' % err)
      log('Error checking wait limit status, waiting for 10 sec...')
      time.sleep(10)


def get_user_info(api, user_ids):
  """Queries twitter for user information.

  Keyword Arguments:
  api -- (tweepy.API)
  user_ids -- (Set<int>) twitter ids to get info for.

  Returns:
  """
  log('Querying twitter for user info...')
  Util.ensure_dir_exist(_OUTPUT_DIR)
  with codecs.open(_OUTPUT_DIR + 'user_info.tsv', 'a',
                   encoding='utf-8') as out_file:
    with codecs.open(_OUTPUT_DIR + 'bad_user.tsv', 'a',
                     encoding='utf-8') as bad_file:
      count = 1
      for user_id in user_ids:
        check_rate_limit_and_wait_if_needed(api)
        retry_5xx = 3
        while retry_5xx > 0:
          try:
            log('%s: %s' % (count, user_id))            
            tweepy_user = api.get_user(int(user_id))
            user = User.from_tweepy_user(tweepy_user)
            output_user(out_file, user)
            retry_5xx = 0
          except tweepy.error.TweepError, err: # pylint: disable-msg=E1101
            log('%s (user_id: %s)' % (err, user_id))
            if err.reason.startswith("Twitter error response: status code = 5"):
              retry_5xx -= 1
              log('Retrying user id %s' % user_id)
            else:
              retry_5xx = 0
              bad_file.write('%s\n' % user_id)
        count += 1


def load_user_info():
  """Loads previously crawled user infomation from disk.

  Returns:
  users -- (Dict<str, crawl_users.User>) user_id => user
  """
  log('Loading user_info...')
  users = {}
  user_info_file = _OUTPUT_DIR + 'user_info.tsv'
  if not os.path.exists(user_info_file):
    return users
  with codecs.open(user_info_file, encoding='utf-8') as in_file:
    for line in in_file:
      tokens = line.split('\t')
      user_id = tokens[_USER_INFO_FILE_ID_INDEX]
      screen_name = tokens[_USER_INFO_FILE_SCREEN_NAME_INDEX]
      name = tokens[_USER_INFO_FILE_NAME_INDEX]
      followers_count = int(tokens[_USER_INFO_FILE_FOLLOWERS_COUNT_INDEX])
      statuses_count = int(tokens[_USER_INFO_FILE_STATUSES_COUNT_INDEX])
      friends_count = int(tokens[_USER_INFO_FILE_FRIENDS_COUNT_INDEX])
      created_at = tokens[_USER_INFO_FILE_CREATED_AT_INDEX]
      listed_count = int(tokens[_USER_INFO_FILE_LISTED_COUNT_INDEX])
      verified = tokens[_USER_INFO_FILE_VERIFIED_INDEX].strip() == True
      utc_offset = tokens[_USER_INFO_FILE_UTC_INDEX]
      time_zone = tokens[_USER_INFO_FILE_TIME_ZONE_INDEX]
      lang = tokens[_USER_INFO_FILE_LANG_INDEX]
      timestamp_crawled = tokens[_USER_INFO_FILE_TIMESTAMP_CRAWLED_INDEX].strip()
      user = User(user_id, screen_name, name, followers_count, statuses_count,
                  friends_count, created_at, listed_count, verified, utc_offset,
                  time_zone, lang, timestamp_crawled)
      users[user_id] = user
  return users


def output_user(out_file, user):
  """Outputs user info to disk.

  Keyword Arguments:
  users -- (Set<tweepy.model.User>)
  """
  user_id = ''
  if user.id:
    user_id = str(user.id)
  screen_name = ''
  if user.screen_name:
    screen_name = user.screen_name.strip()
    screen_name = ('%r' % screen_name)
    screen_name = screen_name[2:-1] if screen_name[0] == 'u' else screen_name[1:-1]
  name = ''
  if user.name:
    name = user.name.strip()
    name = ('%r' % name)
    name = name[2:-1] if name[0] == 'u' else name[1:-1]
  followers_count = 0
  if user.followers_count:
    followers_count = user.followers_count
  statuses_count = 0 
  if user.statuses_count:
    statuses_count = user.statuses_count
  friends_count = 0
  if user.friends_count:
    friends_count = user.friends_count
  created_at = ''
  if user.created_at:
    created_at = str(created_at)
  listed_count = 0
  if user.listed_count:
    listed_count = user.listed_count
  verified = ''
  if user.verified != None:
    verified = str(user.verified)
  utc_offset = ''
  if user.utc_offset:
    utc_offset = str(utc_offset)
  time_zone = ''
  if user.time_zone:
    time_zone = user.time_zone.strip()
    time_zone = ('%r' % time_zone)
    time_zone = time_zone[2:-1] if time_zone[0] == 'u' else time_zone[1:-1]
  lang = ''
  if user.lang:
    lang = user.lang.strip()
    lang = ('%r' % lang)
    lang = lang[2:-1] if lang[0] == 'u' else lang[1:-1]
  out_file.write(u'%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n'
                 % (user_id, screen_name, name, followers_count, statuses_count,
                    friends_count, created_at, listed_count, verified,
                    utc_offset, time_zone, lang, datetime.now()))


class User:
  """Wrapper class for user infomation.

  Handy for referencing user information by logical name. Also, we don't
  want to be dependant on tweepy objects in other areas of our code.
  """
  def __init__(self, user_id, screen_name, name, followers_count,
               statuses_count, friends_count, created_at,
               listed_count, verified, utc_offset, time_zone, lang,
               timestamp_crawled):
    """Create a new instance of this class."""
    self.id = user_id # pylint: disable-msg=C0103
    self.screen_name = screen_name
    self.name = name
    self.followers_count = followers_count
    self.statuses_count = statuses_count
    self.friends_count = friends_count
    if isinstance(created_at, str):
      self.created_at = datetime.strptime(created_at, _DATETIME_FORMAT)
    else:
      self.created_at = created_at
    self.listed_count = listed_count
    self.verified = verified
    self.utc_offset = utc_offset
    self.time_zone = time_zone
    self.lang = lang
    if isinstance(timestamp_crawled, str):
      self.timestamp_crawled = datetime.strptime(timestamp_crawled, _DATETIME_FORMAT)
    else:
      self.timestamp_crawled = timestamp_crawled

  @classmethod
  def from_tweepy_user(cls, tweepy_user):
    """Factory method for creating a new User instance.

    Keyword Arguments:
    tweepy_user -- (tweepy.model.User) tweepy user instance to copy data from.

    Returns:
    A new User instance.
    """
    return User(tweepy_user.id, tweepy_user.screen_name, tweepy_user.name,
                tweepy_user.followers_count, tweepy_user.statuses_count,
                tweepy_user.friends_count, tweepy_user.created_at,
                tweepy_user.listed_count, tweepy_user.verified,
                tweepy_user.utc_offset, tweepy_user.time_zone,
                tweepy_user.lang, datetime.now())

  def __str__(self):
    """Create a pretty str representation."""
    return pprint.pformat(vars(self))
  

def log(message):
  """Helper method to modularize the format of log messages.
    
    Keyword Arguments:
    message -- A string to print.
  """  
  FileLog.log(_LOG_FILE, message)
