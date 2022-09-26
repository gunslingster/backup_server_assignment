import networkx as nx
import math
import numpy as np

def bipartiteGraphToCostMatrix(G):
    '''
    Convert a complete bipartite graph in dictionary format into a numpy
    cost matrix. For now this assumes r=1
    '''
    vnfs = G['vnfs']
    servers = G['servers']
    m = len(vnfs)
    n = len(servers)
    cost_matrix = np.zeros((m,n))
    for i, vnf in vnfs.items():
        for j, server in servers.items():
            cost_matrix[i,j] = math.log(1/(1 - vnf['failure_prob'] * server['failure_prob']))
    return cost_matrix

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

def convert_flow_dict_to_assignment(flow_dict, m):
    '''
    Convert a networkx flow dict to our standard representation of assignment.

    :param flow_dict: A networkx flow dict
    :param m: The number of VNF
    :return assignment: A list of 2 element arrays that indicates VNF assignment
    '''

    assignment = []
    for i in range(1, m+1):
        mapping = list(flow_dict.items())[i]
        node1 = mapping[0]
        edge_dict = mapping[1]
        for edge in edge_dict.items():
            if edge[1] > 0:
                assignment.append([node1 - 1, edge[0] - (m+1)])
    return assignment

def convert_to_flow_network(G):
    '''
    Convert the bipartite graph into a networkx digraph

    :param G: Bipartite graph
    :returns: A networkx digraph
    '''

    # Extract the necessary parameters
    m = len(G['vnfs'].items())    # number of VNFs
    n = len(G['servers'].items()) # number of servers
    r = G['servers'][0]['r']      # resource capacity
    vnfs = G['vnfs']
    servers = G['servers']

    # First we populate the graph with nodes
    D = nx.DiGraph()
    num_nodes = m + n + 2     # Add 2 for source and sink
    D.add_node(0, layer='source', demand=-m)    # Add source node
    for i in range(m):                          # Add vnf nodes
        D.add_node(1+i, layer='vnf')
    for i in range(n):                          # Add server nodes
        D.add_node(1+m+i, layer='server')
    D.add_node(1+m+n, layer='sink', demand=m)   # Add sink node

    # Now we populate the graph with edges
    # First add edges from source to VNF nodes
    for node in range(1, m+1):
        D.add_edge(0, node, weight=0, capacity=1)
    # Now add edges from each VNF to each server
    for i in range(1, m+1):
        p1 = vnfs[i-1]['failure_prob']
        for j in range(m+1, m+n+1):
            p2 = servers[j-m-1]['failure_prob']
            w = int(math.log(1 / (1-p1*p2)) * 10e10)
            D.add_edge(i, j, weight=w, capacity=1)
    # Now add edges from each server to the sink
    for i in range(m+1, m+n+1):
        D.add_edge(i, m+n+1, weight=0, capacity=r)
    return D
