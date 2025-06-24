from supabase import create_client
from config import supabase_url, supabase_key, special_key
from datetime import datetime


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
    
    def add_user_to_trip(self, google_id, trip_id): # after user accepts invite, add them to the trip
        data = {
            "google_id": google_id,
            "trip_id": trip_id
        }
        response=self.supabase.table('USERTRIP').insert(data).execute()
        return response.data if hasattr(response, 'data') else None
    
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
            .select('trip_id')
            .eq('google_id', google_id)
            .execute()
        )
        #print(f"User trips: {user_trips.data}") #debug
        
        all_trips = []
        if user_trips.data:
            trip_ids = [trip['trip_id'] for trip in user_trips.data]
            for trip_id in trip_ids:
                all_trips.extend((
                    self.supabase.from_('TRIPS')
                    .select('*')
                    .eq('trip_id', trip_id)
                    .execute()
                ).data)

            return all_trips
        
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
    
    def get_latest_location_id(self):
        response = self.supabase.table('LOCATIONS').select('id').order('id', desc=True).limit(1).execute()
        return response.data[0]['id'] if response.data else 0
    
    def get_latest_location(self):
        latest_id = self.get_latest_location_id()
        response = self.supabase.table('LOCATIONS').select('*').eq('id', latest_id).execute()
        return response.data[0] if response.data else None
    
    def get_trip_page_activities(self, trip_id):
        response = self.supabase.table('LOCATIONS').select('*').eq('trip_id', trip_id).order('created_at', desc=True).order('date_removed',desc=True).execute()
        print(response.data)
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
        new.sort(key=lambda x: x['created_at'], reverse=True)
        return new

    def add_location(self, trip_id, name, category, description, date, start_time, end_time, user):
        data = {
            'trip_id': trip_id,
            'name': name,
            'description': description,
            'category': category,
            'date': date,
            'start_time': start_time,
            'end_time': end_time,
            'suggested_by': user  
        }

        response = self.supabase.table('LOCATIONS').insert(data).execute()
        return response.data[0]['id'] if response.data else None
    
    def remove_location(self, location_id, username):
        now_str = datetime.now().isoformat()
        response = self.supabase.table('LOCATIONS').update({'removed': True, 'date_removed': now_str, 'removed_by': username}).eq('id', location_id).execute()
        return response.data[0]['id'] if response.data else None

    def upvote_on_location(self, location_id, user_id):
        # to do
        pass

    def get_trip_itinerary(self, trip_id):
        response = (
            self.supabase.table('LOCATIONS')
            .select('*')
            .eq('trip_id', trip_id)
            .eq('removed', False)
            .order('date')
            .order('start_time')
            .execute()
        )

        print(response.data)

        itinerary = {}
        for item in response.data:
            # print(item)
            # print("\n")
            day = item['date']
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
            .order('date')
            .order('start_time')
            .execute()
        )

        conflicts = []
        locations = response.data

        locations_by_date = {}
        for loc in locations:
            date = loc['date']
            if date not in locations_by_date:
                locations_by_date[date] = []
            locations_by_date[date].append(loc)

        for date, day_locations in locations_by_date.items():
            day_locations.sort(key=lambda x: x['start_time'])

            active_events = []

            for current_event in day_locations:
                #help filter out events that have ended
                active_events = [event for event in active_events if event['end_time'] > current_event['start_time']]

                #if the previous events are still running
                if active_events:
                    if current_event not in conflicts:
                        #add current event(new event we are processing) into conflict
                        conflicts.append(current_event)         
                    
                    #add all active events to conflicts
                    for active_event in active_events:
                        if active_event not in conflicts:
                            conflicts.append(active_event)
                
                active_events.append(current_event)
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
    



# for testing purposes
if __name__ == "__main__":
    db = DB()
    print(db.get_user(1))
    print(db.check_user(1))
    # print(db.add_location(1, "test", "test", "Category", 1, 1, "test1", 1))
    
