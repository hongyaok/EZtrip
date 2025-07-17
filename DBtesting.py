from supabase import create_client
from DB.DB import DB
from datetime import datetime
from zoneinfo import ZoneInfo

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

    # itinerary = DB.get_trip_conflicts(2) 
    # print(itinerary)


    # # test for voting
    # print("\n----Running voting tests----")
    # DB.remove_vote_in_location(0,0)
    # print(DB.get_location_votes(0)) #test location
    # print(DB.check_if_user_voted(0,1)) #true
    # print(DB.check_if_user_voted(0,0)) #false
    # print(DB.upvote_on_location(0,0)) #true
    # print(DB.check_if_user_voted(0,0)) #true
    # print("----voting tests done----\n")

    # print(DB.get_trip_page_activities(2))
    # print("\n")
    # print(DB.vote_table_for_logs(2) )

    # print(DB.get_trip_conflicts(3))
    # print(DB.get_list_of_users_in_trip(3, ver=1))
    # print(datetime.now(tz=ZoneInfo('Asia/Singapore')).isoformat())
    print(DB.get_trip_locations(2, 1))