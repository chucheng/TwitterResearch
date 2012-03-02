"""
This module contains a method for finding user infomation for a given set of
users.

Queries Twitter REST api via tweepy.

__author__ = 'Chris Moghbel (cmoghbel@cs.ucla.edu)'
"""
import FileLog
import Util

from datetime import datetime
import tweepy

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


def get_user_info(api, user_ids):
  """Queries twitter for user information.

  Keyword Arguments:
  api -- (tweepy.API)
  user_ids -- (Set<int>) twitter ids to get info for.

  Returns:
  users -- (Set<tweepy.model.User>)
  """
  log('Querying twitter for user info...')
  users = set()
  for user_id in user_ids:
    user = api.get_user(user_id)
    users.add(user)
  return users


def output_users(users):
  """Outputs user info to disk.

  Keyword Arguments:
  users -- (Set<tweepy.model.User>)
  """
  log('Outputting user info to disk...')
  Util.ensure_dir_exist(_OUTPUT_DIR)
  with open(_OUTPUT_DIR + 'user_info.tsv', 'w') as out_file:
    for user in users:
      out_file.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n'
                     % (user.id, user.screen_name, user.name,
                        user.followers_count, user.statuses_count,
                        user.description, user.friends_count,
                        user.created_at, user.listed_count,
                        user.verified))


def run():
  """For debugging purposes. Uses mock data and mocks out
  tweepy api object's methods to avoid actually calling the Twitter
  api and using up rate limit."""
  api = tweepy.API()
  api.get_user = __mock_get_user
  users = get_user_info(api, _DEBUG_USER_IDS)
  output_users(users)
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


class MockUser:
  """Mock tweepy.api.User for debugging purposes."""

  def __init__(self, user_id, handle, name):
    """Initialize an instance of this class."""
    self.id = user_id
    self.str_id = str(user_id)
    self.screen_name = handle
    self.name = name
    self.followers_count = 10
    self.statuses_count = 10
    self.description = 'Mock account description!'
    self.friends_count = 10
    self.created_at = datetime.now()
    self.listed_count = 10
    self.verified = True


def log(message):
  """Helper method to modularize the format of log messages.
    
    Keyword Arguments:
    message -- A string to print.
  """  
  FileLog.log(_LOG_FILE, message)


if __name__ == "__main__":
  run()
