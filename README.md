# CivMap
Shard maps of the [Civcraft: Worlds (3.0) Minecraft server](https://reddit.com/r/CivCraft)

We aim to provide an easy way to look up the most up-to-date information on
land claims, travel routes, and points of interest.

## Contribute
We still need:
- VoxelMap cache data for rendering the empty parts of the maps
- land claims data, preferably the corner coordinates in order

A big thanks to @WaffleStomper for providing the world radii
and portal coordinates in [a programmer-friendly form](https://github.com/waffle-stomper/WorldBorderViewer/blob/c9314a31a1657723abb787d1d5018ba8d8d06596/forge/src/main/java/wafflestomper/worldborderviewer/WBConfigManager.java#L84)!

## Install
Technologies used:
- React and Leaflet.js for the web interface
- Cairo for rendering the tiles
- Flask to serve the files (and in the future to accept user contributions)

get [pip](https://pypi.python.org) and [npm](https://npmjs.com/), then

    pip install -r requirements.txt
    npm install

run `npm run watchify` to automatically trigger a
rebuild of `static/bundle.js` when editing any file in `js/`

start the web server (does not do much right now besides serving the files,
will be used later for user contributions (map data, artistic maps, claims, roads, cities, ...))

    gunicorn -w 1 app:app --log-file=-
    # or, if you have heroku installed
    heroku local web
