const attribution = '<a href="https://github.com/CivMap">Civcraft Mapping Agency</a>'
  + ' | Visit civmap.github.io'
  + ' | <a href="https://github.com/CivMap/civmap#contribute">contribute</a>';

function getJSON(url, onData, onErr) {
  var request = new XMLHttpRequest();
  request.open('GET', url, true);
  request.onreadystatechange = function() {
    if (this.readyState === 4) {
      if (this.status >= 200 && this.status < 400) {
        onData(JSON.parse(this.responseText));
      } else {
        onErr && onErr(this);
      }
    }
  };
  request.send();
  request = null;
}

function xz(x, z) {
  return [z, x];
}

function intCoords(point) {
  var x = parseInt(point.lng);
  var z = parseInt(point.lat);
  if (point.lng < 0) x -= 1;
  if (point.lat < 0) z -= 1;
  return [z, x];
}

function viewToHash(leaf, worldName) {
  var [z, x] = intCoords(leaf.getCenter());
  return  '' + worldName + '/' + x + 'x/' + z + 'z/' + leaf.getZoom() + 'zoom';
}

function viewToTitle(leaf, worldName) {
  var [z, x] = intCoords(leaf.getCenter());
  return worldName + ' at ' + x + ',' + z + ' - Civcraft 3.0 Maps'
}

function hashToView(hash) {
  if (!hash) return {worldName: null, x: 0, z: 0, zoom: 0};
  var [worldName, x, z, zoom] = hash.slice(1).split('/', 4)
    .concat([0,0,0]); // default coords/zoom if not in url
  return {worldName: worldName, x: parseFloat(x), z: parseFloat(z), zoom: parseFloat(zoom)};
}

function radiusToBounds(radius) {
  return[xz(-radius, -radius), xz(radius, radius)];
}

function getWorld(worlds, worldName) {
  var activeWorld = worlds.filter(w => w.name === worldName)[0];
  if (!activeWorld) return {}; // unknown worldName
  return activeWorld;
}

module.exports = {
  attribution: attribution,
  getJSON: getJSON,
  xz: xz,
  intCoords: intCoords,
  viewToHash: viewToHash,
  viewToTitle: viewToTitle,
  hashToView: hashToView,
  radiusToBounds: radiusToBounds,
  getWorld: getWorld,
}
