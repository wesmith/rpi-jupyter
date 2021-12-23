# rpi_status.py
# WSmith 12/22/21
# run this with python3 (bottle installed with pip3)

import os
import vcgencmd as vc
import RPi.GPIO as gpio
from bottle import route, run, template
from datetime import datetime

vccmd = vc.Vcgencmd()

def get_temp():
    temp_C = vccmd.measure_temp()
    temp_F = temp_C * 9./5. +32.0
    return "CPU TEMP{:0.2f} deg C, {:0.2f} deg F".\
            format(temp_C, temp_F)

def get_time():
    return "TIME: {:%Y-%m-%d %H:%M:%S}".format(datetime.now())

def get_load_average():
    one, five, fifteen = os.getloadavg()
    return "PROCESS AVERAGES: {} (1m), {} (5m), {} (15m)".\
            format(one, five, fifteen)

def get_uptime():
    dd = os.popen('/usr/bin/uptime -p')
    return "UPTIME: {}".format(dd.read()[3:-1])

def get_freq(obj='arm'):
    # obj = arm, core
    return "FREQ of '{}': {} GHz".\
        format(obj, vccmd.measure_clock(obj)/1.e9)

def get_processes(num=5):
    # see unix.stackexchange.com #13968 : sorting on cpu%
    # top result is the header, so get n + 1
    cmd = '/bin/ps aux --sort=-pcpu | head -n {}'.format(num + 1)
    dd  = os.popen(cmd)
    txt = dd.read()
    out = [k.split() for k in txt.split('\n')]
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


@route('/')
def index(nn='RPi Status:'):
    dt = get_time()
    tc = get_temp()
    up = get_uptime()
    fr = get_freq()
    la = get_load_average()
    pr = get_processes(3) # very klugey how this handled at present
    return template('<b>' +\
                    '<p>{{nn}}</p>' +\
                    '<p>{{dt}}</p>' +\
                    '<p>{{tc}}</p>' +\
                    '<p>{{up}}</p>' +\
                    '<p>{{fr}}</p>' +\
                    '<p>{{la}}</p>' +\
                    '<p>{{p0}}</p>' +\
                    '<p>{{p1}}</p>' +\
                    '<p>{{p2}}</p>' +\
                    '<p>{{p3}}</p>' +\
                    '</b>',
                    nn=nn, 
                    dt=dt, 
                    tc=tc,
                    up=up,
                    fr=fr,
                    la=la,
                    p0=pr[0],
                    p1=pr[1],
                    p2=pr[2],
                    p3=pr[3],
                   )

run(host='0.0.0.0', port=80)
