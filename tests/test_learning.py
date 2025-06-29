import torch
import torch.nn as nn
import numpy as np
from simulation import *
from starship import *
from controller_nn import *
from nn_utils import *


import random
from deap import base, creator, tools, algorithms


# Initialize Genetic Algorithm with DEAP
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)


def generate_individual():
    """Generate an individual with random neural network weights."""
    net = RocketNN()
    return flatten_model_weights(net)


def evaluate(individual):
    """Evaluate the fitness of an individual (simulate rocket behavior)."""

    environment = World()
    controller = GuidanceAndControl(individual)
    rocket = StarshipSim(controller)
    config = Config(check_end)

    simulation = Simulation(world=environment,
                            rocket=rocket,
                            config=config)

    results = simulation.simulate()
    score = get_score(results)
    print("Simulation completed. Score:", score)

    return score


# Define DEAP toolbox
toolbox = base.Toolbox()
toolbox.register("individual", tools.initIterate, creator.Individual, generate_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxTwoPoint)  # Crossover method
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.1, indpb=0.1)  # Mutation
toolbox.register("select", tools.selBest)  # Selection method


# Run Genetic Algorithm
def run_evolution():
    population = toolbox.population(n=20)  # Initial population size
    generations = 50  # Number of generations

    for gen in range(generations):
        offspring = algorithms.varAnd(population, toolbox, cxpb=0.5, mutpb=0.2)  # Crossover & mutation
        fits = list(map(toolbox.evaluate, offspring))  # Evaluate fitness
        for ind, fit in zip(offspring, fits):
            ind.fitness.values = (fit, )
        population = toolbox.select(offspring, k=len(population))  # Select best individuals
        print(f"Generation {gen + 1}: Best Fitness = {max(fits):.2f}")

    return tools.selBest(population, k=1)[0]  # Return best neural network


# Run the GA

def test_evolution():
    best_nn_weights = run_evolution()


def test_nn_flattening():
    """Test if the neural network weights can be flattened and restored correctly."""
    net = RocketNN()
    flat_weights = flatten_model_weights(net)
    restored_net = RocketNN()
    set_model_weights_from_flat(restored_net, flat_weights)

    # Check if the weights match
    for original, restored in zip(net.parameters(), restored_net.parameters()):
        assert torch.allclose(original, restored), "Weights do not match after flattening and restoring."