import Util
import ground_truths
import basic_groups
import experts
import even_groups
import random

from ground_truths import DataSet

from params import _SIZE_EXPERTS
from params import _SIZE_TOP_NEWS
from params import _EXCLUDE_RETWEETS
from params import _EXCLUDE_TWEETS_WITHIN_DELTA
from params import _SWITCHED
from params import _TRAINING_SET_MONTHS
from params import _TESTING_SET_MONTHS
from params import _NUM_GROUPS
from params import _SIZE_OF_GROUP_IN_PERCENT
from params import _NON_EXPERTS_SAMPLE_SIZE


class UserGroups:
  population = None
  newsaholics = None
  active_users = None
  common_users = None
  precision = None
  fscore = None
  ci = None
  ci_hi = None
  ci_li = None
  ci_1 = None
  ci_2 = None
  ci_3 = None
  super_experts = None
  social_bias = None
  even_groups = None
  all_experts = None
  non_experts = None
  non_experts_sampled = None
  non_experts_25 = None
  non_experts_10 = None
  non_experts_1 = None
  weighted_followers = None


def get_all_user_groups(delta=4, category=None):
  seeds = Util.load_seeds()

  # Set up params appropriately.
  data_set = DataSet.TRAINING
  months = _TRAINING_SET_MONTHS
  if _SWITCHED:
    data_set = DataSet.TESTING
    months = _TESTING_SET_MONTHS
  retweets = set()
  if _EXCLUDE_RETWEETS:
    retweets = ground_truths.find_retweets(months)

  gt_rankings = ground_truths.get_gt_rankings(seeds, data_set, category,
                                              exclude_tweets_within_delta=_EXCLUDE_TWEETS_WITHIN_DELTA,
                                              retweets=retweets)
  target_news = ground_truths.find_target_news(gt_rankings, _SIZE_TOP_NEWS)

  groups = UserGroups()

  (num_users, groups.newsaholics,
   groups.active_users,
   groups.common_users) = basic_groups.group_users(delta, category)
  groups.population = groups.newsaholics.union(groups.active_users).union(groups.common_users)

  num_users_eg, groups.even_groups = even_groups.group_users(delta,
                                                             _NUM_GROUPS,
                                                             _SIZE_OF_GROUP_IN_PERCENT,
                                                             category)

  groups.precision = experts.select_experts_precision(
      groups.newsaholics.union(groups.active_users), num_users, delta,
      _SIZE_EXPERTS, category)
  groups.fscore = experts.select_experts_fscore(len(target_news),
                                                num_users,
                                                delta, _SIZE_EXPERTS,
                                                category)
  groups.ci = experts.select_experts_ci(num_users, delta, _SIZE_EXPERTS,
                                        category)
  groups.super_experts = experts.select_super_experts(groups.precision,
                                                      groups.fscore,
                                                      groups.ci)

  groups.ci_hi, groups.ci_li = experts.split_ci_experts_by_followers(groups.ci)

  groups.ci_1 = set()
  groups.ci_2 = set()
  groups.ci_3 = set()
  counter = 0
  for ci_expert in groups.ci:
    if counter % 3 == 0:
      groups.ci_1.add(ci_expert)
    elif counter % 3 == 1:
      groups.ci_2.add(ci_expert)
    elif counter % 3 == 2:
      groups.ci_3.add(ci_expert)
    counter += 1

  groups.social_bias, d_num_followers  = experts.select_experts_social_bias(num_users,
                                                                            _SIZE_EXPERTS)
  groups.all_experts = experts.select_all_experts(groups.precision,
                                                  groups.fscore,
                                                  groups.ci)
  groups.non_experts = groups.population.difference(groups.all_experts)
  sample_size = int(len(groups.non_experts) * _NON_EXPERTS_SAMPLE_SIZE)
  sample_size_25 = int(len(groups.non_experts) * 0.05)
  sample_size_10 = int(len(groups.non_experts) * 0.10)
  sample_size_1 = int(len(groups.non_experts) * 0.01)
  groups.non_experts_sampled = set(random.sample(groups.non_experts, sample_size))
  groups.non_experts_25 = set(random.sample(groups.non_experts, sample_size_25))
  groups.non_experts_10 = set(random.sample(groups.non_experts, sample_size_10))
  groups.non_experts_1 = set(random.sample(groups.non_experts, sample_size_1))

  return groups, d_num_followers
