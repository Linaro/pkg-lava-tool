import os
import sys
import yaml

from flask import (
    Flask,
    request,
)

app = Flask(__name__)

aliases = {
    'ok': 200,
    'forbidden': 403,
    'notfound': 404,
}

fixed_response = None

@app.route('/exit')
def exit():
    # http://werkzeug.pocoo.org/docs/serving/#shutting-down-the-server
    if not 'werkzeug.server.shutdown' in request.environ:
        raise RuntimeError('Not running the development server')
    request.environ['werkzeug.server.shutdown']()
    return ""

@app.route('/<status_code>', methods=['GET', 'POST'])
def reply(status_code):

    status = int(aliases.get(status_code, status_code))

    headers = {}
    for k,v in request.headers:
        headers[k] = v

    response_file = os.path.join(os.path.dirname(__file__), 'fixed_response.txt')
    if os.path.exists(response_file):
        response = open(response_file).read()
        os.remove(response_file)
    else:
        response = yaml.dump(
            {
                'status': status,
                'headers': headers,
                'body': request.form.keys(),
                'query': dict(request.args),
            },
            encoding='utf-8',
            default_flow_style=False,
        )
    return response, status, { 'Content-Type': 'text/plain' }

@app.route('/', methods=['GET','POST'])
def root():
    return reply(200)

if __name__ == '__main__':
    app.run(debug=('DEBUG' in os.environ))
