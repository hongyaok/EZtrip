//using global variables to store the map and users' data
let map;
let markers = [];   //use the array to store all the map markers
let tripLocations = []  //for storing all the location data
let previewMarker = null    //to show user's search preview
let currentPreviewPlace = null;     //allow us to store the current searched place


// enhancing our previous map 
function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 1.3521, lng: 103.8198},
        zoom: 10,
    });

    //add search functionality
    setupSearchBox();

    //adding event listener so that locations can be added when users clicked the map
    map.addListener('click', function(event) {
        addLocationByClick(event.latLng);
    });
}

//create searchBox function 
function setupSearchBox() {
    const searchInput = document.getElementById('location-search');     //find search input in the HTML

    if (searchInput) {
        const searchBox = new google.maps.places.SearchBox(searchInput);    //creating google search box

        //prevent the loocation from immediately being added into the list once u press "enter"
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault()
                return false;
            }
        });

        //when users start to search for places
        searchBox.addListener('places_changed', function(){
            const places = searchBox.getPlaces();

            //if no search result pop up 
            if (places.length == 0) {
                return;
            }

            //first result that pops up will be added to our trip
            const place = places[0];

            //Store the place for our form submission
            currentPreviewPlace = place;
            
            //show preview marker and ask user to confirm
            showLocationPreview(place);

           //wait until form is submitted or cancelled
           console.log('📍 Search completed, place stored:', place.name);
        });
    }
}

//create function to show preview marker and confirmation window
function showLocationPreview(place) {
    //remove any existing preview marker
    if (previewMarker) {
        previewMarker.setMap(null);
    }

    //create preview marker(colours between the preview and confirmed markers are different)
    previewMarker = new google.maps.Marker({
        position: place.geometry.location,
        map: map,
        title: place.name || place.formatted_address,
        icon: "https://maps.google.com/mapfiles/ms/icons/blue-dot.png",
        animation: google.maps.Animation.BOUNCE
    });

    //center the map on the preview location
    map.setCenter(place.geometry.location);
    map.setZoom(15);

    //to create an info window with confirmation button
    const placeName = place.name || place.formatted_address;
    const placeDescription = getPlaceDescription(place);

    //all the info that will appear on the map
    const infoContent = `
        <div style="min-width: 200px;">
            <h4>${placeName}</h4>
            <p><strong>Type:</strong>${placeDescription}</p>
            <p><strong>Address:</strong>${place.formatted_address}</p>
            <div style="margin-top: 10px;">
                <button onclick="confirmAddLocation()" style="background: #28a745; color:white; border:none; padding: 8px 16px; margin-right: 5px; border-radius:4px; cursor: pointer;">
                    ✅ Add to Trip
                </button>
                <button onclick="cancelLocationPreview()" style="background: #dc3545; color:white; border:none; padding: 8px 16px; border-radius:4px; cursor: pointer;">
                    ❌ Cancel
                </button>
            </div>
        </div>`;

    const infoWindow = new google.maps.InfoWindow({
        content: infoContent
    });

    //show the infowindow 
    infoWindow.open(map, previewMarker);

    //store the place data for confirmation
    previewMarker.placeData = place;
    previewMarker.infoWindow = infoWindow;

    //Pre-fill the form with search result info
    fillFormWithSearchResult(place);

    //debugging purposes
    console.log('📍 Showing preview for:', placeName);
}

//function to allow users to confirm adding of the location
function confirmAddLocation() {
    if (previewMarker && previewMarker.placeData) {
        //add the location to trip
        addLocationToTrip(previewMarker.placeData);

        //remove the preview
        cancelLocationPreview();

        //for debugging
        console.log('Location confirmed and added to trip')
    }
}


//function to help us pre-fill the form with search result
function fillFormWithSearchResult(place) {
    const descriptionField = document.getElementById('location-description');
    const categoryField = document.getElementById('location-category');

    if (descriptionField) {
        //set a default description based on what type of place it is
        const placeType = getPlaceDescription(place);
        descriptionField.value = `${placeType} - ${place.name || place.formatted_address}`;
    }

    if (categoryField) {
        //help us to select the appropriate category
        const category = getCategoryFromPlace(place);
        categoryField.value = category;
    }
}

//fucntion to help us get the appropriate category
function getCategoryFromPlace(place) {
    const types = place.types || [];

    if (types.includes('lodging')) return 'accommodation';
    if (types.includes('restaurant') || types.includes('food')) return 'restaurant';
    if (types.includes('tourist_attraction') || types.includes('museum') || types.includes('park')) return 'attraction';
    if (types.includes('shopping_mall') || types.includes('store')) return 'shopping';
    if (types.includes('amusement_park') || types.includes('movie_theater')) return 'entertainment';

    return 'other';
}

//function to clear the location form
function clearLocationForm() {
    const descriptionField = document.getElementById('location-description');
    const categoryField = document.getElementById('location-category');
    const searchInput = document.getElementById('location-search');

    if (descriptionField) descriptionField.value = '';
    if (categoryField) categoryField.value = 'restaurant';      //reset to default

    //clear search input
    if (searchInput) {
        searchInput.value = '';
        searchInput.placeholder = 'Search for places (e.g. Namba, Osaka)...';
    }
}

//Cancel the location preview
function cancelLocationPreview() {
    if (previewMarker) {
        //allow us to close the info window
        if(previewMarker.infoWindow) {
            previewMarker.infoWindow.close();
        }

        //remove the preview marker
        previewMarker.setMap(null);
        previewMarker = null;

        //clear the current preview place
        currentPreviewPlace = null;

        //clear the form
        clearLocationForm();

        //zoom out to show all locations
        if (markers.length > 0) {
            //if there are existing location, fit them into suitable view
            const bounds = new google.maps.LatLngBounds();
            markers.forEach(marker => bounds.extend(marker.getPosition()));
            map.fitBounds(bounds);
        } else {
            //if no locatons, zoom back to SG view
            map.setCenter({lat:1.3521, lng:103.8198});
            map.setZoom(10);
        }
        
        //debugging purposes
        console.log('Location preview cancelled');
    }
}

//add locations when user clicks on the map
function addLocationByClick(clickedLocation) {
    // we will be using Google's service to find out what place this is (converting coordinates into places )
    const geocoder = new google.maps.Geocoder();

    geocoder.geocode({'location': clickedLocation}, function(results, status) {
        if (status === 'OK') {
            if(results[0]) {
                //creating an object that provide description of place
                const place = {
                    name: results[0].formatted_address,
                    geometry: {
                        location: clickedLocation 
                    },
                    formatted_address: results[0].formatted_address
                };
                
                addLocationToTrip(place);
            }
        } else {
            console.log("Unable to find the location name");    //when Google cannot find the place
        }
    });
}


//add locations to our trip
function addLocationToTrip(place) {
    //get customised description and category from form if they do exist
    const descriptionField = document.getElementById('location-description');
    const categoryField = document.getElementById('location-category');

    let customDescription =  '';
    let customCategory = 'other';

    //remove the extra space at the start and back for custom message
    if (descriptionField && descriptionField.value.trim()) {
        customDescription = descriptionField.value.trim();
    } else {
        customDescription = getPlaceDescription(place);
    }

    if (categoryField && categoryField.value) {
        customCategory = categoryField.value;
    }

    //create location object
    const newLocation = {
        name: place.name || place.formatted_address,
        lat: place.geometry.location.lat(),
        lng: place.geometry.location.lng(),
        address: place.formatted_address,
        description: customDescription,
        category: customCategory
    };

    //add new location into our list
    tripLocations.push(newLocation);

    //create red marker to mark the location 
    const marker = new google.maps.Marker({
        position: place.geometry.location,
        map: map,
        title: newLocation.name,
        icon: "https://maps.google.com/mapfiles/ms/icons/red-dot.png"
    });


    //add a pop up window about info related to the place 
    const infoWindow = new google.maps.InfoWindow({
        content: `<div><h4>${newLocation.name}</h4><p>${newLocation.description}</p><p><strong>Category:</strong> ${newLocation.category}</p></div>`
    });

    //add event listener to the mark for window to pop up 
    marker.addListener('click', function(){
        infoWindow.open(map,marker);
    });

    //store the marker
    markers.push(marker);

    // update the list on the page, for users to see the new location added
    updateLocationsList()

    //clear the form after successful addition
    clearLocationForm();

    //for debugging purposes using the console
    console.log('Added location: ' + newLocation.name);
}

//add location from existing suggestion card
function addLocationFromCard(name, description, category, lat, lng) {
    //create location object using data that is formatted from our database
    const newLocation = {
        name: name,
        lat: lat,
        lng: lng,
        address: name,
        description: description,
        category: category
    };

    //add location to the list
    tripLocations.push(newLocation);

    //create a red marker to mark the location
    const marker = new google.maps.Marker({
        position: {lat: lat, lng: lng},
        map: map,
        title: name,
        icon: "https://maps.google.com/mapfiles/ms/icons/red-dot.png"
    });

    //create better window popup
    const infoWindow = new google.maps.InfoWindow({
        content: `<div>
                    <h4>${name}</h4>
                    <p>${description}</p>
                    <p><strong>Category:</strong>${category}</p>
                </div>`
    });

    //make marker clickabe to show info window
    marker.addListener('click', function(){
        infoWindow.open(map, marker);
    });

    //store the marker
    markers.push(marker);

    //update 'Added Locations" list 
    updateLocationsList();

    //for debugging
    console.log('Added lication from suggestion card:', name);

}

//function that give description of the place user would like to visit
function getPlaceDescription(place) {
    const types = place.types || [];
    const name = place.name || place.formatted_address;

    //check what of type of place it is
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

    //Default to the name of the name if unable to catgorise it
    return place.formatted_address;
}


//function to update the location list
function updateLocationsList() {

    let listDiv = document.getElementById('added-locations-list');

    //our fallback if listDiv does not exist
    if (!listDiv) {
        listDiv = document.getElementById('locations-list');
    }
        //if there are no locations, will show a message
    if(listDiv){
        if (tripLocations.length === 0){
            listDiv.innerHTML = '<p> No locations added yet. Search above or click on the map. </p>';
            return;
        }

        //create an empty container to build on user trip list
        let allLocationHTML = '';

        //add each location to the list
        for(let i = 0; i < tripLocations.length; i++) {
            const location = tripLocations[i];

            // create HTML for this location
            let locationHTML = '<div style= "border: 1px solid #ccc; padding: 10px; margin: 5px 0; border-radius: 5px;">';
            locationHTML += '<strong>' + location.name + '</strong><br>';
            locationHTML += '<small><strong>Category:</strong>' + location.category + '</small><br>';
            locationHTML += '<small>' + location.description + '</small><br>';
            locationHTML += '<button onclick= "removeLocation('+ i + ')" class="btn btn-outline btn-small" style=  "margin-top: 5px;"> Remove </button>';
            locationHTML += '</div>';

            allLocationHTML += locationHTML;    //add to the complete string
        }
        listDiv.innerHTML = allLocationHTML;      //allow us to set all the HTML at once
    } else {
        //help me to debug
        console.log('ERROR: Could not find locations-list div!');
    }
}

//Toggle add location form (transferred from trips.html)
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

//delete a location
function removeLocation(index) {
    //remove the location from our array
    tripLocations.splice(index, 1);

    //remove marker from the map 
    if(markers[index]) {
        markers[index].setMap(null);
        markers.splice(index, 1);
    }

    //update list
    updateLocationsList();

    //for debugging purposes
    console.log('Removed location at index: ' + index);
}


//function to clear all locations
function clearAllLocations() {
    //confirm with user if they wanna remove all locations
    if (confirm('Are you sure you want to clear all the locations?')){
        //clear the list
        tripLocations = []

        //remove all the markers
        for(let i = 0; i < markers.length; i++) {
            markers[i].setMap(null);
        }
        markers = [];

        //update the list
        updateLocationsList();

        console.log('Cleared all locations');
    }
}

//give us all the locations
function getCurrentLocations() {
    return tripLocations
}

//connect the map data to our form submission
document.addEventListener('DOMContentLoaded', function(){
    //submit form for create trip page if the form exists
    const form = document.querySelector('form[action="/api/trips"]');
    if (form) {
        form.addEventListener('submit', function(e){
            //help to copy the locations to a hidden filed before submission
            const locationsData = JSON.stringify(tripLocations);

            //check if hidden field exists
            const hiddenField = document.getElementById('locations-data');
            if (hiddenField) {
                hiddenField.value = locationsData;
                console.log('Submitting locations to server: ', locationsData);
            } else {
                console.log("Warning: No hidden field for locations");
            }
        });
    }

    //Add event listeners for trip page if the element exists
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
            cancelLocationPreview();        //cancel any preview when closing the form
        });
    }

    //prevent page refresh 
    const locationForm = document.getElementById('locationForm');
    if(locationForm) {
        locationForm.addEventListener('submit', function(e) {
            e.preventDefault();

            //debug
            console.log('Form submitted.,checking for preview place now');
            console.log('currentPreviewPlace: ', currentPreviewPlace);

            //if got preview place ffrom the search, add it with the form info
            setTimeout(() => {
                if (currentPreviewPlace) {
                    console.log('Adding location to trip')      //debugging
                    addLocationToTrip(currentPreviewPlace);
                    cancelLocationPreview();
                    console.log('Location is added successfully');
                } else {
                    alert('Please search for a location first.');
                }
            },100);
         });
    }   

    //add to trip button functionality
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('add-to-trip-btn')) {
            const lat = parseFloat(e.target.dataset.lat);
            const lng = parseFloat(e.target.dataset.lng);
            const name = e.target.dataset.name;
            const description= e.target.dataset.description;
            const category = e.target.dataset.category;

            addLocationFromCard(name, description,category, lat, lng);

            //show confirmation
            e.target.innerHTML = '<i class="plus"></i> Added!';
            e.target.style.background = '#28a745';

            //reset button after 2 secs
            setTimeout(()=> {
                e.target.innerHTML = '<i class="plus"></i> Add to Trip';
                e.target.style.background = '';
            }, 2000);
        }
    });



    //show on map button
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('show-on-map-btn')) {
            const lat = parseFloat(e.target.dataset.lat);
            const lng = parseFloat(e.target.dataset.lng);
            const name = e.target.dataset.name;

            if (map) {
                map.setCenter({lat: lat, lng: lng});
                map.setZoom(15);

                //create temporary marker to highlight location
                const tempMarker = new google.maps.Marker({
                    position: {lat: lat, lng: lng},
                    map: map,
                    title: name,
                    animation: google.maps.Animation.BOUNCE
                });

                //remove the animation after 2 seconds
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

