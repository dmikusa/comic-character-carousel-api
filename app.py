import os
import sys
from subprocess import check_output
from flask import Flask
from flask import render_template

app = Flask(__name__)
app.config.from_object('config')

@app.route('/')
def index():
    return render_template("index.html", vi=sys.version_info)

@app.route('/env')
def env():
    return render_template("env.html", env=os.environ)

@app.route('/spawn')
def spawn(shell=False):
    print("shell: {}", shell)
    output=check_output(['ps', 'auxf']).decode('utf8').split('\n')
    return render_template("spawn.html", output=output)

@app.route('/stdout')
def stdout():
    sys.stdout.write("Hello World!")
    sys.stdout.flush()
    return "Done"

@app.route('/stderr')
def stderr():
    sys.stderr.write("Hello Error!")
    sys.stderr.flush()
    return "Done"

@app.route('/junk')
def junk():
    import junk
    return "Junk"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5001)))
