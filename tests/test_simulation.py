
from starship import *
from controller_nn import *
from simulation import *
from animation import *


def check_end(state):
    if state.position[1] <= 0:
        return True
    if abs(state.position[0]) > 150:
        return True
    return False


def test_simulation():
    environment = World()
    controller = GuidanceAndControl()
    rocket = StarshipSim(controller)
    config = Config(check_end)

    simulation = Simulation(world=environment,
                            rocket=rocket,
                            config=config)

    results = simulation.simulate()
    score = get_score(results)

    results.plot_trajectory()
    results.plot_property('pitch')

    print("Simulation scored:", score)
    print("Simulation time:", results.time[-1])

    world_sprite = StaticObject((300, 900), "data/ground.png")
    rocket_sprite = DynamicObject("data/starship.png", results)

    animation = Animation([world_sprite], [rocket_sprite])

    animation.play()
