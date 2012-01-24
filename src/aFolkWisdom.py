import DataUtils

from datetime import datetime 

def get_ground_truths(cache):
  """Gets the ground truth counts and rankings for urls.

  To determine the ground truth, we do the following:
    1. Find all news appearing in months 09, 10, 11
    2. Exclude all news appearing in 08
    3. Find the true counts by summing tweets from 09, 10, 11, 12

  Keyword Arguments:
  cache -- A dictionary mapping short urls to long urls.

  Returns:
  ground_truths -- A dictionary of url to ground_truth tweet counts.
  """
  ground_truths = DataUtils.gather_tweet_counts_for(['09', '10', '11'], cache)
  DataUtils.eliminate_news_for(['08'], ground_truths, cache)
  DataUtils.add_tweets_from(['12'], ground_truths, cache)
  return ground_truths
  

def get_rankings_for_groups(cache, experts, active_users):
  etc, atc, ctc = DataUtils.gather_tweet_counts_for_groups(['09', '10', '11'], cache, experts, active_users)
  expert_rankings = sorted(etc.items(), key=lambda x: x[1], reverse=True)
  active_rankings = sorted(atc.items(), key=lambda x: x[1], reverse=True)
  common_rankings = sorted(ctc.items(), key=lambda x: x[1], reverse=True)
  return expert_rankings, active_rankings, common_rankings


def group_users(user_id_sorted_by_tweet_count):
  num_users = len(user_id_sorted_by_tweet_count)
  bucket_size = num_users / 100
  
  user_id_to_percentile = {}
  experts = set()
  active_users = set()
  common_users = set()
  current_percentile = 1
  for i in range(num_users):
    user_id, tweet_count = user_id_sorted_by_tweet_count[i]
    if current_percentile < 3:
      experts.add(user_id)
    elif current_percentile < 26:
      active_users.add(user_id)
    else:
      common_users.add(user_id)
    if i is not 0 and i % bucket_size is 0:
      # Dont increase percentile past 100. We need to do this because we need
      # bucket size to be a integer, but to have 100 even buckets we would need
      # decimal bucket sizes. This takes care of this "rounding issue".
      if current_percentile < 100:
        current_percentile += 1
  return experts, active_users, common_users


def run():
  cache = DataUtils.load_cache()
  ground_truths = get_ground_truths(cache)
  log('Number of news stories (total): %s' % len(ground_truths.keys()))
  user_ids_sorted = DataUtils.get_users_sorted_by_tweet_count(['09', '10', '11'])
  experts, active_users, common_users = group_users(user_ids_sorted)
  log('Num experts: %s' % len(experts))
  log('Num active: %s' % len(active_users))
  log('Num common: %s' % len(common_users))
  expert_rankings, active_rankings, common_rankings = get_rankings_for_groups(cache, experts, active_users)
  log('Num expert rankings: %s' % len(expert_rankings))
  log('Num active_rankings: %s' % len(active_rankings))
  log('Num common_rankings: %s' % len(common_rankings))
  sorted_ground_truths = sorted(ground_truths.items(), key=lambda x: x[1], reverse=True)
  log('Num ground_truth_rankings: %s' % len(sorted_ground_truths))
  log('Ground Truth Top 10')
  for i in range(10):
    url, count = sorted_ground_truths[i]
    log('[%s] %s\t%s' %(i, url, count))
  log('-----------------------------------')
  log('Expert Top 10')
  for i in range(10):
    url, count = expert_rankings[i]
    log('[%s] %s\t%s' %(i, url, count))
  log('-----------------------------------')
  log('Active Top 10')
  for i in range(10):
    url, count = active_rankings[i]
    log('[%s] %s\t%s' %(i, url, count))
  log('-----------------------------------')
  log('Common Top 10')
  for i in range(10):
    url, count = common_rankings[i]
    log('[%s] %s\t%s' %(i, url, count))


def log(message):
  print '[%s] %s' %(datetime.now(), message)
  

if __name__ == "__main__":
    run()
