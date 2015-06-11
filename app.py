import json
from flask import Flask
from flask import render_template


app = Flask(__name__)
app.config.from_object('config')


@app.route('/')
def index():
    return json.dumps("Hello World!")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5001)))
