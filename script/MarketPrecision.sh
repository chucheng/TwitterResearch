#!/bin/sh
src_dir='../src/'
data_dir='../data/'
python $src_dir"MarketPrecision.py" $data_dir"URLExpand.tweet.longurl.2011_08.http_nyti_ms.txt" $data_dir"URLExpand.tweet.longurl.2011_09.http_nyti_ms.txt" $data_dir"URLExpand.tweet.longurl.2011_10.http_nyti_ms.txt"
