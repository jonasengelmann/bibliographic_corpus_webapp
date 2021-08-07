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


property_orders = {
    'id': ['Type', 'Value', 'Scheme'],
    'ar': ['Type', 'Role', 'Relates To Document', 'Has Next', 'Relates To Organization'],
    'ra': ['Type', 'Name', 'Given Name', 'Family Name', 'Has Identifier'],
    'br': [
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
        ],
    're': ['Type', 'Format', 'Starting Page', 'Ending Page', 'URL'],
    'be': ['Type', 'Content', 'References', 'Annotation'],
    'oe': ['Type', 'Name', 'Has Identifier'],
    'st': ['Type', 'Name', 'Has Identifier'],
}


def get_resource_data(iri, key_order):
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

    return {
        key: sorted(resource_data[key], key=lambda x: x['name'])
        for key in key_order
        if key in resource_data
    }


def fromat_as_short_iri(iri):
    return iri.replace(f'{BASE_IRI}/', '').replace('/', ':')


@blueprint.route('/')
def resource_example():
    return redirect(url_for('.resource', dataset_identifier='br', iri_count=1))


@blueprint.route('<dataset_identifier>/<iri_count>')
def resource(dataset_identifier, iri_count):
    resource_data = get_resource_data(
        iri=f'{BASE_IRI}/{dataset_identifier}/{iri_count}',
        key_order=property_orders[dataset_identifier]
    )
    return render_template('corpus/resource.html', data=resource_data)
