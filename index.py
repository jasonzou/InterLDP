from flask import Flask,Response
from rdflib import ConjunctiveGraph,Graph
from rdflib.namespace import Namespace, NamespaceManager
app = Flask(__name__)

base = "http://127.0.0.1:5000/"
g = ConjunctiveGraph()
data = Namespace(base)
g.bind("data",data)
g.parse("graph.ttl",format="trig",publicID=base)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def generic_controller(path):
	
	response = Response()
	
	#check if the resource exist in the LDP dataset
	qres = g.query("ASK WHERE { GRAPH <"+base+path+"> {?s ?p ?o .}}")
	result = False
	for result in qres:
		if not result:
			print 
			response.status_code = 404
			return response

	response.headers["Allow"] = "GET"

	#the resource exist so create the result
	qres = g.query("CONSTRUCT { ?s ?p ?o . } WHERE { GRAPH <"+base+path+"> {?s ?p ?o .}}")
	resultGraph = Graph()
	
	#binding namespaces
	ldpns = Namespace('http://www.w3.org/ns/ldp#')
	resultGraph.bind("ldp",ldpns)

	foafns = Namespace("http://xmlns.com/foaf/0.1/")
	resultGraph.bind("foaf",foafns)
	
	dcns = Namespace("http://purl.org/dc/terms/")
	resultGraph.bind("dc",dcns)
	
	dcatns = Namespace("http://www.w3.org/ns/dcat#")
	resultGraph.bind("dcat",dcatns)

	data = Namespace(base)
	resultGraph.bind("data",data)

	#creating the result graph from the construct query	
	resultGraph = resultGraph.parse(data=qres.serialize(format='xml'))

	#creating the result	
	response.content_type = "text/turtle"
	link_header = '<http://wiki.apache.org/marmotta/LDPImplementationReport/2014-09-16>; rel="http://www.w3.org/ns/ldp#constrainedBy", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://www.w3.org/ns/ldp#RDFSource>; rel="type"'
	qres = g.query("ASK WHERE { GRAPH <"+base+path+"> { <"+base+path+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/ldp#BasicContainer> .}}")
	for result in qres:
		if (result):
			link_header = link_header + ' ,<http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type" '
	response.headers["Link"] = link_header
	response.data = resultGraph.serialize(format="n3")
	return response

if __name__ == "__main__":
        app.debug = True
        app.run()
