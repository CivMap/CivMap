// what to load when?
// first check if we can show tiles at all (tiles take long to load)
// -> do we have tiles for this world? load them now!
// load all other stuff in the background (radii, map overlays, , ...)

var React = require('react');
var ReactDOM = require('react-dom');
var L = require('leaflet');
var RL = require('react-leaflet');

var Util = require('./util.js');

const dataRoot = 'https://raw.githubusercontent.com/CivMap/civ3-data/master/';

const errorTileUrl = '/no-tile.png';

var mcCRS = L.extend({}, L.CRS.Simple, {
  transformation: new L.Transformation(1, 0, 1, 0)
});

class Centered extends React.Component {
  render() {
    return (
      <div className='center-outer full'>
      <div className='center-middle'>
      <div className='center-inner'>
        {this.props.children}
      </div></div></div>);
  }
}

class CoordsDisplay extends React.Component {
  render() {
    const x = parseInt(this.props.cursor.lng);
    const z = parseInt(this.props.cursor.lat);
    return <div className='coords-display control-box leaflet-control leaflet-control-layers'>
      {'X ' + x + ' ' + z + ' Z'}</div>;
  }
}

class CivMap extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      view: Util.hashToView(location.hash),
      worldBorders: {},
      maps: {},
      cursorPos: L.latLng(0,0),
    };
  }

  componentWillMount() {
    Util.getJSON(dataRoot+'meta/world-borders.json', worldBorders => {
      this.setState({worldBorders: worldBorders});
    });
    Util.getJSON(dataRoot+'meta/maps.json', maps => {
      this.setState({maps: maps});
    });
  }

  onbaselayerchange(o) {
    this.state.view.worldName = o.name;
    this.setState({view: this.state.view});
    this.updateHash(o);
  }

  updateHash(o) {
    const stateUrl = '#' + Util.viewToHash(o.target, this.state.view.worldName);
    history.replaceState({}, '', stateUrl);
  }

  onmousemove(o) {
    this.setState({cursorPos: o.latlng});
  }

  render() {
    var activeWorldName = this.state.view.worldName;
    var activeWorldMaps = ((this.state.maps || {})[activeWorldName] || []);
    var maxBounds = L.latLngBounds();
    if (activeWorldName in this.props.tilesMeta) {
      maxBounds.extend(this.props.tilesMeta[activeWorldName].bounds);
    }
    if (this.state.worldBorders[activeWorldName]) {
      maxBounds.extend(Util.radiusToBounds(this.state.worldBorders[activeWorldName]));
    }
    activeWorldMaps.map(m => maxBounds.extend(m.bounds));
    var minZoom = -3;
    return (
      <RL.Map
          className="map"
          crs={mcCRS}
          maxBounds={maxBounds}
          center={Util.xz(this.state.view.x, this.state.view.z)}
          zoom={this.state.view.zoom}
          maxZoom={5}
          minZoom={minZoom}
          onmoveend={this.updateHash.bind(this)}
          onbaselayerchange={this.onbaselayerchange.bind(this)}
          onmousemove={this.onmousemove.bind(this)}
          >

        <CoordsDisplay cursor={this.state.cursorPos} />

        { this.props.tilesMeta[activeWorldName] ? null :
            <Centered>
              <div className='message'>
                <h1>Choose a world on the top right</h1>
                { activeWorldName ?
                  <h2>{'Unknown world "' + activeWorldName + '"'}</h2>
                  : null
                }
              </div>
            </Centered>
        }

        <RL.LayersControl position='topright'>

          { Object.keys(this.props.tilesMeta).map(worldName =>
              <RL.LayersControl.BaseLayer name={worldName}
                  key={'tilelayer-' + worldName}
                  checked={worldName === activeWorldName}>
                <RL.TileLayer
                  attribution={Util.attribution}
                  url={dataRoot+'tiles/'+worldName+'/z{z}/{x},{y}.png'}
                  errorTileUrl={errorTileUrl}
                  tileSize={256}
                  bounds={L.latLngBounds(this.props.tilesMeta[worldName].bounds)}
                  minZoom={minZoom}
                  maxNativeZoom={0}
                  continuousWorld={true}
                  />
              </RL.LayersControl.BaseLayer>
            )
          }

          { activeWorldMaps.map(m =>
              <RL.LayersControl.Overlay
                  key={'full map ' + m.name}
                  name={m.name}
                  checked={false}
                  >
                <RL.ImageOverlay
                  url={m.url}
                  bounds={L.latLngBounds(m.bounds)}
                  opacity={.5}
                  />
              </RL.LayersControl.Overlay>
            )
          }

          { this.state.worldBorders[activeWorldName] ?
              <RL.LayersControl.Overlay name='world border' checked={true}>
                <RL.Circle
                  center={[0, 0]}
                  radius={this.state.worldBorders[activeWorldName]}
                  color='#ff8888'
                  fill={false}
                  />
              </RL.LayersControl.Overlay>
            : null
          }

          <RL.LayersControl.Overlay name='world center'>
            <RL.Marker position={[0, 0]} title='world center' />
          </RL.LayersControl.Overlay>

        </RL.LayersControl>
      </RL.Map>
    );
  }
}

const tiles_url = dataRoot + 'meta/tiles.json';
Util.getJSON(tiles_url, tilesMeta => {
  ReactDOM.render(
    <CivMap tilesMeta={tilesMeta} />,
    document.getElementById('civmap')
  );
}, err_request => {
  ReactDOM.render(
    <div className="message">
      <h1>Error {err_request.status}</h1>
      <p>
        Failed loading
        <a href={tiles_url}>
          <code>{tiles_url}</code></a>,
        response:
      </p>
      <pre style={{whiteSpace: 'pre-line'}}>
        {err_request.responseText}</pre>
    </div>,
    document.getElementById('civmap')
  );
});
