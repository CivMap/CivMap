# CivMap
Shard maps of the Civcraft: Worlds (3.0) Minecraft server

uses react, leaflet.js, flask, cairo

## Install
get pip and npm (how to depends on your system), then

    pip install -r requirements.txt
    npm install
    npm install -g gulp

## Running
create `static/bundle.js`:

    gulp browserify

start the web server:

    gunicorn -w 1 app:app --log-file=-
    # or heroku local web, if you have heroku installed

you can run `gulp watch` to automatically trigger a
rebuild of `static/bundle.js` when editing any file in `js/`
