from DataSource import *
from Utilities import *

def createDataSource(iri,data):
	print data
	ds = None
	location = data["location"]
	if data["type"] == getTerm("SPARQLDataSource"):
		ds = SPARQLDataSource(location)
	else:
		liftingRule = None
		if "liftingRule" in data: liftingRule = data["liftingRule"]
		ds = RDFFileDataSource(location,liftingRule)
	return ds
