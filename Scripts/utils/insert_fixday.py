from datetime import datetime
from pymongo import MongoClient, UpdateOne
from tqdm import tqdm

client = MongoClient('mongodb://localhost:27017/')
db = client.memleak
collection = db.data

DATE_FORMAT = "%Y/%m/%d"


def calculate_fix_days():
    cursor = collection.find(
        {"time": {"$exists": True}, "fixtime": {"$exists": True}},
        projection=["_id", "time", "fixtime"]
    ).batch_size(100)

    bulk_operations = []
    total_docs = collection.count_documents({})

    with tqdm(total=total_docs, desc="Processing bugs") as pbar:
        for doc in cursor:
            try:
                report_date = datetime.strptime(doc["time"], DATE_FORMAT)
                fix_date = datetime.strptime(doc["fixtime"], DATE_FORMAT)

                delta = fix_date - report_date
                day_of_fix = delta.days

                bulk_operations.append(
                    UpdateOne(
                        {"_id": doc["_id"]},
                        {"$set": {"day_of_fix": day_of_fix}}
                    )
                )

                if len(bulk_operations) % 100 == 0:
                    collection.bulk_write(bulk_operations)
                    bulk_operations = []
                    pbar.update(100)

            except Exception as e:
                print(f"Error processing doc {doc['_id']}: {str(e)}")

        if bulk_operations:
            collection.bulk_write(bulk_operations)
            pbar.update(len(bulk_operations))


if __name__ == "__main__":
    calculate_fix_days()
    print("Day_of_fix update finish.")