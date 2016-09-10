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

function viewToHash(leaf, worldName) {
  var center = leaf.getCenter();
  return  '' + worldName + '/' + center.lng + 'x/' + center.lat + 'z/' + leaf.getZoom() + 'zoom';
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
  viewToHash: viewToHash,
  hashToView: hashToView,
  radiusToBounds: radiusToBounds,
  getWorld: getWorld,
}
