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
            'marker-color': '#029CB2',
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
            'marker-color': '#029CB2',
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
            'marker-color': '#029CB2',
            'marker-size': 'large'
        }
    }
];
var map = L.mapbox.map('map')
    .setView([37.8, -96], 5);
L.mapbox.featureLayer().setGeoJSON(geojson).addTo(map);
map.scrollWheelZoom.disable();
var styleLayer = L.mapbox.styleLayer('mapbox://styles/mapbox/dark-v9').addTo(map);