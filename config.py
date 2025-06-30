"""
Configuration management system for the starship simulation framework.

This module provides utilities for loading, validating, and managing
simulation configurations from JSON files and other sources.
"""

import json
import os
from typing import Any, Dict, List, Optional, Union
from pathlib import Path


class ConfigurationError(Exception):
    """Exception raised for configuration-related errors."""
    pass


class ConfigLoader:
    """
    Utility class for loading and managing simulation configurations.
    
    Supports JSON configuration files with validation, defaults,
    and environment-specific overrides.
    """
    
    def __init__(self, search_paths: Optional[List[str]] = None):
        """
        Initialize the configuration loader.
        
        Args:
            search_paths: List of directories to search for config files.
                         Defaults to current directory and data/ subdirectory.
        """
        if search_paths is None:
            search_paths = [".", "data", "configs"]
        self.search_paths = [Path(p) for p in search_paths]
    
    def load_config(self, filename: str) -> Dict[str, Any]:
        """
        Load configuration from a JSON file.
        
        Args:
            filename: Name of the configuration file
            
        Returns:
            Dictionary containing configuration data
            
        Raises:
            ConfigurationError: If file not found or invalid JSON
        """
        config_path = self._find_config_file(filename)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in {config_path}: {e}")
        except IOError as e:
            raise ConfigurationError(f"Error reading {config_path}: {e}")
    
    def save_config(self, config: Dict[str, Any], filename: str, 
                   directory: Optional[str] = None) -> None:
        """
        Save configuration to a JSON file.
        
        Args:
            config: Configuration dictionary to save
            filename: Name of the file to save to
            directory: Directory to save in (default: first search path)
        """
        if directory is None:
            directory = self.search_paths[0]
        else:
            directory = Path(directory)
        
        # Ensure directory exists
        directory.mkdir(parents=True, exist_ok=True)
        
        filepath = directory / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, sort_keys=True)
        except IOError as e:
            raise ConfigurationError(f"Error writing {filepath}: {e}")
    
    def _find_config_file(self, filename: str) -> Path:
        """
        Find a configuration file in the search paths.
        
        Args:
            filename: Name of the configuration file
            
        Returns:
            Path to the configuration file
            
        Raises:
            ConfigurationError: If file not found
        """
        for search_path in self.search_paths:
            filepath = search_path / filename
            if filepath.exists():
                return filepath
        
        # If not found, check if it's an absolute path
        filepath = Path(filename)
        if filepath.exists():
            return filepath
        
        raise ConfigurationError(
            f"Configuration file '{filename}' not found in any of: "
            f"{[str(p) for p in self.search_paths]}"
        )


class ConfigValidator:
    """
    Utility class for validating simulation configurations.
    
    Provides methods to check configuration completeness, value ranges,
    and consistency across related parameters.
    """
    
    @staticmethod
    def validate_starship_config(config: Dict[str, Any]) -> List[str]:
        """
        Validate a starship configuration.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check required fields
        required_fields = ["name", "x", "y", "mass", "fuel"]
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Validate numeric ranges
        if "mass" in config and config["mass"] < 0:
            errors.append("Mass must be non-negative")
        
        if "fuel" in config and config["fuel"] < 0:
            errors.append("Fuel must be non-negative")
        
        # Validate components
        if "components" in config:
            component_errors = ConfigValidator._validate_components(config["components"])
            errors.extend(component_errors)
        
        return errors
    
    @staticmethod
    def _validate_components(components: List[Dict[str, Any]]) -> List[str]:
        """Validate component configurations."""
        errors = []
        
        for i, component in enumerate(components):
            if "type" not in component:
                errors.append(f"Component {i}: Missing type field")
                continue
            
            comp_type = component["type"]
            
            if comp_type == "Thruster":
                thruster_errors = ConfigValidator._validate_thruster(component, i)
                errors.extend(thruster_errors)
            elif comp_type == "Model":
                model_errors = ConfigValidator._validate_model(component, i)
                errors.extend(model_errors)
        
        return errors
    
    @staticmethod
    def _validate_thruster(thruster: Dict[str, Any], index: int) -> List[str]:
        """Validate thruster component configuration."""
        errors = []
        prefix = f"Thruster {index}"
        
        required_fields = ["name", "thrust", "x", "y"]
        for field in required_fields:
            if field not in thruster:
                errors.append(f"{prefix}: Missing required field '{field}'")
        
        # Validate ranges
        if "thrust" in thruster and thruster["thrust"] <= 0:
            errors.append(f"{prefix}: Thrust must be positive")
        
        if "max_pitch" in thruster:
            max_pitch = thruster["max_pitch"]
            if max_pitch < 0 or max_pitch > 90:
                errors.append(f"{prefix}: max_pitch should be between 0 and 90 degrees")
        
        if "min_power" in thruster and "max_power" in thruster:
            if thruster["min_power"] > thruster["max_power"]:
                errors.append(f"{prefix}: min_power cannot exceed max_power")
        
        return errors
    
    @staticmethod
    def _validate_model(model: Dict[str, Any], index: int) -> List[str]:
        """Validate model component configuration."""
        errors = []
        prefix = f"Model {index}"
        
        required_fields = ["name", "mass"]
        for field in required_fields:
            if field not in model:
                errors.append(f"{prefix}: Missing required field '{field}'")
        
        if "mass" in model and model["mass"] <= 0:
            errors.append(f"{prefix}: Mass must be positive")
        
        return errors


class ConfigManager:
    """
    High-level configuration manager for the simulation system.
    
    Combines loading, validation, and default value management
    for easy configuration handling.
    """
    
    def __init__(self, search_paths: Optional[List[str]] = None):
        """
        Initialize the configuration manager.
        
        Args:
            search_paths: List of directories to search for config files
        """
        self.loader = ConfigLoader(search_paths)
        self.validator = ConfigValidator()
        self._cache = {}
    
    def get_config(self, filename: str, validate: bool = True) -> Dict[str, Any]:
        """
        Get a configuration, with caching and optional validation.
        
        Args:
            filename: Configuration filename
            validate: Whether to validate the configuration
            
        Returns:
            Configuration dictionary
            
        Raises:
            ConfigurationError: If loading fails or validation errors found
        """
        # Check cache first
        if filename in self._cache:
            return self._cache[filename].copy()
        
        # Load configuration
        config = self.loader.load_config(filename)
        
        # Validate if requested
        if validate:
            errors = self.validator.validate_starship_config(config)
            if errors:
                raise ConfigurationError(f"Validation errors in {filename}:\n" + 
                                       "\n".join(f"  - {error}" for error in errors))
        
        # Apply defaults
        config = self._apply_defaults(config)
        
        # Cache and return
        self._cache[filename] = config.copy()
        return config
    
    def _apply_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default values to configuration."""
        defaults = {
            "vx": 0.0,
            "vy": 0.0,
            "angle": 0.0,
            "rot_velocity": 0.0,
            "inertial_moment": 1.0,
        }
        
        # Apply top-level defaults
        for key, default_value in defaults.items():
            if key not in config:
                config[key] = default_value
        
        # Apply component defaults
        if "components" in config:
            for component in config["components"]:
                if component.get("type") == "Thruster":
                    thruster_defaults = {
                        "min_power": 0,
                        "max_power": 100,
                        "max_pitch": 15,
                        "isp": 300,
                        "angle": 0.0,
                        "mass": 100.0,
                        "inertial_moment": 1.0
                    }
                    for key, default_value in thruster_defaults.items():
                        if key not in component:
                            component[key] = default_value
                
                elif component.get("type") == "Model":
                    model_defaults = {
                        "x": 0.0,
                        "y": 0.0,
                        "angle": 0.0,
                        "inertial_moment": 1.0
                    }
                    for key, default_value in model_defaults.items():
                        if key not in component:
                            component[key] = default_value
        
        return config
    
    def create_sample_config(self, filename: str = "sample_starship.json") -> None:
        """
        Create a sample configuration file.
        
        Args:
            filename: Name of the sample file to create
        """
        sample_config = {
            "name": "Sample Starship",
            "x": 100.0,
            "y": 500.0,
            "vx": 0.0,
            "vy": 0.0,
            "angle": 90.0,
            "rot_velocity": 0.0,
            "mass": 50000.0,
            "inertial_moment": 100.0,
            "fuel": 3000.0,
            "components": [
                {
                    "type": "Model",
                    "name": "Main Body",
                    "x": 0.0,
                    "y": 0.0,
                    "mass": 50000.0,
                    "angle": 0.0,
                    "inertial_moment": 100.0
                },
                {
                    "type": "Thruster",
                    "name": "Main Engine",
                    "thrust": 1000000.0,
                    "min_power": 20,
                    "max_power": 100,
                    "max_pitch": 10,
                    "isp": 350,
                    "x": 0.0,
                    "y": -20.0,
                    "angle": 0.0,
                    "mass": 500.0,
                    "inertial_moment": 1.0
                },
                {
                    "type": "Thruster",
                    "name": "RCS Thruster",
                    "is_rcs": "yes",
                    "thrust": 10000.0,
                    "min_power": 100,
                    "max_power": 100,
                    "max_pitch": 0,
                    "isp": 250,
                    "x": 5.0,
                    "y": 10.0,
                    "angle": 90.0,
                    "mass": 20.0,
                    "inertial_moment": 0.5
                }
            ]
        }
        
        self.loader.save_config(sample_config, filename)
    
    def clear_cache(self) -> None:
        """Clear the configuration cache."""
        self._cache.clear()


# Global configuration manager instance
config_manager = ConfigManager()


def load_config(filename: str, validate: bool = True) -> Dict[str, Any]:
    """
    Convenience function to load a configuration file.
    
    Args:
        filename: Configuration filename
        validate: Whether to validate the configuration
        
    Returns:
        Configuration dictionary
    """
    return config_manager.get_config(filename, validate)


def create_sample_configs() -> None:
    """Create sample configuration files for reference."""
    config_manager.create_sample_config("sample_starship.json")
    
    # Create a simple scenario config
    scenario_config = {
        "name": "Basic Landing Scenario",
        "description": "Simple vertical landing from 500m altitude",
        "initial_conditions": {
            "altitude": 500.0,
            "horizontal_position": 0.0,
            "horizontal_velocity": -20.0,
            "vertical_velocity": -50.0,
            "angle": 85.0
        },
        "environment": {
            "gravity": -9.81,
            "wind_speed": 0.0,
            "atmospheric_density": 1.225
        },
        "success_criteria": {
            "max_landing_velocity": 5.0,
            "max_horizontal_offset": 10.0,
            "max_landing_angle": 5.0
        }
    }
    
    config_manager.loader.save_config(scenario_config, "sample_scenario.json")