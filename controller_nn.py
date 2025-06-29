# THIS IS CLASS TEMPLATE FOR CONTROL
# it is imported when passed as argument to starship.py
# ("control_system" in this example)
import numpy as np

from starship import IMU, Controller
from math import radians
import torch
import torch.nn as nn
from nn_utils import *


class RocketNN(nn.Module):
    def __init__(self, weights=None):
        super(RocketNN, self).__init__()

        self.raptor_min_power = 40
        self.raptor_max_power = 100
        self.raptor_max_pitch = radians(15)

        # x, y, vx, vy, ax, ay, theta, omega, epsilon
        self.fc1 = nn.Linear(9, 64) # IMU state inputs
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 16)
        self.fc4 = nn.Linear(16, 8)  # 4 control outputs

        # 1: rcs_top_left_power, 2: rcs_top_right_power, 3: rcs_bot_left_power, 4: rcs_bot_right_power,
        # 5: raptor_left_power, 6: raptor_right_power, 7: raptor_right_pitch, 8: raptor_left_pitch

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        output = self.fc4(x)
        # 1-4: rcs 0 or 100
        rcs_thrusters = torch.sigmoid(output[:4])
        rcs_thrusters = 100 * (rcs_thrusters>=0.5).float()
        #print('rcs_thrusters', rcs_thrusters)
        # 5-6: raptor from 40 to 100
        raptor_power = self.raptor_min_power + (self.raptor_max_power-self.raptor_min_power) * torch.sigmoid(output[4:6])
        #print('raptor_power', raptor_power)
        # 7-8: raptor angle from -15 to 15
        raptor_angle = torch.tanh(output[-2:]) * self.raptor_max_pitch
        #print('raptor_angle', raptor_angle)

        return torch.cat([rcs_thrusters, raptor_power, raptor_angle])


class GuidanceAndControl:
    def __init__(self, weights=None):
        self.control_nn = RocketNN()

        if weights is not None:
            #print("Assigning weights to control neural network")
            set_model_weights_from_flat(self.control_nn, weights)
        self.commands = np.zeros(8)  # Initialize commands array


    def control(self, imu, controller, fuel, dt):

        #INPUT state
        position = imu.getPosition()
        velocity = imu.getVelocity()
        acceleration =imu.getAcceleration()
        pitch = imu.getPitch()
        rotationalVelocity = imu.getRotationalVelocity()
        rotationalAcceleration = imu.getRotationalAcceleration()
        input = np.array([position[0],
            position[1],
            velocity[0],
            velocity[1],
            acceleration[0],
            acceleration[1],
            pitch,
            rotationalVelocity,
            rotationalAcceleration])

        input_state = torch.tensor(input, dtype=torch.float32)

        commands = self.control_nn(input_state).detach().numpy()
        self.commands = commands

        #OUTPUT state
        #print('commands:', *commands)

        controller.rcs_top_left_power = commands[0]
        controller.rcs_top_right_power = commands[1]
        controller.rcs_bot_left_power = commands[2]
        controller.rcs_bot_right_power = commands[3]
        controller.raptor_left_power = commands[4]
        controller.raptor_right_power = commands[5]
        controller.raptor_right_pitch = commands[6]
        controller.raptor_left_pitch = commands[7]

if __name__ == "__main__":
    control_nn = RocketNN()
    input = torch.tensor([0, 1, 2, 3, 4, 5, 6, 7, 8], dtype=torch.float)
    output = control_nn(input).detach().numpy()
    print(output)
