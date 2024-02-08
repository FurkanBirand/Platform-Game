import os
import random
import math
import pygame
from pygame.locals import *
import sys
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5
volume = 50
volume_change_rate = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))


options = ["Start", "Options", "Quit"]
selected_option = 0  # Index of the currently selected option
font = pygame.font.Font(None, 36)


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)



def draw_main_menu(window, selected_option):
    # Yeni arka plan resmini yükleyin
    background_image = pygame.image.load(join("assets", "main_menu_bg.png")).convert()
    window.blit(background_image, (0, 0))
    pygame.display.flip()


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 3
    MAX_HEALTH = 3
    HEALTH_BAR_WIDTH = 50
    HEALTH_BAR_HEIGHT = 10

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.health = self.MAX_HEALTH

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        if not self.hit:
            self.health -= 1
            self.hit = True
            self.hit_count = 0
            if self.health <= 0:
                print("Game Over")

    def heal(self):
        if self.health < self.MAX_HEALTH:
            self.health += 1

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))
        self.draw_health_bar(win, offset_x)

    def draw_health_bar(self, win, offset_x):
        bar_width = int((self.health / self.MAX_HEALTH) * self.HEALTH_BAR_WIDTH)
        pygame.draw.rect(win, (0, 255, 0), (self.rect.x - offset_x, self.rect.y - 20, bar_width, self.HEALTH_BAR_HEIGHT))
        pygame.draw.rect(win, (255, 0, 0), (self.rect.x - offset_x + bar_width, self.rect.y - 20, self.HEALTH_BAR_WIDTH - bar_width, self.HEALTH_BAR_HEIGHT))

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height))
        self.image.fill((255, 0, 0))  # Boss karakterinin rengi
        self.mask = pygame.mask.from_surface(self.image)
        self.health = 100  # Boss'un sağlığı
        self.attack_damage = 10  # Boss'un oyuncuya verdiği saldırı hasarı

    def update(self):
        # Boss karakterinin güncellendiği yer
        pass  # Henüz boss hareketi veya durumu için bir güncelleme yok

    def draw(self, window, offset_x):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))  # Boss karakterini çizmek için kullanılıyor





def main_menu():
    options = ["start", "options", "quit"]
    selected_option = 0

    while True:
        window.fill((0, 0, 0))  # Fill the window with black

        # Draw menu text
        font = pygame.font.Font(None, 36)

        for i, option in enumerate(options):
            text = font.render(f"{i + 1}. {option.capitalize()}", True, (255, 255, 255))
            text_position = (WIDTH // 2 - text.get_width() // 2, HEIGHT // 4 + i * 50)

            # Highlight the selected option
            if i == selected_option:
                pygame.draw.rect(window, (255, 0, 0), (text_position[0] - 10, text_position[1], text.get_width() + 20, text.get_height()))

            window.blit(text, text_position)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == K_RETURN:
                    return options[selected_option]




def options_menu():
    options = ["Volume", "Fullscreen", "Back"]
    selected_option = 0
    volume = 50
    fullscreen = False

    while True:
        window.fill((0, 0, 0))  # Fill the window with black

        # Draw menu text
        font = pygame.font.Font(None, 36)

        for i, option in enumerate(options):
            text = font.render(option, True, (255, 255, 255))
            text_position = (WIDTH // 2 - text.get_width() // 2, HEIGHT // 4 + i * 50)

            # Highlight the selected option
            if i == selected_option:
                pygame.draw.rect(window, (255, 0, 0), (text_position[0] - 10, text_position[1], text.get_width() + 20, text.get_height()))

            window.blit(text, text_position)

        # Display volume and fullscreen status
        volume_text = font.render(f"Volume: {volume}", True, (255, 255, 255))
        volume_position = (WIDTH // 2 - volume_text.get_width() // 2, HEIGHT // 2)
        window.blit(volume_text, volume_position)

        fullscreen_text = font.render(f"Fullscreen: {'On' if fullscreen else 'Off'}", True, (255, 255, 255))
        fullscreen_position = (WIDTH // 2 - fullscreen_text.get_width() // 2, HEIGHT // 2 + 50)
        window.blit(fullscreen_text, fullscreen_position)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == K_RETURN:
                    if options[selected_option] == "Back":
                        return
                    elif options[selected_option] == "Volume" and event.key == K_BACKSPACE:
                        # Decrease volume using BACKSPACE
                        volume = max(0, volume - 10)
                        print(f"Volume decreased to {volume}")
                    elif options[selected_option] == "Volume":
                        # Increase volume
                        volume = min(100, volume + 10)
                        print(f"Volume increased to {volume}")
                    elif options[selected_option] == "Fullscreen":
                        # Toggle fullscreen
                        fullscreen = not fullscreen
                        pygame.display.set_mode((WIDTH, HEIGHT), FULLSCREEN if fullscreen else 0)
                        print(f"Fullscreen {'enabled' if fullscreen else 'disabled'}")


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()


def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 96

    player = Player(100, 100, 50, 50)
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, HEIGHT - block_size * 4, block_size), fire]
    

    boss = Boss(500, 100, 100, 100)  # Boss karakterini ekleyin

    boss_spawned = False

    offset_x = 0
    scroll_area_width = 200

    options = ["Start", "Options", "Quit"]
    selected_option = 0

    def draw_main_menu():
        # Implement your main menu drawing logic here
        # You can use pygame functions to draw menu items and highlight the selected one
        pass

    main_menu = True

    while main_menu:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if options[selected_option] == "Start":
                        print("Starting the game...")
                        main_menu = False  # Exit the main menu loop
                    elif options[selected_option] == "Options":
                        print("Opening options menu...")
                        # You can call your options menu function here
                    elif options[selected_option] == "Quit":
                        pygame.quit()
                        quit()

        draw_main_menu()

    # Main game loop starts here
    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

                if event.key == pygame.K_h:
                    player.heal()

        player.loop(FPS)
        fire.loop()
        # Boss spawn kontrolü ve ekleme
        if not boss_spawned:
            boss = Boss(500, 100, 100, 100)
            boss_spawned = True


        boss.update()  # Boss karakterinin güncellenmesi
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)
        boss.draw(window, offset_x)  # Boss karakterinin çizilmesi

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()


if __name__ == "__main__":
    pygame.init()
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    
    choice = main_menu()

    if choice == "start":
        main(window)
    elif choice == "options":
        options_menu()
    elif choice == "quit":
        pygame.quit()
        sys.exit()
