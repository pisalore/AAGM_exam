import json
import networkx as nx
import random

D1 = 0.8
D2 = 0.08
R_NUM_NODES = 2000

with open('dpc-covid19-ita-province.json') as f:
    json_provinces = json.load(f)


def construct_graph(provinces, threshold):
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
    index = 0
    for a in graph.nodes(data=True):
        index += 1
        for b in (n for n in graph.nodes(data=True) if (n[0] > index and n != a)):
            if (a[1]['long'] - threshold < b[1]['long'] < a[1]['long'] + threshold) \
                    and (a[1]['lat'] - threshold < b[1]['lat'] < a[1]['lat'] + threshold):
                graph.add_edge(a[0], b[0], a=a[1]['city'], b=b[1]['city'])
                print('Città: ' + a[1]['city'] + ' longitudine: ', a[1]['long'], 'latitudine: ', a[1]['lat'],
                      'Città: ' + b[1]['city'] + ' longitudine: ', b[1]['long'], 'latitudine: ', b[1]['lat'])
    return graph


def construct_random_graph(nodes_num, x_inf, x_sup, y_inf, y_sup, threshold):
    graph = nx.Graph()
    for node_id in range(nodes_num):
        graph.add_node(node_id, x=random.uniform(x_inf, x_sup), y=random.uniform(y_inf, y_sup))
    index = 0
    for a in graph.nodes(data=True):
        index += 1
        for b in (n for n in graph.nodes(data=True) if (n[0] > index and n != a)):
            if (a[1]['x'] - threshold < b[1]['x'] < a[1]['x'] + threshold) \
                    and (a[1]['y'] - threshold < b[1]['y'] < a[1]['y'] + threshold):
                graph.add_edge(a[0], b[0])
                print(' x: ', a[1]['x'], 'y: ', a[1]['y'],
                      ' x: ', b[1]['x'], 'y: ', b[1]['y'])
    return graph


print('P')
P = construct_graph(json_provinces, D1)
print('R')
R = construct_random_graph(R_NUM_NODES, 30, 51, 10, 19, 0.08)
