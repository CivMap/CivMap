from collections import defaultdict
import struct

missing_blocks = defaultdict(int)
def print_missing_blocks():
    for item_id, n in missing_blocks.items():
        print('could not find color for %6s %3i:%-2i %ix'
            % (hex(item_id), item_id & 0xfff, item_id >> 12, n))

item_colors = {}
def gen_item_colors(item_colors_path):
    if item_colors: return
    for line in open(item_colors_path):
        id_tup, color = map(lambda e: e.split(','), line.split(':'))
        item_id = int(id_tup[0]) | int(id_tup[1]) << 12
        item_colors[item_id] = tuple(map(lambda c: int(c) / 255, color[:3]))

def get_item_color(item_id):
    color = item_colors.get(item_id)
    if color is None:
        color = item_colors.get(item_id & 0x0fff)
        if color is None:
            missing_blocks[item_id] += 1
            return (1,0,1)
    return color

def get_simple_block_color(column, x, z):
    level1, level2, level3, level4, biome = struct.unpack('>IIIIB', column)

    block_id = level1 >> 8 & 0xffff
    y = level1 >> 24
    if block_id == 0:
        block_id = level4 >> 8 & 0xffff
        y = level4 >> 24

    shade = 1 - (((256-y)/4)%3)*.02
    r, g, b = get_item_color(block_id)
    r, g, b = r * shade, g * shade, b * shade

    if level2:  # underwater
        block_id = level2 >> 8 & 0xffff
        r, g, b = get_item_color(block_id)
        b = b*.6 + .4

    return r, g, b
