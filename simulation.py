from starship import World
import matplotlib.pyplot as plt
import copy





class Simulation:
    def __init__(self, world, rocket, config):
        self.world = world
        self.rocket = rocket
        self.config = config
        self.sim_results = None

    def simulate(self):
        sim_results = SimulationResults()
        while not self.config.isFinished(self.rocket.model.state):
           # print(World.time, self.rocket.model.state.position)
            sim_results.add_state(World.time, self.rocket.model.state)
            sim_results.add_commands(self.rocket.control_system.commands)
            self.rocket.update()
        World.time = 0
        self.sim_results = sim_results

        return sim_results


class Config:
    def __init__(self, isFinished):
        self.isFinished = isFinished


class SimulationResults:
    def __init__(self):
        self.time = []
        self.state_list = []
        self.command_list = []

    def add_state(self, time, state):
        self.time.append(time)
        self.state_list.append(copy.deepcopy(state))

    def add_commands(self, commands):
        self.command_list.append(commands)

    def get_property(self, state_property, time):
        for i in range(len(self.time) - 1):
            if self.time[i] <= time <= self.time[i + 1]:
                t1, t2 = self.time[i], self.time[i + 1]
                state1, state2 = self.state_list[i], self.state_list[i + 1]
                value1, value2 = getattr(state1, state_property), getattr(state2, state_property)
                # Linear interpolation
                return value1 + (value2 - value1) * ((time - t1) / (t2 - t1))
        raise ValueError("Time out of bounds")

    def plot_property(self, state_property):

        values = [getattr(state, state_property) for state in self.state_list]
        plt.plot(self.time, values)
        plt.xlabel('Time (s)')
        plt.ylabel(state_property)
        plt.title(f'{state_property} over Time')
        plt.grid()
        plt.show()

    def plot_trajectory(self):

        xs = [getattr(state, 'position')[0] for state in self.state_list]
        ys = [getattr(state, 'position')[1] for state in self.state_list]
        plt.plot(xs, ys)
        plt.xlabel('X [m]')
        plt.ylabel('Y [m]')
        plt.title('Trajectory')
        plt.grid()
        plt.show()


def check_end(state):
    if state.position[1] <= 0:
        return True
    if abs(state.position[0]) > 150:
        return True
    return False


def get_score(results):
    last_state = results.state_list[-1]
    score = 0
    score += one_over_abs_x(last_state.position[0])
    score += one_over_abs_x(last_state.velocity[0])
    score += one_over_abs_x(last_state.velocity[1])
    score += one_over_abs_x(last_state.pitch)

    return score


def one_over_abs_x(x):
    return 1 / abs(x)