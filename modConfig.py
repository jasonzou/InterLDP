import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

contexts = json.load(open("config.json","r"))
datasetDirectory = "/home/nbakeral/github/LDPDatasetFrontend/datasets/"

endpointbase = "http://opensensingcity.emse.fr/sparql/"
newContexts = []

for context in contexts["contexts"]:
	base = "http://opensensingcity.emse.fr/ldpdfend/" 
	
	name = context["name"]
	graphName = context["graph"]
	graphName = graphName[graphName.rfind("/")+1:]
	newGraphName = graphName[:graphName.rfind(".")]
	newGraphName = newGraphName + ".trig"

	newContext = {}
	newContext["name"] = name
	newContext["pldpdataset"] = endpointbase + "newGraphName"	

	graph = open(context["graph"],"r")
	
	base = "@base <"+base + name + "/> .\n"
	
	graphContent = graph.read()

	newGraph = open("graphs1/"+newGraphName,"w")
	newGraph.write(base+graphContent)
	newGraph.close()

	newContexts.append(newContext)

print json.dumps(newContexts)
