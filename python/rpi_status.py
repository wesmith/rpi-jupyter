# rpi_status.py
# WSmith 12/22/21
# run this with python3 (bottle installed with pip3)

import os, sys
import vcgencmd as vc
import RPi.GPIO as gpio
from bottle import Bottle, route, run, template, debug, static_file
from datetime import datetime

css_local_path = '/static/css'

dd = os.popen('pwd')
dirname  = dd.read()[:-1]
css_path = dirname + css_local_path

print('running from: {}\nCSS path: {}'.format(dirname, css_path))

vccmd = vc.Vcgencmd()

def get_temp():
    temp_C = vccmd.measure_temp()
    temp_F = temp_C * 9./5. +32.0
    return ["CPU TEMP", "{:0.2f} deg C, {:0.2f} deg F".\
            format(temp_C, temp_F)]

def get_time():
    return ["TIME", "{:%Y-%m-%d %H:%M:%S}".format(datetime.now())]

def get_load_average():
    one, five, fifteen = os.getloadavg()
    return ["PROCESS AVERAGES", "{} (1m), {} (5m), {} (15m)".\
            format(one, five, fifteen)]

def get_uptime():
    dd = os.popen('/usr/bin/uptime -p')
    return ["UPTIME", "{}".format(dd.read()[3:-1])]

def get_freq(obj='arm'):
    # obj = arm, core
    return ["FREQ of '{}'".format(obj), 
            "{:0.3f} GHz".format(vccmd.measure_clock(obj)/1.e9)]
'''
def get_processes(num=5): # this version returns a text block
    # see unix.stackexchange.com #13968 : sorting on cpu%
    # top result is the header, so get n + 1
    cmd = '/bin/ps aux --sort=-pcpu | head -n {}'.format(num + 1)
    dd  = os.popen(cmd)
    txt = dd.read()
    # [:-1] gets rid of empty list after last \n
    out = [k.split() for k in txt.split('\n')][:-1]
    fields = [0, 1, 2, 3, 8, 9, 10] # limit the output fields
    txt = []
    header = ''
    for k in fields:
        header += out[0][k] + '\t'
    txt.append(header)
    for j in range(1, len(out) - 1):
        process = ''
        for k in fields: # split affects only the last field
            process += out[j][k].split('/')[-1] + '\t'
        txt.append(process)
    return txt
'''
def get_processes(num=5, fields=[0, 1, 2, 3, 8, 9, 10]): 
    # this version returns a list of lists
    # num    = number of processes to display
    # fields = desired field to display from 'ps aux' output
    # see unix.stackexchange.com #13968 : sorting on cpu%
    # top result is the header, so get n + 1
    cmd = '/bin/ps aux --sort=-pcpu | head -n {}'.\
            format(num + 1)
    dd  = os.popen(cmd)
    txt = dd.read()
    # [:-1] gets rid of empty list after last \n
    out = [k.split() for k in txt.split('\n')][:-1]
    short = []
    for j in range(len(out)): # split affects only the last field
        short.append([out[j][k].split('/')[-1] for k in fields])
    return short

# FUNCTION index() inputs
# function outputs to display
nproc  = 10  # number of processes to display
fns = [get_time, get_temp, get_load_average, get_uptime, get_freq]
fields = [0, 1, 2, 3, 8, 9, 10] # 'ps aux' output fields to display
fields = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

app = Bottle()
# note: template changes take effect without stopping the server
debug(True) # turn off in production env

@app.route('/static/<filename:re:.*\.css>')
def send_css(filename):
    return static_file(filename, root=css_path)

@app.route('/')
def index():
    dd1 = [k() for k in fns]
    dd2 = get_processes(num=nproc, fields=fields)
    return template('views/table-template-2.tpl', 
                    name1='Raspberry Pi 4 Status:',
                    name2='Top {} %CPU Processes:'.\
                    format(nproc), 
                    table1=dd1, table2=dd2)

# reloader = True: will automatically detect changes in this script
# and rerun the new version wnen it is called again by the browser:
# no need to stop/restart the browser 
app.run(host='0.0.0.0', port=80, reloader=True)
