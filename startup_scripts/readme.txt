WESmith 01/05/22

##### Raspberry Pi startup scripts #####


### General Comments ###

For the 'rpi_status' server tune the browser to 10.0.0.7:90

For the 'led_web_control' server tune the browser to 10.0.0.7.92

Note that for the 'led_web_control' server the R, G, B LED leads 
(via a 680 ohm or higher resistor on each LED) are connected to RPi GPIO 
pins 18, 23, 24, respectively.


### init.d startup files ###

COPIES (not links) of the web-server scripts in this init.d section are in /etc/init.d/

They are registered to be run on the raspberry pi at startup as follows:

To TURN ON (i.e., register) the script to run at RPi reboot:
    'sudo update-rc.d <script_name> defaults'

        For example:
        'sudo update-rc.d rpi_status defaults'

To TURN OFF (i.e., de-register) the script to run at RPi reboot:
    1) remove the script from /etc/init.d/
    2) then 'sudo update-rc.d <script_name> remove'

These scripts can be tested prior to registering them:

    /etc/init.d/<script_name> start

and killed with 

    /etc/init.d/<script_name> stop

Note that this latter command may need to be repeated. 


01/06/22 UPDATE:
- for unknown reasons, rpi_status.py would not automatically run after reboot, even though
  proper links were set up in /etc/rc*.d/; this may be due to the fact that rpi_status.py is
  a web server, and the network wasn't yet configured when the script was run at startup: TBD
- shifted to use systemd for startup: see below


*** systemd startup script for rpi_status ***

A COPY (not a link) of the web-server script rpi_status.service is in
    /lib/systemd/system/rpi_status.service

It is registered to be run on the raspberry pi at startup as follows:

To TURN ON (i.e., register) the script to run at RPi reboot:
    'sudo systemctl daemon-reload'
    'sudo systemctl enable rpi_status.service'

To TURN OFF (i.e., de-register) the script to run at RPi reboot:
    'sudo systemctl stop    rpi_status.service'
    'sudo systemctl disable rpi_status.service'

These scripts can be tested prior to registering them:
    'sudo systemctl start rpi_status.service'
    'sudo systemctl stop  rpi_status.service'
    
01/06/22 UPDATE:
- this seems to work intermittenly: upon reboot testing the rpi_status.service is sometimes
  running and sometimes not: it may be related to the fact that this is a web-server service, 
  and the network wasn't yet configured when the script was run at startup: TBD
  
- next steps: 
  - dig into the proper configuration of the rpi_status.service script for a web server: 
    systemd is a world unto itself

- will move on to other items at present, this was not a priority, just a training exercise