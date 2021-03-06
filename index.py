from flask import Flask,Response,request
from rdflib import ConjunctiveGraph,Graph
from rdflib.namespace import Namespace, NamespaceManager
import json
import hashlib
import os
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import urllib


from Utilities import *
from DataSourceFactory import *
from DataSource import *
from VirtualLDP import *

reload(sys)
sys.setdefaultencoding("utf-8")
app = Flask(__name__)


#object to hold all graphs
graphs = {}

#loading configurations
##base_directory = "/home/nbakeral/github/LDPDatasetFrontend/"
base_directory = ""
conf = open(base_directory+'config.json')
conf = json.load(conf)

##base="http://opensensingcity.emse.fr/ldpdfend/"
base = conf["base"]

def getContext(path):
	names = {}
	for obj in conf["contexts"]:
		names[obj["name"]] = obj	
	while (len(path) > 0):
		if path in names:
			return names[path]
		path = path[:path.rfind("/")]
	return None

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def generic_controller(path):
	currentbase = base
	
	#create the response object and set generic 
	response = Response()

	#validate if the request can be served
        #get the second part just after /
	obj = getContext(path)	
	print obj
	if obj != None:
		name = obj["name"]
		pURL = obj["PLDPDataset"]
		vURL = None
		if "VLDPDataset" in obj:
			vURL = obj["VLDPDataset"]
		if (currentbase[-1] != "/"):
			currentbase = currentbase+"/"
		currentbase = currentbase +  name + "/"
	else:
		response.status_code = 404
		return response
	
	#create the etag
	etag = hashlib.sha1(path).hexdigest()
	
	#response headers
	response.headers["Allow"] = "GET, OPTIONS, HEAD"
	
	 #validate preference
	prefer_header = None 
        if prefer_header != None:
                response.headers["Preference-Applied"] = "return=representation"
        response.set_etag(etag)



	#get accept header
	accept_header = request.headers["Accept"]
	
	#check preference header
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
			
	
	
	#get the absolute path for the resource	
	resourceIRI = base + urllib.quote(path.encode('utf8'))
	print resourceIRI	
	#resourceIRI = base + urllib.quote(path)
		
	#check if the resource exist in the LDP dataset
	qask = "ASK WHERE { GRAPH <"+resourceIRI+"> {?s ?p ?o .}}"
	qres = getRS(pURL,qask)
	result = qres["boolean"]
	
	#if result is none, return 404
	if not result:
		response.status_code = 404
		return response


	
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
	resultGraph = getG(pURL,rgraph)

	#loading prefixes from configuration
        for prefix in conf["prefixes"]:
                resultGraph.bind(prefix,conf["prefixes"][prefix])
	
	#bind the root prefix
	resultGraph.namespace_manager.bind("child",base+path+"/")
	resultGraph.namespace_manager.bind("parent",base+path[:path.rfind("/")+1])
	
	#creating the result graph from the construct query	
	#resultGraph = resultGraph.parse(data=qres.serialize(format='xml'))

	#creating the result	
	link_header = '<https://github.com/noorbakerally/InterLDP>; rel="http://www.w3.org/ns/ldp#constrainedBy", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://www.w3.org/ns/ldp#RDFSource>; rel="type"'
	qres = resultGraph.query("ASK WHERE { <"+resourceIRI+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/ldp#BasicContainer> .}")
	for result in qres:
		if (result):
			link_header = link_header + ' ,<http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type" '
	response.headers["Link"] = link_header
	
	#generate the virtual graph
	resultGraph = resultGraph + getVirtualGraph(vURL,resourceIRI)	

	#serialize graph based on accept
	#or set turtle by default
	if "application/ld+json" in accept_header:
		response.data = resultGraph.serialize(format="json-ld")
		response.content_type = "application/ld+json"
	else:
		response.data = resultGraph.serialize(format="turtle")
		response.content_type = "text/turtle"

	return response

if __name__ == "__main__":
        app.debug = True
        app.run()
