from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph
#the LDP design vocabulary prefix
vPrefix = "http://opensensingcity.emse.fr/LDPDesignVocabulary/"

def getRS(url,query):
	query = query.replace("http://127.0.0.1:5000/","http://opensensingcity.emse.fr/ldpdfend/")
	sparql = SPARQLWrapper(url)
	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()
	return results

def getG(url,query):
	query = query.replace("http://127.0.0.1:5000/","http://opensensingcity.emse.fr/ldpdfend/")
        sparql = SPARQLWrapper(url)
        sparql.returnFormat = "text/turtle"
        sparql.setQuery(query)
        result = sparql.query()
        data = result.response.read()
        resultGraph = Graph().parse(data=data,format="turtle")
        return resultGraph

def getTerm(term):
	return vPrefix+str(term)
