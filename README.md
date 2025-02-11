# findmy-mqtt
This project is a hacky collection of scripts and tools to forward a MQTT location into Apple's FindMy.

### How It Works:
The heavy lifting is done by the [locsim tool](https://github.com/udevsharold/locsim/tree/main). A python script is used to subscribe to an MQTT broker to obtain location data and pass this to locsim.

### You will need:
- a jailbroken iOS device (tested with an iPhone SE 1st Gen and iPhone 8 Plus)
- HomeAssistant with External Access setup (Nabu Casa is the easiest but it costs money, I prefer using the Cloudflared method as I already had a domain and is just as easy as NabuCasa)
- a MQTT broker (This can be done within HomeAssistant. I reccomend this video https://www.youtube.com/watch?v=dqTn-Gk4Qeo)

## Setting up the iPhone
The iOS device will need to be jailbroken and some packages will need to be installed. The Sileo store was used to install these packages. See here for help [jailbreaking](https://ios.cfw.guide/) and here for help with [Sileo](https://ios.cfw.guide/using-sileo/)

1. Go to Settings and sign into your Apple ID. Make sure you can open FindMy and see your friends locations.

#### NOTE: If you are using something like OpenBubbles to register a phone number with iMessage, doing this will degresiter you! Also make sure to disable iMessage and FaceTime in Settings.

2. While in Settings go to WiFi->[your network] and note your IP address.

3. Install `openssh` in Sileo. It might ask for you to set up a password. Modern versions of Windows come with SSH. If your version doesn't look into an SSH client such as PuTTY.

4. SSH into your jailbroken iPhone. Try using the `mobile` user or the `root` user. Use the password you set up (or if you didn't the default is `alpine`).

5. Update your packages for good measure: `sudo apt update` and `sudo apt upgrade`.

#### NOTE: If you plan on using this phone for a validation relay, some groundwork needs to be laid down .

First, disable iMessage and FaceTime in the settings on the jailbroken iPhone

Next, run these commands
```sudo launchctl stop identityservicesd```
```sudo launchctl disable system/identityservicesd```
```sudo launchctl unload identityservicesd```
```sudo launchctl stop system/com.apple.MobileSMS```
```sudo launchctl disable system/com.apple.MobileSMS```
Lastly, follow the setup found here https://openbubbles.app/docs/pnr.html#relay-apps

#### NOTE: I inputted resetup OpenBubble's once I verified the script was working as expected. 
You may also have to repeat these commands if you are experiencing issues with getting degresitered


6. Install python, locsim, and screen `sudo apt install python3 locsim screen wget nano`

7. Install pip `python -m ensurepip` and install the mqtt library `python -m pip install paho-mqtt`

8. Download the script using wget `https://raw.githubusercontent.com/versionDefect/findmy-mqtt/refs/heads/main/forwardLoc.py`

9. Configure the script using `nano forwardLoc.py`. Once the variables are set to your liking, hit ctrl + x. Then hit Y and hit enter.
Note that is script is configured to connect to a broker via websockets as that makes hosting one easier. 
- `MQTT_HOST` is the URL of your MQTT broker
- `MQTT_PORT` is the port of your MQTT broker
- `MQTT_USERNAME` and `MQTT_PASSWORD` are used to authenticate
- `TOPIC` is the topic to subscribe to
- `USE_TLS` is used to enable TLS. Do this if your broker has TLS (and if it does not you should probably change that)

TOPIC to `location/findmy` but you can set it to whatever you want, just remember it. 

10. Open a new screen session (used to keep the script running in the background) `screen -R location`

11. Run the python script! `python3 forwardLoc.py`

12. Exit screen with Ctrl+A, Ctrl+D and exit SSH with Ctrl+D.


### Testing
Now that the script is running, we can test it. This documentation is going to describe how to use it in HomeAssistant MQTT but its not required
Go into Settings > Integrations > MQTT > Configure

Next, in the listener, enter # and hit "START LISTENING". This is going to listen to all MQTT Traffic on your network. 

Now, set the topic in the Publish a Packet section to the topic you previously set and for the pay load enter this. 
Note that you can change this lattitude and longitude to whatever you'd like, this will just set your location to a popular area in MN.  

`{
  "lat": "44.974",
  "lon": -93.274",
  "acc": "100",
  "alt": "828",
  "vac": "100",
  "vel": "0",
  "cog": "0"
}`

Hit publish the topic, and examine the device's location. I personally used my Mac's FindMy app but I'm sure you could use the maps app on the device. 
If it worked, Great! We can keep going. If it didn't try to figure out what the error is. Open a GitHub Issue if you need help. 

Now in Home Assistant create a new automation. 
This is the trigger I used. 
<img width="1055" alt="image" src="https://github.com/user-attachments/assets/1dfaeda6-bbcf-4235-b730-07a56874410c" />
This is because if a device's state does not change, it won't consider the device updated and won't trigger. 

You can add conditions but I did not. 

In payload enter this. 

`{
  "lat": {{states.device_tracker.pixel_9_pro.attributes.latitude}},
  "lon": {{states.device_tracker.pixel_9_pro.attributes.longitude}},
  "acc": {{states.device_tracker.pixel_9_pro.attributes.gps_accuracy}},
  "alt": {{states.device_tracker.pixel_9_pro.attributes.altitude}},
  "vac": {{states.device_tracker.pixel_9_pro.attributes.vertical_accuracy}},
  "vel": {{states.device_tracker.pixel_9_pro.attributes.speed}},
  "cog": {{states.device_tracker.pixel_9_pro.attributes.course}}
}`

### NOTE: Replace "pixel_9_pro" with whatever your device's tracker is. 

<img width="1069" alt="image" src="https://github.com/user-attachments/assets/fe7f4123-7b90-4d0b-a266-43fa72f37c9d" />

Once thats entered, Every 5 minutes your jailbroken iPhone's location will be updated to your other device's current location. 

All done! Everything is completed! Enjoy being able to have your close friend's watch you. 
If you want to view other people's location, the only app that is able to do this is OpenBubbles. I reccomend setting it up. 
