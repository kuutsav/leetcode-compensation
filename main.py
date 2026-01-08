import json

ids = set()

with open("data/parsed_posts.jsonl", "r") as f:
    for line in f:
        ids.add(json.loads(line)["id"])

print(len(ids))
