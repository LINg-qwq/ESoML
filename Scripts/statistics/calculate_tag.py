import pymongo
from collections import Counter

def calculate_tag_statistics(collection):
    tags = [doc.get('tag', 'N/A') for doc in collection.find({})]

    tag_counter = Counter(tags)

    print("\nTag Result:")
    print("-" * 30)
    print(f"{'Tag':<25} {'Count':<5}")
    print("-" * 30)

    for tag, count in sorted(tag_counter.items(), key=lambda x: x[1], reverse=True):
        print(f"{tag:<25} {count:<5}")

    print("-" * 30)
    print(f"Total: {sum(tag_counter.values())}")

def main():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['memleak']
    collection = db['data']

    try:
        print("Begin analyze tag...")
        calculate_tag_statistics(collection)
    except Exception as e:
        print(f"Exception: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    main() 