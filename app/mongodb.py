from pymongo import MongoClient


client = MongoClient() #to connect to database you need to run MongoDB before
database = client.snowboards_photos_database
collection = database.photos_collection
