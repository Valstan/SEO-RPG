from pymongo import MongoClient

from my_mongo import my_mongo

client = MongoClient(my_mongo)
mongo_base = client['postopus']
collection = mongo_base['config']
table = collection.find_one({'title': 'seo_rpg'}, {'_id': 0, 'title': 0})
