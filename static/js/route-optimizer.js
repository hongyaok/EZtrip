// sources
// https://developers.google.com/maps/documentation/javascript/tutorials
// https://developers.google.com/maps/documentation/routes/compute-route-over

let googleDirectionsService;
let isGoogleMapsReady = false;
let globalRouteData = {};

function initializeGoogleMaps() {
    //console.log('Setting up Google Maps...');
    if (typeof google !== 'undefined' && google.maps) {
        googleDirectionsService = new google.maps.DirectionsService();
        isGoogleMapsReady = true;
        //console.log('Google Maps is ready')
    } else {
        //console.log('Google maps is not ready');
        setTimeout(initializeGoogleMaps, 1000)
    }
}

//function called when user clicks on the optimization button
function showOptimizeModal() {
    //console.log('user clicked Optimize Route');
    if (!isGoogleMapsReady) {
        alert('Please wait for a moment, Google Maps is still loading...');
        return ;
    }
    startOptimization();
}

//Close the modal
function closeOptimizeModal() {
    document.getElementById('optimizeModal').style.display = 'none';
}

//start optimising with smart recommendations
async function startOptimization() {
    //console.log('Starting route optimization');
    try{
        showGlobalLoadingMessage();
        const dayElements = document.querySelectorAll('.day-section');
        if (dayElements.length == 0) {
            throw new Error('No trip days found. Please add some location first');
        }
        //console.log(`Found ${dayElements.length} days to optimize`);
        const routeData = {};
        for (let i = 0; i <dayElements.length; i++) {
            const dayElement = dayElements[i];
            const date = dayElement.getAttribute('data-date');
            if (!date) continue;
            //console.log(`Processing day: ${date}`);
            const activities = getActivitiesForDay(dayElement);
            if (activities.length < 2) {
                //console.log(`Day ${date} has less than 2 activities, skipping`);
                continue;
            }
            routeData[date] = await calculateAllRoutesForDay(activities);
        }
        hideGlobalLoadingMessage();
        displayRouteOptimizationModal(routeData);
    } catch(error) {
        //console.error('Error during opitimization', error);
        hideGlobalLoadingMessage();
        alert('Error: ' + error.message);
    }
}

//get data from google maps API
function getRouteFromGoogle(fromActivity, toActivity, method) {
    return new Promise((resolve) => {
        if (!fromActivity.lat || !fromActivity.lng || !toActivity.lat || !toActivity.lng) {
            //console.warn(`missing coordinate fro ${fromActivity.name} or ${toActivity.name}`);
            resolve(null);
            return;
        }
        const request = {
            origin: new google.maps.LatLng(fromActivity.lat, fromActivity.lng),
            destination: new google.maps.LatLng(toActivity.lat, toActivity.lng),
            travelMode: google.maps.TravelMode[method]
        };
        if (method == 'TRANSIT') {
            request.transitOptions = {
                modes: ['BUS', 'TRAIN'],
                routingPreference: 'FEWER_TRANSFERS'
            };
        }
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
                //console.log(`${method}: ${routeData.minutes} min, ${routeData.distance}`);
                resolve(routeData);
            } else {
                //console.warn(`Google Maps error for ${method}: ${status}`);
                resolve(null);
            }
        });
    });
}

async function calculateAllRoutesForDay(activities) {
    //console.log(`Calculating routes for ${activities.length} activities`);
    const routes = [];
    for(let i = 0; i < activities.length - 1; i++) {
        const fromActivity = activities[i];
        const toActivity = activities[i+1];
        //console.log(`Route from ${fromActivity.name} to ${toActivity.name}`);
        const [driving, walking, transit] = await Promise.all([
            getRouteFromGoogle(fromActivity, toActivity, 'DRIVING'),
            getRouteFromGoogle(fromActivity, toActivity, 'WALKING'),
            getRouteFromGoogle(fromActivity, toActivity, 'TRANSIT'),
        ]);
        const options = {
            driving: driving,
            walking: walking,
            transit: transit
        };
        const validOptions = Object.entries(options).filter(([_, data]) => data !== null);
        let selectedMode = 'DRIVING';
        if (validOptions.length > 0) {
            const fastest = validOptions.reduce((min, [mode, data]) => {
                return data.minutes < min.minutes ? { mode, minutes: data.minutes } : min;
            }, { mode: validOptions[0][0], minutes: validOptions[0][1].minutes });
            selectedMode = fastest.mode.toUpperCase();
        }
        routes.push({
            from: fromActivity.name,
            to: toActivity.name,
            options: options,
            selected: selectedMode
        });
    }
    return routes;
}

function displayRouteOptimizationModal(routeData) {
    globalRouteData = routeData;
    const modal = document.getElementById('optimizeModal');
    modal.innerHTML = `
        <div class="modal-content">
            <div class="container">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3>Optimize Trip Routes</h3>
                <div style="position: relative;">
                        <span style="
                            display: inline-block;
                            width: 20px;
                            height: 20px;
                            background-color: #007bff;
                            color: white;
                            border-radius: 50%;
                            text-align: center;
                            line-height: 20px;
                            font-size: 14px;
                            cursor: pointer;
                            font-weight: bold;
                        " title="Instructions:\nClick on different transport options to compare routes\nClick on route headers to view detailed directions">?</span>
                    </div>
                </div>
                <div id="route-sections-container">
                </div>
                <div class="clearfix">
                    <button type="button" class="cancelbtn" onclick="closeOptimizeModal()">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="closeOptimizeModal()">Done</button>
                </div>
            </div>
        </div>
    `;
    const container = document.getElementById('route-sections-container');
    let html = '';
    Object.entries(routeData).forEach(([date, routes]) => {
        html += `
            <div class="date-section">
                <h4>${date}</h4>
                ${routes.map((route, index) => createRouteSection(route, date, index)).join('')}
            </div>
            `;
    });
    container.innerHTML = html;
    document.getElementById('optimizeModal').style.display = 'flex';
}

function createRouteSection(route, date, index) {
    const sectionId = `route-${date.replace(/\s+/g, '-')}-${index}`;
    return `
        <div class="route-section">
            <div class="route-header" onclick="toggleRouteDetails('${sectionId}')">
                <span class="route-path">${route.from} -> ${route.to}</span>
            </div>
            <div class="transport-options">
                ${createTransportButtons(route, sectionId)}
            </div>
            <div id="${sectionId}-details" class="route-details" style="display: none;">
            </div>
        </div>
    `;
}

function createTransportButtons(route, sectionId) {
    const transportModes = [
        { key: 'driving', icon: '🚗', label: 'Driving' },
        { key: 'walking', icon: '🚶', label: 'Walking' },
        { key: 'transit', icon: '🚌', label: 'Transit' }
    ];
    return transportModes.map(mode => {
        const routeData = route.options[mode.key];
        const isSelected = route.selected.toLowerCase() === mode.key;
        const isDisabled = !routeData;
        if (isDisabled) {
            return `
                <button class="transport-option disabled" disabled>
                    ${mode.icon} N/A
                </button>
            `;
        }
        return `
            <button class="transport-option ${isSelected? 'selected' : ''}" 
                    onclick="selectTransportMode('${sectionId}', '${mode.key}', event)">
                ${mode.icon} ${routeData.formattedTime}
            </button>
        `;
    }).join('');
}

function selectTransportMode(sectionId, mode, event) {
    event.stopPropagation();
    const section = document.querySelector(`#${sectionId}-details`).parentElement;
    const buttons = section.querySelectorAll('.transport-option'); 
    buttons.forEach(btn => btn.classList.remove('selected'));
    event.target.classList.add('selected');
    const detailsDiv = document.getElementById(`${sectionId}-details`);
    if (detailsDiv.style.display !== 'none') {
        updateRouteDetails(sectionId, mode);
    }
}

function  toggleRouteDetails(sectionId) {
    const detailsDiv = document.getElementById(`${sectionId}-details`);
    if (detailsDiv.style.display === 'none') {
        const section = detailsDiv.parentElement;
        const selectedButton = section.querySelector('.transport-option.selected');
        if (selectedButton) {
            const buttonText = selectedButton.textContent;
            let mode = 'driving'
            if (buttonText.includes('🚗')) mode = 'driving';
            else if (buttonText.includes('🚶')) mode = 'walking';
            else if (buttonText.includes('🚌')) mode = 'transit';
                updateRouteDetails(sectionId, mode);
        }
        detailsDiv.style.display = 'block';
    } else {
        detailsDiv.style.display = 'none';
    }
}

function updateRouteDetails(sectionId, mode) {
    const detailsDiv = document.getElementById(`${sectionId}-details`);
    const routeData = getRouteDataFromSection(sectionId, mode);
    if (routeData && routeData.directions) {
        let modeDisplayName = mode.toUpperCase();
        if (mode === 'transit') {
            modeDisplayName = "PUBLIC TRANSPORT"
        }
        detailsDiv.innerHTML = `
            <div style="margin: 0; padding: 0; text-align: left;">
                <div style="margin: 0 0 3px 0; padding: 0; text-align: left;">
                    <strong style="font-size: 1.1em; color: #333; text-align: left; display: block;">${modeDisplayName} DIRECTIONS:</strong>
                    <div style="margin: 0 0 3px 0; padding: 0; text-align: left; color: #666; font-size: 1.1em;">
                        <div style="margin: 0; padding: 0;"><strong>Duration:</strong> ${routeData.formattedTime}</div>
                        <div style="margin: 0; padding: 0;"><strong>Distance:</strong> ${routeData.distance}</div>
                    </div>
                </div>
                <div style="margin: 0; padding: 0; line-height: 1.5; font-family: monospace; font-size: 1.2em; margin: 0; padding: 0; text-align: left;">
                    ${routeData.directions.replace(/\n/g, '<br>')}
                </div>
            </div>
        `;
    } else {
        let modeDisplayName = mode.toUpperCase();
        if (mode === 'transit') {
            modeDisplayName = "PUBLIC TRANSPORT"
        }
        detailsDiv.innerHTML = `
        <div style="margin: 0; padding: 0; text-align: left;">
            <div style="margin: 0 0 3px 0; padding: 0; text-align: left;">
                <strong style="font-size: 1.1em; color: #333; text-align: left; display: block;">${modeDisplayName} DIRECTIONS:</strong>
            </div>
            <div style="margin: 0; padding: 0; color: #999; font-size: 1.1em; text-align: left;">
                Directions not available for this route.
            </div>
        </div>
    `;
    }
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

//helper function to retrieve route data
function getRouteDataFromSection(sectionId, mode) {
    const parts = sectionId.split('-');
    const routeIndex = parseInt(parts[parts.length - 1]);
    for (const [date, routes] of Object.entries(globalRouteData)) {
        if (routes[routeIndex] && routes[routeIndex].options[mode]){
            return routes[routeIndex].options[mode];
        }
    }
    return null;
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
    //console.log('route optimizer loading');
    initializeGoogleMaps();
    //console.log('Ready.');
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
                    //console.log('HTML instructions:', step.html_instructions);
                }
            }
            if (index < steps.length - 1) {
                directions.push('');
                directions.push('   ↓');
                directions.push('');
            }
        });
    } else {
        let routeType;
        if (travelMode === 'WALKING') {
            routeType = '🚶‍♂️ WALKING';
        } else if (travelMode === 'DRIVING') {
            routeType = '🚗 DRIVING';
        } else {
            routeType = '🚴‍♂️ CYCLING';
        }
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
            if (index < steps.length - 1) {
                directions.push('');
            }
        });
    }
    return directions.join('\n');
}
