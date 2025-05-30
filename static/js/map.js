function initMap(location = null) {
    var defaultLocation = {lat: 1.3521, lng: 103.8198};
    var mapCenter = location || defaultLocation;
    
    var map = new google.maps.Map(document.getElementById('map'), {
        center: mapCenter,
        zoom: 10,
    });

    // the red pin
    var marker = null;

    // if marker exists, remove and place new marker
    map.addListener('click', function(event) {
        if (marker) {
            marker.setMap(null);
        }
        
        marker = new google.maps.Marker({
            position: event.latLng,
            map: map,
            title: 'Selected Location'
        });
    });
}