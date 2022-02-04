#!/usr/bin/python3

# rpi_status.py
# WSmith 12/22/21
# run this with python3 (bottle installed with pip3):
# 'sudo ./rpi_status.py <port>' will invoke python3

import os, sys, argparse
import vcgencmd as vc
import RPi.GPIO as gpio
from bottle import Bottle, template, debug, static_file
from datetime import datetime


vccmd = vc.Vcgencmd()

def get_port(argv=sys.argv):
    txt     = 'Run rpi_status web server'
    helptxt = 'port number for the server (required)'
    parser = argparse.ArgumentParser(description=txt)
    parser.add_argument('PORT', type=int, help=helptxt)
    port = parser.parse_args(argv[1:]).PORT
    print('\nUsing PORT: {}'.format(port))
    return port

def get_paths(tpl_local_path, css_local_path):
    # get path to script, no matter where it is run from
    dirname = os.path.dirname(os.path.realpath(__file__))
    tpl_path = dirname + tpl_local_path
    css_path = dirname + css_local_path
    print('\nScript in: {}\n\nUsing CSS path: {}\n'.\
          format(dirname, css_path))
    return tpl_path, css_path

def get_temp():
    temp_C = vccmd.measure_temp()
    temp_F = temp_C * 9./5. + 32.0
    txt = '{} deg C, {} deg F'.format(int(temp_C), int(temp_F))
    return ["CPU TEMP", txt]

def get_time():
    return ["TIME", "{:%Y-%m-%d %H:%M:%S}".\
            format(datetime.now())]

def get_load_average():
    one, five, fifteen = os.getloadavg()
    txt = '{} (1m), {} (5m), {} (15m)'.format(one, five, fifteen)
    return ["PROCESS AVERAGES",txt]

def get_uptime():
    dd = os.popen('/usr/bin/uptime -p')
    return ["UPTIME", "{}".format(dd.read()[3:-1])]

def get_freq(obj='arm'):
    # obj = arm, core
    return ["FREQ of '{}'".format(obj), 
            "{:0.3f} GHz".format(vccmd.measure_clock(obj)/1.e9)]

def get_processes_in_list(num=5, fields=[0, 1, 2, 3, 8, 9, 10]):
    # this version returns a list of lists: use in run()
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
    for j in range(len(out)): 
        # split affects only the last field
        short.append([out[j][k].split('/')[-1] for k in fields])
    return short

def get_processes_in_text(num=5):
    # this version returns a text block
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


def run(argv, nproc=10, 
        fields=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        debug_on=True,
        tpl_file='rpi_status.tpl',
        css_file='rpi_status.css',
        tpl_local_path='/views',
        css_local_path='/static/css'):
    '''
    nproc:  number of processes to display
    fields: 'ps aux' output fields to display (default: all fields)
            (e.g., for a subset: fields = [0, 1, 2, 3, 8, 9, 10])
    '''
    port = get_port(argv=argv)

    app = Bottle()

    debug(debug_on) # turn off in production env

    tpl_path, css_path = get_paths(tpl_local_path, css_local_path)
    @app.route('/static/<filename:re:.*\.css>')
    def send_css(filename):
        return static_file(filename, root=css_path)

    # fns list includes function outputs to display
    fns = [get_time, get_temp, get_load_average,
           get_uptime, get_freq]

    @app.route('/')
    def index():
        dd1 = [k() for k in fns]
        dd2 = get_processes_in_list(num=nproc, fields=fields)
        return template(os.path.join(tpl_path, tpl_file),
                        css_file=css_file,
                        name1='Raspberry Pi 4 Status on Port {}'.\
                        format(port),
                        name2='Top {} %CPU Processes:'.\
                        format(nproc),
                        table1=dd1, table2=dd2)
    # reloader = True: 
    # will automatically detect changes in this script and
    # rerun the new version wnen it is called again by the browser:
    # no need to stop/restart the browser
    app.run(host='0.0.0.0', port=port, reloader=True)


if __name__=="__main__":

    run(sys.argv)
