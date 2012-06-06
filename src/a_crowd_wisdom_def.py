"""
This module performs an analysis on determining which group can perform better
at ranking when compared to the ground truth. Some definitions which apply
throughout this analysis:

ground_truth -- Determined as the ranking after summing up the tweet counts for
all four months.

market -- Defined as all users.

newsaholics -- Defined as the top 2% of active users when ranked by the rate at
which they tweet.

active_users -- Defined as users between 2% and 25% when ranked by the rate at
which they tweet.

common_users -- Defined as users ranked more than 25% when ranked by the rate
at which they tweet.

There are also 4 groups of experts, selected by precision, F-score, and
confidence interval methods described in wiki and in paper. The fourth expert
group, super experts, is defined as the intersection of the other 3.

Tweet counts for the user groups (market, newsaholics, active users, and common
users) are counted if they occur within a certain time delta of the original
introduction of that url.

__author__ = 'Chris Moghbel (cmoghbel@cs.ucla.edu)'
"""
import FileLog
import Util

import experts
import basic_groups
import common_user_groups
import ground_truths
from ground_truths import DataSet

import matplotlib
matplotlib.use("Agg")

# from constants import _DELTAS

_GRAPH_DIR = Util.get_graph_output_dir('CrowdWisdomDef/')
_LOG_FILE = 'a_crowd_wisdom_def.log'

_SIZE_EXPERTS = .10
_SIZE_TOP_NEWS = .02 # This is reset at the beginning of run.

_NUM_GROUPS = 5

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


def calc_precision_recall(gt_rankings, other_rankings):
  """Calculates the precision recall scores for a set of rankings against truth.

  Keyword Arguments:
  gt_rankings -- A list of (url, count) pairs representing the ground truth
                 rankings.
  other_rankings -- A list of (url, count) pairs representing the other
                    rankings.

  Returns:
  precisions -- A list of precisions, with the index equal to the number of
                'guesses'.
  recalls -- A list of recalls, with the index equal to the number of 'guesses'.
  """
  size_target_news = int(len(gt_rankings) * _SIZE_TOP_NEWS)
  max_num_news_to_consider = min(len(other_rankings),
                                 int(len(gt_rankings) * _SIZE_TOP_NEWS))
  target_news = set()
  for i in range(size_target_news):
    (url, _) = gt_rankings[i]
    target_news.add(url)

  precisions = []
  recalls = []
  # Increase # guesses from 1 to max_number
  for num_guesses in range(1, max_num_news_to_consider + 1):
    # for each guess, check if it's a hit
    hits = 0.0
    misses = 0.0
    for j in range(0, num_guesses):
      (url, _) = other_rankings[j]
      if url in target_news:
        hits += 1
      else:
        misses += 1
    precision = (hits / (hits + misses)) * 100.0
    recall = (hits / len(target_news)) * 100.0
    precisions.append(precision)
    recalls.append(recall)
  return precisions, recalls


def run():
  """Contains the main logic for this analysis."""
  global _SIZE_TOP_NEWS
  FileLog.set_log_dir()

  seeds = Util.load_seeds()
  for category in _CATEGORIES:
    log('Preforming analysis for category: %s' % category)
    if category:
      _SIZE_TOP_NEWS = .10
    else:
      _SIZE_TOP_NEWS = .02

    gt_rankings = ground_truths.get_gt_rankings(seeds, DataSet.TESTING,
                                                category)
    log('Num ground_truth_rankings: %s' % len(gt_rankings))


    target_news = ground_truths.find_target_news(gt_rankings, _SIZE_TOP_NEWS)
    log('Size target_news: %s' % len(target_news))

    # for delta in _DELTAS:
    for delta in [4]:
      run_params_str = 'd%s_t%s_e%s_%s' % (delta, int(_SIZE_TOP_NEWS * 100),
                                           int(_SIZE_EXPERTS * 100), category)
      output_dir = '../graph/CrowdWisdomDef/%s/' % run_params_str
      Util.ensure_dir_exist(output_dir)

      info_output_dir = '../graph/CrowdWisdomDef/%s/info/' % run_params_str
      Util.ensure_dir_exist(info_output_dir)

      output_dir = '../graph/CrowdWisdomDef/%s/' % run_params_str
      Util.ensure_dir_exist(output_dir)

      (num_users, newsaholics,
       active_users, common_users) = basic_groups.group_users(delta, category)
      log('Num newsaholics: %s' % len(newsaholics))
      log('Num active: %s' % len(active_users))
      log('Num common: %s' % len(common_users))

      common_user_buckets = common_user_groups.group_users(common_users, _NUM_GROUPS)
      for i, common_user_bucket in enumerate(common_user_buckets):
        print 'Number users in common user bucket %s: %s' % (i, len(common_user_bucket))

      experts_precision = experts.select_experts_precision(
          newsaholics.union(active_users), num_users, delta, _SIZE_EXPERTS,
          category)
      experts_fscore = experts.select_experts_fscore(len(target_news),
                                                     num_users,
                                                     delta, _SIZE_EXPERTS,
                                                     category)
      experts_ci = experts.select_experts_ci(num_users, delta, _SIZE_EXPERTS,
                                             category)
      super_experts = experts.select_super_experts(experts_precision,
                                                   experts_fscore,
                                                   experts_ci)

      log('Num experts (precision): %s' % len(experts_precision))
      log('Num experts (fscore): %s' % len(experts_fscore))
      log('Num experts (ci): %s' % len(experts_ci))

      log('Finding rankings with an %s hour delta.' % delta)
      (market_rankings, newsaholic_rankings,
       active_rankings,
       common_rankings) = basic_groups.get_rankings(delta, seeds, newsaholics,
                                                    active_users, category)
      (expert_precision_rankings, expert_fscore_rankings,
       expert_ci_rankings,
       expert_s_rankings) = experts.get_rankings(delta, seeds,
                                                 experts_precision,
                                                 experts_fscore,
                                                 experts_ci,
                                                 super_experts,
                                                 category)

      common_groups_rankings = common_user_groups.get_rankings(delta, seeds,
                                                               common_user_buckets,
                                                               category)

      num_votes_common = 0
      for url, count in common_rankings:
        num_votes_common += count
      log('Num common_rankings: %s' % len(common_rankings))
      log('Num common votes: %s' % num_votes_common)
      num_votes_expert_precision = 0
      for url, count in expert_precision_rankings:
        num_votes_expert_precision += count
      log('Num expert_precision rankings: %s' % len(expert_precision_rankings))
      log('Num expert_precision votes: %s' % num_votes_expert_precision)
      num_votes_expert_fscore = 0
      for url, count in expert_fscore_rankings:
        num_votes_expert_fscore += count
      log('Num expert_fscore rankings: %s' % len(expert_fscore_rankings))
      log('Num expert_fscore votes: %s' % num_votes_expert_fscore)
      num_votes_expert_ci = 0
      for url, count in expert_ci_rankings:
        num_votes_expert_ci += count
      log('Num expert_ci rankings: %s' % len(expert_ci_rankings))
      log('Num expert_ci votes: %s' % num_votes_expert_ci)
      num_votes_buckets = []
      for i, common_group_rankings in enumerate(common_groups_rankings):
        num_votes = 0
        for url, count in common_group_rankings:
          num_votes += count
        num_votes_buckets.append(num_votes)
        log('Num common rankings (%s buckets): %s' % (i, len(common_group_rankings)))
        log('Num expert_ci votes (%s buckets): %s' % (i, num_votes))

      with open('%suser_demographics_%s.txt'
                % (info_output_dir, run_params_str), 'w') as output_file:
        output_file.write('Number of Common Users: %s\n' % len(common_users))
        output_file.write('\n');
        output_file.write('Number of Precision Experts: %s\n' % len(experts_precision))
        output_file.write('Number of F-Score Experts: %s\n' % len(experts_fscore))
        output_file.write('Number of CI Experts: %s\n' % len(experts_ci))
        output_file.write('Number users per common user bucket: %s\n' %len(common_user_buckets[0]))
        output_file.write('Number of Precision and F-Score Experts: %s\n'
                          % len(experts_precision.intersection(experts_fscore)))
        output_file.write('Number of Precision and CI Experts: %s\n'
                          % len(experts_precision.intersection(experts_ci)))
        output_file.write('Number of F-Score and CI Experts: %s\n'
                          % len(experts_fscore.intersection(experts_ci)))
        output_file.write('\n');
        output_file.write('Number of Users (Total): %s\n'
                          % (len(newsaholics) + len(active_users)
                             + len(common_users)))
        output_file.write('\n')
        output_file.write('Number of votes by Common Users: %s\n'
                          % num_votes_common)
        output_file.write('\n');
        output_file.write('Number of votes by Expert (Precision) Users: %s\n'
                % num_votes_expert_precision) 
        output_file.write('Number of votes by Expert (fscore) Users: %s\n'
                % num_votes_expert_fscore) 
        output_file.write('Number of votes by Expert (ci) Users: %s\n'
                % num_votes_expert_ci) 
        output_file.write('Number of votes per bucket: %s\n' % num_votes_buckets)
        output_file.write('\n')
        output_file.write('Total Number of Good News: %s\n' % len(target_news))

      log('Ground Truth Top 5')
      for i in range(min(len(gt_rankings), 5)):
        url, count = gt_rankings[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
      log('-----------------------------------')
      log('Common Top 5')
      for i in range(min(len(common_rankings), 5)):
        url, count = common_rankings[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
      log('-----------------------------------')
      log('Expert (Precision) Top 5')
      for i in range(min(len(expert_precision_rankings), 5)):
        url, count = expert_precision_rankings[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
      log('-----------------------------------')
      log('Expert (fscore) Top 5')
      for i in range(min(len(expert_fscore_rankings), 5)):
        url, count = expert_fscore_rankings[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
      log('-----------------------------------')
      log('Expert (ci) Top 5')
      for i in range(min(len(expert_ci_rankings), 5)):
        url, count = expert_ci_rankings[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
      log('-----------------------------------')
        

      common_precisions, common_recalls = calc_precision_recall(gt_rankings,
                                                                common_rankings)
      (expert_p_precisions,
       expert_p_recalls) = calc_precision_recall(gt_rankings,
                                                 expert_precision_rankings)
      (expert_f_precisions,
       expert_f_recalls) = calc_precision_recall(gt_rankings,
                                                 expert_fscore_rankings)
      (expert_c_precisions,
       expert_c_recalls) = calc_precision_recall(gt_rankings,
                                                 expert_ci_rankings)

      common_group_ps = []
      common_group_rs = []
      for common_group_ranking in common_groups_rankings:
        common_group_p, common_group_r = calc_precision_recall(gt_rankings,
                                                               common_group_ranking)
        common_group_ps.append(common_group_p)
        common_group_rs.append(common_group_r)
                                                

      log('Drawing common group model precision-recall graph...')
      common_user_groups.draw_precision_recall(common_group_ps, common_group_rs,
                                               expert_p_precisions, expert_p_recalls,
                                               expert_f_precisions, expert_f_recalls,
                                               expert_c_precisions, expert_c_recalls,
                                               run_params_str)

      log('Drawing common group model precision graph...')
      common_user_groups.draw_precision(common_group_ps, expert_p_precisions,
                                        expert_f_precisions, expert_c_precisions,
                                        run_params_str)



def log(message):
  """Helper method to modularize the format of log messages.
  
  Keyword Arguments:
  message -- A string to log.
  """
  FileLog.log(_LOG_FILE, message)
  

if __name__ == "__main__":
  run()
