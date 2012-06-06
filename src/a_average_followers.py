import FileLog
import Util
import basic_groups
import experts
import ground_truths
import crawl_users
from ground_truths import DataSet

_CATEGORIES = []
# Comment categories in/out individually as needed.
_CATEGORIES.append(None)
_CATEGORIES.append('world')
_CATEGORIES.append('business')
_CATEGORIES.append('opinion')
_CATEGORIES.append('sports')
# _CATEGORIES.append('us')
_CATEGORIES.append('technology')
# _CATEGORIES.append('movies')

_SIZE_EXPERTS = .02
_SIZE_TOP_NEWS = .02
_DELTA = 4

_LOG_FILE = 'a_average_followers.log'


def run():
  FileLog.set_log_dir()
  output_dir = '../data/AverageFollowers/'
  Util.ensure_dir_exist(output_dir)

  seeds = Util.load_seeds()

  for category in _CATEGORIES:
    run_params_str = '%s' % (category)
    log('Preforming analysis: Cateogry = %s' % run_params_str)

    gt_rankings = ground_truths.get_gt_rankings(seeds, DataSet.TESTING,
                                                category)
    target_news = ground_truths.find_target_news(gt_rankings, _SIZE_TOP_NEWS)

    (num_users, newsaholics,
     active_users, common_users) = basic_groups.group_users(_DELTA, category)

    experts_precision = experts.select_experts_precision(
        newsaholics.union(active_users), num_users, _DELTA, _SIZE_EXPERTS,
        category)
    experts_fscore = experts.select_experts_fscore(len(target_news),
                                                   num_users,
                                                   _DELTA, _SIZE_EXPERTS,
                                                   category)
    experts_ci = experts.select_experts_ci(num_users, _DELTA, _SIZE_EXPERTS,
                                           category)

    user_info = crawl_users.load_user_info()

    num_followers_newsaholics = 0
    num_followers_active = 0
    num_followers_common = 0
    num_followers_experts_p = 0
    num_followers_experts_f = 0
    num_followers_experts_c = 0

    num_crawled_newsaholics = 0
    num_crawled_active = 0
    num_crawled_common = 0
    num_crawled_experts_p = 0
    num_crawled_experts_f = 0
    num_crawled_experts_c = 0

    for user_id, user in user_info.items():
      if user_id in newsaholics:
        num_followers_newsaholics += user.followers_count
        num_crawled_newsaholics += 1
      if user_id in active_users:
        num_followers_active += user.followers_count
        num_crawled_active += 1
      if user_id in common_users:
        num_followers_common += user.followers_count
        num_crawled_common += 1
      if user_id in experts_precision:
        num_followers_experts_p += user.followers_count
        num_crawled_experts_p += 1
      if user_id in experts_fscore:
        num_followers_experts_f += user.followers_count
        num_crawled_experts_f += 1
      if user_id in experts_ci:
        num_followers_experts_c += user.followers_count
        num_crawled_experts_c += 1

    avg_followers_newsaholics = round(num_followers_newsaholics / num_crawled_newsaholics)
    avg_followers_active = round(num_followers_active / num_crawled_active)
    avg_followers_common = round(num_followers_common / num_crawled_common)
    avg_followers_experts_p = round(num_followers_experts_p / num_crawled_experts_p)
    avg_followers_experts_f = round(num_followers_experts_f / num_crawled_experts_f)
    avg_followers_experts_c = round(num_followers_experts_c / num_crawled_experts_c)
    avg_followers_all = round(0.75 * avg_followers_common + 0.23 * avg_followers_active + 0.02 * avg_followers_newsaholics)


    with open('%s%s.txt' % (output_dir, run_params_str), 'w') as out_file:
      out_file.write('Num avg followers newsaholics: %s\n' % (avg_followers_newsaholics))
      out_file.write('Num avg followers active: %s\n' % (avg_followers_active))
      out_file.write('Num avg followers common: %s\n' % (avg_followers_common))
      out_file.write('Num avg followers experts_p: %s\n' % (avg_followers_experts_p))
      out_file.write('Num avg followers experts_f: %s\n' % (avg_followers_experts_f))
      out_file.write('Num avg followers experts_c: %s\n' % (avg_followers_experts_c))
      out_file.write('Num avg followers all: %s\n' % (avg_followers_all))

    log('Analysis complete.')


def log(message):
  """Helper method to modularize the format of log messages.
  
  Keyword Arguments:
  message -- A string to log.
  """
  FileLog.log(_LOG_FILE, message)
  

if __name__ == "__main__":
  run()
