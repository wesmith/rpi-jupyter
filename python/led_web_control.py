# led_web_control.py
# WESmith 12/29/21
# modified from Raspberry Pi Cookbook ed 3, ch_16_web_control.py
# to add cyan, magenta, yellow, white, black LED patterns
# run this with python3 (bottle installed with pip3):
# 'sudo python3 led_web_control.py'


from bottle import Bottle, template, debug, static_file
from gpiozero import LED, Button

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

def html_for_led(led_number):
    i = str(led_number)
    result = " <input type='button'" +\
             " onClick='changed(" + i + ")'" +\
             " value='" + button_names[led_number] + "'/>"
             #" value='LED " + i + "'/>"
    return result

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
        
    response = "<script>"
    response += "function changed(led)"
    response += "{"
    response += "  window.location.href='/' + led"
    response += "}"
    response += "</script>"
    
    response += '<h1>GPIO Control</h1>'
    #response += '<h2>Button=' + switch_status() + '</h2>'
    response += '<h2>LEDs</h2>'
    for k in range(8):
        response += html_for_led(k)
    return response

app.run(host='0.0.0.0', port=90, reloader=True) # note: port 90
