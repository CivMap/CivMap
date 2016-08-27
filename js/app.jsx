var React = require('react');
var ReactDOM = require('react-dom');
var L = require('leaflet');
var RL = require('react-leaflet');
var geoJsonTestData = require('./GeoJsonTestData.js');

RL.setIconDefaultImagePath('/leaflet-dist/images');

var mcCRS = L.extend({}, L.CRS.Simple, {
  transformation: new L.Transformation(1, 0, 1, 0)
});

function xz(x, z) {
  return [z, x];
}

var CivMap = React.createClass({
  render: function() {
    var bounds = [xz(-1280, -1280), xz(1280, 1280)];
    return (
      <RL.Map
          className="map"
          crs={mcCRS}
          center={[0, 0]}
          maxBounds={bounds}
          maxZoom={5}
          minZoom={-2}
          zoom={0}
          >
        <RL.LayersControl position='topright'>
          <RL.LayersControl.BaseLayer name='tiles' checked={true}>
            <RL.TileLayer
              url={'/tiles/'+this.props.name+'/{z}/{x}_{y}.png'}
              tileSize={256}
              bounds={bounds}
              minZoom={0}
              maxNativeZoom={0}
              continuousWorld={true}
              />
          </RL.LayersControl.BaseLayer>
          <RL.LayersControl.BaseLayer name='full img'>
            <RL.ImageOverlay
              url={'/maps/'+this.props.name+'.png'}
              bounds={[xz(-1000, -1000), xz(1000, 1000)]}
              />
          </RL.LayersControl.BaseLayer>

          <RL.LayersControl.Overlay name='geojson' checked={true}>
            <RL.GeoJson data={this.props.geojson} />
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
});

ReactDOM.render(
  <CivMap name='naunet' geojson={geoJsonTestData} />,
  document.getElementById('content')
);
