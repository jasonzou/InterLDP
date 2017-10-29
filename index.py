from flask import Flask
from rdflib import ConjunctiveGraph,Graph
from rdflib.namespace import Namespace, NamespaceManager
app = Flask(__name__)


base = "http://127.0.0.1:5000/"
strDataset = open('graph.ttl', 'r')
strDataset = strDataset.read()

strDataset = "@base <"+base+"> .\n" + strDataset

g = ConjunctiveGraph()
g.parse(data=strDataset,format="trig")


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def generic_controller(path):
	qres = g.query("ASK WHERE { GRAPH <"+base+path+"> {?s ?p ?o .}}")
	result = False
	for result in qres:
		if not result:
			return "not exist"
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
	
	resultGraph = resultGraph.parse(data=qres.serialize(format='xml'))
	
	return resultGraph.serialize(format="n3")
	

if __name__ == "__main__":
        app.debug = True
        app.run()
