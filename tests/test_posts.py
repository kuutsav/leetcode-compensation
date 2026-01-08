import json

from leetcomp import POSTS_FILE, PARSED_FILE


def test_posts_record_ordering():
    last_rec_id = None
    with open(POSTS_FILE, "r") as f:
        for line in f:
            rec_id = json.loads(line)["id"]
            if last_rec_id:
                assert last_rec_id > rec_id
            last_rec_id = rec_id


def test_parsed_posts_record_ordering():
    last_rec_id = None
    with open(PARSED_FILE, "r") as f:
        for line in f:
            rec_id = json.loads(line)["id"]
            if last_rec_id:
                assert last_rec_id >= rec_id
            last_rec_id = rec_id
