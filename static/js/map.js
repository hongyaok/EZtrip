// Sources
// https://developers.google.com/maps/documentation/javascript/tutorials
// see https://developers.google.com/maps/documentation/javascript/examples/places-searchbox
// https://developers.google.com/maps/documentation/javascript/examples
// https://www.w3schools.com/graphics/google_maps_intro.asp
// https://nordicapis.com/getting-started-with-google-maps-javascript-api/
// https://youtu.be/uPhWSyRqQDA

let map;
let markers = [];
let tripLocations = [];
let previewMarker = null;
window.currentPreviewPlace = null;

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 1.3521, lng: 103.8198},
        zoom: 10,
    });

    setupSearchBox();
    loadExistingLocations();
    map.addListener('click', function(event) {
        addLocationByClick(event.latLng);
    });
}

function setupSearchBox() {
    const searchInput = document.getElementById('location-search');
    if (searchInput) {
        const searchBox = new google.maps.places.SearchBox(searchInput);
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault()
                return false;
            }
        });
        searchBox.addListener('places_changed', function(){
            const places = searchBox.getPlaces();
            if (places.length == 0) {
                return;
            }
            const place = places[0];
            window.currentPreviewPlace = place;
            showLocationPreview(place);
            //console.log('📍 Search completed, place stored:', place.name);
        });
    }
}

function showLocationPreview(place) {
    if (previewMarker) {
        previewMarker.setMap(null);
    }
    previewMarker = new google.maps.Marker({
        position: place.geometry.location,
        map: map,
        title: place.name || place.formatted_address,
        icon: "https://maps.google.com/mapfiles/ms/icons/blue-dot.png",
        animation: google.maps.Animation.BOUNCE
    });
    map.setCenter(place.geometry.location);
    map.setZoom(15);
    const placeName = place.name || place.formatted_address;
    const placeDescription = getPlaceDescription(place);
    const infoContent = `
        <div style="min-width: 200px;">
            <h4>${placeName}</h4>
            <p><strong>Type:</strong>${placeDescription}</p>
            <p><strong>Address:</strong>${place.formatted_address}</p>
        </div>`;
    const infoWindow = new google.maps.InfoWindow({
        content: infoContent
    });
    infoWindow.open(map, previewMarker);
    previewMarker.placeData = place;
    previewMarker.infoWindow = infoWindow;
    fillFormWithSearchResult(place);
    showAddLocationForm();
    //console.log('📍 Showing preview for:', placeName);
}

function showAddLocationForm() {
    const form = document.getElementById('add-location-form');
    if (form) {
        form.style.display = 'block';
    }
}

function fillFormWithSearchResult(place) {
    const descriptionField = document.getElementById('location-description');
    const categoryField = document.getElementById('location-category');
    if (descriptionField) {
        const placeType = getPlaceDescription(place);
        descriptionField.value = `${placeType} - ${place.name || place.formatted_address}`;
    }
    if (categoryField) {
        const category = getCategoryFromPlace(place);
        categoryField.value = category;
    }
}

function getCategoryFromPlace(place) {
    const types = place.types || [];
    if (types.includes('lodging')) return 'accommodation';
    if (types.includes('restaurant') || types.includes('food')) return 'restaurant';
    if (types.includes('tourist_attraction') || types.includes('museum') || types.includes('park')) return 'attraction';
    if (types.includes('shopping_mall') || types.includes('store')) return 'shopping';
    if (types.includes('amusement_park') || types.includes('movie_theater')) return 'entertainment';
    return 'other';
}

function clearLocationForm() {
    const descriptionField = document.getElementById('location-description');
    const categoryField = document.getElementById('location-category');
    const searchInput = document.getElementById('location-search');
    const startDateField = document.getElementById('locationStartDate');
    const endDateField = document.getElementById('locationEndDate');
    const startTimeField = document.getElementById('locationStartTime');
    const endTimeField = document.getElementById('locationEndTime');
    if (descriptionField) descriptionField.value = '';
    if (categoryField) categoryField.value = 'restaurant';
    if (startDateField) startDateField.value = '';
    if (endDateField) endDateField.value = '';
    if (startTimeField) startTimeField.value = '';
    if (endTimeField) endTimeField.value = '';
    if (searchInput) {
        searchInput.value = '';
        searchInput.placeholder = 'Search for places (e.g. Namba, Osaka)...';
    }
}

function cancelLocationPreview() {
    if (previewMarker) {
        if(previewMarker.infoWindow) {
            previewMarker.infoWindow.close();
        }
        previewMarker.setMap(null);
        previewMarker = null;
        window.currentPreviewPlace = null;
        clearLocationForm();
        hideAddLocationForm()
        if (markers.length > 0) {
            fitMapToMarkers();
        } else {
            map.setCenter({lat:1.3521, lng:103.8198});
            map.setZoom(10);
        }
        //console.log('Location preview cancelled');
    }
}

function hideAddLocationForm() {
    const form = document.getElementById('add-location-form');
    if (form) {
        form.style.display = 'none';
    }
}

function addLocationByClick(clickedLocation) {
    const geocoder = new google.maps.Geocoder();
    geocoder.geocode({'location': clickedLocation}, function(results, status) {
        if (status === 'OK') {
            if(results[0]) {
                const place = {
                    name: results[0].formatted_address,
                    geometry: {
                        location: clickedLocation
                    },
                    formatted_address: results[0].formatted_address
                };
                showLocationPreview(place);
            }
        } else {
            //console.log("Unable to find the location name");
        }
    });
}

function addLocationToTrip(place) {
    const descriptionField = document.getElementById('location-description');
    const categoryField = document.getElementById('location-category');
    let customDescription =  '';
    let customCategory = 'other';
    if (descriptionField && descriptionField.value.trim()) {
        customDescription = descriptionField.value.trim();
    } else {
        customDescription = getPlaceDescription(place);
    }
    if (categoryField && categoryField.value) {
        customCategory = categoryField.value;
    }
    const dateField = document.getElementById('locationStartDate');
    const startTimeField = document.getElementById('locationStartTime');
    const endTimeField = document.getElementById('locationEndTime');
    const endDateField = document.getElementById('locationEndDate');
    let startDate = dateField ? dateField.value : '';
    let startTime = startTimeField ? startTimeField.value : '';
    let endTime = endTimeField ? endTimeField.value : '';
    let endDate = endDateField? endDateField.value : '';
    const newLocation = {
        name: place.name || place.formatted_address,
        lat: place.geometry.location.lat(),
        lng: place.geometry.location.lng(),
        address: place.formatted_address,
        description: customDescription,
        category: customCategory,
        start_date: startDate,
        end_date: endDate,
        startTime: startTime,
        endTime: endTime,
        id: Date.now()
    };
    tripLocations.push(newLocation);
    const marker = new google.maps.Marker({
        position: place.geometry.location,
        map: map,
        title: newLocation.name,
        icon: "https://maps.google.com/mapfiles/ms/icons/red-dot.png"
    });
    marker.locationId = newLocation.id;
    let infoContent = `<div><h4>${newLocation.name}</h4><p>${newLocation.description}</p><p><strong>Category:</strong> ${newLocation.category}</p>`;
    if (newLocation.start_date) {
        infoContent += `<p><strong>Start Date:</strong> ${formatDate(newLocation.start_date)}</p>`;
    }
    if (newLocation.end_date) {
        infoContent += `<p><strong>End Date:</strong> ${formatDate(newLocation.end_date)}</p>`;
    }
    if (newLocation.startTime && newLocation.endTime) {
        infoContent += `<p><strong>Time:</strong> ${formatTime(newLocation.startTime)} - ${formatTime(newLocation.endTime)}</p>`;
    }
    infoContent += `</div>`;
    const infoWindow = new google.maps.InfoWindow({
        content: infoContent
    });
    marker.addListener('click', function(){
        infoWindow.open(map,marker);
    });
    markers.push(marker);
    updateLocationsList()
    clearLocationForm();
    hideAddLocationForm();
    //console.log('Added location: ' + newLocation.name);
}

function addLocationFromCard(name, description, category, lat, lng) {
    const newLocation = {
        name: name,
        lat: lat,
        lng: lng,
        address: name,
        description: description,
        category: category,
        date: '',
        startTime: '',
        endTime: ''
    };
    tripLocations.push(newLocation);
    const marker = new google.maps.Marker({
        position: {lat: lat, lng: lng},
        map: map,
        title: name,
        icon: "https://maps.google.com/mapfiles/ms/icons/red-dot.png"
    });
    const infoWindow = new google.maps.InfoWindow({
        content: `<div>
                    <h4>${name}</h4>
                    <p>${description}</p>
                    <p><strong>Category:</strong>${category}</p>
                </div>`
    });
    marker.addListener('click', function(){
        infoWindow.open(map, marker);
    });
    markers.push(marker);
    updateLocationsList();
    //console.log('Added lication from suggestion card:', name);
}

function getPlaceDescription(place) {
    const types = place.types || [];
    const name = place.name || place.formatted_address;
    if (types.includes('lodging')) return "Hotel";
    if (types.includes('restaurant')) return  "Restaurant";
    if (types.includes('airport')) return "Airport";
    if (types.includes('tourist_attraction')) return "Tourist Attraction";
    if (types.includes('shopping_mall')) return "Shopping Mall";
    if (types.includes('park')) return "Park";
    if (types.includes('museum')) return "Museum";
    if (types.includes('amusement_park')) return "Theme Park";
    if (types.includes('zoo')) return "Zoo";
    if (types.includes('beach')) return "Beach";
    if (types.includes('hospital')) return "Hospital";
    return place.formatted_address;
}

function updateLocationsList() {
    let listDiv = document.getElementById('added-locations-list');
    if (!listDiv) {
        listDiv = document.getElementById('locations-list');
    }
    if(listDiv){
        if (tripLocations.length === 0){
            listDiv.innerHTML = '<p> No locations added yet. Search above or click on the map. </p>';
            return;
        }
        let allLocationHTML = '';
        for(let i = 0; i < tripLocations.length; i++) {
            const location = tripLocations[i];
            let locationHTML = '<div style= "border: 1px solid #ccc; padding: 10px; margin: 5px 0; border-radius: 5px;">';
            locationHTML += '<strong>' + location.name + '</strong><br>';
            locationHTML += '<small><strong>Category:</strong>' + location.category + '</small><br>';
            if (location.date) {
                locationHTML += '<small><strong>Date:</strong> ' + formatDate(location.date) + '</small><br>';
            }
            if (location.startTime && location.endTime) {
                locationHTML += '<small><strong>Time:</strong> ' + formatTime(location.startTime) + ' - ' + formatTime(location.endTime) + '</small><br>';
            }
            locationHTML += '<small>' + location.description + '</small><br>';
            locationHTML += '<button onclick= "removeLocation('+ i + ')" class="btn btn-outline btn-small" style=  "margin-top: 5px;"> Remove </button>';
            locationHTML += '</div>';
            allLocationHTML += locationHTML;
        }
        listDiv.innerHTML = allLocationHTML;
    } else {
        //console.log('ERROR: Could not find locations-list div!');
    }
}

function toggleAddLocation() {
    const form = document.getElementById('add-location-form');
    if (form) {
        if (form.style.display === 'none' || form.style.display === '') {
            form.style.display = 'block';
        } else {
            form.style.display = 'none';
        }
    }
}

function removeLocation(index) {
    const locationToRemove = tripLocations[index];
    const markerIndex = markers.findIndex(marker =>
        marker.locationId === locationToRemove.id
    );
    if (markerIndex !== -1) {
        markers[markerIndex].setMap(null);
        markers.splice(markerIndex, 1);
    }
    tripLocations.splice(index, 1);
    updateLocationsList();
    //console.log('Removed location at index: ' + index);
}

function locateActivityOnMap(lat, lng, name) {
    if (!map) {
        //console.error('Map not initialized yet');
        alert('Map is still loading. Please try again in a moment.');
        return;
    }
    let existingMarker = null;
    if (lat && lng && !isNaN(lat) && !isNaN(lng)) {
        existingMarker = markers.find(marker => {
            const markerPos = marker.getPosition();
            const markerLat = markerPos.lat();
            const markerLng = markerPos.lng();
            return Math.abs(markerLat - lat) < 0.0001 && Math.abs(markerLng - lng) < 0.0001;
        });
    }
    if (!existingMarker) {
        existingMarker = markers.find(marker => {
            const markerTitle = marker.getTitle();
            return markerTitle === name ||
                   markerTitle.includes(name) ||
                   name.includes(markerTitle);
        });
    }
    if (existingMarker) {
        const mapSection = document.getElementById('map');
        if (mapSection) {
            mapSection.scrollIntoView({behavior: 'instant', block:'center'});
        }
        const markerPos = existingMarker.getPosition();
        map.setCenter(markerPos);
        map.setZoom(16);
        existingMarker.setAnimation(google.maps.Animation.BOUNCE);
        const infoWindow = new google.maps.InfoWindow({
            content: `<div><h4>${name}</h4><p>📍 Location in your trip!</p></div>`
        });
        infoWindow.open(map, existingMarker);
        setTimeout(() => {
            existingMarker.setAnimation(null);
            infoWindow.close();
        }, 3000);
        //console.log('Found and highlighted existing marker for:', name);
    } else {
        //console.log('No existing marker found for:', name);
        alert(`Cannot locate "${name}" - no marker found on the map. Make sure the location has valid coordinates.`);
    }
}

function clearAllLocations() {
    if (confirm('Are you sure you want to clear all the locations?')){
        tripLocations = []
        for(let i = 0; i < markers.length; i++) {
            markers[i].setMap(null);
        }
        markers = [];
        updateLocationsList();
        //console.log('Cleared all locations');
    }
}

function getCurrentLocations() {
    return tripLocations
}

document.addEventListener('DOMContentLoaded', function(){
    const form = document.querySelector('form[action="/api/trips"]');
    if (form) {
        form.addEventListener('submit', function(e){
            const locationsData = JSON.stringify(tripLocations);
            const hiddenField = document.getElementById('locations-data');
            if (hiddenField) {
                hiddenField.value = locationsData;
                //console.log('Submitting locations to server: ', locationsData);
            } else {
                //console.log("Warning: No hidden field for locations");
            }
        });
    }
    const addLocationBtn = document.getElementById('add-location-btn');
    if (addLocationBtn) {
        addLocationBtn.addEventListener('click', function(e) {
            e.preventDefault();
            toggleAddLocation();
        });
    }
    const cancelLocationBtn = document.getElementById('cancel-location-btn');
    if (cancelLocationBtn) {
        cancelLocationBtn.addEventListener('click', function(e) {
            e.preventDefault();
            toggleAddLocation();
            cancelLocationPreview();
        });
    }
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('add-to-trip-btn')) {
            const lat = parseFloat(e.target.dataset.lat);
            const lng = parseFloat(e.target.dataset.lng);
            const name = e.target.dataset.name;
            const description= e.target.dataset.description;
            const category = e.target.dataset.category;
            addLocationFromCard(name, description,category, lat, lng);
            e.target.innerHTML = '<i class="plus"></i> Added!';
            e.target.style.background = '#28a745';
            setTimeout(()=> {
                e.target.innerHTML = '<i class="plus"></i> Add to Trip';
                e.target.style.background = '';
            }, 2000);
        }
    });
    document.addEventListener('click', function(e) {
        if (e.target.closest('.locate-btn')) {
            const button = e.target.closest('.locate-btn');
            const lat = parseFloat(button.dataset.lat);
            const lng = parseFloat(button.dataset.lng);
            const name = button.dataset.name;
            //console.log('Locate button clicked:', {lat, lng, name});
            locateActivityOnMap(lat, lng, name);
        }
    });
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('show-on-map-btn')) {
            const lat = parseFloat(e.target.dataset.lat);
            const lng = parseFloat(e.target.dataset.lng);
            const name = e.target.dataset.name;
            if (map) {
                map.setCenter({lat: lat, lng: lng});
                map.setZoom(15);
                const tempMarker = new google.maps.Marker({
                    position: {lat: lat, lng: lng},
                    map: map,
                    title: name,
                    animation: google.maps.Animation.BOUNCE
                });
                setTimeout(() => {
                    tempMarker.setAnimation(null);
                    setTimeout(() => {
                        tempMarker.setMap(null);
                    }, 1000);
                }, 2000);
            }
        }
    });
});

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatTime(timeString) {
    if (!timeString) return '';
    const [hours, minutes] = timeString.split(':');
    const hour = parseInt(hours);
    if (hour == 0) {
        return `12:${minutes} AM`;
    } else if (hour < 12) {
        return `${hour}:${minutes} AM`;
    } else if (hour == 12) {
        return `12:${minutes} PM`;
    } else {
        return `${hour-12}:${minutes} PM`;
    }
}

function loadExistingLocations() {
    const itineraryItems = document.querySelectorAll('.timeline-item[data-activity-id]');
    itineraryItems.forEach(item => {
        const activityId = item.getAttribute('data-activity-id');
        const locateBtn = item.querySelector('.locate-btn');
        if (locateBtn) {
            const lat = parseFloat(locateBtn.getAttribute('data-lat'));
            const lng = parseFloat(locateBtn.getAttribute('data-lng'));
            const name = locateBtn.getAttribute('data-name');
            if (!isNaN(lat) && !isNaN(lng) && lat !== 0 && lng !== 0) {
                createPermanentMarker(lat, lng, name, activityId);
            }
        }
    });
    if (markers.length > 0) {
        fitMapToMarkers();
    }
}

function createPermanentMarker(lat, lng, name, activityId) {
    const marker = new google.maps.Marker({
        position: {lat: lat, lng: lng},
        map: map,
        title: name,
        icon: "https://maps.google.com/mapfiles/ms/icons/red-dot.png"
    });
    marker.activityId = activityId;
    const infoWindow = new google.maps.InfoWindow({
        content: `<div><h4>${name}</h4><p>📍 Location in your trip</p></div>`
    });
    marker.addListener('click', function() {
        infoWindow.open(map, marker);
    });
    markers.push(marker);
}

function fitMapToMarkers() {
    if (markers.length === 0) return;
    const bounds = new google.maps.LatLngBounds();
    markers.forEach(marker => bounds.extend(marker.getPosition()));
    map.fitBounds(bounds);
}

function removeMarkerByActivityId(activityId) {
    const markerIndex = markers.findIndex(marker => marker.activityId === activityId);
    if (markerIndex !== -1) {
        markers[markerIndex].setMap(null);
        markers.splice(markerIndex, 1);
        if (markers.length > 0) {
            fitMapToMarkers();
        } else {
            map.setCenter({lat: 1.3521, lng: 103.8198});
            map.setZoom(10);
        }
    }
}

