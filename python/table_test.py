# template_test.py
# WESmith 12/23/21
# cmd line to run: 'sudo python3 template_test.py'

import os
from bottle import Bottle, route, run, template
from datetime import datetime

app = Bottle()

@app.route('/')
def index():
    return template('blank-template.html', name='RPI STATUS')

app.run(host='0.0.0.0', port=80)



