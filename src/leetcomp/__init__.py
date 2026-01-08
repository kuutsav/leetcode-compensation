from enum import StrEnum

DATA_DIR = "data"
TEMP_FILE = f"{DATA_DIR}/temp.jsonl"
PARSED_TEMP_FILE = f"{DATA_DIR}/parsed_temp.jsonl"
POSTS_FILE = f"{DATA_DIR}/posts.jsonl"
PARSED_FILE = f"{DATA_DIR}/parsed_posts.jsonl"
FINAL_DATA_FILE = f"{DATA_DIR}/final_data.json"


class NormalizedEntity(StrEnum):
    COMPANY = "company-normalized"
    ROLE = "role-normalized"
    LOCATION = "location"
