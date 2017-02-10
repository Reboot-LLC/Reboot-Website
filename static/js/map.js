var zoomLevel;
var w = window.innerWidth;
var h = window.innerHeight;
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
            coordinates: [-118.3118677, 34.0575926]
        },
        properties: {
            title: 'Los Angeles, CA',
            description: 'Valentino Constantinou<br> Rustam Mirzaev<br> Taylor Stevens',
            'marker-color': '#ffb81e',
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
            title: 'Philadelphia, PA',
            description: 'Michael Thompson',
            'marker-color': '#ffb81e',
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
            title: 'Knoxville, TN',
            description: 'Sammy Thomas',
            'marker-color': '#ffb81e',
            'marker-size': 'large'
        }
    }
];
var map = L.mapbox.map('map')
    .setView([37.8, -96], zoomLevel);
L.mapbox.featureLayer().setGeoJSON(geojson).addTo(map);
map.scrollWheelZoom.disable();
var styleLayer = L.mapbox.styleLayer('mapbox://styles/mapbox/streets-v9').addTo(map);