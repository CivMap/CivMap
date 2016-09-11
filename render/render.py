# generate leaflet tiles from VoxelMap cache
import json
import os
import struct
import sys
import time
from zipfile import ZipFile

import cairo

from bounds import write_bounds
from large_tiles import stitch_all
from render_utils import gen_item_colors, get_simple_block_color, print_missing_blocks


gen_item_colors('item-colors')

region_size = 16*16  # blocks per region edge

def get_region_file_from_zip(zip_path):
    return ZipFile(zip_path).open('data')

def get_world_regions(world_path):
    return [tuple(map(int, region[:-4].split(',')))
            for region in os.listdir(world_path)]


class Renderer(object):
    def __init__(self, cache_path, get_pixel_color, quiet=False):
        self.cache_path = cache_path
        self.get_pixel_color = get_pixel_color
        self.quiet = quiet

    def render_tiles(self, tiles_path, print_progress=True):
        self.qprint('Rendering tiles to', tiles_path)
        regions = get_world_regions(self.cache_path)
        os.makedirs(tiles_path + '/z0', exist_ok=True)

        last_progress = time.time()
        for rn, (rx, rz) in enumerate(regions):
            if print_progress and last_progress + 3 < time.time():
                last_progress += 3
                self.qprint('%i/%i tiles' % (rn, len(regions)))
            # TODO skip if this has been rendered recently (metadata)
            tile_path = '%s/z0/%i,%i.png' % (tiles_path, rx, rz)
            self.render_tile(rx, rz, tile_path)

    def render_tile(self, rx, rz, tile_path):
        region_file = get_region_file_from_zip(self.cache_path + '/%i,%i.zip' % (rx, rz))
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

    def qprint(self, *args, **kwargs):
        if self.quiet:  return
        print(*args, **kwargs)


def usage():
    print('Args: [-h] [-q] [-t] [-z] [-b <world name> <worlds.json path>] <tiles path> <world cache path>')
    print('-t   render tiles')
    print('-z   create zoomed-out tiles')
    print('-b   write tiles metadata')
    print('-q   do not print activity messages')
    print('-h   show this help and quit')
    print('you can pass multiple flags per arg: -ztm -q')
    return 1

def main(*args):
    if (not args) or '--help' in args:
        return usage()
    args = list(args)

    flags = ''
    while len(args) > 0 and '-' == args[0][0]:
        flags += args[0][1:]
        del args[0]

    if 'h' in flags:
        return usage()

    if 'b' in flags:
        world_name, tiles_json_path, *args = args

    quiet = 'q' in flags

    tiles_path = args[0]
    cache_path = args[1]

    r = Renderer(cache_path, get_simple_block_color, quiet=quiet)

    if 't' in flags:
        r.render_tiles(tiles_path)

    if 'z' in flags:
        for i in range(3):
            if not quiet:
                print('Creating zoomed-out tiles, level', -i-1)
            stitch_all('%s/z%i' % (tiles_path, -i-1),
                       '%s/z%i' % (tiles_path, -i))

    if 'b' in flags:
        if not quiet:
            print('Writing bounds to', tiles_json_path)
        write_bounds(world_name, tiles_path+'/z0', tiles_json_path)

    if not quiet:
        print_missing_blocks()

    return 0

if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
