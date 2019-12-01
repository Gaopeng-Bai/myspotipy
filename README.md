# My Spotify Client wrote by python

## 1. Make sure you have Python or Conda installed
## 2. Install package described in requirement file.
## 3. This application require spotify premium account.
## 4. Set environment variables:

SPOTIPY_CLIENT_ID= xxx
SPOTIPY_CLIENT_SECRET= xxx
SPOTIPY_REDIRECT_URI='your-app-redirect-url'

Register Spotify dashboard to get your credentials: <https://developer.spotify.com/dashboard/login>

Details pls check the documents in <https://spotipy.readthedocs.io/en/latest/>

## 5. Make sure the graph data that generate by Model already exited in ../data_resources/save_data

## 6. Run this application with your Spotify ID.

Login your Spotify client -> Click on your profile photo -> The menu button under your photo. 

When you're on your account and find your account sharing link, the characters after /user will be the user id.

Run program: python xxx.py user on the console.  Or set your IDE.

## 7. Authorization. 

The program will jump to the browser with your redirect URL (whatever it is). Copy the URL represent in browser to command line, then press Enter to go.