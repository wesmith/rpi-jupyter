Raspberry Pi startup scripts:

COPIES (not links) of the web-server scripts in this directory are in /etc/init.d/

They are registered to be run on the raspberry pi at startup as follows:

'sudo update-rc.d <script_name> defaults'

For example:

'sudo update-rc.d rpi_status defaults'

To turn off the script at startup:
- first remove the script from /etc/init.d/
- then type 'sudo update-rc.d <script_name> remove'

These scripts can be tested prior to registering them:

/etc/init.d/<script_name> start

and killed with 

/etc/init.d/<script_name> stop

Note that this latter command may need to be repeated. 

For the 'rpi_status' server tune the browser to 10.0.0.7:90

For the 'led_web_control' server tune the browser to 10.0.0.7.92

Note that for the 'led_web_control' server the R, G, B LED leads 
(via a 680 ohm or higher resistor on each LED) are connected to RPi GPIO 
pins 18, 23, 24, respectively.

WESmith 1/5/22