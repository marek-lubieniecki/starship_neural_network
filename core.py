"""
Abstract base classes and interfaces for the starship simulation framework.

This module defines the core abstractions that enable extensibility and 
modularity in the simulation system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
import vectormath as vmath


class SimulationObject(ABC):
    """
    Abstract base class for all objects that participate in the simulation.
    
    This defines the core interface for physics objects, sensors, actuators,
    and other simulation components.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize a simulation object.
        
        Args:
            name: Unique identifier for this object
            config: Configuration dictionary for object parameters
        """
        self.name = name
        self.config = config
    
    @abstractmethod
    def update(self, dt: float) -> None:
        """
        Update the object state for one simulation time step.
        
        Args:
            dt: Time step duration in seconds
        """
        pass
    
    @abstractmethod
    def getState(self) -> Dict[str, Any]:
        """
        Get the current state of this object.
        
        Returns:
            Dictionary containing object state variables
        """
        pass
    
    @abstractmethod
    def setState(self, state: Dict[str, Any]) -> None:
        """
        Set the state of this object.
        
        Args:
            state: Dictionary containing state variables to set
        """
        pass


class PhysicsObject(SimulationObject):
    """
    Abstract base class for objects with physical properties and dynamics.
    
    Extends SimulationObject with physics-specific methods for forces,
    mass, and spatial relationships.
    """
    
    @abstractmethod
    def getPosition(self) -> vmath.Vector2:
        """Get the current position of this object."""
        pass
    
    @abstractmethod
    def getVelocity(self) -> vmath.Vector2:
        """Get the current velocity of this object."""
        pass
    
    @abstractmethod
    def getMass(self) -> float:
        """Get the current mass of this object."""
        pass
    
    @abstractmethod
    def getForces(self) -> vmath.Vector2:
        """Get the net force acting on this object."""
        pass
    
    @abstractmethod
    def getTorques(self) -> float:
        """Get the net torque acting on this object."""
        pass


class ControllableObject(SimulationObject):
    """
    Abstract base class for objects that can be controlled.
    
    Provides interface for control systems to interact with actuators
    and other controllable components.
    """
    
    @abstractmethod
    def setControlInputs(self, inputs: Dict[str, float]) -> None:
        """
        Set control inputs for this object.
        
        Args:
            inputs: Dictionary mapping control channel names to values
        """
        pass
    
    @abstractmethod
    def getControlLimits(self) -> Dict[str, Tuple[float, float]]:
        """
        Get the limits for each control input.
        
        Returns:
            Dictionary mapping control names to (min, max) tuples
        """
        pass


class SensorObject(SimulationObject):
    """
    Abstract base class for sensor objects.
    
    Provides interface for reading measurements from the simulation.
    """
    
    @abstractmethod
    def getMeasurement(self) -> Dict[str, Any]:
        """
        Get the current sensor measurement.
        
        Returns:
            Dictionary containing sensor readings
        """
        pass
    
    @abstractmethod
    def getNoise(self) -> Dict[str, float]:
        """
        Get the noise characteristics of this sensor.
        
        Returns:
            Dictionary mapping measurement types to noise standard deviations
        """
        pass


class ConfigurableObject(ABC):
    """
    Abstract base class for objects that can be configured from external sources.
    
    Provides standardized configuration loading and validation.
    """
    
    @abstractmethod
    def loadConfiguration(self, config: Dict[str, Any]) -> None:
        """
        Load configuration from a dictionary.
        
        Args:
            config: Configuration dictionary
        """
        pass
    
    @abstractmethod
    def validateConfiguration(self, config: Dict[str, Any]) -> bool:
        """
        Validate a configuration dictionary.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if configuration is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def getDefaultConfiguration(self) -> Dict[str, Any]:
        """
        Get the default configuration for this object type.
        
        Returns:
            Dictionary containing default configuration values
        """
        pass


class AnimationObject(ABC):
    """
    Abstract base class for objects that can be animated/visualized.
    
    Provides interface for rendering objects in the animation system.
    """
    
    @abstractmethod
    def loadAssets(self) -> None:
        """Load visual assets (images, sprites, etc.) for this object."""
        pass
    
    @abstractmethod
    def update(self, simulation_time: float) -> None:
        """
        Update visual representation based on simulation time.
        
        Args:
            simulation_time: Current simulation time in seconds
        """
        pass
    
    @abstractmethod
    def getPosition(self) -> Tuple[float, float]:
        """
        Get the screen position for rendering.
        
        Returns:
            (x, y) screen coordinates
        """
        pass
    
    @abstractmethod
    def getRotation(self) -> float:
        """
        Get the rotation angle for rendering.
        
        Returns:
            Rotation angle in radians
        """
        pass


class RenderableObject(AnimationObject):
    """
    Abstract base class for objects that can be rendered to screen.
    
    Extends AnimationObject with specific rendering methods.
    """
    
    @abstractmethod
    def render(self, screen: Any, camera_transform: Optional[Any] = None) -> None:
        """
        Render this object to the screen.
        
        Args:
            screen: Pygame screen surface or similar rendering target
            camera_transform: Optional camera transformation matrix
        """
        pass
    
    @abstractmethod
    def getBounds(self) -> Tuple[float, float, float, float]:
        """
        Get the bounding box of this object.
        
        Returns:
            (left, top, width, height) bounding rectangle
        """
        pass


class ControllerInterface(ABC):
    """
    Abstract base class for control systems.
    
    Defines the interface that all controllers must implement.
    """
    
    @abstractmethod
    def control(self, sensor_data: Dict[str, Any], dt: float) -> Dict[str, float]:
        """
        Compute control outputs based on sensor data.
        
        Args:
            sensor_data: Dictionary containing sensor measurements
            dt: Time step duration in seconds
            
        Returns:
            Dictionary mapping control output names to values
        """
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset the controller to initial state."""
        pass
    
    @abstractmethod
    def getParameters(self) -> Dict[str, Any]:
        """
        Get controller parameters.
        
        Returns:
            Dictionary containing controller parameters
        """
        pass
    
    @abstractmethod
    def setParameters(self, parameters: Dict[str, Any]) -> None:
        """
        Set controller parameters.
        
        Args:
            parameters: Dictionary containing parameters to set
        """
        pass


class SimulationEnvironment(ABC):
    """
    Abstract base class for simulation environments.
    
    Defines the interface for simulation world management.
    """
    
    @abstractmethod
    def step(self, dt: float) -> None:
        """
        Advance the simulation by one time step.
        
        Args:
            dt: Time step duration in seconds
        """
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset the simulation to initial conditions."""
        pass
    
    @abstractmethod
    def addObject(self, obj: SimulationObject) -> None:
        """
        Add an object to the simulation.
        
        Args:
            obj: Object to add to the simulation
        """
        pass
    
    @abstractmethod
    def removeObject(self, obj: SimulationObject) -> None:
        """
        Remove an object from the simulation.
        
        Args:
            obj: Object to remove from the simulation
        """
        pass
    
    @abstractmethod
    def getObjects(self) -> List[SimulationObject]:
        """
        Get all objects in the simulation.
        
        Returns:
            List of all simulation objects
        """
        pass