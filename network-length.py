import datetime
import os
from scipy.stats import lognorm
import math
import networkx as nx
import random
import csv

# 平均ノード間距離を求める

###########################################
# 設定
# ここでノード数を決める
node_min = 100
node_max = 1000
node_diff = 100
saved_file = f'node-distance_{node_min}-{node_max}.csv'
###########################################

# images-for-readme.ipynb で最尤推定した値
mode_set = 98.4  # LogNorm分布の最頻値
mu_set = 5.60  # LogNorm分布の形を定めるparameter


def make_samples(node, mode, mu, loc=0, upper=1000, size_extra=2):
    # upper：samplingで作られる値の上限。cutoff
    # size_extra : cutoffによりsampling数が足らなくなるように調整。
    scale = math.exp(mu)
    sigma = math.sqrt(math.log(scale) - math.log(mode)) 

    _samples = lognorm.rvs(s=sigma, loc=loc, scale=math.exp(mu), size=size_extra*node)
    _samples = [round(i) for i in _samples if i <= upper]

    _sum = 1
    while _sum % 2 != 0:
        samples = random.sample(_samples, node)
        _sum = sum(samples)
    
    return samples

def network(samples):
    Graph = nx.configuration_model(list(samples))
    Graph = nx.Graph(Graph)  # remove parallel edges
    Graph.remove_edges_from(nx.selfloop_edges(Graph))
    return Graph

def path_length(Graph):
    result = {}
    mean_distance = 0
    max_nodes = 0
    max_node_dis = 0
    print(f'{datetime.datetime.now()} calculate connect_num')
    result['connect_num'] = nx.number_connected_components(Graph)  # connected graph の数
    component_num = 0
    print(f'{datetime.datetime.now()} calculate connected_components')
    for Component_g in (Graph.subgraph(_c).copy() for _c in nx.connected_components(Graph)):
        component_num += 1
        _nodes = Component_g.number_of_nodes()
        print(f'{datetime.datetime.now()} calculate average')
        _distance = nx.average_shortest_path_length(Component_g)
        mean_distance += _nodes * _distance
        if _nodes > max_nodes:
            max_nodes = _nodes
            max_node_dis = _distance
    result['length_av'] = mean_distance / Graph.number_of_nodes()  # Graph全体の平均距離
    result['max_component_node'] = max_nodes
    result['max_component_length'] = max_node_dis
    return result


def main():
    if not os.path.isfile(saved_file):
        with open(saved_file, mode='w') as f:
            writer = csv.writer(f)
            writer.writerow(['node_num', 'connect_num', 'average_path_length', 'node_num_of_max_component', 'average_path_length_of_max_component'])

    for node in range(node_min, node_max + node_diff, node_diff):
        print('')
        print(f'{datetime.datetime.now()}')
        print(f'{datetime.datetime.now()} node : {node} ')
        samples = make_samples(node, mode_set, mu_set)
        print(f'{datetime.datetime.now()} make graph ')
        Graph = network(samples)
        print(f'{datetime.datetime.now()} calculate length')
        length_data = path_length(Graph)
        result_list = [node, length_data['connect_num'], length_data['length_av'], length_data['max_component_node'], length_data['max_component_length']]
        Graph.clear()

        with open(saved_file, "a", newline="") as f:
            writer_object = csv.writer(f)
            writer_object.writerow(result_list)
            f.close()

if __name__ == "__main__":
    main()
