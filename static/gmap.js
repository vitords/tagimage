// Mostly from here: https://wrightshq.com/playground/placing-multiple-markers-on-a-google-map-using-api-3/
// Adapted by me to fill the needs of this application.

function pausecomp(millis)
{
    var date = new Date();
    var curDate = null;
    do { curDate = new Date(); }
    while(curDate-date < millis);
}

function initialize() {
    var map;
    var bounds = new google.maps.LatLngBounds();
    var mapOptions = {
        mapTypeId: 'roadmap'
    };
                    
    // Display a map on the page
    map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);
    map.setTilt(45);
    

    var geocoder = new google.maps.Geocoder();
    var newMarkers = [];

    for (var i = 0; i < tagMarkers.length; i++) {
        var tagMarker = tagMarkers[i];
        var country = [];
        country.push(tagMarker[0]);
        country.push([tagMarker[2][0], tagMarker[2][1]]);
        country.push(tagMarker[1]);
        newMarkers.push(country);
    }
 
    // Display multiple markers on a map
    var infoWindow = new google.maps.InfoWindow(), marker, i;

    // Loop through our array of markers & place each one on the map  
    for( i = 0; i < newMarkers.length; i++ ) {
        var markerInfo = newMarkers[i];
        var position = new google.maps.LatLng(markerInfo[1][0], markerInfo[1][1]);
        bounds.extend(position);
        marker = new google.maps.Marker({
            position: position,
            map: map,
            title: markerInfo[0]
        });
        
        // Allow each marker to have an info window    
        google.maps.event.addListener(marker, 'click', (function(marker, i) {
            return function() {
                infoWindow.setContent('<div class="info_content"><h3>' + newMarkers[i][0] + 
                    '</h3><h4>Most viewed videos in this location used these in their thumbnails:</h4><p>' +
                    newMarkers[i][2] + '</p></div>');
                infoWindow.open(map, marker);
            }
        })(marker, i));

        // Automatically center the map fitting all markers on the screen
        map.fitBounds(bounds);
    }

    // Override our map zoom level once our fitBounds function runs (Make sure it only runs once)
    var boundsListener = google.maps.event.addListener((map), 'bounds_changed', function(event) {
        this.setZoom(3);
        google.maps.event.removeListener(boundsListener);
    });
    
}
