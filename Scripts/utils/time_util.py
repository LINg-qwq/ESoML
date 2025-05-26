import datetime as dt


def to_time_stamp(my_time):
    return dt.datetime.strptime(my_time, "%Y/%m/%d")


def get_time_delta(begin, end):
    return (end.date() - begin.date()).days
