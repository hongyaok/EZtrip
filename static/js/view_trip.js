let map;
let markers = [];
let autocompleteService;
let placesService;
let selectedLocation = null;

// This function will be called by Google Maps API

window.initMap = function() {
    const defaultLocation = { lat: 1.3521, lng: 103.8198 }; // Singapore
    
    map = new google.maps.Map(document.getElementById('map'), {
        center: defaultLocation,
        zoom: 12,
        styles: [
            {
                featureType: 'poi',
                elementType: 'labels',
                stylers: [{ visibility: 'on' }]
            }
        ]
    });

    autocompleteService = new google.maps.places.AutocompleteService();
    placesService = new google.maps.places.PlacesService(map);
    
    // Load existing locations on map
    loadLocationsOnMap();
    
    // Setup location search
    setupLocationSearch();
    
    // Setup event listeners after map is loaded
    setupEventListeners();
};

function initMap() {
    const defaultLocation = { lat: 1.3521, lng: 103.8198 }; // Singapore
    
    map = new google.maps.Map(document.getElementById('map'), {
        center: defaultLocation,
        zoom: 12,
        styles: [
            {
                featureType: 'poi',
                elementType: 'labels',
                stylers: [{ visibility: 'on' }]
            }
        ]
    });

    autocompleteService = new google.maps.places.AutocompleteService();
    placesService = new google.maps.places.PlacesService(map);
    
    // Load existing locations on map
    loadLocationsOnMap();
    
    // Setup location search
    setupLocationSearch();
    
    // Setup event listeners after map is loaded
    setupEventListeners();
}

function setupEventListeners() {
    // Add location button
    const addLocationBtn = document.getElementById('add-location-btn');
    if (addLocationBtn) {
        addLocationBtn.addEventListener('click', toggleAddLocation);
    }
    
    // Cancel button
    const cancelBtn = document.getElementById('cancel-location-btn');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', toggleAddLocation);
    }
    
    // Vote buttons
    document.querySelectorAll('.vote-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const locationId = this.getAttribute('data-location-id');
            const voteType = this.getAttribute('data-vote');
            vote(locationId, voteType);
        });
    });
    
    // Add to itinerary buttons
    document.querySelectorAll('.add-to-itinerary-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const locationId = this.getAttribute('data-location-id');
            addToItinerary(locationId);
        });
    });
    
    // Show on map buttons
    document.querySelectorAll('.show-on-map-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const lat = parseFloat(this.getAttribute('data-lat'));
            const lng = parseFloat(this.getAttribute('data-lng'));
            const name = this.getAttribute('data-name');
            showOnMap(lat, lng, name);
        });
    });
    
    // Category filter
    const categoryFilter = document.getElementById('category-filter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            filterLocations(this.value);
        });
    }
    
    // Location form submission
    const locationForm = document.getElementById('locationForm');
    if (locationForm) {
        locationForm.addEventListener('submit', handleLocationSubmit);
    }
    
    // Optimize route button
    const optimizeBtn = document.getElementById('optimize-route-btn');
    if (optimizeBtn) {
        optimizeBtn.addEventListener('click', optimizeRoute);
    }
}

function setupLocationSearch() {
    const searchInput = document.getElementById('location-search');
    const resultsDiv = document.getElementById('search-results');
    
    if (!searchInput || !resultsDiv) return;
    
    searchInput.addEventListener('input', function() {
        const query = this.value;
        if (query.length < 3) {
            resultsDiv.innerHTML = '';
            return;
        }
        
        autocompleteService.getPlacePredictions({
            input: query,
            types: ['establishment', 'geocode']
        }, (predictions, status) => {
            if (status === google.maps.places.PlacesServiceStatus.OK && predictions) {
                displaySearchResults(predictions);
            }
        });
    });
}

function displaySearchResults(predictions) {
    const resultsDiv = document.getElementById('search-results');
    resultsDiv.innerHTML = '';
    
    predictions.forEach(prediction => {
        const resultItem = document.createElement('div');
        resultItem.className = 'search-result-item';
        resultItem.innerHTML = `
            <div class="result-name">${prediction.structured_formatting.main_text}</div>
            <div class="result-address">${prediction.structured_formatting.secondary_text || ''}</div>
        `;
        
        resultItem.addEventListener('click', function() {
            selectSearchResult(prediction);
        });
        
        resultsDiv.appendChild(resultItem);
    });
}

function selectSearchResult(prediction) {
    placesService.getDetails({
        placeId: prediction.place_id,
        fields: ['name', 'geometry', 'formatted_address', 'types']
    }, (place, status) => {
        if (status === google.maps.places.PlacesServiceStatus.OK) {
            selectedLocation = {
                name: place.name,
                lat: place.geometry.location.lat(),
                lng: place.geometry.location.lng(),
                address: place.formatted_address
            };
            
            document.getElementById('location-name').value = place.name;
            document.getElementById('location-search').value = place.name;
            document.getElementById('search-results').innerHTML = '';
            
            // Show location on map
            showLocationOnMap(selectedLocation.lat, selectedLocation.lng, selectedLocation.name);
        }
    });
}

function showLocationOnMap(lat, lng, name) {
    const position = { lat: lat, lng: lng };
    
    // Clear previous temporary markers
    markers.forEach(marker => {
        if (marker.temporary) {
            marker.setMap(null);
        }
    });
    markers = markers.filter(marker => !marker.temporary);
    
    // Add new marker
    const marker = new google.maps.Marker({
        position: position,
        map: map,
        title: name,
        temporary: true,
        icon: {
            url: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png'
        }
    });
    
    markers.push(marker);
    map.setCenter(position);
    map.setZoom(15);
}

function loadLocationsOnMap() {
    // Check if locations data exists
    if (!window.tripData || !window.tripData.locations) return;
    
    const locations = window.tripData.locations;
    
    locations.forEach(location => {
        if (location.lat && location.lng) {
            const marker = new google.maps.Marker({
                position: { lat: parseFloat(location.lat), lng: parseFloat(location.lng) },
                map: map,
                title: location.name,
                icon: {
                    url: getCategoryIcon(location.category)
                }
            });
            
            const infoWindow = new google.maps.InfoWindow({
                content: `
                    <div class="info-window">
                        <h4>${location.name}</h4>
                        <p>${location.description || ''}</p>
                        <div class="info-actions">
                            <button onclick="addToItinerary(${location.id})">Add to Itinerary</button>
                        </div>
                    </div>
                `
            });
            
            marker.addListener('click', function() {
                infoWindow.open(map, marker);
            });
            
            markers.push(marker);
        }
    });
}

function getCategoryIcon(category) {
    const icons = {
        restaurant: 'https://maps.google.com/mapfiles/ms/icons/restaurant.png',
        attraction: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
        accommodation: 'https://maps.google.com/mapfiles/ms/icons/lodging.png',
        shopping: 'https://maps.google.com/mapfiles/ms/icons/shopping.png',
        entertainment: 'https://maps.google.com/mapfiles/ms/icons/movies.png',
        other: 'https://maps.google.com/mapfiles/ms/icons/yellow-dot.png'
    };
    return icons[category] || icons.other;
}

// Form and UI functions
function toggleAddLocation() {
    const form = document.getElementById('add-location-form');
    if (form.style.display === 'none' || form.style.display === '') {
        form.style.display = 'block';
    } else {
        form.style.display = 'none';
        // Reset form
        document.getElementById('locationForm').reset();
        selectedLocation = null;
        document.getElementById('search-results').innerHTML = '';
    }
}

function handleLocationSubmit(e) {
    e.preventDefault();
    
    if (!selectedLocation) {
        alert('Please select a location from the search results');
        return;
    }
    
    const formData = {
        trip_id: window.tripData.tripId,
        name: document.getElementById('location-name').value,
        description: document.getElementById('location-description').value,
        category: document.getElementById('location-category').value,
        lat: selectedLocation.lat,
        lng: selectedLocation.lng,
        address: selectedLocation.address
    };
    
    fetch('/api/locations', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload(); // Reload to show new location
        } else {
            alert('Error adding location: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error adding location');
    });
}

function showOnMap(lat, lng, name) {
    showLocationOnMap(lat, lng, name);
}

// Voting functions
function vote(locationId, voteType) {
    fetch('/api/vote', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            location_id: locationId,
            vote_type: voteType
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update vote counts in UI
            updateVoteDisplay(locationId, data.upvotes, data.downvotes, data.user_vote);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function updateVoteDisplay(locationId, upvotes, downvotes, userVote) {
    const locationCard = document.querySelector(`[data-location-id="${locationId}"]`);
    if (!locationCard) return;
    
    const upvoteBtn = locationCard.querySelector('.upvote');
    const downvoteBtn = locationCard.querySelector('.downvote');
    
    if (upvoteBtn) {
        upvoteBtn.innerHTML = `<i class="fas fa-thumbs-up"></i> ${upvotes}`;
        upvoteBtn.classList.toggle('voted', userVote === 'up');
    }
    
    if (downvoteBtn) {
        downvoteBtn.innerHTML = `<i class="fas fa-thumbs-down"></i> ${downvotes}`;
        downvoteBtn.classList.toggle('voted', userVote === 'down');
    }
}

// Itinerary functions
function addToItinerary(locationId) {
    fetch('/api/itinerary/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            location_id: locationId,
            trip_id: window.tripData.tripId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Refresh itinerary section
            loadItinerary();
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function optimizeRoute() {
    fetch('/api/itinerary/optimize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            trip_id: window.tripData.tripId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadItinerary();
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function filterLocations(selectedCategory) {
    const locationCards = document.querySelectorAll('.location-card');
    
    locationCards.forEach(card => {
        if (selectedCategory === 'all' || card.dataset.category === selectedCategory) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

function loadItinerary() {
    // This function would reload the itinerary section
    // For now, just reload the page
    location.reload();
}
