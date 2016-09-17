import os
import sys
import time
from colorsys import hsv_to_rgb
from zipfile import ZipFile

import cairo
from civ_shards import shard_names

region_size = 256
zeroes = b'\0' * 17

def get_cache_path(world_path):
    entries = os.listdir(world_path)
    if any(filter(lambda f: f[-4:] == '.zip', entries)):
        return world_path
    return world_path + '/' + sorted(entries)[0]

def get_bounds(regions):
    regions = [tuple(map(int, region[:-4].split(',')))
               for region in regions if region[-4:] == '.zip']
    min_x = min(x for x,y in regions)
    min_z = min(z for x,z in regions)
    max_x = (max(x for x,y in regions) + 1)
    max_z = (max(z for x,z in regions) + 1)
    return min_x, min_z, max_x, max_z

def time_hue(path):
    mtime = os.path.getmtime(path)
    # one distinct color per hour, starting in the past
    t = (mtime - 1469800000) / (256*6 * 3600)
    if t > 1:
        raise ValueError('t > 1: %s %s %s' % (t, mtime, path))
    if t < 0:
        raise ValueError('t < 0: %s %s %s' % (t, mtime, path))
    return t

def show_zip(ctx, region_path):
    file = ZipFile(region_path).open('data')
    t = time_hue(region_path)
    for z in range(region_size):
        for x in range(region_size):
            column = file.read(17)
            if column == zeroes: continue
            ctx.set_source_rgb(*hsv_to_rgb(t, 1, 1))
            ctx.rectangle(x, z, 1, 1)
            ctx.fill()

def show_world_detailed(img_path, world_path):
    regions = [r for r in os.listdir(world_path) if r[-4:] == '.zip']
    # min_x, min_z, max_x, max_z = get_bounds(regions)
    min_x, min_z, max_x, max_z = -20, -20, 20, 20
    width = max_x - min_x
    height = max_z - min_z
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, width*region_size, height*region_size)
    ctx = cairo.Context(surf)
    ctx.translate(-min_x*region_size, -min_z*region_size)

    last_progress = time.time()
    for rn, region in enumerate(regions):
        if last_progress + 3 < time.time():
            last_progress += 3
            print('timemap: %i/%i regions' % (rn, len(regions)))

        rx, rz = map(int, region[:-4].split(','))
        region_path = world_path + '/' + region

        ctx.save()
        ctx.translate(rx*region_size, rz*region_size)
        show_zip(ctx, region_path)
        ctx.restore()

    print('Saving as', img_path)
    surf.write_to_png(img_path)

def show_world_regions(img_path, world_path):
    regions = [r for r in os.listdir(world_path) if r[-4:] == '.zip']
    # min_x, min_z, max_x, max_z = get_bounds(regions)
    min_x, min_z, max_x, max_z = -20, -20, 20, 20
    width = max_x - min_x
    height = max_z - min_z
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surf)
    ctx.translate(-min_x, -min_z)

    min_t = 1
    max_t = 0

    last_progress = time.time()
    for rn, region in enumerate(regions):
        if last_progress + 3 < time.time():
            last_progress += 3
            print('timemap: %i/%i regions' % (rn, len(regions)))

        rx, rz = map(int, region[:-4].split(','))
        t = time_hue(world_path + '/' + region)

        min_t = min(t, min_t)
        max_t = max(t, max_t)

        ctx.set_source_rgb(*hsv_to_rgb(t, 1, 1))
        ctx.rectangle(rx, rz, 1, 1)
        ctx.fill()

    print('Saving as', img_path)
    surf.write_to_png(img_path)

    return min_t, max_t

def show_cache(img_dir, cache_path, detail):
    os.makedirs(img_dir, exist_ok=True)

    min_t = 1
    max_t = 0

    for world_id in os.listdir(cache_path):
        world_name = world_id
        if world_name not in shard_names.values():
            if world_id not in shard_names:
                continue
            world_name = shard_names[world_id]
        print('Drawing timemap for', world_name, world_id, 'to', img_dir)
        try:
            world_path = get_cache_path(cache_path + '/' + world_id)
        except IndexError:
            print('no data, skipping')
            continue
        img_base = img_dir + '/' + world_name
        if 'regions' == detail:
            ti, ta = show_world_regions(img_base + '-regions.png', world_path)

            min_t = min(ti, min_t)
            max_t = max(ta, max_t)

        elif 'detailed' == detail:
            show_world_detailed(img_base + '-detailed.png', world_path)
        else:
            print('Unknown detail level', detail)
            print('must be "regions" or "detailed"')
            return

    print('min/max t:', min_t, max_t)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Args: <regions|detailed> <img or img dir> <cache path>')
        sys.exit(1)
    detail, img_dir, cache_path = sys.argv[1:]
    if img_dir[-4:] == '.png':
        img_path, world_path = img_dir, cache_path
        if 'regions' == detail:
            show_world_regions(img_path, world_path)
        elif 'detailed' == detail:
            show_world_detailed(img_path, world_path)
        else:
            print('Unknown detail level', detail)
            print('must be "regions" or "detailed"')
    else:
        show_cache(img_dir, cache_path, detail)
