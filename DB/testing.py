from supabase import create_client
from config import supabase_url, supabase_key, special_key

#file to test the supabase connection, just change if needed
if __name__ == "__main__":
    # get keys from config.py
    url = supabase_url
    key = supabase_key
    key_change = special_key

    # Initialize the Supabase client
    supabase = create_client(url, key_change)

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

    response = supabase.table('USERS').select('*').execute() # get data from USERS table

    data = response.data # view table
    print(data)

    print(f"Response status: {response.status_code if hasattr(response, 'status_code') else 'No status code'}")
    print(f"Response error: {response.error if hasattr(response, 'error') else 'No error'}")


