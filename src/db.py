import os
from dotenv import load_dotenv
from pymongo import MongoClient

def connect_to_mongodb():
    load_dotenv()
    # Create the MongoDB connection string with the provided credentials
    MONGODB_URI = os.environ['MONGODB_URI']

    # Create a MongoClient instance using the connection string
    client = MongoClient(MONGODB_URI)

    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    
        
    return client['clearview']


