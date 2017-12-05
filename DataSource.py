from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, JSON
import requests
import json

class DataSource:
	def __init__(self):
		self.location = None
	
	def __init__(self,location):
		self.location = location

	def setLocation(self,location):
		self.location = location

class RDFFileDataSource(DataSource):
	def __init__(self):
		self.graph = None
		self.location = None
		self.liftingRule = None

	def __init__(self,location,liftingRule):
		self.graph = None
                self.location = location
		self.liftingRule = liftingRule

	def loadGraph(self):
		#if the graph is already loaded
		if self.graph != None:
			return
		
		if self.liftingRule == None:
			self.graph = Graph()
			self.graph.parse(self.location)
		else:
			query = requests.get(self.liftingRule)
			query = query.text
			headers = {'content-type': 'application/x-www-form-urlencoded'}
			params = {"query":query}
			url = "https://ci.mines-stetienne.fr/sparql-generate/api/transform"
			response = requests.post(url, params=params, headers=headers)
			data = json.loads(response.text)
			graphdata = data["output"]
			self.graph = Graph().parse(data=graphdata,format="turtle")
			
	
			
	def cquery(self,query):
		if self.graph == None:
			#load graph
			self.loadGraph()
		
		#perform the query
		resultGraph = self.graph.query(query)
		return Graph().parse(data=resultGraph.serialize(format='xml'))
			



class SPARQLDataSource(DataSource):
	def __init__(self):
		self.location = None
	
	def __init__(self,location):
		self.location = location
	
	def cquery(self,query):
		sparql = SPARQLWrapper(self.location)
		sparql.returnFormat = "text/turtle"
		sparql.setQuery(query)
		result = sparql.query()
		data = result.response.read()
		resultGraph = Graph().parse(data=data,format="turtle")
		return resultGraph
