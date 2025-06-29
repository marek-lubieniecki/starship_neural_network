import pygame
import math
from starship import World
from math import sin, cos, degrees, radians


class DynamicObject(pygame.sprite.Sprite):
    def __init__(self, image_path, simulation_results):
        super().__init__()
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


class StaticObject(pygame.sprite.Sprite):
    def __init__(self, position, image_path):
        super().__init__()
        self.image = None
        self.rect = None
        self.image_path = image_path
        self.position = position

    def load_image(self):
        self.image = pygame.image.load(self.image_path).convert_alpha()
        self.rect = self.image.get_rect(center=self.position)


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