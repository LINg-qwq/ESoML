from utils.mongo_helper import MongoHelper
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd


def to_time_stamp(my_time):
    return dt.datetime.strptime(my_time, "%Y/%m/%d")


def get_time_delta(begin, end):
    return (end.date() - begin.date()).days


if __name__ == '__main__':
    # print("Analyzing time statistics...")
    mongo = MongoHelper()
    data = mongo.get_all()
    delta_list = []
    for i in data:
        delta = get_time_delta(
            to_time_stamp(i.get("time")),
            to_time_stamp(i.get("fixtime"))
        )
        delta_list.append(delta)
    se = pd.Series(delta_list)
    divided = pd.cut(se, [-1, 0, 3, 7, 14, 30, 90, se.max()])
    print(divided.value_counts().sort_index())
