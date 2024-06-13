import sys
import os
from app import create_app
from flask import jsonify

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'common'))

app = create_app('dev')


@app.route('/')
def index():
    return jsonify({rule.endpoint: rule.rule for rule in app.url_map.iter_rules()})
