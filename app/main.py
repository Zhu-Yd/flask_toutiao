from flask import Flask
from flask import jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return jsonify({rule.endpoint: rule.rule for rule in app.url_map.iter_rules()})
