from pymongo import MongoClient,InsertOne, DeleteMany, ReplaceOne, UpdateOne
import configparser
config = configparser.ConfigParser()
config.read("config.ini")
PASSWORD = config.get('DATABASE', 'PASSWORD')
USERNAME = config.get('DATABASE', 'USERNAME')
# TODO

drop_tables = False

client = MongoClient("mongodb+srv://{username}:{pw}@longbow.luvkv.mongodb.net".format(pw = PASSWORD,username = USERNAME))

db = client["LONGBOW"]
Systems = db["Systems"]
Users = db["Users"]
SystemReport = db["SystemReport"]
Characters = db["Characters"]

if drop_tables:
    Characters.delete_many({})
    SystemReport.delete_many({})