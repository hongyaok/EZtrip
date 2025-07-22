from ics import Calendar, Event
from datetime import datetime, time
import os
from pytz import timezone

def convert_to_ics(itinerary, username='EZtrip'):
    try:
        cal = Calendar()
        sg_tz = timezone('Asia/Singapore')
        print(itinerary)
        for date_str, day_info in itinerary.items():
            for activity in day_info['activities']:
                event = Event()
                event.name = activity['name']
                # Parse start and end datetime, localize to SG time
                start_dt = datetime.strptime(f"{activity['start_date']} {activity['start_time']}", "%Y-%m-%d %H:%M:%S")
                end_dt = datetime.strptime(f"{activity['end_date']} {activity['end_time']}", "%Y-%m-%d %H:%M:%S")
                event.begin = sg_tz.localize(start_dt)
                event.end = sg_tz.localize(end_dt)
                event.description = activity['description']
                cal.events.add(event)
        print(cal) #test
        if not os.path.exists('icsFiles'):
            os.makedirs('icsFiles')
        file_name = f'icsFiles/{datetime.now().strftime("%Y-%m-%d")}_{username}.ics'
        with open(file_name, 'w') as f:
            f.writelines(cal)
        print(f"ICS file '{file_name}' created successfully.")
        return file_name
    except Exception as e:
        print(f"Error: {e}")
        return None

def clear_all_ics(ics_dir = 'icsFiles'):
    print(f"\n&&&&&&&&&&&&&&&&&&&&\ncleared all .ics files\n&&&&&&&&&&&&&&&&&&&&\n")
    try:
        if os.path.exists(ics_dir):
            for file in os.listdir(ics_dir):
                file_path = os.path.join(ics_dir, file)
                if os.path.isfile(file_path) and file.endswith('.ics'):
                    os.remove(file_path)
        else:
            print(f"Directory '{ics_dir}' does not exist.")
    except Exception as e:
        print(f"Error: {e}")

# testing
if __name__ == "__main__":
    itinerary = {'2025-06-28': {'date': '2025-06-28', 'activities': [{'id': 36, 'trip_id': 3, 'name': 'JBS BUS STOP STAND, Jubilee Bus Station, Utkoor - Mogdumpur Road, Gandhi Nagar, Nehru Nagar Colony, West Marredpally, Secunderabad, Telangana, India', 'description': 'Jubilee Bus Station, Utkoor - Mogdumpur Rd, Gandhi Nagar, Nehru Nagar Colony, West Marredpally, Secunderabad, Telangana 500026, India - JBS BUS STOP STAND', 'category': 'other', 'end_time': '23:03:00', 'created_at': '2025-06-28T22:03:14.79821', 'start_time': '22:03:00', 'date': '2025-06-28', 'suggested_by': 'HONG YAO KOH', 'removed': False, 'date_removed': '2025-06-28T22:03:14.79821', 'removed_by': 'NULL', 'lat': 17.447807, 'lng': 78.4973758}, {'id': 37, 'trip_id': 3, 'name': 'Testaccio, Rome, Metropolitan City of Rome Capital, Italy', 'description': 'Monte Testaccio, 00153 Rome, Metropolitan City of Rome Capital, Italy - Monte Testaccio', 'category': 'other', 'end_time': '23:04:00', 'created_at': '2025-06-28T22:04:21.031465', 'start_time': '22:04:00', 'date': '2025-06-28', 'suggested_by': 'HONG YAO KOH', 'removed': False, 'date_removed': '2025-06-28T22:04:21.031465', 'removed_by': 'NULL', 'lat': 41.875952, 'lng': 12.475694}]}}
    convert_to_ics(itinerary, username='tester')
    print("ics test done")
    clear_all_ics()
    print("ics clear done")