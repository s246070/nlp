from rdflib import Graph, Namespace, Literal
from rdflib.namespace import XSD

g = Graph()
g.parse("project/data/stock_knowledge_graph.ttl", format="turtle")

EX = Namespace("https://example.org/stocks/")

# Add a new closing-price observation
observation = EX["vws-2026-11-06"]

g.add((EX["vws-co"], EX.hasObservation, observation))
g.add((observation, EX.closePrice,
       Literal(205.50, datatype=XSD.decimal)))

# Save the graph
g.serialize(
    destination="project/data/stock_knowledge_graph.ttl",
    format="turtle"
)