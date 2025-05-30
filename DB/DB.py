from supabase import create_client
from DB.config import supabase_url, supabase_key, special_key
from werkzeug.utils import secure_filename
import uuid
import os

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
    
    def add_trip(self, google_id, trip_name, dest, theme, start_date, end_date, desc, privacy, image_path=None):
        data = {
            "trip_name": trip_name,
            "dest": dest,
            "theme": theme,
            "start_date": start_date,
            "end_date": end_date,
            "desc": desc,
            "privacy": privacy,
            "trip_image": image_path 
        }
        
        response = self.supabase.table('TRIPS').insert(data).execute()
        
        if hasattr(response, 'data') and response.data:
            print("Trip added successfully!")
            print(response.data)
        else:
            print("Error adding trip")
            print(response)
        
        id = self.get_latest_id_from_trips()
        if id:
            self.add_user_to_trip(google_id, id)
        return id

    
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
    
    def upload_image_to_storage(self, file, bucket_name="trip-images"):
        try:
            # Secure the filename and create unique name
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = f"images/{unique_filename}"
            
            # Upload to Supabase Storage
            response = self.supabase.storage.from_(bucket_name).upload(
                path=file_path,
                file=file.read(),
                file_options={
                    "cache-control": "3600",
                    "upsert": "false",
                    "content-type": file.content_type
                }
            )
            
            if response:
                return file_path
            return None
            
        except Exception as e:
            print(f"Error uploading image: {str(e)}")
            return None

    def get_image_url(self, file_path, bucket_name="trip-images"):
        """Get public URL for an image from Supabase Storage"""
        try:
            response = self.supabase.storage.from_(bucket_name).get_public_url(file_path)
            return response['publicUrl'] if response else None
        except Exception as e:
            print(f"Error getting image URL: {str(e)}")
            return None

    def update_trip_image(self, trip_id, image_path):
        """Update trip record with image path"""
        try:
            response = self.supabase.table('TRIPS').update({'trip_image': image_path}).eq('trip_id', trip_id).execute()
            return response.data if hasattr(response, 'data') else None
        except Exception as e:
            print(f"Error updating trip image: {str(e)}")
            return None



# for testing purposes
if __name__ == "__main__":
    db = DB()
    print(db.get_user(1))
    print(db.check_user(1))
    
