var React = require('react');
var ReactDOM = require('react-dom');
var L = require('leaflet');
var RL = require('react-leaflet');

var Util = require('./util.js');

RL.setIconDefaultImagePath('/leaflet-dist/images');

const dataRoot = 'https://raw.githubusercontent.com/CivMap/civ3-data/master/';

const emptyImg = 'data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==';

var mcCRS = L.extend({}, L.CRS.Simple, {
  transformation: new L.Transformation(1, 0, 1, 0)
});

class CivMap extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      activeWorld: Util.getWorld(props.worlds, props.initialView.worldName),
    };
  }

  onbaselayerchange(o) {
    this.setState({activeWorld: Util.getWorld(this.props.worlds, o.name, this.state.activeWorld)});
    this.updateHash(o);
  }

  updateHash(o) {
    if (this.state.activeWorld && 'name' in this.state.activeWorld)
      location.hash = Util.viewToHash(o.target, this.state.activeWorld.name);
  }

  render() {
    var maxBounds = L.latLngBounds(Util.makeBounds(this.state.activeWorld.bounds));
    maxBounds.extend(Util.radiusToBounds(this.state.activeWorld.radius));
    return (
      <RL.Map
          className="map"
          crs={mcCRS}
          maxBounds={maxBounds}
          center={Util.xz(this.props.initialView.x, this.props.initialView.z)}
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
                  attribution={Util.attribution}
                  url={dataRoot+'tiles/'+world.name+'/{x}_{y}.png'}
                  errorTileUrl={emptyImg}
                  tileSize={256}
                  bounds={Util.makeBounds(world.bounds)}
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

Util.getJSON(dataRoot+'meta/worlds.json', function(worlds) {
  worlds = worlds.filter((w) => 'bounds' in w); // ignore incomplete world data
  ReactDOM.render(
    <CivMap worlds={worlds} initialView={Util.hashToView(location.hash)} />,
    document.getElementById('civmap')
  );
});
