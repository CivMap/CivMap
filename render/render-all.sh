#!/bin/bash

root=../static/.civ3-data
worldsjson=$root/meta/worlds.json

for n in abydos drakontas eilon isolde naunet ovid padzahr rokko sheol tigrillo tjikko volans; do
    shardid="`python -c "from civ_shards import shard_ids as n;print(n['$n'])"`"
    python render.py -tzm $n $worldsjson $root/tiles/$n/ \
        ~/.minecraft/mods/VoxelMods/voxelMap/cache/mc.civcraft.co/$shardid/Overworld\ \(dimension\ 0\)/
done
