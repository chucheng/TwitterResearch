"""
This file contains constants that will be used accross analyses. This will
ensure that we have consistent definitions accross all analyses.

__author__ = 'Chris Moghbel (cmoghbel@cs.ucla.edu)
"""
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

_TIMEDELTAS_FILE_TWEET_ID_INDEX = 0
_TIMEDELTAS_FILE_USER_ID_INDEX = 1 
_TIMEDELTAS_FILE_DELTA_INDEX = 2 # In seconds.
_TIMEDELTAS_FILE_URL_INDEX = 3
_TIMEDELTAS_FILE_CATEGORY_INDEX = 4
_TIMEDELTAS_FILE_SOURCE_INDEX = 5

_HITS_MISSES_FILE_USER_ID_INDEX = 0
_HITS_MISSES_FILE_HITS_INDEX = 1
_HITS_MISSES_FILE_MISSES_INDEX = 2

_USER_ACTIVITY_FILE_ID_INDEX = 0
_USER_ACTIVITY_FILE_COUNT_INDEX = 1

_DEVICE_FILE_DEVICE_INDEX = 0
_DEVICE_FILE_COUNT_INDEX = 1
_DEVICE_FILE_PERCENT1_INDEX = 2
_DEVICE_FILE_PERCENT2_INDEX = 3

_RATES_FILE_USER_ID_INDEX = 0
_RATES_FILE_RATE_INDEX = 1

_USER_INFO_FILE_ID_INDEX = 0
_USER_INFO_FILE_SCREEN_NAME_INDEX = 1
_USER_INFO_FILE_NAME_INDEX = 2
_USER_INFO_FILE_FOLLOWERS_COUNT_INDEX = 3
_USER_INFO_FILE_STATUSES_COUNT_INDEX = 4
_USER_INFO_FILE_FRIENDS_COUNT_INDEX = 5
_USER_INFO_FILE_CREATED_AT_INDEX = 6
_USER_INFO_FILE_LISTED_COUNT_INDEX = 7
_USER_INFO_FILE_VERIFIED_INDEX = 8
_USER_INFO_FILE_UTC_INDEX = 9
_USER_INFO_FILE_TIME_ZONE_INDEX = 10
_USER_INFO_FILE_LANG_INDEX = 11
_USER_INFO_FILE_TIMESTAMP_CRAWLED_INDEX = 12

_DATA_DIR = '/dfs/birch/tsv'
_CACHE_FILENAME = '/dfs/birch/tsv/URLExapnd.cache.txt'
_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

_DELTAS = [1, 4, 8]

_TRAINING_SET_MONTHS = ['09', '10']
_TESTING_SET_MONTHS = ['11', '12']
_FULL_SET_MONTHS = ['08', '09', '10', '11', '12', '01']
_WINDOW_MONTHS = ['09', '10', '11', '12']
