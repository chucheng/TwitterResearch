import FileLog
import experts
import basic_groups
import ground_truths
import Util
from ground_truths import DataSet

from constants import _TIMEDELTAS_FILE_DELTA_INDEX
from constants import _TIMEDELTAS_FILE_URL_INDEX 
from constants import _TIMEDELTAS_FILE_USER_ID_INDEX

_NUM_SEC_PER_HOUR = 3600
_LOG_FILE = 'a_hour_thresholds.py'
_BREAKDOWN = False
_SIZE_EXPERTS = .02
_SIZE_TOP_NEWS = .02


def run():

  category = None
  delta = 4
  seeds = Util.load_seeds()
  gt_rankings = ground_truths.get_gt_rankings(seeds, DataSet.TESTING,
                                              category)
  log('Num ground_truth_rankings: %s' % len(gt_rankings))
  target_news = ground_truths.find_target_news(gt_rankings, _SIZE_TOP_NEWS)
  log('Size target_news: %s' % len(target_news))

  (num_users, newsaholics,
   active_users, common_users) = basic_groups.group_users(delta, category)
  population = newsaholics.union(active_users).union(common_users)
  log('Num newsaholics: %s' % len(newsaholics))
  log('Num active: %s' % len(active_users))
  log('Num common: %s' % len(common_users))
  log('Num users (population): %s' % len(population))
  experts_precision = experts.select_experts_precision(
      newsaholics.union(active_users), num_users, delta, _SIZE_EXPERTS,
      category)
  experts_fscore = experts.select_experts_fscore(len(target_news),
                                                 num_users,
                                                 delta, _SIZE_EXPERTS,
                                                 category)
  experts_ci = experts.select_experts_ci(num_users, delta, _SIZE_EXPERTS,
                                         category)
  all_experts = experts.select_all_experts(experts_precision,
                                           experts_fscore,
                                           experts_ci)
  log('Num experts (precision): %s' % len(experts_precision))
  log('Num experts (fscore): %s' % len(experts_fscore))
  log('Num experts (ci): %s' % len(experts_ci))
  log('Num all experts: %s' % len(all_experts))

  # other_users = population.difference(all_experts).difference(common_users)


  total_num_tweets = 0
  total_num_tweets_experts = 0
  total_num_tweets_common = 0
  total_num_tweets_other = 0
  hour_to_num_tweets = {}
  with open('../data/FolkWisdom/time_deltas.tsv') as in_file:
    for line in in_file:
      tokens = line.split('\t')
      time_delta_in_sec = int(tokens[_TIMEDELTAS_FILE_DELTA_INDEX])
      url = tokens[_TIMEDELTAS_FILE_URL_INDEX].strip()
      user_id = tokens[_TIMEDELTAS_FILE_USER_ID_INDEX]
      if time_delta_in_sec > 0 and url in target_news:
        current_hour = time_delta_in_sec / _NUM_SEC_PER_HOUR
        total_num_tweets += 1
        if current_hour in hour_to_num_tweets:
          (num_tweets,
           num_tweets_experts,
           num_tweets_common,
           num_tweets_other) = hour_to_num_tweets[current_hour]
          num_tweets += 1
          if user_id in all_experts:
            num_tweets_experts += 1
            total_num_tweets_experts += 1
          elif user_id in common_users:
            num_tweets_common += 1
            total_num_tweets_common += 1
          else:
            num_tweets_other += 1
            total_num_tweets_other += 1
          hour_to_num_tweets[current_hour] = (num_tweets, num_tweets_experts,
                                              num_tweets_common,
                                              num_tweets_other)
        else:
          hour_to_num_tweets[current_hour] = (total_num_tweets,
                                              total_num_tweets_experts,
                                              total_num_tweets_common,
                                              total_num_tweets_other)
  
  for hour in hour_to_num_tweets.keys():
    (num_tweets, num_tweets_experts,
     num_tweets_common, num_tweets_other) = hour_to_num_tweets[hour]
    percentage = (num_tweets / float(total_num_tweets)) * 100.0
    percentage_experts = (num_tweets_experts / float(total_num_tweets)) * 100.0
    percentage_common = (num_tweets_common / float(total_num_tweets)) * 100.0
    percentage_other = (num_tweets_other / float(total_num_tweets)) * 100.0
    log('%s: %s\t%s\t%s\t%s' % (hour, percentage, percentage_experts,
                                percentage_common, percentage_other))


def log(message):
  """Helper method to modularize the format of log messages.
  
  Keyword Arguments:
  message -- A string to log.
  """
  FileLog.log(_LOG_FILE, message)


if __name__ == "__main__":
  run()
