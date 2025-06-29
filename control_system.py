# THIS IS CLASS TEMPLATE FOR CONTROL
# it is imported when passed as argument to starship.py
# ("control_system" in this example)
from starship import IMU, Controller
from math import radians

class GuidanceAndControl:
    def __init__(self):
        print("Hello world control starting...")
        self.trigger_height = 275
        self.trigger_power = 80
        self.trigger_pitch = radians(15)
        self.trigger_time1 = 2.25
        self.trigger_time2 = 1.5
        self.timer = 0
        self.mode=0

    def control(self, imu, controller, fuel, dt):
        print(f"{imu.getPosition().y:.2f}m")

        if imu.getPosition().y <= self.trigger_height and self.mode==0:
            self.mode = 1
            print(f"Switching to mode {self.mode}")
            controller.raptor_left_power = self.trigger_power
            controller.raptor_right_power = self.trigger_power
            controller.raptor_left_pitch = self.trigger_pitch
            controller.raptor_right_pitch = self.trigger_pitch
            controller.rcs_bot_left_power = 100
            controller.rcs_top_left_power = 100
            
        if self.mode>0:
            self.timer += dt
        
        if self.mode == 1 and self.timer > self.trigger_time1:
            self.mode = 2
            print(f"Switching to mode {self.mode}")
            controller.raptor_left_pitch = -self.trigger_pitch
            controller.raptor_right_pitch = -self.trigger_pitch
            self.timer = 0
        
        if self.mode == 2 and self.timer > self.trigger_time2:
            print(f"Switching to mode {self.mode}")
            self.mode = -1
            controller.raptor_left_pitch = 0
            controller.raptor_right_pitch = 0
            controller.raptor_left_power = 100
            controller.raptor_right_power = 0
        
        if fuel <= 0:
            print("OUT OF FUEL")
        

