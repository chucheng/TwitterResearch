# Comment categories in/out individually as needed.
_CATEGORIES = [
  None,
  # 'world',
  # 'business',
  # 'opinion',
  # 'sports',
  # 'us',
  # 'technology'
  # 'movies'
]

# Comment deltas in/out individually as needed.
_DELTAS = [
  1,
  4,
  # 8,
]

_TRAINING_SET_MONTHS = ['09', '10']
_TESTING_SET_MONTHS = ['11', '12']
_FULL_SET_MONTHS = ['08', '09', '10', '11', '12', '01']
_WINDOW_MONTHS = ['09', '10', '11', '12']

_SIZE_EXPERTS = .02
_SIZE_TOP_NEWS = .05
_NUM_GROUPS = 5
_SIZE_OF_GROUP_IN_PERCENT = .02
_NON_EXPERTS_SAMPLE_SIZE = .33

_BETA = 2
_Z_SCORE = 1.645 # 95% 1 sided

_EXCLUDE_RETWEETS = False
_EXCLUDE_TWEETS_WITHIN_DELTA = False

# Toggle for switching training and testing sets.
_SWITCHED = False

_CI_WEIGHT = .65
_WEIGHT = .15
