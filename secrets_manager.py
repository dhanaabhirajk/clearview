import json

# Read the contents of the JSON file
with open("secrets.json", "r") as file:
    secrets = json.load(file)


# Define variables for the secrets
MONGODB_URI = secrets["MONGODB_URI"]
NGROK_AUTH_TOKEN = secrets["NGROK_AUTH_TOKEN"]
SECRET_KEY = secrets["SECRET_KEY"]
DB_NAME = secrets["DB_NAME"]
