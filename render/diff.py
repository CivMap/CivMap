import os
import sys
import time
from zipfile import ZipFile

import cairo

color_main_data     = .5, .5, .5
color_initial_data  = 0, 0, 1
color_unchanged     = .5, .5, 0
color_updated_data  = 0, 1, 0
color_outdated_data = 1, 0, 0
color_main_region   = color_main_data + (.5,)
color_add_region    = color_initial_data + (.5,)

region_size = 256
zeroes = b'\0' * 17

def get_bounds(regions):
    regions = [tuple(map(int, region[:-4].split(',')))
               for region in regions if region[-4:] == '.zip']
    min_x = region_size * min(x for x,y in regions)
    min_z = region_size * min(z for x,z in regions)
    max_x = region_size * (max(x for x,y in regions) + 1)
    max_z = region_size * (max(z for x,z in regions) + 1)
    return min_x, min_z, max_x, max_z

def diff_zips(ctx, region_main, region_add):
    file_main = ZipFile(region_main).open('data')
    file_add = ZipFile(region_add).open('data')

    time_main = os.path.getmtime(region_main)
    time_add = os.path.getmtime(region_add)
    newer = time_main < time_add

    for z in range(region_size):
        for x in range(region_size):
            col_main = file_main.read(17)
            col_add = file_add.read(17)

            if col_add == zeroes:
                if col_main == zeroes:
                    continue
                color = color_main_data
            elif col_main == zeroes:
                color = color_initial_data
            elif col_main == col_add:
                color = color_unchanged
            elif newer:
                color = color_updated_data
            else:
                color = color_outdated_data

            ctx.set_source_rgba(*color)
            ctx.rectangle(x, z, 1, 1)
            ctx.fill()

def show_zip(ctx, region, color):
    file = ZipFile(region).open('data')
    for z in range(region_size):
        for x in range(region_size):
            column = file.read(17)
            if column == zeroes: continue
            ctx.set_source_rgba(*color)
            ctx.rectangle(x, z, 1, 1)
            ctx.fill()

def diff_worlds(out_path, cache_main, cache_add):
    regions = set(os.listdir(cache_main)) \
           .union(os.listdir(cache_add))
    regions = [r for r in regions if r[-4:] == '.zip']
    min_x, min_z, max_x, max_z = get_bounds(regions)
    width = max_x - min_x
    height = max_z - min_z
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surf)
    ctx.translate(-min_x, -min_z)

    last_progress = time.time()
    for rn, region in enumerate(regions):
        if last_progress + 3 < time.time():
            last_progress += 3
            print('diff: %i/%i regions' % (rn, len(regions)))
        rx, rz = map(int, region[:-4].split(','))
        region_main = cache_main + '/' + region
        region_add = cache_add + '/' + region

        ctx.save()
        ctx.translate(rx*region_size, rz*region_size)
        if not os.path.isfile(region_main):
            show_zip(ctx, region_add, color_add_region)
        elif not os.path.isfile(region_add):
            show_zip(ctx, region_main, color_main_region)
        else:
            diff_zips(ctx, region_main, region_add)
        ctx.restore()

    surf.write_to_png(out_path)


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 3:
        print('Args: <diff img> <main cache> <add cache>')
        sys.exit(1)
    diff_worlds(*args)
