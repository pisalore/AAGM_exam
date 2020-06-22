import json

with open('dpc-covid19-ita-province.json') as f:
    data = json.load(f)

    print(data)
