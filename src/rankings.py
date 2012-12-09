import math
import Util
import user_groups

from datetime import timedelta

from constants import _TIMEDELTAS_FILE_URL_INDEX
from constants import _TIMEDELTAS_FILE_USER_ID_INDEX
from constants import _TIMEDELTAS_FILE_DELTA_INDEX
from constants import _TIMEDELTAS_FILE_CATEGORY_INDEX

from params import _SWITCHED
from params import _CI_WEIGHT
from params import _WEIGHT


def gather_tweet_counts(hours, seeds, groups, d_num_followers, category=None):
  """Gathers the tweet counts for a given set of months.
  
  Only counts votes if they occur within the given time delta from the seed
  time (except for the ground truth rankings).
  
  Keyword Arguments:
  hours -- The number of hours from the seed time in which to accept votes.
  seeds -- A dictionary of url to the datetime of it first being seend
  Accepts a parameter for a set defining each of the following user groups:
  newsaholics, active users, experts (precision), experts (F-score),
  experts (confidence interval), and experts (super experts).
  category -- The category to gather tweets for, None if for all news.

  Returns:
  Dictionary of url to tweet count for all user groups. This includes:
  ground truth, market, newsaholic, active users, common users, and
  experts (precision, F-score, confidence interval, and super).
  """
  tweet_counts = user_groups.UserGroups()
  tweet_counts.precision = {}
  tweet_counts.fscore = {}
  tweet_counts.ci = {}
  tweet_counts.ci_hi = {}
  tweet_counts.ci_li = {}
  tweet_counts.ci_1 = {}
  tweet_counts.ci_2 = {}
  tweet_counts.ci_3 = {}
  tweet_counts.super_experts = {}
  tweet_counts.social_bias = {}
  tweet_counts.newsaholics = {}
  tweet_counts.active_users = {}
  tweet_counts.common_users = {}
  tweet_counts.non_experts = {}
  tweet_counts.non_experts_sampled = {}
  tweet_counts.non_experts_25 = {}
  tweet_counts.non_experts_10 = {}
  tweet_counts.non_experts_1 = {}
  tweet_counts.weighted_followers = {}
  tweet_counts.ci_weighted = {}
  tweet_counts.weighted = {}
  tweet_counts.weighted_both = {}

  with open('../data/FolkWisdom/time_deltas.tsv') as input_file:
    for line in input_file:
      tokens = line.split('\t')
      url = tokens[_TIMEDELTAS_FILE_URL_INDEX]
      user_id = tokens[_TIMEDELTAS_FILE_USER_ID_INDEX]
      time_delta = timedelta(seconds=int(tokens[_TIMEDELTAS_FILE_DELTA_INDEX]))
      url_category = tokens[_TIMEDELTAS_FILE_CATEGORY_INDEX].strip()
      max_delta = timedelta.max
      if hours:
        max_delta = timedelta(hours=hours)

      if url in seeds:
        (seed_tweet_id, seed_user_id, seed_time) = seeds[url]

        if (in_correct_set(seed_time) and time_delta < max_delta
            and category_matches(category, url_category)):

          # Market
          if tweet_counts.population == None:
            tweet_counts.population = {}
          if url in tweet_counts.population:
            tweet_counts.population[url] += 1
          else:
            tweet_counts.population[url] = 1

          increment_tweet_count(groups.precision, tweet_counts.precision, user_id, url)
          increment_tweet_count(groups.fscore, tweet_counts.fscore, user_id, url)
          increment_tweet_count(groups.ci, tweet_counts.ci, user_id, url)
          increment_tweet_count(groups.ci_hi, tweet_counts.ci_hi, user_id, url)
          increment_tweet_count(groups.ci_li, tweet_counts.ci_li, user_id, url)
          increment_tweet_count(groups.ci_1, tweet_counts.ci_1, user_id, url)
          increment_tweet_count(groups.ci_2, tweet_counts.ci_3, user_id, url)
          increment_tweet_count(groups.ci_3, tweet_counts.ci_3, user_id, url)
          increment_tweet_count(groups.super_experts, tweet_counts.super_experts, user_id, url)
          increment_tweet_count(groups.social_bias, tweet_counts.social_bias, user_id, url)
          increment_tweet_count(groups.newsaholics, tweet_counts.newsaholics, user_id, url)
          increment_tweet_count(groups.active_users, tweet_counts.active_users, user_id, url)
          increment_tweet_count(groups.common_users, tweet_counts.common_users, user_id, url)
          increment_tweet_count(groups.non_experts, tweet_counts.non_experts, user_id, url)
          increment_tweet_count(groups.non_experts_sampled, tweet_counts.non_experts_sampled, user_id, url)
          increment_tweet_count(groups.non_experts_25, tweet_counts.non_experts_25, user_id, url)
          increment_tweet_count(groups.non_experts_10, tweet_counts.non_experts_10, user_id, url)
          increment_tweet_count(groups.non_experts_1, tweet_counts.non_experts_1, user_id, url)
          weight = 1.0
          if user_id in d_num_followers:
            num_followers = d_num_followers[user_id] + 1 # need to account for the case of 0 followers
            weight = math.log(num_followers)
          increment_tweet_count(groups.ci, tweet_counts.weighted_followers, user_id, url, weight=weight)

          # Weighted ci model
          increment_tweet_count(groups.ci_hi, tweet_counts.ci_weighted, user_id, url, weight=_CI_WEIGHT)
          increment_tweet_count(groups.ci_li, tweet_counts.ci_weighted, user_id, url, weight=(1 - _CI_WEIGHT))

          # Weighted Model
          increment_tweet_count(groups.non_experts, tweet_counts.weighted, user_id, url, weight=_WEIGHT)
          increment_tweet_count(groups.ci, tweet_counts.weighted, user_id, url, weight=(1 - _WEIGHT))

          # Weighted (Both)
          increment_tweet_count(groups.non_experts, tweet_counts.weighted_both, user_id, url, weight=_WEIGHT)
          increment_tweet_count(groups.ci_hi, tweet_counts.weighted_both, user_id, url, weight=((1 - _WEIGHT) * _CI_WEIGHT))
          increment_tweet_count(groups.ci_li, tweet_counts.weighted_both, user_id, url, weight=((1 - _WEIGHT) * (1 - _CI_WEIGHT)))
                
  return tweet_counts


def in_correct_set(seed_time):
  in_correct_set = Util.is_in_testing_set(seed_time)
  if _SWITCHED:
    in_correct_set = Util.is_in_training_set(seed_time)
  return in_correct_set


def category_matches(category, url_category):
  category_matches = True
  if category:
    category_matches = False
    if url_category == category:
      category_matches = True
  return category_matches


def increment_tweet_count(group, tc, user_id, url, weight=1.0):
  if user_id in group:
    if url in tc:
      tc[url] += weight * 1
    else:
      tc[url] = weight * 1


def sort_tweet_counts(tweet_counts):
  rankings = user_groups.UserGroups()
  rankings.population= sorted(tweet_counts.population.items(), key=lambda x: x[1], reverse=True)
  rankings.newsaholics= sorted(tweet_counts.newsaholics.items(), key=lambda x: x[1], reverse=True)
  rankings.common_users = sorted(tweet_counts.common_users.items(), key=lambda x: x[1], reverse=True)
  rankings.active_users = sorted(tweet_counts.active_users.items(), key=lambda x: x[1], reverse=True)
  rankings.precision = sorted(tweet_counts.precision.items(), key=lambda x: x[1], reverse=True)
  rankings.fscore = sorted(tweet_counts.fscore.items(), key=lambda x: x[1], reverse=True)
  rankings.ci = sorted(tweet_counts.ci.items(), key=lambda x: x[1], reverse=True)
  rankings.ci_hi = sorted(tweet_counts.ci_hi.items(), key=lambda x: x[1], reverse=True)
  rankings.ci_li = sorted(tweet_counts.ci_li.items(), key=lambda x: x[1], reverse=True)
  rankings.ci_1 = sorted(tweet_counts.ci_1.items(), key=lambda x: x[1], reverse=True)
  rankings.ci_2 = sorted(tweet_counts.ci_3.items(), key=lambda x: x[1], reverse=True)
  rankings.ci_3 = sorted(tweet_counts.ci_3.items(), key=lambda x: x[1], reverse=True)
  rankings.non_experts = sorted(tweet_counts.non_experts.items(), key=lambda x: x[1], reverse=True)
  rankings.non_experts_sampled = sorted(tweet_counts.non_experts_sampled.items(), key=lambda x: x[1], reverse=True)
  rankings.non_experts_25 = sorted(tweet_counts.non_experts_25.items(), key=lambda x: x[1], reverse=True)
  rankings.non_experts_10 = sorted(tweet_counts.non_experts_10.items(), key=lambda x: x[1], reverse=True)
  rankings.non_experts_1 = sorted(tweet_counts.non_experts_1.items(), key=lambda x: x[1], reverse=True)
  rankings.super_experts = sorted(tweet_counts.super_experts.items(), key=lambda x: x[1], reverse=True)
  rankings.social_bias = sorted(tweet_counts.social_bias.items(), key=lambda x: x[1], reverse=True)
  rankings.weighted_followers = sorted(tweet_counts.weighted_followers.items(), key=lambda x: x[1], reverse=True)
  rankings.ci_weighted = sorted(tweet_counts.ci_weighted.items(), key=lambda x: x[1], reverse=True)
  rankings.weighted = sorted(tweet_counts.weighted.items(), key=lambda x: x[1], reverse=True)
  rankings.weighted_both = sorted(tweet_counts.weighted_both.items(), key=lambda x: x[1], reverse=True)
  return rankings


def get_rankings(delta, seeds, groups, category, d_num_followers):
  tweet_counts = gather_tweet_counts(delta, seeds, groups, d_num_followers, category)
  rankings = sort_tweet_counts(tweet_counts)
  return rankings
