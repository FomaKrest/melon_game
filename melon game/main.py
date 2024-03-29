import math
import sys
import os

import pygame
import random


def resize(image, coefficient):
    return pygame.transform.scale(image, (image.get_width() * coefficient, image.get_height() * coefficient))


def mirror(image, vertical=False):
    if vertical:
        return pygame.transform.flip(image, False, True)
    return pygame.transform.flip(image, True, False)


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


class Animation:
    def __init__(self, images, delay, color_key=None, cycle=True, is_mirror=False, size=0):
        self.images = [load_image(i, color_key) for i in images]
        if is_mirror:
            for i in range(len(self.images)):
                self.images[i] = mirror(self.images[i])
        if size:
            for i in range(len(self.images)):
                self.images[i] = resize(self.images[i], size)

        self.cycle = cycle
        self.delay = delay
        self.current_frame = 0
        self.start_ticks = pygame.time.get_ticks()

    def get_frame(self):
        seconds = (pygame.time.get_ticks() - self.start_ticks) / 200
        if seconds > self.delay:
            self.current_frame = self.current_frame + 1
            if not self.cycle and self.current_frame + 1 > len(self.images):
                return None
            self.current_frame %= len(self.images)
            self.start_ticks = pygame.time.get_ticks()
        return self.images[self.current_frame - 1]

    def restart(self):
        self.current_frame = 0


def generate_map(level, boss=False):
    plates = ['\\/', '\\w/', '\\ww/']
    f = list(',,,,,,,,,,,,') + ['w'] + ['.' for _ in range(70)] + ['w'] + list(',,,,,,,,,,,,')
    floor = list(',,,,,,,,,,,,') + ['w' for _ in range(72)] + list(',,,,,,,,,,,,')
    map = [f] * 5 + [floor] + [list(',,,,,,,,,,,,') + ['w'] + ['.' for _ in range(70)] +
                             ['w'] + list(',,,,,,,,,,,,') for _ in range(20)] + [floor] + [f] * 5
    enemies_count = 0
    is_player = False
    for i in range(9, len(map) - 6, 2):
        for _ in range(5):
            plate = random.choice(plates)
            pos = random.choice(range(16, 75))
            for j in range(len(plate)):
                if map[i][pos] == '.':
                    map[i][pos] = plate[j]
                else:
                    map[i][pos] = 'w'
                    break
                structure = random.choice(range(20 + level * 2))
                if structure == 1:
                    map[i - 1][pos] = 'c'
                elif structure in range(level):
                    if not is_player or not boss:
                        if enemies_count <= level + 5:
                            if is_player:
                                map[i - 1][pos] = 'e'
                                enemies_count += 1
                            else:
                                map[i - 1][pos] = '@'
                                print(i - 1, pos)
                                is_player = True
                pos += 1
    ret = []
    for i in map:
        ret.append(''.join(i))
    if boss:
        ret[-7] = ',,,,,,,,,,,,w.....................................................клбп..ПБhЛК......w,,,,,,,,,,,,'
        ret[-8] = ',,,,,,,,,,,,w...........m............................................тнН...........w,,,,,,,,,,,,'
        ret[-9] = ',,,,,,,,,,,,w.........................................................гГ...........w,,,,,,,,,,,,'
        ret[-10] = ',,,,,,,,,,,,w......................................................................w,,,,,,,,,,,,'
        ret[-11] = ',,,,,,,,,,,,w......................................................................w,,,,,,,,,,,,'
        ret[-12] = ',,,,,,,,,,,,w......................................................................w,,,,,,,,,,,,'
        ret[-13] = ret[-13].replace('c', '.')
    return ret

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
sounds_volume = 20
music_volume = 20

font_name = pygame.font.match_font('arial')
screen = pygame.display.set_mode((1080, 540))
clock = pygame.time.Clock()


def draw_text(text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, pygame.Color('black'))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface, text_rect)


class Button(pygame.sprite.Sprite):
    """Class used to create a button, use setCords to set
        position of topleft corner. Method pressed() returns
        a boolean and should be called inside the input loop."""

    def __init__(self, x, y, image):
        super().__init__(buttons_group, all_sprites)
        self.image = image
        self.rect = self.image.get_rect().move(x, y)
        self.hover = False
        self.pressed = False

    def is_pressed(self, mouse):
        if mouse[0] > self.rect.topleft[0]:
            if mouse[1] > self.rect.topleft[1]:
                if mouse[0] < self.rect.bottomright[0]:
                    if mouse[1] < self.rect.bottomright[1]:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        return False


def death_screen():
    global player, boss
    menu_button_image = resize(load_image('buttons/to_menu.png'), 4)
    menu_button_image_hover = resize(load_image('buttons/to_menu_hover.png'), 4)
    fon = resize(load_image('menu.png'), 4)
    for s in all_sprites:
        s.kill()
    menu_button = Button(300, 200, menu_button_image)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                for button in buttons_group:
                    if button.is_pressed(event.pos):
                        button.hover = True
                    else:
                        button.hover = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in buttons_group:
                        if button.is_pressed(event.pos):
                            button.pressed = True
                            break
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    for button in buttons_group:
                        button.pressed = False
        if menu_button.hover:
            menu_button.image = menu_button_image_hover
            if menu_button.pressed:
                buttons_group.empty()
                player = None
                boss = None
                main()
        else:
            menu_button.image = menu_button_image
        screen.blit(fon, (0, 0))
        draw_text(f'Вы дошли до уровня {current_level}', 30, 480, 100)
        buttons_group.update()
        buttons_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def story():
    text = '''На одно арбузное поле ветром занесло тыквянное семечко
              и среди арбузов выросла тыква по имени Рик Декард.
              Из-за его непохожести на других Рик комплексовал
              Он хотел стать таким-же арбузом как вся его семья и друзья
              Но Рик нашёл решение. Малахитовые монеты, которые были в ходу
              в его стране обладали свойствами краски если из раздробить
              и залить водой. На его теле был такой слой краски, что он
              смог стать полноценным членом общества арбузов.
              Но к несчастью в те земли пришли пираты-киборги - деревянные коробки.
              Они ограбили города и забрали весь малахит.
              Нашему герою ничего не остаётся, кроме как отомстить и вернуть
              всё отнятое у его страны. Незаметно Рик пробрался на корабль
              неприятелей, тут и начинается его приключение...'''
    back_button_image = resize(load_image('buttons/back.png', -1), 3)
    back_button_image_hover = resize(load_image('buttons/back_hover.png', -1), 3)
    back_button = Button(50, 50, back_button_image)
    fon = resize(load_image('menu.png'), 4)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    buttons_group.empty()
                    return
            elif event.type == pygame.MOUSEMOTION:
                for button in buttons_group:
                    if button.is_pressed(event.pos):
                        button.hover = True
                    else:
                        button.hover = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in buttons_group:
                        if button.is_pressed(event.pos):
                            button.pressed = True
                            break
        screen.blit(fon, (0, 0))
        y = 50
        for i in text.split('\n'):
            draw_text(i, 20, 600, y)
            y += 30
        if back_button.hover:
            back_button.image = back_button_image_hover
            if back_button.pressed:
                buttons_group.empty()
                return
        else:
            back_button.image = back_button_image
        buttons_group.update()
        buttons_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def settings():
    global sounds_volume, music_volume, sounds
    fon = resize(load_image('menu.png'), 4)
    volume_road = pygame.Surface((120, 5))
    back_button_image = resize(load_image('buttons/back.png', -1), 3)
    back_button_image_hover = resize(load_image('buttons/back_hover.png', -1), 3)
    volume_button = Button(300 + sounds_volume, 190, resize(load_image('iron_particle.png'), 4))
    music_button = Button(300 + music_volume, 270, resize(load_image('iron_particle.png'), 4))
    back_button = Button(50, 50, back_button_image)
    numbers = [resize(load_image(f'numbers/{i}.png'), 4) for i in range(10)]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    buttons_group.empty()
                    return
            elif event.type == pygame.MOUSEMOTION:
                for button in [music_button, volume_button]:
                    if button.pressed:
                        pos = event.pos[0] - 10
                        if 300 <= pos <= 400:
                            button.rect.x = pos
                        elif pos < 300:
                            button.rect.x = 300
                        elif pos > 400:
                            button.rect.x = 400
                for button in buttons_group:
                    if button.is_pressed(event.pos):
                        button.hover = True
                    else:
                        button.hover = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in buttons_group:
                        if button.is_pressed(event.pos):
                            button.pressed = True
                            break
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    for button in buttons_group:
                        button.pressed = False
                    for sound in sounds:
                        sound.set_volume(sounds_volume / 100)
                    pygame.mixer.music.set_volume(music_volume / 100)
        screen.blit(fon, (0, 0))
        screen.blit(volume_road, (300, 200))
        screen.blit(volume_road, (300, 280))
        draw_text('Звуки', 30, 200, 180)
        draw_text('Музыка', 30, 200, 260)
        sounds_volume = volume_button.rect.x - 300
        music_volume = music_button.rect.x - 300
        if back_button.hover:
            back_button.image = back_button_image_hover
            if back_button.pressed:
                buttons_group.empty()
                return
        else:
            back_button.image = back_button_image
        for i, num in enumerate(str(sounds_volume)[::-1]):
            screen.blit(numbers[int(num)], (480 - i * 25, 180))
        for i, num in enumerate(str(music_volume)[::-1]):
            screen.blit(numbers[int(num)], (480 - i * 25, 260))
        buttons_group.update()
        buttons_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def menu(is_start=True):
    back_button_image = resize(load_image('buttons/back.png', -1), 4)
    back_button_image_hover = resize(load_image('buttons/back_hover.png', -1), 4)
    settings_button_image = resize(load_image('buttons/settings.png', -1), 4)
    settings_button_image_hover = resize(load_image('buttons/settings_hover.png', -1), 4)
    story_button_image = resize(load_image('buttons/story.png', -1), 4)
    story_button_image_hover = resize(load_image('buttons/story_hover.png', -1), 4)
    start_button_image = resize(load_image('buttons/start.png', -1), 4)
    start_button_image_hover = resize(load_image('buttons/start_hover.png', -1), 4)
    is_menu = False
    if is_start:
        start_button = Button(200, 100, start_button_image)
    else:
        start_button = Button(200, 100, back_button_image)
    settings_button = Button(200, 180, settings_button_image)
    story_button = Button(200, 260, story_button_image)
    fon = resize(load_image('menu.png'), 4)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                for button in buttons_group:
                    if button.is_pressed(event.pos):
                        button.hover = True
                    else:
                        button.hover = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in buttons_group:
                        if button.is_pressed(event.pos):
                            button.pressed = True
                            break
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    for button in buttons_group:
                        button.pressed = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not is_start and is_menu:
                        buttons_group.empty()
                        return
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    is_menu = True
        if start_button.hover:
            if is_start:
                start_button.image = start_button_image_hover
            else:
                start_button.image = back_button_image_hover
            if start_button.pressed:
                buttons_group.empty()
                return
        else:
            if is_start:
                start_button.image = start_button_image
            else:
                start_button.image = back_button_image
        if settings_button.hover:
            settings_button.image = settings_button_image_hover
            if settings_button.pressed:
                buttons_group.empty()
                settings()
                settings_button.pressed = False
                if is_start:
                    start_button = Button(200, 100, start_button_image)
                else:
                    start_button = Button(200, 100, back_button_image)
                settings_button = Button(200, 180, settings_button_image)
                story_button = Button(200, 260, story_button_image)
        else:
            settings_button.image = settings_button_image
        if story_button.hover:
            story_button.image = story_button_image_hover
            if story_button.pressed:
                buttons_group.empty()
                story()
                settings_button.pressed = False
                if is_start:
                    start_button = Button(200, 100, start_button_image)
                else:
                    start_button = Button(200, 100, back_button_image)
                settings_button = Button(200, 180, settings_button_image)
                story_button = Button(200, 260, story_button_image)
        else:
            story_button.image = story_button_image
        screen.blit(fon, (0, 0))
        buttons_group.update()
        buttons_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r', encoding='utf-8') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


boss_parts = []
player = None


def generate_level(level):
    global boss_parts
    boss_parts = []
    new_player, x, y, enemies = None, None, None, []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] in 'bmcse@/\\':
                if level[y][x + 1] == ',' or level[y][x - 1] == ',':
                    Tile('empty', 'sky', x, y)
                else:
                    Tile('empty', 'empty', x, y)
            if level[y][x] == ',':
                Tile('empty', 'sky', x, y)
            elif level[y][x] == '.':
                Tile('empty', 'empty', x, y)
            elif level[y][x] == '#':
                Tile('empty', 'wood', x, y)
            elif level[y][x] in 'w\/':
                Tile('barrier', level[y][x], x, y)
            elif level[y][x] == 'f':
                Tile('barrier', 'f', x, y)
            elif level[y][x] == 'l':
                Tile('barrier', 'cloud', x, y)
            elif level[y][x] in 'кКлЛсСбБнНпПгГтh':
                Tile('empty', 'empty', x, y)
                print(boss_parts)
                boss_parts.append((x, y, level[y][x]))
            elif level[y][x] == '@':
                if not player:
                    new_player = Player(x, y)
                else:
                    new_player = None
                    player.move(x, y)
            elif level[y][x] == 'e':
                Enemy(tile_width * x, tile_height * y)
            elif level[y][x].isdigit():
                Tile('empty', level[y][x], x, y)
            elif level[y][x] == 's':
                Weapon(x, y, 'scrap', None, 3)
            elif level[y][x] == 'c':
                Chest(x, y)
            elif level[y][x] == 'm':
                Shop(x, y)
            elif level[y][x] == 'b':
                Weapon(x, y, 'bellows')

    return new_player, x, y, enemies


tile_images = {
    'cloud': resize(load_image('tiles/cloud.png', -1), 2),
    'sky': resize(load_image('tiles/sky.png', -1), 2),
    'wood': resize(load_image('ship_tiles/wood.png'), 2),
    'f': resize(load_image('ship_tiles/wood.png'), 2),
    'empty': resize(load_image('ship_tiles/fon.png'), 2),
    'w': resize(load_image('ship_tiles/plate.png'), 2),
    '\\': resize(load_image('ship_tiles/boat_left.png'), 2),
    '/': resize(load_image('ship_tiles/boat_right.png'), 2),
}


melon_right_anim = [f'melon/run_right/{i}.png' for i in range(1, 13)]
open_chest_anim = [f'chest/{i}.png' for i in range(1, 4)]
krenk_anim = [f'enemy/krenk{i}.png' for i in range(1, 4)]
scrap_hit_anim = [f'weapon/scrap_hit/{i}.png' for i in range(1, 4)]
saber_hit_anim = [f'weapon/saber_hit/{i}.png' for i in range(1, 4)]
bellows_anim = [f'weapon/bellows/{i}.png' for i in range(1, 4)]
explosion_anim = [f'explosion/{i}.png' for i in range(1, 9)]

speed_effect = resize(load_image('speed_effect.png', -1), 4)
power_effect = resize(load_image('power_effect.png', -1), 4)
shop_menu = resize(load_image('shop_menu.png', -1), 6)
rocket_target_image = resize(load_image('rocket_target.png', -1), 2)
rocket_image = resize(load_image('rocket.png', -1), 2)
bellows_image = resize(load_image('weapon/bellows.png', -1), 2)
scrap_image = resize(load_image('weapon/scrap.png', -1), 2)
saber_image = resize(load_image('weapon/saber.png', -1), 2)
leg_image = resize(load_image('enemy/leg.png', -1), 2)
box_image = resize(load_image('enemy/box.png', -1), 2)
box1_image = resize(load_image('enemy/1.png', -1), 2)
box2_image = resize(load_image('enemy/2.png', -1), 2)
iron_box_image = resize(load_image('enemy/iron_box.png', -1), 2)
krenk_image = resize(load_image('enemy/krenk1.png', -1), 2)
close_button = resize(load_image('buttons/close.png', -1), 8)
close_button_hover = resize(load_image('buttons/close_hover.png', -1), 8)
buy_button = resize(load_image('buttons/buy.png', -1), 2)
buy_button_hover = resize(load_image('buttons/buy_hover.png', -1), 2)
take_button = resize(load_image('buttons/take.png', -1), 2)
take_button_hover = resize(load_image('buttons/take_hover.png', -1), 2)
equip_button = resize(load_image('buttons/equip.png', -1), 2)
equip_button_hover = resize(load_image('buttons/equip_hover.png', -1), 2)
open_button = resize(load_image('buttons/open.png', -1), 2)
open_button_hover = resize(load_image('buttons/open_hover.png', -1), 2)
level_image = resize(load_image('buttons/level.png', -1), 4)
next_level_button = resize(load_image('buttons/next_level.png', -1), 4)
next_level_button_hover = resize(load_image('buttons/next_level_hover.png', -1), 4)
full_chest = resize(load_image('chest/3.png', -1), 2)
empty_chest = resize(load_image('chest/2.png', -1), 2)
chest_image = resize(load_image('chest/closed.png', -1), 2)
player_image = resize(load_image('melon/run_right/1.png', -1), 2)
melon_seed = load_image('melon_seed.png')
heart_image = load_image('heart.png', -1)
half_heart_image = load_image('half_heart.png', -1)
not_heart_image = load_image('not_heart.png', -1)
enemy_image = resize(load_image('enemy/head.png', -1), 2)
enemy1_image = resize(load_image('enemy/1head.png', -1), 2)
enemy2_image = resize(load_image('enemy/2head.png', -1), 2)

boss_end_sound = pygame.mixer.Sound('data/sounds/boss/end.mp3')
boss_going_sound = pygame.mixer.Sound('data/sounds/boss/going.mp3')
boss_start_sound = pygame.mixer.Sound('data/sounds/boss/start.mp3')
boss_step_sound = pygame.mixer.Sound('data/sounds/boss/step.mp3')
take_item_sound = pygame.mixer.Sound('data/sounds/take_item.mp3')
melon_shoot_sound = pygame.mixer.Sound('data/sounds/melon_shoot.mp3')
hit_sound = pygame.mixer.Sound('data/sounds/hit.mp3')
box_died_sound = pygame.mixer.Sound('data/sounds/box_died.mp3')
open_chest_sound = pygame.mixer.Sound('data/sounds/open_chest.mp3')
rocket_start_sound = pygame.mixer.Sound('data/sounds/rocket_start.mp3')
hits = [pygame.mixer.Sound(f'data/sounds/hit{i}.mp3') for i in range(1, 4)]
steps = [pygame.mixer.Sound(f'data/sounds/steps/{i}.mp3') for i in range(1, 7)]
explosion_sounds = [pygame.mixer.Sound(f'data/sounds/explosions/{i}.mp3') for i in range(1, 5)]

sounds = [
    boss_end_sound,
    boss_going_sound,
    boss_start_sound,
    boss_step_sound,
    take_item_sound,
    melon_shoot_sound,
    hit_sound,
    box_died_sound,
    open_chest_sound,
    rocket_start_sound,
]
sounds += hits
sounds += steps
sounds += explosion_sounds

pygame.mixer.music.load('data/sounds/music.mp3')
pygame.mixer.music.play(-1)

tile_width = tile_height = 50


def create_particles(position, side):
    # количество создаваемых частиц
    particle_count = 6
    # возможные скорости
    if side == 'right':
        x = range(-5, 1)
        y = range(-5, 6)
    elif side == 'left':
        x = range(1, 6)
        y = range(-5, 6)
    elif side == 'up':
        x = range(-5, 6)
        y = range(-5, -1)
    elif side == 'down':
        x = range(-5, 6)
        y = range(1, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(x), random.choice(y))


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2 - 200)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, tile_image, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_image]
        self.img = tile_image
        self.type = tile_type
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, dx, dy, img="wood_particle.png"):
        super().__init__(all_sprites, particle_group)
        self.fire = [load_image(img)]
        for scale in (5, 1, 3):
            self.fire.append(pygame.transform.scale(self.fire[0], (scale, scale)))
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


class Shop(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(structures_group, all_sprites)
        self.image = resize(load_image('soda_machine.png', -1), 2)
        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y + 3)
        self.button = None
        self.opened = False
        self.resources = {
            'heal': resize(load_image('items/heal.png', -1), 8),
            'power': resize(load_image('items/power.png', -1), 8),
            'speed': resize(load_image('items/speed.png', -1), 8)
        }
        self.malachite_image = resize(load_image('items/malachite.png'), 4)
        self.frame_image = resize(load_image('items/frame.png'), 8)
        self.hover_frame_image = resize(load_image('items/frame_hover.png'), 8)
        self.numbers = [load_image(f'numbers/{i}.png') for i in range(10)]
        self.slots = [[self.resources[i], random.choice([1, 2, 3, 4])] for i in ['heal', 'power', 'speed']]
        self.buy_buttons = [Button(308, 200, buy_button),
                            Button(508, 200, buy_button),
                            Button(708, 200, buy_button)]
        self.close_button = Button(800, 30, close_button)
        all_sprites.remove(self.close_button)
        buttons_group.remove(self.close_button)
        for i in self.buy_buttons:
            all_sprites.remove(i)
            buttons_group.remove(i)

    def update(self):
        if not player.is_shopping:
            if self.buy_buttons[0] in buttons_group:
                for i in self.buy_buttons:
                    buttons_group.remove(i)
                buttons_group.remove(self.close_button)
            if pygame.sprite.collide_rect(self, player):
                if not self.button:
                    self.button = Button(self.rect.x, self.rect.y - 20, open_button)
            elif self.button:
                self.button.kill()
                self.button = None
            if self.button:
                if self.button.hover:
                    self.button.image = open_button_hover
                    if self.button.pressed:
                        self.opened = True
                        player.is_shopping = True
                        player.shop = self
                        for i in self.buy_buttons:
                            buttons_group.add(i)
                        buttons_group.add(self.close_button)
                        self.button.kill()
                        self.button = None
                else:
                    self.button.image = open_button
        elif player.shop == self:
            self.menu()

    def menu(self):
        screen.blit(shop_menu, (230, 60))
        x, y = 270, 100
        step = 200
        if self.close_button.hover:
            self.close_button.image = close_button_hover
            if self.close_button.pressed:
                player.is_shopping = False
                self.close_button.pressed = False
        else:
            self.close_button.image = close_button
        for num, b in enumerate(self.buy_buttons):
            if b.hover:
                b.image = buy_button_hover
                if b.pressed:
                    if inventory.malachite_amount >= self.slots[num][1]:
                        inventory.malachite_amount -= self.slots[num][1]
                        name = ['heal', 'power', 'speed'][num]
                        inventory.add_item(name, 1)
                        player.weapons[name] = inventory.resources[name]
                    b.pressed = False
            else:
                b.image = buy_button
        for s in self.slots:
            screen.blit(self.frame_image, (x, y))
            screen.blit(s[0], (x, y))
            for i, num in enumerate(str(s[1])[::-1]):
                screen.blit(resize(self.numbers[int(num)], 4), (x + 21 - i * 8, y + 140))
                screen.blit(self.malachite_image, (x + 35 - i * 8, y + 125))
            x += step


class Target(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, rockets_group)
        self.image = rocket_target_image
        self.rect = self.image.get_rect().move(x, y)

    def update(self):
        pass


class Rocket(pygame.sprite.Sprite):
    def __init__(self, x, y, end_x, end_y):
        super().__init__(all_sprites, rockets_group)
        self.start_y = y
        self.start_x = x
        self.end_x = end_x
        self.end_y = end_y
        self.side = 'up'
        self.image = rocket_image
        self.start_ticks = pygame.time.get_ticks()
        self.rect = self.image.get_rect().move(x, y)
        self.explosionAnim = Animation(explosion_anim, 0.1, -1, False, False, 2)
        self.is_explosion = False
        self.target = Target(end_x, end_y)
        rocket_start_sound.play()

    def update(self):
        if not self.is_explosion:
            if self.side == 'up':
                self.rect.y -= 4
                seconds = (pygame.time.get_ticks() - self.start_ticks) / 1000
                if seconds > 3:
                    self.side = 'down'
                    self.rect.x = self.target.rect.x
                    self.rect.y = player.rect.y - 400
                    self.image = mirror(rocket_image, True)
            else:
                self.rect.y += 15
                if pygame.sprite.collide_rect(self, player):
                    player.hp -= 1
                    self.is_explosion = True
                    self.target.kill()
                    random.choice(explosion_sounds).play()
                    return
                # for b in barriers_group:
                #     if pygame.sprite.collide_rect(self, b):
                #         self.is_explosion = True
                #         random.choice(explosion_sounds).play()
                #         return
                if self.rect.y > self.target.rect.y:
                    self.is_explosion = True
                    self.target.kill()
                    random.choice(explosion_sounds).play()
                    return
                for p in boss_group:
                    if pygame.sprite.collide_rect(self, p):
                        if p.type not in 'нНт':
                            p.hp -= 1
                            self.is_explosion = True
                            self.target.kill()
                            random.choice(explosion_sounds).play()
                            return
        else:
            frame = self.explosionAnim.get_frame()
            if frame:
                screen.blit(frame, (self.rect.x - 20, self.rect.y))
            else:
                self.kill()


boss_parts_dependencies = {'к': ('л', 'tc', 'bc', (-4, 0)), 'л': ('б', 'tc', 'bc', (-4, 0)),
                           'б': ('п', 'tc', 'bc', (-4, 0)), 'п': ('г', 'cr', 'cl', (0, 0)),
                           'К': ('Л', 'tc', 'bc', (4, 0)), 'Л': ('Б', 'tc', 'bc', (4, 0)),
                           'Б': ('П', 'tc', 'bc', (4, 0)), 'П': ('Г', 'cl', 'cr', (0, 0)),
                           'Г': ('т', 'bc', 'tr', (0, 0)), 'н': ('с', 'bc', 'tc', (-1, 0)),
                           'г': ('т', 'bc', 'tl', (0, 0)), 'Н': ('С', 'bc', 'tc', (1, 0)),
                           'т': ('Н', 'bc', 'tl', (0, 0)), 'h': ('г', 'bc', 'tr', (0, 0))}
reversed_tree = {'л': 'к', 'б': 'л', 'п': 'б', 'г': 'п', 'Л': 'К', 'Б': 'Л',
                 'П': 'Б', 'Г': 'П', 'т': 'гГ', 'с': 'н', 'С': 'Н', 'Н': 'т'}


class Boss:
    def __init__(self, parts):
        self.speed = 2
        self.legs_speed = 1
        self.arms_speed = 1
        self.current_leg = 'н'
        self.triggered = False
        self.grouped = False
        self.walking = False
        self.is_hit = False
        self.current_leg_move_distance = 0
        self.arms_hit_move_distance = 0
        self.start_hit_ticks = pygame.time.get_ticks()
        self.side = 'right'
        self.left_arm = []
        self.right_arm = []
        self.shoulders = []
        for i in parts:
            if i[2] == 'т':
                self.head = BossPart(i[0], i[1], i[2])
            elif i[2] == 'н':
                self.left_leg = BossPart(i[0], i[1], i[2])
            elif i[2] == 'Н':
                self.right_leg = BossPart(i[0], i[1], i[2])
            elif i[2] in 'пблк':
                self.left_arm.append(BossPart(i[0], i[1], i[2]))
            elif i[2] in 'ПБЛК':
                self.right_arm.append(BossPart(i[0], i[1], i[2]))
            elif i[2] in 'гГ':
                self.shoulders.append(BossPart(i[0], i[1], i[2]))
            else:
                BossPart(i[0], i[1], i[2])

            for i in boss_group:
                try:
                    i.points = boss_parts_dependencies[i.type]
                    i.find_parent(boss_parts_dependencies[i.type][0])
                except KeyError:
                    i.points = None

    def trigger(self):
        self.triggered = True
        boss_start_sound.play()
        boss_going_sound.play(-1)

    def update(self):
        if self.triggered and self.grouped:
            self.follow_player()
        if all([i.grouped for i in boss_group if i.type not in 'нН']):
            self.grouped = True
        else:
            self.grouped = False

        if self.grouped:
            if not self.walking:
                self.grow_hit()
            seconds = (pygame.time.get_ticks() - self.start_hit_ticks) / 1000
            if seconds > 3.5:
                self.rockets()
                self.start_hit_ticks = pygame.time.get_ticks()
        for i in boss_group:
            i.update()
        if len(boss_group) == 3:
            for _ in range(40):
                Particle((self.head.rect.x, self.head.rect.y), random.choice(range(-5, 6)),
                         random.choice(range(-6, -1)), 'iron_particle.png')
            boss_going_sound.stop()
            boss_group.empty()
            global boss
            boss = None

    def legs_move(self):
        self.current_leg_move_distance += self.legs_speed
        if self.current_leg == 'Н':
            if self.current_leg_move_distance < 0:
                boss_step_sound.play()
                self.right_leg.rect.y += self.current_leg_move_distance
                self.current_leg_move_distance = 0
                self.current_leg = 'н'
                self.legs_speed = 1
            elif self.current_leg_move_distance >= 15:
                self.legs_speed = -3
            self.right_leg.rect.y -= self.legs_speed
        elif self.current_leg == 'н':
            if self.current_leg_move_distance < 0:
                boss_step_sound.play()
                self.left_leg.rect.y += self.current_leg_move_distance
                self.current_leg_move_distance = 0
                self.current_leg = 'Н'
                self.legs_speed = 1
            elif self.current_leg_move_distance >= 15:
                self.legs_speed = -3
            self.left_leg.rect.y -= self.legs_speed

    def follow_player(self):
        if player.rect.x > self.head.rect.x:
            self.head.image = self.head.animation_left.get_frame()
        elif player.rect.x < self.head.rect.x:
            self.head.image = self.head.animation_right.get_frame()

        if player.rect.x - 200 > self.head.rect.x:
            self.side = 'right'
            self.legs_move()
            self.walking = True
        elif player.rect.x + 200 < self.head.rect.x:
            self.side = 'left'
            self.legs_move()
            self.walking = True
        else:
            self.side = None
            self.walking = False

        if self.side == 'right':
            for i in boss_group:
                i.rect.x += self.speed
        elif self.side == 'left':
            for i in boss_group:
                i.rect.x -= self.speed

    def rockets(self):
        px = player.rect.x
        py = player.rect.y
        rockets = []
        if self.shoulders[0].groups():
            rockets.append([self.shoulders[0].rect.x, self.shoulders[0].rect.y - 30, px, py])
            # Rocket(self.shoulders[0].rect.x, self.shoulders[0].rect.y - 30, px, py)
        if self.shoulders[1].groups():
            rockets.append([self.shoulders[1].rect.centerx + 12, self.shoulders[1].rect.y - 30, px, py])
            # Rocket(self.shoulders[1].rect.centerx + 12, self.shoulders[1].rect.y - 30, px, py)
        if rockets:
            Rocket(*random.choice(rockets))

    def grow_hit(self):
        if all([i.groups() for i in self.left_arm]) or all([i.groups() for i in self.right_arm]) and self.grouped:
            self.arms_hit_move_distance += self.arms_speed
            if self.arms_hit_move_distance < 0:
                self.grouped = False
                if self.left_arm[0].groups():
                    create_particles((self.left_arm[0].rect.centerx, self.left_arm[0].rect.bottom), 'up')
                if self.right_arm[-1].groups():
                    create_particles((self.right_arm[-1].rect.centerx, self.right_arm[-1].rect.bottom), 'up')
                boss_step_sound.play()
                for i in self.left_arm:
                    if i.groups():
                        i.rect.y += self.arms_hit_move_distance
                for i in self.right_arm:
                    if i.groups():
                        i.rect.y += self.arms_hit_move_distance
                self.arms_hit_move_distance = 0
                self.arms_speed = 1
                if player.rect.bottom == max([self.left_leg.rect.bottom, self.right_leg.rect.bottom]):
                    player.yvel = -5
            elif self.arms_hit_move_distance >= 35:
                self.arms_speed = -6
            for i in self.left_arm:
                if i.groups():
                    i.rect.y -= self.arms_speed
            for i in self.right_arm:
                if i.groups():
                    i.rect.y -= self.arms_speed


class BossPart(pygame.sprite.Sprite):
    def __init__(self, x, y, part_type):
        super().__init__(all_sprites, boss_group)
        self.type = part_type
        self.parent_part = None
        self.side = 'right'
        self.grouped = False
        self.points = None
        self.hp = 3
        self.jump_power = 5
        self.xvel = 0  # скорость перемещения. 0 - стоять на месте
        self.yvel = 0
        self.left, self.right, self.up = False, False, False
        self.onGround = False
        self.speed = 1
        if self.type == 'т':
            self.animation_right = Animation(krenk_anim, 1, -1, True, False, 2)
            self.animation_left = Animation(krenk_anim, 1, -1, True, True, 2)
        if self.type in 'нН':
            self.image = leg_image
        elif self.type == 'т':
            self.image = iron_box_image
        else:
            self.image = box_image
        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y)

    def update(self):
        if self.hp <= 0 or self.rect.y > boss.left_leg.rect.y + 120:
            box_died_sound.play()
            Enemy(self.rect.x, self.rect.y)
            for _ in range(20):
                Particle((self.rect.x, self.rect.y), random.choice(range(-5, 6)), random.choice(range(-6, -1)))
            boss.grouped = False
            childs = ''
            current_child = self.type
            try:
                first_child = reversed_tree[current_child]
                while True:
                    current_child = reversed_tree[current_child]
                    childs += current_child
            except KeyError:
                for i in boss_group:
                    if self.type in 'Гг' and i.type == 'h':
                        i.kill()
                        continue
                    if i.type in childs:
                        try:
                            i.type = boss_parts_dependencies[i.type][0]
                            i.points = boss_parts_dependencies[i.type]
                        except KeyError:
                            i.points = None
                        if i.type == boss_parts_dependencies[first_child[0]][0]:
                            try:
                                i.find_parent(boss_parts_dependencies[i.type][0])
                            except KeyError:
                                pass
            for i in boss_group:
                i.grouping()
            self.kill()
            for i in boss_group:
                if i.type == 'г':
                    boss.shoulders[0] = i
                elif i.type == 'Г':
                    boss.shoulders[1] = i
        elif self.hp <= 1:
            self.image = box2_image
        elif self.hp <= 2:
            self.image = box1_image

        if boss.triggered:
            self.grouping()

    def define_points(self, obj, is_self=True):
        x, y = None, None
        if is_self:
            n = 1
        else:
            n = 2
        if self.points[n][0] == 'c':
            y = obj.rect.centery
        elif self.points[n][0] == 'b':
            y = obj.rect.bottom
        elif self.points[n][0] == 't':
            y = obj.rect.top
        if self.points[n][1] == 'c':
            x = obj.rect.centerx
        elif self.points[n][1] == 'l':
            x = obj.rect.left
        elif self.points[n][1] == 'r':
            x = obj.rect.right
        if is_self:
            return x - self.points[3][0], y - self.points[3][1]
        return x, y

    def find_parent(self, type):
        for i in boss_group:
            if i.type == type:
                if i != self:
                    self.parent_part = i
                    return i
        else:
            self.find_parent(boss_parts_dependencies[type][0])

    def grouping(self):
        if self.points and not boss.grouped:
            self_x, self_y = self.define_points(self)
            parent_x, parent_y = self.define_points(self.parent_part, False)

            if parent_x < self_x:
                self.left = True
                self.side = 'left'
            elif parent_x > self_x:
                self.right = True
                self.side = 'right'
            elif parent_y < self_y:
                self.up = True

            if parent_y + 2 >= self_y >= parent_y - 2:
                self.yvel = 0
                self.onGround = True
            elif self.up:
                self.yvel = -self.jump_power
            if parent_x + 2 >= self_x >= parent_x - 2:
                self.xvel = 0

            if self.left:
                self.xvel = -self.speed  # Лево = x- n
                if self.side == 'right':
                    self.image = mirror(self.image)
                    self.side = 'left'
            if self.right:
                self.xvel = self.speed  # Право = x + n
                if self.side == 'left':
                    self.image = mirror(self.image)
                    self.side = 'right'

            self.left, self.right, self.up = False, False, False

            if not self.onGround and self.type not in 'нН':
                self.yvel += GRAVITY

            self.onGround = False  # Мы не знаем, когда мы на земле((
            self.rect.y += self.yvel

            if self.type == 'h':
                for p in boss_group:
                    if p != self:
                        self.collide(0, self.yvel, p)
        for b in bullets_group:
            if pygame.sprite.collide_rect(self, b):
                create_particles((b.rect.x, b.rect.y), b.side)
                b.kill()
                if self.type not in 'нНт':
                    self.hp -= b.damage

        for p in barriers_group:
            self.collide(0, self.yvel, p)

        self.rect.x += self.xvel  # переносим своё положение на xvel

        if self.xvel == self.yvel == 0:
            self.grouped = True
        else:
            self.grouped = False

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


class Chest(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, structures_group)
        self.image = chest_image
        self.opened = False
        self.button = None
        self.empty = False
        self.opening = False
        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y + 5)
        self.openAnim = Animation(open_chest_anim, 0.5, -1, False, False, 2)

    def update(self):
        if self.opening:
            self.image = self.openAnim.get_frame()
            if not self.image:
                self.image = full_chest
                self.opening = False
        if not self.opened:
            if pygame.sprite.collide_rect(self, player):
                if not self.opened and not self.button:
                    self.button = Button(self.rect.x, self.rect.y - 20, open_button)
            elif self.button:
                self.button.kill()
                self.button = None

            if self.button and not self.opened:
                if self.button.hover:
                    self.button.image = open_button_hover
                    if self.button.pressed:
                        open_chest_sound.play()
                        self.button.kill()
                        self.button = None
                        self.opened = True
                        self.opening = True
                else:
                    self.button.image = open_button
        else:
            if pygame.sprite.collide_rect(self, player):
                if not self.button:
                    self.button = Button(self.rect.x, self.rect.y - 20, take_button_hover)
            elif self.button:
                self.button.kill()
                self.button = None

            if self.button:
                if self.button.hover:
                    self.button.image = take_button_hover
                else:
                    self.button.image = take_button
                if self.button.pressed:
                    take_item_sound.play()
                    self.button.kill()
                    self.image = empty_chest
                    self.empty = True
                    inventory.malachite_amount += random.choice([1, 2])
                    self.update = lambda: None


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(enemies_group, all_sprites)
        self.side = 'right'
        self.start_ticks = pygame.time.get_ticks()
        self.hp = 3
        self.xvel = 0  # скорость перемещения. 0 - стоять на месте
        self.yvel = 0
        self.speed = 3
        self.left, self.right, self.up = False, False, False
        self.weapon = Weapon(0, 0, 'saber', self)
        self.weapon.update = self.weapon.taken_update
        self.onGround = True
        self.image = enemy_image
        self.move(pos_x, pos_y)

    def move(self, x, y):
        self.x = x
        self.y = y
        self.rect = self.image.get_rect().move(x, y)

    def shoot(self):
        seconds = (pygame.time.get_ticks() - self.start_ticks) / 1000
        if seconds > 2:
            self.start_ticks = pygame.time.get_ticks()
            self.weapon.hit()

    def update(self):
        if self.rect.y > 2000:
            self.kill()
        self.weapon.side = self.side
        if self.hp <= 1:
            if self.side == 'right':
                self.image = enemy2_image
            else:
                self.image = mirror(enemy2_image)
        elif self.hp <= 2:
            if self.side == 'right':
                self.image = enemy1_image
            else:
                self.image = mirror(enemy1_image)
        if self.hp <= 0:
            box_died_sound.play()
            for _ in range(20):
                Particle((self.rect.x, self.rect.y), random.choice(range(-5, 6)), random.choice(range(-6, -1)))
            self.weapon.kill()
            self.kill()

        if self.rect.x + 1000 > player.rect.x > self.rect.x + 60:
            self.right = True
        elif self.rect.x - 1000 < player.rect.x < self.rect.x - 50:
            self.left = True
        if self.rect.x > player.rect.x:
            if self.side == 'right':
                self.image = mirror(self.image)
                self.side = 'left'
        elif self.rect.x < player.rect.x:
            if self.side == 'left':
                self.image = mirror(self.image)
                self.side = 'right'
        if player.rect.y + 40 >= self.rect.y >= player.rect.y - 40:
            self.shoot()
        if self.up:
            if self.onGround:  # прыгаем, только когда можем оттолкнуться от земли
                self.yvel = -JUMP_POWER
        if self.left:
            self.xvel = -self.speed  # Лево = x- n
            if self.side == 'right':
                self.image = mirror(self.image)
                self.side = 'left'
        if self.right:
            self.xvel = self.speed  # Право = x + n
            if self.side == 'left':
                self.image = mirror(self.image)
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
    def __init__(self, sx, sy, side, sender, damage=1):
        super().__init__(bullets_group, all_sprites)
        self.image = melon_seed
        self.damage = damage
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

    def collide(self):
        if self.sender == 'player':
            for e in enemies_group:
                if pygame.sprite.collide_rect(self, e):
                    create_particles((self.rect.x, self.rect.y), self.side)
                    e.hp -= self.damage
                    self.kill()
                    return
        elif self.sender == 'enemy':
            if pygame.sprite.collide_rect(self, player):
                player.hp -= self.damage
                random.choice(hits).play()
                self.kill()
        for t in barriers_group:
            if pygame.sprite.collide_rect(self, t):
                create_particles((self.rect.x, self.rect.y), self.side)
                self.killed = True


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.side = 'right'
        self.side_hit = None
        self.x = pos_x
        self.y = pos_y
        self.move_speed = 6
        self.current_slot = 0
        self.hp = 10
        self.on_mast = True
        self.xvel = 0  # скорость перемещения. 0 - стоять на месте
        self.yvel = 0
        self.weapons = {None: None, 'scrap': None, 'bellows': None, 'power': None, 'speed': None, 'heal': None}
        self.weapon = None
        self.onGround = True
        self.damage = 1
        self.image = player_image
        self.is_shopping = False
        self.effects = {'power': False, 'speed': False}

        self.boltAnimRight = Animation(melon_right_anim, 0.2, -1, True, False, 2)
        self.boltAnimLeft = Animation(melon_right_anim, 0.2, -1, True, True, 2)
        self.numbers = [load_image(f'numbers/{i}.png') for i in range(10)]

        self.speed_start_ticks = pygame.time.get_ticks()
        self.power_start_ticks = pygame.time.get_ticks()
        self.start_ticks_shoot = pygame.time.get_ticks()
        self.start_ticks_step = pygame.time.get_ticks()
        self.move(pos_x, pos_y)
        self.hp_bar = HpBar(self.rect.x, self.rect.y, self.hp)

    def move(self, x, y):
        self.x = x
        self.y = y
        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y)

    def shoot(self):
        if self.is_shopping:
            return
        if not self.weapon:
            seconds = (pygame.time.get_ticks() - self.start_ticks_shoot) / 200
            if seconds > 2:
                melon_shoot_sound.play()
                self.start_ticks_shoot = pygame.time.get_ticks()
                Bullet(self.rect.centerx, self.rect.top, self.side, 'player', self.damage)
        elif self.weapon == self.weapons['scrap']:
            seconds = (pygame.time.get_ticks() - self.start_ticks_shoot) / 200
            if seconds > 2:
                self.weapon.hit()
                self.start_ticks_shoot = pygame.time.get_ticks()
        elif self.weapon == self.weapons['bellows']:
            seconds = (pygame.time.get_ticks() - self.start_ticks_shoot) / 200
            if seconds > 6.5:
                self.weapon.hit()
                self.yvel = -JUMP_POWER
                self.start_ticks_shoot = pygame.time.get_ticks()
        elif self.weapon == self.weapons['heal']:
            if self.hp < 10:
                self.weapons['heal'].amount -= 1
                self.hp += 1
        elif self.weapon == self.weapons['power']:
            if not self.effects['power']:
                self.effects['power'] = True
                self.weapons['power'].amount -= 1
                self.damage *= 2
                if self.weapons['scrap']:
                    self.weapons['scrap'].damage *= 2
                self.power_start_ticks = pygame.time.get_ticks()
        elif self.weapon == self.weapons['speed']:
            if not self.effects['speed']:
                self.effects['speed'] = True
                self.weapons['speed'].amount -= 1
                self.move_speed *= 2
                self.speed_start_ticks = pygame.time.get_ticks()

    def update(self, left, right, up):
        x, y = 20, 20
        for k, v in self.effects.items():
            if v and k == 'power':
                seconds = (pygame.time.get_ticks() - self.power_start_ticks) // 1000
                screen.blit(power_effect, (x, y))
                for i, num in enumerate(str(20 - seconds)):
                    screen.blit(resize(self.numbers[int(num)], 4), (x + 60 + i * 20, y + 10))
                if seconds >= 20:
                    self.effects['power'] = False
                    self.damage /= 2
                    if self.weapons['scrap']:
                        self.weapons['scrap'].damage /= 2
                y += 80
            elif v and k == 'speed':
                seconds = (pygame.time.get_ticks() - self.speed_start_ticks) // 1000
                screen.blit(speed_effect, (x, y))
                for i, num in enumerate(str(20 - seconds)):
                    screen.blit(resize(self.numbers[int(num)], 4), (x + 60 + i * 20, y + 10))
                if seconds >= 20:
                    self.effects['speed'] = False
                    self.move_speed /= 2
        if self.is_shopping:
            return
        self.weapon = self.weapons[inventory.slots[self.current_slot].name]
        if inventory.current_slot != self.current_slot:
            inventory.set_current_slot(self.current_slot)
        if self.weapon:
            self.weapon.side = self.side
        if up:
            if self.onGround:  # прыгаем, только когда можем оттолкнуться от земли
                self.yvel = -JUMP_POWER
        if left:
            self.image = self.boltAnimLeft.get_frame()
            if self.boltAnimLeft.current_frame == 0:
                if self.yvel in [0.75, 0.35, 0]:
                    seconds = (pygame.time.get_ticks() - self.start_ticks_step) / 200
                    if seconds >= 1:
                        random.choice(steps).play()
                        self.start_ticks_step = pygame.time.get_ticks()
            self.xvel = -self.move_speed  # Лево = x - n
            self.side = 'left'
        elif right:
            self.image = self.boltAnimRight.get_frame()
            if self.boltAnimRight.current_frame == 0:
                if self.yvel in [0.75, 0.35, 0]:
                    seconds = (pygame.time.get_ticks() - self.start_ticks_step) / 200
                    if seconds >= 1:
                        random.choice(steps).play()
                        self.start_ticks_step = pygame.time.get_ticks()
            self.xvel = self.move_speed  # Право = x + n
            self.side = 'right'
        else:
            self.xvel = 0
            # if self.weapon_name == 'sekira':
            #     if self.side == 'right':
            #         self.image = sekira_melon_right
            #     else:
            #         self.image = sekira_melon_left

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
                self.image = player_image
            else:
                self.image = mirror(player_image)
            self.side_hit = None

        if not self.onGround:
            self.yvel += GRAVITY

        self.onGround = False  # Мы не знаем, когда мы на земле((
        self.rect.y += self.yvel
        for p in barriers_group:
            self.collide(0, self.yvel, p)
        for p in boss_group:
            if self.collide(0, self.yvel, p):
                if not boss.triggered:
                    boss.trigger()
        self.rect.x += self.xvel  # переносим свои положение на xvel
        for p in barriers_group:
            self.collide(self.xvel, 0, p)
        for p in boss_group:
            if self.collide(self.xvel, 0, p):
                if not boss.triggered:
                    boss.trigger()

        self.hp_bar.update(self.hp, self.rect.x, self.rect.y)
        if self.hp <= 0:
            death_screen()

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
            return True
        return False


class Weapon(pygame.sprite.Sprite):
    def __init__(self, x, y, name, owner=None, damage=1.0):
        super().__init__(structures_group, weapons_group, all_sprites)
        self.taken = False
        self.side = None
        self.button = None
        self.owner = owner
        self.amplitude = 8
        self.freq = 0.002
        self.damage = damage
        self.start_ticks = pygame.time.get_ticks()
        self.offset = 0
        self.is_hit = False
        self.name = name
        if name == 'scrap':
            self.image = scrap_image
            self.hitRightAnim = Animation(scrap_hit_anim, 0.3, -1, False, False, 2)
            self.hitLeftAnim = Animation(scrap_hit_anim, 0.3, -1, False, True, 2)
            self.x_right = 30
            self.x_left = -30
        elif name == 'saber':
            self.image = saber_image
            self.hitRightAnim = Animation(saber_hit_anim, 0.3, -1, False, False, 2)
            self.hitLeftAnim = Animation(saber_hit_anim, 0.3, -1, False, True, 2)
            self.x_right = 30
            self.x_left = -30
        elif name == 'bellows':
            self.image = load_image('weapon/bellows.png', -1)
            self.hitRightAnim = Animation(bellows_anim, 0.3, -1, False, False)
            self.hitLeftAnim = Animation(bellows_anim, 0.3, -1, False, True)
            self.x_right = 30
            self.x_left = -20

        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y)
        self.img = self.image

    def hit(self):
        hit_sound.play()
        self.is_hit = True

    def update(self):
        if not self.owner:
            self.owner = player
        if not self.taken:
            # harmonic motion
            time = (pygame.time.get_ticks() - self.start_ticks)
            offset = self.amplitude * math.sin(time * self.freq) // 1
            self.rect.y += self.offset
            self.offset = offset
            self.rect.y -= offset

            self.player_collision()
        else:
            inventory.add_item(self.name, 1)
            self.owner.weapons[self.name] = self
            self.update = self.taken_update

    def taken_update(self):
        if self.owner.weapon != self:
            if self in structures_group:
                structures_group.remove(self)
        else:
            if self not in structures_group:
                structures_group.add(self)
        if self.side == 'right':
            self.rect.x = self.owner.rect.x + self.x_right
            self.rect.y = self.owner.rect.y
            self.image = self.img
        else:
            self.rect.x = self.owner.rect.x + self.x_left
            self.rect.y = self.owner.rect.y
            self.image = mirror(self.img)
        if self.is_hit:
            if self.side == 'right':
                self.image = self.hitRightAnim.get_frame()
            else:
                self.image = self.hitLeftAnim.get_frame()
            if not self.image:
                self.enemy_collision()
                self.is_hit = False
                if self.side == 'right':
                    self.image = self.img
                else:
                    self.image = mirror(self.img)
                self.hitLeftAnim.restart()
                self.hitRightAnim.restart()

    def enemy_collision(self):
        if self.name == 'scrap':
            for e in enemies_group:
                if pygame.sprite.collide_rect(self, e):
                    e.hp -= self.damage
            if boss:
                if boss.triggered:
                    for p in boss_group:
                        if p.type not in 'нНт':
                            if pygame.sprite.collide_rect(self, p):
                                p.hp -= self.damage
        elif self.name == 'saber':
            if pygame.sprite.collide_rect(self, player):
                player.hp -= self.damage

    def player_collision(self):
        if pygame.sprite.collide_rect(self, player):
            if not self.taken and not self.button:
                self.button = Button(self.rect.x - 10, self.rect.y - 20, equip_button)
        elif self.button:
            self.button.kill()
            self.button = None

        if self.button and not self.taken:
            if self.button.hover:
                self.button.image = equip_button_hover
                if self.button.pressed:
                    take_item_sound.play()
                    self.button.kill()
                    self.taken = True
            else:
                self.button.image = equip_button


class Inventory:
    def __init__(self):
        self.resources = {
            'scrap': InventoryItem('scrap', "items/scrap.png"),
            'bellows': InventoryItem('bellows', 'items/bellows.png'),
            'heal': InventoryItem('heal', 'items/heal.png'),
            'power': InventoryItem('power', 'items/power.png'),
            'speed': InventoryItem('speed', 'items/speed.png')
        }
        self.malachite_amount = 0
        self.slots = [InventoryItem(None, None) for _ in range(8)]
        self.current_slot = 0
        self.malachite_image = resize(load_image('items/malachite.png'), 2)
        self.frame_image = resize(load_image('items/frame.png'), 2)
        self.hover_frame_image = resize(load_image('items/frame_hover.png'), 2)
        self.numbers = [load_image(f'numbers/{i}.png') for i in range(10)]

    def set_current_slot(self, slot):
        self.current_slot = slot
        self.slots[slot].choose()

    def update(self):
        self.draw_slots()

    def add_item(self, name, amount):
        self.resources[name].amount += amount
        for name, item in self.resources.items():
            if item.amount != 0 and item not in self.slots:
                for s in self.slots:
                    if not s.name:
                        index = self.slots.index(s)
                        self.slots[index] = item
                        self.set_current_slot(self.current_slot)
                        break

    def draw_slots(self):
        x, y = 400, 500
        step = 40
        for n, s in enumerate(self.slots):
            if s.chosen:
                screen.blit(self.hover_frame_image, (x, y))
            else:
                screen.blit(self.frame_image, (x, y))
            if s.name:
                if s.amount == 0:
                    self.slots[n] = InventoryItem(None, None)
                    self.slots[n].chosen = True
                    continue
                if s.taken:
                    x1, y1 = pygame.mouse.get_pos()
                    screen.blit(s.image, (x1, y1))
                    for i, num in enumerate(str(s.amount)[::-1]):
                        screen.blit(self.numbers[int(num)], (x1 + 21 - i * 4, y1 + 20))
                else:
                    screen.blit(s.image, (x, y))
                    for i, num in enumerate(str(s.amount)[::-1]):
                        screen.blit(self.numbers[int(num)], (x + 21 - i * 4, y + 20))
            x += step
        screen.blit(self.malachite_image, (x, y))
        for i, num in enumerate(str(self.malachite_amount)[::-1]):
            screen.blit(resize(self.numbers[int(num)], 2), (x + 21 - i * 8, y + 20))


class InventoryItem:
    def __init__(self, name, image, size=2):
        self.chosen = False
        self.taken = False
        if image:
            self.image = resize(load_image(image, -1), size)
            self.name = name
        else:
            self.name = None
            self.image = None
        self.amount = 0

    def choose(self):
        for slot in inventory.slots:
            slot.chosen = False
        self.chosen = True


class HpBar:
    def __init__(self, pos_x, pos_y, hp):
        self.hp = hp
        self.x = pos_x
        self.y = pos_y + 100
        self.hearts = []
        self.move(422, 280)
        print(pos_x, pos_y)

    def move(self, x, y):
        for i in range((self.hp + 1) // 2):
            self.hearts.append(Heart(x + (i * 12), y))

    def update(self, hp, x, y):
        self.x = x
        self.y = y + 80
        if hp % 2:
            for num, i in enumerate(self.hearts):
                if num + 1 <= hp // 2:
                    heart = 'heart'
                elif num + 1 == hp // 2 + 1:
                    heart = 'half_heart'
                else:
                    heart = 'not_heart'
                i.update(heart, self.x + (num * 10) - 5, self.y - 20)
        else:
            for num, i in enumerate(self.hearts):
                if num + 1 <= hp // 2:
                    heart = 'heart'
                else:
                    heart = 'not_heart'
                i.update(heart, self.x + (num * 10) - 5, self.y - 20)


class Heart(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__(hearts_group)
        self.image = heart_image
        self.move(x_pos, y_pos)

    def move(self, x, y):
        self.rect = self.image.get_rect().move(x, y)

    def update(self, type, x, y):
        # self.rect.x = x
        # self.rect.y = y
        if type == 'heart':
            self.image = heart_image
        elif type == 'half_heart':
            self.image = half_heart_image
        elif type == 'not_heart':
            self.image = not_heart_image


class LevelBar(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(inventory_group)
        self.image = level_image
        self.rect = self.image.get_rect().move(400, 20)
        self.is_next_level = False
        self.button = None
        self.numbers = [resize(load_image(f'numbers/{i}.png'), 4) for i in range(10)]

    def update(self, num):
        global current_level, next_level
        for i, n in enumerate(str(num)[::-1]):
            screen.blit(self.numbers[int(n)], (561 - i * 25, 35))
        if self.button:
            if self.button.hover:
                self.button.image = next_level_button_hover
                if self.button.pressed:
                    take_item_sound.play()
                    self.button.kill()
                    self.button = None
                    current_level += 1
                    next_level = True
                    self.is_next_level = False
            else:
                self.button.image = next_level_button
        elif self.is_next_level and not self.button:
            print(1)
            self.button = Button(400, 90, next_level_button)
            all_sprites.remove(self.button)
            self.is_next_level = False


class Barrier(pygame.sprite.Sprite):
    def __init__(self, cords1, cords2):
        super().__init__(barriers_group, all_sprites)
        self.image = pygame.Surface((cords2[0] - cords1[0] + tile_width, tile_height))
        self.rect = pygame.Rect(cords1[0], cords1[1], cords2[0] - cords1[0] + tile_width, tile_height)


def make_barriers(l):
    barriers = []
    for i in range(len(l)):
        for j in range(len(l[i])):
            if l[i][j] in 'w\\/lf':
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
        Barrier(i[0], i[-1])


def main():
    global level_map, player, level_x, level_y, enemies, current_level, bullets, next_level, inventory, level_bar,\
        boss, camera, left, right, up, running, all_sprites, barriers_group, tiles_group, enemies_group, player_group,\
        bullets_group, rockets_group, particle_group, hearts_group, structures_group, buttons_group, boss_group,\
        weapons_group, inventory_group

    all_sprites = pygame.sprite.Group()
    barriers_group = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    enemies_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    bullets_group = pygame.sprite.Group()
    rockets_group = pygame.sprite.Group()
    particle_group = pygame.sprite.Group()
    hearts_group = pygame.sprite.Group()
    structures_group = pygame.sprite.Group()
    buttons_group = pygame.sprite.Group()
    boss_group = pygame.sprite.Group()
    weapons_group = pygame.sprite.Group()
    inventory_group = pygame.sprite.Group()
    for sound in sounds:
        sound.set_volume(0.2)
    pygame.mixer.music.set_volume(0.2)
    menu()
    level_map = load_level('ship_level.txt')
    make_barriers(level_map)
    player, level_x, level_y, enemies = generate_level(level_map)
    current_level = 0
    bullets = []
    next_level = False
    inventory = Inventory()
    inventory.set_current_slot(0)
    level_bar = LevelBar()
    is_menu = False
    boss = None
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
                elif event.key == pygame.K_ESCAPE:
                    if player.is_shopping:
                        player.is_shopping = False
                    elif is_menu == False:
                        buttons_group.empty()
                        is_menu = True
                        menu(False)
                        if level_bar.is_next_level:
                            level_bar.button = Button(400, 90, next_level_button)
                            all_sprites.remove(level_bar.button)
                elif event.key in range(49, 57):
                    player.current_slot = event.key - 49
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    up = False
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    right = False
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    left = False
                elif event.key == pygame.K_ESCAPE:
                    is_menu = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in buttons_group:
                        if button.is_pressed(event.pos):
                            button.pressed = True
                            break
                    else:
                        player.shoot()
                elif event.button == 4:
                    player.current_slot = (player.current_slot - 1) % 8
                elif event.button == 5:
                    player.current_slot = (player.current_slot + 1) % 8
            elif event.type == pygame.MOUSEMOTION:
                for button in buttons_group:
                    if button.is_pressed(event.pos):
                        button.hover = True
                    else:
                        button.hover = False

        screen.fill(pygame.Color(0, 0, 0))
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        if boss:
            boss.update()
        if next_level:
            tiles_group.empty()
            barriers_group.empty()
            boss_group.empty()
            boss = None
            structures_group.empty()
            buttons_group.empty()
            bullets_group.empty()
            enemies_group.empty()
            for i in weapons_group:
                if not i.taken:
                    i.kill()
            all_sprites.empty()
            all_sprites.add(player)
            if current_level % 2 == 0:
                level_map = generate_map(current_level, True)
            else:
                level_map = generate_map(current_level)
            make_barriers(level_map)
            _, level_x, level_y, enemies = generate_level(level_map)
            if current_level % 2 == 0:
                boss = Boss(boss_parts)
            next_level = False
        if not enemies_group and not boss:
            level_bar.is_next_level = True
        bullets_group.update()
        enemies_group.update()
        particle_group.update()
        weapons_group.update()

        tiles_group.draw(screen)
        player_group.draw(screen)
        enemies_group.draw(screen)
        bullets_group.draw(screen)
        particle_group.draw(screen)
        rockets_group.draw(screen)
        boss_group.draw(screen)
        structures_group.draw(screen)
        hearts_group.draw(screen)
        rockets_group.update()
        inventory.update()
        structures_group.update()
        player.update(left, right, up)
        buttons_group.draw(screen)
        inventory_group.draw(screen)
        level_bar.update(current_level)

        pygame.display.flip()

        clock.tick(FPS)


main()

sys.exit()
