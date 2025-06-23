from supabase import create_client
from DB.DB import DB

#file to test the supabase connection, just change if needed
if __name__ == "__main__":
    # get keys from config.py
    DB = DB()  # create an instance of the DB class

    # # test for adding new user
    # new_user = {
    #     "username": "new_user",
    #     "email": "user@example.com",
    #     "role": True,  # Boolean value for role column
    #     "created_at": "2023-10-01T12:00:00Z"
    #     # additional field for user_img
    # }
    # response = supabase.table('USERS').insert(new_user).execute()
    # if hasattr(response, 'data') and response.data:
    #     print("User added successfully!")
    #     print(response.data)
    # else:
    #     print("Error adding user")
    #     print(response)


    # data = response.data # view table
    # print(data)

    # Test get_latest_location
    # latest_location = DB.get_latest_location()
    # print("Latest location:", latest_location)

    itinerary = DB.get_trip_conflicts(2) 
    # print(itinerary)

    # DB.get_trip_page_activities(2)