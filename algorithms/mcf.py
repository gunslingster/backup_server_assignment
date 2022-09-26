import sys
sys.path.append('../')

import networkx as nx
import math
import copy
from utils.helper_functions import * 


def residualNetwork(G, path):
    '''
    Helper function that takes a networkx graph and path as input and produces a
    residual graph.

    :param G: Networkx digraph
    :param path: A list which represents a path of nodes
    :returns R: The residual network
    '''
    R = G.copy()
    for i in range(len(path)-1):
        node1 = path[i]
        node2 = path[i+1]
        R[node1][node2]['capacity'] -= 1
        weight = G[node1][node2]['weight']
        if R[node1][node2]['capacity'] <= 0:
            R.remove_edge(node1, node2)
            R.add_edge(node2, node1, weight=-weight, capacity=1)
        else:
            R.add_edge(node2, node1, weight=-weight, capacity=1)
    return R

def succShortestPaths(G, m, n):
    '''
    Successive shortest paths algorithm. This runs on successive residual networks.

    :param G: Networkx digraph
    :param m: Number of vnf
    :param n: number of backup servers
    :returns shortest_paths: A list of the successive shortest paths
    '''
    R = G.copy()
    shortest_paths = []
    for num_iters in range(m):
        # Can use dijkstra
        shortest_path = nx.bellman_ford_path(R, 0, m+n+1)
        shortest_paths.append(shortest_path)
        R = residualNetwork(R, shortest_path)
    return shortest_paths

def findAssignment(paths, m):
    '''
    Takes the list of shortest paths and analyzes it to find the optimal backup
    server assignment.

    :param paths: List of the successive shortest paths
    :returns assignment: The vnf->backup server assignment
    '''
    assignment = []
    for path in paths:
        for i in range(1, len(path)-2):
            if ([path[i+1], path[i]] in assignment):
                assignment.remove([path[i+1], path[i]])
            else:
                assignment.append([path[i], path[i+1]])

    # We add this step because in our networkx graph the vnf are nodes [1, m], 
    # and the servers are nodes [m+1, m+n]. In our original bipartite graph,
    # both the vnf and servers started at node 0. So you can have an assignement 
    # of [0,0] for instance. So we just subtract the appropriate constant from
    # node index.
    for pair in assignment:
        pair[0] -= 1
        pair[1] -= (m+1)
    return assignment

def calcSfcAvailability(G, assignment):
    '''
    This will calculate the SFC availability. It takes our original bipartite 
    graph, and the server assignment, and calculate the availability. Because
    both our VNF nodes and server nodes start at index 0 in our bipartite graph,
    it is a little confusing. We have to do some manipulation with the indicies.
    '''
    vnfs = G['vnfs']
    servers = G['servers']
    m = len(vnfs.items())
    n = len(servers.items())
    availability = 1

    for pair in assignment:
        # Now we just calculate availability
        vnf = pair[0]
        server = pair[1]
        availability *= (1 - vnfs[vnf]['failure_prob'] * servers[server]['failure_prob'])
    return availability

def mcf(G):
    '''
    We implement our own version of mcf, minimum cost flow. Python networkx also
    has their own implementation of mcf, which we can compare to for correctness.
    We take as input our bipartite graph G, and add a source and sink node. We 
    then run the successive shortest paths algorithm on the successive residual
    graphs in order to find the optimal backup server assignment. 

    :param G: This represents a complete bipartite graph between the VNF and
              backup server nodes. It is a list of two dictionaries. 
    :returns: A dictionary with two key-value pairs. The first being a mapping,
              which pairs the vnf nodes with backup server nodes. The second being the SFC
              availability, which is one minus the failure probability of the SFC.
    '''

    m = len(G['vnfs'].items())    # number of VNFs
    n = len(G['servers'].items()) # number of servers
    r = G['servers'][0]['r']      # resource capacity
    G_ = copy.deepcopy(G)
    vnfs = G_['vnfs']
    servers = G_['servers']

    D = convert_to_flow_network(G_)
    shortest_paths = succShortestPaths(D, m, n)
    assignment = findAssignment(shortest_paths, m)
    availability = calcSfcAvailability(G_, assignment)
    return {'mapping': assignment, 'availability': availability}

def mcf2(G):
    G_ = copy.deepcopy(G)
    m = len(G['vnfs'].items())
    D = convert_to_flow_network(G_)
    flow_dict = nx.min_cost_flow(D)
    assignment = convert_flow_dict_to_assignment(flow_dict, m)
    availability = calcSfcAvailability(G_, assignment)
    return {'mapping': assignment, 'availability': availability}
    
