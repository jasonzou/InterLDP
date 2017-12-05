# InterLDP
InterLDP is a linked data platform server based on the Linked Data Platform (LDP) 1.0 W3C Recommendation. It uses two core concepts: <a href="http://opensensingcity.emse.fr/ldpdl/ldpdl.html#ldp-dataset">LDP dataset</a> and <a href="http://opensensingcity.emse.fr/ldpdl/ldpdl.html#virtual-ldp-graph">Virtual LDP Graph</a>. InterLDP acts as an LDP frontend on top of a SPARQL endpoint which serves LDP resources structured per the structure of an LDP dataset. It can also operates in virtual mode whereby the content of the LDP RDF source (i.e. part of the RDF graph) is generated at query time.

## LDP Conformance
The execution report generated using the <a href="https://w3c.github.io/ldp-testsuite/">LDP Test Suite</a> can be found at <a href="http://opensensingcity.emse.fr/interldp/ldp-testsuite-execution-report.html">http://opensensingcity.emse.fr/interldp/ldp-testsuite-execution-report.html</a>. In summary: 

1. Only LDP basic containers are supported
2. LDP Non-RDF Sources are not supported
3. Only GET,HEAD,OPTIONS HTTP requests are supported on LDP RDF Sources
4. Paging and sorting are not supported
5. Sec. 4.2.1.6 (rel='ldp:constrainedBy'-Link) is fulfilled by pointing to this page.
`Link: <https://github.com/noorbakerally/InterLDP>; rel="http://www.w3.org/ns/ldp#constrainedBy"`


## Usage

- InterLDP can hosts several LDPs at the same time and operate in different contexts. The contexts are defined in `config.json` which normally resides in the root directory. `config.json` is made up of 3 parts:

1. base: which acts as a namespace for all the LDPs to be hosted at the specified base URL
2. prefixes: defines a set of prefixes which is used when serializing RDF graph of LDP RDF sources
3. contexts: defines a set of contexts where each context is a json object of the form `{"name":"","PLDPDataset": "","VLDPGraph": ""}`. `name` specifies the name of the context which must be unique. `PLDPDataset` specifies the URL of a SPARQL endpoint of the LDP dataset to be exposed. `VLDPGraph` specifies the URL of a SPARQL endpoint which exposes the Virtual Graph for the LDP. 

## Installation
InterLDP is written in python using <a href="http://flask.pocoo.org/">Flask</a>. The following are main dependencies which needs to be installed:

1. <a href="https://github.com/RDFLib/rdflib">RDFLib</a> which is a python library for working with RDF
2. <a href="https://rdflib.github.io/sparqlwrapper/">SPARQLWrapper</a> which is a wrapper around a SPARQL service

InterLDP can function in debug mode or deploy mode:

- debug mode: use the command `python index.py` to start the server
- deploy mode: InterLDP is deployed via an HTTP Server. We provide the configuration for Apache HTTP Server only.

### Apache HTTP Server configuration

We provide a complete sample of a VirtualHost file:

```
LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so

<VirtualHost>
        ServerName example.com
	WSGIDaemonProcess AppContextName user=www-data group=www-data threads=5
	WSGIScriptAlias /AppContextName /path/to/start.wsgi`
</VirtualHost>
```

## References:
1. Speicher, Steve, John Arwe, and Ashok Malhotra. "Linked data platform 1.0." W3C Recommendation, February 26 (2015).
APA	(https://www.w3.org/TR/ldp/)
