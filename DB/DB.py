from supabase import create_client
from config import supabase_url, supabase_key, special_key
from datetime import datetime
from zoneinfo import ZoneInfo
from DB.conflicts import detect_conflicts, Event
from pytz import timezone

class DB:
    def __init__(self):
        self.supabase = create_client(supabase_url, special_key)

    def get_user(self, id): # get user from supabase
        response = self.supabase.table('USERS').select('*').eq('google_id', id).execute() #gets the row that matches the 'google_id' column with the id passed in
        if response.data:
            return response.data[0] # returns a dict containing all the user's data (the first matching record)

    def check_user(self, id): # check if user exists in supabase
        if self.get_user(id):
            return True
        else:
            return False
    
    def get_name_from_id(self, id):
        response = self.supabase.table('USERS').select('username').eq('google_id', id).execute()
        if response.data:
            return response.data[0]['username']
        return None
    
    def add_user(self, id, name, email, picture, isAdmin=False): # add new user to supabase
        try:
            data = {
                "google_id": id,
                "username": name,
                "email": email,
                "user_img": picture, # pic should be a link
                "role": isAdmin # havent implement admin privilege
            }
            response = self.supabase.table('USERS').insert(data).execute()
            return response.data
        except Exception as e:
            print(f"db.add_user: {e}")  # debug
            return None
    
    def get_latest_id_from_trips(self):
        response = self.supabase.table('TRIPS').select('trip_id').order('trip_id', desc=True).limit(1).execute()
        #print(response.data)  # debug
        if response.data:
            return response.data[0]['trip_id']
        return None
    
    def check_if_user_in_trip(self, google_id, trip_id): # check if user is in trip
        response = self.supabase.table('USERTRIP').select('*').eq('google_id', google_id).eq('trip_id', trip_id).execute()
        return len(response.data) > 0
    
    def remove_user_from_trip(self, google_id, trip_id): # remove user from trip
        if self.check_if_user_in_trip(google_id, trip_id):
            response = self.supabase.table('USERTRIP').delete().eq('google_id', google_id).eq('trip_id', trip_id).execute()
            try:
                return response.data
            except Exception as e:
                print(f"error removing user from trip: {e}")
                return None
    
    def add_user_to_trip(self, google_id, trip_id): # after user accepts invite, add them to the trip
        if not self.check_if_user_in_trip(google_id, trip_id):
            data = {
                "google_id": google_id,
                "trip_id": trip_id
            }
            response=self.supabase.table('USERTRIP').insert(data).execute()
        try:
            return response.data
        except Exception as e:
            print(f"error adding user to trip: {e}")
            return None
    
    def get_list_of_users_in_trip(self, trip_id, ver=0):
        response = self.supabase.table('USERTRIP').select('google_id').eq('trip_id', trip_id).execute()
        google_ids = [user['google_id'] for user in response.data] if response.data else []
        if not google_ids:
            return []
        
        keywords = {0: 'username', 1: 'email', 2: 'user_img'}
        keyword = keywords.get(ver, 'username')

        users_response = self.supabase.table('USERS').select('google_id', keyword).in_('google_id', google_ids).execute()
        return [user[keyword] for user in users_response.data] if users_response.data else []

    def add_trip(self, google_id, trip_name, dest, theme, start_date, end_date, desc, privacy):
        data = {
            "trip_name": trip_name,
            "dest": dest,
            "theme": theme,
            "start_date": start_date,
            "end_date": end_date,
            "desc": desc,
            "privacy": privacy
        }
        
        try:
            response = self.supabase.table('TRIPS').insert(data).execute()
            
            # if hasattr(response, 'data') and response.data:
            #     print("Trip added successfully!")
            #     print(response.data)
            # else:
            #     print("Error adding trip")
            #     print(response)
            
            id = self.get_latest_id_from_trips()
            if id:
                self.add_user_to_trip(google_id, id)
            return id
        except Exception as e:
            print(f"Error adding trip: {e}")
            return None

    
    def get_all_trips_for_user(self, google_id):
        # First get the trip IDs for the user
        user_trips = (
            self.supabase.from_('USERTRIP')
            .select("trip_id ,TRIPS(*)")
            .eq('google_id', google_id)
            .execute()
        )
        # print(user_trips.data)  # debug
        try:
            all_trips = []
            if user_trips.data:
                for trip in user_trips.data:
                    all_trips.append(trip['TRIPS'])
                    trip_id = all_trips[-1]['trip_id']  # Ensure trip_id is included in the trip data
                    all_users = self.get_list_of_users_in_trip(trip_id, 2) # use 2 to get img
                    all_trips[-1]['user_imgs'] = all_users
                    # print(all_trips[-1])  # debug
                return all_trips

            return []
        except Exception as e:
            print(f"error in get_all_trips_for_user: {e}")
            return []
    
    def get_trip_by_id(self, trip_id):
        response= self.supabase.table('TRIPS').select('*').eq('trip_id', trip_id).execute()
        return response.data[0]

    def user_has_access_to_trip(self, user_id, trip_id):
        response =self.supabase.table('USERTRIP').select('*').eq('google_id', user_id).eq('trip_id', trip_id).execute()
        return len(response.data) > 0

    def get_trip_locations(self, trip_id, user_id):
        response = self.supabase.table('LOCATIONS').select('*').eq('trip_id', trip_id).execute()
        locations = response.data
        return locations
    
    def get_trip_location_by_id(self, location_id):
        response = self.supabase.table('LOCATIONS').select('*').eq('id', location_id).execute()
        return response.data[0]['name'] if response.data else None

    def get_latest_location_id(self):
        response = self.supabase.table('LOCATIONS').select('id').order('id', desc=True).limit(1).execute()
        return response.data[0]['id'] if response.data else 0
    
    def get_latest_location(self):
        latest_id = self.get_latest_location_id()
        response = self.supabase.table('LOCATIONS').select('*').eq('id', latest_id).execute()
        return response.data[0] if response.data else None
    
    def get_trip_page_activities(self, trip_id):
        response = self.supabase.table('LOCATIONS').select('*').eq('trip_id', trip_id).order('created_at', desc=True).order('date_removed',desc=True).execute()
        # print(response.data)
        new = []
        for item in response.data:
            if not item['removed']:
                item['action'] = 'suggested'
                new.append(item)
            else:
                item['action'] = 'suggested'
                decoy = item.copy()
                new.append(decoy)
                item['suggested_by'] = item['removed_by']
                item['created_at'] = item['date_removed']
                item['action'] = 'removed'
                new.append(item)
        new.extend(self.vote_table_for_logs(trip_id))  # add votes to the logs
        new.sort(key=lambda x: x['created_at'], reverse=True)
        return new

    def add_location(self, trip_id, name, category, description, start_date, end_date, start_time, end_time, user, lat, lng):
        data = {
            'trip_id': trip_id,
            'name': name,
            'description': description,
            'category': category,
            'start_date': start_date,
            'end_date': end_date,  # Assuming start_date and end_date are the same for a single day activity
            'start_time': start_time,
            'end_time': end_time,
            'suggested_by': user,
            'lat': lat,
            'lng': lng
        }

        response = self.supabase.table('LOCATIONS').insert(data).execute()
        return response.data[0]['id'] if response.data else None
    
    def remove_location(self, location_id, username):
        now_str = datetime.now(timezone('Asia/Singapore')).isoformat()
        response = self.supabase.table('LOCATIONS').update({'removed': True, 'date_removed': now_str, 'removed_by': username}).eq('id', location_id).execute()
        return response.data[0]['id'] if response.data else None
    
    def get_location_by_id(self, location_id):
        response = self.supabase.table('LOCATIONS').select('*').eq('id', location_id).execute()
        if response.data:
            return response.data[0]
        return None

### voting system not yet complete
    def get_location_votes(self, location_id):
        response = self.supabase.table('VOTES').select('*').eq('location_id', location_id).execute()
        return(len(response.data))

    def check_if_user_voted(self, location_id, user_id):
        response = self.supabase.table('VOTES').select('*').eq('location_id', location_id).eq('user_id', user_id).execute()
        return len(response.data) > 0
    
    def remove_vote_in_location(self, location_id, user_id): #for testing/admin purposes
        if not self.check_if_user_voted(location_id, user_id): return False
        else:
            response = self.supabase.table('VOTES').delete().eq('location_id', location_id).eq('user_id', user_id).execute()
        return True
    
    def vote_table_for_logs(self, trip_id):
        all_locations = self.get_trip_locations(trip_id, None)  # Ensure the trip exists
        location_id_only = [location['id'] for location in all_locations]
        response = self.supabase.table('VOTES').select('*').in_('location_id', location_id_only).execute()
        garage = response.data
        for item in garage:
            item['suggested_by'] = self.get_name_from_id(item['user_id'])
            item['trip_id'] = trip_id
            item['name'] = self.get_location_by_id(item['location_id'])['name']
            item['action'] = 'voted for'
            item['id'] = item['location_id']
            item['description'] = ''
            item['category'] = ''
            item['start_date'] = ''
            item['end_date'] = ''
            item['start_time'] = ''
            item['end_time'] = ''
            item['removed'] = False
            item['date_removed'] = item['created_at'] 
            item['removed_by'] = ''
            item['lat'] = 0.0
            item['lng'] = 0.0
        return garage

    def upvote_on_location(self, location_id, user_id):
        if self.check_if_user_voted(location_id, user_id): return False
        else:
            data = {'location_id': location_id, 'user_id': user_id}
            response = self.supabase.table('VOTES').insert(data).execute()
            # print(response.data) 
            if response.data:
                print("Vote added successfully!")
                # print(response.data)
            else:
                print("Error adding vote")
                # print(response)
        return True
        # # to do
        # pass

###############################

    def get_trip_itinerary(self, trip_id):
        response = (
            self.supabase.table('LOCATIONS')
            .select('*')
            .eq('trip_id', trip_id)
            .eq('removed', False)
            .order('start_date')
            .order('start_time')
            .execute()
        )

        # print(response.data)

        itinerary = {}
        for item in response.data:
            # print(item)
            # print("\n")
            day = item['start_date']
            if day not in itinerary:
                itinerary[day] = {'date': day, 'activities': []}
            itinerary[day]['activities'].append(item)

        return(itinerary)

### Buggy to be fixed
    def get_trip_conflicts(self, trip_id):
        response = (
            self.supabase.table('LOCATIONS')
            .select('*')
            .eq('trip_id', trip_id)
            .eq('removed', False) 
            .order('start_date')
            .order('start_time')
            .execute()
        )

        conflicts = []
        locations = response.data
        new_locations = []
        for loc in locations:
            event = Event(loc)
            new_locations.append(event)
        conflicts = detect_conflicts(new_locations)

        # locations_by_date = {}
        # for loc in locations:
        #     date = loc['start_date']
        #     if date not in locations_by_date:
        #         locations_by_date[date] = []
        #     locations_by_date[date].append(loc)

        # for date, day_locations in locations_by_date.items():
        #     day_locations.sort(key=lambda x: x['start_time'])

        #     active_events = []

        #     for current_event in day_locations:
        #         #help filter out events that have ended
        #         active_events = [event for event in active_events if event['end_time'] > current_event['start_time']]

        #         #if the previous events are still running
        #         if active_events:
        #             if current_event not in conflicts:
        #                 #add current event(new event we are processing) into conflict
        #                 conflicts.append(current_event)         
                    
        #             #add all active events to conflicts
        #             for active_event in active_events:
        #                 if active_event not in conflicts:
        #                     conflicts.append(active_event)
                
        #         active_events.append(current_event)
        for conflict in conflicts:
            loc= conflict['id']
            conflict['votes'] = self.get_location_votes(loc)
        return conflicts

        # locations = response.data
        # conflicts = []
        # temp = []
        # startT, endT = 0, 0
        # date = 0

        # #using line sweep algo for search
        # for location in locations:
        #     if not temp:
        #         temp.append(location)
        #         startT = location['start_time']
        #         endT = location['end_time']
        #         date = location['date']
        #         continue
        #     elif date != location['date']:
        #         if len(temp) > 1:
        #             conflicts.extend(temp)
        #         temp.clear()
        #         continue
        #     else:
        #         if(startT <= location['start_time'] <= endT or startT <= location['end_time'] <= endT):
        #             startT = min(startT, location['start_time'])
        #             endT = max(endT, location['end_time'])
        #             temp.append(location)

        # return conflicts

    def add_comment_to_location(self, location_id, username, comment):
        # print("adding comment to location")
        data = {
            'location_id': location_id,
            'username': username,
            'comment': comment
        }
        response = self.supabase.table('COMMENTS').insert(data).execute()
        return response.data[0]['id'] if response.data else None
    
    def get_comments_for_location(self, location_id):
        response = self.supabase.table('COMMENTS').select('*').eq('location_id', location_id).order('created_at').execute()
        comments = response.data
        return comments
    
    def edit_trip(self, new_data, trip_id):
        print(f"Editing trip {trip_id} with data: {new_data}")
        response = self.supabase.table('TRIPS').update(new_data).eq('trip_id', trip_id).execute()
        return response.data[0] if response.data else None



# for testing purposes
if __name__ == "__main__":
    db = DB()
    print(db.get_user(1))
    print(db.check_user(1))
    # use DBtesting.py to test the DB class methods
    # print(db.add_location(1, "test", "test", "Category", 1, 1, "test1", 1))
    
