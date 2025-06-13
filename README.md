Full motion flight simulator project using inputs from X-Plane.
Uses Electrak HD linear actuators with CANopen interface.

To Do:
Test sending and receiving CAN messages to control actuators with electrak.py
Validate input data received from X-Plane using xpc and Get_data.py
Validate calculations in geometry.py and washout.py
Validate platform and actuator measurements in main.py
Write script to Convert geometry calculations to actuator movement values
Update main.py to use electrak.py to send and receive CAN messages to/from actuators