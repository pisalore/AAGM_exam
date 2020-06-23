import json
import networkx as nx

D1 = 0.8
D2 = 0.08

with open('dpc-covid19-ita-province.json') as f:
    provinces = json.load(f)

# Provinces graph
P = nx.Graph()
# filter reference date
reference_date = provinces[0]['data']

# filtering provinces using date and 'denominazione_provincia'
i = 0
for province in (y for y in provinces if y['denominazione_provincia'] != 'In fase di definizione/aggiornamento'):
    if province['data'] == reference_date:
        P.add_node(i, city=province['denominazione_provincia'], long=province['long'], lat=province['lat'])
        i += 1
    else:
        break
for a in P.nodes(data=True):
    for b in (n for n in P.nodes(data=True) if n != a):
        if (a[1]['long'] - D1 < b[1]['long'] < a[1]['long'] + D1)\
                and (a[1]['lat'] - D1 < b[1]['lat'] < a[1]['lat'] + D1):
            print('edge', 'a: ', a[1]['city'], 'b: ', b[1]['city'])

