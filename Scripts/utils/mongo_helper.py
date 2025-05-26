import pymongo
import urllib.parse
import pandas as pd

username = urllib.parse.quote_plus('Admin')
password = urllib.parse.quote_plus('njuse@104')


class MongoHelper:
    def __init__(self):
        self.client = pymongo.MongoClient('mongodb://localhost:27017')
        self.db = self.client["memleak"]

    def get_all(self):
        return self.db["data"].find()

    def select_by_tag(self, tag):
        data_collection = self.db["data"]
        res = data_collection.find(
            {'tag': tag}
        )
        return pd.DataFrame(list(res))

    def get_next_id(self, sequence_name):
        counter_collection = self.db["counters"]
        ret = counter_collection.find_one_and_update(
            {'_id': sequence_name},
            {'$inc': {"sequence_value": 1}}
        )
        return ret['sequence_value']