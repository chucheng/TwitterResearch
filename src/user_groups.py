import Util
import ground_truths
import basic_groups
import experts

from ground_truths import DataSet

from params import _SIZE_EXPERTS
from params import _SIZE_TOP_NEWS


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

  gt_rankings = ground_truths.get_gt_rankings(seeds, DataSet.TESTING,
                                              category)
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

  return groups
