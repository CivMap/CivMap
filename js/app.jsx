var jQuery = require('jquery');
var React = require('react');
var ReactDOM = require('react-dom');
var L = require('leaflet');
var RL = require('react-leaflet');
var geoJsonTestData = require('./GeoJsonTestData.js');

RL.setIconDefaultImagePath('/leaflet-dist/images');

const dataRoot = '/data/';

var mcCRS = L.extend({}, L.CRS.Simple, {
  transformation: new L.Transformation(1, 0, 1, 0)
});

function xz(x, z) {
  return [z, x];
}

function pos2hash(leaf) {
  var center = leaf.getCenter();
  return  '' + leaf.getZoom() + '/' + center.lng + '/' + center.lat;
}

function hash2pos(hash) {
  if (!hash) return {x: 0, z: 0, zoom: 0};
  var [zoom, x, z] = hash.slice(1).split('/', 3);
  return {x: parseFloat(x), z: parseFloat(z), zoom: parseFloat(zoom)};
}

class CivMap extends React.Component {
  constructor() {
    super();
    this.state = {
      bounds: null,
    };
  }

  componentDidMount() {
    jQuery.getJSON(dataRoot+'meta/'+this.props.name+'/map.json', function(data) {
      var bounds = [xz(data.min_x, data.min_z), xz(data.max_x, data.max_z)];
      this.setState({bounds: bounds});
    }.bind(this));
  }

  onmoveend(o) {
    location.hash = pos2hash(o.target);
  }

  render() {
    return (
      <RL.Map
          className="map"
          crs={mcCRS}
          center={xz(this.props.pos.x, this.props.pos.z)}
          maxBounds={this.state.bounds}
          maxZoom={5}
          minZoom={-3}
          zoom={this.props.pos.zoom}
          onmoveend={this.onmoveend}
          >
        <RL.LayersControl position='topright'>
          <RL.LayersControl.BaseLayer name='tiles' checked={true}>
            <RL.TileLayer
              attribution='<a href="https://github.com/Gjum/civmap">github.com/Gjum/civmap</a>'
              ref={(ref) => {if (ref) this.tiles = ref.leafletElement}}
              url={dataRoot+'tiles/'+this.props.name+'/{z}_{x}_{y}.png'}
              errorTileUrl='data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
              tileSize={256}
              bounds={this.state.bounds}
              minZoom={0}
              maxNativeZoom={0}
              continuousWorld={true}
              />
          </RL.LayersControl.BaseLayer>

          <RL.LayersControl.BaseLayer name='full img'>
            <RL.ImageOverlay
              url={dataRoot+'maps/'+this.props.name+'.png'}
              bounds={this.state.bounds}
              />
          </RL.LayersControl.BaseLayer>

          <RL.LayersControl.Overlay name='geojson' checked={true}>
            <RL.GeoJson data={geoJsonTestData} />
          </RL.LayersControl.Overlay>
          <RL.LayersControl.Overlay name='marker' checked={true}>
            <RL.LayerGroup>
              <RL.Marker position={xz(775, -76)} title='Aquila'>
                <RL.Popup>
                  <span>Aquila center</span>
                </RL.Popup>
              </RL.Marker>
              <RL.Marker position={[0, 0]} title={this.props.name}>
                <RL.Popup>
                  <span>Center of {this.props.name}</span>
                </RL.Popup>
              </RL.Marker>
            </RL.LayerGroup>
          </RL.LayersControl.Overlay>
        </RL.LayersControl>
      </RL.Map>
    );
  }
}

ReactDOM.render(
  <CivMap name='naunet' pos={hash2pos(location.hash)} />,
  document.getElementById('content')
);
