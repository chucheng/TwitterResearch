import Util
import crawl_users
import user_groups

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from constants import _HITS_MISSES_FILE_USER_ID_INDEX
from constants import _HITS_MISSES_FILE_HITS_INDEX
from constants import _HITS_MISSES_FILE_MISSES_INDEX

_GRAPH_DIR = Util.get_graph_output_dir('FollowersPrecisionCorrelation/')


def draw(num_followers, precision_scores):
  figure = plt.figure()
  axs = figure.add_subplot(111)

  axs.set_xscale('log')
  axs.scatter(num_followers, precision_scores)

  plt.grid(True, which='major')
  plt.xlabel('Number of Followers')
  plt.ylabel('Precision Score')
  plt.xlim(0, max(num_followers))

  with open(_GRAPH_DIR + '/followers_precision_correlation.png', 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + '/followers_precision_correlation.eps', 'w') as graph:
    plt.savefig(graph, format='eps')


def get_user_precisions():
  user_id_to_precision = {}
  with open('../data/FolkWisdom/user_hits_and_misses_4_None.tsv') as in_file:
    for line in in_file:
      tokens = line.split('\t')
      user_id = tokens[_HITS_MISSES_FILE_USER_ID_INDEX].strip()
      hits = float(tokens[_HITS_MISSES_FILE_HITS_INDEX].strip())
      misses = float(tokens[_HITS_MISSES_FILE_MISSES_INDEX].strip())
      user_id_to_precision[user_id] = (hits / (hits + misses), hits + misses)

  return user_id_to_precision


def run():
  users = crawl_users.load_user_info()
  groups = user_groups.get_all_user_groups()
  user_id_to_precision = get_user_precisions()

  num_followers = []
  precision_scores = []
  awesome_people = []
  missing = 0
  awesome_people_votes = 0
  for user in users.values():
    if user.id in groups.all_experts and user.id in user_id_to_precision:
      num_followers.append(user.followers_count)
      precision, num_tweets = user_id_to_precision[user.id]
      precision_scores.append(precision)
      if precision >= .5 and num_tweets > 7 and user.followers_count > 1254:
        awesome_people.append(user)
        awesome_people_votes += num_tweets
    else:
      missing += 1

  for user in awesome_people:
    print user.screen_name
  print 'Number of awesome people: %s' % len(awesome_people)
  print 'Number of votes awesome people: %s' % awesome_people_votes
  print 'Missing: %s' % missing

  draw(num_followers, precision_scores)


if __name__ == "__main__":
  run()
