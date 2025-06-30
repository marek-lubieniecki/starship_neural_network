# Starship Neural Network

A physics-based simulation framework for training neural networks to control spacecraft landing sequences, inspired by SpaceX's Starship autonomous landing system.

## Features

- **Physics Simulation**: Realistic rocket dynamics with thrust vectoring, RCS controls, and fuel consumption
- **Neural Network Integration**: PyTorch-based neural networks for autonomous control
- **Visual Animation**: Real-time Pygame visualization of simulations
- **Genetic Algorithm Training**: DEAP-based evolutionary training for neural network controllers
- **Configurable Scenarios**: JSON-based configuration system for different simulation scenarios

## Installation

### Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/marek-lubieniecki/starship_neural_network.git
cd starship_neural_network
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Running a Basic Simulation

```python
from starship import World
from control_system import GuidanceAndControl
from starship import StarshipSim
from simulation import Simulation, Config

# Create simulation components
environment = World()
controller = GuidanceAndControl()
rocket = StarshipSim(controller)
config = Config(lambda state: state.position[1] <= 0)  # End when rocket lands

# Run simulation
simulation = Simulation(world=environment, rocket=rocket, config=config)
results = simulation.simulate()

# View results
results.plot_trajectory()
results.plot_property('pitch')
```

### Running with Animation

```python
from animation import Animation, StaticObject, DynamicObject

# Create animation objects
world_sprite = StaticObject((300, 900), "data/ground.png")
rocket_sprite = DynamicObject("data/starship.png", results)

# Create and play animation
animation = Animation([world_sprite], [rocket_sprite])
animation.play()
```

### Training a Neural Network Controller

```python
from tests.test_learning import run_evolution

# Train using genetic algorithm
best_weights = run_evolution()
print(f"Best neural network weights: {best_weights}")
```

## Project Structure

```
starship_neural_network/
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore patterns
├── starship.py              # Core physics simulation classes
├── simulation.py            # Simulation framework
├── animation.py             # Animation and visualization
├── control_system.py        # Example manual control system
├── controller_nn.py         # Neural network controller
├── nn_utils.py              # Neural network utilities
├── starship.json            # Default configuration file
├── data/                    # Assets (images, etc.)
└── tests/                   # Test files
    ├── test_simulation.py   # Simulation tests
    ├── test_learning.py     # Machine learning tests
    └── starship.json        # Test configuration
```

## Core Architecture

### Simulation Framework

The simulation system is built around several key abstract concepts:

- **Simulation Objects**: Entities that participate in the simulation
- **Configuration System**: JSON-based configuration management
- **Animation Objects**: Visual representation components

### Key Classes

#### Simulation Framework (`simulation.py`)
- `Simulation`: Main simulation runner
- `Config`: Simulation configuration and end conditions
- `SimulationResults`: Results storage and analysis

#### Physics Engine (`starship.py`)
- `World`: Global simulation parameters and coordinate systems
- `State`: Physical state representation (position, velocity, orientation)
- `Model`: Base physics model with components
- `Thruster`: Thrust-generating component
- `StarshipSim`: Complete spacecraft simulation
- `Controller`: Control input interface
- `IMU`: Inertial measurement unit for sensor data

#### Animation System (`animation.py`)
- `Animation`: Main animation controller
- `StaticObject`: Non-moving visual elements
- `DynamicObject`: Moving visual elements driven by simulation data

#### Control Systems
- `GuidanceAndControl` (`control_system.py`): Example manual control logic
- `RocketNN` (`controller_nn.py`): Neural network-based controller

## Configuration System

The simulation uses JSON configuration files to define spacecraft parameters:

```json
{
    "name": "Starship",
    "x": 120, "y": 400,
    "mass": 0,
    "fuel": 5000,
    "components": [
        {
            "type": "Thruster",
            "name": "Raptor 1",
            "thrust": 1920000.0,
            "max_pitch": 15
        }
    ]
}
```

### Configuration Parameters

- **Position**: Initial spacecraft position (`x`, `y`)
- **Dynamics**: Mass, fuel, inertial properties
- **Components**: Thrusters, sensors, and other subsystems
- **Thruster Properties**: Thrust force, gimbal limits, efficiency

## Extension Points

### Creating Custom Controllers

Implement the control interface:

```python
class MyController:
    def control(self, imu, controller, fuel, dt):
        # Read sensor data from imu
        position = imu.getPosition()
        velocity = imu.getVelocity()
        
        # Set control outputs
        controller.raptor_left_power = 50
        controller.raptor_right_power = 50
```

### Adding New Simulation Objects

Extend the base Model class:

```python
class MyComponent(Model):
    def __init__(self, config):
        super().__init__(config)
        # Custom initialization
    
    def getForce(self):
        # Return force vector
        return vmath.Vector2(0, 0)
```

### Creating Custom Animation Objects

Extend Pygame sprite classes:

```python
class MyAnimationObject(pygame.sprite.Sprite):
    def __init__(self, simulation_results):
        super().__init__()
        self.simulation_results = simulation_results
    
    def update(self):
        # Update based on simulation time
        pass
```

## Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

### Test Structure

- `test_simulation.py`: Basic simulation functionality
- `test_learning.py`: Neural network training and genetic algorithms

## Development

### Code Style

- Follow PEP 8 style guidelines
- Use descriptive variable names
- Document complex algorithms
- Keep functions focused and small

### Adding Features

1. Create abstract interfaces first
2. Implement concrete classes
3. Add configuration support
4. Include tests
5. Update documentation

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed via `pip install -r requirements.txt`
2. **Display Issues**: Make sure you have a display available for Pygame
3. **Performance**: Simulations can be CPU-intensive; consider reducing time steps or complexity

### Getting Help

- Check existing issues and tests for examples
- Review the code documentation
- Run simulations with debug output enabled

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]