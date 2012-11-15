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
import user_groups
import rankings
import mixed_model
import ground_truths
import precision_recall
from ground_truths import DataSet

from params import _DELTAS
from params import _CATEGORIES
from params import _SIZE_EXPERTS
from params import _SIZE_TOP_NEWS
from params import _SWITCHED
from params import _EXCLUDE_TWEETS_WITHIN_DELTA
from params import _EXCLUDE_RETWEETS

from constants import _TESTING_SET_MONTHS

_GRAPH_DIR = Util.get_graph_output_dir('FolkWisdom/')
_LOG_FILE = 'aFolkWisdom.log'


def run():
  """Contains the main logic for this analysis."""
  FileLog.set_log_dir()

  seeds = Util.load_seeds()
  for category in _CATEGORIES:
    log('Preforming analysis for category: %s' % category)
    size_top_news = _SIZE_TOP_NEWS
    if category:
      size_top_news = .10

    data_set = DataSet.TESTING
    retweets = set()
    if _SWITCHED:
      data_set = DataSet.TRAINING
    if _EXCLUDE_RETWEETS:
      retweets = ground_truths.find_retweets(_TESTING_SET_MONTHS)
    log('Num retweets to exclude: %s' % len(retweets))
    gt_rankings = ground_truths.get_gt_rankings(seeds, data_set, category,
                                                exclude_tweets_within_delta=_EXCLUDE_TWEETS_WITHIN_DELTA,
                                                retweets=retweets)
    log('Num ground_truth_rankings: %s' % len(gt_rankings))

    # Format for use later.
    ground_truth_url_to_rank = {}
    for rank, (url, count) in enumerate(gt_rankings):
      ground_truth_url_to_rank[url] = rank

    target_news = ground_truths.find_target_news(gt_rankings, size_top_news)
    log('Size target_news: %s' % len(target_news))

    for delta in _DELTAS:
      run_params_str = 'd%s_t%s_e%s_%s' % (delta, int(size_top_news * 100),
                                           int(_SIZE_EXPERTS * 100), category)
      info_output_dir = '../graph/FolkWisdom/%s/info/' % run_params_str
      Util.ensure_dir_exist(info_output_dir)


      groups = user_groups.get_all_user_groups(delta, category)
      log('Num experts (precision): %s' % len(groups.precision))
      log('Num experts (fscore): %s' % len(groups.fscore))
      log('Num experts (ci): %s' % len(groups.ci))
      log('Num Super Experts: %s' %len(groups.super_experts))
      log('Num Social Bias Experts: %s' % len(groups.social_bias))

      log('Finding rankings with an %s hour delta.' % delta)
      ranks = rankings.get_rankings(delta, seeds, groups, category)

      # Output some interesting info to file
      size_market_unfiltered = '0'
      with open('../data/FolkWisdom/size_of_market_unfiltered.txt') as in_file:
        size_market_unfiltered = in_file.readline().strip()

      with open('%suser_demographics_%s.txt'
                % (info_output_dir, run_params_str), 'w') as output_file:
        output_file.write('Number of Newsaholics: %s\n' % len(groups.newsaholics))
        output_file.write('Number of Active Users: %s\n' % len(groups.active_users))
        output_file.write('Number of Common Users: %s\n' % len(groups.common_users))
        output_file.write('\n');
        output_file.write('Number of Precision Experts: %s\n' % len(groups.precision))
        output_file.write('Number of F-Score Experts: %s\n' % len(groups.fscore))
        output_file.write('Number of CI Experts: %s\n' % len(groups.ci))
        output_file.write('Number of Social Bias Experts: %s\n' % len(groups.social_bias))
        output_file.write('Total number of unique experts: %s\n' % len(groups.all_experts))
        output_file.write('Number of Precision and F-Score Experts: %s\n'
                          % len(groups.precision.intersection(groups.fscore)))
        output_file.write('Number of Precision and CI Experts: %s\n'
                          % len(groups.precision.intersection(groups.ci)))
        output_file.write('Number of F-Score and CI Experts: %s\n'
                          % len(groups.fscore.intersection(groups.ci)))
        output_file.write('Number of Super Experts: %s\n' % len(groups.super_experts))
        output_file.write('\n');
        output_file.write('Number of Users (Total): %s\n'
                          % (len(groups.newsaholics) + len(groups.active_users)
                             + len(groups.common_users)))
        output_file.write('Size of market (unfiltered): %s\n'
                          % size_market_unfiltered)
        output_file.write('\n')
        # output_file.write('Number of votes by Newsaholics: %s\n'
        #                   % num_votes_newsaholics)
        # output_file.write('Number of votes by Market: %s\n' % num_votes_market)
        # output_file.write('Number of votes by Active Users: %s\n'
        #                   % num_votes_active)
        # output_file.write('Number of votes by Common Users: %s\n'
        #                   % num_votes_common)
        # output_file.write('\n');
        # output_file.write('Number of votes by Expert (Precision) Users: %s\n'
        #         % num_votes_expert_precision) 
        # output_file.write('Number of votes by Expert (fscore) Users: %s\n'
        #         % num_votes_expert_fscore) 
        # output_file.write('Number of votes by Expert (ci) Users: %s\n'
        #         % num_votes_expert_ci) 
        # output_file.write('Number of votes by Super Experts: %s\n'
        #                   % num_votes_expert_s)
        # output_file.write('Number of votes by Social Bias Experts: %s\n'
        #                   % num_votes_expert_sb)
        # output_file.write('\n')
        # output_file.write('Total Number of votes cast: %s\n'
        #                   % (num_votes_newsaholics + num_votes_active
        #                      + num_votes_common))
        # output_file.write('\n')
        output_file.write('Total Number of Good News: %s\n' % len(target_news))

      log('Ground Truth Top 50')
      for i in range(min(len(gt_rankings), 50)):
        url, count = gt_rankings[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
      log('-----------------------------------')
      log('Newsaholic Top 5')
      for i in range(min(len(ranks.newsaholics), 5)):
        url, count = ranks.newsaholics[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
      log('-----------------------------------')
      log('Active Top 5')
      for i in range(min(len(ranks.active_users), 5)):
        url, count = ranks.active_users[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
      log('-----------------------------------')
      log('Common Top 5')
      for i in range(min(len(ranks.common_users), 5)):
        url, count = ranks.common_users[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
      log('-----------------------------------')
      log('nonexpert Top 5')
      for i in range(min(len(ranks.non_experts), 5)):
        url, count = ranks.non_experts[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
      log('-----------------------------------')
      log('Expert (Precision) Top 5')
      for i in range(min(len(ranks.precision), 5)):
        url, count = ranks.precision[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
      log('-----------------------------------')
      log('Expert (fscore) Top 5')
      for i in range(min(len(ranks.fscore), 5)):
        url, count = ranks.fscore[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
      log('-----------------------------------')
      log('Expert (ci) Top 5')
      for i in range(min(len(ranks.ci), 5)):
        url, count = ranks.ci[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
      log('-----------------------------------')
      log('Super Expert Top 5')
      for i in range(min(len(ranks.super_experts), 5)):
        url, count = ranks.super_experts[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))
      log('-----------------------------------')
      log('Social Bias Expert Top 5')
      for i in range(min(len(ranks.social_bias), 5)):
        url, count = ranks.social_bias[i]
        log('[%s] %s\t%s' %(i, url.strip(), count))

        
      market_rank_to_url = {}
      newsaholic_rank_to_url = {}
      active_rank_to_url = {}
      common_rank_to_url = {}
      expert_p_rank_to_url = {}
      expert_f_rank_to_url = {}
      expert_c_rank_to_url = {}
      expert_s_rank_to_url = {}
      for rank, (url, count) in enumerate(ranks.newsaholics):
        newsaholic_rank_to_url[rank] = url
      for rank, (url, count) in enumerate(ranks.population):
        market_rank_to_url[rank] = url
      for rank, (url, count) in enumerate(ranks.active_users):
        active_rank_to_url[rank] = url
      for rank, (url, count) in enumerate(ranks.common_users):
        common_rank_to_url[rank] = url
      for rank, (url, count) in enumerate(ranks.precision):
        expert_p_rank_to_url[rank] = url
      for rank, (url, count) in enumerate(ranks.fscore):
        expert_f_rank_to_url[rank] = url
      for rank, (url, count) in enumerate(ranks.ci):
        expert_c_rank_to_url[rank] = url
      for rank, (url, count) in enumerate(ranks.super_experts):
        expert_s_rank_to_url[rank] = url

      market_url_to_rank = {}
      precision_url_to_rank = {}
      fscore_url_to_rank = {}
      ci_url_to_rank = {}
      ci_1_url_to_rank = {}
      ci_2_url_to_rank = {}
      ci_3_url_to_rank = {}
      for rank, (url, count) in enumerate(ranks.non_experts):
        market_url_to_rank[url] = rank
      for rank, (url, count) in enumerate(ranks.precision):
        precision_url_to_rank[url] = rank
      for rank, (url, count) in enumerate(ranks.fscore):
        fscore_url_to_rank[url] = rank
      for rank, (url, count) in enumerate(ranks.ci):
        ci_url_to_rank[url] = rank
      for rank, (url, count) in enumerate(ranks.ci_1):
        ci_1_url_to_rank[url] = rank
      for rank, (url, count) in enumerate(ranks.ci_2):
        ci_2_url_to_rank[url] = rank
      for rank, (url, count) in enumerate(ranks.ci_3):
        ci_3_url_to_rank[url] = rank

      precisions, recalls = precision_recall.get_precision_recalls(gt_rankings, ranks)

      mixed_rankings = mixed_model.get_mixed_rankings(market_url_to_rank,
                                                      precisions.population,
                                                      precision_url_to_rank,
                                                      precisions.precision,
                                                      fscore_url_to_rank,
                                                      precisions.fscore,
                                                      ci_url_to_rank,
                                                      precisions.ci,
                                                      ground_truth_url_to_rank)

      mixed_ci_rankings = mixed_model.get_mixed_rankings(market_url_to_rank,
                                                         precisions.population,
                                                         ci_1_url_to_rank,
                                                         precisions.ci_1,
                                                         ci_2_url_to_rank,
                                                         precisions.ci_2,
                                                         ci_3_url_to_rank,
                                                         precisions.ci_3,
                                                         ground_truth_url_to_rank)
                                                         

      mixed_precisions, mixed_recalls = precision_recall.calc_precision_recall(gt_rankings, 
                                                                               mixed_rankings)

      mixed_ci_precisions, mixed_ci_recalls = precision_recall.calc_precision_recall(gt_rankings, 
                                                                                     mixed_ci_rankings)

      log('-----------------------------------')
      log('Mixed (min) Top 5')
      for i in range(min(len(mixed_rankings), 5)):
        url, count = mixed_rankings[i]
        log('[%s] %s\t%s' %(i + 1, url, count))
      log('-----------------------------------')

      with open('%sranking_comparisons_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as out_file:
        for gt_rank, (gt_url, _) in enumerate(gt_rankings):
          market_rank = 0
          precision_rank = 0
          ci_rank = 0
          fscore_rank = 0
          if gt_url in market_url_to_rank:
            market_rank = market_url_to_rank[gt_url] + 1
          if gt_url in precision_url_to_rank:
            precision_rank = precision_url_to_rank[gt_url] + 1
          if gt_url in ci_url_to_rank:
            ci_rank = ci_url_to_rank[gt_url] + 1
          if gt_url in fscore_url_to_rank:
            fscore_rank = fscore_url_to_rank[gt_url] + 1
          line = '%s\t%s\t%s\t%s\t%s\t%s\n' % (gt_url, gt_rank + 1, market_rank,
                                               precision_rank, ci_rank,
                                               fscore_rank)
          out_file.write(line)


      with open('%sground_truth_rankings_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as output_file:
        for url, count in gt_rankings:
          output_file.write('%s\t%s\n' % (url.strip(), count))
      with open('%smarket_rankings_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as output_file:
        for rank, (url, count) in enumerate(ranks.common_users):
          output_file.write('%s\t%s\t(%s,%s)\n'
                            % (url.strip(), count, rank,
                               ground_truth_url_to_rank[url]))
      with open('%snewsaholic_rankings_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as output_file:
        for rank, (url, count) in enumerate(ranks.newsaholics):
          output_file.write('%s\t%s\t(%s,%s)\n'
                            % (url.strip(), count, rank,
                               ground_truth_url_to_rank[url]))
      with open('%sactive_user_rankings_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as output_file:
        for rank, (url, count) in enumerate(ranks.active_users):
          output_file.write('%s\t%s\t(%s,%s)\n'
                            % (url.strip(), count, rank,
                               ground_truth_url_to_rank[url]))
      with open('%scommon_user_rankings_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as output_file:
        for rank, (url, count) in enumerate(ranks.common_users):
          output_file.write('%s\t%s\t(%s,%s)\n'
                            % (url.strip(), count, rank,
                               ground_truth_url_to_rank[url]))
      with open('%snonexpert_user_rankings_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as output_file:
        for rank, (url, count) in enumerate(ranks.non_experts):
          output_file.write('%s\t%s\t(%s,%s)\n'
                            % (url.strip(), count, rank,
                               ground_truth_url_to_rank[url]))
      with open('%sexpert_p_user_rankings_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as output_file:
        for rank, (url, count) in enumerate(ranks.precision):
          output_file.write('%s\t%s\t(%s,%s)\n'
                            % (url.strip(), count, rank,
                               ground_truth_url_to_rank[url]))
      with open('%sexpert_f_user_rankings_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as output_file:
        for rank, (url, count) in enumerate(ranks.fscore):
          output_file.write('%s\t%s\t(%s,%s)\n'
                            % (url.strip(), count, rank,
                               ground_truth_url_to_rank[url]))
      with open('%sexpert_c_user_rankings_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as output_file:
        for rank, (url, count) in enumerate(ranks.ci):
          output_file.write('%s\t%s\t(%s,%s)\n'
                            % (url.strip(), count, rank,
                               ground_truth_url_to_rank[url]))
      with open('%sexpert_s_user_rankings_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as output_file:
        for rank, (url, count) in enumerate(ranks.super_experts):
          output_file.write('%s\t%s\t(%s,%s)\n'
                            % (url.strip(), count, rank,
                            ground_truth_url_to_rank[url]))
      with open('%smixed_rankings_%s.tsv'
                % (info_output_dir, run_params_str), 'w') as output_file:
        for rank, (url, count) in enumerate(mixed_rankings):
          output_file.write('%s\t%s\t(%s,%s)\n'
                            % (url.strip(), count, rank,
                            ground_truth_url_to_rank[url]))

      with open('../data/FolkWisdom/market_precisions_%s.txt'
                % run_params_str, 'w') as out_file:
        for precision in precisions.common_users:
          out_file.write('%s\n' % precision)

      with open('../data/FolkWisdom/nonexpert_precisions_%s.txt'
                % run_params_str, 'w') as out_file:
        for precision in precisions.non_experts:
          out_file.write('%s\n' % precision)

      with open('../data/FolkWisdom/expert_p_precisions_%s.txt'
                % run_params_str, 'w') as out_file:
        for precision in precisions.precision:
          out_file.write('%s\n' % precision)

      with open('../data/FolkWisdom/expert_f_precisions_%s.txt'
                % run_params_str, 'w') as out_file:
        for precision in precisions.fscore:
          out_file.write('%s\n' % precision)

      with open('../data/FolkWisdom/expert_c_precisions_%s.txt'
                % run_params_str, 'w') as out_file:
        for precision in precisions.ci:
          out_file.write('%s\n' % precision)

      log('Drawing summary precision-recall graphs...')
      # draw_precision_recall_graph(market_precisions, market_recalls,
      precision_recall.draw([precisions.newsaholics, precisions.active_users,
                             precisions.common_users, precisions.precision,
                             precisions.fscore, precisions.ci,
                             precisions.super_experts],
                            [recalls.newsaholics, recalls.active_users,
                             recalls.common_users, recalls.precision,
                             recalls.fscore, recalls.ci, recalls.super_experts],
                            ['Newsaholics', 'Active', 'Common', 'Precision',
                             'F-score', 'CI', 'Super Experts'],
                            'precision_recall_all',
                            run_params_str)

      # Draw via old method because it has fancy markings.
      experts.draw_precision_recall_experts(precisions.non_experts, recalls.non_experts,
                                            precisions.precision, recalls.precision,
                                            precisions.fscore, recalls.fscore,
                                            precisions.ci, recalls.ci,
                                            run_params_str)

      log('Drawing experts precision-recall graph...')
      # precision_recall.draw([precisions.non_experts, precisions.precision,
      #                        precisions.fscore, precisions.ci],
      #                       [recalls.non_experts, recalls.precision,
      #                        recalls.fscore, recalls.ci],
      #                       ['Crowd', 'Precision', 'F-score', 'CI'],
      #                       'precision_recall_experts',
      #                       run_params_str)

      log('Drawing ci breakdown by followers precisions-recall graph...')
      precision_recall.draw([precisions.non_experts, precisions.ci,
                             precisions.ci_hi, precisions.ci_li],
                            [recalls.non_experts, recalls.ci,
                             recalls.ci_hi, recalls.ci_li],
                            ['Crowd', 'CI', 'CI High', 'CI Low'],
                            'precision_recall_ci_followers_breakdown',
                            run_params_str)

      log('Drawing social bias precision-recall graph...')
      precision_recall.draw([precisions.non_experts, precisions.social_bias,
                             precisions.precision, precisions.fscore,
                             precisions.ci],
                            [recalls.non_experts, recalls.social_bias,
                             recalls.precision, recalls.fscore,
                             recalls.ci],
                            ['Crowd', 'Influence Experts', 'Precision',
                             'F-score', 'CI'],
                            'precision_recall_social_bias',
                            run_params_str)

      log('Drawing basic groups precision-recall graph...')
      precision_recall.draw([precisions.newsaholics, precisions.active_users,
                             precisions.common_users],
                            [recalls.newsaholics, recalls.active_users,
                             recalls.common_users],
                            ['Newsaholics', 'Active Users', 'Common Users'],
                            'precision_recall_basic_groups',
                            run_params_str)

      log('Drawing crowd def precision-recall graph...')
      precision_recall.draw([precisions.population, precisions.non_experts,
                             precisions.common_users, precisions.non_experts_sampled],
                            [recalls.population, recalls.non_experts,
                             recalls.common_users, recalls.non_experts_sampled],
                            ['Population', 'Non-experts', 'Common Users',
                             'Non-experts sampling'],
                            'precision_recall_crowd_def',
                            run_params_str)

      # TODO: Replace with new method.
      log('Drawing mixed model precision-recall graph...')
      mixed_model.draw_precision_recall_mixed(precisions.non_experts, recalls.non_experts,
                                              mixed_precisions, mixed_recalls,
                                              run_params_str)

      log('Drawing mixed ci model precision-recall graph...')
      precision_recall.draw([precisions.non_experts, mixed_ci_precisions],
                            [recalls.non_experts, mixed_ci_recalls],
                            ['Crowd', 'Mixed'],
                            'precision_recall_mixed_ci',
                            run_params_str)


def log(message):
  """Helper method to modularize the format of log messages.
  
  Keyword Arguments:
  message -- A string to log.
  """
  FileLog.log(_LOG_FILE, message)
  

if __name__ == "__main__":
  run()
