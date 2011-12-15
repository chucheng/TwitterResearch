"""
This module contains utility functions useful in analysis of Market Decisions
data.

Exports:
RELATIVE_PATH_TO_DATA -- Relative path to the data directory
FILE_TEMPLATE -- The file name convention, parameterize by hours
TRUE_COUNT_FILE -- The name of the true count file.

Functions:
load_true_ranks -- Loads the true counts from disk into memory.
pad_time_period -- Returns 3 char string representation of an int.

__author__ = 'Chris Moghbel (cmoghbel@cs.ucla.edu)'
"""

import Configuration
config = Configuration.getConfig()
_data_dir = config.get("Path", "base-dir") + config.get("Path", "data-dir")
FULL_PATH_TO_DATA = _data_dir + \
    config.get("aMarketDecision", "relative-path-to-data") 
FILE_TEMPLATE = config.get("aMarketDecision", "data-file-template")
TRUE_COUNT_FILE = FULL_PATH_TO_DATA + config.get("aMarketDecision", "groud-truth-file")

def load_true_ranks():
    """Loads the true ranks from disk.

    Avoids having to load the true ranks multiple times, which would be
    inefficient.

    Returns:
    true_ranks -- A Dictionary with urls mapped to their ranks
    """
    true_count_file_path = TRUE_COUNT_FILE

    true_ranks = {}

    with open(true_count_file_path) as f:
        lines = f.readlines()
        for i in range(0, len(lines)):
            rank = i + 1
            line = lines[i]
            tokens = line.split('\t')
            news_url = tokens[0]
            true_ranks[news_url] = rank

    return true_ranks


def pad_time_period(time_period):
    """Gives a 3 character string representation for an integer.

    Useful for when iterating over the 1-100 hour files.

    Keyword Arguments:
    time_period -- An integer representing the time period

    Returns:
    A 3 character representation of the given integer
    """
    if time_period < 1:
        raise Exception('Time period of less than 0 does not make sense.')
    elif time_period >= 1 and time_period < 10:
        return '00%s' % time_period
    elif time_period >= 10 and time_period < 100:
        return '0%s' % time_period
    else:
        return '%s' % time_period