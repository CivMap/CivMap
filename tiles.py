# generate leaflet tiles from VoxelMap cache
import os
import sys
import time
from collections import defaultdict
import struct
import cairo
from zipfile import ZipFile

shardIds = {
    # 'abydos': '',
    'dracontas': 'a7cbf239-6c11-4146-a715-ef0a9827b4c4',
    # 'eilon': '',
    'isolde': '197e2c4f-2fd6-464a-8754-53b24d9f7898',
    'naunet': 'de730958-fa83-4e73-ab7f-bfdab8e27960',
    # 'ovid': '',
    # 'padzahr': '',
    'rokko': 'a72e4777-ad62-4e3b-a4e0-8cf2d15147ea',
    # 'sheol': '',
    'tigrillo': 'a358b10c-7041-40c5-ac5e-db5483a9dfc2',
    'tjikko': '44f4b133-a646-461a-a14a-5fd8c8dbc59c',
    'ulca': '7f03aa4d-833c-4b0c-9d3b-a65a5c6eada0',
    'volans': 'b25abb31-fd1e-499d-a5b5-510f9d2ec501',
}

region_size = 16*16  # blocks per region edge

item_colors = {}
for line in open('item-colors'):
    id_tup, color = map(lambda e: e.split(','), line.split(':'))
    item_id = int(id_tup[0]) | int(id_tup[1]) << 12
    item_colors[item_id] = tuple(map(lambda c: int(c) / 255, color[:3]))

missing_blocks = defaultdict(int)
def print_missing_blocks():
    for item_id, n in missing_blocks.items():
        print('could not find color for %6s %3i:%-2i %ix'
            % (hex(item_id), item_id & 0xfff, item_id >> 12, n))

def get_block_color(item_id):
    color = item_colors.get(item_id)
    if color is None:
        color = item_colors.get(item_id & 0x0fff)
        if color is None:
            missing_blocks[item_id] += 1
            return (1,0,1)
    return color

def civ_world_path(base_path, world_id=None, name=None):
    if world_id is None: world_id = shardIds[name]
    return base_path + '/cache/mc.civcraft.co/' + world_id + '/Overworld (dimension 0)/'

def get_region_file_from_zip(zip_path):
    return ZipFile(zip_path).open('data')

def get_world_regions(world_path):
    return [tuple(map(int, region[:-4].split(','))) for region in os.listdir(world_path)]


class TileRenderer(object):
    def __init__(self, world_path, tiles_path):
        self.world_path = world_path
        self.tiles_path = tiles_path
        os.makedirs(self.tiles_path, exist_ok=True)

    def render_tiles(self, print_progress=True):
        regions = get_world_regions(self.world_path)
        last_progress = time.time()
        for rn, (rx, rz) in enumerate(regions):
            if print_progress and last_progress + 3 < time.time():
                last_progress += 3
                print('%i/%i tiles' % (rn, len(regions)))
            self.render_tile(rx, rz)

    def render_tile(self, rx, rz):
        region_file = get_region_file_from_zip(self.world_path + '/%i,%i.zip' % (rx, rz))
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, region_size, region_size)
        ctx = cairo.Context(surf)

        for z in range(region_size):
            for x in range(region_size):
                column = region_file.read(17)
                if column[0] == 0: continue  # no data present

                ctx.set_source_rgba(*self.get_pixel_color(column, x, z))
                ctx.rectangle(x, z, 1, 1)
                ctx.fill()

        surf.write_to_png('%s/%i_%i.png' % (self.tiles_path, rx, rz))

class BlockRenderer(TileRenderer):
    def get_pixel_color(self, column, x, z):
        level1, level2, level3, level4, biome = struct.unpack('>IIIIB', column)

        block_id = level1 >> 8 & 0xffff
        y = level1 >> 24
        if block_id == 0:
            block_id = level4 >> 8 & 0xffff
            y = level4 >> 24

        shade = 1 - (((256-y)/4)%3)*.02
        r, g, b = get_block_color(block_id)
        r, g, b = r * shade, g * shade, b * shade

        if level2:  # underwater
            block_id = level2 >> 8 & 0xffff
            r, g, b = get_block_color(block_id)
            b = b*.6 + .4

        return r, g, b
