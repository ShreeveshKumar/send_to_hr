import os
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv

load_dotenv()
from pymongo.errors import ConnectionFailure, ConfigurationError




def connect_mongo():
    uri = os.getenv("DATABASE_URL")
    db_name = "telebot" 
    if not uri:
        db_user = os.getenv("DATABASE_USER")
        db_password = os.getenv("DATABASE_PASSWORD")
        if db_user and db_password:
            uri = f"mongodb+srv://{db_user}:{db_password}@check1.gzludkc.mongodb.net/?appName=check1"
    
    if not uri:
        print("Warning: DATABASE_URL (or DATABASE_USER/PASSWORD) is not set. Database connections disabled.")
        return None
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000, tlsCAFile=certifi.where(), tlsAllowInvalidCertificates=True)
        client.admin.command("ping")
        return client[db_name]
    except (ConnectionFailure, ConfigurationError) as e:
        print(f"Warning: Database connection failed: {e}")
        return None

db = connect_mongo()

def get_collection(collection_name):
    if db is not None:
        return db[collection_name]
    return None