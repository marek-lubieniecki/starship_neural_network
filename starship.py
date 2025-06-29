import os, sys
import pygame
import vectormath as vmath
from pygame.locals import *
from math import sin, cos, degrees, radians
import numpy as np
import json
import threading
import importlib
import imageio
import multiprocessing

if not pygame.font: print('Warning, fonts disabled')
if not pygame.mixer: print('Warning, sound disabled')

import numpy

def patch_asscalar(a):
    return a.item()

setattr(numpy, "asscalar", patch_asscalar)


class ImageStore:
    """Collects images, avoids loading same image multiple times"""
    store={}

    @classmethod
    def load_image(cls, name, colorkey=None):
        if name in cls.store:
            image = cls.store[name]
            return image, image.get_rect()

        fullname = os.path.join('data', name)
        try:
            image = pygame.image.load(fullname)
        except pygame.error as message:
            print('Cannot load image:', name)
            raise SystemExit(message)
        image = image.convert_alpha()
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, RLEACCEL)
        return image, image.get_rect()


class State():
    """Represents physical state of object"""

    def __init__(self, x, y, vx, vy, pitch, rot_velocity, mass, inertial_moment):
        self.position=vmath.Vector2(x, y)
        self.velocity=vmath.Vector2(vx, vy)
        self.pitch=pitch
        self.rot_velocity=rot_velocity
        self.mass=mass
        self.inertial_moment=inertial_moment

    def setPosition(self, x, y):
        self.position.x=x
        self.position.y=y
        
    def setVelocity(self, vx, vy):
        self.velocity.x=vx
        self.velocity.y=vy

class Model():
    """Handles physical model"""
    def __init__(self, config):
        self.name = config["name"]
        x=config["x"]
        y=config["y"]
        if "vx" in config:
            vx = config["vx"]
        else:
            vx = 0
        if "vy" in config:
            vy = config["vy"]
        else:
            vy = 0
        if "rot_vel" in config:
            rot_vel = config ["rot_vel"]
        else:
            rot_vel = 0
        angle=radians(config["angle"])
        mass=config["mass"]
        I=config["inertial_moment"]
        self.state = State(x,y,vx,vy,angle, rot_vel, mass, I)
        self.components = [] # models appended to this one
        self.force_sources = []

    @classmethod
    def fromConfig(cls, config):
        return cls(config)

    def addComponent(self, component):
        self.components.append(component)
    
    def getPosition(self):
        return self.state.position

    def setPosition(self, x, y):
        self.state.setPosition(x,y)

    def setVelocity(self, vx, vy):
        self.state.setVelocity(vx,vy)

    def getMass(self):
        mass = self.state.mass
        if hasattr(self, "fuel"):
            mass += self.fuel
        for component in self.components:
            mass += component.getMass()
        return mass

    def getMomentOfInertia(self):
        moment = self.state.inertial_moment*self.getMass()
        for component in self.components:
            moment += component.getMomentOfInertia() \
                + component.getMass()*component.state.position.length*component.state.position.length
            # I0 += I + m*d^2
        return moment

    def getForce(self):
        F = vmath.Vector2(0,0)
        if "gravity" in self.force_sources:
            F += vmath.Vector2(0, self.getMass()*World.g)
        return F
    
    def getRotationMatrix(self):
        theta = self.state.pitch
        return np.array([ [cos(theta), -sin(theta)],[sin(theta), cos(theta)] ])

    def getForces(self):
        F = self.getForce()
        rot = self.getRotationMatrix()
        for component in self.components:
            F += rot.dot(component.getForces())
        return F
    
    def getTorque(self):
        return 0.0
    
    def getTorques(self):
        T = self.getTorque()
        for component in self.components:
#            if mode == "debug":
 #               print(f"   [{component.name}] r={component.getPosition()} F={component.getForces()}", end='')
            T += component.getPosition().cross(component.getForces())[2] #third component
  #          if mode == "debug":
   #             print(f" T={T}")
        return T

    def update(self, dt):
        F = self.getForces()
        a = F * (1.0/self.getMass())
        T = self.getTorques()
        e = T * ( 1.0/(self.getMomentOfInertia()))

        
#        if mode == "debug":
 #           print(f"[{self.name}] pos={self.state.position} vel={self.state.velocity}")
#        if mode == "debug":
#            print(f"[{self.name}] F={F} a={a} T={T} e={e}")
#        if mode == "debug":
 #           print(f"I={self.getMass()*self.getMomentOfInertia()}")

        self.state.position += self.state.velocity*dt
        self.state.velocity += a*dt
        self.state.pitch += self.state.rot_velocity*dt
        self.state.rot_velocity += e*dt

        return a, e

class IMUHandler:
    def __init__(self, imu):
        self.imu=imu
    
    def updatePosition(self, position):
        self.imu.position = position
    
    def updateVelocity(self, velocity):
        self.imu.velocity = velocity

    def updateAcceleration(self, acceleration):
        self.imu.acceleration = acceleration
    
    def updatePitch(self, pitch):
        self.imu.pitch = pitch
    
    def updateRotationalVelocity(self, rot_vel):
        self.imu.rot_vel = rot_vel

    def updateRotationalAcceleration(self, rot_acc):
        self.imu.rot_acc = rot_acc

class IMU:
    def __init__(self):
        self.position = vmath.Vector2(0,0)
        self.pitch = 0
        self.rot_vel = 0
        self.rot_acc = 0
        self.acceleration = vmath.Vector2(0,0)
        self.velocity = vmath.Vector2(0,0)
    
    """ Returns current position as vectormath's Vector2 which is
    a numpy array vector with two components."""
    def getPosition(self):
        return self.position

    """ Returns current velocity as vectormath's Vector2 which is
    a numpy array vector with two components."""
    def getVelocity(self):
        return self.velocity
    
    """ Returns current acceleration as vectormath's Vector2 which is
    a numpy array vector with two components."""
    def getAcceleration(self):
        return self.acceleration

    """ Returns pitch as a float """
    def getPitch(self):
        return self.pitch
    
    """ Returns rotational velocity as a float """
    def getRotationalVelocity(self):
        return self.rot_vel
    
    """ Returns acceleration as a float """
    def getRotationalAcceleration(self):
        return self.rot_acc

class Controller:
    def __init__(self):
        self.rcs_top_left_power = 0
        self.rcs_top_right_power = 0
        self.rcs_bot_left_power = 0
        self.rcs_bot_right_power = 0
        self.raptor_left_power = 0
        self.raptor_right_power = 0
        self.raptor_right_pitch = 0
        self.raptor_left_pitch = 0



class Thruster(Model):
    def __init__(self, config):
        super().__init__(config)
        self.power = 0.0
        self.thrust = config['thrust']
        self.min_power = config['min_power']
        self.max_power = config['max_power']
        self.isp = config['isp']
        self.max_pitch = radians(config['max_pitch'])
        self.ignition_duration = config['ignition_duration']

        self.initializing = False
        self.power_to_set = 0
        self.time_at_power = 0

    @classmethod
    def fromConfig(cls, config):
        return cls(config)

    def gimbal(self, pitch):
        if pitch > self.max_pitch:
            pitch = self.max_pitch
        if pitch < -self.max_pitch:
            pitch = -self.max_pitch
        self.state.pitch = pitch

    def setPower(self, power):
        power = self.constrainPower(power)
        if power > 0 and self.power == 0 and not self.initializing:
            self.initializing = True
            self.power_to_set = power
            self.time_at_power = World.time + self.ignition_duration
        elif power == 0 and self.power > 0:
            self.power = 0
        elif self.power > 0:
            self.power = power
    
    def constrainPower(self, power):
        if power > self.max_power:
            power = self.max_power
        if power < self.min_power and power != 0:
            power = self.min_power

        return power
    
    def getPower(self):
        if self.initializing:
            if World.time > self.time_at_power:
                self.initializing = False
                self.power = self.power_to_set

        return self.power

    def getForce(self):
        thrust = self.getPower()/100.0*self.thrust
        return vmath.Vector2(-thrust*sin(self.state.pitch), thrust*cos(self.state.pitch))

class StarshipSim():
    """Operates starship"""

    def __init__(self, control_system=None):
        self.IMU = IMU()
        self.IMUHandler = IMUHandler(self.IMU)
        self.controller = Controller()

        self.createModel()

        self.control_system = control_system

    def createModel(self):
        with open("starship.json") as f:
            config = json.loads(f.read())
            self.model = Model.fromConfig(config)
            self.model.setVelocity(config['vx'], config['vy'])
            self.model.state.rot_velocity = config['rot_velocity']
            self.r = config['r']
            self.h = config['h']
            self.model.force_sources.append("gravity")

            self.model.fuel = config['fuel']

            for component in config["components"]:
                self.model.components.append(eval(f"{component['type']}.fromConfig(component)"))

    def setPower(self, power, name):
        if name == "all":
            for component in self.model.components:
                if isinstance(component, Thruster):
                    component.power = power
        else:
            self.getComponent(name).setPower(power)

    def gimbalThruster(self, pitch, name):
        self.getComponent(name).gimbal(pitch)

    def getComponent(self, name):
        for component in self.model.components:
            if component.name == name:
                return component

    def getPosition(self):
        return self.model.state.position

    def getPitch(self):
        return self.model.state.pitch

    def getVelocity(self):
        return self.model.state.velocity

    def update(self):
        dt = 1.0 / 60.0
        World.time += dt
#        if mode == "debug":
     #       print(f"t={World.time:.2f}")
        acc, rot_acc = self.model.update(dt)
        self.updateThrusters(dt)
        self.updateGuidanceAndControl(acc, rot_acc, dt)

    def updateGuidanceAndControl(self, acc, rot_acc, dt):
        if self.control_system == None:
            return

        self.IMUHandler.updatePosition(self.getPosition())
        self.IMUHandler.updateVelocity(self.getVelocity())
        self.IMUHandler.updateAcceleration(acc)

        self.IMUHandler.updatePitch(self.getPitch())
        self.IMUHandler.updateRotationalVelocity(self.model.state.rot_velocity)
        self.IMUHandler.updateRotationalAcceleration(rot_acc)

        self.control_system.control(self.IMU, self.controller, self.model.fuel, dt)

        if self.model.fuel > 0:
            self.setPower(self.controller.raptor_left_power, "Raptor 1")
            self.setPower(self.controller.raptor_right_power, "Raptor 2")
            self.setPower(self.controller.rcs_top_left_power, "RCS TL")
            self.setPower(self.controller.rcs_top_right_power, "RCS TR")
            self.setPower(self.controller.rcs_bot_left_power, "RCS BL")
            self.setPower(self.controller.rcs_bot_right_power, "RCS BR")

        self.gimbalThruster(self.controller.raptor_left_pitch, "Raptor 1")
        self.gimbalThruster(self.controller.raptor_right_pitch, "Raptor 2")

    def updateThrusters(self, dt):
#        if mode == "debug":
 #           print(f"fuel = {self.model.fuel:.2f}kg")
        for component in self.model.components:
            if isinstance(component, Thruster):
                if self.model.fuel <= 0:
                    component.power = 0
                if component.power > 0:
                    mass_flow_rate = -component.power / 100 * component.thrust / World.g / component.isp
                    self.model.fuel -= mass_flow_rate * dt
                    # print(f"  [{component.name}]: {mass_flow_rate:.2f} kg/s",end='')
                    #component.updateSprite(self.getPosition().x, self.getPosition().y, self.getPitch())
        # print()

class Starship(pygame.sprite.Sprite):
    """Operates starship"""
    def __init__(self, control_system=None):
        pygame.sprite.Sprite.__init__(self)
        image, rect = ImageStore.load_image("starship.png")
        self.base_image = pygame.transform.scale(image, (25, 100))
        self.image=self.base_image
        self.rect = self.image.get_rect()

        self.IMU = IMU()
        self.IMUHandler = IMUHandler(self.IMU)
        self.controller = Controller()

        self.createModel()

        self.control_system = control_system

    def createModel(self):
        with open("starship.json") as f:
            config = json.loads(f.read())
            self.model=Model.fromConfig(config)
            self.model.setVelocity(config['vx'], config['vy'])
            self.model.state.rot_velocity = config['rot_velocity']
            self.r = config['r']
            self.h = config['h']
            self.model.force_sources.append("gravity")

            self.model.fuel = config['fuel']

            for component in config["components"]:
                self.model.components.append(eval(f"{component['type']}.fromConfig(component)"))

    def setPower(self, power, name):
        if name == "all":
            for component in self.model.components:
                if isinstance(component, Thruster):
                    component.power = power
        else:
            self.getComponent(name).setPower(power)
    
    def gimbalThruster(self, pitch, name):
        self.getComponent(name).gimbal(pitch)
    
    def getComponent(self, name):
        for component in self.model.components:
            if component.name == name:
                return component

    def getPosition(self):
        return self.model.state.position
    
    def getPitch(self):
        return self.model.state.pitch
    
    def getVelocity(self):
        return self.model.state.velocity

    def rotateTo(self, pitch):
        """Rotate starship image to a given angle - radians"""
        self.image = pygame.transform.rotate(self.base_image, degrees(pitch))
        self.rect = self.image.get_rect()

    def update(self):
        dt = 1.0/60.0
        World.time += dt
        #if mode == "debug":
        #    print(f"t={World.time:.2f}")
        acc, rot_acc = self.model.update(dt)
        self.updateThrusters(dt)
        self.updateGuidanceAndControl(acc, rot_acc, dt)
            
        self.rotateTo(self.getPitch())
        self.rect.center = ( World.pos_meters_to_screen(self.getPosition()) )

    def updateGuidanceAndControl(self, acc, rot_acc, dt):
        if self.control_system == None:
            return

        self.IMUHandler.updatePosition(self.getPosition())
        self.IMUHandler.updateVelocity(self.getVelocity())
        self.IMUHandler.updateAcceleration(acc)

        self.IMUHandler.updatePitch(self.getPitch())
        self.IMUHandler.updateRotationalVelocity(self.model.state.rot_velocity)
        self.IMUHandler.updateRotationalAcceleration(rot_acc)

        self.control_system.control(self.IMU, self.controller, self.model.fuel, dt)

        if self.model.fuel > 0:
            self.setPower(self.controller.raptor_left_power, "Raptor 1")
            self.setPower(self.controller.raptor_right_power, "Raptor 2")
            self.setPower(self.controller.rcs_top_left_power, "RCS TL")
            self.setPower(self.controller.rcs_top_right_power, "RCS TR")
            self.setPower(self.controller.rcs_bot_left_power, "RCS BL")
            self.setPower(self.controller.rcs_bot_right_power, "RCS BR")

        self.gimbalThruster(self.controller.raptor_left_pitch, "Raptor 1")
        self.gimbalThruster(self.controller.raptor_right_pitch, "Raptor 2")


    def updateThrusters(self, dt):
        #if mode == "debug":
        #   print(f"fuel = {self.model.fuel:.2f}kg")
        for component in self.model.components:
            if isinstance(component, Thruster):
                if self.model.fuel <= 0:
                    component.power=0
                if component.power>0:
                    mass_flow_rate = -component.power/100*component.thrust / World.g / component.isp
                    self.model.fuel -= mass_flow_rate*dt
                    #print(f"  [{component.name}]: {mass_flow_rate:.2f} kg/s",end='')
                    component.updateSprite(self.getPosition().x, self.getPosition().y, self.getPitch())
        #print()

class World():
    """This class holds global parameters"""
    g=-9.81
    pos=[0,0]
    target_pos=(300,900-108)
    m_per_px=0.5
    time=0

    @classmethod
    def pos_meters_to_screen(cls, pos_to_calc):
        pos_pix = (pos_to_calc.x/cls.m_per_px+cls.target_pos[0], -pos_to_calc.y/cls.m_per_px+cls.target_pos[1])
        return pos_pix

    @classmethod
    def update(cls, target):
        if target.rect.center[1] < 100:
            cls.pos[1]+=100


class Ground(pygame.sprite.Sprite):
    """This is the object that is displayed as ground"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = ImageStore.load_image("ground.png")
        self.position = vmath.Vector2(0,13.5)

    def update(self):
        self.rect.midtop = World.pos_meters_to_screen(self.position)

class SpriteFX(pygame.sprite.Sprite):
    """This is the FX sprite"""
    def __init__(self, fx_name, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = ImageStore.load_image(fx_name)
        self.position = vmath.Vector2(x,y)
        self.anchor = "center"

    def update(self):
        exec(f"self.rect.{self.anchor} = World.pos_meters_to_screen(self.position)")

def drawExhaust(allsprites, starship):
    for name in ["Raptor 1", "Raptor 2", "RCS TL", "RCS TR", "RCS BL", "RCS BR"]:
        thruster = starship.getComponent(name)
        sprite = thruster.sprite
        if thruster.power == 0 and sprite  in allsprites:
            allsprites.remove(sprite)
        elif thruster.power != 0 and not sprite  in allsprites:
            allsprites.add(sprite)

def processEvents(pygame, allsprites, starship, going, paused):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            going = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            going = False
        elif not paused:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                starship.setPower(100, "Raptor 1")
                starship.setPower(100, "Raptor 2")
                allsprites.add(starship.getComponent("Raptor 1").sprite)
                allsprites.add(starship.getComponent("Raptor 2").sprite)
            elif event.type == pygame.KEYUP and event.key == pygame.K_UP:
                starship.setPower(0, "Raptor 1")
                allsprites.remove(starship.getComponent("Raptor 1").sprite)
                starship.setPower(0, "Raptor 2")
                allsprites.remove(starship.getComponent("Raptor 2").sprite)

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                starship.setPower(100, "RCS TL")
                allsprites.add(starship.getComponent("RCS TL").sprite)
                starship.setPower(100, "RCS BR")
                allsprites.add(starship.getComponent("RCS BR").sprite)
                starship.getComponent("Raptor 2").gimbal(radians(25))
                starship.getComponent("Raptor 1").gimbal(radians(25))
            elif event.type == pygame.KEYUP and event.key == pygame.K_RIGHT:
                starship.setPower(0, "RCS TL")
                allsprites.remove(starship.getComponent("RCS TL").sprite)
                starship.setPower(0, "RCS BR")
                allsprites.remove(starship.getComponent("RCS BR").sprite)
                starship.getComponent("Raptor 2").gimbal(radians(0))
                starship.getComponent("Raptor 1").gimbal(radians(0))
                    
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                starship.setPower(100, "RCS TR")
                allsprites.add(starship.getComponent("RCS TR").sprite)
                starship.setPower(100, "RCS BL")
                allsprites.add(starship.getComponent("RCS BL").sprite)
                starship.getComponent("Raptor 2").state.pitch = radians(-15)
                starship.getComponent("Raptor 1").state.pitch = radians(-15)
            elif event.type == pygame.KEYUP and event.key == pygame.K_LEFT:
                starship.setPower(0, "RCS TR")
                allsprites.remove(starship.getComponent("RCS TR").sprite)
                starship.setPower(0, "RCS BL")
                allsprites.remove(starship.getComponent("RCS BL").sprite)
                starship.getComponent("Raptor 2").state.pitch = radians(0)
                starship.getComponent("Raptor 1").state.pitch = radians(0)
    return going, paused

def checkEndConditions(background, allsprites, starship, paused):
    pitch = starship.getPitch()

    if (starship.getPosition().y < abs(starship.r*sin(pitch)+starship.h/2*cos(pitch)) \
        or abs(starship.getPosition().x)>150) \
        and starship in allsprites:

        starship.setPower(0, "all")

        paused = True

        if abs(starship.getPitch()) > degrees(5) or abs(starship.getPosition().x) > 20 or abs(starship.getVelocity().x) > 1 or abs(starship.getVelocity().y) > 1:
            allsprites.remove(starship)
            font = pygame.font.Font(None, 100)
            text = font.render("Game Over", 1, (50, 10, 10))
            textpos = text.get_rect(centerx=background.get_width() / 2, centery=background.get_height() / 2 )

            background.fill((170, 40, 0))
            background.blit(text, textpos)
            if not abs(starship.getPosition().x)>150:
                blast = SpriteFX("blast.png", 0, 15)
                allsprites.add(blast)
                blast.position.x = starship.getPosition().x
                blast.update()
        
        else:
            points = 20-abs(starship.getPosition().x)
            points -= abs(starship.getVelocity().x)*10
            points -= abs(starship.getVelocity().y)*10
            points -= abs(degrees(starship.getPitch()))
            font = pygame.font.Font(None, 50)
            text = font.render("Success: {:.2f} pts".format(points), 1, (10, 140, 10))
            textpos = text.get_rect(centerx=background.get_width() / 2, centery=background.get_height() / 2 )
            background.blit(text, textpos)

    return paused

def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""
    pygame.init()
    screen = pygame.display.set_mode((600, 900))
    pygame.display.set_caption('Starship landing coding contest')
    #pygame.mouse.set_visible(0)

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((220, 218, 250))

    screen.blit(background, (0, 0))
    pygame.display.flip()

    if not os.path.exists("frames"):
        os.makedirs("frames")

    frame_count = 0

    if mode != "debug" and mode !="":
        print(f"Importing {mode}")
        control_module = importlib.import_module(mode)
        starship = Starship(control_module.GuidanceAndControl())
    else:
        starship = Starship()
    ground = Ground()

    allsprites = pygame.sprite.RenderPlain((starship, ground))

    clock = pygame.time.Clock()

    going = True
    paused = False
    while going:
        clock.tick(60)

        # Handle Input Events
        going, paused = processEvents(pygame, allsprites, starship, going, paused)

        World.update(starship)

        drawExhaust(allsprites, starship)

        paused = checkEndConditions(background, allsprites, starship, paused)
        
        if not paused:
            allsprites.update()

        # Draw Everything
        screen.blit(background, (0, 0))
        allsprites.draw(screen)
        pygame.display.flip()

        # Copy screen surface to avoid delays
        #frame_copy = screen.copy()

        # Save frame asynchronously
        #pygame.image.save(frame_copy, f"frames/frame_{frame_count:03d}.png")

        #frame_count += 1

    pygame.quit()

    #frames = [imageio.imread(f"frames/frame_{i:03d}.png") for i in range(frame_count)]
    #imageio.mimsave("fast_animation.gif", frames, fps=30)



# this calls the 'main' function when this script is executed
if __name__ == "__main__":
    if len(sys.argv) == 2:
        mode = sys.argv[1]
        if mode.endswith(".py"):
            mode = mode[:-3]
    else:
        mode = ""

    main()
