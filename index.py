from flask import Flask,Response,request
from rdflib import ConjunctiveGraph,Graph
from rdflib.namespace import Namespace, NamespaceManager
import json
import hashlib

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
	accept_header = request.headers["Accept"]
	prefer_header = None 
	if "Prefer" in request.headers:
		#print request.headers
		prefer = request.headers["Prefer"]
		if "PreferMinimalContainer" in prefer:
			prefer_header = "minimal" 
		elif "PreferContainment" in prefer:
			prefer_header = "containment"
		
		if "include" in prefer:
			prefer_header = "include_" + prefer_header
		else:
			prefer_header = "omit_" + prefer_header
			
	etag = hashlib.sha1(path).hexdigest()
	
	currentbase = base
	g = graphs["ROOT"]
	secondPart = path.index("/")+path[path.index("/")+1:].index("/")+1
	secondPart = path[:secondPart]
	rootPath = path.split("/")[0]

	
	if secondPart in graphs:
		currentbase = currentbase + secondPart + "/"
		g = graphs[secondPart]
	elif rootPath in graphs:
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
			response.status_code = 404
			return response

	response.headers["Allow"] = "GET, OPTIONS, HEAD"

	
	#the resource exist so create the result
	rgraph = "CONSTRUCT { ?s ?p ?o . } WHERE { GRAPH <"+resourceIRI+"> {?s ?p ?o .}}"
	
	#change graph based on the Prefered header
	if prefer_header == "include_minimal":
		rgraph = "CONSTRUCT { ?s ?p ?o . } WHERE { GRAPH <"+resourceIRI+"> {?s ?p ?o .} FILTER (?p not in (<http://www.w3.org/ns/ldp#contains>))}"
	elif prefer_header == "omit_minimal":
		rgraph = "CONSTRUCT { ?s ?p ?o . } WHERE { GRAPH <"+resourceIRI+"> {?s ?p ?o .} FILTER (?p not in (<http://www.w3.org/ns/ldp#contains>))}"
	elif prefer_header == "omit_containment":
		rgraph = "CONSTRUCT { ?s ?p ?o . } WHERE { GRAPH <"+resourceIRI+"> { ?s ?p ?o .} FILTER (?p not in (<http://www.w3.org/ns/ldp#contains>))}"
	elif prefer_header == "include_containment":
                rgraph = "CONSTRUCT { ?s ?p ?o . } WHERE { GRAPH <"+resourceIRI+"> { ?s ?p ?o .} }"
	#print rgraph
	
	#execute construct query and build LDPRS graph based on it
	qres = g.query(rgraph)
	resultGraph = Graph()
	resultGraph.bind("data",currentbase)

	#loading prefixes from configuration
        for prefix in conf["prefixes"]:
                resultGraph.bind(prefix,conf["prefixes"][prefix])
	
	#bind the root prefix
	resultGraph.namespace_manager.bind("",base+path+"/")
	
	#creating the result graph from the construct query	
	resultGraph = resultGraph.parse(data=qres.serialize(format='xml'))

	#creating the result	
	link_header = '<http://wiki.apache.org/marmotta/LDPImplementationReport/2014-09-16>; rel="http://www.w3.org/ns/ldp#constrainedBy", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://www.w3.org/ns/ldp#RDFSource>; rel="type"'
	qres = g.query("ASK WHERE { GRAPH <"+resourceIRI+"> { <"+resourceIRI+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/ldp#BasicContainer> .}}")
	for result in qres:
		if (result):
			link_header = link_header + ' ,<http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type" '
	response.headers["Link"] = link_header
	if "application/ld+json" in accept_header:
		response.data = resultGraph.serialize(format="json-ld")
		response.content_type = "application/ld+json"
	else:
		response.data = resultGraph.serialize(format="turtle")
		response.content_type = "text/turtle"

	#validate preference
	if prefer_header != None:
		response.headers["Preference-Applied"] = "return=representation"
	response.set_etag(etag)
	return response

if __name__ == "__main__":
        app.debug = True
        app.run()
