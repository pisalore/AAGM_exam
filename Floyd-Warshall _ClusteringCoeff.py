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


def cast_dict_to_list(dictionary):
    dict_list = []
    for key, value in dictionary.items():
        temp = [key, value]
        dict_list.append(temp)
    return dict_list


# ref_value is the point (city) we want to find near points
# dictionary is the sorted points list
# d is used to define search criteria
def binary_search(dictionary_list, d, sorted_1d_coord):
    all_near_cities = []
    for i in range(len(sorted_1d_coord)):
        near_cities = []
        index_inf, index_sup = find_closest_value(sorted_1d_coord, sorted_1d_coord[i] - d, d), \
                               find_closest_value(sorted_1d_coord, sorted_1d_coord[i] + d, d) + 1
        near_cities.append(dictionary_list[i][0])
        near_cities.append(dictionary_list[i][1]['city'])
        near_cities.append(dictionary_list[index_inf: index_sup])
        all_near_cities.append(near_cities)

    # O(n)
    # res_key_point_inf, res_val_point_inf = min(dictionary.items(), key=lambda x: abs(point_inf - x[1][axis]))
    # res_key_point_sup, res_val_point_sup = min(dictionary.items(), key=lambda x: abs( - x[1][axis]))
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
def construct_random_graph(nodes_num, x_inf, x_sup, y_inf, y_sup, threshold):
    graph = nx.Graph()
    for node_id in range(nodes_num):
        graph.add_node(node_id, city='', long=random.uniform(x_inf, x_sup), lat=random.uniform(y_inf, y_sup))
    return graph


# add edges if edge near criteria is satisfied
def set_provinces_edges_expensive(graph, threshold):
    for a in graph.nodes(data=True):
        for b in (n for n in graph.nodes(data=True)):
            if (a[1]['long'] - threshold < b[1]['long'] < a[1]['long'] + threshold) \
                    and (a[1]['lat'] - threshold < b[1]['lat'] < a[1]['lat'] + threshold):
                graph.add_edge(a[0], b[0], a=a[1]['city'], b=b[1]['city'],
                               weight=euclidean_distance(a[1]['long'], a[1]['lat'], b[1]['long'], b[1]['lat']))
                # print('Città: ' + a[1]['city'] + ' longitudine: ', a[1]['long'], 'latitudine: ', a[1]['lat'],
                #       'Città: ' + b[1]['city'] + ' longitudine: ', b[1]['long'], 'latitudine: ', b[1]['lat'])
    return graph


# add edges if edge near criteria is satisfied
def set_random_graph_edges_expensive(graph, threshold):
    index = 0
    for a in graph.nodes(data=True):
        index += 1
        for b in (n for n in graph.nodes(data=True) if (n[0] > index and n != a)):
            if (a[1]['x'] - threshold < b[1]['x'] < a[1]['x'] + threshold) \
                    and (a[1]['y'] - threshold < b[1]['y'] < a[1]['y'] + threshold):
                graph.add_edge(a[0], b[0], weight=euclidean_distance(a[1]['x'], a[1]['y'], b[1]['x'], b[1]['y']))
                print(' x: ', a[1]['x'], 'y: ', a[1]['y'], ' x: ', b[1]['x'], 'y: ', b[1]['y'])
    return graph


def set_provinces_edges_binary_search(graph, threshold):
    graph_dict = dict(graph.nodes)
    bisect_x, bisect_y, result = [], [], []

    # sort dict by long (city) and lat (y)
    sorted_x = {k: v for k, v in sorted(graph_dict.items(), key=lambda item: item[1]['long'])}
    sorted_y = {k: v for k, v in sorted(graph_dict.items(), key=lambda item: item[1]['lat'])}
    # get list nodes representation to search near cities to one given
    dict_list_x, dict_list_y = cast_dict_to_list(sorted_x), cast_dict_to_list(sorted_y)
    # generate city x and y separated coords list in order to compute binary search
    for i in range(len(graph_dict)):
        bisect_x.append(dict_list_x[i][1]['long'])
        bisect_y.append(dict_list_y[i][1]['lat'])

    start_time = time.time()
    closest_x = binary_search(dict_list_x, threshold, bisect_x)
    closest_y = binary_search(dict_list_y, threshold, bisect_y)
    print('binary:', time.time() - start_time)


    # sort result by province codes in order to compute intersection

    closest_x.sort(key=lambda x_long: x_long[0])
    closest_y.sort(key=lambda y_lat: y_lat[0])

    # compute intersections
    for i in range(len(graph_dict)):
        cities_cluster = [closest_x[i][0], closest_x[i][1], [city for city in closest_x[i][2] if city in closest_y[i][2]]]
        result.append(cities_cluster)
        if cities_cluster[2]:
            for city in cities_cluster[2]:
                graph.add_edge(cities_cluster[0], city[0], a=cities_cluster[1], b=city[1]['city'],
                               weight=euclidean_distance(graph_dict[i]['long'], graph_dict[i]['lat'],
                                                         city[1]['long'], city[1]['lat']))

    # results are ordered by province province_id
    print(result)


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
    print(adj_matrix)

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

    print('Construct provinces graph...')
    # P = construct_provinces_graph(json_provinces)
    # set_provinces_edges_expensive(P, D1)
    # set_provinces_edges_binary_search(P, D1)
    # set_provinces_edges_expensive(P, D1)

    # print('Construct random nodes graph with', R_NUM_NODES, 'nodes...')
    R = construct_random_graph(5000, 30, 51, 10, 19, 0.08)
    print('assign edges')
    start1 = time.time()
    set_provinces_edges_binary_search(R, D1)
    print('binary:', time.time() - start1)
    start = time.time()
    set_provinces_edges_expensive(R, D1)
    print('expensive:', time.time() - start)



    print("Run Floyd-Warshall algorithm...")
    #shortest_graph_paths = floyd_warshall(P)
    # floyd_warshall(R)
    # nx.draw(R)
    # plt.show()

    # nx clustering results (for comparision purposes)
    # print("Clustering coefficient nx (for each node): ", nx.clustering(P))
    # print("Clustering coefficient nx (average): ", nx.average_clustering(P))

    print("Calculate local and global clustering coefficients...")
    # clustering_coefficient(P)
    # clustering_coefficient(R)


if __name__ == "__main__":
    main()
# floyd_warshall(R)
# to draw graph. TODO:use graphviz

