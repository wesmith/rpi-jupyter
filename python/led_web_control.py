#!/usr/bin/python3

# led_web_control.py
# WESmith 12/29/21
# modified from Raspberry Pi Cookbook ed 3, ch_16_web_control.py
# to add cyan, magenta, yellow, white, black LED patterns
# run this with python3 (bottle installed with pip3):
# 'sudo ./led_web_control.py <port>'  will invoke python3


from bottle import Bottle, template, static_file, debug
from gpiozero import LED, Button
import os, sys
import rpi_status as ws # WS module

# RPi4 GPIO pin mapping: red, green, blue
RGB = [18, 23, 24]
leds = [LED(k) for k in RGB]
button_names = ['RED',   'GREEN',   'BLUE', 
                'CYAN',  'MAGENTA', 'YELLOW',
                'WHITE', 'BLACK']

def set_color(n): # WS
    ee = [(1,0,0), (0,1,0), (0,0,1),
          (0,1,1), (1,0,1), (1,1,0),
          (1,1,1), (0,0,0)] # R, G, B, C, M, Y, W, B
    for i, k in enumerate(ee[n]):
        leds[i].on() if k==1 else leds[i].off()

def run(argv, debug_on=True,
        tpl_file='led_web_control.tpl',
        css_file='led_web_control.css',
        tpl_local_path='/views',
        css_local_path='/static/css'):
        
    port = ws.get_port(argv=argv)

    app = Bottle()

    debug(debug_on) # turn off in production env

    tpl_path, css_path = ws.get_paths(tpl_local_path, css_local_path)
    @app.route('/static/<filename:re:.*\.css>')
    def send_css(filename):
        return static_file(filename, root=css_path)

    fns = [ws.get_time, ws.get_temp]

    @app.route('/')
    @app.route('/<led_num>')
    def index(led_num='7'): # default to 'black': all lights off
        dd1 = [k() for k in fns]
        txt1 = 'LED Remote Control on Port {}'.format(port)
        txt2 = 'R, G, B LEDs connected to GPIOs {}, {}, {}'.\
                format(*RGB)
        txt2 += ' (use a 680 ohm resistor for each LED)'
        set_color(int(led_num))
        dd1.append(["LIGHT STATUS", button_names[int(led_num)]])
        dd1[0][0] = 'TIME BUTTON PUSHED' # modify name from import
        return template(os.path.join(tpl_path, tpl_file),
                        css_file=css_file,
                        name1=txt1, name2=txt2,
                        buttons=button_names,
                        table1=dd1)

    # reloader = True: 
    # will automatically detect changes in this script and
    # rerun the new version wnen it is called again by the browser:
    # no need to stop/restart the browser
    app.run(host='0.0.0.0', port=port, reloader=True)

if __name__=="__main__":

    run(sys.argv)
