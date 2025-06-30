"""
Starship Neural Network - A physics-based simulation framework for spacecraft control.

This package provides tools for simulating spacecraft dynamics and training
neural networks for autonomous landing control systems.
"""

__version__ = "0.1.0"
__author__ = "Starship Neural Network Contributors"

# Core simulation components
from .starship import World, State, Model, Thruster, StarshipSim, Controller, IMU
from .simulation import Simulation, Config, SimulationResults
from .animation import Animation, StaticObject, DynamicObject

# Framework abstractions
from .core import (
    SimulationObject,
    PhysicsObject, 
    ControllableObject,
    SensorObject,
    ConfigurableObject,
    AnimationObject,
    RenderableObject,
    ControllerInterface,
    SimulationEnvironment
)

# Configuration management
from .config import ConfigManager, ConfigLoader, ConfigValidator, load_config

# Neural network components
from .controller_nn import RocketNN
from .nn_utils import flatten_model_weights, set_model_weights_from_flat

__all__ = [
    # Core simulation
    "World", "State", "Model", "Thruster", "StarshipSim", "Controller", "IMU",
    "Simulation", "Config", "SimulationResults",
    "Animation", "StaticObject", "DynamicObject",
    
    # Framework abstractions
    "SimulationObject", "PhysicsObject", "ControllableObject", "SensorObject",
    "ConfigurableObject", "AnimationObject", "RenderableObject", 
    "ControllerInterface", "SimulationEnvironment",
    
    # Configuration
    "ConfigManager", "ConfigLoader", "ConfigValidator", "load_config",
    
    # Neural networks
    "RocketNN", "flatten_model_weights", "set_model_weights_from_flat",
]