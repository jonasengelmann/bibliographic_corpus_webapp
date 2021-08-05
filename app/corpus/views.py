# -*- coding: utf-8 -*-

# Standard library imports
from collections import defaultdict

# Third party imports
from flask import Blueprint, render_template, url_for, redirect
from environs import Env

# Local imports
from app.extensions import sparqlstore
from app.corpus.vocabularies import vocabularies


env = Env()
env.read_env()

BASE_IRI = env.str('BASE_IRI').strip('/')
CORPUS_NAME = env.str('CORPUS_NAME')

blueprint = Blueprint('corpus', __name__, static_folder='../static', url_prefix=f'/{CORPUS_NAME}')


def get_corpus_resource_data(iri):
    query = f'SELECT * WHERE {{<{iri}> ?pred ?obj .}}'
    result = sparqlstore.query(query)

    resource_data = defaultdict(lambda: [])
    for triple in result:
        predicate = triple['pred']['value']
        object = triple['obj']['value']
        if triple['obj']['type'] == 'uri':
            value = vocabularies.get(object)
            if not value:
                value = fromat_as_short_iri(object)
            x = {'name': value, 'link': object}
        else:
            x = {'name': object, 'link': None}
        resource_data[vocabularies[predicate]].append(x)

    return resource_data


def fromat_as_short_iri(iri):
    return iri.replace(f'{BASE_IRI}/', '').replace('/', ':')


def generate_resource_view(dataset_name, count, property_order):
    resource_data = get_corpus_resource_data(iri=f'{BASE_IRI}/{identifier}/{count}')
    ordered_resource_data = {
        key: sorted(resource_data[key], key=lambda x: x['name'])
        for key in property_order
        if key in resource_data
    }
    return render_template('corpus/resource.html', data=ordered_resource_data)


@blueprint.route('/')
def corpus_example():
    return redirect(url_for('.bibliographic_resource', id=1))


@blueprint.route('/id/<id>')
def identifier(id):
    property_order = ['Value', 'Scheme']
    return generate_resource_view(dataset_name='id', count=id, property_order=property_order)


@blueprint.route('/ar/<id>')
def agent_role(id):
    property_order = ['Role', 'Relates To Document', 'Has Next', 'Relates To Organization']
    return generate_resource_view(dataset_name='ar', count=id, property_order=property_order)


@blueprint.route('/ra/<id>')
def responsible_agent(id):
    property_order = ['Name', 'Given Name', 'Family Name', 'Identifier']
    return generate_resource_view(dataset_name='ra', count=id, property_order=property_order)


@blueprint.route('/br/<id>')
def bibliographic_resource(id):
    property_order = [
        'Type',
        'Title',
        'Sequence Identifier',
        'Edition',
        'Has Identifier',
        'Publication Date',
        'Contributor',
        'Part Of',
        'Embodiment',
        'Relation',
        'Contains',
        'Cites',
        ]
    return generate_resource_view(dataset_name='br', count=id, property_order=property_order)


@blueprint.route('/re/<id>')
def resource_embodiment(id):
    property_order = ['Format', 'Starting Page', 'Ending Page', 'URL']
    return generate_resource_view(dataset_name='re', count=id, property_order=property_order)


@blueprint.route('/be/<id>')
def bibliographic_reference(id):
    property_order = ['Content', 'References', 'Annotation']
    return generate_resource_view(dataset_name='be', count=id, property_order=property_order)


@blueprint.route('oe/<id>')
def organizational_entity(id):
    property_order = ['Name']
    return generate_resource_view(dataset_name='oe', count=id, property_order=property_order)


@blueprint.route('st/<id>')
def subject_term(id):
    property_order = ['Name']
    return generate_resource_view(dataset_name='st', count=id, property_order=property_order)
