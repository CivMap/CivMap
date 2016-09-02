var React = require('react');
var ReactDOM = require('react-dom');
var L = require('leaflet');
var RL = require('react-leaflet');

RL.setIconDefaultImagePath('/leaflet-dist/images');

const attribution = '<a href="https://github.com/CivMap">Civcraft Mapping Agency</a>'
  + ' | Visit civmap.herokuapp.com'
  + ' | <a href="https://github.com/CivMap/civmap">contribute</a>';

const dataRoot = 'https://raw.githubusercontent.com/CivMap/civ3-data/master/';

const emptyImg = 'data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==';

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

var mcCRS = L.extend({}, L.CRS.Simple, {
  transformation: new L.Transformation(1, 0, 1, 0)
});

function xz(x, z) {
  return [z, x];
}

function viewToHash(leaf, worldName) {
  var center = leaf.getCenter();
  return  '' + worldName + '/' + center.lng + 'x/' + center.lat + 'z/' + leaf.getZoom() + 'zoom';
}

function hashToView(hash) {
  if (!hash) return {worldName: 'dracontas', x: 0, z: 0, zoom: 0}; // default world if no hash
  var [worldName, x, z, zoom] = hash.slice(1).split('/', 4)
    .concat([0,0,0]); // default coords/zoom if not in url
  return {worldName: worldName, x: parseFloat(x), z: parseFloat(z), zoom: parseFloat(zoom)};
}

function makeBounds(bounds) {
  return[xz(bounds.min_x, bounds.min_z), xz(bounds.max_x, bounds.max_z)];
}

function getWorld(worlds, worldName, defaultWorld) {
  if (!worldName) return defaultWorld || worlds[0];
  var activeWorld = worlds.filter(w => w.name === worldName)[0];
  if (!activeWorld) return defaultWorld || worlds[0]; // unknown world
  return activeWorld;
}

class CivMap extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      activeWorld: getWorld(props.worlds, props.initialView.worldName),
    };
  }

  onbaselayerchange(o) {
    this.setState({activeWorld: getWorld(this.props.worlds, o.name, this.state.activeWorld)});
    this.updateHash(o);
  }

  updateHash(o) {
    if (this.state.activeWorld && 'name' in this.state.activeWorld)
      location.hash = viewToHash(o.target, this.state.activeWorld.name);
  }

  render() {
    return (
      <RL.Map
          className="map"
          crs={mcCRS}
          maxBounds={makeBounds(this.state.activeWorld.bounds)}
          center={xz(this.props.initialView.x, this.props.initialView.z)}
          zoom={this.props.initialView.zoom}
          maxZoom={5}
          minZoom={0}
          onmoveend={this.updateHash.bind(this)}
          onbaselayerchange={this.onbaselayerchange.bind(this)}
          >
        <RL.LayersControl position='topright'>

          { this.props.worlds.map((world) =>
              <RL.LayersControl.BaseLayer name={world.name}
                  key={'tilelayer-' + world.name}
                  checked={world.name === this.state.activeWorld.name}>
                <RL.TileLayer
                  attribution={attribution}
                  url={dataRoot+'tiles/'+world.name+'/{x}_{y}.png'}
                  errorTileUrl={emptyImg}
                  tileSize={256}
                  bounds={makeBounds(world.bounds)}
                  minZoom={0}
                  maxNativeZoom={0}
                  continuousWorld={true}
                  />
              </RL.LayersControl.BaseLayer>
            )
          }

          <RL.LayersControl.Overlay name='world border' checked={true}>
            <RL.Circle
              center={[0, 0]}
              radius={this.state.activeWorld.radius}
              color='#ff8888'
              stroke={true}
              fill={false}
              />
          </RL.LayersControl.Overlay>

          <RL.LayersControl.Overlay name='world center'>
            <RL.Marker position={[0, 0]} title='world center' />
          </RL.LayersControl.Overlay>

        </RL.LayersControl>
      </RL.Map>
    );
  }
}

getJSON(dataRoot+'meta/worlds.json', function(worlds) {
  worlds = worlds.filter((w) => 'bounds' in w); // ignore incomplete world data
  ReactDOM.render(
    <CivMap worlds={worlds} initialView={hashToView(location.hash)} />,
    document.getElementById('civmap')
  );
});
