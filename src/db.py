import os
from pymongo import MongoClient
from secrets_manager import MONGODB_URI,DB_NAME

def connect_to_mongodb():
    # Create the MongoDB connection string with the provided credentials

    # Create a MongoClient instance using the connection string
    client = MongoClient(MONGODB_URI)

    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    
        
    return client[DB_NAME]


