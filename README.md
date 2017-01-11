Smart Lights Over Voice Control
============================
###Usage
1. Clone the repository
> git clone https://futebolUFMG@bitbucket.org/futebolUFMG/voice_control.git

2. Copy the files to each agent
> cd voice_control<br />
> scp -r newconn/sensor pi@**_IP_RASPBERRY_SENSOR_**:~
> scp -r newconn/VM **_USER_**@**_IP_VM_**:~
> scp -r newconn/Actuator pi@**_IP_RASPBERRY_ACTUATOR_**:~
 
3. On each agent, execute the main files
* Raspberry (Sensor):
> cd newconn/sensor
> python sensor.py [--log-level **_LOG_LEVEL_**] [--verbose]

* VM (speech recognition)
PORT_RECV and PORT_SEND default to 5007 and 5008 respectively.
> cd newconn/sensor
> python converter.py [--port-recv **_PORT_RECV_**] [--port-send **_PORT_SEND_**] [--log-level **_LOG_LEVEL_**] [--verbose]

* Raspberry (Actuator):
> cd newconn/sensor
> python actuator.py [--log-level **_LOG_LEVEL_**] [--verbose]

* The values for **_LOG_LEVEL_** are [error,warning,info,debug,notset]
</p>

#####**Commands:**
* This system recognizes the following type of commands:
> _LIGHTS_ ?(1|2|3) (ON|OFF) ?(?(_COLOR_) **_COLOR_NAME_**) ?(BRIGHTNESS **_BROPTIONS_**)

* The options for **_COLOR_NAME_** are: [red, blue, yellow, green, pink, white]
* The options for **_BROPTIONS_** are: [up, down, low, medium, high]
 * _Up_ and _Down_ respectively increases and decreases the current brightness value in 20%.
 * _Low_ changes the brightness value to 0%. (That does not mean the lights are turned off, it means the brightness is dimmed to the minimum value it can achieve)
 * _Medium_ changes the brightness value to 50%.
 * _High_ changes the brightness value to 100%.

