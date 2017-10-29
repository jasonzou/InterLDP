from flask import Flask,Response
from rdflib import ConjunctiveGraph,Graph
from rdflib.namespace import Namespace, NamespaceManager
import json

app = Flask(__name__)

base = "http://127.0.0.1:5000/"

#object to hold all graphs
graphs = {}

#loading configurations
conf = open('config.json')
conf = json.load(conf)

for context in conf["contexts"]:
        name = context["name"]
        graph = context["graph"]
        tempGraph = ConjunctiveGraph()

        #generating the base
        currentbase = base
        if (name != "ROOT"):
                currentbase = currentbase + name + "/"

        #loading the graph
        tempGraph.parse(graph,format="trig",publicID=currentbase)
        graphs[name] = tempGraph

        #loading the prefixes
        for prefix in conf["prefixes"]:
                tempGraph.bind(prefix,conf["prefixes"][prefix])
	tempGraph.bind("data",currentbase)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def generic_controller(path):
	
	currentbase = base
	g = graphs["ROOT"]
	rootPath = path.split("/")[0]
	if rootPath in graphs:
		currentbase = currentbase + rootPath + "/"
		g = graphs[rootPath]	
	
	response = Response()
	
	resourceIRI = base + path
	
	#check if the resource exist in the LDP dataset
	qask = "ASK WHERE { GRAPH <"+resourceIRI+"> {?s ?p ?o .}}"
	#print g.serialize(format="turtle")
	qres = g.query(qask)
	result = False
	for result in qres:
		if not result:
			print 
			response.status_code = 404
			return response

	response.headers["Allow"] = "GET"

	#the resource exist so create the result
	qres = g.query("CONSTRUCT { ?s ?p ?o . } WHERE { GRAPH <"+resourceIRI+"> {?s ?p ?o .}}")
	resultGraph = Graph()
	resultGraph.bind("data",currentbase)

	#loading prefixes from configuration
        for prefix in conf["prefixes"]:
                resultGraph.bind(prefix,conf["prefixes"][prefix])
	
	#creating the result graph from the construct query	
	resultGraph = resultGraph.parse(data=qres.serialize(format='xml'))

	#creating the result	
	response.content_type = "text/turtle"
	link_header = '<http://wiki.apache.org/marmotta/LDPImplementationReport/2014-09-16>; rel="http://www.w3.org/ns/ldp#constrainedBy", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://www.w3.org/ns/ldp#RDFSource>; rel="type"'
	qres = g.query("ASK WHERE { GRAPH <"+resourceIRI+"> { <"+resourceIRI+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/ldp#BasicContainer> .}}")
	for result in qres:
		if (result):
			link_header = link_header + ' ,<http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type" '
	response.headers["Link"] = link_header
	response.data = resultGraph.serialize(format="n3")
	return response

if __name__ == "__main__":
        app.debug = True
        app.run()
