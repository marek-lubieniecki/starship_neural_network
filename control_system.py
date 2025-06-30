# THIS IS CLASS TEMPLATE FOR CONTROL
# it is imported when passed as argument to starship.py
# ("control_system" in this example)
from starship import IMU, Controller
from math import radians
from .core import ControllerInterface
from typing import Any, Dict

class GuidanceAndControl(ControllerInterface):
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

        # Store current commands for the control method
        self.commands = {
            'raptor_left_power': controller.raptor_left_power,
            'raptor_right_power': controller.raptor_right_power,
            'raptor_left_pitch': controller.raptor_left_pitch,
            'raptor_right_pitch': controller.raptor_right_pitch,
            'rcs_top_left_power': controller.rcs_top_left_power,
            'rcs_top_right_power': controller.rcs_top_right_power,
            'rcs_bot_left_power': controller.rcs_bot_left_power,
            'rcs_bot_right_power': controller.rcs_bot_right_power
        }

    # Implement ControllerInterface abstract methods
    def control(self, sensor_data: Dict[str, Any], dt: float) -> Dict[str, float]:
        """Compute control outputs based on sensor data."""
        # Convert IMU sensor data format to dictionary
        if hasattr(sensor_data, 'getPosition'):
            # Legacy IMU object format
            imu = sensor_data
            sensor_dict = {
                'position': [imu.getPosition().x, imu.getPosition().y],
                'velocity': [imu.getVelocity().x, imu.getVelocity().y],
                'acceleration': [imu.getAcceleration().x, imu.getAcceleration().y],
                'pitch': imu.getPitch(),
                'rot_velocity': imu.getRotationalVelocity(),
                'rot_acceleration': imu.getRotationalAcceleration()
            }
        else:
            sensor_dict = sensor_data

        # Create a mock controller object to use with legacy control method
        mock_controller = Controller()
        
        # Call legacy control method (assuming fuel parameter is available)
        fuel = sensor_dict.get('fuel', 1000)  # Default fuel if not provided
        self.control_legacy(MockIMU(sensor_dict), mock_controller, fuel, dt)
        
        # Return control outputs
        return {
            'raptor_left_power': mock_controller.raptor_left_power,
            'raptor_right_power': mock_controller.raptor_right_power,
            'raptor_left_pitch': mock_controller.raptor_left_pitch,
            'raptor_right_pitch': mock_controller.raptor_right_pitch,
            'rcs_top_left_power': mock_controller.rcs_top_left_power,
            'rcs_top_right_power': mock_controller.rcs_top_right_power,
            'rcs_bot_left_power': mock_controller.rcs_bot_left_power,
            'rcs_bot_right_power': mock_controller.rcs_bot_right_power
        }

    def control_legacy(self, imu, controller, fuel, dt):
        """Legacy control method for backward compatibility."""
        # This is the original control method, renamed
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

    def reset(self) -> None:
        """Reset the controller to initial state."""
        self.timer = 0
        self.mode = 0

    def getParameters(self) -> Dict[str, Any]:
        """Get controller parameters."""
        return {
            'trigger_height': self.trigger_height,
            'trigger_power': self.trigger_power,
            'trigger_pitch': self.trigger_pitch,
            'trigger_time1': self.trigger_time1,
            'trigger_time2': self.trigger_time2
        }

    def setParameters(self, parameters: Dict[str, Any]) -> None:
        """Set controller parameters."""
        if 'trigger_height' in parameters:
            self.trigger_height = parameters['trigger_height']
        if 'trigger_power' in parameters:
            self.trigger_power = parameters['trigger_power']
        if 'trigger_pitch' in parameters:
            self.trigger_pitch = parameters['trigger_pitch']
        if 'trigger_time1' in parameters:
            self.trigger_time1 = parameters['trigger_time1']
        if 'trigger_time2' in parameters:
            self.trigger_time2 = parameters['trigger_time2']


class MockIMU:
    """Mock IMU class to bridge between dictionary and legacy IMU interface."""
    def __init__(self, sensor_data: Dict[str, Any]):
        self.data = sensor_data

    def getPosition(self):
        class Vector2:
            def __init__(self, data):
                self.x = data[0]
                self.y = data[1]
        return Vector2(self.data['position'])

    def getVelocity(self):
        class Vector2:
            def __init__(self, data):
                self.x = data[0]
                self.y = data[1]
        return Vector2(self.data['velocity'])

    def getAcceleration(self):
        class Vector2:
            def __init__(self, data):
                self.x = data[0] 
                self.y = data[1]
        return Vector2(self.data['acceleration'])

    def getPitch(self):
        return self.data['pitch']

    def getRotationalVelocity(self):
        return self.data['rot_velocity']

    def getRotationalAcceleration(self):
        return self.data['rot_acceleration']
        

