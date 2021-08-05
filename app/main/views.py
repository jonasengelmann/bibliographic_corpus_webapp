# -*- coding: utf-8 -*-

# Third party imports
from flask import Blueprint, render_template

blueprint = Blueprint('main', __name__, static_folder='../static')


@blueprint.route('/')
@blueprint.route('/query')
def query():
    return render_template('main/query.html')
