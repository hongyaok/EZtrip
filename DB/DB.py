from supabase import create_client
from DB.config import supabase_url, supabase_key, special_key

class DB:
    def __init__(self):
        self.supabase = create_client(supabase_url, special_key) # initialise connection to supabase

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
        data = {
            "google_id": id,
            "username": name,
            "email": email,
            "user_img": picture,
            "role": isAdmin
        }
        response = self.supabase.table('USERS').insert(data).execute()
        return response.data if hasattr(response, 'data') else None
    
    def get_latest_id_from_trips(self):
        response = self.supabase.table('TRIPS').select('trip_id').order('trip_id', desc=True).limit(1).execute()
        if response.data:
            return response.data[0]['trip_id']
        return None
    
    def add_user_to_trip(self, google_id, trip_id): # additional: after user accepts invite, add them to the trip
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
        response=self.supabase.table('TRIPS').insert(data).execute()
        if hasattr(response, 'data') and response.data:
            print("Trip added successfully!")
            print(response.data)
        else:
            print("Error adding trip")
            print(response)
        id = self.get_latest_id_from_trips()
        if id:
            self.add_user_to_trip(google_id, id)
        return id # to email the invite link to the user
    
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


# for testing purposes
if __name__ == "__main__":
    db = DB()
    print(db.get_user(1))
    print(db.check_user(1))
    
