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

from constants import _DATETIME_FORMAT

_NYTIMES_USER_ID = 807095
_NYTIMES_HANDLE = u'@nytimes'
_NYTIMES_NAME = u'The New York Times'

_POGUE_USER_ID = 9534522
_POGUE_HANDLE = u'@pogue'
_POGUE_NAME = u'David Pogue'

_FIVETHIRTYEIGHT_USER_ID = 16017475
_FIVETHIRTYEIGHT_HANDLE = u'@fivethirtyeight'
_FIVETHIRTYEIGHT_NAME = u'Nate Silver'

_ANDYRNYT_USER_ID = 14434063
_ANDYRNYT_HANDLE = u'@andyrNYT'
_ANDYRNYT_NAME = u'Andrew Rosenthal' 

_NYTPOLLS_USER_ID = 255719070
_NYTPOLLS_HANDLE = u'@nytpolls'
_NYTPOLLS_NAME = u'New York Times Polls' 

_DEBUG_USER_IDS = set()
_DEBUG_USER_IDS.add(_NYTIMES_USER_ID)
_DEBUG_USER_IDS.add(_POGUE_USER_ID)
_DEBUG_USER_IDS.add(_FIVETHIRTYEIGHT_USER_ID)
_DEBUG_USER_IDS.add(_ANDYRNYT_USER_ID)
_DEBUG_USER_IDS.add(_NYTPOLLS_USER_ID)


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
      if hits_remaining < 10:
        log('Rate limit status low, waiting for 15 min...')
        time.sleep(15 * 60)
      else:
        return
    except tweepy.error.TweepError, err: # pylint: disable-msg=E1101
      log('%s' % err)
      log('Error checking wait limit status, waiting for 15 min...')
      time.sleep(15 * 60)


def get_user_info(api, user_ids):
  """Queries twitter for user information.

  Keyword Arguments:
  api -- (tweepy.API)
  user_ids -- (Set<int>) twitter ids to get info for.

  Returns:
  users -- (Set<User>)
  users_ids_not_found -- (Set<str>) user ids that were not found.
  """
  log('Querying twitter for user info...')
  users = set()
  user_ids_not_found = set()
  for user_id in user_ids:
    check_rate_limit_and_wait_if_needed(api)
    try:
      tweepy_user = api.get_user(int(user_id))
      users.add(User.from_tweepy_user(tweepy_user))
    except tweepy.error.TweepError, err: # pylint: disable-msg=E1101
      log('%s (user_id: %s)' % (err, user_id))
      user_ids_not_found.add(user_id)
  return users, user_ids_not_found


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
      user = User(user_id, screen_name, name, followers_count, statuses_count,
                  friends_count, created_at, listed_count, verified)
      users[user_id] = user
  return users


def output_users(users):
  """Outputs user info to disk.

  Keyword Arguments:
  users -- (Set<tweepy.model.User>)
  """
  log('Outputting user info to disk...')
  Util.ensure_dir_exist(_OUTPUT_DIR)
  with codecs.open(_OUTPUT_DIR + 'user_info.tsv', 'w',
                   encoding='utf-8') as out_file:
    for user in users:
      out_file.write(u'%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n'
                     % (user.id, user.screen_name, user.name,
                        user.followers_count, user.statuses_count,
                        user.friends_count, user.created_at, user.listed_count,
                        user.verified))


def run():
  """For debugging purposes. Uses mock data and mocks out
  tweepy api object's methods to avoid actually calling the Twitter
  api and using up rate limit."""
  api = tweepy.API()
  api.get_user = __mock_get_user
  users, user_ids_not_found = get_user_info(api, # pylint: disable-msg=W0612
                                            _DEBUG_USER_IDS)
  for user in users:
    log('%s' % user)
  log('Analysis done!')
  

def __mock_get_user(user_id):
  """Mock get_user for debugging purposes."""
  if user_id == _NYTIMES_USER_ID:
    return MockUser(user_id, _NYTIMES_HANDLE, _NYTIMES_NAME)
  elif user_id == _POGUE_USER_ID:
    return MockUser(user_id, _POGUE_HANDLE, _POGUE_NAME)
  elif user_id == _FIVETHIRTYEIGHT_USER_ID:
    return MockUser(user_id, _FIVETHIRTYEIGHT_HANDLE, _FIVETHIRTYEIGHT_NAME)
  elif user_id == _ANDYRNYT_USER_ID:
    return MockUser(user_id, _ANDYRNYT_HANDLE, _ANDYRNYT_NAME)
  elif user_id == _NYTPOLLS_USER_ID:
    return MockUser(user_id, _NYTPOLLS_HANDLE, _NYTPOLLS_NAME)
  else:
    return MockUser(user_id, '@fake', 'Fake')


class User:
  """Wrapper class for user infomation.

  Handy for referencing user information by logical name. Also, we don't
  want to be dependant on tweepy objects in other areas of our code.
  """
  def __init__(self, user_id, screen_name, name, followers_count,
               statuses_count, friends_count, created_at,
               listed_count, verified):
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
                tweepy_user.listed_count, tweepy_user.verified)

  def __str__(self):
    """Create a pretty str representation."""
    return pprint.pformat(vars(self))

  
class MockUser:
  """Mock tweepy.api.User for debugging purposes."""

  def __init__(self, user_id, handle, name):
    """Initialize an instance of this class."""
    self.id = user_id # pylint: disable-msg=C0103
    self.str_id = str(user_id)
    self.screen_name = handle
    self.name = name
    self.followers_count = 10
    self.statuses_count = 10
    self.friends_count = 10
    self.created_at = datetime.now()
    self.listed_count = 10
    self.verified = True

  def __str__(self):
    """Create a pretty str representation."""
    return pprint.pformat(vars(self))


def log(message):
  """Helper method to modularize the format of log messages.
    
    Keyword Arguments:
    message -- A string to print.
  """  
  FileLog.log(_LOG_FILE, message)


if __name__ == "__main__":
  run()
