import urlparse
import re


def extract_category(url):
  """Extracts the 'categories' from a given nytimes url.

  Keyword Params:
  url -- A url from the nytimes.

  Returns:
  The keyword of the category the url belongs to, or None if we cannot det
  """
  r1 = re.compile('http://www.nytimes.com/[0-9]{4}/[0-9]{2}/[0-9]{2}/.*/.*')
  r2 = re.compile(
      'http://www.nytimes.com/[a-zA-Z]+/[0-9]{4}/[0-9]{2}/[0-9]{2}/.*/.*')
  if r1.match(url):
    return url.split('/')[6]
  elif r2.match(url):
    return url.split('/')[7]
  else:
    return None


def extract_http(text):
  """Extract URLs(http) from a given content"""
  r = re.compile(r"(http://[^ ]+)")
  return r.findall(text)


def parse_urls(text, cache):
  urls = extract_http(text)
  expanded_urls = []
  for url in urls:
    if cache.has_key(url):
      long_url = cache[url]
      if 'nytimes.com' in long_url:
        expanded_urls.append(long_url.strip())
    else:
      if 'nytimes.com' in url:
        expanded_urls.append(url.strip())
  return expanded_urls
