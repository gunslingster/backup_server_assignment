import copy

def rsga(G):
    '''
    Sorted greedy algorithm. This is a simple greedy algorithm that sorts
    both the VNFs and Backup servers by failure probability and then assigns 
    them in that order. The algorithm will account for r > 1.

    :param G: This represents a complete bipartite graph between the VNF and
              backup server nodes. It is a list of two dictionaries. 
    :returns: A dictionary with two key-value pairs. The first being a mapping,
              which pairs the vnf nodes with backup server nodes. The second being the SFC
              availability, which is one minus the failure probability of the SFC.
    '''
    
    result = {'mapping': [], 'availability': 1}
    G_ = copy.deepcopy(G)
    vnfs = G_['vnfs']
    servers = G_['servers']

    # Sort VNFs and servers by their failure probability
    sorted_vnfs = sorted(vnfs.items(), key=lambda kv: kv[1]['failure_prob'])
    sorted_servers = sorted(servers.items(), key=lambda kv: kv[1]['failure_prob'])

    # Iterate though the VNFs and match with the highest available server
    for vnf in sorted_vnfs:
        for server in sorted_servers:
            if server[1]['r'] > 0:
                result['mapping'].append([vnf[0], server[0]])
                result['availability'] *= (1 - vnf[1]['failure_prob'] * server[1]['failure_prob'])
                server[1]['r'] -= 1
                break
    return result
