import requests
import spotipy
import json
import time
import random
import base64
from PIL import Image
import io
from spotipy.oauth2 import SpotifyOAuth

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="SPOTIPY_CLIENT_ID",
                                               client_secret="SPOTIPY_CLIENT_SECRET",
                                               redirect_uri="http://localhost:8888/callback",
                                               scope="playlist-modify-public ugc-image-upload"))

# Get the user's Spotify ID
user_id = sp.current_user()["id"]
hf_token = "HF_TOKEN"

def get_prompt():
    prompt = input("Enter a prompt or press enter to use song titles: ")
    if prompt == "":
        playlist_id = get_random_playlist_id()
        prompt = get_song_names_from_playlist(playlist_id)
    return prompt


# Function to print song names from a Spotify playlist
def get_song_names_from_playlist(playlist_id):
    song_titles = []
    if playlist_id is not None:
        # Get the playlist tracks
        playlist_tracks = sp.playlist_tracks(playlist_id)

        # Collect the song names in a single string separated by commas
        for item in playlist_tracks["items"]:
            song_titles.append(item["track"]["name"])
        # Shuffle the song_titles list
        random.shuffle(song_titles)
        song_titles_string = ", ".join(song_titles)
        print(song_titles_string)
        return song_titles_string
    else:
        print("No playlists found.")



def get_random_playlist_id():
    playlists = sp.user_playlists(user_id)
    print(playlists)
    if playlists["items"]:
        random_playlist = random.choice(playlists["items"])
        #print(random_playlist["name"], "hello")  # Print the playlist name
        return random_playlist["id"]
    return None

def set_playlist_cover_image(playlist_id, image_base64):
    sp.playlist_upload_cover_image(playlist_id, image_base64)

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_base64

def query(payload, seed=None, retries=3):
    headers = {"Authorization": f"Bearer {hf_token}"}
    API_URL = "https://api-inference.huggingface.co/models/prompthero/openjourney"
    if seed is None:
        seed = random.randint(0, 10000)
    payload["seed"] = seed
    for i in range(retries):
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.content
        else:
            print(f"API call failed with status code {response.status_code}. Retrying...")
            time.sleep(1)
    print("API call failed after multiple retries. Exiting.")
    return None

    

prompt = get_prompt()
playlist_id = get_random_playlist_id()
image_bytes = query({"inputs": f"{prompt}"})
# You can access the image with PIL.Image for example


# Convert the image bytes to a PIL Image
image = Image.open(io.BytesIO(image_bytes))

# Convert the image to base64 format
image_base64 = image_to_base64(image)

# Set the cover image of the playlist
set_playlist_cover_image(playlist_id, image_base64)

# Display the image
#image.show()
