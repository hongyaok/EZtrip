# Why EZtrip?

We developed EZtrip because we want a hassle-free trip planning. From our personal experiences, trip planning is always disastrous, with many conflicting opinions and different goals. With EZtrip, we aim to provide an easy to use platform, that integrates Google api (through authentication and map services), a voting system (work in progress), email invites and more!

# Preview

![Index](https://i.ibb.co/pjL0ch58/Screenshot-2025-05-27-212934.png)

![auth](https://i.ibb.co/rfyk3VKv/Screenshot-2025-05-27-214531.png")

![dashboard](https://i.ibb.co/9ktHXJxF/Screenshot-2025-05-27-214707.png)

![new-trip](https://i.ibb.co/C5mhTNk0/Screenshot-2025-05-27-214832.png)

Try it now here: [EZtrip](https://eztrip-vbi5.onrender.com/)


# Setup Instructions

If you are setting up the project locally, follow these steps:

1. Obtain and set up configurations for both `DB` and `auth`, placing all required keys into the a config.py file as shown in File Structure below.
2. For `DB` folder, ensure the following configurations from supabase with the same Database schema implemented within a project:
    - `supabase_url`
    - `supabase_key`
    - `special_key`
    - Database tables as specified below.
3. For `auth` folder, ensure the following configurations obtained from google services:
    - `ClientID`
    - `ClientSecret`
4. For `func` folder, ensure the following configurations are provided:
    - `email` (refers to the sender email)
    - `password` (refers to the 16 digit password attainable from a google account)


Otherwise, you may use our deployed site over at [EZtrip](https://eztrip-vbi5.onrender.com/) (subject to free usage limits). You may have to wait for a couple of minutes while the the site starts up as well.

## Set Up Dependencies

To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Running the Web App

To start the web app, use the command from the eztrip directory:

```bash
python app.py
```

# File Structure

```
auth       --> Authentication required configs and backend
DB         --> Supabase required configs and functions
static     --> Styles and images for HTML
templates  --> HTML templates
app.py     --> Main Flask application to handle routing
func       --> Functions for email invitations
config.py  --> Stores all secret keys
```

# Database 

The database is being implemented using Supabase. Find out more about Supabase here: [Supabase Python Documentation](https://supabase.com/docs/reference/python/introduction)

## Schema

`USERS` table schema
```
USERS:
    - id: int8, primary key, auto-increment
    - google_id: numeric, unique
    - created_at: timestamp, default value: now()
    - username: text
    - role: bool
    - email: text, unique
    - user_img: text
```

`USERTRIP` table schema
```
USERTRIP:
    - id: int8, primary key, auto-increment
    - google_id: numeric, unique
    - trip_id: int8
```

`TRIPS` table schema
```
TRIPS:
    - trip_id: int8, primary key, auto-increment
    - trip_name: text
    - dest: text
    - theme: text
    - start_date: datetime
    - end_date: datetime
    - desc: text
    - privacy: varchar
```

`LOCATIONS` table schema
```
LOCATIONS:
    - id: int4, primary key, auto-increment
    - trip_id: int4
    - name: text
    - description: text
    - category: text
    - end_time: time
    - start_time: time
    - created_at: timestamp
    - date: date
    - suggested_by: text
    - removed: boolean, default false
    - date_removed: timestamp
    - removed_by: text
    - lat: numeric
    - lng: numeric
```

`VOTES` table schema
```
VOTES:
    - id: int8, primary key, auto-increment
    - created_at: timestamp
    - location_id: int8
    - user_id: numeric
```


## Database class

Our database is initialised as a `DB` class stored within the DB.py file in the DB folder. The class currently supports the following methods:

`User Management Methods`
```
DB.get_user(google_id) 
    -> returns row from USERS table with matching google_id

DB.check_user(google_id) 
    -> returns True if the google_id exists in USERS

DB.get_name_from_id(google_id)
    -> returns username from USERS table with matching google_id

DB.get_email_from_id(google_id)
    -> returns email from USERS table with matching google_id

DB.add_user(google_id, name, email, picture, isAdmin=False) 
    -> adds the user into USERS table with optional admin role
```

`Trip Management Methods`
```
DB.get_latest_id_from_trips() 
    -> returns the latest trip_id from TRIPS table

DB.add_user_to_trip(google_id, trip_id) 
    -> adds google_id and trip_id into USERTRIP table

DB.get_list_of_users_in_trip(trip_id, ver=0)
    -> returns list of users in trip (ver=0 for names, ver=1 for emails)

DB.add_trip(google_id, trip_name, dest, theme, start_date, end_date, desc, privacy)
    -> adds the trip into TRIPS table and automatically adds creator to trip

DB.get_all_trips_for_user(google_id)
    -> joins the TRIPS and USERTRIP table by trip_id and finds all rows that has google_id

DB.get_trip_by_id(trip_id)
    -> returns trip details from TRIPS table with matching trip_id

DB.user_has_access_to_trip(user_id, trip_id)
    -> returns True if user has access to the specified trip
```

`Location Management Methods`
```
DB.get_trip_locations(trip_id, user_id)
    -> returns all locations for a specific trip

DB.get_trip_location_by_id(location_id)
    -> returns location name by location ID

DB.get_latest_location_id()
    -> returns the highest location ID from LOCATIONS table

DB.get_latest_location()
    -> returns the most recently added location

DB.add_location(trip_id, name, category, description, date, start_time, end_time, user, lat, lng)
    -> adds a new location/activity to LOCATIONS table

DB.remove_location(location_id, username)
    -> marks location as removed with timestamp and removing user

DB.get_location_by_id(location_id)
    -> returns complete location details by ID
```

`Activity Logs`
```
DB.get_trip_page_activities(trip_id)
    -> returns activity log including suggestions, removals, and votes according to latest (in desc order)

DB.vote_table_for_logs(trip_id)
    -> returns voting activities formatted for activity logs
```

`Voting management`
```
DB.get_location_votes(location_id)
    -> returns count of votes for a specific location

DB.check_if_user_voted(location_id, user_id)
    -> returns True if user has already voted for the location

DB.upvote_on_location(location_id, user_id)
    -> adds a vote for the location (prevents duplicate voting)

DB.remove_vote_in_location(location_id, user_id)
    -> removes user's vote from location (for testing/admin purposes)
```

`Itinerary and conflict management`
```
DB.get_trip_itinerary(trip_id)
    -> returns organized itinerary grouped by date with activities sorted by time

DB.get_trip_conflicts(trip_id)
    -> returns list of conflicting activities (overlapping times on same date)
    -> includes vote counts for each conflicting location using DB.get_location_votes
```

## Side Note

Ensure you are using Python 3.12 or above to avoid dependency issues.

