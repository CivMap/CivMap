module.exports = {
  "type": "FeatureCollection",
  "features": [
  {
    "type": "Feature",
    "geometry": {
      "type": "Point", "coordinates": [10.0, 20.0]
    },
    "properties": {
      "title": "A title",
      "description": "A description",
      "marker-size": "medium",
      "marker-symbol": "bus",
      "marker-color": "#137"
    }
  },
  {
    "type": "Feature",
    "geometry": {
      "type": "LineString",
      "coordinates":
      [ [120.0,  0.0]
      , [130.0, 10.0]
      , [140.0,  0.0]
      , [150.0, 10.0]
      ]
    },
    "properties": {
      "prop0": "value0",
      "prop1":  0.0
    }
  },
  {
    "type": "Feature",
    "geometry": {
      "type": "Polygon",
      "coordinates":
      [
      [ [100.0,  0.0]
      , [110.0,  0.0]
      , [110.0, 10.0]
      , [100.0, 10.0]
      , [100.0,  0.0]
      ]
      ]
    },
    "properties": {
      "fill-opacity": 0.5,
      "stroke": "#aa66aa",
      "stroke-opacity": 1.0,
      "stroke-width": 2,
      "fill": "#123123"
    }
  }
  ]
}
;
