let googleDirectionsService;
let isGoogleMapsReady = false;

function initializeGoogleMaps() {
    console.log('Setting up Google Maps...');

    if (typeof google !== 'undefined' && google.maps) {
        googleDirectionsService = new google.maps.DirectionsService();
        isGoogleMapsReady = true;
        console.log('Google Maps is ready')
    } else {
        console.log('Google maps is not ready');
        setTimeout(initializeGoogleMaps, 1000)
    }
}

//function called when user clicks on the optimization button
function showOptimizeModal() {
    console.log('user clicked Optimize Route');

    if (!isGoogleMapsReady) {
        alert('Please wait for a moment, Google Maps is still loading...');
        return ;
    }

    //show the options to the user
    createSmartPreferenceModal();
    document.getElementById('optimizeModal').style.display = 'flex';
}

//Close the modal
function closeOptimizeModal() {
    document.getElementById('optimizeModal').style.display = 'none';
}

//create the smart preference model for users
function createSmartPreferenceModal() {
    const modal = document.getElementById('optimizeModal');

    modal.innerHTML = `
        <div class="modal-content">
            <div class="container">
                <h3>Smart Route Optimization</h3>
                <p>Select your preferred transportation methods.</p>

                <div class="smart-preferences">
                    <h4>Your Transportation Preferences:</h4>
                    <div class="preference-options">
                        <div class="preference-option">
                            <input type="checkbox" id="pref-walking" value="WALKING" checked>
                            <label for="pref-walking">🚶‍♂️ Walking</label>
                        </div>
                         <div class="preference-option">
                            <input type="checkbox" id="pref-public" value="TRANSIT" checked>
                            <label for="pref-public">🚌 Public Transport</label>
                        </div>
                         <div class="preference-option">
                            <input type="checkbox" id="pref-driving" value="DRIVING" checked>
                            <label for="pref-driving">🚗 Driving</label>
                        </div>
                    </div>
                </div>

                <div class="clearfix">
                    <button type="button" class="cancelbtn" onclick="closeOptimizeModal()">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="startSmartOptimization()">Optimize with Preferences</button>
                </div>
            </div>
        </div>  
    `;
}

//start optimising with smart recommendations
async function startSmartOptimization() {
    console.log('Starting smart optimization');

    try {
        //get the users' preferences first
        const userPreferences = getUserPreferences();
        console.log('User preferences:', userPreferences);

        //close the modal and show the loading 
        closeOptimizeModal();
        showGlobalLoadingMessage();

        //get all the days inside the itinerary
        const dayElements = document.querySelectorAll('.day-section');

        if (dayElements.length == 0) {
            throw new Error('No trip days found. Please add some locations first');
        }
        console.log(`Found ${dayElements.length} days to optimize`);

        //process each day
        for (let i=0; i<dayElements.length; i++) {
            const dayElement = dayElements[i];
            const date = dayElement.getAttribute('data-date');

            if (!date) continue;

            console.log(`optimizing day ${i+1}: ${date}`);

            //get the activities for the day
            const activities = getActivitiesForDay(dayElement);

            if (activities.length < 2) {
                console.log(`Day ${date} has less than 2 activities, skipping...`);
                continue;
            }

            //optimize the particular day with recommendations
            await optimizeDayWithPreferences(date, activities, userPreferences);
        }
        hideGlobalLoadingMessage();
        showSuccessMessage();
    } catch(error) {
        console.error('Error during optimization:', error)
        hideGlobalLoadingMessage();
        alert('Error: ' + error.message);
    }
}

//get users' preference
function getUserPreferences() {
    const preferences = [];
    const checkboxes = document.querySelectorAll('.preference-option input[type="checkbox"]:checked');

    checkboxes.forEach(checkbox => {
        preferences.push(checkbox.value);
    });
    return preferences;
}

//optimize each day with smart preferences
async function optimizeDayWithPreferences(date, activities, userPreferences) {
    console.log(`Calculating smart recommendations for ${activities.length} activities on ${date}`);

    //process each route within the day
    for (let i=0; i <activities.length - 1; i++) {
        const fromActivity = activities[i];
        const toActivity = activities[i+1];

        console.log(`Route from ${fromActivity.name} to ${toActivity.name}`);

        //calculate all transport methods for this route segment
        const allRouteOptions = await calculateAllTransportMethods(fromActivity, toActivity);

        //display options with our smart recommendation
        displaySmartRouteOptions(fromActivity.id, allRouteOptions, userPreferences);
    }
}

//calculate all 4 transport methods for each individual route
async function calculateAllTransportMethods(fromActivity, toActivity) {
    console.log('Calculating all transport methods');

    const transportMethods = ['DRIVING', 'TRANSIT', 'WALKING'];
    const routePromises = [];

    for (const method of transportMethods) {
        const promise = getRouteFromGoogle(fromActivity, toActivity, method);
        routePromises.push(promise);
    }
    const results = await Promise.all(routePromises);

    //filter the failed routes and orgainise the result
    const routeOptions = {
        driving: results[0],
        transit: results[1],
        walking: results[2],
    };

    //remove null results
    Object.keys(routeOptions).forEach(key => {
        if (routeOptions[key] === null) {
            delete routeOptions[key];
        }
    });

    console.log(`Got ${Object.keys(routeOptions).length} valid route options`);
    return routeOptions;
}

//get data from google maps API
function getRouteFromGoogle(fromActivity, toActivity, method) {
    return new Promise((resolve) => {
        //check if have the coordinates
        if (!fromActivity.lat || !fromActivity.lng || !toActivity.lat || !toActivity.lng) {
            console.warn(`missing coordinate fro ${fromActivity.name} or ${toActivity.name}`);
            resolve(null);
            return;
        }

        //prep Google Maps request
        const request = {
            origin: new google.maps.LatLng(fromActivity.lat, fromActivity.lng),
            destination: new google.maps.LatLng(toActivity.lat, toActivity.lng),
            travelMode: google.maps.TravelMode[method]
        };

        //for public transport
        if (method == 'TRANSIT') {
            request.transitOptions = {
                modes: ['BUS', 'TRAIN'],
                routingPreference: 'FEWER_TRANSFERS'
            };
        }

        //call google maps api
        googleDirectionsService.route(request, function(response, status) {
            if (status == 'OK' && response.routes.length > 0) {
                const route = response.routes[0];
                const leg = route.legs[0];

                const routeData = {
                    method: getMethodName(method),
                    icon: getMethodIcon(method),
                    minutes: Math.round(leg.duration.value / 60),
                    formattedTime: formatDuration(leg.duration.value),
                    distance: leg.distance.text,
                    directions: getSimpleDirections(leg.steps, method),
                    rawMethod: method,
                    fromLocation: fromActivity.name,
                    toLocation: toActivity.name
                };

                console.log(`${method}: ${routeData.minutes} min, ${routeData.distance}`);
                resolve(routeData);
            } else {
                console.warn(`Google Maps error for ${method}: ${status}`);
                resolve(null);
            }
        });
    });
}

//display the route options with recommendations
function displaySmartRouteOptions(fromActivityId, routeOptions, userPreferences) {
    const routeElement = document.getElementById(`route-info-${fromActivityId}`);

    if (!routeElement || Object.keys(routeOptions).length == 0){
        return;
    }

    //find the fastest option
    const allOptions = Object.values(routeOptions);
    const fastestOption = allOptions.reduce((fastest, current) =>
        current.minutes < fastest.minutes? current : fastest
    );

    //Filter options to only show preferred transport methods
    const filteredOptions = allOptions.filter(option => 
        userPreferences.includes(option.rawMethod)
    );

    // If no preferred options are available, show all options (just in case)
    const optionsToShow = filteredOptions.length > 0 ? filteredOptions : allOptions;

    //create html to show the options 
    let optionsHTML = '<div class="route-options-container">';
    
    //sort by travel time - use optionsToShow instead of allOptions
    const sortedOptions = optionsToShow.sort((a,b) => a.minutes - b.minutes);

    sortedOptions.forEach((option)=> {
        const isFastest = option.minutes == fastestOption.minutes;

        let cardClass = 'transport-option-card';
        let badges = '';

        if (isFastest) {
            cardClass += ' fastest-option';
            badges += '<span class="fastest-badge">⚡FASTEST</span>';
        }

        optionsHTML += `
            <div class="${cardClass}" onclick="showRouteDetails('${option.method}', '${option.formattedTime}', '${option.distance}', \`${option.directions}\`, '${option.fromLocation}', '${option.toLocation}')">
                <div class="option-header">
                    <span class="option-icon">${option.icon}</span>
                    <span class="option-method">${option.method}</span>
                    ${badges}
                </div>
                <div class="option-details">
                    <span class="option-time">${option.formattedTime}</span>
                    <span class="option-distance">${option.distance}</span>
                </div>
            </div>
        `;
    });

    optionsHTML += '</div>';

    //display the options
    routeElement.innerHTML = optionsHTML;
    routeElement.style.display ='block';
}

//show the detailed info when user clicks on an option
function showRouteDetails(method, minutes, distance, directions, fromLocation, toLocation) {
    //create a popup
    const popup = document.createElement('div');
    popup.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        border: 2px solid #333;
        padding: 20px;
        max-width: 600px;
        max-height: 700px;
        overflow-y: auto;
        z-index: 10000;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    `;

    //create overlay background 
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        z-index: 9999;
    `;

    popup.innerHTML = `
        <h3>${method} Route Details </h3>
        <p><strong>From:</strong> ${fromLocation}</p>
        <p><strong>To:</strong> ${toLocation}</p>
        <p><strong>Duration:</strong> ${minutes}</p>
        <p><strong>Distance:</strong> ${distance}</p>
        <hr>
        <pre style="white-space: pre-wrap; font-family: Arial; font-size: 14px; line-height: 1.4;">${directions}</pre>
        <br>
        <button onclick="closePopup()" style="background: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">Close</button>
    `;

    //close popup 
    overlay.onclick = function() {
        closePopup();
    };

    //Add to page
    document.body.appendChild(overlay);
    document.body.appendChild(popup);

    window.currentPopup = popup;
    window.currentOverlay = overlay;
}

function closePopup() {
     if (window.currentPopup) {
        document.body.removeChild(window.currentPopup);
        window.currentPopup = null;
    }
    if (window.currentOverlay) {
        document.body.removeChild(window.currentOverlay);
        window.currentOverlay = null;
    }
}

//helper function to get activities from each day
function getActivitiesForDay(dayElement) {
    const timelineItems = dayElement.querySelectorAll('.timeline-item');
    const activities = [];

    timelineItems.forEach(item => {
        const id = item.getAttribute('data-activity-id');
        const nameElement = item.querySelector('.activity-info h5');
        const locateButton = item.querySelector('.locate-btn');

        if (nameElement && locateButton) {
            const activity = {
                id: id,
                name: nameElement.textContent.trim(),
                lat: parseFloat(locateButton.getAttribute('data-lat')),
                lng: parseFloat(locateButton.getAttribute('data-lng'))
            };

            //include those places/activites with valid coordinate
            if (!isNaN(activity.lat) && !isNaN(activity.lng)) {
                activities.push(activity);
            }
        }
    });
    return activities;
}

//helper function for transport methods
function getMethodName(method) {
    const names = {
        'WALKING': 'Walking',
        'DRIVING': 'Driving',
        'TRANSIT': 'Public Transport',
    };
    return names[method] || method;
}

function getMethodIcon(method) {
    const icons = {
       'WALKING': '🚶‍♂️',
        'DRIVING': '🚗',
        'TRANSIT': '🚌',
    };
    return icons[method];
}

// UI functions
function showGlobalLoadingMessage() {
    //creating loading
    const overlay = document.createElement('div');
    overlay.id = 'optimization-loading';
    overlay.innerHTML = `
        <div style="
            position: fixed;
            top: 0;
            left: 0; 
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        ">
            <div style="
                background: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
                max-width: 400px;
            ">
                <h3>Optimizing Routes</h3>
                <p>Calculating all transport methods for your entire trip...</p>
                <div style="margin: 20px 0;">
                    <div class="loading-spinner">⏳</div>
                </div>
                <p><small>This will take a moment</small></p>
            </div>
        </div>
    `;
    document.body.appendChild(overlay)
}

function hideGlobalLoadingMessage() {
    const overlay = document.getElementById('optimization-loading');
    if (overlay) {
        overlay.remove();
    }
}

function showSuccessMessage() {
    const notification = document.createElement('div');
    notification.innerHTML = `
        <div style= "
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #4caf50, #45a049);
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        font-weight: 500;
    ">
        Optimized routes have been created. Clicked any transport option for details.
    </div>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 5000);
}

//initialise this when the page laod
document.addEventListener('DOMContentLoaded', function() {
    console.log('route optimizer loading...');
    initializeGoogleMaps();
    console.log('Ready.');
});

//formatting of time 
function formatDuration(seconds) {
    const totalMinutes = Math.round(seconds / 60);

    if (totalMinutes < 60) {
        return `${totalMinutes} min`;
    } else {
        const hours = Math.floor(totalMinutes / 60);
        const minutes = totalMinutes % 60;
        return minutes === 0? `${hours}h` : `${hours}h ${minutes}m`;
    }
}

function getSimpleDirections(steps, travelMode) {
    if (!steps || steps.length === 0) return 'No directions available';
    
    const directions = [];
    
    if (travelMode === 'TRANSIT') {
        directions.push('🚌 PUBLIC TRANSPORT:');
        directions.push(''); 
        
        steps.forEach((step, index) => {
            if (step.travel_mode === 'WALKING') {
                const duration = Math.round(step.duration.value / 60);
                const distance = step.distance ? step.distance.text : '';
                
                // Get walking instruction
                let walkInstruction = 'Walk to destination';
                if (step.instructions) {
                    walkInstruction = step.instructions
                        .replace(/<[^>]*>/g, '')
                        .replace(/&nbsp;/g, ' ')
                        .replace(/&amp;/g, '&')
                        .replace(/&lt;/g, '<')
                        .replace(/&gt;/g, '>')
                        .trim();
                }
                
                directions.push(`🚶‍♂️ Walk ${duration} min (${distance}):`);
                directions.push(`   ${walkInstruction}`);
                
            } else if (step.travel_mode === 'TRANSIT') {
                const duration = Math.round(step.duration.value / 60);
                const distance = step.distance ? step.distance.text : '';
                
                let transitInstruction = 'Take public transport';
                if (step.instructions) {
                    transitInstruction = step.instructions
                        .replace(/<[^>]*>/g, '')
                        .replace(/&nbsp;/g, ' ')
                        .replace(/&amp;/g, '&')
                        .replace(/&lt;/g, '<')
                        .replace(/&gt;/g, '>')
                        .trim();
                }
                
                directions.push(`🚌 ${transitInstruction}:`);
                directions.push(`   Journey time: ${duration} min`);
                directions.push(`   Distance: ${distance}`);
                
                if (step.html_instructions) {
                    console.log('HTML instructions:', step.html_instructions);
                }
            }
            
            // Add separator between steps (not after the last step)
            if (index < steps.length - 1) {
                directions.push('');
                directions.push('   ↓');
                directions.push('');
            }
        });
        
    } else {
        // Handle walking and driving modes
        const routeType = travelMode === 'WALKING' ? '🚶‍♂️ WALKING' : 
                         travelMode === 'DRIVING' ? '🚗 DRIVING' : '🚴‍♂️ CYCLING';
        directions.push(`${routeType}:`);
        directions.push('');
        
        steps.forEach((step, index) => {
            let instruction = 'Continue';
            if (step.instructions) {
                instruction = step.instructions
                    .replace(/<[^>]*>/g, '')
                    .replace(/&nbsp;/g, ' ')
                    .replace(/&amp;/g, '&')
                    .replace(/&lt;/g, '<')
                    .replace(/&gt;/g, '>')
                    .trim();
            }
            
            const distance = step.distance ? step.distance.text : '';
            const timeInfo = travelMode === 'WALKING' ? 
                ` (${Math.round(step.duration.value / 60)} min)` : '';
            
            directions.push(`${index + 1}. ${instruction}`);
            if (distance) {
                directions.push(`   Distance: ${distance}${timeInfo}`);
            }
            
            // Add spacing between steps for readability (not after the last step)
            if (index < steps.length - 1) {
                directions.push('');
            }
        });
    }
    
    return directions.join('\n');
}