import os
from zipfile import ZipFile


class WorldCache(object):
    def __init__(self, world_path):
        self.world_path = world_path
        self.region_cache = {}

    def available_regions(self):
        return [tuple(map(int, region[:-4].split(',')))
                for region in os.listdir(self.world_path)]

    def load_region(self, x, z)
        region = self.region_cache.get((x,z))
        if not region:
            region = RegionCache(self.world_path + '/%i,%i.zip' % (rx, rz))
            self.region_cache[(x,z)] = region
        return region


class RegionCache(object):
    def __init__(self, zip_path):
        self.zip_path = zip_path
        region_file = ZipFile(zip_path).open('data')
        self.data = bytearray(region_file.read())

    def get(self, x,z):
        return self.data[17 * (x + 256*z)]
