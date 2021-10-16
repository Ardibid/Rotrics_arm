# Rotrics DexArm Dashboard

![demo](/media/demo.gif?raw=true)

A series of tools to work with [Rotrics DexArm]("https://www.rotrics.com/") robotic arms.
The dash app interface the robot through a web app.



## Guides

### Running the app

To run the app, run this script from the same folder that the drawing_app.py exists and then access the app from your browser:

```
python pyArm.py -mode local 
```

![demo](/media/run_app.gif?raw=true)


There are three modes of running the app:

* **local**: runs on the local machine, you can access it on http://127.0.0.1:8050/
* **debug**: runs on the local machine, with debugging options. you can access it on http://127.0.0.1:8050/
* **remote**: runs on the local machine as a server, you can access it from other deives on the same network on http://0.0.0.0:8050/, replace the 0.0.0.0 part with your server machine's IP address, i.e., http://192.168.86.34:8050/ 

### Setup

1. After starting the app, make sure the robot is on and connected
2. Find the robot COM port
3. Use the Port drop down menu to select the right port, it is by default set to COM3
4. Hit connect and wait for the robot connection message to show up
5. If you are using a slider track, check the option and if it is necessary initialize the slider track

![demo](/media/start_running.gif?raw=true)

* To check if your marker is at the correct height, hit **Touch Paper**, the robot moves down to the paper level and stays there. Adjust your marker and hit the button again. The robot goes back to default z height.

* To slighly adjust the height without actually moving your marker, use Offset slider. 

* If you are not satisfied with the range of thickneses that your brush or marker makes, change the Pressure slider to let the robot push the marker further down. Larger numbers mean more pressure and thicker lines on p=1.0.

* In case of emergency hit STOP to stop the robot. Please be noted that the robot will not stop immediately, but (probably) after finishing its last buffered action.

## Drawing Modes

There are two drawing modes:

### Drawing from canvas

In this mode, user draws something directly on the canvas and hits Draw Now to start the drawing on the robot.

* The drawings will be directly save in a JSON file located at `./data/path_data_test.json`, then the app reads it from that file
* The canvas can be cleared using Clear Canvas button. This also wipes the JSON file data and replaces it with the data for a rectangle
* No presure nor rotation is implemented for the canvas drawing mode.
![demo](/media/canvas_draw.gif?raw=true)

### Drawing from JSON file:
In this mode you can drag and drop a JSON file in the format below, and the app will plot it for your inspection. After that you can run it on the robot.

By default, the Draw Now button draws the content of  `./data/path_data.json`. If you have used the Canvas, this file still holds your drawing.
![demo](/media/json_draw.gif?raw=true)

## Data Format
Drawing data must be saved as a JSON file. For each target there are 4 values:
1. **x**: x value of the target, when using the track, the x value will be used as the **e** vakue to move the robot across the track (X asix is along the track)
2. **y**: y value of the target, very small and very large y values are not accessible for the robot. 
3. **a**: the rotation value for the rotary module in degrees (disabled as of now, the module is not reliable)
4. **p**: the pressure value, this number multiplied with the pressure factor will be subtracted from the z_safe vale. The larger p values means the marker or brush will be pushed further over the paper and it makes wider strokes.

```json
{
   "drawing":{
      "strokes":[
         [
            {
               "x":50,
               "y":250,
               "a":15,
               "p":0.4
            },
            {
               "x":75,
               "y":250,
               "a":90,
               "p":0.5
            },
            {
               "x":50,
               "y":300,
               "a":125,
               "p":1.0
            }
         ],
         [
            {
               "x":-50,
               "y":250,
               "a":45,
               "p":0.2
            },
            {
               "x":-75,
               "y":250,
               "a":45,
               "p":0.3
            }
         ]
      ]
   }
}
```

## Technicals 

### Dependencies
(the toolkit is developed with the versions mentioned here, use other versions at your own risk)

* pydexarm
* [plotly](https://pypi.org/project/plotly/): 4.14.3
* [dash](https://pypi.org/project/dash/): 1.19.0
* [dash_core_components](https://pypi.org/project/dash-core-components/): 1.15.0
  * dash_html_components: 1.1.2
  * dash_bootstrap_components: 0.12.0250
* [numpy](https://numpy.org/): 1.20.2
* [pyserial](https://pypi.org/project/pyserial/): 3.5 
* re: 2.2.1

### Known Issues

#### Connections

* If there is an issue with the serial connection, reset the robot (with the physical button on its back) and reset your server, then connect it again.
* Once on the sliding track, the robot stands so high that it cannot reach to targets on the surface of the table on which the track is placed. You need to have a platform to raise your work even higher than the robot's base plate.
* Running the app on the debug mode means that Dash backend will randomly restart your server, please avoid using that mode!
* Runnint the app remotely means that all your devices need to be on the same network as the server. Check your firewall, network search settings, wifi architecture, etc. if you cannot see the app page. 
* You probably cannot run this app remotely on CMU network, there are safety measures on that network that prevents you from it. You need to reach out to IT team.

#### Slider Track

* The slider track initiation is a hit-and-miss. Probably before using it you should restart the robot, reset your server, and move the robot slightly on the track towards the positive side. Otherwise, the slider track hits the zero point (physically) and tries to go beyond it, resulting in a strong vibration all over the robot.
* Never address the robot to go to negative **e** values, this will result in the same shaking issue.

#### Rotary Module

* The rotary module is different from the other joints. It is worth mentioning that the rotary module works separately from the other 3 joints, it should be called separately after a motion command over the other three axes is cleared. 
* The rotary module only rotates at the beginning or at the end of a motion. This means that when the second axis rotates, the orientation of the pen/marker/brush will also change, until it gets corrected at the end of motion. So, basically worthless for motions that require maintain a specific rotation across a motion.

It doesn't work as intended on the Python API. It works in Rotrics Studio, but the Python API somehow doesn't work and ignores the rotation commands if it is sandwiched between move commands.

### To do

* [x] Handle the multi inputs, as of now if you remove the pencil from the surface and put it back, it will break the dashboard

* [x] Inegrating the [rail kit](https://www.rotrics.com/products/sliding-rail-kit)

* [x] Integrating the pressure values

* [x] Reading drawings in the JSON format

* [ ] ~~Inegrating the [rotary module](https://www.rotrics.com/products/rotary-kit) Canceled due to technical issues~~

--- 
By Ardavn Bidgoli, Summer 2021
