# generate leaflet tiles from VoxelMap cache
import os
import sys
import time
from collections import defaultdict
import json
import struct
import cairo
from zipfile import ZipFile

data_root = 'static/civ3-data/'

# spawn: ba0cfdfb-4857-4efb-b516-0f5876d460d3
shardIds = {
    'abydos': '182702a7-ea3f-41de-a2d3-c046842d5e74',
    'drakontas': 'a7cbf239-6c11-4146-a715-ef0a9827b4c4',
    'eilon': 'a358b10c-7041-40c5-ac5e-db5483a9dfc2',
    'isolde': '197e2c4f-2fd6-464a-8754-53b24d9f7898',
    'naunet': 'de730958-fa83-4e73-ab7f-bfdab8e27960',
    # 'ovid': '',
    'padzahr': '7120b7a6-dd21-468c-8cd7-83d96f735589',
    'rokko': 'a72e4777-ad62-4e3b-a4e0-8cf2d15147ea',
    'sheol': 'fc891b9e-4b20-4c8d-8f97-7436383e8105',
    'tigrillo': '63a68417-f07f-4cb5-a9d8-e5e702565967',
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

def get_bounds(world_path=None, regions=None):
    if regions is None: regions = get_world_regions(world_path)
    min_x = region_size * min(x for x,y in regions)
    min_z = region_size * min(z for x,z in regions)
    max_x = region_size * (max(x for x,y in regions) + 1)
    max_z = region_size * (max(z for x,z in regions) + 1)
    return min_x, min_z, max_x, max_z


class Renderer(object):
    def __init__(self, world_path, get_pixel_color=None, meta_path='.', quiet=False):
        self.world_path = world_path
        self.get_pixel_color = get_pixel_color
        self.meta_path = meta_path
        self.quiet = quiet

    def render_map(self, img_path, print_progress=True):
        self.qprint('Rendering full map to', img_path)
        regions = get_world_regions(self.world_path)
        min_x, min_z, max_x, max_z = get_bounds(regions=regions)
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, max_x - min_x, max_z - min_z)
        ctx = cairo.Context(surf)
        ctx.translate(-min_x, -min_z)
        os.makedirs(os.path.dirname(img_path), exist_ok=True)

        last_progress = time.time()
        for rn, (rx, rz) in enumerate(regions):
            if print_progress and last_progress + 3 < time.time():
                last_progress += 3
                self.qprint('%i/%i regions' % (rn, len(regions)))

            region_file = get_region_file_from_zip(self.world_path + '/%i,%i.zip' % (rx, rz))
            for z in range(rz*region_size, (rz+1)*region_size):
                for x in range(rx*region_size, (rx+1)*region_size):
                    column = region_file.read(17)
                    if column[0] == 0: continue  # no data present

                    ctx.set_source_rgba(*self.get_pixel_color(column, x, z))
                    ctx.rectangle(x, z, 1, 1)
                    ctx.fill()

        surf.write_to_png(img_path)

    def render_tiles(self, tiles_path, print_progress=True):
        self.qprint('Rendering tiles to', tiles_path)
        regions = get_world_regions(self.world_path)
        os.makedirs(tiles_path, exist_ok=True)

        last_progress = time.time()
        for rn, (rx, rz) in enumerate(regions):
            if print_progress and last_progress + 3 < time.time():
                last_progress += 3
                self.qprint('%i/%i tiles' % (rn, len(regions)))
            # TODO skip if this has been rendered recently (metadata)
            tile_path = '%s/z0/%i,%i.png' % (tiles_path, rx, rz)
            self.render_tile(rx, rz, tile_path)

    def render_tile(self, rx, rz, tile_path):
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

        surf.write_to_png(tile_path)

    def write_map_metadata(self, world_name):
        json_path = self.meta_path + '/worlds.json'
        self.qprint('Writing map metadata for', world_name, 'to', json_path)
        min_x, min_z, max_x, max_z = get_bounds(self.world_path)
        os.makedirs(self.meta_path, exist_ok=True)

        try:
            worlds_data = json.load(open(json_path))
            data = [d for d in worlds_data if d['name'] == world_name][0]
        except:
            data = {'name': world_name}
            worlds_data = [data]

        data['bounds'] = {
            'min_x': min_x,
            'min_z': min_z,
            'max_x': max_x,
            'max_z': max_z,
        }

        json.dump(worlds_data, open(json_path, 'w'), indent='    ', sort_keys=True)

    def qprint(self, *args, **kwargs):
        if self.quiet:  return
        print(*args, **kwargs)


def block_color(column, x, z):
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


def usage():
    print('Args: [-h] [-t] [-f] [-m] [-q] <world name> [world path]')
    print('-t   render tiles')
    print('-f   render full map image')
    print('-m   write metadata')
    print('-q   do not print activity messages')
    print('-h   show this help and quit')
    print('you can pass multiple flags per arg: -q -mtf')
    return 1

def main(*args):
    if len(args) <= 1 or '--help' in args:
        return usage()
    args = list(args)

    flags = ''
    while len(args) > 1 and '-' == args[1][0]:
        flags += args[1][1:]
        del args[1]

    if 'h' in flags:
        return usage()

    quiet = 'q' in flags

    world_name = args[1]
    try:
        world_path = args[2]
    except IndexError:
        voxelmap_path = os.path.expanduser('~/.minecraft/mods/VoxelMods/voxelMap/')
        world_path = civ_world_path(voxelmap_path, name=world_name)

    full_map_path = data_root + 'maps/%s.png' % world_name
    tiles_path = data_root + 'tiles/' + world_name
    meta_path = data_root + 'meta/'

    r = Renderer(world_path, block_color, meta_path, quiet)

    if 'm' in flags:
        r.write_map_metadata(world_name)

    if 't' in flags:
        r.render_tiles(tiles_path)

    if 'f' in flags:
        r.render_map(full_map_path)

    if not quiet:
        print_missing_blocks()

    return 0

if __name__ == '__main__':
    sys.exit(main(*sys.argv))
