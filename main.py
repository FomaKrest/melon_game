import sys
import pygame
import random
from Animate import Animation, load_image


pygame.init()
pygame.key.set_repeat(5, 0)

FPS = 50
WIDTH = 500
HEIGHT = 500
MOVE_SPEED = 6
STEP = 1
JUMP_POWER = 10
GRAVITY = 0.35
ANIMATION_DELAY = 35

font_name = pygame.font.match_font('arial')
screen = pygame.display.set_mode((1080, 540))
clock = pygame.time.Clock()


all_sprites = pygame.sprite.Group()
barriers_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
particle_group = pygame.sprite.Group()
hearts_group = pygame.sprite.Group()
structures_group = pygame.sprite.Group()
buttons_group = pygame.sprite.Group()


def draw_text(text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, pygame.Color('black'))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface, text_rect)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    global flower
    new_player, x, y, enemies = None, None, None, []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', 'empty', x, y)
            elif level[y][x] == '#':
                Tile('empty', 'dirt', x, y)
            elif level[y][x] in ['d', 'l', 'r', 'u', 'D', 'L', 'R', 'U', '<', '>', '^', 'v', '=', 'N']:
                Tile('empty', 'empty', x, y)
                Tile('barrier', level[y][x], x, y)
            elif level[y][x] == '@':
                Tile('empty', 'empty', x, y)
                new_player = Player(x, y)
            elif level[y][x] == 'e':
                Enemy(x, y)
                Tile('empty', 'empty', x, y)
            elif level[y][x].isdigit():
                Tile('empty', level[y][x], x, y)
            elif level[y][x] == 's':
                Tile('empty', 'empty', x, y)
                Sekira(x, y)
            elif level[y][x] == 'f':
                Tile('empty', 'empty', x, y)
                Flower(x, y)
            elif level[y][x] == 'c':
                Tile('empty', 'empty', x, y)
                Chest(x, y)

    return new_player, x, y, enemies


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def resize(image, coefficient):
    return pygame.transform.scale(image, (image.get_width() * coefficient, image.get_height() * coefficient))


tile_images = {
    'dirt': resize(load_image('tiles/dirt_tile.png'), 2),
    'empty': load_image('sky.png'),
    '<': resize(load_image('tiles/grass_3_l.png', -1), 2),
    '>': resize(load_image('tiles/grass_3_r.png', -1), 2),
    '^': resize(load_image('tiles/grass_3_u.png', -1), 2),
    'v': resize(load_image('tiles/grass_3_d.png', -1), 2),
    '=': resize(load_image('tiles/grass=.png', -1), 2),
    'N': resize(load_image('tiles/grassN.png', -1), 2)
}
for i in range(1, 5):
    tile_images[f'{i}'] = resize(load_image(f'tiles/angle_grass_tile_{i}.png'), 2)
for i in ['u', 'l', 'd', 'r']:
    tile_images[i] = resize(load_image(f'tiles/{i}_grass_tile.png'), 2)
    tile_images[i.upper()] = resize(load_image(f'tiles/grass_2_{i}.png'), 2)


s = 15

sekira_hit_right_anim = []
for i in range(1, 6):
    sekira_hit_right_anim.append(f'sekira/hit_right/{i}.png')

sekira_hit_left_anim = []
for i in range(1, 6):
    sekira_hit_left_anim.append(f'sekira/hit_left/{i}.png')

melon_right_anim = []
for i in range(1, 13):
    melon_right_anim.append(f'melon/run_right/{i}.png')

melon_left_anim = []
for i in range(1, 13):
    melon_left_anim.append(f'melon/run_left/{i}.png')

sekira_melon_run_right_anim = []
for i in range(1, 13):
    sekira_melon_run_right_anim.append(f'sekira/run_right/{i}.png')

sekira_melon_run_left_anim = []
for i in range(1, 13):
    sekira_melon_run_left_anim.append(f'sekira/run_left/{i}.png')

sekira_melon_hit_right_anim = []
for i in range(1, 13):
    sekira_melon_hit_right_anim.append(f'sekira/hit_right/{i}.png')

sekira_melon_hit_left_anim = []
for i in range(1, 13):
    sekira_melon_hit_left_anim.append(f'sekira/hit_left/{i}.png')

melon_shoot_anim = []
for i in range(1, 7):
    melon_shoot_anim.append(f'melon/shoot/{i}.png')

open_chest_anim = []
for i in range(1, 3):
    open_chest_anim.append(f'chest/{i}.png')

open_button = resize(load_image('buttons/open.png', -1), 2)
open_button_hower = resize(load_image('buttons/open_hower.png', -1), 2)
opened_chest = resize(load_image('chest/2.png', -1), 2)
chest_image = resize(load_image('chest/closed.png', -1), 2)
sekira_melon_right = resize(load_image('sekira/melon_right.png', -1), 2)
sekira_melon_left = resize(load_image('sekira/melon_left.png', -1), 2)
sekira_image = resize(load_image('sekira/sekira.png', -1), 2)
flower_image = load_image('flower.png', -1)
dead_flower_image = load_image('dead_flower.png', -1)
player_image = resize(load_image('melon/run_right/1.png', -1), 2)
melon_seed = load_image('melon_seed.png')
heart_image = load_image('heart.png', -1)
half_heart_image = load_image('half_heart.png', -1)
not_heart_image = load_image('not_heart.png', -1)
bullet_image = load_image('bullet.png', -1)
bullet_image = pygame.transform.scale(
    bullet_image, (bullet_image.get_width() // 30,
               bullet_image.get_height() // 30))
enemy_image = resize(load_image('box.png', -1), 2)
enemy1_image = resize(load_image('1box.png', -1), 2)
enemy2_image = resize(load_image('2box.png', -1), 2)
stick_image = load_image('stick.png', -1)
stick_image = pygame.transform.scale(
    stick_image, (stick_image.get_width() // s,
               stick_image.get_height() // s))

melon_shoot_sound = pygame.mixer.Sound('data/sounds/melon_shoot.mp3')
melon_shoot_sound.set_volume(0.2)
flower_died_sound = pygame.mixer.Sound('data/sounds/flower_died.mp3')
sekira_hit_sound = pygame.mixer.Sound('data/sounds/sekira_hit.mp3')
sekira_hit_sound.set_volume(0.2)
box_died_sound = pygame.mixer.Sound('data/sounds/box_died.mp3')
box_died_sound.set_volume(0.2)
open_chest_sound = pygame.mixer.Sound('data/sounds/open_chest.mp3')
open_chest_sound.set_volume(0.2)
hits = [pygame.mixer.Sound(f'data/sounds/hit{i}.mp3') for i in range(1, 4)]
for i in hits:
    i.set_volume(0.2)
steps = [pygame.mixer.Sound(f'data/sounds/steps/{i}.mp3') for i in range(1, 6)]

tile_width = tile_height = 50


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        # if obj.rect.x < -obj.rect.width:
        #     obj.rect.x += (self.field_size[0] + 1) * obj.rect.width
        # if obj.rect.x >= (self.field_size[0]) * obj.rect.width:
        #     obj.rect.x += -obj.rect.width * (1 + self.field_size[0])
        obj.rect.y += self.dy
        # if obj.rect.y < -obj.rect.height:
        #     obj.rect.y += (self.field_size[1] + 1) * obj.rect.height
        # if obj.rect.y >= (self.field_size[1]) * obj.rect.height:
        #     obj.rect.y += -obj.rect.height * (1 + self.field_size[1])

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2 - 200)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


class Button(pygame.sprite.Sprite):
    """Class used to create a button, use setCords to set
        position of topleft corner. Method pressed() returns
        a boolean and should be called inside the input loop."""
    def __init__(self, x, y, image):
        super().__init__(buttons_group, all_sprites)
        self.image = image
        self.rect = self.image.get_rect().move(x, y)
        self.hower = False
        self.pressed = False

    def is_pressed(self, mouse):
        if mouse[0] > self.rect.topleft[0]:
            if mouse[1] > self.rect.topleft[1]:
                if mouse[0] < self.rect.bottomright[0]:
                    if mouse[1] < self.rect.bottomright[1]:
                        return True
                    else: return False
                else: return False
            else: return False
        return False


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, tile_image, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_image]
        self.img = tile_image
        self.type = tile_type
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [load_image("wood_particle.png")]
    for scale in (5, 1, 3):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites, particle_group)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой (значение константы)
        self.gravity = GRAVITY

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if self.rect.y > 850:
            self.kill()


class Chest(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, structures_group)
        self.image = chest_image
        self.opened = False
        self.button = None
        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y + 5)
        self.openAnim = Animation(open_chest_anim, 0.5, -1, False, 2)

    def update(self):
        if pygame.sprite.collide_rect(self, player):
            if not self.opened and not self.button:
                self.button = Button(self.rect.x, self.rect.y - 20, open_button)
            #self.opened = True
        elif self.button:
            self.button.kill()
            self.button = None

        if self.button:
            if self.button.hower:
                self.button.image = open_button_hower
                if self.button.pressed:
                    self.button.kill()
                    self.opened = True
            else:
                self.button.image = open_button
        if self.opened:
            self.image = self.openAnim.get_frame()
            if not self.image:
                self.image = opened_chest
                self.update = lambda: None


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(enemies_group, all_sprites)
        self.side = 'right'
        self.x = pos_x
        self.y = pos_y
        self.start_ticks = pygame.time.get_ticks()
        self.hp = 3
        self.xvel = 0  # скорость перемещения. 0 - стоять на месте
        self.yvel = 0
        self.speed = 3
        self.left, self.right, self.up = False, False, False
        self.onGround = True
        self.image = enemy_image
        self.move(pos_x, pos_y)

    def move(self, x, y):
        self.x = x
        self.y = y
        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y)

    def shoot(self):
        seconds = (pygame.time.get_ticks() - self.start_ticks) / 1000
        if seconds > 2:
            self.start_ticks = pygame.time.get_ticks()
            Bullet(self.rect.centerx, self.rect.top, self.side, 'enemy')

    def update(self):
        if self.hp <= 2:
            self.image = enemy1_image
        if self.hp <= 1:
            self.image = enemy2_image
        if self.hp <= 0:
            box_died_sound.play()
            for _ in range(20):
                Particle((self.rect.x, self.rect.y), random.choice(range(-5, 6)), random.choice(range(-6, -1)))
            self.kill()

        if self.rect.x + 1000 > player.rect.x > self.rect.x + 100:
            self.right = True
        elif self.rect.x - 1000 < player.rect.x < self.rect.x - 100:
            self.left = True
        if player.rect.y + 40 >= self.rect.y >= player.rect.y - 40:
            self.shoot()
        if self.up:
            if self.onGround:  # прыгаем, только когда можем оттолкнуться от земли
                self.yvel = -JUMP_POWER
        if self.left:
            self.xvel = -self.speed  # Лево = x- n
            if self.side == 'right':
                self.image = pygame.transform.flip(self.image, True, False)
                self.side = 'left'
        if self.right:
            self.xvel = self.speed  # Право = x + n
            if self.side == 'left':
                self.image = pygame.transform.flip(self.image, True, False)
                self.side = 'right'

        if not (self.left or self.right):  # стоим, когда нет указаний идти
            self.xvel = 0

        self.left, self.right, self.up = False, False, False

        if not self.onGround:
            self.yvel += GRAVITY

        self.onGround = False  # Мы не знаем, когда мы на земле((
        self.rect.y += self.yvel
        for p in enemies_group:
            if p != self:
                self.collide(0, self.yvel, p)
        for p in barriers_group:
            self.collide(0, self.yvel, p)

        self.rect.x += self.xvel  # переносим свои положение на xvel

        for p in enemies_group:
            if p != self:
                self.collide(self.xvel, 0, p)
        for p in barriers_group:
            self.collide(self.xvel, 0, p)

    def collide(self, xvel, yvel, p):
        if pygame.sprite.collide_rect(self, p):
            if xvel > 0:  # если движется вправо
                self.up = True
                self.rect.right = p.rect.left  # то не движется вправо

            if xvel < 0:  # если движется влево
                self.up = True
                self.rect.left = p.rect.right  # то не движется влево

            if yvel > 0:  # если падает вниз
                self.rect.bottom = p.rect.top  # то не падает вниз
                self.onGround = True  # и становится на что-то твердое
                self.yvel = 0  # и энергия падения пропадает

            if yvel < 0:  # если движется вверх
                self.rect.top = p.rect.bottom  # то не движется вверх
                self.yvel = 0


class Bullet(pygame.sprite.Sprite):
    def __init__(self, sx, sy, side, sender):
        super().__init__(bullets_group, all_sprites)
        if sender == 'enemy':
            self.image = bullet_image
        else:
            self.image = melon_seed
        self.sender = sender
        self.killed = False
        self.side = side
        if side == 'right':
            self.speed = 10
        elif side == 'left':
            self.image = pygame.transform.flip(self.image, True, False)
            self.speed = -10
        self.move(sx, sy, side)

    def move(self, x, y, side):
        if side == 'right':
            self.rect = self.image.get_rect().move(x + 20, y + 27)
        else:
            self.rect = self.image.get_rect().move(x - 20, y + 27)

    def update(self):
        if self.killed:
            self.kill()
        self.rect.x += self.speed
        self.collide()

    @staticmethod
    def create_particles(position, side):
        # количество создаваемых частиц
        particle_count = 6
        # возможные скорости
        if side == 'right':
            x = range(-5, 1)
            y = range(-5, 6)
        else:
            x = range(1, 6)
            y = range(-5, 6)
        for _ in range(particle_count):
            Particle(position, random.choice(x), random.choice(y))

    def collide(self):
        if self.sender == 'player':
            for e in enemies_group:
                if pygame.sprite.collide_rect(self, e):
                    self.create_particles((self.rect.x, self.rect.y), self.side)
                    e.hp -= 1
                    self.kill()
                    return
        elif self.sender == 'enemy':
            if pygame.sprite.collide_rect(self, player):
                player.hp -= 1
                random.choice(hits).play()
                self.kill()
        for t in barriers_group:
            if pygame.sprite.collide_rect(self, t):
                self.create_particles((self.rect.x, self.rect.y), self.side)
                self.killed = True


class Flower(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, structures_group)
        self.image = flower_image
        self.died = False
        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y + 30)

    def update(self):
        if not self.died:
            if pygame.sprite.collide_rect(self, player):
                flower_died_sound.play()
                self.image = dead_flower_image
                self.died = True
                self.update = lambda: None


class Stick(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.x = pos_x
        self.y = pos_y
        self.original_image = self.image = stick_image
        self.move(pos_x, pos_y)
        self.rot = 90
        self.rot_speed = 10
        self.last_angle = 0
        self.last_update = pygame.time.get_ticks()
        self.center_image = (54, 250)

    def move(self, x, y):
        self.x = x
        self.y = y
        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y)

    def update(self, x, y, side):
        self.rect.x = x
        self.rect.y = y

    def rotate(self, side, pivot):
        if side == 'right':
            self.rot_speed = -10
        else:
            self.rot_speed = 10
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = self.rot + self.rot_speed
            self.image = pygame.transform.rotate(self.original_image, self.rot - 90)
            self.rect = self.image.get_rect()
            self.rect.center = pivot
            self.x = self.rect.x
            self.y = self.rect.y


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.side = 'right'
        self.side_hit = None
        self.x = pos_x
        self.y = pos_y
        self.hp = 10
        self.xvel = 0  # скорость перемещения. 0 - стоять на месте
        self.yvel = 0
        self.weapon_name = 'seeds'
        self.weapon = None
        self.onGround = True
        self.image = player_image

        self.boltAnimRight = Animation(melon_right_anim, 0.2, -1, True, 2)
        self.boltAnimLeft = Animation(melon_left_anim, 0.2, -1, True, 2)
        self.sekiraAnimHitRight = Animation(sekira_hit_right_anim, 0.5, -1, False, 2)
        self.sekiraAnimHitLeft = Animation(sekira_hit_left_anim, 0.5, -1, False, 2)

        #self.stick = Stick(pos_x, pos_y - tile_height)
        self.hp_bar = HpBar(pos_x, pos_y, self.hp)
        self.start_ticks_shoot = pygame.time.get_ticks()
        self.start_ticks_step = pygame.time.get_ticks()
        self.move(pos_x, pos_y)

    def move(self, x, y):
        self.x = x
        self.y = y
        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y)

    def shoot(self):
        if self.weapon_name == 'seeds':
            seconds = (pygame.time.get_ticks() - self.start_ticks_shoot) / 200
            if seconds > 2:
                melon_shoot_sound.play()
                self.start_ticks_shoot = pygame.time.get_ticks()
                Bullet(self.rect.centerx, self.rect.top, self.side, 'player')
        elif self.weapon_name == 'sekira':
            seconds = (pygame.time.get_ticks() - self.start_ticks_shoot) / 200
            if seconds > 3:
                sekira_hit_sound.play()
                self.side_hit = self.side
                self.start_ticks_shoot = pygame.time.get_ticks()

    def update(self, left, right, up):
        if up:
            if self.onGround:  # прыгаем, только когда можем оттолкнуться от земли
                self.yvel = -JUMP_POWER
        if left:
            self.image = self.boltAnimLeft.get_frame()
            self.xvel = -MOVE_SPEED  # Лево = x - n
            self.side = 'left'
        elif right:
            self.image = self.boltAnimRight.get_frame()
            self.xvel = MOVE_SPEED  # Право = x + n
            self.side = 'right'
        else:
            self.xvel = 0
            if self.weapon_name == 'sekira':
                if self.side == 'right':
                    self.image = sekira_melon_right
                else:
                    self.image = sekira_melon_left

        if (left or right) and self.onGround:
            seconds = (pygame.time.get_ticks() - self.start_ticks_step) / 200
            if seconds >= 2.5:
                random.choice(steps).play()
                self.start_ticks_step = pygame.time.get_ticks()

        if self.side_hit:
            for e in enemies_group:
                if pygame.sprite.collide_rect(self, e):
                    e.hp -= 0.1

        if self.side_hit == 'right':
            self.image = self.sekiraAnimHitRight.get_frame()
        elif self.side_hit == 'left':
            self.image = self.sekiraAnimHitLeft.get_frame()

        if not self.image:
            self.sekiraAnimHitRight.restart()
            self.sekiraAnimHitLeft.restart()
            if self.side == 'right':
                self.image = sekira_melon_right
            else:
                self.image = sekira_melon_left
            self.side_hit = None

        if not self.onGround:
            self.yvel += GRAVITY

        self.onGround = False  # Мы не знаем, когда мы на земле((
        self.rect.y += self.yvel
        for p in barriers_group:
            self.collide(0, self.yvel, p)
        self.rect.x += self.xvel  # переносим свои положение на xvel
        for p in barriers_group:
            self.collide(self.xvel, 0, p)
        self.hp_bar.update(self.hp, self.rect.x, self.rect.y)

    def collide(self, xvel, yvel, p):
        if pygame.sprite.collide_rect(self, p):  # если есть пересечение платформы с игроком
            if xvel > 0:  # если движется вправо
                self.rect.right = p.rect.left  # то не движется вправо
            elif xvel < 0:  # если движется влево
                self.rect.left = p.rect.right  # то не движется влево
            if yvel > 0:  # если падает вниз
                self.rect.bottom = p.rect.top  # то не падает вниз
                self.onGround = True  # и становится на что-то твердое
                self.yvel = 0  # и энергия падения пропадает
            elif yvel < 0:  # если движется вверх
                self.rect.top = p.rect.bottom  # то не движется вверх
                self.yvel = 0  # и энергия прыжка пропадает


class Sekira(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(structures_group, all_sprites)
        self.taked = False
        self.hit_side = None
        self.image = sekira_image
        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y)

    def update(self):
        if not self.taked:
            self.player_collision()
        else:
            player.weapon_name = 'sekira'
            self.kill()

    def player_collision(self):
        if pygame.sprite.collide_rect(self, player):
            self.taked = True
            player.boltAnimRight = Animation(sekira_melon_run_right_anim, 0.2, -1, True, 2)
            player.boltAnimLeft = Animation(sekira_melon_run_left_anim, 0.2, -1, True, 2)
            if player.side == 'right':
                player.image = sekira_melon_right
            else:
                player.image = sekira_melon_left
            player.rect.height = player.image.get_height()
            player.rect.width = player.image.get_width()


class HpBar:
    def __init__(self, pos_x, pos_y, hp):
        self.hp = hp
        self.x = pos_x
        self.y = pos_y + 100
        self.hearts = []
        self.move(pos_x, pos_y)

    def move(self, x, y):
        for i in range((self.hp + 1) // 2):
            self.hearts.append(Heart(x, y))

    def update(self, hp, x, y):
        self.x = x
        self.y = y + 80
        if hp % 2:
            for num, i in enumerate(self.hearts):
                if num + 1 <= hp // 2:
                    i.update('heart', self.x + (num * 10), self.y - 20)
                elif num + 1 == hp // 2 + 1:
                    i.update('half_heart', self.x + (num * 10), self.y - 20)
                else:
                    i.update('not_heart', self.x + (num * 10), self.y - 20)
        else:
            for num, i in enumerate(self.hearts):
                if num + 1 <= hp // 2:
                    i.update('heart', self.x + (num * 10), self.y - 20)
                else:
                    i.update('not_heart', self.x + (num * 10), self.y - 20)


class Heart(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__(all_sprites, hearts_group)
        self.image = heart_image
        self.move(x_pos, y_pos)

    def move(self, x, y):
        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y)

    def update(self, type, x, y):
        self.rect.x = x
        self.rect.y = y
        if type == 'heart':
            self.image = heart_image
        elif type == 'half_heart':
            self.image = half_heart_image
        elif type == 'not_heart':
            self.image = not_heart_image


class Barrier(pygame.sprite.Sprite):
    def __init__(self, cords1, cords2, max_width):
        super().__init__(barriers_group, all_sprites)
        self.image = pygame.Surface((cords2[0] - cords1[0] + tile_width, tile_height))
        self.rect = pygame.Rect(cords1[0], cords1[1], cords2[0] - cords1[0] + 50, 50)


def make_barriers(max_width):
    barriers = []
    l = load_level('level1.txt')
    for i in range(len(l)):
        for j in range(len(l[i])):
            if l[i][j] not in ['.', '#', 'e', '@', 'f', 's', 'c']:
                barriers.append((j * tile_width, i * tile_height))
    barriers.sort(key=lambda a: (a[1], a[0]))

    groups = []
    stack = []
    for i in barriers:
        if stack:
            if stack[-1][1] == i[1] and stack[-1][0] + tile_width == i[0]:
                stack.append(i)
            else:
                groups.append(stack)
                stack = [i]

        else:
            stack.append(i)
    groups.append(stack)
    for i in groups:
        Barrier(i[0], i[-1], max_width)


start_screen()
level_map = load_level('level1.txt')
player, level_x, level_y, enemies = generate_level(level_map)
bullets = []

make_barriers(level_x)
camera = Camera()
left, right, up = 0, 0, 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                left = True
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                right = True
            elif event.key in [pygame.K_UP, pygame.K_w]:
                up = True
            elif event.key == pygame.K_SPACE:
                player.shoot()
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_UP, pygame.K_w]:
                up = False
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                right = False
            elif event.key in [pygame.K_LEFT, pygame.K_a]:
                left = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for button in buttons_group:
                if button.is_pressed(event.pos):
                    button.pressed = True
                    break
            else:
                player.shoot()
        elif event.type == pygame.MOUSEMOTION:
            for button in buttons_group:
                if button.is_pressed(event.pos):
                    button.hower = True
                else:
                    button.hower = False
    player.update(left, right, up)

    screen.fill(pygame.Color(0, 0, 0))
    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)
    tiles_group.draw(screen)
    player_group.draw(screen)
    enemies_group.draw(screen)
    bullets_group.draw(screen)
    hearts_group.draw(screen)
    particle_group.draw(screen)
    structures_group.draw(screen)
    buttons_group.draw(screen)

    bullets_group.update()
    enemies_group.update()
    particle_group.update()
    structures_group.update()

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()
sys.exit()
