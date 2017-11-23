from DataSource import *
from Utilities import *

def createDataSource(data):
	ds = None
	location = data["location"]["value"]
	if data["type"]["value"] == getTerm("SPARQLDataSource"):
		ds = SPARQLDataSource(location)
	else:
		liftingRule = None
		if "liftingRule" in data: liftingRule = data["liftingRule"]
		ds = RDFFileDataSource(location,liftingRule)
	return ds
