# findmy-mqtt
This project is a hacky collection of scripts and tools to forward a MQTT location into Apple's FindMy.

### How It Works:
The heavy lifting is done by the [locsim tool](https://github.com/udevsharold/locsim/tree/main). A python script is used to subscribe to an MQTT broker to obtain location data and pass this to locsim.

### You will need:
- a jailbroken iOS device (tested with an iPhone SE 1st Gen)
- a MQTT broker (and a way to host/access it remotely)
- a MQTT client on the device whose location you want to appear in FindMy

## Setting up the iPhone
The iOS device will need to be jailbroken and some packages will need to be installed. The Sileo store was used to install these packages. See here for help [jailbreaking](https://ios.cfw.guide/) and here for help with [Sileo](https://ios.cfw.guide/using-sileo/)

1. Go to Settings and sign into your Apple ID. Make sure you can open FindMy and see your friends locations.

#### NOTE: If you are using something like OpenBubbles to register a phone number with iMessage, doing this will degresiter you! Also make sure to disable iMessage and FaceTime in Settings.

2. While in Settings go to WiFi->[your network] and note your IP address.

3. Install `openssh` in Sileo. It might ask for you to set up a password. Windows users will need to install an SSH client like [PuTTY](https://www.putty.org/)

4. Copy the python script to the iPhone. `scp [path to script] [iphone ip and user]:~`

5. SSH into your jailbroken iPhone. Try using the `mobile` user or the `root` user. Use the password you set up (or if you didn't the default is `alpine`).

6. Update your packages for good measure: `sudo apt update` and `sudo apt upgrade`.

#### NOTE: If you plan on using this phone for a validation relay, now is a good time to install CopperBoy's [relay](https://github.com/OpenBubbles/relayserver). Make sure to first run `sudo launchctl stop identityservicesd` followed by `sudo launchctl disable system/identityservicesd` to prevent registration issues since your Apple ID is logged in. You may also have to repeat these two commands with `com.apple.MobileSMS` if you are experiencing issues with getting degresitered

7. Install python, locsim, and screen `sudo apt install python3 locsim screen`

8. Install pip `python -m ensurepip` and install the mqtt library `python -m pip install paho-mqtt`

9. Open a new screen session (used to keep the script running in the background) `screen -R location`

10. Run the python script! `./forwardLoc.py`

11. Exit screen with Ctrl+A, Ctrl+D and exit SSH with Ctrl+D.

### About the Script
Note that is script is configured to connect to a broker via websockets as that makes hosting one easier. 
- `MQTT_HOST` is the URL of your MQTT broker
- `MQTT_PORT` is the port of your MQTT broker
- `MQTT_USERNAME` and `MQTT_PASSWORD` are used to authenticate
- `TOPIC` is the topic to subscribe to
- `USE_TLS` is used to enable TLS. Do this if your broker has TLS (and if it does not you should probably change that)

### Setting up a broker
I recommend using docker to set up the broker. Here is an example using the Mosquitto broker. It uses host networking and requires a `mosquitto.conf` and password file to be stored in [YOUR_PATH]/mosquitto-conf. See the [mosquitto documentation](https://mosquitto.org/documentation/) for more help.
```
services:
  mosquitto:
    image: eclipse-mosquitto
    container_name: mqtt-owntracks
    network_mode: host
    volumes:
      - [YOUR_PATH]/mosquitto-data:/mosquitto/data
      - [YOUR_PATH]/mosquitto-logs:/mosquitto/logs
      - [YOUR_PATH]/mosquitto-conf:/mosquitto/config
    restart: unless-stopped
```
```
per_listener_settings true

listener 1883 0.0.0.0
allow_anonymous false
password_file /mosquitto/config/passwd_file

listener 8883 0.0.0.0
protocol websockets
allow_anonymous false
password_file /mosquitto/config/passwd_file
```

### Subscribing an Android device to the broker
In my experience, Owntracks is the best way to do this. Unfortunately, it seems to be a kind of buggy app. 