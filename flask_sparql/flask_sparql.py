# -*- coding: utf-8 -*-

# Third party imports
from flask import current_app, _app_ctx_stack
from SPARQLWrapper import SPARQLWrapper, SPARQLExceptions


class SPARQLStore(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        pass

    def connect(self):
        return SPARQLWrapper(
            endpoint=current_app.config['SPARQL_ENDPOINT'],
            returnFormat='json'
        )

    def connection(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'sparqlstore'):
                ctx.sparqlstore = self.connect()
            return ctx.sparqlstore

    def query(self, query):
        sparqlstore = self.connection()
        sparqlstore.setMethod('GET')
        sparqlstore.setQuery(query)
        try:
            results = sparqlstore.queryAndConvert()
        except SPARQLExceptions.SPARQLWrapperException as ex:
            raise ex
        return results['results']['bindings']
