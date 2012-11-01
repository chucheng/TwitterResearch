import Util
import matplotlib
matplotlib.use("Agg")

from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt

_GRAPH_DIR = Util.get_graph_output_dir('FolkWisdom/')


def draw(precisions_list, recalls_list, labels, file_prefix, run_params_str):
  plots = []
  figure = plt.figure()
  axs = figure.add_subplot(111)

  max_x = 0
  for (precisions, recalls) in zip(precisions_list, recalls_list):
    plot = axs.plot(recalls, precisions, '--', linewidth=2)
    plots.append(plot)
    max_recall = max(recalls)
    if max_recall > max_x:
      max_x = max_recall

  plt.legend(plots, labels, loc=0, ncol=2, columnspacing=0, handletextpad=0)
  plt.axis([0, max_x + 5, 0, 105])
  plt.grid(True, which='major', linewidth=1)

  axs.xaxis.set_minor_locator(MultipleLocator(5))
  axs.yaxis.set_minor_locator(MultipleLocator(5))
  plt.grid(True, which='minor')

  plt.xlabel('Recall (%)')
  plt.ylabel('Precision (%)')

  with open(_GRAPH_DIR + run_params_str + '/%s_%s.png'
            % (file_prefix, run_params_str), 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + run_params_str + '/%s_%s.eps'
            % (file_prefix, run_params_str), 'w') as graph:
    plt.savefig(graph, format='eps')

  plt.close()
