import FileLog
import Util

import re

_LOG_FILE = 'aTopCateogires.log'

_TIMEDELTAS_FILE_TWEET_ID_INDEX = 0
_TIMEDELTAS_FILE_USER_ID_INDEX = 1 
_TIMEDELTAS_FILE_DELTA_INDEX = 2
_TIMEDELTAS_FILE_URL_INDEX = 3

def extract_category(url):
  """Extracts the 'categories' from a given nytimes url.

  Keyword Params:
  url -- A url from the nytimes.

  Returns:
  The keyword of the category the url belongs to, or None if we cannot det
  """
  r1 = re.compile('http://www.nytimes.com/[0-9]{4}/[0-9]{2}/[0-9]{2}/.*/.*')
  r2 = re.compile(
      'http://www.nytimes.com/[a-zA-Z]/[0-9]{4}/[0-9]{2}/[0-9]{2}/.*/.*')
  if r1.match(url):
    return url.split('/')[6]
  elif r2.match(url):
    return url.split('/')[7]
  else:
    return None

def run():
  """Main logic for this anlysis.

  Iterates of the time deltas, attempts to determine a category for each one,
  and counts the number of stories and number of tweets for each category.
  """
  categories = {}
  urls_seen = set()
  with open('../data/FolkWisdom/time_deltas.tsv') as f:
    for line in f:
      tokens = line.split('\t')
      url = tokens[_TIMEDELTAS_FILE_URL_INDEX]
      category = extract_category(url)
      if category in categories:
        (num_stories, total_num_tweets) = categories[category]
        if url in urls_seen:
          categories[category] = (num_stories, total_num_tweets + 1)
        else:
          categories[category] = (num_stories + 1, total_num_tweets + 1)
          urls_seen.add(url)
      elif category:
        categories[category] = (1, 1)
        urls_seen.add(url)
  categories_sorted_sec = sorted(categories.items(), key=lambda x: x[1][1],
                                 reverse=True)
  categories_sorted = sorted(categories_sorted_sec, key=lambda x: x[1][0],
                             reverse=True)


  Util.ensure_dir_exist('../data/TopCategories/')
  with open('../data/TopCategories/category_counts.tsv', 'w') as f:
    for (category, (num_stories, total_num_tweets)) in categories_sorted:
      f.write('%s\t%s\t%s\n' % (category, num_stories, total_num_tweets))
      log('%s\t%s\t%s' % (category, num_stories, total_num_tweets))


def log(message):
  """Helper method to modularize the format of log messages.
  
  Keyword Arguments:
  message -- A string to log.
  """
  FileLog.log(_LOG_FILE, message)
  

if __name__ == "__main__":
    run()
