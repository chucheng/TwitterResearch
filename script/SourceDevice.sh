#!/bin/sh

# Sum up all number of tweets 
cut -f2 source_device_all.tsv|python -c "import sys; print sum(int(l) for l in sys.stdin)"
