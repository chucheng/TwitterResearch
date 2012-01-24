import urlparse
import re


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
        expanded_urls.append(long_url)
    else:
      if 'nytimes.com' in url:
        expanded_urls.append(url)
  return expanded_urls
