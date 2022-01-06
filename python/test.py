#!/usr/bin/python3

# test.py
# WESmith 01/05/22
# test that paths are found correctly when running
# from /etc/init.d/ as a startup script

import os, sys, argparse
import rpi_status as ws
from bottle import Bottle, template, static_file, debug

app = Bottle()

css_path = ws.get_css_path()
@app.route('/static/<filename:re:.*\.css>')
def send_css(filename):
    return static_file(filename, root=css_path)

app = Bottle()

foo = 'led_web_control.css'

print('return from send_css({}):\n\n{}\n'.format(foo, send_css(foo)))