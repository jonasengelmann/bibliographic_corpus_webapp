# -*- coding: utf-8 -*-

# Third party imports
from flask import Flask

# Local imports
from app import main, corpus
from app.extensions import sparqlstore


def create_app(config_object='app.settings'):
    '''
    Create application factory, as explained
    here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    '''
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    return app


def register_blueprints(app):
    '''Register Flask blueprints.'''
    app.register_blueprint(main.views.blueprint)
    app.register_blueprint(corpus.views.blueprint)
    return None


def register_extensions(app):
    '''Register Flask extensions.'''
    sparqlstore.init_app(app)
