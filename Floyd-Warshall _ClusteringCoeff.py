import json
import networkx as nx
import random
import pylab as plt
import math
from bisect import bisect_left
import time

# CONSTANTS
D1 = 0.8
D2 = 0.08
R_NUM_NODES = 2000
INF = 9999
X_INF, X_SUP = 30, 51
Y_INF, Y_SUP = 10, 19
GRAPH_DIMS = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]


# Euclidean distance in order to calculate distances between cities
def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))


# binary search core
def find_closest_value(ordered_list, target, d):
    pos = bisect_left(ordered_list, target)
    if pos == 0:
        return 0
    if pos == len(ordered_list):
        return ordered_list.index(ordered_list[-1])
    before = ordered_list[pos - 1]
    after = ordered_list[pos]
    if after - target < target - before and after < target - d:
        return ordered_list.index(after)
    else:
        return ordered_list.index(before)


def retrieve_data_dict_to_list(dictionary, geo):
    coords_1d, dict_list = [], []
    for key, value in dictionary.items():
        temp = [key, value]
        coords_1d.append(temp[1][geo])
        dict_list.append([temp[0], temp[1]['city']])
    return dict_list, coords_1d


# dictionary is the sorted points list
# d is used to define search criteria
def binary_search(dictionary_list, d, sorted_1d_coord):
    all_near_cities = []
    for i in range(len(sorted_1d_coord)):
        near_cities = []
        index_inf, index_sup = \
            find_closest_value(sorted_1d_coord, sorted_1d_coord[i] - d, d), \
            find_closest_value(sorted_1d_coord, sorted_1d_coord[i] + d, d) + 1
        near_cities.append(dictionary_list[i][0])
        near_cities.append(dictionary_list[i][1])
        near_cities.append([item[0] for item in dictionary_list[index_inf: index_sup]])
        all_near_cities.append(near_cities)

    return all_near_cities


# Construct provinces graph from a json provinces file
def construct_provinces_graph(provinces):
    # Provinces graph
    graph = nx.Graph()
    # filter reference date
    reference_date = provinces[0]['data']
    # filtering provinces using date and 'denominazione_provincia'
    province_id = 0
    for province in (y for y in provinces if y['denominazione_provincia'] != 'In fase di definizione/aggiornamento'):
        if province['data'] == reference_date:
            graph.add_node(province_id, city=province['denominazione_provincia'], long=province['long'],
                           lat=province['lat'])
            province_id += 1
        else:
            break
    return graph


# Construct a random  graph of "nodes_num" nodes add edges if edge criteria is satisfied
def construct_random_graph(nodes_num, x_inf, x_sup, y_inf, y_sup):
    graph = nx.Graph()
    for node_id in range(nodes_num):
        graph.add_node(node_id, city='', long=random.uniform(x_inf, x_sup), lat=random.uniform(y_inf, y_sup))
    return graph


# add edges if edge near criteria is satisfied O(n^2)
def set_provinces_edges_expensive(graph, threshold):
    start_expensive = time.time()
    for a in graph.nodes(data=True):
        for b in graph.nodes(data=True):
            if (a[1]['long'] - threshold < b[1]['long'] < a[1]['long'] + threshold) \
                    and (a[1]['lat'] - threshold < b[1]['lat'] < a[1]['lat'] + threshold):
                graph.add_edge(a[0], b[0], a=a[1]['city'], b=b[1]['city'],
                               weight=euclidean_distance(a[1]['long'], a[1]['lat'], b[1]['long'], b[1]['lat']))
                # print('Città: ' + a[1]['city'] + ' longitudine: ', a[1]['long'], 'latitudine: ', a[1]['lat'],
                #       'Città: ' + b[1]['city'] + ' longitudine: ', b[1]['long'], 'latitudine: ', b[1]['lat'])
    print('"Expensive method" provinces graph:', time.time() - start_expensive)
    return graph


def set_provinces_edges_binary_search(graph, threshold):
    graph_dict = dict(graph.nodes)

    # sort dict by long (cities) and lat (y)
    sorted_x = {k: v for k, v in sorted(graph_dict.items(), key=lambda item: item[1]['long'])}
    sorted_y = {k: v for k, v in sorted(graph_dict.items(), key=lambda item: item[1]['lat'])}

    # get data from dict in list nodes representation to search near cities to one given
    # and generate cities x and y separated coords lists in order to compute binary search
    dict_list_x, bisect_x = retrieve_data_dict_to_list(sorted_x, 'long')
    dict_list_y, bisect_y = retrieve_data_dict_to_list(sorted_y, 'lat')

    # binary search: it returns near cities' codes grouped by id
    start_binary = time.time()
    closest_x = binary_search(dict_list_x, threshold, bisect_x)
    closest_y = binary_search(dict_list_y, threshold, bisect_y)
    closest_x.sort(key=lambda x_long: x_long[0])
    closest_y.sort(key=lambda y_lat: y_lat[0])

    # compute intersections and add edges to graph
    for i in range(len(graph_dict)):
        cities_cluster = [closest_x[i][0], closest_x[i][1],
                          list(set(closest_x[i][2]).intersection(closest_y[i][2]))]
        if cities_cluster[2]:
            for j in range(len(cities_cluster[2])):
                graph.add_edge(cities_cluster[0], cities_cluster[2][j], a=cities_cluster[1],
                               b=graph_dict[cities_cluster[2][j]]['city'],
                               weight=euclidean_distance(graph_dict[i]['long'], graph_dict[i]['lat'],
                                                         graph_dict[cities_cluster[2][j]]['long'],
                                                         graph_dict[cities_cluster[2][j]]['lat']))
    print('"Binary search method":', time.time() - start_binary, '\n')


# Floyd-Warshall Algorithm
def floyd_warshall(graph):
    # nodes number
    n = graph.number_of_nodes()
    # Init a full n*n csc_matrix (from scipy)
    sparse_adj = nx.adjacency_matrix(graph, nodelist=None, weight='weight')
    # Get a full representation of adjacency matrix and set to INF the distance between not linked cities
    adj_matrix = sparse_adj.toarray()
    for i in range(n):
        for j in range(n):
            if i != j and adj_matrix[i][j] == 0:
                adj_matrix[i][j] = INF
    # Core algorithm
    for k in range(n):
        for i in range(n):
            for j in range(n):
                adj_matrix[i][j] = min(adj_matrix[i][j], adj_matrix[i][k] + adj_matrix[k][j])
    print(adj_matrix)
    return adj_matrix


# Global and local clustering coefficients
def clustering_coefficient(graph):
    local_clustering_coefficients_for_nodes = {}
    avg = 0
    for node in graph.nodes()(data=True):
        neighbours = [n for n in nx.neighbors(graph, node[0])]
        n_neighbors = len(neighbours)
        n_links = 0
        if n_neighbors > 1:
            for node1 in neighbours:
                for node2 in neighbours:
                    if graph.has_edge(node1, node2):
                        n_links += 1
            n_links /= 2  # because n_links is calculated twice
            c = n_links / (0.5 * n_neighbors * (n_neighbors - 1))
            avg += c
            local_clustering_coefficients_for_nodes[node[1]['city']] = c
            # print(c)
        else:
            local_clustering_coefficients_for_nodes[node[1]['city']] = 0
            # print(0)
    print("My clustering coefficients for each node: ", local_clustering_coefficients_for_nodes)
    print("My clustering coefficient (average): ", avg / graph.number_of_nodes())


def main():
    # Open JSON file with provinces
    with open('dpc-covid19-ita-province.json') as f:
        json_provinces = json.load(f)
    # Create graphs for experiments
    print('Construct provinces and random graphs... \n')
    # P and R are used for expensive edges adding
    P = construct_provinces_graph(json_provinces)
    R = construct_random_graph(R_NUM_NODES, X_INF, X_SUP, Y_INF, Y_SUP)
    # P1, R1 is for binary edges adding
    P1 = nx.create_empty_copy(P, with_data=True)
    R1 = nx.create_empty_copy(R, with_data=True)
    print('Add edges with expensive and binary methods to provinces graphs...')
    set_provinces_edges_expensive(P, D1)
    set_provinces_edges_binary_search(P1, D1)
    print('Add edges with expensive and binary methods to random graphs...')
    set_provinces_edges_expensive(R, D2)
    set_provinces_edges_binary_search(R1, D2)

    # Draw graphs
    # nx.draw(P)
    # plt.show()
    # to draw graph. TODO:use graphviz

    # nx clustering results (for comparision purposes)
    print("Clustering coefficient nx (for each node): ", nx.clustering(P))
    print("Clustering coefficient nx (average): ", nx.average_clustering(P))
    print("Calculate local and global clustering coefficients...")
    clustering_coefficient(P)
    clustering_coefficient(R)

    print("Run Floyd-Warshall algorithm on provinces graph...")
    shortest_graph_paths = floyd_warshall(P)
    print('Shortest paths between provinces', shortest_graph_paths, '\n')
    print('Run Floyd-Warshall algorithm increasing progressively the graph dimension...')
    for i in range(len(GRAPH_DIMS)):
        graph = construct_random_graph(GRAPH_DIMS[i], 0, 10, 0, 10)
        set_provinces_edges_binary_search(graph, D1)
        start = time.time()
        floyd_warshall(graph)
        print('Floyd-Warshall algorithm with graph dim:', GRAPH_DIMS[i], '--->', time.time() - start, '\n')


if __name__ == "__main__":
    main()
