# Architecture Overview

This document provides a detailed overview of the Starship Neural Network simulation framework architecture.

## Core Design Principles

1. **Modularity**: Components are loosely coupled and can be easily extended or replaced
2. **Abstraction**: Abstract base classes define clear interfaces for extensibility
3. **Configuration-driven**: Behavior is controlled through JSON configuration files
4. **Physics-accurate**: Realistic simulation of spacecraft dynamics and control systems
5. **ML-ready**: Integration points for neural networks and other machine learning approaches

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
├─────────────────────────────────────────────────────────────┤
│  Training Scripts │  Simulation Scripts │  Animation Views  │
├─────────────────────────────────────────────────────────────┤
│                    Framework Layer                          │
├─────────────────────────────────────────────────────────────┤
│  Simulation      │  Animation        │  Configuration       │
│  Framework       │  Framework        │  Management          │
├─────────────────────────────────────────────────────────────┤
│                    Core Abstractions                        │
├─────────────────────────────────────────────────────────────┤
│  SimulationObject │ AnimationObject  │  ConfigurableObject │
│  PhysicsObject    │ RenderableObject │  ControllerInterface │
├─────────────────────────────────────────────────────────────┤
│                    Implementation Layer                     │
├─────────────────────────────────────────────────────────────┤
│  Physics Engine  │  Control Systems  │  Neural Networks    │
│  (starship.py)   │  (controllers)    │  (PyTorch)          │
└─────────────────────────────────────────────────────────────┘
```

## Component Overview

### Physics Engine (`starship.py`)

The physics engine provides realistic simulation of spacecraft dynamics:

- **World**: Global coordinate system and physical constants
- **State**: Position, velocity, orientation, and angular velocity
- **Model**: Base class for physical objects with mass, forces, and torques
- **Thruster**: Thrust-generating components with gimbal control
- **StarshipSim**: Complete spacecraft with multiple thruster components

#### Physics Integration

The physics engine uses Euler integration for simplicity:

```python
# Position integration
position += velocity * dt
velocity += acceleration * dt

# Rotation integration  
angle += angular_velocity * dt
angular_velocity += angular_acceleration * dt
```

Forces and torques are computed hierarchically:
1. Each component computes its local forces
2. Forces are rotated to global coordinates
3. Torques are computed from force cross products
4. Net forces and torques drive integration

### Simulation Framework (`simulation.py`)

Manages the overall simulation process:

- **Simulation**: Main simulation loop with configurable end conditions
- **Config**: Encapsulates simulation parameters and termination criteria
- **SimulationResults**: Stores and analyzes simulation trajectories

#### Simulation Loop

```python
while not config.isFinished(rocket.state):
    # Record current state
    results.add_state(World.time, rocket.state)
    results.add_commands(rocket.control_system.commands)
    
    # Update physics
    rocket.update()
    
    # Advance time
    World.time += dt
```

### Animation Framework (`animation.py`)

Provides real-time visualization using Pygame:

- **Animation**: Main animation controller with play/pause functionality
- **StaticObject**: Non-moving visual elements (ground, obstacles)
- **DynamicObject**: Moving objects driven by simulation data

#### Rendering Pipeline

1. Load sprites and initialize Pygame display
2. Create sprite groups for efficient batch rendering
3. Update dynamic object positions from simulation data
4. Render all sprites to screen buffer
5. Present frame and handle user input

### Control Systems

Multiple control approaches are supported:

- **Manual Control** (`control_system.py`): Hand-coded control logic
- **Neural Networks** (`controller_nn.py`): PyTorch-based learned controllers
- **Custom Controllers**: User-defined control implementations

#### Control Interface

All controllers implement a common interface:

```python
def control(self, imu, controller, fuel, dt):
    # Read sensor data
    position = imu.getPosition()
    velocity = imu.getVelocity()
    
    # Compute control outputs
    controller.raptor_left_power = compute_power()
    controller.raptor_right_power = compute_power()
```

### Configuration System (`config.py`)

Provides flexible configuration management:

- **ConfigLoader**: Load/save JSON configurations with search paths
- **ConfigValidator**: Validate configuration completeness and ranges
- **ConfigManager**: High-level interface with caching and defaults

#### Configuration Hierarchy

1. **Default Values**: Hard-coded sensible defaults
2. **Base Configuration**: Default JSON configuration file
3. **Environment Overrides**: Environment-specific modifications
4. **Runtime Parameters**: Command-line or programmatic overrides

## Abstract Base Classes (`core.py`)

Define extension points for the framework:

### SimulationObject

Base class for all simulation entities. Provides:
- Standard update interface
- State management
- Configuration loading

### PhysicsObject

Extends SimulationObject for objects with physical properties:
- Position and velocity queries
- Mass and inertia properties
- Force and torque computation

### ControllableObject

Interface for objects that can be controlled:
- Control input setting
- Control limit queries
- Actuator state management

### AnimationObject

Base class for visual objects:
- Asset loading
- Position and rotation queries
- Time-based updates

### ControllerInterface

Standard interface for control systems:
- Sensor data input
- Control output computation
- Parameter management

## Extension Points

### Adding New Physics Components

1. Extend `PhysicsObject` or `Model`
2. Implement force and torque computation
3. Add configuration support
4. Include in component hierarchy

```python
class MyThruster(PhysicsObject):
    def getForces(self):
        # Compute thrust forces
        return force_vector
    
    def getTorques(self):
        # Compute thrust torques
        return torque_value
```

### Creating Custom Controllers

1. Implement `ControllerInterface`
2. Define control logic in `control()` method
3. Handle sensor data and compute outputs
4. Manage internal state and parameters

```python
class MyController(ControllerInterface):
    def control(self, sensor_data, dt):
        # Custom control logic
        return control_outputs
```

### Adding New Sensors

1. Extend `SensorObject`
2. Implement measurement computation
3. Add noise modeling
4. Provide measurement interface

```python
class MySensor(SensorObject):
    def getMeasurement(self):
        # Compute sensor reading
        return measurement_dict
```

### Integrating ML Models

1. Extend `ControllerInterface`
2. Load trained models in constructor
3. Convert sensor data to model inputs
4. Convert model outputs to control commands

```python
class MLController(ControllerInterface):
    def __init__(self, model_path):
        self.model = torch.load(model_path)
    
    def control(self, sensor_data, dt):
        inputs = self.prepare_inputs(sensor_data)
        outputs = self.model(inputs)
        return self.convert_outputs(outputs)
```

## Performance Considerations

### Simulation Performance

- Physics integration uses simple Euler method for speed
- Component updates are O(n) in number of components
- No spatial partitioning - suitable for single vehicle simulation

### Rendering Performance

- Pygame sprites provide hardware-accelerated blitting
- Sprite groups enable efficient batch operations
- Frame rate limited to 60 FPS for real-time visualization

### Memory Usage

- Simulation results stored in lists (linear growth)
- Configuration caching reduces file I/O
- Model states use shallow copying where possible

## Testing Strategy

### Unit Tests

- Individual component functionality
- Configuration validation
- Physics computations

### Integration Tests

- End-to-end simulation runs
- Control system interactions
- Animation playback

### Performance Tests

- Simulation timing benchmarks
- Memory usage profiling
- Rendering frame rate analysis

## Future Extensions

### Planned Features

1. **3D Physics**: Extension to 3D dynamics and visualization
2. **Distributed Simulation**: Multi-process physics computation
3. **Advanced Sensors**: Lidar, cameras, GPS simulation
4. **Multi-Vehicle**: Fleet simulation capabilities
5. **Real-time Interface**: Hardware-in-the-loop testing

### Extension Guidelines

1. Maintain backward compatibility
2. Follow abstract interface patterns
3. Add comprehensive tests
4. Update documentation
5. Provide example usage