# do batch operations on world caches: diff, merge, render, stitch
import os
import sys
import time

from civ_shards import shard_names
from diff import diff_worlds
from merge_caches import merge_worlds
from render import Renderer
from render_utils import get_simple_block_color, print_missing_blocks
from large_tiles import stitch_all
from bounds import write_bounds

overworld = 'Overworld (dimension 0)'

def usage():
    print('Args: <main path> [-[d][m] <new data path>] [-[t][z] <tiles path>] [-b <world name> <worlds.json path>] [-o <only,world,names>] [-i <ignored,world,names>]')
    print('-d   diff caches')
    print('-m   merge caches')
    print('-t   render tiles')
    print('-z   create zoomed-out tiles')
    print('-b   write tiles bounds')
    print('-o   only operate on these worlds')
    print('-i   ignored worlds')
    print('-o and -i take comma separated world names')
    return 1

def main(*args):
    if (not args) or '--help' in args:
        return usage()

    cache_main, *args = list(args)
    cache_add = tiles_path = world_name = worlds_json_path = ''
    only_worlds = set()
    ignored_worlds = ['spawn', 'ulca']

    flags = ''
    while len(args) > 0 and '-' == args[0][0]:
        new_flags, *args = args
        if 'd' in new_flags or 'm' in new_flags:
            cache_add, *args = args
        if 't' in new_flags or 'z' in new_flags:
            tiles_path, *args = args
        if 'b' in new_flags:
            world_name, tiles_json_path, *args = args
        if 'o' in new_flags:
            new_only, *args = args
            only_worlds = only_worlds.union(new_only.split(','))
        if 'i' in new_flags:
            new_ignored, *args = args
            ignored_worlds += new_ignored.split(',')
        flags += new_flags

    if args:
        print('Leftover args:', *args)
        return usage()

    print('Ignored worlds:', ','.join(ignored_worlds))
    if only_worlds: print('and all except', ','.join(only_worlds))

    batch_id = time.time()

    world_ids = set(os.listdir(cache_main))
    if cache_add:
        world_ids = world_ids.union(os.listdir(cache_add))

    for world_id in world_ids:
        if world_id not in shard_names:
            if world_id not in shard_names.values():
                print('Unknown shard id', world_id)
            continue

        world_name = shard_names[world_id]
        if only_worlds and world_name not in only_worlds:
            continue
        if world_name in ignored_worlds:
            continue

        print('Found world', world_name, world_id)

        world_main = cache_main + '/' + world_name
        world_tiles = tiles_path + '/' + world_name
        world_add = cache_add + '/' + world_id + '/' + overworld

        if 'd' in flags:
            diff_img = 'diffs/diff-%s/diff-%s.png' % (batch_id, world_name)
            print('Creating diff image at', diff_img)
            os.makedirs('diffs/diff-%s' % batch_id, exist_ok=True)
            try:
                diff_worlds(diff_img, world_main, world_add)
            except FileNotFoundError as e:
                print('ERROR', e.__class__.__name__, e)
                continue

        if 'm' in flags:
            print('Merging from', world_add)
            try:
                merge_worlds(world_main, world_main, world_add, by_time=True)
            except FileNotFoundError as e:
                print('ERROR', e.__class__.__name__, e)
                continue

        if 't' in flags:
            r = Renderer(world_main, get_simple_block_color)
            r.render_tiles(world_tiles)
            print_missing_blocks()

        if 'z' in flags:
            for i in range(3):
                print('Creating zoomed-out tiles, level', -i-1)
                stitch_all('%s/z%i' % (world_tiles, -i-1),
                           '%s/z%i' % (world_tiles, -i))

        if 'b' in flags:
            print('Writing bounds to', tiles_json_path)
            write_bounds(world_name, world_main, tiles_json_path)

if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
