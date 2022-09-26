import sys
from .mcf import mcf2
from utils.helper_functions import *
from utils.gen_nodes import *
import keras
from keras.models import Sequential
from keras.layers import Dense
import numpy as np
sys.path.append('../')

def gen_training_instance(G):
    '''
    A traning instance consists of a cost matrix, and an optimal assignment. We 
    Can use this to trian our DNN instances. We need to convert the assignment 
    into a set of one hot vectors. For instance, for job 1, the vector 
    [0,0,1] means it was assigned to server 2. 

    :param G: Bipartite graph
    :returns: Our training instance
    '''
    training_instance = []
    cost_matrix = bipartiteGraphToCostMatrix(G)
    cost_vector = cost_matrix.flatten()
    assignment = mcf2(G)['mapping']
    assignment.sort(key=lambda x: x[0])
    n = len(assignment)
    vectors = [np.zeros(n, dtype=np.int8) for i in range(n)]
    for a, vec in zip(assignment, vectors):
        vec[a[1]] = 1
    return (cost_vector, vectors)

def gen_training_data(m, n, r, vnf_fail_prob, server_fail_prob, num_rounds):
    '''
    Generate multiple training instances

    :param m: number vnf
    :param n: number servers
    :param r: capacity
    :param vnf_fail_prob: probability of vnf failure
    :param server_fail_prob: probability of failure
    :param num_rounds: number of training rounds
    '''
    training_graphs = [gen_graph(m, n, r, vnf_fail_prob, server_fail_prob) for _ in range(num_rounds)]
    training_data = [gen_training_instance(G) for G in training_graphs]
    return training_data

def gen_models(m, n, r, vnf_fail_prob, server_fail_prob, num_rounds):
    '''
    Generate the DNN models

    :param m: number vnf
    :param n: number servers
    :param r: capacity
    :param vnf_fail_prob: probability of vnf failure
    :param server_fail_prob: probability of failure
    :param num_rounds: number of training rounds
    '''

    training_data = gen_training_data(m, n, r, vnf_fail_prob, server_fail_prob, num_rounds)
    inputs = [x[0] for x in training_data]
    input_arr = np.array(inputs)
    print(input_arr.shape)
    for i in range(n):
        model = keras.Sequential()
        model.add(keras.layers.Input(shape=(n*n,)))
        model.add(keras.layers.Dense(32, activation='relu', name='hidden1'))
        model.add(keras.layers.Dense(64, activation='relu', name='hidden2'))
        model.add(keras.layers.Dense(256, activation='relu', name='hidden3'))
        model.add(keras.layers.Dense(n, activation='softmax', name='output'))
        model.build((m,n))
        opt = keras.optimizers.Adam(learning_rate=0.001)
        model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
        outputs = [x[1][i] for x in training_data] 
        output_arr = np.array(outputs)
        model.fit(x=input_arr, y=output_arr, batch_size=1024, epochs=1000, shuffle=True)
        model.save(f'../models/model{i}.h5')

def dnn_assignment(graphs):
    pass
