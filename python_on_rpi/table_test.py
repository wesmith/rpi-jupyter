# template_test.py
# WESmith 12/23/21
# cmd line to run: 'sudo python3 template_test.py'

import os
from bottle import Bottle, route, run, template, debug
from datetime import datetime

app = Bottle()

dd1 = ('item 1', 'item 2', 'item 3')

dd2 = (
        ('USER', 'PID', '%CPU', 'START'), 
          ('pi', 21, 15.0, '10:00 AM'),)

@app.route('/')
def index():
    #return template('views/table-template.tpl', name='Table Test')
    return template('views/table-template-2.tpl', 
                    name1='Raspberry Pi 4 Status:',
                    name2='Processes:', list=dd1, table=dd2)

# note: template changes take effect without stopping the server
debug(True) # turn off in production env

# reloader = True: will automatically detect changes in this script
# and rerun the new version wnen it is called again by the browser:
# no need to stop/restart the browser 

app.run(host='0.0.0.0', port=80, reloader=True)



