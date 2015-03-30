import json
import subprocess
from flask import Flask
from flask import request
from flask import jsonify
from flask.ext.cors import CORS
app = Flask(__name__)
CORS(app)


@app.route('/qlayout', methods=['POST'])
def qlayout():
    obj = request.json
    json.dump(obj, open('data.json', 'w'))
    p = subprocess.Popen(
        ['pyomo', '-q', 'model.py', '--json'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE)
    out, err = p.communicate()
    result = json.load(open('results.json'))
    sol = result['Solution'][1]['Variable']

    def getrank(node):
        yi = sol.get('y[{}]'.format(node['index']))
        if yi:
            return yi['Value']
        return 0
    response = jsonify({'entries': [
        {'key': node['index'], 'rank': getrank(node)}
        for node in obj['nodes']]})
    response.headers['Content-Type'] = 'application/json'
    return response


if __name__ == '__main__':
    app.run(debug=True)
