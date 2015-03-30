from __future__ import division
import json
import networkx as nx
from coopr.pyomo import ConcreteModel, Objective, Constraint, Var
from coopr.pyomo import Binary, NonNegativeIntegers
from coopr.pyomo import summation

data = json.load(open('data.json'))
G = nx.DiGraph()
for node in data['nodes']:
    G.add_node(node['index'])
for link in data['links']:
    G.add_edge(link['source'], link['target'], weight=-1)

dist = {}
for node in nx.topological_sort(G):
    pairs = [(dist[v][0]+1, v) for v in G.pred[node]]
    if pairs:
        dist[node] = max(pairs)
    else:
        dist[node] = (0, node)
_, (maxLayer, _) = max(dist.items(), key=lambda x: x[1])
L = list(range(1, maxLayer + 1))

model = ConcreteModel('layout')
model.y = Var([node['index'] for node in data['nodes']],
              domain=NonNegativeIntegers)
for node in data['nodes']:
    yi = 'y{}'.format(node['index'])
    if G.in_degree(node['index']) == 0:
        setattr(model, yi, Constraint(expr=model.y[node['index']] == 0))
    elif G.out_degree(node['index']) == 0:
        setattr(model, yi, Constraint(expr=model.y[node['index']] == maxLayer))
for i, link in enumerate(data['links']):
    xi = 'x{}'.format(i)
    edgei = 'edge{}'.format(i)
    mci = 'mc{}'.format(i)
    u = link['source']
    v = link['target']
    setattr(model, xi, Var(L, domain=Binary))
    setattr(model, edgei,
            Constraint(expr=sum(k * getattr(model, xi)[k] for k in L)
                       - model.y[v] + model.y[u] == 0))
    setattr(model, mci, Constraint(expr=summation(getattr(model, xi)) == 1))

model.OBJ = Objective(expr=sum(sum(k * k * getattr(model, 'x{}'.format(i))[k]
                                   for k in L)
                               for i in range(len(data['links']))))
