import json

# Read the contents of the JSON file
with open("secrets.json", "r") as file:
    secrets = json.load(file)


# Define other configuration parameters
STATUS_ENV = secrets["STATUS_ENV"]
MAX_LENGTH = secrets["MAX_LENGTH"]
TOP_P = secrets["TOP_P"]
TEMPERATURE = secrets["TEMPERATURE"]
PORT = secrets["PORT"]