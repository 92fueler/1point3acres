from pymongo import MongoClient

from config import MONGO_URI, DATABASE_NAME, COLLECTION_NAME


def get_collection():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    return db[COLLECTION_NAME]
