Starting:
```
pip install -r requirements.txt
```
```
python app.py
```

File structure idea:
```
eztrip/
│
├── app.py                     # Main Flask application file
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
│
├── static/                    # Static files
│   ├── css/
│   │   └── styles.css         # Main stylesheet (extracted from HTML)
│   ├── js/
│   │   └── main.js            # Main JavaScript file
│   └── img/                   # Image assets folder
│
├── templates/                 # HTML templates
│   ├── index.html             # Home page (updated to reference CSS
|
├── functions/                 # handle our functions here
|
├── auth/                      # handle our authentication here
|
├── DB/                        # handle our DB related functions here
```
