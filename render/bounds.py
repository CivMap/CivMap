"""
zip format: <cache_path>/<x>,<z>.zip
tiles format: <tiles_path>/<x>,<z>.png
json format:
{
    "<world_name>": {
        "bounds": [[<north>, <west>], [<south>, <east>]]
    },
    ...
}
"""
import os
import sys
import json

region_size = 256

def write_bounds(world_name, regions_path, json_path):
    os.makedirs(os.path.dirname(json_path), exist_ok=True)

    regions = [tuple(map(int, region[:-4].split(',')))
             for region in os.listdir(regions_path)
             if region[-4:] in ('.png', '.zip')
             and ',' in region]

    north = region_size * min(z for x,z in regions)
    west  = region_size * min(x for x,y in regions)
    south = region_size * (max(z for x,z in regions) + 1)
    east  = region_size * (max(x for x,y in regions) + 1)

    try:
        with open(json_path) as f:
            all_bounds = json.load(f)
    except FileNotFoundError as e:
        all_bounds = {}

    if world_name not in all_bounds:
        all_bounds[world_name] = {}

    all_bounds[world_name]['bounds'] = [[north, west], [south, east]]

    with open(json_path, 'w') as f:
        json.dump(all_bounds, f, sort_keys=True, indent='  ')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Args: <world_name> <tiles_path | cache_path> <json_path>')
    else:
        write_bounds(*sys.argv[1:4])
