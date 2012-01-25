#!/usr/bin

#working dir
#cd /dfs/birch/tsv

#counting tweets
find . -iname tweeter_stream_data.*.tweet.http_nyti_ms.tsv -exec wc -l '{}' \; >line_count_tweet_08_12.txt
total line_count_tweet_08_12.txt

#counting users -- take 1 minute
find . -iname tweeter_stream_data.*.user.http_nyti_ms.tsv -print|xargs awk '{print $1}'|sort|uniq|wc -l

#counting urls 08~12: 2,474,615 short url --> 92452 news url
awk '{print $2}' URLExapnd.cache.txt|sort|uniq|wc -l
