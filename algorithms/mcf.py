import networkx as nx
import math

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
        shortest_path = nx.dijkstra_path(R, 0, m+n+1)
        shortest_paths.append(shortest_path)
        R = residualNetwork(R, shortest_path)
    return shortest_paths

def findAssignment(paths):
    '''
    Takes the list of shortest paths and analyzes it to find the optimal backup
    server assignment.

    :param paths: List of the successive shortest paths
    :returns assignment: The vnf->backup server assignment
    '''
    assignment = []
    for path in paths:
        for i in range(1, len(path)-2):
            if ((path[i+1], path[i]) in assignment):
                assignment.remove((path[i+1], path[i]))
            else:
                assignment.append((path[i], path[i+1]))
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
    assignment = [list(tup) for tup in assignment]

    # This produces the same assignment but with the original offsets in the 
    # bipartite graph
    # For instance, you could have (0,0) which means VNF 0 matches to server 0
    for tup in assignment:
        tup[0] -= 1
        tup[1] -= (m+1)
        # Now we just calculate availability
        vnf = tup[0]
        server = tup[1]
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
    vnfs = G['vnfs']
    servers = G['servers']

    def convert_to_flow_network(G):
        '''
        Convert the bipartite graph into a networkx digraph

        :param G: Bipartite graph
        :returns: A networkx digraph
        '''

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
    
    D = convert_to_flow_network(G)
    shortest_paths = succShortestPaths(D, m, n)
    assignment = findAssignment(shortest_paths)
    availability = calcSfcAvailability(G, assignment)
    return {'mapping': assignment, 'availability': availability}


