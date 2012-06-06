
import Util
import FileLog
import ground_truths
from ground_truths import DataSet

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from constants import  _TIMEDELTAS_FILE_USER_ID_INDEX
from constants import  _TIMEDELTAS_FILE_DELTA_INDEX
from constants import  _TIMEDELTAS_FILE_URL_INDEX
from constants import _DELTAS

_LOG_FILE = 'a_rate_increase_specific.log'
_GRAPH_DIR = Util.get_graph_output_dir('RateIncrease/specific/')

_SIZE_TOP_NEWS = .02

_NYT_USER_ID = '807095'

_STORY_NYT = ('http://thelede.blogs.nytimes.com/2011/08/21/'
              'latest-updates-on-the-battle-for-tripoli/')

_STORY_NOT_NYT = ('http://opinionator.blogs.nytimes.com/2011/12/27/'
                  'bacteria-1-f-d-a-0/')


def draw_graph(counts_nyt, counts_not_nyt, annotations, param_str):
  """Draws a line graph comparing the two aggregate counts.

  Keyword Arguments:
  counts_nyt -- (List<int>) list of total num tweets accumulated by each minute.
  counts_not_nyt -- (List<int>) list of total num tweets accum by each minute.
  (nyt_x, nyt_y) -- The (x,y) coordinates corresponding to the min, count at
                    which @nytimes tweeted.
  num -- (int) The corresponding legend number.
  param_str -- The params the data was generated under.
  """
  figure = plt.figure()
  axs = figure.add_subplot(111)

  nyt_plot = axs.plot(counts_nyt, linewidth=2)
  not_nyt_plot = axs.plot(counts_not_nyt, '--', linewidth=2)

  # nytimes
  (x, y, screen_name) = annotations[0]
  axs.annotate(screen_name, xy=(x, y), xytext=(x - 100, y + 10), fontsize=16,
               arrowprops=dict(facecolor='black', shrink=0.05, width=0.75,
                               headwidth=10))
  # evertuts
  (x, y, screen_name) = annotations[1]
  axs.annotate(screen_name, xy=(x, y), xytext=(x - 100,  y + 20), fontsize=16,
               arrowprops=dict(facecolor='black', shrink=0.05, width=0.75,
                               headwidth=10))
  # nytjim
  (x, y, screen_name) = annotations[2]
  axs.annotate(screen_name, xy=(x, y), xytext=(x - 100,  y), fontsize=16,
               arrowprops=dict(facecolor='black', shrink=0.05, width=0.75,
                               headwidth=10))
  # nytimesglobal
  (x, y, screen_name) = annotations[3]
  axs.annotate(screen_name, xy=(x, y), xytext=(x + 30,  y), fontsize=16,
               arrowprops=dict(facecolor='black', shrink=0.05, width=0.75,
                               headwidth=10))
  # Larryferlazzo
  (x, y, screen_name) = annotations[4]
  axs.annotate(screen_name, xy=(x, y), xytext=(x - 150,  y + 50), fontsize=16,
               arrowprops=dict(facecolor='black', shrink=0.05, width=0.75,
                               headwidth=10))
  
  plt.legend([nyt_plot, not_nyt_plot],
             ['@nytimes is participant', '@nytimes not participant'],
             loc=0, handletextpad=0)

  plt.xlabel('Time (Minutes)', fontsize='16')
  plt.ylabel('Number of Tweets Accumulated', fontsize='16')

  with open(_GRAPH_DIR + '%s/rate_increase_%s.png'
            % (param_str, param_str), 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + '%s/rate_increase_%s.eps'
            % (param_str, param_str), 'w') as graph:
    plt.savefig(graph, format='eps')

  plt.close()
  

def find_counts(target_news, delta):
  """Finds the counts for each news story within a given delta.

  Keyword Arguments:
  target_news -- (Set<str>) urls to get counts for.
  delta -- (int) given in hours, the time in which a tweet must occur.

  Returns:
  counts -- (Dict<url, Dict<min, count>>) url ->
                                          (min -> num of tweets in that min)
  news_nyt_participant -- (Set<str>) urls in which @nytimes tweeted in window.
  news_nyt_not_participant -- (Set<str>) urls where @nytimes did not tweet.
  when_nyt_tweeted -- (Dict<url, int>) url -> min at which nyt tweeted.
  """
  log('Finding counts...')
  news_nyt_participant = set()
  counts = {}
  when_nyt_tweeted = {}
  with open('../data/FolkWisdom/time_deltas.tsv') as in_file:
    for line in in_file:
      tokens = line.split('\t')
      url = tokens[_TIMEDELTAS_FILE_URL_INDEX].strip()
      tweet_delta = int(tokens[_TIMEDELTAS_FILE_DELTA_INDEX])
      user_id = tokens[_TIMEDELTAS_FILE_USER_ID_INDEX]
      if (tweet_delta / 3600.) >= delta:
        break
      if url in target_news:
        tweet_delta_min = tweet_delta / 60
        if url in counts:
          if tweet_delta_min in counts[url]:
            counts[url][tweet_delta_min] += 1
          else:
            counts[url][tweet_delta_min] = 1
        else:
          counts[url] = {tweet_delta_min: 1}
        if user_id == _NYT_USER_ID:
          news_nyt_participant.add(url)
          when_nyt_tweeted[url] = tweet_delta_min
  news_nyt_not_participant = target_news.difference(news_nyt_participant)
  return (counts, news_nyt_participant, news_nyt_not_participant,
          when_nyt_tweeted)


def aggregate_counts(counts, delta):
  """Takes basic count info and aggregates it on per minute basis.

  Keyword Arguments:
  counts -- (Dict<url, Dict<min, count>>) url ->
                                          (min -> num of tweets in that min)
  delta -- (int) The delta, in hours.

  Returns:
  agg_counts -- (Dict<url, list<int>) url -> list of total number of tweets
                                      accumulated by each minute.
  """
  log('Aggregating counts...')
  agg_counts = {}
  for url, count_dict in counts.items():
    count_list = []
    for minute in range(0, delta * 60):
      num_tweets_in_minute = count_dict[minute] if minute in count_dict else 0
      prev_count = 0 if minute == 0 else count_list[minute - 1]
      count_list.append(prev_count + num_tweets_in_minute)
    agg_counts[url] = count_list
  return agg_counts


def find_additional_info(url, user_info, delta):
  """Gathers additional information about a given url.

  Keyword Arguments:
  url -- (str) The url to find additional info for.
  user_info -- (Dict<str, crawl_users.User>) user_id -> crawl_users.User
  delta -- (int) The delta for the time window, given in hours.

  Returns:
  additional_info -- (List<(str, (str, int, int))>)
                     [(user_id, (followers_count, screen_name, minutes))...]
  """
  log('Finding addtional information for: %s with delta %s...' % (url, delta))
  additional_info = {}
  with open('../data/FolkWisdom/time_deltas.tsv', 'r') as in_file:
    for line in in_file:
      tokens = line.split('\t')
      tweet_delta = int(tokens[_TIMEDELTAS_FILE_DELTA_INDEX])
      if tweet_delta < (delta * 3600):
        tweet_url = tokens[_TIMEDELTAS_FILE_URL_INDEX]
        if tweet_url == url:
          tweet_author_id = tokens[_TIMEDELTAS_FILE_USER_ID_INDEX]
          if tweet_author_id in user_info:
            user = user_info[tweet_author_id]
            additional_info[tweet_author_id] = (user.followers_count,
                                                user.screen_name,
                                                tweet_delta / 60)
  return sorted(additional_info.items(), key=lambda x: x[1][0], reverse=True)


def run():
  """Main logic for this analysis."""
  seeds = Util.load_seeds()
  gt_ranks = ground_truths.get_gt_rankings(seeds, DataSet.ALL)
  target_news = ground_truths.find_target_news(gt_ranks, _SIZE_TOP_NEWS)
  # for delta in _DELTAS:
  for delta in [8] :
    log('Performing analysis for delta %s' % delta)
    param_str = 'd%s' % delta
    Util.ensure_dir_exist(_GRAPH_DIR + '%s/' % param_str)
    Util.ensure_dir_exist(_GRAPH_DIR + '%s/info/' % param_str)

    (counts, news_nyt_participant,
     news_nyt_not_participant, when_nyt_tweeted) = find_counts(target_news,
                                                               delta)
    agg_counts = aggregate_counts(counts, delta)

    with open(_GRAPH_DIR + '%s/info/stats.txt' % param_str, 'w') as out_file:
      out_file.write('Num stories total: %s\n' % len(target_news))
      out_file.write('Num NYT Participant: %s\n' % len(news_nyt_participant))
      out_file.write('Num NYT Not Participant: %s\n'
                     % len(news_nyt_not_participant))

    with open(_GRAPH_DIR + '%s/info/legend.tsv' % param_str, 'w') as out_file:
      log('Outputting graph...')
      nyt_tweeted_min = when_nyt_tweeted[_STORY_NYT]
      annotations = []
      annotations.append((nyt_tweeted_min,
                          agg_counts[_STORY_NYT][nyt_tweeted_min], '@nytimes'))
      annotations.append((204, agg_counts[_STORY_NYT][204], '@evertuts'))
      annotations.append((193, agg_counts[_STORY_NYT][193], '@nytjim'))
      annotations.append((194, agg_counts[_STORY_NYT][194], '@nytimesglobal'))
      annotations.append((222, agg_counts[_STORY_NYT][222], '@Larryferlazzo'))
      draw_graph(agg_counts[_STORY_NYT], agg_counts[_STORY_NOT_NYT],
                 annotations, param_str)


  log('Analysis complete!')


def log(message):
  """Helper method to modularize the format of log messages.
  
  Keyword Arguments:
  message -- A string to log.
  """
  FileLog.log(_LOG_FILE, message)
  

if __name__ == "__main__":
  run()
