import Configuration
import Util

from MarketDecisionUtils import *
from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt

_PERCENTAGES = [.02, .05, .10]
_LABELS = ['Top 2%', 'Top 5%', 'Top 10%']
_BIG_CHANGE_THRESHOLD_PERCENTAGE = 0.02
_NUM_TIME_PERIODS = 100
_GRAPH_DIR = None # defined right after _get_graph_output_dir()

"""
This module performs an analysis on how the rank of a tweet changes between
a given time and its eventual true count. The rank is determined by the number
of tweets a url has, including retweets. This analysis produces two graphs:

    1. The first graph examines the average change in rank from a time to
       it's final rank in the true count.
    2. The second graph examines the total number of changes in rank from a
       time to the final rank in the true count that exceed a threshold
       percentage of the total number of urls.
    3. The third graph examines the percentage of the top X% of urls that stay
       the same between a time period and the true counts, which I am calling
       "stability".

All graphs compare the top 2%, 5%, and 10% at each time period collected in
the data set.

Functions:
calculate_stability -- Calculates percentage of the top X% that stays the same.
calculate_changes -- Calculates change metrics against true counts.
draw_avg_change_graph -- Draws the appropriate graph.
draw_big_changes -- Draws the appropriate graph.
draw_stability -- Draws the appropriate graph.
run -- Main logic.


__author__ = 'Chris Moghbel (cmoghbel@cs.ucla.edu)'
"""

def _get_graph_output_dir():
    """Assign an output path for the graph(s).
    
    """
    cfg = Configuration.getConfig()
    graph_dir = cfg.get("Path", "base-dir") + cfg.get("Path", "graph-dir")
    graph_dir += "MarketDecision/"
    Util.ensure_dir_exist(graph_dir)
    return graph_dir


_GRAPH_DIR = _get_graph_output_dir()

def calculate_stability(hour, true_ranks, percentage):
    """Compares "stability" of a time period against the true count values.

    "Stability" is the percentage of the top X% of urls that stay the same
    between a time period and the true counts.

    Keyword Arguments:
    hour -- The time period to compare with. Should be in the format of a
            3 char string, e.g. 001
    true_ranks -- Dictionary of the true count values, mapping urls to ranks.
    percentage -- The current percentage (top X%) to consider.

    Returns:
    stability -- The percentage of the top X% of urls that stay the same.
                          compared to the true counts, as an int
    """
    time_file_path = FULL_PATH_TO_DATA + FILE_TEMPLATE % hour

    rank_cutoff = int(percentage * len(true_ranks))

    num_similar = 0
    with open(time_file_path) as f:
        for i in range(0, rank_cutoff):
            line = f.readline()
            tokens = line.split('\t')
            news_url = tokens[0]
            if true_ranks.has_key(news_url):
                true_rank = true_ranks.get(news_url)
                if true_rank < rank_cutoff:
                    num_similar += 1

    stability = ((1.0 * num_similar) / rank_cutoff) * 100.0
    return stability

def calculate_changes(hour, true_ranks, percentage):
    """Compares rankings values of a time period against the true count values.

    Keyword Arguments:
    hour -- The time period to compare with. Should be in the format of a
            3 char string, e.g. 001
    true_ranks -- Dictionary of the true count values, mapping urls to ranks.
    percentage -- The current percentage (top X%) to consider.

    Returns:
    avg_change_in_rank -- The average change in rank for the time period when
                          compared to the true counts, as an int
    num_big_changes_in_rank -- The number of changes in rank exceeding the
                               given threshold
    """
    time_file_path = FULL_PATH_TO_DATA + FILE_TEMPLATE % hour

    # Calculate necessary threshold values.
    num_urls_to_consider = int(percentage * len(true_ranks))
    rank_change_threshold = int(_BIG_CHANGE_THRESHOLD_PERCENTAGE *
                               len(true_ranks))

    sum_changes_in_rank = 0
    num_big_changes_in_rank = 0
    with open(time_file_path) as f:
        for i in range(0, num_urls_to_consider):
            rank = i + 1
            line = f.readline()
            tokens = line.split('\t')
            news_url = tokens[0]
            change_in_rank = abs(rank - true_ranks[news_url])
            sum_changes_in_rank += change_in_rank
            if change_in_rank > rank_change_threshold:
                num_big_changes_in_rank += 1

    avg_change_in_rank = sum_changes_in_rank / num_urls_to_consider
    return avg_change_in_rank, num_big_changes_in_rank


def draw_avg_change_graph(avg_rank_changes, max_y):
    """Plots "average change" graph using matplotlib.

    This graph shows the average change in rank between a time and the true
    count. The data is given in the parameter avg_rank_changes.
    avg_rank_changes should be a list of 3 lists, one list for each
    percentage (2%, 5%, and 10%). Each of these three lists should have
    100 entries, one for each time period.
    e.g. avg_rank_changes = [[e1,...,e100][e1,...,e100][e1,...,e100]]
                            with ei being the entry at index i in the list

    Keyword Arguments:
    avg_rank_changes -- The data for the avg changes graph.
    max_y -- The maximum y value seen in avg_rank_changes.
    """
    plots = []
    figure = plt.figure()
    ax = figure.add_subplot(111)
    for avg_rank_changes_for_percentage in avg_rank_changes:
        myplt = ax.plot(avg_rank_changes_for_percentage)
        plots.append(myplt)

    plt.legend(plots, _LABELS)
    plt.axis([1, _NUM_TIME_PERIODS + 1, 0, int(max_y)])
    plt.grid(True, 'major', linewidth=2)
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    ax.yaxis.set_minor_locator(MultipleLocator(100))
    plt.grid(True, 'minor')
    plt.xlabel('time (hours)')
    plt.ylabel('average difference ($R_{x}$ vs $R_{t}$)')
    plt.title('Average Change in Rank from Time Period to True Count')

    with open(_GRAPH_DIR + 'avg_change_in_rank.png', 'w') as graph:
        plt.savefig(graph, format='png')
    with open(_GRAPH_DIR + 'avg_change_in_rank.eps', 'w') as graph:
        plt.savefig(graph, format='eps')        
    print ('Outputted Graph: Average Change in Rank from Time Period to '
           'True Count')
    plt.close()


def draw_big_changes_graph(big_rank_changes, max_y):
    """Plots "number of big changes" graph using matplotlib.

    This graph shows the number of "big" changes in rank that occur.
    The data is given in the parameter big_rank_changes. big_rank_changes
    should be a lists of lists, one for each percentage, and each list should
    have 100 entries.
    e.g. big_rank_changes = [[e1,...,e100][e1,...,e100][e1,...,e100]]
                            with ei being the entry at index i in the list

    Keyword Arguments:
    big_rank_changes -- The data for the big rank changes graph.
    max_y -- The maximum y value seen in big_rank_changes
    """
    plots = []
    figure = plt.figure()
    ax = figure.add_subplot(111)
    for big_rank_changes_for_percentage in big_rank_changes:
        myplt = ax.plot(big_rank_changes_for_percentage)
        plots.append(myplt)

    plt.legend(plots, _LABELS)
    plt.legend(loc=4)
    plt.axis([1, _NUM_TIME_PERIODS + 1, 0, int(max_y)])
    plt.grid(True, 'major', linewidth=2)
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    ax.yaxis.set_minor_locator(MultipleLocator(100))
    plt.grid(True, 'minor')
    plt.xlabel('time (hours)')
    plt.ylabel(('num rank changes (> %s percent)'
                % int(100 * _BIG_CHANGE_THRESHOLD_PERCENTAGE)))
    plt.title('Number of Large Rank Changes between Time Period and True Count')

    with open(_GRAPH_DIR + 'num_big_changes_in_rank.png', 'w') as graph:
        plt.savefig(graph, format='png')
    with open(_GRAPH_DIR + 'num_big_changes_in_rank.eps', 'w') as graph:
        plt.savefig(graph, format='eps')        
    print ('Outputted Graph: Number of Large Rank Changes between Time Period '
           'and True Count')
    plt.close()


def draw_stability_graph(stabilities, max_y):
    """Plots "stability" graph using matplotlib.

    This graph shows the stability of the top X% between a time period and the
    true count. In other words, it shows the percentage of the top X% that stay
    the same between a given time period and the true counts..

    The data is given in the parameter stabilities. stabilities should be a
    lists of lists, one for each percentage, and each list should have 100
    entries.
    e.g. big_rank_changes = [[e1,...,e100][e1,...,e100][e1,...,e100]]
                            with ei being the entry at index i in the list

    Keyword Arguments:
    stabilities -- The data for the stability graph.
    max_y -- The maximum y value (stability) seen.
    """
    plots = []
    figure = plt.figure()
    ax = figure.add_subplot(111)
    for stabilities_for_percentage in stabilities:
        myplt = ax.plot(stabilities_for_percentage)
        plots.append(myplt)

    plt.legend(plots, _LABELS, loc='lower right')
    plt.axis([1, _NUM_TIME_PERIODS + 1, 0, int(max_y * 1.10)])
    plt.grid(True, 'major', linewidth=2)
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    ax.yaxis.set_minor_locator(MultipleLocator(5))
    plt.grid(True, 'minor')
    plt.xlabel('time (hours)')
    plt.ylabel('percentage still in top X%')
    plt.title('Stability of Top X% Between Time Period and True Count')

    with open(_GRAPH_DIR + 'stability.png', 'w') as graph:
        plt.savefig(graph, format='png')
    with open(_GRAPH_DIR + 'stability.eps', 'w') as graph:
            plt.savefig(graph, format='eps')        
    print('Outputted Graph: Stability of Top X% Between Time Period '
          'and True Count')
    plt.close()


def run():
    """Main logic of this analysis.

    A high level overview of the logic follows:

    for each desired percentage:
        for each time period 1 to 100:
            find the avg change in rank, number of large rank changes,
            and stability for the current combination of percentage and rank
    plot graphs for avg change, big changes, and stability
    """
    # Pre-load the true counts once for efficiency.
    true_counts = load_true_ranks()

    # Blank data declarations, matching the parameters to the graph drawing
    # method.
    avg_rank_changes = []
    big_rank_changes = []
    stabilities = []
    max_avg_rank_change = 0
    max_num_big_rank_change = 0
    max_stability = 0

    for percentage in _PERCENTAGES:
        print 'Calculating for top %s percent' % int(100 * percentage)

        avg_rank_changes_for_percentage = []
        num_big_rank_changes_for_percentage = []
        stabilities_for_percentage = []
        for i in range(1, _NUM_TIME_PERIODS + 1):
            time_period = pad_time_period(i)
            avg_change_in_rank,num_big_changes_in_rank = \
                    calculate_changes(time_period, true_counts, percentage)
            stability = calculate_stability(time_period, true_counts,
                                            percentage)

            # Need to keep track of maximum y values for each set of data,
            # so we can appropriately scale the graphs.
            if avg_change_in_rank > max_avg_rank_change:
                max_avg_rank_change = avg_change_in_rank
            if num_big_changes_in_rank > max_num_big_rank_change:
                max_num_big_rank_change = num_big_changes_in_rank
            if stability > max_stability:
                max_stability = stability

            avg_rank_changes_for_percentage.append(avg_change_in_rank)
            num_big_rank_changes_for_percentage.append(num_big_changes_in_rank)
            stabilities_for_percentage.append(stability)

        avg_rank_changes.append(avg_rank_changes_for_percentage)
        big_rank_changes.append(num_big_rank_changes_for_percentage)
        stabilities.append(stabilities_for_percentage)

    draw_avg_change_graph(avg_rank_changes, max_avg_rank_change)
    draw_big_changes_graph(big_rank_changes,max_num_big_rank_change)
    draw_stability_graph(stabilities, max_stability)


if __name__ == "__main__":
    run()