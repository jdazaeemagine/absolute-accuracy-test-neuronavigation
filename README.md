# Stimguide automated accuracy test
Based on the .json exported file from the Horizon API, the test asses the accuracy of the position and rotation/tilt values on the stimguide system according to a calibration board with fixed coil positions


### Physical steps to obtain the .json exported files from Horizon API
0. Place the coil on the exact Motor Target position marked as number 1
1. Open Stimguide and Horizon API
2. (On Stimguide) Go to settings and select "Use HorizonAPI"
3. (On Horizon API) Click on the play button.
4. Using the trigger button, send a stimulus right on Motor target position. 
5. (On Stimguide) Select this stimulus and set this as Motor target.
6. Place the coil on the exact Threatment target position marked as number 2
7. 4. Using the trigger button, send a stimulus right on threatment target position. 
8. (On Stimguide) Select this stimulus and set this as Threatment target.
9. Once targets has been stablished, proceed to threatment session.
10. Stimulate on the threatment position marked with number 2 which is displaced on the X-axis 0.055 m.
11. Stimulate on the threatment position marked with number 3 which is displaced on the Y-axis X m.
12. Stimulate on the threatment position marked with number 4 which is rotated over the same plane as the motor position X degrees.
13. Stimulate on the threatment position marked with number 5 which is tilted over the plane X degrees.
14. Export the .json file from the Horizon API.

The undefined values (above mentioned as X) are specified on the config.xml file.

### Steps to configure and run the script.

1. Download the repository or clone it.
2. (Wether the config.xml file is not available for the calibration used) Change values of configuration file as follows:
  - "Motor_Position_X", "Motor_Position_Y", "Motor_Position_Z": this values are the coordinates (x,y,z) of the coil central point on its motor position (marked as number 1)
  - "Treatment_Target_Displaced_Position_X": this value define the displacement on the X-axis from the motor target to the threatment target (marked as number 2). As aforementioned, this value is 0.055 mm (value defined on stimguide)
  - "Displaced_Position_Y": this value represent the displacement on the Y-axis from the motor target to the position marked as number 3. 
  - "Rotation_Angle": this value define the rotation difference between the motor position and the position marked as number 4. 







