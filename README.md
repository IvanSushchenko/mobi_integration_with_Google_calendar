# Mobidziennik integration with Google Calendar

### Requirement installation

Version of Python 3.8.2 was used.

`pip install -r requirements.txt`

or

`pip3 install -r requirements.txt`

### Creating Google App

1. Go to https://console.developers.google.com/apis/
2. Click "Library" in sidebar
3. Search "Google Calendar API"
4. Click "Enable"
5. Click "Credentials" in sidebar
6. Click "Create Credentials" and select "Create OAuth client ID"
7. Click "Configure Consent Screen"
8. Select "External"
9. Fill all fields:
    - Enter name
    - Click "Add scope" and select: "Google Calendar API /auth/calendar.events"
    - Click "Save"
10. Click "Credentials" in sidebar
11. Click "Create Credentials" and select "Create OAuth client ID"
12. Choose  "Desktop app"
13. Click "Create"
14. In table OAuth 2.0 Client IDs click download button
15. Place this file in project folder.
16. Copy file name and enter in "setting.json"

    example:
    
    `"google_settings": {
    "credentials_file": "google_credentials.json"
    }`

### Mobi

1. Enter your credentials from Mobidziennik in "mobi_credentials.json"
    
    example:
    
    `{
        "mobi": {
            "login": "ENTER LOGIN",
            "haslo": "ENTER PASSWORD"
        }
    }`

##### OPTIONAL

- amount of next week 
    
    1 - only current week
    
    2 - current and next week
    
    ...
    
    example:
    
    `"app_settings": {
        "week_limit": 1  
    }`

### Run script

    `python main.py`
    
or
    
    `python3 main.py`




author: Ivan Sushchenko




