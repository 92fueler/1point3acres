from pymongo import MongoClient

from config import MONGO_URI, DATABASE_NAME, COLLECTION_NAME


def get_db():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    return db


def get_collection():
    db = get_db()
    return db[COLLECTION_NAME]
