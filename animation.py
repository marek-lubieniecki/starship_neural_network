import pygame
import math
from starship import World
from math import sin, cos, degrees, radians
from .core import RenderableObject
from typing import Any, Dict, Optional, Tuple


class DynamicObject(pygame.sprite.Sprite, RenderableObject):
    def __init__(self, image_path, simulation_results):
        pygame.sprite.Sprite.__init__(self)
        RenderableObject.__init__(self, "DynamicObject", {})
        self.image_path = image_path
        self.image = None
        self.base_image = None
        self.rect = None
        self.simulation_results = simulation_results
        self.initial_position = World.pos_meters_to_screen(simulation_results.get_property('position', 0))
        self.initial_angle = self.simulation_results.get_property('pitch', 0)

    def load_image(self):
        self.base_image = pygame.image.load(self.image_path).convert_alpha()
        self.base_image = pygame.transform.scale(self.base_image, (25, 100))
        self.image = pygame.transform.rotate(self.base_image,  degrees(self.initial_angle))
        self.rect = self.image.get_rect(center=self.initial_position)

    def update(self):
        position = self.simulation_results.get_property('position', pygame.time.get_ticks() / 1000)
        angle = self.simulation_results.get_property('pitch', pygame.time.get_ticks() / 1000)
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.image = pygame.transform.rotate(self.base_image, degrees(angle))
        self.rect.center = (World.pos_meters_to_screen(position))

    # Implement RenderableObject abstract methods
    def loadAssets(self) -> None:
        """Load visual assets for this object."""
        self.load_image()

    def getPosition(self) -> Tuple[float, float]:
        """Get the screen position for rendering."""
        position = self.simulation_results.get_property('position', pygame.time.get_ticks() / 1000)
        return World.pos_meters_to_screen(position)

    def getRotation(self) -> float:
        """Get the rotation angle for rendering."""
        return self.simulation_results.get_property('pitch', pygame.time.get_ticks() / 1000)

    def render(self, screen: Any, camera_transform: Optional[Any] = None) -> None:
        """Render this object to the screen."""
        if self.image and self.rect:
            screen.blit(self.image, self.rect)

    def getBounds(self) -> Tuple[float, float, float, float]:
        """Get the bounding box of this object."""
        if self.rect:
            return (self.rect.left, self.rect.top, self.rect.width, self.rect.height)
        return (0, 0, 0, 0)

    # Implement SimulationObject abstract methods
    def getState(self) -> Dict[str, Any]:
        """Get the current state of this animation object."""
        return {
            'position': self.getPosition(),
            'rotation': self.getRotation(),
            'image_path': self.image_path
        }

    def setState(self, state: Dict[str, Any]) -> None:
        """Set the state of this animation object."""
        # Animation objects typically get their state from simulation results
        pass


class StaticObject(pygame.sprite.Sprite, RenderableObject):
    def __init__(self, position, image_path):
        pygame.sprite.Sprite.__init__(self)
        RenderableObject.__init__(self, "StaticObject", {})
        self.image = None
        self.rect = None
        self.image_path = image_path
        self.position = position

    def load_image(self):
        self.image = pygame.image.load(self.image_path).convert_alpha()
        self.rect = self.image.get_rect(center=self.position)

    # Implement RenderableObject abstract methods
    def loadAssets(self) -> None:
        """Load visual assets for this object."""
        self.load_image()

    def update(self, simulation_time: float) -> None:
        """Update visual representation based on simulation time."""
        pass  # Static objects don't change

    def getPosition(self) -> Tuple[float, float]:
        """Get the screen position for rendering."""
        return self.position

    def getRotation(self) -> float:
        """Get the rotation angle for rendering."""
        return 0.0  # Static objects don't rotate

    def render(self, screen: Any, camera_transform: Optional[Any] = None) -> None:
        """Render this object to the screen."""
        if self.image and self.rect:
            screen.blit(self.image, self.rect)

    def getBounds(self) -> Tuple[float, float, float, float]:
        """Get the bounding box of this object."""
        if self.rect:
            return (self.rect.left, self.rect.top, self.rect.width, self.rect.height)
        return (0, 0, 0, 0)

    # Implement SimulationObject abstract methods
    def getState(self) -> Dict[str, Any]:
        """Get the current state of this static object."""
        return {
            'position': self.position,
            'image_path': self.image_path
        }

    def setState(self, state: Dict[str, Any]) -> None:
        """Set the state of this static object."""
        if 'position' in state:
            self.position = state['position']


class Animation:
    def __init__(self, static_objects=None, dynamic_object=None):
        self.static_objects = static_objects
        self.dynamic_object = dynamic_object

    def play(self):

        pygame.init()
        screen = pygame.display.set_mode((600, 900))
        clock = pygame.time.Clock()

        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((220, 218, 250))

        screen.blit(background, (0, 0))
        pygame.display.flip()

        for static_object in self.static_objects:
            static_object.load_image()
        for dynamic_object in self.dynamic_object:
            dynamic_object.load_image()

        # Create sprite groups
        static_sprites = pygame.sprite.Group(self.static_objects)
        dynamic_sprites = pygame.sprite.Group(self.dynamic_object)

        sim_end_time = self.dynamic_object[0].simulation_results.time[-1] * 1000
        running = True
        paused = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((255, 255, 255))

            # Update and draw static objects
            static_sprites.draw(screen)

            # Update and draw dynamic objects

            if not paused:
                dynamic_sprites.update()
            dynamic_sprites.draw(screen)

            pygame.display.flip()
            clock.tick(60)
            if pygame.time.get_ticks() >= sim_end_time:
                paused = True

        pygame.quit()