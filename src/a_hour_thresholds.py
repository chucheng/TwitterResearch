import FileLog
import experts
import basic_groups
import ground_truths
import Util
from ground_truths import DataSet

from constants import _TIMEDELTAS_FILE_DELTA_INDEX
from constants import _TIMEDELTAS_FILE_URL_INDEX 
from constants import _TIMEDELTAS_FILE_USER_ID_INDEX

from params import _DELTAS
from params import _SIZE_EXPERTS
from params import _SIZE_TOP_NEWS

_NUM_SEC_PER_HOUR = 3600
_LOG_FILE = 'a_hour_thresholds.log'
_DATA_DIR = '../data/HourThresholds/'
_BREAKDOWN = False

# enum Expert type
class ExpertGroup:
  precision = None
  fscore = None
  ci = None
  union = None

class GroupCount:
  population = 0
  common = 0
  union = 0
  other = 0

  precision = 0
  fscore = 0
  ci = 0

  def add(self, gc):
    self.population += gc.population
    self.common += gc.common
    self.union += gc.union
    self.other += gc.other
    self.precision += gc.precision
    self.fscore += gc.fscore
    self.ci += gc.ci

def run():

  Util.ensure_dir_exist(_DATA_DIR)
  category = None
  seeds = Util.load_seeds() #read twitter data

  gt_rankings = ground_truths.get_gt_rankings(seeds, DataSet.TESTING,
                                              category)
  log('Num ground_truth_rankings: %s' % len(gt_rankings))
  target_news = ground_truths.find_target_news(gt_rankings, _SIZE_TOP_NEWS)
  log('Size target_news: %s' % len(target_news))

  for delta in _DELTAS:
    (num_users, newsaholics,
     active_users, common_users) = basic_groups.group_users(delta, category)
    population = newsaholics.union(active_users).union(common_users)
    log('Num newsaholics: %s' % len(newsaholics))
    log('Num active: %s' % len(active_users))
    log('Num common: %s' % len(common_users))
    log('Num users (population): %s' % len(population))

    # -- Get experts --
    ExpertGroup.precision = experts.select_experts_precision(
        newsaholics.union(active_users), num_users, delta, _SIZE_EXPERTS,
        category)
    ExpertGroup.fscore = experts.select_experts_fscore(len(target_news),
                                                   num_users,
                                                   delta, _SIZE_EXPERTS,
                                                   category)
    ExpertGroup.ci = experts.select_experts_ci(num_users, delta, _SIZE_EXPERTS,
                                           category)
    ExpertGroup.union = experts.select_all_experts(ExpertGroup.precision,
                                             ExpertGroup.fscore,
                                             ExpertGroup.ci)

    log('Num experts (precision): %s' % len(ExpertGroup.precision))
    log('Num experts (fscore): %s' % len(ExpertGroup.fscore))
    log('Num experts (ci): %s' % len(ExpertGroup.ci))
    log('Num all experts: %s' % len(ExpertGroup.union))

    # other_users = population.difference(all_experts).difference(common_users)


    # -- counting --

    total_num_tweets = 0 
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

          if current_hour not in hour_to_num_tweets:
            hour_to_num_tweets[current_hour] = GroupCount()
          gcount = hour_to_num_tweets[current_hour]

          gcount.population += 1
          if user_id in ExpertGroup.union:
            gcount.union += 1
            if user_id in ExpertGroup.precision:
              gcount.precision += 1
            if user_id in ExpertGroup.fscore:
              gcount.fscore += 1
            if user_id in ExpertGroup.ci:
              gcount.ci += 1
            
            #  print >> sys.stderr, 'Error, a user in expert union but not belongs to any expert group'

          elif user_id in common_users:
            gcount.common += 1
          else :
            gcount.other += 1

    gcount = GroupCount()  
    with open(_DATA_DIR + 'hour_thresholds_%s.tsv' % delta, 'w') as out_file:
      for hour in hour_to_num_tweets.keys():
        gc = hour_to_num_tweets[hour]
        gcount.add(gc)
        percentage = (gcount.population / float(total_num_tweets)) * 100.0
        percentage_common = (gcount.common / float(total_num_tweets)) * 100.0
        percentage_other = (gcount.other / float(total_num_tweets)) * 100.0
        percentage_experts = (gcount.union / float(total_num_tweets)) * 100.0
        
        out_file.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (hour, percentage,
                                                             percentage_experts,
                                                             percentage_common,
                                                             percentage_other,
                                                             (gcount.precision / float(total_num_tweets)) * 100.0,
                                                             (gcount.fscore / float(total_num_tweets)) * 100.0,
                                                             (gcount.ci / float(total_num_tweets)) * 100.0))
        log('%s: %s\t%s\t%s\t%s\t%s\t%s\t%s' % (hour, percentage, percentage_experts,
                                    percentage_common, percentage_other,
                                    (gcount.precision / float(total_num_tweets)) * 100.0,
                                    (gcount.fscore / float(total_num_tweets)) * 100.0,
                                    (gcount.ci / float(total_num_tweets)) * 100.0))
    log('hour: population\texperts\tcommon\tprecision\tfscore\tci')

def log(message):
  """Helper method to modularize the format of log messages.
  
  Keyword Arguments:
  message -- A string to log.
  """
  FileLog.log(_LOG_FILE, message)


if __name__ == "__main__":
  run()
