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

1. Obtain and set up configurations for both `DB` and `auth`.
2. For `DB` folder, ensure the following configurations are provided in a config.py file from supabase with the same Database schema implemented within a project:
    - `supabase_url`
    - `supabase_key`
    - `special_key`
    - Database tables as specified below.
3. For `auth` folder, ensure the following configurations are provided in a config.py file and obtained from google services:
    - `ClientID`
    - `ClientSecret`
4. For `func` folder, ensure the following configurations are provided in a emailconfig.py file:
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

## Database class

Our database is initialised as a `DB` class stored within the DB.py file in the DB folder. The class currently supports the following methods:

```
DB.get_user(google_id) 
    -> returns row from USERS table with matching google_id

DB.check_user(google_id) 
    -> returns True if the google_id exists in USERS

DB.add_user(google_id,name,email,picture) 
    -> adds the user into USERS

DB.get_latest_id_from_trips() 
    -> returns the latest trip_id from TRIPS

DB.add_user_to_trip(google_id, trip_id) 
    -> adds google_id and trip_id into USERTRIP

DB.add_trip(google_id, trip_name, dest, theme, start_date, end_date, desc, privacy)
    -> adds the trip into TRIPS table

DB.get_all_trips_for_user(google_id)
    -> joins the TRIPS and USERTRIP table by trip_id and finds all rows that has google_id

```

## Side Note

Ensure you are using Python 3.12 or above to avoid dependency issues.

