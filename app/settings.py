# -*- coding: utf-8 -*-
'''
Application configuration.
Most configuration is set via environment variables.
For local development, use a .env file to set
environment variables.
'''
# Third party imports
from environs import Env

env = Env()
env.read_env()


ENV = env.str('FLASK_ENV', default='production')
DEBUG = ENV == 'development'

SPARQL_ENDPOINT = env.str('SPARQL_ENDPOINT')
BASE_IRI = env.str('BASE_IRI')
CORPUS_NAME = env.str('CORPUS_NAME')
CORPUS_TITLE = env.str('CORPUS_TITLE')
