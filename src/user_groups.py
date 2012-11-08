import Util
import ground_truths
import basic_groups
import experts

from ground_truths import DataSet

from params import _SIZE_EXPERTS
from params import _SIZE_TOP_NEWS
from params import _EXCLUDE_RETWEETS
from params import _EXCLUDE_TWEETS_WITHIN_DELTA
from params import _SWITCHED
from params import _TRAINING_SET_MONTHS
from params import _TESTING_SET_MONTHS


class UserGroups:
  population = None
  newsaholics = None
  active_users = None
  common_users = None
  precision = None
  fscore = None
  ci = None
  all_experts = None
  non_experts = None


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

  groups.precision = experts.select_experts_precision(
      groups.newsaholics.union(groups.active_users), num_users, delta,
      _SIZE_EXPERTS, category)
  groups.fscore = experts.select_experts_fscore(len(target_news),
                                                num_users,
                                                delta, _SIZE_EXPERTS,
                                                category)
  groups.ci = experts.select_experts_ci(num_users, delta, _SIZE_EXPERTS,
                                        category)
  groups.all_experts = experts.select_all_experts(groups.precision,
                                                  groups.fscore,
                                                  groups.ci)
  groups.non_experts = groups.population.difference(groups.all_experts)

  return groups
