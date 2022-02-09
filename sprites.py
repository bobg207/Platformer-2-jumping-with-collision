import pygame
from settings import *

pygame.init()


class Block(pygame.sprite.Sprite):
    """class to create a block object for walls and platforms
    x_loc, y_loc: the position of the block in the LAYOUT
    tile_size: the size of the block from settings TILE_SIZE
    """

    def __init__(self, x_loc, y_loc, tile_size):
        super().__init__()
        # the Surface class can be replaced with a specific image
        self.image = pygame.Surface((tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x_loc
        self.rect.y = y_loc

    def update(self, x_shift):
        """method for shifting the blocks by x_shift creating a horizontal 'camera' effect"""

        self.rect.x += x_shift


class Layout():
    '''class to handle creating the level and interaction between objects in the level
    layout_map: the list containing the layout for a level
    display: the surface that the layout is being drawn to
    '''

    def __init__(self, layout_map, display):
        self.display = display
        self.blocks = None
        self.players = None
        self.create_layout(layout_map)  # call method, pass in the map param

        self.camera_shift = 0  # updated based on player movement

    def create_layout(self, map):
        """method to create layout
        map: the layout_map passed into the __init__
        """
        self.blocks = pygame.sprite.Group()
        self.players = pygame.sprite.GroupSingle()

        for i, row in enumerate(map):
            for j, col in enumerate(row):
                x_val = j * TILE_SIZE
                y_val = i * TILE_SIZE

                if col == '1':
                    block = Block(x_val, y_val, TILE_SIZE)
                    self.blocks.add(block)
                if col == 'P':
                    player = Player(x_val, y_val, TILE_SIZE)
                    self.players.add(player)

    def move_camera(self):

        left_edge = DISPLAY_WIDTH // 4
        right_edge = DISPLAY_WIDTH - left_edge

        # get the sprite that is in the Group, only needed to shorten amount of typing throughout this method
        player = self.players.sprite
        player_x = player.rect.centerx
        dir_x = player.dir_x

        if player_x < left_edge and dir_x == -1:  # close to left and moving left
            self.camera_shift = 5
            player.speed = 0
        elif player_x > right_edge and dir_x == 1:  # close to right and moving right
            self.camera_shift = -5
            player.speed = 0
        else:
            self.camera_shift = 0
            player.speed = 5

    def horiz_collision(self):
        player = self.players.sprite
        player.rect.x += player.dir_x * player.speed  # moved from player class

        for block in self.blocks.sprites():
            if block.rect.colliderect(player.rect):
                if player.dir_x < 0:
                    player.rect.left = block.rect.right
                elif player.dir_x > 0:
                    player.rect.right = block.rect.left

    def vert_collision(self):
        player = self.players.sprite
        player.add_gravity()  # moved from player class

        for block in self.blocks.sprites():
            if block.rect.colliderect(player.rect):
                if player.dir_y < 0:
                    player.rect.top = block.rect.bottom
                    player.dir_y = 0
                elif player.dir_y > 0:
                    player.rect.bottom = block.rect.top
                    player.dir_y = 0
                    player.on_ground = True

        if player.on_ground and player.dir_y < 0 or player.dir_y > 1:
            player.on_ground = False

    def update(self):
        """method to update all objects on the map
                called in the game loop"""

        # level walls and platforms
        self.blocks.update(self.camera_shift)
        self.blocks.draw(self.display)
        self.move_camera()

        # level player
        self.players.update()
        self.horiz_collision()
        self.vert_collision()
        self.players.draw(self.display)


class Player(pygame.sprite.Sprite):
    """class to create a player object
    x, y: the location of the player in the layout
    """

    def __init__(self, x_loc, y_loc, tile_size):
        super().__init__()
        self.tile_size = tile_size
        # change the image to actual image
        self.image = pygame.Surface((self.tile_size, self.tile_size))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x_loc
        self.rect.y = y_loc
        self.on_ground = True

        # player movement
        self.dir_y = 0  # up=-, down=+
        self.dir_x = 0  # rt=1, lft=-1
        self.gravity = 0.8
        self.init_velo = -5
        self.speed = 5

    def update(self):
        self.get_keys()

        # to keep the player from dropping off screen, b4 collision coded
        if self.rect.bottom >= DISPLAY_HEIGHT - TILE_SIZE:
            self.rect.bottom = DISPLAY_HEIGHT - TILE_SIZE

    def add_gravity(self):
        self.dir_y += self.gravity
        print(self.dir_y)
        if self.dir_y >= 10:
            self.dir_y = 10

        self.rect.y += self.dir_y

    def jump(self):
        self.dir_y = self.init_velo

    def get_keys(self):
        """method to handle keyboard presses"""
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.dir_x = 1
        elif keys[pygame.K_LEFT]:
            self.dir_x = -1
        else:
            self.dir_x = 0

        if keys[pygame.K_SPACE] and self.on_ground:
            self.jump()
            self.on_ground = False

