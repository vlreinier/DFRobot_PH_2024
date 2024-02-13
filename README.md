# DFRobot_PH_2024
An updated Python implementation for reading and calibrating the PH sensor from DFRobot.
This class uses a JSON file to store calibration data.

## Usage:

1. Copy the file and import the module `DFRobotPHSensor`
2. Create a class instance `ph_sensor = DFRobotPHSensor()`
3. Read the PH value using the mV value from the sensor `current_ph = ph_sensor.read_ph(mv=1515)`

## Calibration

1. Calibrate the PH sensor with `ph_sensor.auto_calibrate(mv=1515)`
