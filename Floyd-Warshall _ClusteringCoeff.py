import json
import networkx as nx

with open('dpc-covid19-ita-province.json') as f:
    provinces = json.load(f)

# Provinces graph
P = nx.Graph()
# filter reference date
reference_date = provinces[0]['data']
all_provinces = [provinces[0]]

# filtering provinces using date and 'denominazione_provincia'
for province in (y for y in provinces[1:] if y['denominazione_provincia'] != 'In fase di definizione/aggiornamento'):
    if province['data'] == reference_date:
        all_provinces.append(province)
    else:
        break

print(all_provinces)
