import json
import networkx as nx

D1 = 0.8
D2 = 0.08

with open('dpc-covid19-ita-province.json') as f:
    json_provinces = json.load(f)


def construct_graph(provinces, threshold):
    # Provinces graph
    P = nx.Graph()
    # filter reference date
    reference_date = provinces[0]['data']
    # filtering provinces using date and 'denominazione_provincia'
    province_id = 0
    for province in (y for y in provinces if y['denominazione_provincia'] != 'In fase di definizione/aggiornamento'):
        if province['data'] == reference_date:
            P.add_node(province_id, city=province['denominazione_provincia'], long=province['long'],
                       lat=province['lat'])
            province_id += 1
        else:
            break
    for a in P.nodes(data=True):
        for b in (n for n in P.nodes(data=True) if n != a):
            if (a[1]['long'] - threshold < b[1]['long'] < a[1]['long'] + threshold) \
                    and (a[1]['lat'] - threshold < b[1]['lat'] < a[1]['lat'] + threshold):
                P.add_edge(a[0], b[0])
                print('EDGE')
                print('Città: ' + a[1]['city'] + ' longitudine: ', a[1]['long'], 'latitudine: ', a[1]['lat'],
                      'Città: ' + b[1]['city'] + ' longitudine: ', b[1]['long'], 'latitudine: ', b[1]['lat'])
                print()
    print('finished')


construct_graph(json_provinces, D1)