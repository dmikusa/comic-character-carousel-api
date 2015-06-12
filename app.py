import os
import json
import uuid
import requests
import hashlib
import logging
from flask import Flask
from flask import render_template


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s')
logging.getLogger('requests').setLevel(logging.DEBUG)
log = logging.getLogger('ccc-api')



app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')


def list_characters():
    req_id = uuid.uuid1().hex
    req_data = req_id + app.config['PRIVATE_KEY'] + app.config['PUBLIC_KEY']
    req_hash = hashlib.md5(req_data).hexdigest()
    params = {
        'ts': req_id,
        'hash': req_hash,
        'apikey': app.config['PUBLIC_KEY']
    }
    r = requests.get(
        '%s/v1/public/characters' % app.config['API'], params=params)
    if r.status_code == 200:
        data = r.json()['data']
        cc = []
        log.info('Found %d characters', len(data['results']))
        for item in data['results']:
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
            cc.append(c)
        return cc
    else:
        log.error('HTTP Code [%d]', r.status_code)
        return []


@app.route('/')
def index():
    return json.dumps(list_characters())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5001)))
