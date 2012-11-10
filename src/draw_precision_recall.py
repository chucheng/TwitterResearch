import Util
import matplotlib
matplotlib.use("Agg")

from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt

_GRAPH_DIR = Util.get_graph_output_dir('FolkWisdom/')


def draw_precision_only(newsaholic_precisions,
                        active_precisions, common_precisions,
                        expert_p_precisions, expert_f_precisions,
                        expert_c_precisions, expert_s_precisions,
                        run_params_str):
  """Draws the precision recall graph for all the user groups and a given delta.

  Plots the given list of precisions against the number of top news that the
  precision value was calculated for.
  """
  plots = []
  figure = plt.figure()
  axs = figure.add_subplot(111)

  # Groups
  newsaholic_plot = axs.plot(newsaholic_precisions, '--', linewidth=2)
  plots.append(newsaholic_plot)
  active_plot = axs.plot(active_precisions, ':', linewidth=2)
  plots.append(active_plot)
  common_plot = axs.plot(common_precisions, '-.', linewidth=2)
  plots.append(common_plot)

  # Experts
  expert_p_plot = axs.plot(expert_p_precisions, '--', linewidth=2)
  plots.append(expert_p_plot)
  expert_f_plot = axs.plot(expert_f_precisions, '-.', linewidth=2)
  plots.append(expert_f_plot)
  expert_c_plot = axs.plot(expert_c_precisions, ':', linewidth=2)
  plots.append(expert_c_plot)
  expert_s_plot = axs.plot(expert_s_precisions, ':', linewidth=2)
  plots.append(expert_s_plot)

  labels = ['News-addicted', 'Active Users', 'Common Users',
            'Experts (Precision)', 'Experts (F-score)', 'Experts (CI)',
            'Super Experts']
  plt.legend(plots, labels, loc=0, ncol=2, columnspacing=0, handletextpad=0)

  plt.grid(True, which='major', linewidth=1)

  axs.yaxis.set_minor_locator(MultipleLocator(5))
  plt.grid(True, which='minor')

  plt.xlabel('Recall (%)')
  plt.ylabel('Num Top News Picked')

  with open(_GRAPH_DIR + run_params_str + '/precision_all_%s.png'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='png')
  with open(_GRAPH_DIR + run_params_str + '/precision_all_%s.eps'
            % run_params_str, 'w') as graph:
    plt.savefig(graph, format='eps')

  plt.close()


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
