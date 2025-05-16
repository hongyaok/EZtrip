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

# for testing purposes
if __name__ == "__main__":
    db = DB()
    print(db.get_user(1))
    print(db.check_user(1))
    
