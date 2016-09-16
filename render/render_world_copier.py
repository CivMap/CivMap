import os
import sys
from shutil import copy2
from civ_shards import shards_sorted

INTERVAL = 20  # region width of largest world, plus padding

def copy_regions(from_path, world_path, off_x):
    regions = [tuple(map(int, region[:-4].split(',')))
             for region in os.listdir(from_path)
             if region[-4:] == '.zip' and ',' in region]

    for x, z in regions:
        copy2('%s/%i,%i.zip' % (from_path, x, z),
            '%s/%i,%i.zip' % (world_path, x + off_x, z))

def copy_worlds(cache_path, world_path):
    for world in os.listdir(cache_path):
        i = shards_sorted.index(world)
        print('copying world %s at %i' % (world, i*INTERVAL*256))
        copy_regions(cache_path + '/' + world, world_path, i * INTERVAL)

def copy_tiles(tiles_path, world_path):
    os.makedirs(tiles_path, exist_ok=True)
    img_path = world_path + '/images/z1'
    tiles = [tuple(map(int, tile[:-4].split(',')))
             for tile in os.listdir(img_path)
             if tile[-4:] == '.png' and ',' in tile]

    for x, z in tiles:
        i = (x + INTERVAL//2) // INTERVAL
        off_x = i * INTERVAL
        world = shards_sorted[i]
        tiles_world = '%s/%s/z0' % (tiles_path, world)
        os.makedirs(tiles_world, exist_ok=True)
        copy2('%s/%i,%i.png' % (img_path, x, z),
            '%s/%i,%i.png' % (tiles_world, x - off_x, z))


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('Args: <regions|tiles> <cache path> <render world path> <tiles path>')
    else:
        mode, cache_path, world_path, tiles_path = sys.argv[1:]
        if mode[0] == 'r':
            print('copying regions from', cache_path, 'to', world_path)
            copy_worlds(cache_path, world_path)
        if mode[0] == 't':
            print('copying tiles from', world_path, 'to', tiles_path)
            copy_tiles(tiles_path, world_path)
