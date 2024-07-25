import random
import tkinter.messagebox

import pygame
import tkinter as tk
from tkinter import simpledialog

img_path = 'img/'
scree_width = 900
scree_height = 500
GameOver = False


class Map:
    map_name_list = [img_path + 'map1.png', img_path + 'map2.png']

    def __init__(self, x, y, img_index):
        self.image = pygame.image.load(Map.map_name_list[img_index])
        self.position = (x, y)
        self.grow = True

    def load_map(self):
        Game.window.blit(self.image, self.position)


class Plant(pygame.sprite.Sprite):
    def __init__(self):
        super(Plant, self).__init__()
        self.live = True

    def load_image(self):
        if hasattr(self, 'image') and hasattr(self, 'rect'):
            Game.window.blit(self.image, self.rect)
        else:
            print('can not load plant image')


class Sunflower(Plant):
    def __init__(self, x, y):
        super(Sunflower, self).__init__()
        self.image_middle = pygame.transform.scale(pygame.image.load('img/sunflower0.png').convert_alpha(), [70, 70])
        self.image_left = pygame.image.load('img/peashooter.png')
        self.rect = self.image_middle.get_rect()
        self.rect.x = x + 15
        self.rect.y = y + 15
        self.price = 50
        self.hp = 100
        self.time_count = 0

    def produce_sun(self):
        self.time_count += 1
        if self.time_count == 100:
            Game.suns += 25
            self.time_count = 0

    def display_sunflower(self):
        Game.window.blit(self.image_middle, self.rect)


class PeaShooter(Plant):
    def __init__(self, x, y):
        super(PeaShooter, self).__init__()
        self.image = pygame.transform.scale(pygame.image.load('img/peashooter.png').convert_alpha(), [70, 70])
        self.rect = self.image.get_rect()
        self.rect.x = x + 10
        self.rect.y = y + 15
        self.price = 100
        self.hp = 200
        self.shot_count = 0

    def shot(self):
        fire = False
        for zombie in Game.zombie_list:
            if zombie.rect.y + 10 == self.rect.y and zombie.rect.x < 900:
                if zombie.rect.x > self.rect.x:
                    fire = True
        if self.live and fire:
            self.shot_count += 1
            if self.shot_count == 25:
                peabullet = PeaBullet(self)
                Game.peabullet_list.append(peabullet)
                self.shot_count = 0

    def display(self):
        Game.window.blit(self.image, self.rect)


class PeaBullet(pygame.sprite.Sprite):
    def __init__(self, peashooter):
        super(PeaBullet, self).__init__()
        self.live = True
        self.image = pygame.transform.scale(pygame.image.load('img/peabullet.png').convert_alpha(), [20, 20])
        self.damage = 100
        self.speed = 10
        self.rect = self.image.get_rect()
        self.rect.x = peashooter.rect.x + 70
        self.rect.y = peashooter.rect.y + 15

    def move(self):
        if self.rect.x < scree_width:
            self.rect.x += self.speed
        else:
            self.live = False

    def hit_zombie(self):
        for zombie in Game.zombie_list:
            if pygame.sprite.collide_rect(self, zombie):
                self.live = False
                zombie.hp -= self.damage
                if zombie.hp <= 0:
                    zombie.live = False

    def display(self):
        Game.window.blit(self.image, self.rect)


class Zombie(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Zombie, self).__init__()
        self.image = pygame.transform.scale(pygame.image.load('img/zombie.png').convert_alpha(), [90, 90])
        self.rect = self.image.get_rect()
        self.rect.x = x + 10
        self.rect.y = y + 5
        self.hp = 1000
        self.damage = 2
        self.speed = 0.6
        self.live = True
        self.stop = False

    def move(self):
        if self.live and not self.stop:
            self.rect.x -= self.speed
            if self.rect.x < -80:
                Game.game_over()

    def touch_plant(self):
        for plant in Game.plants_list:
            if pygame.sprite.collide_rect(self, plant):
                self.stop = True
                self.eat(plant)

    def eat(self, plant):
        plant.hp -= self.damage
        if plant.hp <= 0:
            a = plant.rect.y // 100
            b = plant.rect.x // 100
            tar_map = Game.map_list[a][b]
            tar_map.grow = True
            plant.live = False
            self.stop = False

    def display_zombie(self):
        Game.window.blit(self.image, self.rect)


class Game:
    score = 0
    suns = 150
    map_points_list = []
    map_list = []
    plants_list = []
    peabullet_list = []
    zombie_list = []
    count_zombie = 0
    produce_zombie = 200

    @staticmethod
    def init_window():
        pygame.display.init()
        Game.window = pygame.display.set_mode([scree_width, scree_height])
        pygame.display.set_caption("Plants vs. Zombies")

    @staticmethod
    def init_points():
        for height in range(0, 6):
            points = []
            for width in range(9):
                point = (width, height)
                points.append(point)
            Game.map_points_list.append(points)

    @staticmethod
    def init_map():
        for points in Game.map_points_list:
            temp_map_list = list()
            for point in points:
                if (point[0] + point[1]) % 2 == 0:
                    sub_map = Map(point[0] * 100, point[1] * 100, 0)
                else:
                    sub_map = Map(point[0] * 100, point[1] * 100, 1)
                temp_map_list.append(sub_map)
            Game.map_list.append(temp_map_list)

    @staticmethod
    def load_map():
        for map_list in Game.map_list:
            for maps in map_list:
                maps.load_map()

    @staticmethod
    def load_plants():
        for plant in Game.plants_list:
            if plant.live:
                if isinstance(plant, Sunflower):
                    plant.display_sunflower()
                    plant.produce_sun()
                elif isinstance(plant, PeaShooter):
                    plant.display()
                    plant.shot()
            else:
                Game.plants_list.remove(plant)

    @staticmethod
    def load_peabullets():
        for bullet in Game.peabullet_list:
            if bullet.live:
                bullet.display()
                bullet.move()
                bullet.hit_zombie()
            else:
                Game.peabullet_list.remove(bullet)

    def deal_events(self):
        event_lists = pygame.event.get()
        for event in event_lists:
            if event.type == pygame.QUIT:
                self.game_over()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x = event.pos[0] // 100
                y = event.pos[1] // 100
                tar_map = Game.map_list[y][x]
                if event.button == 1:
                    if tar_map.grow and Game.suns >= 50:
                        sunflower = Sunflower(tar_map.position[0], tar_map.position[1])
                        Game.plants_list.append(sunflower)
                        tar_map.grow = False
                        Game.suns -= 50
                elif event.button == 3:
                    if tar_map.grow and Game.suns >= 100:
                        peashooter = PeaShooter(tar_map.position[0], tar_map.position[1])
                        Game.plants_list.append(peashooter)
                        tar_map.grow = False
                        Game.suns -= 100

    @staticmethod
    def init_zombies():
        for i in range(0, 5):
            dis = random.randint(1, 5) * 100
            zombie = Zombie(900 + dis, i * 100)
            Game.zombie_list.append(zombie)

    @staticmethod
    def load_zombies():
        for zombie in Game.zombie_list:
            if zombie.live:
                zombie.display_zombie()
                zombie.move()
                zombie.touch_plant()
            else:
                Game.zombie_list.remove(zombie)

    def start_game(self):
        self.init_window()
        self.init_points()
        self.init_map()
        self.init_zombies()

        while not GameOver:
            self.load_map()
            self.load_plants()
            self.load_peabullets()
            self.deal_events()
            self.load_zombies()
            Game.count_zombie += 1
            if Game.count_zombie == Game.produce_zombie:
                self.init_zombies()
                Game.count_zombie = 0
            pygame.time.wait(10)
            pygame.display.update()

    @staticmethod
    def game_over():
        pygame.time.wait(500)
        root = tk.Tk()
        root.withdraw()
        tkinter.messagebox.showinfo('Game Over', 'Zombies Win!')
        global GameOver
        GameOver = True


if __name__ == '__main__':
    game = Game()
    game.start_game()
