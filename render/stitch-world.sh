#!/bin/bash
python3 large_tiles.py ../static/.civ3-data/tiles/"$1"/z{-1,0}/
python3 large_tiles.py ../static/.civ3-data/tiles/"$1"/z-{2,1}/
python3 large_tiles.py ../static/.civ3-data/tiles/"$1"/z-{3,2}/
