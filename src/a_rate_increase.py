"""
This analysis attempts to show the impact of social hub bias.

The analysis outputs a number of graphs that compare a story in
which nyt participated to a story in which nyt did not participate.
The main concept stands that if social hub bias happens, we should see
a 'surge' right after nyt tweets in some graphs.

__author__ = 'Chris Moghbel (cmoghbel@cs.ucla.edu)'
"""
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

_LOG_FILE = 'a_rate_increase.log'
_GRAPH_DIR = Util.get_graph_output_dir('RateIncrease/')

_SIZE_TOP_NEWS = .02

_NYT_USER_ID = '807095'


def draw_graph(counts_nyt, counts_not_nyt, (nyt_x, nyt_y),  num, param_str):
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

  nyt_plot = axs.plot(counts_nyt)
  not_nyt_plot = axs.plot(counts_not_nyt)

  # plt.text(x, y, 'nyt')
  axs.annotate('nyt', xy=(nyt_x, nyt_y), xytext=(nyt_x + 5, nyt_y + 5),
               arrowprops=dict(facecolor='black', shrink=0.05, width=0.50,
                               headwidth=5))
  plt.legend([nyt_plot, not_nyt_plot],
             ['@nytimes is participant', '@nytimes not participant'],
             loc=0, handletextpad=0)

  plt.xlabel('Time (Minutes)')
  plt.ylabel('Number of Tweets Accumulated')

  with open(_GRAPH_DIR + '%s/rate_increase_%s_%s.png'
            % (param_str, param_str, num), 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + '%s/rate_increase_%s_%s.eps'
            % (param_str, param_str, num), 'w') as graph:
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


def run():
  """Main logic for this analysis."""
  seeds = Util.load_seeds()
  gt_ranks = ground_truths.get_gt_rankings(seeds, DataSet.ALL)
  target_news = ground_truths.find_target_news(gt_ranks, _SIZE_TOP_NEWS)
  for delta in _DELTAS:
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
      for i in range(min(50, min(len(news_nyt_participant),
                                 len(news_nyt_not_participant)))):
        log('Outputting graph %s...' % i)
        url_nyt = news_nyt_participant.pop()
        url_not_nyt = news_nyt_not_participant.pop()
        nyt_tweeted_min = when_nyt_tweeted[url_nyt]
        out_file.write('%s\t%s\t%s\n' % (i, url_nyt, url_not_nyt))
        draw_graph(agg_counts[url_nyt], agg_counts[url_not_nyt],
                   (nyt_tweeted_min, agg_counts[url_nyt][nyt_tweeted_min]), i,
                   param_str)

  log('Analysis complete!')


def log(message):
  """Helper method to modularize the format of log messages.
  
  Keyword Arguments:
  message -- A string to log.
  """
  FileLog.log(_LOG_FILE, message)
  

if __name__ == "__main__":
  run()
