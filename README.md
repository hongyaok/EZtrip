## Set Up Dependencies

To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Running the Web App

To start the web app, use the command:

```bash
python app.py
```

## File Structure

```
auth       --> Authentication required configs and backend
DB         --> Supabase required configs and functions
static     --> Styles and images for HTML
templates  --> HTML templates
app.py     --> Main Flask application to handle routing
```

## Setup Instructions

If setting up the project, follow these steps:

1. Obtain and set up configurations for both `DB` and `auth`.
2. For `DB`, ensure the following configurations are provided:
    - `supabase_url`
    - `supabase_key`
    - `special_key`
    - Database tables as specified below.
3. For `auth`, ensure the following configurations are provided:
    - `ClientID`
    - `ClientSecret`

## Database Schema (Using Supabase)

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

## Side Note

Ensure you are using Python 3.12 or above to avoid dependency issues.