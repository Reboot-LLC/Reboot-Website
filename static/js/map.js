var zoomLevel;
var w = window.innerWidth;
var h = window.innerHeight;


function mapbox_js() {
    if (w < 1086) {
        // set the zoom level to 4
        zoomLevel = 4;
    }  else {
        // set the zoom level to 5
        zoomLevel = 5;
    }
    L.mapbox.accessToken = 'pk.eyJ1IjoicmVib290IiwiYSI6ImNpeGdiaXl0MDAwMXkyeW52NTJjMm1jMHIifQ.IwhmgHr1XEF2iNDo5_eXDA';
    var geojson = [
        {
            type: 'Feature',
            geometry: {
                type: 'Point',
                coordinates: [-118.2167464, 34.0878233]
            },
            properties: {
                title: '[re:boot] - Los Angeles',
                description: 'Data Science & Intelligent Web Applications',
                'marker-color': '#1AADC1',
                'marker-size': 'large'
            }
        },
        {
            type: 'Feature',
            geometry: {
                type: 'Point',
                coordinates: [-75.167473, 39.951852]
            },
            properties: {
                title: '[re:boot] - Philadelphia',
                description: 'Intelligent Web Applications',
                'marker-color': '#1AADC1',
                'marker-size': 'large'
            }
        },
        {
            type: 'Feature',
            geometry: {
                type: 'Point',
                coordinates: [-84.0651685, 35.9586599]
            },
            properties: {
                title: '[re:boot] - Knoxville',
                description: 'Strategy, Consulting, & Financial Planning',
                'marker-color': '#1AADC1',
                'marker-size': 'large'
            }
        }
    ];
    var map = L.mapbox.map('map')
        .setView([37.8, -96], zoomLevel);
    L.mapbox.featureLayer().setGeoJSON(geojson).addTo(map);
    map.scrollWheelZoom.disable();
    var styleLayer = L.mapbox.styleLayer('mapbox://styles/mapbox/outdoors-v9').addTo(map);
}


function mapbox_gl() {
    // set zoom based on screen size
    if (w < 1086) {
        // set the zoom level to 3
        zoomLevel = 3;
    }  else {
        // set the zoom level to 4
        zoomLevel = 4;
    }
    // access token
    mapboxgl.accessToken = 'pk.eyJ1IjoicmVib290IiwiYSI6ImNpeGdiaXl0MDAwMXkyeW52NTJjMm1jMHIifQ.IwhmgHr1XEF2iNDo5_eXDA';
    // generate map object with style
    var map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/outdoors-v9',
        center: [-96, 37.8],
        zoom: 4
    });

    // markers object
    var geojson = {
        type: "FeatureCollection",
        features: [{
            type: "Feature",
            geometry: {
                type: "Point",
                coordinates: [-118.2167464, 34.0878233]
            },
            properties: {
                id: "LosAngeles",
                description: "<h6>[re:boot] - Los Angeles</h6><br>Data Science & Intelligent Web Applications",
                iconSize: [60, 60]
            }
        },
        {
            type: "Feature",
            geometry: {
                type: "Point",
                coordinates: [-75.167473, 39.951852]
            },
            properties: {
                id: "Philadelphia",
                description: "<h6>[re:boot] - Philadelphia</h6><br>Intelligent Web Applications",
                iconSize: [60, 60]
            }
        },
        {
            type: "Feature",
            geometry: {
                type: "Point",
                coordinates: [-84.0651685, 35.9586599]
            },
            properties: {
                id: "Knoxville",
                description: "<h6>[re:boot] - Knoxville</h6><br>Strategy, Consulting, & Financial Planning",
                iconSize: [60, 60]
            }
        }]
    }

    // add on map after it loads
    map.on('load', function () {
        // add the images to the markers
        geojson.features.forEach(function(marker) {
            // create a DOM element for the marker
            var el = document.createElement('div');
            el.className = 'marker-img';
            el.style.backgroundImage = 'url(../static/images/' + marker.properties.id + '_small.jpg)';
            el.style.width = marker.properties.iconSize[0] + 'px';
            el.style.height = marker.properties.iconSize[1] + 'px';

            // add marker to map
            new mapboxgl.Marker(el, {offset: [-marker.properties.iconSize[0] / 2, -marker.properties.iconSize[1] / 2]})
                .setLngLat(marker.geometry.coordinates)
                .addTo(map);
        });

        // add layer

        console.log(geojson);
        console.log(String(geojson));
        console.log(geojson[0]);

        map.addLayer({
            "id": "points",
            "type": "symbol",
            "source": {
                "type": "geojson",
                "data": geojson
            },
            "layout": {
//                "icon-image": "{icon}-15",
                "text-field": "{title}",
                "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
                "text-offset": [0, 0.6],
                "text-anchor": "top"
            }
        });
    });

    // fly to marker on click and center screen, display popup
    map.on('click', function (e) {

        // popup and fly
        function euclidean_dist(x1, y1, x2, y2) {
            var a = x1 - x2;
            var b = y1 - y2;
            var c = Math.sqrt( a * a + b * b );
            return c;
        }

        // grab the features to compare
        var features = geojson['features']

        // not exactly the most efficient means of producing the popup but meh
        for (var i = 0; i < features.length; i++) {
            if (euclidean_dist(e.lngLat.lat, e.lngLat.lng, features[i].geometry.coordinates[1], features[i].geometry.coordinates[0]) < 3) {
                var feature = features[i];
                var popup = new mapboxgl.Popup()
                    .setLngLat(feature.geometry.coordinates)
                    .setHTML(feature.properties.description)
                    .addTo(map);
                map.flyTo({center: feature.geometry.coordinates, speed: 0.75, curve: 1});
            }
        }

        //TO-DO: environ var for api key
        // grab real time IP addresses, map those to a latitude and longitude
        // from lat/long pull up other information
        // from ip pull up other information
        // display this info on the map for effect



    });

    // on mouse move listen for movement over a marker and change the cursor if hovering
    map.on('mousemove', function (e) {
        var features = map.queryRenderedFeatures(e.point, { layers: ['points'] });
        map.getCanvas().style.cursor = features.length ? 'pointer' : '';
    });

    // Add zoom and rotation controls to the map.
    map.addControl(new mapboxgl.NavigationControl());

//    // add geolocation control
//    map.addControl(new mapboxgl.GeolocateControl());
//
//    // add fullscreen control
//    map.addControl(new mapboxgl.FullscreenControl());
}


function render_map() {
    // if webGL is not supported, use mapbox js.
    if (mapboxgl.supported() == true) {
        mapbox_gl();
    }
    else {
        mapbox_js()
    }
}

render_map();







