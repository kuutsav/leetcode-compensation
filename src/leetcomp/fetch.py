import asyncio
import datetime
import json
import os
import shutil

import httpx

from leetcomp import DATA_DIR, POSTS_FILE, TEMP_FILE


LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql/"
SKIP, FIRST, SLEEP_PER_BATCH = 0, 50, 3
COMPENSATION_POSTS_QUERY = {
    "query": "query discussPostItems($orderBy: ArticleOrderByEnum, $keywords: [String]!, $tagSlugs: [String!], $skip: Int, $first: Int) {\n  ugcArticleDiscussionArticles(\n    orderBy: $orderBy\n    keywords: $keywords\n    tagSlugs: $tagSlugs\n    skip: $skip\n    first: $first\n  ) {\n    totalNum\n    pageInfo {\n      hasNextPage\n    }\n    edges {\n      node {\n        uuid\n        title\n        slug\n        summary\n        author {\n          realName\n          userAvatar\n          userSlug\n          userName\n          nameColor\n          certificationLevel\n          activeBadge {\n            icon\n            displayName\n          }\n        }\n        isOwner\n        isAnonymous\n        isSerialized\n        scoreInfo {\n          scoreCoefficient\n        }\n        articleType\n        thumbnail\n        summary\n        createdAt\n        updatedAt\n        status\n        isLeetcode\n        canSee\n        canEdit\n        isMyFavorite\n        myReactionType\n        topicId\n        hitCount\n        reactions {\n          count\n          reactionType\n        }\n        tags {\n          name\n          slug\n          tagType\n        }\n        topic {\n          id\n          topLevelCommentCount\n        }\n      }\n    }\n  }\n}",
    "variables": {
        "orderBy": "MOST_RECENT",
        "keywords": [""],
        "tagSlugs": ["compensation"],
        "skip": SKIP,
        "first": FIRST,
    },
    "operationName": "discussPostItems",
}
POST_CONTENT_QUERY = {
    "query": "query discussPostDetail($topicId: ID!) {\n  ugcArticleDiscussionArticle(topicId: $topicId) {\n    uuid\n    title\n    slug\n    summary\n    content\n    isSlate\n    author {\n      realName\n      userAvatar\n      userSlug\n      userName\n      nameColor\n      certificationLevel\n      activeBadge {\n        icon\n        displayName\n      }\n    }\n    createdAt\n    updatedAt\n    topicId\n    hitCount\n  }\n}",
    "variables": {"topicId": ""},
    "operationName": "discussPostDetail",
}


def fetch_recent_posts(skip: int = SKIP, first: int = FIRST) -> list[dict]:
    query = {
        **COMPENSATION_POSTS_QUERY,
        "variables": {
            **COMPENSATION_POSTS_QUERY["variables"],
            "skip": skip,
            "first": first,
        },
    }

    with httpx.Client(timeout=10.0) as client:
        resp = client.post(LEETCODE_GRAPHQL_URL, json=query)
        resp.raise_for_status()
        data = resp.json()

    nodes = [
        edge["node"] for edge in data["data"]["ugcArticleDiscussionArticles"]["edges"]
    ]
    return nodes


def filter_posts(posts: list[dict], till_id: int | None, till_timestamp: str | None) -> tuple[list[dict], bool]:
    def get_votes_count(reactions: list[dict], reaction_type):
        return next(
            (
                reaction["count"]
                for reaction in reactions
                if reaction["reactionType"] == reaction_type
            ),
            0,
        )

    filtered_posts, found_till_id = [], False
    for post in posts:
        # Stop if we found the exact post ID
        if till_id and post["topic"]["id"] == till_id:
            found_till_id = True
            break

        # Stop if we passed the timestamp (posts are ordered by most recent first)
        # This is a fallback in case the till_id post was deleted
        if till_timestamp and post["createdAt"] < till_timestamp:
            found_till_id = True
            break

        filtered_posts.append(
            {
                "id": post["topic"]["id"],
                "title": post["title"],
                "created_at": post["createdAt"],
                "updated_at": post["updatedAt"],
                "hits": post["hitCount"],
                "comment_count": post["topic"]["topLevelCommentCount"],
                "upvotes": get_votes_count(post.get("reactions", []), "UPVOTE"),
                "downvotes": get_votes_count(post.get("reactions", []), "THUMBS_DOWN"),
            }
        )

    return filtered_posts, found_till_id


async def enrich_posts(posts: list[dict]) -> None:
    async def fetch_content(post: dict):
        query = {**POST_CONTENT_QUERY, "variables": {"topicId": post["id"]}}
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(LEETCODE_GRAPHQL_URL, json=query)
            resp.raise_for_status()
            data = resp.json()
            post["content"] = data["data"]["ugcArticleDiscussionArticle"]["content"]

    await asyncio.gather(*[fetch_content(post) for post in posts])


def update_status(posts: list[dict]) -> str | None:
    if not posts:
        return None
    first_timestamp, last_timestamp = posts[0]["created_at"], posts[-1]["created_at"]
    start_dt = datetime.datetime.fromisoformat(last_timestamp)
    end_dt = datetime.datetime.fromisoformat(first_timestamp)
    start_str = f"{start_dt.strftime('%d/%m/%Y, %H:%M:%S')}"
    end_str = f"{end_dt.strftime('%d/%m/%Y, %H:%M:%S')}"
    return f"{start_str} -> {end_str} ({len(posts)})"


def save_posts(posts: list[dict], file_path: str) -> None:
    with open(file_path, "a") as f:
        for post in posts:
            f.write(json.dumps(post) + "\n")


def prepend_to_posts(temp_file: str, posts_file: str) -> None:
    if not os.path.exists(temp_file):
        return
    if not os.path.exists(posts_file):
        shutil.move(temp_file, posts_file)
        return

    with open(temp_file, "r") as temp_f:
        new_content = temp_f.read()
    with open(posts_file, "r") as posts_f:
        old_content = posts_f.read()
    with open(posts_file, "w") as posts_f:
        posts_f.write(new_content)
        posts_f.write(old_content)


async def fetch_posts_in_bulk(
    n: int = 3000, till_id: int | None = None, till_timestamp: str | None = None, sleep_seconds: float = SLEEP_PER_BATCH,
):
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
    if os.path.exists(TEMP_FILE):
        os.remove(TEMP_FILE)

    posts_not_found_counter = 0

    for skip in range(0, n, FIRST):
        posts = fetch_recent_posts(skip=skip)
        if not posts:
            posts_not_found_counter += 1
            if posts_not_found_counter > 1:
                print("Exiting; likely exhaused...")
                break
        posts, found_till_id = filter_posts(posts, till_id, till_timestamp)
        await enrich_posts(posts)
        save_posts(posts, file_path=TEMP_FILE)

        status = update_status(posts)
        if status:
            print(status)

        if found_till_id:
            break

        await asyncio.sleep(sleep_seconds)

    prepend_to_posts(TEMP_FILE, POSTS_FILE)
