// Adding simple map functions to the map in Create Trip page
function initMap() {
    var map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 1.3521, lng: 103.8198},
        zoom: 10,
    });

//adding a red pin to the location we are at now (hardcoded btw)
    var marker = new google.maps.Marker({
        position: {lat: 1.3521, lng: 103.8198},
        map: map,
        title: 'Singapore'
      });
}
