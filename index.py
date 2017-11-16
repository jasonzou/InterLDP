        #create the response object and set generic
        #response headers
        response = Response()
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


        currentbase = base

        #validate if the request can be served

        #get the second part just after /
        try:
                rootPath = path.split("/")[0]
                secondPart = path.index("/")+path[path.index("/")+1:].index("/")+1
                secondPart = path[:secondPart]
                if secondPart in graphs:
                        currentbase = currentbase + secondPart + "/"
                        g = graphs[secondPart]
                elif rootPath in graphs:
                        currentbase = currentbase + rootPath + "/"
                        g = graphs[rootPath]
                else:
                        response.status_code = 404
                        return response
        except:
                response.status_code = 404
                return response

        #get the absolute path for the resource
        resourceIRI = base + path

        #check if the resource exist in the LDP dataset
        qask = "ASK WHERE { GRAPH <"+resourceIRI+"> {?s ?p ?o .}}"
        qres = g.query(qask)
        result = False

        #if result is none, return 404
        for result in qres:
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
        qres = g.query(rgraph)
        resultGraph = Graph()

        #loading prefixes from configuration
        for prefix in conf["prefixes"]:
                resultGraph.bind(prefix,conf["prefixes"][prefix])

        #bind the root prefix
        resultGraph.namespace_manager.bind("child",base+path+"/")
        resultGraph.namespace_manager.bind("parent",base+path[:path.rfind("/")]+"/")

        #creating the result graph from the construct query
        resultGraph = resultGraph.parse(data=qres.serialize(format='xml'))

        #creating the result
        link_header = '<http://wiki.apache.org/marmotta/LDPImplementationReport/2014-09-16>; rel="http://www.w3.org/ns/ldp#constrainedBy", <http://www.w3.org/ns/ldp#Resource>; rel="type", <http://www.w3.org/ns/ldp#RDFSource>; rel="type"'
        qres = resultGraph.query("ASK WHERE { <"+resourceIRI+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/ldp#BasicContainer> .}")
        for result in qres:
                if (result):
                        link_header = link_header + ' ,<http://www.w3.org/ns/ldp#Container>; rel="type", <http://www.w3.org/ns/ldp#BasicContainer>; rel="type" '
        response.headers["Link"] = link_header


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
~                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
~                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
~                                                 
