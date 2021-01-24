import random


def generate_map(level, boss=False):
    plates = ['\\/', '\\w/', '\\ww/']
    floor = ['w' for _ in range(72)]
    map = [floor] + [['w'] + ['.' for _ in range(70)] + ['w'] for _ in range(20)] + [floor]
    enemies_count = 0
    for i in range(4, len(map) - 1, 2):
        for _ in range(5):
            plate = random.choice(plates)
            pos = random.choice(range(1, level * 5 + 50))
            for j in range(len(plate)):
                if map[i][pos] == '.':
                    map[i][pos] = plate[j]
                else:
                    map[i][pos] = 'w'
                    break
                structure = random.choice(range(20))
                if structure == 1:
                    map[i - 1][pos] = 'c'
                elif structure in range(level) and not boss:
                    if enemies_count <= level + 10:
                        map[i - 1][pos] = 'e'
                        enemies_count += 1
                pos += 1
    ret = []
    for i in map:
        ret.append(''.join(i))
    if boss:
        ret[-2] = 'w.....................................................клбп..ПБhЛК......w'
        ret[-3] = 'w...........m............................................тнН...........w'
        ret[-4] = 'w.........................................................гГ...........w'
        ret[-5] = 'w......................................................................w'
        ret[-6] = ret[-6].replace('c', '.')
    return ret