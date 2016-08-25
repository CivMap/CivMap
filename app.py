import os
import json
from flask import Flask, Response, request

app = Flask(__name__)
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))

@app.route('/<path:path>')
def static_path(path):
  return app.send_static_file(path)

@app.route('/todos.json', methods=['GET', 'POST'])
def todo():
    todos = []

    if request.method == 'POST':
        todos = request.get_json()

    return Response(json.dumps(todos), mimetype='application/json')

if __name__ == '__main__':
  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port, debug=True)
