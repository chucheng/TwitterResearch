import FileLog
import Util
import basic_groups
import experts
import ground_truths
from datetime import timedelta
from ground_truths import DataSet

from constants import _TIMEDELTAS_FILE_URL_INDEX
from constants import _TIMEDELTAS_FILE_DELTA_INDEX
from constants import _TIMEDELTAS_FILE_CATEGORY_INDEX
from constants import _TIMEDELTAS_FILE_USER_ID_INDEX

_CATEGORIES = []
# Comment categories in/out individually as needed.
_CATEGORIES.append(None)
# _CATEGORIES.append('world')
# _CATEGORIES.append('business')
# _CATEGORIES.append('opinion')
# _CATEGORIES.append('sports')
# _CATEGORIES.append('us')
# _CATEGORIES.append('technology')
# _CATEGORIES.append('movies')

_SIZE_EXPERTS = .10

_LOG_FILE = 'a_time_constraint.log'


def category_matches(desired_category, tweet_category):
  if desired_category:
    if tweet_category == desired_category: return True
    else: return False
  else: return True


def find_counts(seeds, category=None):
  num_0_1 = 0
  num_1_4 = 0
  num_4_8 = 0
  num_after_8 = 0
  num_total = 0

  log('Finding common users delta 1...')
  (num_users_1, newsaholics_1, active_users_1, common_users_1) = basic_groups.group_users(1, category)
  log('Finding common users delta 4...')
  (num_users_4, newsaholics_4, active_users_4, common_users_4) = basic_groups.group_users(4, category)
  log('Finding common users delta 8...')
  (num_users_8, newsaholics_8, active_users_8, common_users_8) = basic_groups.group_users(8, category)

  copy_common_users_1 = set(common_users_1)
  common_users_1_1 = set()
  common_users_1_2 = set()
  common_users_1_3 = set()
  count = 0
  while len(copy_common_users_1) > 0:
    if count % 3 == 0:
      common_users_1_1.add(copy_common_users_1.pop())
    elif count % 3 == 1:
      common_users_1_2.add(copy_common_users_1.pop())
    elif count % 3 == 2:
      common_users_1_3.add(copy_common_users_1.pop())
    count += 1

  copy_common_users_4 = set(common_users_4)
  common_users_4_1 = set()
  common_users_4_2 = set()
  common_users_4_3 = set()
  count = 0
  while len(copy_common_users_4) > 0:
    if count % 3 == 0:
      common_users_4_1.add(copy_common_users_4.pop())
    elif count % 3 == 1:
      common_users_4_2.add(copy_common_users_4.pop())
    elif count % 3 == 2:
      common_users_4_3.add(copy_common_users_4.pop())
    count += 1

  copy_common_users_8 = set(common_users_8)
  common_users_8_1 = set()
  common_users_8_2 = set()
  common_users_8_3 = set()
  count = 0
  while len(copy_common_users_8) > 0:
    if count % 3 == 0:
      common_users_8_1.add(copy_common_users_8.pop())
    elif count % 3 == 1:
      common_users_8_2.add(copy_common_users_8.pop())
    elif count % 3 == 2:
      common_users_8_3.add(copy_common_users_8.pop())
    count += 1

  log('Size Common Users 1 (delta 1): %s' % len(common_users_1_1))
  log('Size Common Users 2 (delta 1): %s' % len(common_users_1_2))
  log('Size Common Users 3 (delta 1): %s' % len(common_users_1_3))
  log('Size Common Users 1 (delta 4): %s' % len(common_users_4_1))
  log('Size Common Users 2 (delta 4): %s' % len(common_users_4_2))
  log('Size Common Users 3 (delta 4): %s' % len(common_users_4_3))
  log('Size Common Users 1 (delta 8): %s' % len(common_users_8_1))
  log('Size Common Users 2 (delta 8): %s' % len(common_users_8_2))
  log('Size Common Users 3 (delta 8): %s' % len(common_users_8_3))

  log('Finding precision experts delta 1...')
  experts_p_1 = experts.select_experts_precision(newsaholics_1.union(active_users_1),
                                                 num_users_1, 1, _SIZE_EXPERTS, category)
  log('Finding precision experts delta 1...')
  experts_p_4 = experts.select_experts_precision(newsaholics_4.union(active_users_4),
                                                 num_users_4, 4, _SIZE_EXPERTS, category)
  log('Finding precision experts delta 1...')
  experts_p_8 = experts.select_experts_precision(newsaholics_8.union(active_users_8),
                                                 num_users_8, 8, _SIZE_EXPERTS, category)

  log('Finding ground truths...')
  gt_rankings = ground_truths.get_gt_rankings(seeds, DataSet.TESTING, category)
  log('Finding target news...')
  target_news = ground_truths.find_target_news(gt_rankings, _SIZE_EXPERTS)
  size_target_news = len(target_news)

  log('Finding fscore experts delta 1...')
  experts_f_1 = experts.select_experts_fscore(size_target_news, num_users_1,
                                              1, _SIZE_EXPERTS, category)
  log('Finding fscore experts delta 4...')
  experts_f_4 = experts.select_experts_fscore(size_target_news, num_users_4,
                                              4, _SIZE_EXPERTS, category)
  log('Finding fscore experts delta 8...')
  experts_f_8 = experts.select_experts_fscore(size_target_news, num_users_8,
                                              8, _SIZE_EXPERTS, category)

  log('Finding ci experts delta 1...')
  experts_ci_1 = experts.select_experts_ci(num_users_1, 1, _SIZE_EXPERTS, category)
  log('Finding ci experts delta 4...')
  experts_ci_4 = experts.select_experts_ci(num_users_4, 4, _SIZE_EXPERTS, category)
  log('Finding ci experts delta 8...')
  experts_ci_8 = experts.select_experts_ci(num_users_8, 8, _SIZE_EXPERTS, category)

  experts_all_1 = experts_p_1.union(experts_f_1).union(experts_ci_1)
  experts_all_4 = experts_p_4.union(experts_f_4).union(experts_ci_4)
  experts_all_8 = experts_p_8.union(experts_f_8).union(experts_ci_8)

  num_0_1_common = 0
  num_1_4_common = 0
  num_4_8_common = 0
  
  num_cu_1_1 = 0
  num_cu_1_2 = 0
  num_cu_1_3 = 0

  num_cu_4_1 = 0
  num_cu_4_2 = 0
  num_cu_4_3 = 0

  num_cu_8_1 = 0
  num_cu_8_2 = 0
  num_cu_8_3 = 0

  num_0_1_experts_p = 0
  num_1_4_experts_p = 0
  num_4_8_experts_p = 0

  num_0_1_experts_f = 0
  num_1_4_experts_f = 0
  num_4_8_experts_f = 0

  num_0_1_experts_ci = 0
  num_1_4_experts_ci = 0
  num_4_8_experts_ci = 0

  num_0_1_experts_all = 0
  num_1_4_experts_all = 0
  num_4_8_experts_all = 0

  log('Finding counts...')
  with open('../data/FolkWisdom/time_deltas.tsv') as input_file:
    for line in input_file:

      # parse line
      tokens = line.split('\t')
      url = tokens[_TIMEDELTAS_FILE_URL_INDEX]
      time_delta = timedelta(seconds=int(tokens[_TIMEDELTAS_FILE_DELTA_INDEX]))
      tweet_category = tokens[_TIMEDELTAS_FILE_CATEGORY_INDEX].strip()
      user_id = tokens[_TIMEDELTAS_FILE_USER_ID_INDEX]

      if url in seeds:
        (seed_tweet_id, seed_user_id, seed_time) = seeds[url]

        if Util.is_in_testing_set(seed_time) and category_matches(category,
                                                                  tweet_category):
            num_total += 1
            if time_delta < timedelta(hours=1):
              num_0_1 += 1
              if user_id in common_users_1:
                num_0_1_common += 1
              if user_id in experts_p_1:
                num_0_1_experts_p += 1
              if user_id in experts_f_1:
                num_0_1_experts_f += 1
              if user_id in experts_ci_1:
                num_0_1_experts_ci += 1
              if user_id in experts_all_1:
                num_0_1_experts_all += 1
              if user_id in common_users_1_1:
                num_cu_1_1 += 1
              if user_id in common_users_1_2:
                num_cu_1_2 += 1
              if user_id in common_users_1_3:
                num_cu_1_3 += 1
            elif time_delta >= timedelta(hours=1) and time_delta < timedelta(hours=4):
              num_1_4 += 1
              if user_id in common_users_4:
                num_1_4_common += 1
              if user_id in experts_p_4:
                num_1_4_experts_p += 1
              if user_id in experts_f_4:
                num_1_4_experts_f += 1
              if user_id in experts_ci_4:
                num_1_4_experts_ci += 1
              if user_id in experts_all_4:
                num_1_4_experts_all += 1
              if user_id in common_users_4_1:
                num_cu_4_1 += 1
              if user_id in common_users_4_2:
                num_cu_4_2 += 1
              if user_id in common_users_4_3:
                num_cu_4_3 += 1
            elif time_delta >= timedelta(hours=4) and time_delta < timedelta(hours=8):
              num_4_8 += 1
              if user_id in common_users_8:
                num_4_8_common += 1
              if user_id in experts_p_8:
                num_4_8_experts_p += 1
              if user_id in experts_f_8:
                num_4_8_experts_f += 1
              if user_id in experts_ci_8:
                num_4_8_experts_ci += 1
              if user_id in experts_all_8:
                num_4_8_experts_all += 1
              if user_id in common_users_8_1:
                num_cu_8_1 += 1
              if user_id in common_users_8_2:
                num_cu_8_2 += 1
              if user_id in common_users_8_3:
                num_cu_8_3 += 1
            else:
              num_after_8 += 1

  return (num_0_1, num_0_1_common, num_0_1_experts_p, num_0_1_experts_f, num_0_1_experts_ci, num_0_1_experts_all,
          num_1_4, num_1_4_common, num_1_4_experts_p, num_1_4_experts_f, num_1_4_experts_ci, num_1_4_experts_all,
          num_4_8, num_4_8_common, num_4_8_experts_p, num_4_8_experts_f, num_4_8_experts_ci, num_4_8_experts_all,
          num_cu_1_1, num_cu_1_2, num_cu_1_3,
          num_cu_4_1, num_cu_4_2, num_cu_4_3,
          num_cu_8_1, num_cu_8_2, num_cu_8_3,
          num_after_8, num_total)


def run():
  FileLog.set_log_dir()
  output_dir = '../data/TimeConstraint/'
  Util.ensure_dir_exist(output_dir)

  seeds = Util.load_seeds()

  for category in _CATEGORIES:
    run_params_str = '%s' % (category)
    log('Preforming analysis: Cateogry = %s' % run_params_str)

    # Find counts.
    (num_0_1, num_0_1_common, num_0_1_experts_p, num_0_1_experts_f, num_0_1_experts_ci, num_0_1_experts_all,
     num_1_4, num_1_4_common, num_1_4_experts_p, num_1_4_experts_f, num_1_4_experts_ci, num_1_4_experts_all,
     num_4_8, num_4_8_common, num_4_8_experts_p, num_4_8_experts_f, num_4_8_experts_ci, num_4_8_experts_all,
     num_cu_1_1, num_cu_1_2, num_cu_1_3,
     num_cu_4_1, num_cu_4_2, num_cu_4_3,
     num_cu_8_1, num_cu_8_2, num_cu_8_3,
     num_after_8, num_total) = find_counts(seeds, category)

    # Calculate non-common users.
    num_0_1_noncommon = num_0_1 - num_0_1_common
    num_1_4_noncommon = num_1_4 - num_1_4_common
    num_4_8_noncommon = num_4_8 - num_4_8_common

    with open('%s%s.txt' % (output_dir, run_params_str), 'w') as out_file:
      out_file.write('Common Users\n')
      out_file.write('------------\n')
      out_file.write('0 - 1 hours: %s (%s percent of total)\n'
                     % (num_0_1_common, (100 * (float(num_0_1_common) / num_total))))
      out_file.write('1 - 4 hours: %s (%s percent of total)\n'
                     % (num_1_4_common, (100 * (float(num_1_4_common) / num_total))))
      out_file.write('4 - 8 hours: %s (%s percent of total)\n'
                     % (num_4_8_common, (100 * (float(num_4_8_common) / num_total))))

      out_file.write('\nCommon Users (Breakdown, Delta 1)\n')
      out_file.write('------------\n')
      out_file.write('Common Users 1:  %s (%s percent of total)\n'
                     % (num_cu_1_1, (100 * (float(num_cu_1_1) / num_total))))
      out_file.write('Common Users 2: %s (%s percent of total)\n'
                     % (num_cu_1_2, (100 * (float(num_cu_1_2) / num_total))))
      out_file.write('Common Users 3: %s (%s percent of total)\n'
                     % (num_cu_1_3, (100 * (float(num_cu_1_1) / num_total))))
      out_file.write('\nCommon Users (Breakdown, Delta 4)\n')

      out_file.write('\nCommon Users (Breakdown, Delta 4)\n')
      out_file.write('------------\n')
      out_file.write('Common Users 1:  %s (%s percent of total)\n'
                     % (num_cu_4_1, (100 * (float(num_cu_4_1) / num_total))))
      out_file.write('Common Users 2: %s (%s percent of total)\n'
                     % (num_cu_4_2, (100 * (float(num_cu_4_2) / num_total))))
      out_file.write('Common Users 3: %s (%s percent of total)\n'
                     % (num_cu_4_3, (100 * (float(num_cu_4_3) / num_total))))

      out_file.write('\nCommon Users (Breakdown, Delta 8)\n')
      out_file.write('------------\n')
      out_file.write('Common Users 1:  %s (%s percent of total)\n'
                     % (num_cu_8_1, (100 * (float(num_cu_8_1) / num_total))))
      out_file.write('Common Users 2: %s (%s percent of total)\n'
                     % (num_cu_8_2, (100 * (float(num_cu_8_2) / num_total))))
      out_file.write('Common Users 3: %s (%s percent of total)\n'
                     % (num_cu_8_3, (100 * (float(num_cu_8_3) / num_total))))

      out_file.write('\nNon-Common Users\n')
      out_file.write('----------------\n')
      out_file.write('0 - 1 hours: %s (%s percent of total)\n'
                     % (num_0_1_noncommon, (100 * (float(num_0_1_noncommon) / num_total))))
      out_file.write('1 - 4 hours: %s (%s percent of total)\n'
                     % (num_1_4_noncommon, (100 * (float(num_1_4_noncommon) / num_total))))
      out_file.write('4 - 8 hours: %s (%s percent of total)\n'
                     % (num_4_8_noncommon, (100 * (float(num_4_8_noncommon) / num_total))))

      out_file.write('\nExpert Precision Users\n')
      out_file.write('----------------\n')
      out_file.write('0 - 1 hours: %s (%s percent of total)\n'
                     % (num_0_1_experts_p, (100 * (float(num_0_1_experts_p) / num_total))))
      out_file.write('1 - 4 hours: %s (%s percent of total)\n'
                     % (num_1_4_experts_p, (100 * (float(num_1_4_experts_p) / num_total))))
      out_file.write('4 - 8 hours: %s (%s percent of total)\n'
                     % (num_4_8_experts_p, (100 * (float(num_4_8_experts_p) / num_total))))

      out_file.write('\nExpert Fscore Users\n')
      out_file.write('----------------\n')
      out_file.write('0 - 1 hours: %s (%s percent of total)\n'
                     % (num_0_1_experts_f, (100 * (float(num_0_1_experts_f) / num_total))))
      out_file.write('1 - 4 hours: %s (%s percent of total)\n'
                     % (num_1_4_experts_f, (100 * (float(num_1_4_experts_f) / num_total))))
      out_file.write('4 - 8 hours: %s (%s percent of total)\n'
                     % (num_4_8_experts_f, (100 * (float(num_4_8_experts_f) / num_total))))

      out_file.write('\nExpert CI Users\n')
      out_file.write('----------------\n')
      out_file.write('0 - 1 hours: %s (%s percent of total)\n'
                     % (num_0_1_experts_ci, (100 * (float(num_0_1_experts_ci) / num_total))))
      out_file.write('1 - 4 hours: %s (%s percent of total)\n'
                     % (num_1_4_experts_ci, (100 * (float(num_1_4_experts_ci) / num_total))))
      out_file.write('4 - 8 hours: %s (%s percent of total)\n'
                     % (num_4_8_experts_ci, (100 * (float(num_4_8_experts_ci) / num_total))))

      out_file.write('\nExpert All Users\n')
      out_file.write('----------------\n')
      out_file.write('0 - 1 hours: %s (%s percent of total)\n'
                     % (num_0_1_experts_all, (100 * (float(num_0_1_experts_all) / num_total))))
      out_file.write('1 - 4 hours: %s (%s percent of total)\n'
                     % (num_1_4_experts_all, (100 * (float(num_1_4_experts_all) / num_total))))
      out_file.write('4 - 8 hours: %s (%s percent of total)\n'
                     % (num_4_8_experts_all, (100 * (float(num_4_8_experts_all) / num_total))))

      out_file.write('\nAll Users\n')
      out_file.write('---------\n')
      out_file.write('0 - 1 hours: %s (%s percent of total)\n'
                     % (num_0_1, (100 * (float(num_0_1) / num_total))))
      out_file.write('1 - 4 hours: %s (%s percent of total)\n'
                     % (num_1_4, (100 * (float(num_1_4) / num_total))))
      out_file.write('4 - 8 hours: %s (%s percent of total)\n'
                     % (num_4_8, (100 * (float(num_4_8) / num_total))))
      out_file.write('8 - + hours: %s (%s percent of total)\n'
                     % (num_after_8, (100 * (float(num_after_8) / num_total))))

      out_file.write('\ntotal: %s' % num_total);


def log(message):
  """Helper method to modularize the format of log messages.
  
  Keyword Arguments:
  message -- A string to log.
  """
  FileLog.log(_LOG_FILE, message)
  

if __name__ == "__main__":
  run()
