from datetime import datetime

class Event:
    def __init__(self, location_data):
        self.start_time = location_data['start_time']
        self.start_date = location_data['start_date']
        self.end_time = location_data['end_time']
        self.end_date = location_data['end_date']
        self.event_id = location_data['id']
        self.data = location_data

        # Combine date and time into datetime objects
        self.start_datetime = datetime.strptime(f"{self.start_date} {self.start_time}", "%Y-%m-%d %H:%M:%S")
        self.end_datetime = datetime.strptime(f"{self.end_date} {self.end_time}", "%Y-%m-%d %H:%M:%S")

def detect_conflicts(events):
    time_points = []

    # Create time points using datetime
    for event in events:
        time_points.append((event.start_datetime, "start", event.event_id))
        time_points.append((event.end_datetime, "end", event.event_id))

    # Sort time points
    time_points.sort(key=lambda x: (x[0], x[1] == "start", x[2]))

    active_events = set()
    conflicts = []

    # Sweep through time points
    for time, event_type, event_id in time_points:
        if event_type == "start":
            if active_events:  # Conflict detected
                conflicts.append(event.data)
            active_events.add(event_id)
        else:  # event_type == "end"
            try:
                active_events.remove(event_id)
            except KeyError:
                continue
    if len(conflicts) == 1:
        conflicts = []

    return conflicts
