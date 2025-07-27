from datetime import datetime

class Event:
    def __init__(self, location_data):
        self.start_time = location_data['start_time']
        self.start_date = location_data['start_date']
        self.end_time = location_data['end_time']
        self.end_date = location_data['end_date']
        self.event_id = location_data['id']
        self.data = location_data

        self.start_datetime = datetime.strptime(f"{self.start_date} {self.start_time}", "%Y-%m-%d %H:%M:%S")
        self.end_datetime = datetime.strptime(f"{self.end_date} {self.end_time}", "%Y-%m-%d %H:%M:%S")

def detect_conflicts(events):
    events.sort(key = lambda x: x.start_datetime)
    ret = []
    S = set()
    for event in events:
        for sec_event in events:
            if event == sec_event: continue
            if (event.start_datetime < sec_event.end_datetime and event.end_datetime > sec_event.start_datetime) or \
                (sec_event.start_datetime < event.end_datetime and sec_event.end_datetime > event.start_datetime):
                if event.event_id not in S:
                    S.add(event.event_id)
                    ret.append(event.data)
                if sec_event.event_id not in S:
                    S.add(sec_event.event_id)
                    ret.append(sec_event.data)
    return ret

    # time_points = []

    # for event in events:
    #     time_points.append((event.start_datetime, "start", event.event_id))
    #     time_points.append((event.end_datetime, "end", event.event_id))

    # time_points.sort(key=lambda x: (x[0], x[1] == "start", x[2]))

    # active_events = set()
    # conflicts = []

    # for time, event_type, event_id in time_points:
    #     if event_type == "start":
    #         if active_events:  
    #             conflicts.append(event.data)
    #         active_events.add(event_id)
    #     else:  
    #         try:
    #             active_events.remove(event_id)
    #         except KeyError:
    #             continue
    # if len(conflicts) == 1:
    #     conflicts = []

    # return conflicts
