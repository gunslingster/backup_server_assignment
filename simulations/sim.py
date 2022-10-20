import sys
sys.path.append('../')
from utils.gen_nodes import *
from algorithms.cdnn import cdnn
from algorithms.sga import sga
from algorithms.rsga import rsga
from algorithms.mcf import mcf,mcf2
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

def sim(**kwargs):
    num_sims = kwargs['num_sims']
    n = kwargs['n']
    m = kwargs['m']
    r = kwargs['r']
    algos = kwargs['algos']
    vnf_fail_prob = kwargs['vnf_fail_prob']
    server_fail_prob = kwargs['server_fail_prob']
    graphs = [gen_graph(m, n, r, vnf_fail_prob, server_fail_prob) for _ in range(num_sims)]
    results = {}
    for algo in algos:
        availabilities = [algo(G)['availability'] for G in graphs]
        avg = sum(availabilities) / len(availabilities)
        results[algo.__name__] = avg
    return results

def gen_plots(m_vals, m_step, n, r, vnf_fail_prob, server_fail_prob, width, algos, title):
    font = {'size'   : 6}
    matplotlib.rc('font', **font)
    labels = [f'm={m}' for m in m_vals]
    algo_names = [algo.__name__ for algo in algos]
    num_algos = len(algos)
    data = []
    for i in range(m_vals[0], m_vals[-1]+1, m_step):
        sim_data = sim(num_sims=1000, m=i, n=n, r=r, vnf_fail_prob=vnf_fail_prob, server_fail_prob=server_fail_prob, algos=algos)
        for algo_name in algo_names:
            data.append(round(sim_data[algo_name], 3))
    x = np.arange(len(labels))
    fig, ax = plt.subplots()
    rects = []
    offset  = 1
    for label, dat in zip(algo_names, data):
        rects.append(ax.bar(x - offset*width/2, dat ,width, label=label.upper()))
        offset *= -1
    ax.set_ylabel('Average Availability')
    ax.set_title(title)
    ax.set_xticks(x, labels)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    for rect in rects:
        ax.bar_label(rect, padding=3)
    fig.tight_layout()
    plt.savefig('/mnt/c/Users/t0pma/OneDrive/Desktop/csudh/thesis/test.png')

gen_plots([4, 8, 12], 4, 24, 3, (0, 0.1), (0, 0.2), 0.4, [mcf2, cdnn], 'Availability of MCF vs CDNN')

