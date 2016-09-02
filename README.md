# CivMap
Shard maps of the Civcraft: Worlds (3.0) Minecraft server

uses react, leaflet.js, flask, cairo

## Install
get pip and npm (how to depends on your system), then

    pip install -r requirements.txt
    npm install

open `static/index.html` in your browser

## Develop
run `npm run watchify` to automatically trigger a
rebuild of `static/bundle.js` when editing any file in `js/`

### start the web server
does not do much right now besides serving the files,
will be used later for user contributions
(map data, artistic maps, claims, roads, cities, ...)

    gunicorn -w 1 app:app --log-file=-
    # or, if you have heroku installed
    heroku local web
