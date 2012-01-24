import DataUtils

from datetime import datetime 


def calculate_hit_miss_rate(ground_truth_rankings, other_rankings):
  """Calculate the hit and miss rate for a set of rankings against ground truth.
  
  Hit rate is defined as the percentage of urls from the top X urls of the ground
  truth rankings that appear in the top X urls of the other rankings.
  
  Consequently, miss rate is defined as the percentage of urls from the top X
  urls of the ground truths that do not appear in the top X urls of the other
  rankings.
  
  Keyword Arguments:
  ground_truth_rankings -- A list of (url, count) pairs, in ranked
  (sorted by count) order, representing the ground truth.
  other_rankings -- A list of (url, count) pairs, in ranked (sorted by count)
  order, representing the other set of rankings.
  
  Returns:
  hit_rate -- The hit rate as a percentage.
  miss_rate -- The miss rate as a percentage.
  """
  num_news_to_consider = int(len(ground_truth_rankings) * .02)
  hit_rate = 0
  miss_rate = 0
  other_rankings_set = set()
  for i in range(num_news_to_consider):
    url, count = other_rankings[i]
    other_rankings_set.add(url)
  for i in range(num_news_to_consider):
    url, count = ground_truth_rankings[i]
    if url in other_rankings_set:
      hit_rate +=1
    else:
      miss_rate += 1
  hit_rate = (hit_rate/float(num_news_to_consider)) * 100.0
  miss_rate = (miss_rate/float(num_news_to_consider)) * 100.0 
  return hit_rate, miss_rate


def calculate_mean_and_variance(ground_truth_rankings, other_rankings):
  """Calculates the mean and variance of the top X ranked urls.

  Keyword Arguments:
  ground_truth_rankings -- A list of (url, count) pairs, in ranked
  (sorted by count) order, representing the ground truth.
  other_rankings -- A list of (url, count) pairs, in ranked (sorted by count)
  order, representing the other set of rankings.
  
  Returns:
  mean -- The mean, defined as the average ground truth ranking of the
  top X urls, as ranked in the other rankings set.
  var -- The var, defined as the sum of the differences of ranks 1...100
  from the mean squared.
  """
  num_news_to_consider = int(len(ground_truth_rankings) * .02)
  mean = 0
  for i in range(num_news_to_consider):
    url, count = other_rankings[i]
    for j, (gt_url, count) in enumerate(ground_truth_rankings):
      if gt_url == url:
        mean += j
        break
  mean /= float(num_news_to_consider)
  var = 0
  for i in range(num_news_to_consider):
    var += ((i+1) - mean)**2
  var /= float(num_news_to_consider)
  return mean, var


def calculate_mean_and_variance_missing(ground_truth_rankings, other_rankings):
  """Calculates the mean and variance of any 'missing' urls from the top X urls.
  
  Keyword Arguments:
    ground_truth_rankings -- A list of (url, count) pairs, in ranked
    (sorted by count) order, representing the ground truth.
    other_rankings -- A list of (url, count) pairs, in ranked (sorted by count)
    order, representing the other set of rankings.
    
  Returns:
  mean -- The mean, defined as the average ground truth ranking urls from the
  top X urls of the other rankings that don't appear in the top X of the ground
  truth rankings.
  var -- The var, defined as the sum of the differences of the missing ranks
  from the mean squared.
  """
  num_news_to_consider = int(len(ground_truth_rankings) * .02)
  mean = 0
  gt_top_urls = set()
  for i in range(num_news_to_consider):
    url, count = ground_truth_rankings[i]
    gt_top_urls.add(url)
  ranks_of_urls_not_in_top = []
  for i in range(num_news_to_consider):
    url, count = other_rankings[i]
    if not url in gt_top_urls:
      for j, (gt_url, count) in enumerate(ground_truth_rankings):
        if gt_url == url:
          mean += j
          ranks_of_urls_not_in_top.append(j)
          break
  mean /= float(len(ranks_of_urls_not_in_top))
  var = 0
  for rank in ranks_of_urls_not_in_top:
    var += (rank - mean)**2
  var /= float(len(ranks_of_urls_not_in_top))
  return mean, var
  

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
  """Determines the rankings for the Expert, Active, and Common users.
  
  Keyword Arguments:
  cache -- A dictionary mapping short urls to long urls.
  experts -- A python set of user ids representing 'expert' users.
  active_users -- A python set of user ids representing 'active' users.
  
  Returns:
  expert_rankings -- A list of (url, count) pairs in ranked (sorted by count)
  order, as determined by expert users.
  active_rankings -- A list of (url, count) pairs in ranked (sorted by count)
  order, as determined by active users.
  common_rankings -- A list of (url, count) pairs in ranked (sorted by count)
  order, as determined by common users.
  """
  etc, atc, ctc = DataUtils.gather_tweet_counts_for_groups(['09', '10', '11'], cache, experts, active_users)
  expert_rankings = sorted(etc.items(), key=lambda x: x[1], reverse=True)
  active_rankings = sorted(atc.items(), key=lambda x: x[1], reverse=True)
  common_rankings = sorted(ctc.items(), key=lambda x: x[1], reverse=True)
  return expert_rankings, active_rankings, common_rankings


def group_users(user_id_sorted_by_tweet_count):
  """Groups users into 'expert', 'active', and 'common' categories.
  
  Keyword Arguments:
  user_id_sorted_by_tweet_count -- A list of (user_id, tweet_count) pairs in 
  ranked (sorted by count) order.
  
  Returns:
  experts -- A python set of user ids for expert users, defined as users in top
  2% of users as ranked by activity.
  active_users -- A python set of user ids for active users, defined as users
  in between 2% and 25% of users as ranked by activity.
  common_users -- A python set of user ids for common users, defined as users
  whose rank is lower the 25% as ranked by activity.
  """
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
  """Contains the main logic for this analysis.
  
  A high level overview of the logic is as follows:
  
  1. Load a cache of short urls to long urls
  2. Gather the ground truth counts, defined as the number of tweets a url
  received in month 09, 10, 11, and 12.
  3. Gather the tweet counts for each user.
  4. Group users in expert, active, and common categories based on activity.
  5. Get the rankings for urls as determined by each of the three user groups.
  6. Compare these rankings against the ground truth rankings.
  """
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
    
  hit_rate_experts, miss_rate_experts = calculate_hit_miss_rate(sorted_ground_truths, expert_rankings)
  hit_rate_active, miss_rate_active = calculate_hit_miss_rate(sorted_ground_truths, active_rankings)
  hit_rate_common, miss_rate_common = calculate_hit_miss_rate(sorted_ground_truths, common_rankings)
  
  log('')
  log('Expert Hit Rate: %s' % hit_rate_experts)
  log('Expert Miss Rate: %s' % miss_rate_experts)
  log('Active Hit Rate: %s' % hit_rate_active)
  log('Active Miss Rate: %s' % miss_rate_active)
  log('Common Hit Rate: %s' % hit_rate_common)
  log('Common Miss Rate: %s' % miss_rate_common)
  
  mean_experts, var_experts = calculate_mean_and_variance(sorted_ground_truths, expert_rankings)
  mean_active, var_active = calculate_mean_and_variance(sorted_ground_truths, active_rankings)
  mean_common, var_common = calculate_mean_and_variance(sorted_ground_truths, common_rankings)
  
  log('')
  log('Expert Mean: %s' % mean_experts)
  log('Expert Var: %s' % var_experts)
  log('Active Mean: %s' % mean_active)
  log('Active Var: %s' % var_active)
  log('Common Mean: %s' % mean_common)
  log('Common Var: %s' % var_common)
  
  mean_missing_experts, var_missing_experts = calculate_mean_and_variance_missing(sorted_ground_truths, expert_rankings)
  mean_missing_active, var_missing_active = calculate_mean_and_variance_missing(sorted_ground_truths, active_rankings)
  mean_missing_common, var_missing_common = calculate_mean_and_variance_missing(sorted_ground_truths, common_rankings)

  log('')  
  log('Expert Missing Mean: %s' % mean_missing_experts)
  log('Expert Missing Var: %s' % var_missing_experts)
  log('Active Missing Mean: %s' % mean_missing_active)
  log('Active Missing Var: %s' % var_missing_active)
  log('Common Missing Mean: %s' % mean_missing_common)
  log('Common Missing Var: %s' % var_missing_common)  


def log(message):
  """Helper method to modularize the format of log messages.
  
  Keyword Arguments:
  message -- A string to print.
  """
  print '[%s] %s' %(datetime.now(), message)
  

if __name__ == "__main__":
    run()
