"""
zip format: <cache_path>/<x>,<z>.zip
tiles format: <tiles_path>/<x>,<z>.png
json format:
[
    {
        "name": "<world_name>",
        "bounds": {
            "min_x": <min_x>,
            "min_z": <min_z>,
            "max_x": <max_x>,
            "max_z": <max_z>
        }
    },
    ...
]
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

    min_x = region_size * min(x for x,y in regions)
    min_z = region_size * min(z for x,z in regions)
    max_x = region_size * (max(x for x,y in regions) + 1)
    max_z = region_size * (max(z for x,z in regions) + 1)

    try:
        worlds_data = json.load(open(json_path))
        world_data = [d for d in worlds_data
                      if d['name'] == world_name][0]
    except:
        world_data = {'name': world_name}
        worlds_data = [world_data]

    world_data['bounds'] = {
        'min_x': min_x,
        'min_z': min_z,
        'max_x': max_x,
        'max_z': max_z,
    }

    with open(json_path, 'w') as json_file:
        json.dump(worlds_data, json_file, sort_keys=True, indent='    ')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Args: <world_name> <tiles_path | cache_path> <json_path>')
    else:
        write_bounds(*sys.argv[1:4])
