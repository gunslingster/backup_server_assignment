import sys
sys.path.append('../')
from algorithms.sga import sga
from utils.gen_nodes import *
from algorithms.cdnn import cdnn
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
    graphs = [gen_graph(n, m, r, vnf_fail_prob, server_fail_prob) for _ in range(num_sims)]
    results = {}
    for algo in algos:
        availabilities = [algo(G)['availability'] for G in graphs]
        avg = sum(availabilities) / len(availabilities)
        results[algo.__name__] = avg
    return results

def gen_plots():
    font = {'size'   : 6}
    matplotlib.rc('font', **font)
    labels = ['n=3']
    mcf_data = []
    dnn_data = []
    sim_data = sim(num_sims=100, m=3, n=3, r=1, vnf_fail_prob=(0, 0.1), server_fail_prob=(0, 0.2), algos=[mcf2, cdnn])
    mcf_data.append(sim_data['mcf2'])
    dnn_data.append(sim_data['cdnn'])
    mcf_data = [round(elem, 3) for elem in mcf_data]
    dnn_data = [round(elem, 3) for elem in dnn_data]
    x = np.arange(len(labels))
    width = 0.70
    fig, ax = plt.subplots()
    reacts1 = ax.bar(x- width/2, mcf_data ,width, label='MCF')
    reacts2 = ax.bar(x + width/2, dnn_data, width, label='DNN')
    ax.set_ylabel('Average Availability')
    ax.set_title('Availability of DNN vs. MCF')
    ax.set_xticks(x, labels)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.bar_label(reacts1, padding=3)
    ax.bar_label(reacts2, padding=3)
    fig.tight_layout()
    plt.savefig('/mnt/c/Users/t0pma/OneDrive/Desktop/csudh/thesis/test.png')

gen_plots()

