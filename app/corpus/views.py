# -*- coding: utf-8 -*-

# Standard library imports
import re
import json
from collections import defaultdict

# Third party imports
from flask import Blueprint, render_template, url_for, redirect
from environs import Env

# Local imports
from app.extensions import sparqlstore


env = Env()
env.read_env()

BASE_IRI = env.str('BASE_IRI').strip('/')
CORPUS_NAME = env.str('CORPUS_NAME')

blueprint = Blueprint('corpus', __name__, static_folder='../static', url_prefix=f'/{CORPUS_NAME}')

with open('app/corpus/config/property_order.json', 'r') as f:
    property_orders = json.load(f)

with open('app/corpus/config/vocabularies.json', 'r') as f:
    vocabularies = json.load(f)


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
        for key in ['Label', 'Type'] + key_order
        if key in resource_data
    }


def get_history_data(iri):
    query = f"""
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX oco: <https://w3id.org/oc/ontology/>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT *
        FROM <{iri}/prov>
        FROM <{BASE_IRI}/prov/pa>
        WHERE {{
        ?ca a prov:Activity .
        ?ca a ?type .
        ?ca dcterms:description ?description .
        ?se prov:wasGeneratedBy ?ca .
        ?se prov:generatedAtTime ?generated_time .
        ?ca prov:qualifiedAssociation ?curator .
        ?curator prov:hadRole oco:occ-curator .
        ?curator prov:agent ?curator_agent .
        ?curator_agent foaf:name ?curator_name .
        OPTIONAL {{
            ?ca prov:qualifiedAssociation ?metadata_provider .
            ?metadata_provider prov:hadRole
                oco:source-metadata-provider .
            ?metadata_provider prov:agent ?metadata_provider_agent .
            ?metadata_provider_agent foaf:name ?metadata_provider_name .
        }}
        OPTIONAL {{?se oco:hasUpdateQuery ?update_query . }}
        OPTIONAL {{?ca prov:used ?used_resource . }}
        OPTIONAL {{?ca prov:wasInformedBy ?informed_ca .}}
        FILTER(?type != prov:Activity)
    }}
    """
    result = sparqlstore.query(query)

    view_history_objects = []
    for x in result:
        view_history_object = {
            'Type': {'name': vocabularies[x['type']['value']], 'link': x['ca']['value']},
            'Generated At Time': {'name': x['generated_time']['value'], 'link': None},
            'Description': {'name': x['description']['value'], 'link': None},
            'Curator': {'name': x['curator_name']['value'], 'link': x['curator_agent']['value']},
        }
        if x.get('metadata_provider'):
            view_history_object['Metadata Provider'] = {
                'name': x['metadata_provider_name']['value'],
                'link': x['metadata_provider_agent']['value']
            }
        if x.get('informed_ca'):
            view_history_object['Informed By'] = {
                'name': fromat_as_short_iri(x['informed_ca']['value']),
                'link': x['informed_ca']['value']
            }
        if x.get('used_resource'):
            view_history_object['Used Ressource'] = {
                'name': fromat_as_short_iri(x['used_resource']['value']),
                'link': x['used_resource']['value']
            }
        if x.get('primary_resource'):
            view_history_object['Primary Resource'] = {
                'name': x['primary_resource']['value'],
                'link': None,
            }
        view_history_objects.append(view_history_object)
    return view_history_objects


def generate_resource_view(iri, key_order):
    resource_data = get_resource_data(iri=iri, key_order=key_order)
    title = resource_data.pop('Label')[0]['name']
    return render_template('corpus/resource.html', title=title, data=resource_data)


def fromat_as_short_iri(iri):
    result = re.match(pattern=rf'{BASE_IRI}/(.*?)/(\d+)$', string=iri)
    return f'{result.group(1)}:{result.group(2)}'


@blueprint.route('/')
def resource_example():
    return redirect(url_for('.resource', dataset_id='br', iri_count=1))


@blueprint.route('<dataset_id>/<iri_count>')
def resource(dataset_id, iri_count):
    return generate_resource_view(
        iri=f'{BASE_IRI}/{dataset_id}/{iri_count}',
        key_order=property_orders[dataset_id],
        provenance_resource=False
    )


@blueprint.route('prov/<dataset_id>/<iri_count>')
def prov_resource(dataset_id, iri_count):
    return generate_resource_view(
        iri=f'{BASE_IRI}/prov/{dataset_id}/{iri_count}',
        key_order=property_orders[dataset_id],
        provenance_resource=True
    )


@blueprint.route('<resource_dataset_id>/<resource_iri_count>/prov/<dataset_id>/<iri_count>')
def prov_resource2(resource_dataset_id, resource_iri_count, dataset_id, iri_count):
    return generate_resource_view(
        iri=f'{BASE_IRI}/{resource_dataset_id}/{resource_iri_count}/prov/{dataset_id}/{iri_count}',
        key_order=property_orders[dataset_id],
        provenance_resource=True
    )


@blueprint.route('<dataset_id>/<iri_count>/view_history')
def resource_with_history(dataset_id, iri_count):
    resource_data = get_resource_data(
        iri=f'{BASE_IRI}/{dataset_id}/{iri_count}',
        key_order=property_orders[dataset_id]
    )
    title = resource_data.pop('Label')[0]['name']

    history_data = get_history_data(
        iri=f'{BASE_IRI}/{dataset_id}/{iri_count}'
    )

    return render_template(
        'corpus/resource_with_history.html',
        title=title,
        data=resource_data,
        history_data=history_data,
    )
