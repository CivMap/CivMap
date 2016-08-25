import os
import json
from flask import Flask, Response, request
from flask.ext.bower import Bower

app = Flask(__name__, static_url_path='/', static_folder="static")
Bower(app)
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))

@app.route('/<path:path>')
def static_path(path):
  return app.send_static_file(path)

@app.route('/api/add_claim', methods=['POST'])
def add_claim():
    # TODO implement
    return Response(json.dumps([]), mimetype='application/json')

if __name__ == '__main__':
  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port, debug=True)
