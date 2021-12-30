# led_web_control.py
# WESmith 12/29/21
# modified from Raspberry Pi Cookbook ed 3, ch_16_web_control.py
# to add cyan, magenta, yellow, white, black LED patterns
# run this with python3 (bottle installed with pip3):
# 'sudo python3 led_web_control.py'

# TODO:
# - make the port number a command-line input
# - put buttons in a table?
# - move button formatting to the CSS sheet


from bottle import Bottle, template, static_file, debug
from gpiozero import LED, Button
import os

css_local_path = '/static/css'
dd = os.popen('pwd')
dirname  = dd.read()[:-1]
css_path = dirname + css_local_path
print('running from: {}\nCSS path: {}'.format(dirname, css_path))

leds = [LED(18), LED(23), LED(24)] # red, green, blue
#switch = Button(25)  #not going to implement this at present

''' not implementing at present
def switch_status():
    if switch.is_pressed:
        return 'Down'
    else:
        return 'Up'
'''

# RPi 4 GPIO PIN MAPPING: red: 18, green: 23, blue: 24
button_names = ['RED', 'GREEN', 'BLUE', 'CYAN', 'MAGENTA', 'YELLOW',
                'WHITE', 'BLACK']

def set_color(n): # WS
    ee = [(1,0,0), (0,1,0), (0,0,1), (0,1,1), (1,0,1), (1,1,0),
          (1,1,1), (0,0,0)] # R, G, B, C, M, Y, W, B
    for i, k in enumerate(ee[n]):
        leds[i].on() if k==1 else leds[i].off()

app = Bottle()
# note: template changes take effect without stopping the server
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

app.run(host='0.0.0.0', port=90, reloader=True) # note: port 90
