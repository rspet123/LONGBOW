from pymongo import MongoClient
import configparser
config = configparser.ConfigParser()
config.read("config.ini")
PASSWORD = config.get('DATABASE', 'PASSWORD')
# TODO

client = MongoClient("mongodb+srv://KATTE:{pw}@longbow.luvkv.mongodb.net/test".format(pw = PASSWORD))

print(client.close())