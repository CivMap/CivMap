# CivMap
Shard maps of the Civcraft: Worlds (3.0) Minecraft server

uses react, leaflet.js, flask

## Install
get pip and npm (how to depends on your system), then

    pip install -r requirements.txt
    npm install
    npm install -g gulp

## Develop
open `static/index.html` in your favorite browser
run `gulp watch`, now edits to any file in `src/`
trigger a rebuild of `static/bundle.js`

## Deploy
get the heroku command line client,
run `gulp browserify` to create `static/bundle.js`, then

    heroku local web
