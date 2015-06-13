import os
import json
import uuid
import requests
import hashlib
import logging
import wrapt
from timeit import default_timer
from flask import Flask
from flask import request
from flask import render_template


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s')
logging.getLogger('requests').setLevel(logging.DEBUG)
log = logging.getLogger('ccc-api')


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')


@wrapt.decorator
def time_request(wrapped, instance, args, kwargs):
    start = default_timer()
    r = wrapped(*args, **kwargs)
    log.info('Request duration [%s]', (default_timer() - start))
    return r


def generate_auth_params():
    req_id = uuid.uuid1().hex
    req_data = req_id + app.config['PRIVATE_KEY'] + app.config['PUBLIC_KEY']
    req_hash = hashlib.md5(req_data).hexdigest()
    return {
        'ts': req_id,
        'hash': req_hash,
        'apikey': app.config['PUBLIC_KEY']
    }


@time_request
def list_characters(limit=20, offset=0, orderBy='name'):
    start = default_timer()
    params = generate_auth_params()
    params['limit'] = limit
    params['offset'] = offset
    params['orderBy'] = orderBy
    r = requests.get(
        '%s/v1/public/characters' % app.config['API'], params=params)
    if r.status_code == 200:
        resp = r.json()
        result = {
            'copyright': resp['copyright'],
            'attributionText': resp['attributionText'],
            'offset': resp['data']['offset'],
            'limit': resp['data']['limit'],
            'total': resp['data']['total'],
            'count': resp['data']['count'],
            'cc': []
        }
        log.info('Found %d characters', result['count'])
        for item in resp['data']['results']:
            c = {
                'id': item['id'],
                'name': item['name'],
                'description': item['description'],
                'urls': item['urls'],
                'thumbnail': None
            }
            if hasattr(item['thumbnail'], 'keys'):
                c['thumbnail'] = "%s/portrait_uncanny.%s" % (
                    item['thumbnail']['path'], item['thumbnail']['extension'])
            result['cc'].append(c)
        return result
    else:
        log.error('HTTP Code [%d]', r.status_code)
        return []


@app.route('/')
def index():
    return json.dumps(
        list_characters(
            limit=request.args.get('limit', 20),
            offset=request.args.get('offset', 0),
            orderBy=request.args.get('orderBy', 'name')))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5001)))
