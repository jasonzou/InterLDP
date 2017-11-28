from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph

from DataSource import *
from DataSourceFactory import *

def getVirtualGraph(vURL,resourceIRI):
	sparql = SPARQLWrapper(vURL)
	vG = Graph()	

	#return empty graph
	#if there is no virtual URL
	if vURL == None:
		return vG
	
	#SPARQL Prefixes
	prefix = "PREFIX on: <http://opensensingcity.emse.fr/LDPDesignVocabulary/>"
	#get all resource maps
	query = """ SELECT DISTINCT ?rm ?cq ?ds ?type ?location ?liftingRule WHERE { <resourceIRI> on:compiledResourceMap ?rm . ?rm on:compiledGraphQuery ?cq;on:dataSource ?ds;. ?ds a ?type;on:location ?location .OPTIONAL { ?ds on:liftingRule ?liftingRule . }} """
	query = query.replace("resourceIRI",resourceIRI)
	query = prefix+query 	
	query = query.replace("http://127.0.0.1:5000/","http://opensensingcity.emse.fr/ldpdfend/")
	
	#print query
	
	#send the query for processing
	sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

	#creating the resource maps needed to execute for this resource
	#for each resource maps, there can be several data sources	
	rms = {}
	for result in results["results"]["bindings"]:
		#getting details about the current resource map
		rm = result["rm"]["value"]
		dsIRI = result["ds"]["value"]
		dsType = result["type"]["value"]
		dsLoc = result["location"]["value"]
		dsLr = result["liftingRule"]["value"]
		
		#check if the rm has been checked
		#if yes, only get the ds
		if rm in rms:
			rms[rm]["DataSources"][dsIRI] = {"type":dsType,"liftingRule":dsLr,"location":dsLoc}
		else:
			rms[rm] = {}
			rms[rm]["DataSources"] = {}	
			rms[rm]["cq"] = result["cq"]["value"]
			rms[rm]["DataSources"][dsIRI] = {"type":dsType,"liftingRule":dsLr,"location":dsLoc}
	
	#the dynamic graph of the final resource
	resultGraph = Graph()
	
	#iterate on resource maps
	for rm in rms:
		rm = rms[rm]
		cq = rm["cq"]
		
		#allds holds the merge of all ds
		allds = RDFFileDataSource(None,None)
		allds.graph = Graph()
	
		#load all the ds
		#and append it to allds
		for ds in rm["DataSources"]:
			data = rm["DataSources"][ds]
			ds = createDataSource(ds,data)
			ds.loadGraph()
			allds.graph = allds.graph + ds.graph
			
		#append the result graph with result from construct query on allds
		resultGraph = resultGraph + allds.cquery(cq)
	vG = vG + resultGraph
	return vG
