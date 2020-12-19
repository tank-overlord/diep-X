# -*- coding: utf-8 -*-

# Author: Tank Overlord <TankOverLord88@gmail.com>
#
# License: BSD 3-Clause
 
import pygame
from pygame import draw, Color, math, freetype

import time

import random

import math

import pathlib
import os

def sin_deg(deg):
    return math.sin(deg/180*math.pi)

def cos_deg(deg):
    return math.cos(deg/180*math.pi)

# return between 180 and -180
def atan_deg(opposite, adjacent):
    return math.atan2(opposite, adjacent)*180/math.pi

class bg_grid(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid_margin = 25
        self.fg_color = Color(194, 194, 194)
        self.bg_color = Color(228, 228, 228)
        self.surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT),)
        self.rect = self.surf.get_rect(topleft=(0,0),)
        self.draw()

    def draw(self, *args, **kwargs):
        self.surf.fill(self.bg_color)
        # horizontal
        for y in range(0, SCREEN_HEIGHT, self.grid_margin):
            pygame.draw.line(surface = self.surf, color = self.fg_color, start_pos = pygame.math.Vector2((0,y)), end_pos = pygame.math.Vector2((SCREEN_WIDTH,y)), width = 1)
        # vertical
        for x in range(0, SCREEN_WIDTH, self.grid_margin):
            pygame.draw.line(surface = self.surf, color = self.fg_color, start_pos = pygame.math.Vector2((x,0)), end_pos = pygame.math.Vector2((x,SCREEN_HEIGHT)), width = 1)


class shape(object):
    def __init__(self, center_x=None, center_y=None, side_len=30, side_len_scale_factor=1.0, spin_speed=None, screen_margin=60, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.side_len_scale_factor = side_len_scale_factor
        self.screen_margin = screen_margin
        self.center_x = center_x
        if self.center_x is None:
            self.center_x = random.randint(self.screen_margin, SCREEN_WIDTH-self.screen_margin)
        self.center_y = center_y
        if self.center_y is None:
            self.center_y = random.randint(self.screen_margin, SCREEN_HEIGHT-self.screen_margin)
        self.side_len = side_len * self.side_len_scale_factor
        self.bg_color = Color(0, 0, 0, 0) # transparent
        # place holder
        self.fg_color = None
        # spin speed
        self.initial_angle = random.randint(0, 360)
        self.spin_speed = spin_speed
        if self.spin_speed is None:
            self.spin_speed = random.uniform(-0.6, 0.6)
        # combat variables
        self.health = 10.0
        self.hit = 0.1 # unit: square
        self.reward_points = None
        self.respawn_wait_time = random.uniform(1, 4) # seconds
        # surf & rect
        self.r = self.side_len*1.8 # radius
        self.set_surf_rect()
        # for collision detection
        self.mask = pygame.mask.from_surface(self.surf)
        # respawn variables
        self.visible = True
        self.birth_time = time.time()
        # chasing tank?
        self.chasing_tank = False
        self.tank_rect_center = None
        self.chasing_speed = 2 # random.randint(1,3)

    def chase_tank(self, tank):
        #distance = math.sqrt((tank.rect.centerx - self.rect.centerx)**2, (tank.rect.centery - self.rect.centery)**2)
        if not tank.visible:
            return

        tank_rect_center = pygame.Vector2((tank.rect.centerx, tank.rect.centery))
        self.rect_center = pygame.Vector2((self.rect.centerx, self.rect.centery))
        if tank_rect_center.distance_to(self.rect_center) < self.chasing_speed:
            return
        ###########################################
        if (self.tank_rect_center is None) or (self.tank_rect_center != tank_rect_center):
            self.rect_original = self.rect
            self.tank_rect_center = tank_rect_center
            direction = self.tank_rect_center - self.rect_center
            self.chasing_angle = atan_deg(direction[1], direction[0])
            self.total_steps = self.chasing_speed

        # chasing
        self.total_steps += self.chasing_speed
        self.rect = self.rect_original.move(self.total_steps * cos_deg(self.chasing_angle), self.total_steps * sin_deg(self.chasing_angle))


    def set_surf_rect(self, scale_factor=1.1):
        self.surf_width = self.r*2*scale_factor
        self.surf_height = self.r*2*scale_factor
        self.surf_origin_coord = pygame.math.Vector2(self.surf_width/2, self.surf_height/2) # the "(0,0)" coordinate
        self.surf = pygame.Surface((self.surf_width, self.surf_height),).convert_alpha() # transparent; and the size of the surface
        self.rect = self.surf.get_rect(center=(self.center_x, self.center_y),) # the position of the rect

    def draw(self, angle=None):
        self.surf.fill(self.bg_color)
        self.set_points(angle=self.initial_angle+angle)
        pygame.draw.polygon(surface = self.surf, color = self.fg_color, points = self.points, width = 0)
        pygame.draw.aalines(surface = self.surf, color = Color(0,0,0), closed = True, points = self.points)

    def set_points(self, angle=None):
        self.points = None # place holder

    def separate_from_other_shapes(self, existing_rect_list=[]):
        start_time = time.time()
        max_attempt_duration = 5 # seconds
        while self.rect.collidelist(existing_rect_list) != -1 and ((time.time() - start_time) < max_attempt_duration):
            self.center_x = random.randint(self.screen_margin, SCREEN_WIDTH-self.screen_margin)
            self.center_y = random.randint(self.screen_margin, SCREEN_HEIGHT-self.screen_margin)
            self.rect = self.surf.get_rect(center=(self.center_x, self.center_y),)
        if (time.time() - start_time) >= max_attempt_duration:
            return None
        else:
            existing_rect_list.append(self.rect)
            return existing_rect_list

    def collide_with(self, other_shapes_list=[], exclude_shapes_list=[], mask_precomputed=False):
        if not mask_precomputed:
            self.mask = pygame.mask.from_surface(self.surf)
        for idx, other in enumerate(other_shapes_list):
            if other != self and other not in exclude_shapes_list:
                if self.rect.colliderect(other.rect): # to speed things up, because mask.overlap() is much more time-consuming
                    if not mask_precomputed:
                        other.mask = pygame.mask.from_surface(other.surf)
                    offset = (self.rect.x - other.rect.x, self.rect.y - other.rect.y)
                    if other.mask.overlap(self.mask, offset):
                        return idx
        return -1


class square(shape):
    def __init__(self, side_len_scale_factor=1.0, *args, **kwargs):
        super().__init__(side_len_scale_factor=side_len_scale_factor, *args, **kwargs)
        self.h = self.side_len/2 # see games.pptx
        self.r = self.h * math.sqrt(2)
        self.set_surf_rect()
        # color
        self.fg_color = Color(247, 226, 91)
        # combat variables
        self.reward_points = 10.0
    
    def set_points(self, angle=None):
        self.points = [pygame.math.Vector2(p).rotate(angle*self.spin_speed) + self.surf_origin_coord for p in [(self.h, self.h), (self.h, -self.h), (-self.h, -self.h), (-self.h, self.h)]]


class triangle(shape):
    def __init__(self, side_len_scale_factor=4/3, *args, **kwargs):
        super().__init__(side_len_scale_factor=side_len_scale_factor, *args, **kwargs)
        self.r = self.side_len/2/cos_deg(30) # see games.pptx
        self.h = self.side_len*sin_deg(60) # see games.pptx
        self.set_surf_rect()
        # color
        self.fg_color = Color(244, 114, 115)
        # combat variables
        self.reward_points = 25.0

    def set_points(self, angle=None):
        self.points = [pygame.math.Vector2(p).rotate(angle*self.spin_speed) + self.surf_origin_coord for p in [(0, self.r), (-self.side_len/2, -self.h + self.r), (self.side_len/2, -self.h + self.r)]]


class pentagon(shape):
    def __init__(self, side_len_scale_factor=4/3, *args, **kwargs):
        super().__init__(side_len_scale_factor=side_len_scale_factor, *args, **kwargs)
        self.r = self.side_len/2/cos_deg(54) # see games.pptx
        self.w = self.side_len*sin_deg(54) # see games.pptx
        self.h = self.side_len*cos_deg(54) # see games.pptx
        self.a = self.r * sin_deg(54) # see games.pptx
        self.set_surf_rect()
        # color
        self.fg_color = Color(114, 137, 244)
        # combat variables
        self.health = 100
        self.reward_points = 150

    def set_points(self, angle=None):
        self.points = [pygame.math.Vector2(p).rotate(angle*self.spin_speed) + self.surf_origin_coord for p in [(0, self.r), (self.w, self.r-self.h), (self.side_len/2, -self.a), (-self.side_len/2, -self.a), (-self.w, self.r-self.h)]]


class alpha_pentagon(pentagon):
    def __init__(self, side_len_scale_factor=4.0, *args, **kwargs):
        super().__init__(side_len_scale_factor=side_len_scale_factor, *args, **kwargs)
        self.center_x = SCREEN_WIDTH/2 + random.randint(-SCREEN_WIDTH/15, SCREEN_WIDTH/15)
        self.center_y = SCREEN_HEIGHT/2 + random.randint(-SCREEN_HEIGHT/15, SCREEN_HEIGHT/15)
        self.set_surf_rect()
        # spin speed
        self.spin_speed = random.uniform(-0.1, 0.1)
        # combat variables
        self.health = 3000.0
        self.penetration = 750.0
        # combat variables
        self.reward_points = 3000.0


class crasher(triangle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # color
        self.fg_color = Color(233, 115, 214)
        # combat variables
        self.reward_points = 0
        # chasing tank?
        self.chasing_tank = True
        self.chasing_speed =1


class tank(shape):
    def __init__(self, side_len_scale_factor=1.5, *args, **kwargs):
        super().__init__(side_len_scale_factor=side_len_scale_factor, *args, **kwargs)
        # body and turret
        self.r = self.side_len/2 # see games.pptx
        self.d = 0.8 * self.r # see games.pptx
        self.w = self.r # see games.pptx
        self.h = self.r / 1.5 # see games.pptx
        self.set_surf_rect(scale_factor=2.0)
        # color
        self.turret_color = Color(152, 152, 152)
        self.body_color = Color(20, 175, 216)
        self.body_border_color = Color(10, 130, 163)
        # motion variables
        self.tank_move_distance = 3
        # combat variables
        self.health_max = 50.0
        self.health = 50.0
        self.health_recover_rate = 0.05
        self.reward_points = 0.0
        self.bullets = []
        self.last_damage_time = time.time()
        self.recover_waiting_sec = 10

    def take_damage(self, damage):
        self.last_damage_time = time.time()
        self.health -= damage

    def try_recover(self):
        """
        only after certain amount of seconds of no damage, regenerating health
        """
        if self.health == self.health_max:
            return
        T2 = time.time()
        if (T2 - self.last_damage_time) >= self.recover_waiting_sec:
            self.health += self.health_recover_rate
            if self.health > self.health_max:
                self.health = self.health_max

    def time_to_regen(self):
        if self.health == self.health_max:
            return 0
        T2 = time.time()
        if (T2 - self.last_damage_time) < self.recover_waiting_sec:
            return self.recover_waiting_sec - (T2 - self.last_damage_time)
        else:
            return 0

    def draw(self, angle=None):
        self.surf.fill(self.bg_color)
        # turret
        self.points = [pygame.math.Vector2(p).rotate(self.initial_angle) + self.surf_origin_coord for p in [(self.d, self.h/2), (self.d+self.w, self.h/2), (self.d+self.w, -self.h/2), (self.d, -self.h/2)]]
        pygame.draw.polygon(surface = self.surf, color = self.turret_color, points = self.points, width = 0)
        pygame.draw.aalines(surface = self.surf, color = Color(0,0,0), closed = True, points = self.points)
        # body
        pygame.draw.circle(self.surf, self.body_color, self.surf_origin_coord, self.r)
        pygame.draw.circle(self.surf, self.body_border_color, self.surf_origin_coord, self.r, width=2)

    # Move the sprite based on keypresses
    def move(self, pressed_keys=None):

        if pressed_keys is not None:
            if pressed_keys[K_SPACE]:
                self.shoot()
            if pressed_keys[K_UP] or pressed_keys[K_w]:
                self.rect.move_ip(0, -self.tank_move_distance)
            if pressed_keys[K_DOWN] or pressed_keys[K_s]:
                self.rect.move_ip(0, self.tank_move_distance)
            if pressed_keys[K_LEFT] or pressed_keys[K_a]:
                self.rect.move_ip(-self.tank_move_distance, 0)
            if pressed_keys[K_RIGHT] or pressed_keys[K_d]:
                self.rect.move_ip(self.tank_move_distance, 0)

        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        elif self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def face(self, mouse_pos):
        self.rect_center = pygame.Vector2((self.rect.centerx, self.rect.centery))
        self.mouse_pos = pygame.Vector2(mouse_pos)
        self.direction = self.mouse_pos - self.rect_center
        self.initial_angle = atan_deg(self.direction[1], self.direction[0])

    def shoot(self):
        if not self.visible:
            return
        self.bullets.append(bullet(side_len=6.666667*self.side_len_scale_factor, initial_angle=self.initial_angle + random.randint(-2, 2)))
        self.bullets[-1].rect.centerx, self.bullets[-1].rect.centery = self.rect.centerx, self.rect.centery
        self.bullets[-1].move(incremental_steps=40)
        # recoil
        self.rect.centerx -= (self.bullets[-1].rect.centerx - self.rect.centerx) / 9 / 2
        self.rect.centery -= (self.bullets[-1].rect.centery - self.rect.centery) / 9 / 2
        self.move()
        # sound
        bullet_hit_sound.stop()
        enemydown_sound.stop()
        shoot_sound.play()


class bullet(shape):
    def __init__(self, initial_angle=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.r = self.side_len/1.3
        self.bullet_color = Color(20, 175, 216)
        self.travel_speed = 4
        self.max_steps = random.randint(800, 1400) # 40 grid unit
        self.rect_original = self.rect
        self.initial_angle = initial_angle
        self.total_steps = 0
        self.hit = 5
    
    def draw(self):
        self.surf.fill(self.bg_color)
        pygame.draw.circle(self.surf, self.bullet_color, self.surf_origin_coord, self.r)
        pygame.draw.circle(self.surf, Color(0,0,0), self.surf_origin_coord, self.r, width=1)

    def move(self, incremental_steps=None):
        if incremental_steps is None:
            incremental_steps = self.travel_speed
        self.total_steps += incremental_steps
        self.rect = self.rect_original.move(self.total_steps * cos_deg(self.initial_angle), self.total_steps * sin_deg(self.initial_angle))



def diepX():

    curr_dir = pathlib.Path(__file__).parent.absolute()
    os.chdir(curr_dir)

    pygame.mixer.init() # sound setup using defaults
    # background music

    # Sound source: http://ccmixter.org/files/Apoxode/59262
    # License: https://creativecommons.org/licenses/by/3.0/
    pygame.mixer.music.load("bkg.mp3") # Apoxode_-_Electric_1.mp3
    pygame.mixer.music.play(loops=-1)

    global shoot_sound
    global bullet_hit_sound
    global enemydown_sound

    # https://freesound.org/people/Davidsraba/sounds/347171/
    # License: http://creativecommons.org/publicdomain/zero/1.0/
    shoot_sound = pygame.mixer.Sound("shooting.ogg")

    # https://freesound.org/people/qubodup/sounds/211634/
    # License: http://creativecommons.org/licenses/by/3.0/
    bullet_hit_sound = pygame.mixer.Sound("hit.ogg")

    # https://freesound.org/people/qubodup/sounds/171971/
    # License: http://creativecommons.org/publicdomain/zero/1.0/
    enemydown_sound = pygame.mixer.Sound("explosion.ogg")

    shoot_sound.set_volume(0.5)
    bullet_hit_sound.set_volume(0.5)
    enemydown_sound.set_volume(0.5)

    pygame.init()

    global K_ESCAPE
    global K_SPACE
    global K_UP
    global K_DOWN
    global K_LEFT
    global K_RIGHT
    global K_w
    global K_s
    global K_a
    global K_d

    from pygame.locals import (
        FULLSCREEN,
        K_w,
        K_s,
        K_a,
        K_d,
        K_UP,
        K_DOWN,
        K_LEFT,
        K_RIGHT,
        K_ESCAPE,
        K_SPACE,
        KEYDOWN,
        TEXTINPUT,
        MOUSEBUTTONDOWN,
        QUIT,
    )

    global SCREEN_WIDTH
    global SCREEN_HEIGHT

    SCREEN_WIDTH = 1800
    SCREEN_HEIGHT = 900

    screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT),FULLSCREEN)
    screen_rect = screen.get_rect()
    SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.get_surface().get_size()

    angle = 0
    rotation_speed = 1

    #import pathlib

    #font = pygame.font.Font('./cour.ttf', 18)
    #ft_font = pygame.freetype.SysFont(pathlib.Path().absolute().joinpath('cour.ttf'), 18)
    #ft_font = pygame.freetype.SysFont('Courier New', 18)
    font = pygame.font.Font(pygame.font.get_default_font(), 18)

    n_squares = 20
    n_triangles = 10
    n_pentagons = 4
    n_alpha_pentagons = 1
    n_crashers = 2
    tank_player1 = tank()

    bg_grid_instance = bg_grid()

    #
    respawned_shapes = []
    shapes_death_time = []
    max_n_shapes = 200
    shape_growth_multipler = 1

    # instantiate the shapes
    shape_instances = []
    for i in range(n_alpha_pentagons): shape_instances.append(alpha_pentagon())
    for i in range(n_pentagons): shape_instances.append(pentagon())
    for i in range(n_squares): shape_instances.append(square())
    for i in range(n_triangles): shape_instances.append(triangle())
    for i in range(n_crashers): shape_instances.append(crasher())

    shape_instances.append(tank_player1)

    # init: keep the shapes separate from each other
    rect_list = []
    for this_shape in shape_instances:
        rect_list = this_shape.separate_from_other_shapes(existing_rect_list=rect_list)

    clock = pygame.time.Clock()
        
    running = True

    while running:

        screen.blit(bg_grid_instance.surf, bg_grid_instance.rect)

        # pre-computing mask
        for this_shape in shape_instances:
            this_shape.mask = pygame.mask.from_surface(this_shape.surf)

        # shapes collide with tank?
        for idx, this_shape in enumerate(shape_instances):
            if this_shape != tank_player1:
                if this_shape.health <= 1e-9:
                    tank_player1.reward_points += shape_instances[idx].reward_points
                    if len(shape_instances) <= (max_n_shapes-shape_growth_multipler):
                        for i in range(shape_growth_multipler):
                            respawned_shapes.append( type(shape_instances[idx])() )
                            shapes_death_time.append( time.time() )
                    del shape_instances[idx]
                    shoot_sound.stop()
                    bullet_hit_sound.stop()
                    enemydown_sound.play()
                else:
                    # collision detection
                    if this_shape.collide_with([tank_player1], mask_precomputed=True) != -1:
                        this_shape.health -= tank_player1.hit
                        tank_player1.take_damage(this_shape.hit)

        if tank_player1.health <= 1e-9:
            # game over
            idx = shape_instances.index(tank_player1)
            del shape_instances[idx]
            #del tank_player1
            tank_player1 = tank()
            tank_player1.visible = False
            rect_list = [this_shape.rect for this_shape in shape_instances]
            tank_player1.separate_from_other_shapes(existing_rect_list=rect_list)
            shape_instances.insert(-1, tank_player1)

        if not tank_player1.visible:
            if (time.time() - tank_player1.birth_time) >= tank_player1.respawn_wait_time:
                tank_player1.visible = True

        # bullets collide with shapes?
        if len(tank_player1.bullets) > 0:
            # pre-computing mask
            for this_bullet in tank_player1.bullets:
                this_bullet.mask = pygame.mask.from_surface(this_bullet.surf)

            for idx, this_bullet in enumerate(tank_player1.bullets):
                collision_idx = this_bullet.collide_with(shape_instances, exclude_shapes_list=[tank_player1,], mask_precomputed=True)
                if collision_idx != -1:
                    # it hit something
                    shoot_sound.stop()
                    enemydown_sound.stop()
                    bullet_hit_sound.play()
                    shape_instances[collision_idx].health -= this_bullet.hit
                    del tank_player1.bullets[idx]
                    if shape_instances[collision_idx].health <= 1e-9:
                        tank_player1.reward_points += shape_instances[collision_idx].reward_points
                        if len(shape_instances) <= (max_n_shapes-shape_growth_multipler):
                            for i in range(shape_growth_multipler):
                                respawned_shapes.append( type(shape_instances[collision_idx])() )
                                shapes_death_time.append( time.time() )
                        del shape_instances[collision_idx]
                        shoot_sound.stop()
                        bullet_hit_sound.stop()
                        enemydown_sound.play()
                elif not screen_rect.colliderect(this_bullet.rect) or this_bullet.total_steps > this_bullet.max_steps:
                    # bullet went out of fuel, or out of screen
                    del tank_player1.bullets[idx]
                else:
                    this_bullet.draw()
                    this_bullet.move()
                    screen.blit(this_bullet.surf, this_bullet.rect)

        for this_shape in shape_instances:
            if this_shape.chasing_tank:
                this_shape.chase_tank(tank_player1)
            this_shape.draw(angle=angle)
            if this_shape.visible:
                screen.blit(this_shape.surf, this_shape.rect)  # blit = Block Transfer

        if tank_player1.visible:
            #text_surface = font.render(f"fps = {clock.get_fps():.0f}", True, Color(0, 0, 0))
            text_msg = f"fps = {clock.get_fps():.0f}, reward points = {tank_player1.reward_points:.0f}, tank health = {tank_player1.health:.1f} (regen in {tank_player1.time_to_regen():.0f} sec), # shapes = {len(shape_instances)}, # bullets = {len(tank_player1.bullets)}"
            #ft_font.render_to(screen, (5, SCREEN_HEIGHT-20), text_msg, Color(0,0,0))
            text_surface = font.render(text_msg, True, Color(0, 0, 0))
            screen.blit(text_surface, dest=(5, SCREEN_HEIGHT-20))

        pygame.display.flip()

        clock.tick(60)
        angle += rotation_speed

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                #if event.key == K_SPACE:
                #    tank_player1.shoot()
            elif event.type == QUIT: # windows close button
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    tank_player1.shoot()

        # elif event.type == TEXTINPUT:
        #     tank_player1.move(text = event.text)

        pressed_keys = pygame.key.get_pressed()
        tank_player1.move(pressed_keys = pressed_keys)

        mouse_pos = pygame.mouse.get_pos()
        tank_player1.face(mouse_pos)

        tank_player1.try_recover()

        if len(respawned_shapes)>0 and len(shape_instances)<max_n_shapes:
            rect_list = [this_shape.rect for this_shape in shape_instances]
            for idx, respawn_shape in enumerate(respawned_shapes):
                if time.time() - shapes_death_time[idx] > respawn_shape.respawn_wait_time:
                    rect_list = respawn_shape.separate_from_other_shapes(existing_rect_list=rect_list)
                    if rect_list is None:
                        # cannot separate this from others
                        break
                    shape_instances.insert(0, respawn_shape)
                    del respawned_shapes[idx]
                    del shapes_death_time[idx]
                    if len(shape_instances)>=max_n_shapes:
                        break

