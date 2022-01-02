#!/usr/bin/python3

# led_web_control.py
# WESmith 12/29/21
# modified from Raspberry Pi Cookbook ed 3, ch_16_web_control.py
# to add cyan, magenta, yellow, white, black LED patterns
# run this with python3 (bottle installed with pip3):
# 'sudo ./led_web_control.py <port>'  will invoke python3

# TODO:
# - put buttons in a table?


from bottle import Bottle, template, static_file, debug
from gpiozero import LED, Button
import os, sys, getopt, argparse


# RPi4 GPIO pin mapping: red, green, blue
leds = [LED(18), LED(23), LED(24)]

button_names = ['RED',   'GREEN',   'BLUE', 
                'CYAN',  'MAGENTA', 'YELLOW',
                'WHITE', 'BLACK']

def get_port(argv):
    txt = 'Run LED web control server'
    parser = argparse.ArgumentParser(description=txt)
    parser.add_argument('PORT', type=int, 
                        help='port number for the server (required)')
    port = parser.parse_args(argv[1:]).PORT
    print('\nUsing PORT: {}'.format(port))
    return port

def get_css_path(css_local_path='/static/css'):
    dd = os.popen('pwd')
    dirname  = dd.read()[:-1]
    css_path = dirname + css_local_path
    print('\nRunning from: {}\n\nUsing CSS path: {}\n'.\
          format(dirname, css_path))
    return css_path

def set_color(n): # WS
    ee = [(1,0,0), (0,1,0), (0,0,1), (0,1,1), (1,0,1), (1,1,0),
          (1,1,1), (0,0,0)] # R, G, B, C, M, Y, W, B
    for i, k in enumerate(ee[n]):
        leds[i].on() if k==1 else leds[i].off()

port = get_port(sys.argv)        
        
css_path = get_css_path()

app = Bottle()

debug(True) # turn off in production env

@app.route('/static/<filename:re:.*\.css>')
def send_css(filename):
    return static_file(filename, root=css_path)

@app.route('/')
@app.route('/<led_num>')
def index(led_num="n"):
    # set LEDs off (value 7) upon startup
    set_color(7) if led_num == "n" else set_color(int(led_num))
    return template('views/led_web_template.tpl', 
                    name='LED Remote Control',
                    buttons=button_names)

# note: reloader=True: template changes take effect w/o restarting the server
app.run(host='0.0.0.0', port=port, reloader=True)


''' NOTE: not implementing 'switch' in the template at present
switch = Button(25)
def switch_status():
    if switch.is_pressed:
        return 'Down'
    else:
        return 'Up'
'''