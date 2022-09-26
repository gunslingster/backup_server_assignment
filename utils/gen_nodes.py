import random

def gen_vnfs(m, failure_prob_range):
    '''
    This function generates a dictionary of VNF nodes. Each node simply consists
    of a key which is the node index, which has as its value another dictionary.
    This dictionary in general can hold several attributes. In the case for VNF,
    the only attribute it has is a failure probability.
    
    :param m: The number of VNF nodes
    :param failure_prob_range: A list which represents the failure probability range
    :returns: Returns a dictionary of nodes with string attributes. 
    '''
    
    vnfs = {}
    for i in range(m):
        lower_failure_bound = failure_prob_range[0]
        upper_failure_bound = failure_prob_range[1]
        vnfs[i] = {"failure_prob": random.uniform(lower_failure_bound, upper_failure_bound)}
    return vnfs

def gen_servers(n, failure_prob_range, r):
    '''
    This function generates a dictionary of server nodes. Each node simply consists
    of a key which is the node index, which has as its value another dictionary.
    This dictionary in general can hold several attributes. In the case for server,
    it will have two attributes. A failure probability, and a resource capacity.
    
    :param n: The number of server nodes
    :param failure_prob_range: A list which represents the failure probability range
    :param r: resource capacity, number of VNF the server can backup
    :returns: Returns a dictionary of nodes with string attributes. 
    '''
    servers = {}
    for i in range(n):
        lower_failure_bound = failure_prob_range[0]
        upper_failure_bound = failure_prob_range[1]
        servers[i] = {'failure_prob': random.uniform(lower_failure_bound, upper_failure_bound)}
        servers[i]['r'] = r
    return servers

def gen_graph(n, m, r, vnf_fail_prob, server_fail_prob):
    '''
    This will return a dictionary with represents a bipartite graph. The two sets
    of nodes in the graph are the VNFs and servers.

    :param m: number of VNF
    :param m: number of servers
    :param r: resource capacity
    :param vnf_fail_prob: VNF failure probability range
    :param server_fail_prob: Server failure probability range
    :returns: Bipartite graph represented as a dictionary
    '''
    vnfs = gen_vnfs(m, vnf_fail_prob)
    servers = gen_servers(n, server_fail_prob, r)
    graph = {'vnfs': vnfs, 'servers': servers}
    return graph
