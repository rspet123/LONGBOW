from pymongo import MongoClient,InsertOne, DeleteMany, ReplaceOne, UpdateOne
import configparser
config = configparser.ConfigParser()
config.read("config.ini")
PASSWORD = config.get('DATABASE', 'PASSWORD')
USERNAME = config.get('DATABASE', 'USERNAME')
# TODO

client = MongoClient("mongodb+srv://{username}:{pw}@longbow.luvkv.mongodb.net".format(pw = PASSWORD,username = USERNAME))

db = client["LONGBOW"]
Systems = db["Systems"]