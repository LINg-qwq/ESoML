import pymongo
import csv
from collections import defaultdict
from urllib.parse import urlparse

def parse_github_url(url):
    try:
        path = urlparse(url).path
        parts = path.strip('/').split('/')
        if len(parts) >= 4:
            owner = parts[0]
            repo = parts[1]
            pull_id = parts[3]
            return owner, repo, pull_id
    except Exception as e:
        print(f"Error in parsing {url} with exception: {str(e)}")
    return None, None, None

def analyze_cppcheck_results():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['memleak']
    collection = db['data']
    tag_scores = defaultdict(lambda: defaultdict(int))
    
    try:
        mongo_records = defaultdict(set)
        for doc in collection.find({}):
            url = doc.get('url', '')
            tag = doc.get('tag', 'N/A')
            owner, repo, pull_id = parse_github_url(url)
            if owner and repo and pull_id:
                key = f"{owner}-{repo}-{pull_id}"
                mongo_records[key].add(tag)

        with open('analyze/cppcheck_results.csv', 'r') as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                if len(row) >= 2:
                    key = row[0]
                    score = int(row[1])
                    tags = mongo_records.get(key, {'N/A'})
                    for tag in tags:
                        tag_scores[tag][score] += 1
        
        print("\nCppcheck Result:")
        print("-" * 50)
        print(f"{'Tag':<25} {'Level':<10} {'Count':<10}")
        print("-" * 50)

        for tag in sorted(tag_scores.keys()):
            for score in sorted(tag_scores[tag].keys()):
                count = tag_scores[tag][score]
                print(f"{tag:<25} {score:<10} {count:<10}")

        print("\nOverall of Tag")
        print("-" * 30)
        for tag in sorted(tag_scores.keys()):
            total = sum(tag_scores[tag].values())
            print(f"{tag:<25} {total:<10}")
            
    except Exception as e:
        print(f"Exception: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    analyze_cppcheck_results()
