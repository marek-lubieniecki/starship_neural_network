# Space Challenge 1

## Objective
Land satisfying following conditions:
- x = (20m, 20m)
- y = 0m
- pitch < 5 deg
- vx,vy < 1m/s

Create class `GuidanceAndControl` with method `def control(self, imu, controller, fuel, dt)` and pass filename (without `.py`) as argument to `starship.py`.

Starting point: [120, 400].

## Running code
To run your controller in simulation:
```
python3 starship.py <your_file_without_py>
```

To run simulation with keyboard controls:
```
python3 starship.py 
```

## Details
In `Space Challenge 1`, a 2D simulation of landing starship is made using euler integration at 60Hz. There is no aerodynamics or fluids sloshing. Inertial Measurements Unit is 100% accurate, engines are 100% reliable and accurate.
`control_system.py` is provided as a demonstration of providing control.

### Starship
Is a 100ton rigid body with two 1.5ton, 1920kN thrust Raptor engines and four Reaction Control System (RCS) 20kg, 50kN force thrusters. And 5tons of fuel (CH4 and LOX combined) used for both main engines and RCS.

### Inertial Measurements Unit - IMU
IMU class is a middleman between actual simulation data and user code.
Use this class to get current state of starship's center.
```
class IMU:
""" vectormath.Vector2 """
    def getPosition()
    def getVelocity()
    def getAcceleration()

""" float """
    def getPitch()
    def getRotationalVelocity()
    def getRotationalAcceleration()
```

### Controller
Controller is a container holding values of control inputs.
```
class Controller:
        self.rcs_top_left_power
        self.rcs_top_right_power
        self.rcs_bot_left_power
        self.rcs_bot_right_power
        self.raptor_left_power
        self.raptor_right_power
        self.raptor_right_pitch
        self.raptor_left_pitch
```
RCS stands for reaction control system - little thrusters on sides.
Raptors are main engines with variable pitch and power.

### Main engines
Thrust: 1920 kN
Power: 40% - 100%
Ignition time: 1s
Gimbal: +/- 15 degrees

Ignition time is the time needed to go from 0% (OFF) to 40%-100% (ON). If you turn them on, its best to leave them on.

### RCS
Thrust: 50kN
Power: 100%
Ignition time: 10ms
Gimbal: none

Use these to support rotation or arrest sideways motion.

