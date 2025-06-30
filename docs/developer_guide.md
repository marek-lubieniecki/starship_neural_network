# Developer Guide

This guide provides information for developers who want to contribute to or extend the Starship Neural Network simulation framework.

## Getting Started

### Development Environment Setup

1. **Clone the repository**:
```bash
git clone https://github.com/marek-lubieniecki/starship_neural_network.git
cd starship_neural_network
```

2. **Set up virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install in development mode**:
```bash
pip install -e .
```

4. **Install development dependencies**:
```bash
pip install -e .[dev]
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=. --cov-report=html

# Run specific test files
python -m pytest tests/test_simulation.py -v
```

### Code Quality

```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy .
```

## Project Structure

```
starship_neural_network/
├── __init__.py              # Package initialization
├── starship.py             # Core physics engine
├── simulation.py           # Simulation framework
├── animation.py            # Visualization system
├── core.py                 # Abstract base classes
├── config.py               # Configuration management
├── controller_nn.py        # Neural network controllers
├── control_system.py       # Example manual controller
├── nn_utils.py             # Neural network utilities
├── pyproject.toml          # Project configuration
├── requirements.txt        # Dependencies
├── data/                   # Assets (images, etc.)
├── tests/                  # Test files
└── docs/                   # Documentation
```

## Development Workflow

### Adding New Features

1. **Design the API**: Start with abstract interfaces in `core.py`
2. **Implement concrete classes**: Add specific implementations
3. **Add configuration support**: Update `config.py` if needed
4. **Write tests**: Add comprehensive test coverage
5. **Update documentation**: Include examples and API docs

### Example: Adding a New Sensor

1. **Define the interface** in `core.py`:
```python
class AltimeterSensor(SensorObject):
    """Altitude measurement sensor."""
    
    def getMeasurement(self) -> Dict[str, Any]:
        return {"altitude": self.current_altitude}
```

2. **Implement the sensor**:
```python
# In sensors.py (new file)
from core import SensorObject
from starship import World

class Altimeter(SensorObject):
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.noise_std = config.get("noise_std", 0.1)
    
    def getMeasurement(self) -> Dict[str, Any]:
        # Get true altitude from simulation
        true_altitude = self.get_true_altitude()
        
        # Add noise
        noise = np.random.normal(0, self.noise_std)
        measured_altitude = true_altitude + noise
        
        return {"altitude": measured_altitude}
    
    def get_true_altitude(self) -> float:
        # Implementation to get current altitude
        pass
```

3. **Add configuration support**:
```python
# In config.py, extend validation
def _validate_sensor(sensor: Dict[str, Any], index: int) -> List[str]:
    errors = []
    if sensor.get("type") == "Altimeter":
        if "noise_std" in sensor and sensor["noise_std"] < 0:
            errors.append(f"Sensor {index}: noise_std must be non-negative")
    return errors
```

4. **Write tests**:
```python
# In tests/test_sensors.py
def test_altimeter_measurement():
    config = {"noise_std": 0.1}
    altimeter = Altimeter("test_altimeter", config)
    
    measurement = altimeter.getMeasurement()
    assert "altitude" in measurement
    assert isinstance(measurement["altitude"], float)
```

### Code Style Guidelines

1. **Follow PEP 8**: Use `black` for automatic formatting
2. **Type hints**: Add type annotations for public APIs
3. **Docstrings**: Use Google-style docstrings for classes and methods
4. **Naming conventions**:
   - Classes: `PascalCase`
   - Functions/methods: `snake_case`
   - Constants: `UPPER_CASE`
   - Private members: `_leading_underscore`

### Example Class with Proper Style

```python
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

class ExampleController(ControllerInterface):
    """
    Example controller demonstrating proper style.
    
    This controller implements a simple proportional control law
    for spacecraft attitude control.
    
    Args:
        config: Configuration dictionary containing controller parameters
        
    Attributes:
        kp: Proportional gain
        max_torque: Maximum allowable control torque
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the controller with given configuration."""
        self.kp: float = config.get("kp", 1.0)
        self.max_torque: float = config.get("max_torque", 100.0)
        self._last_error: Optional[float] = None
    
    def control(self, sensor_data: Dict[str, Any], dt: float) -> Dict[str, float]:
        """
        Compute control torque based on attitude error.
        
        Args:
            sensor_data: Dictionary containing sensor measurements
            dt: Time step duration in seconds
            
        Returns:
            Dictionary containing control outputs
            
        Raises:
            ValueError: If required sensor data is missing
        """
        if "attitude_error" not in sensor_data:
            raise ValueError("attitude_error required in sensor_data")
        
        error = sensor_data["attitude_error"]
        control_torque = self.kp * error
        
        # Saturate control output
        control_torque = max(-self.max_torque, 
                           min(self.max_torque, control_torque))
        
        self._last_error = error
        
        return {"control_torque": control_torque}
    
    def reset(self) -> None:
        """Reset controller state."""
        self._last_error = None
    
    def getParameters(self) -> Dict[str, Any]:
        """Get current controller parameters."""
        return {
            "kp": self.kp,
            "max_torque": self.max_torque
        }
    
    def setParameters(self, parameters: Dict[str, Any]) -> None:
        """Set controller parameters."""
        if "kp" in parameters:
            self.kp = parameters["kp"]
        if "max_torque" in parameters:
            self.max_torque = parameters["max_torque"]
```

## Testing Guidelines

### Test Organization

- **Unit tests**: Test individual classes and functions
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete simulation workflows

### Test Categories

1. **Physics tests**: Verify physics computations
2. **Control tests**: Verify controller behavior
3. **Configuration tests**: Verify config loading/validation
4. **Animation tests**: Verify rendering components

### Example Test Structure

```python
import pytest
from unittest.mock import Mock, patch
from starship import World, Model
from config import ConfigManager

class TestModel:
    """Test suite for Model class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            "name": "test_model",
            "x": 0, "y": 0,
            "mass": 100,
            "angle": 0,
            "inertial_moment": 1.0
        }
    
    def test_initialization(self):
        """Test model initialization."""
        model = Model(self.config)
        assert model.name == "test_model"
        assert model.getMass() == 100
    
    def test_force_computation(self):
        """Test force computation."""
        model = Model(self.config)
        model.force_sources = ["gravity"]
        
        with patch.object(World, 'g', 9.81):
            force = model.getForce()
            expected_force = 100 * 9.81  # mass * gravity
            assert abs(force.y - expected_force) < 1e-6
    
    @pytest.mark.parametrize("mass,expected", [
        (100, 100),
        (0, 0),
        (1000, 1000)
    ])
    def test_mass_values(self, mass, expected):
        """Test different mass values."""
        config = self.config.copy()
        config["mass"] = mass
        model = Model(config)
        assert model.getMass() == expected
```

## Performance Guidelines

### Optimization Best Practices

1. **Profile before optimizing**: Use `cProfile` to identify bottlenecks
2. **Minimize allocations**: Reuse objects when possible
3. **Vectorize operations**: Use NumPy for mathematical computations
4. **Cache expensive computations**: Store results of complex calculations

### Memory Management

1. **Use generators**: For large data processing
2. **Clear references**: Remove unused simulation results
3. **Monitor memory usage**: Use `memory_profiler` for analysis

```python
# Good: Generator for large datasets
def process_simulation_results(results):
    for i, state in enumerate(results.state_list):
        yield process_state(state)

# Good: Clear references when done
simulation_results = simulation.simulate()
analyze_results(simulation_results)
simulation_results = None  # Clear reference
```

## Documentation Guidelines

### API Documentation

Use Google-style docstrings:

```python
def complex_function(param1: int, param2: str, param3: Optional[bool] = None) -> Dict[str, Any]:
    """
    Brief description of what the function does.
    
    Longer description providing more context about the function's
    purpose and behavior.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
        param3: Optional parameter with default value
        
    Returns:
        Dictionary containing processed results with keys:
            - 'status': Success/failure status
            - 'data': Processed data
            
    Raises:
        ValueError: If param1 is negative
        RuntimeError: If processing fails
        
    Example:
        >>> result = complex_function(42, "test")
        >>> print(result['status'])
        'success'
    """
```

### Updating Documentation

1. **API changes**: Update docstrings and type hints
2. **New features**: Add examples to README
3. **Architecture changes**: Update architecture.md
4. **Breaking changes**: Update migration guide

## Release Process

### Version Management

Use semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Checklist

1. **Update version** in `pyproject.toml` and `__init__.py`
2. **Run full test suite**: Ensure all tests pass
3. **Update documentation**: Include new features and changes
4. **Create release notes**: Summarize changes and improvements
5. **Tag release**: Create git tag with version number

## Troubleshooting

### Common Development Issues

1. **Import errors**: Check Python path and virtual environment
2. **Test failures**: Verify test data and mock objects
3. **Performance issues**: Profile code and optimize hot paths
4. **Memory leaks**: Use memory profiling tools

### Debug Mode

Enable debug output for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# In simulation code
logger = logging.getLogger(__name__)
logger.debug(f"Current state: {rocket.state}")
```

## Contributing

### Pull Request Process

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Make changes**: Follow coding guidelines
4. **Add tests**: Ensure good test coverage
5. **Update documentation**: Include relevant updates
6. **Submit pull request**: Include description of changes

### Code Review Guidelines

1. **Functionality**: Does the code work as intended?
2. **Style**: Does it follow project conventions?
3. **Performance**: Are there obvious performance issues?
4. **Tests**: Is there adequate test coverage?
5. **Documentation**: Are changes properly documented?

## Getting Help

- **Documentation**: Check README and docs/ directory
- **Examples**: Look at test files for usage patterns
- **Issues**: Create GitHub issues for bugs or feature requests
- **Discussions**: Use GitHub discussions for questions