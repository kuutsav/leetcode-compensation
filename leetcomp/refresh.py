import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Iterator

import requests  # type: ignore

from leetcomp.errors import FetchContentException, FetchPostsException
from leetcomp.queries import COMP_POST_CONTENT_DATA_QUERY as content_query
from leetcomp.queries import COMP_POSTS_DATA_QUERY as posts_query
from leetcomp.utils import (
    config,
    latest_parsed_date,
    retry_with_exp_backoff,
    sort_and_truncate,
)


@dataclass
class LeetCodePost:
    id: str
    title: str
    content: str
    vote_count: int
    comment_count: int
    view_count: int
    creation_date: datetime


def get_posts_query(skip: int, first: int) -> dict[Any, Any]:
    query = posts_query.copy()
    query["variables"]["skip"] = skip  # type: ignore
    query["variables"]["first"] = first  # type: ignore
    return query


def get_content_query(post_id: int) -> dict[Any, Any]:
    query = content_query.copy()
    query["variables"]["topicId"] = post_id  # type: ignore
    return query


@retry_with_exp_backoff(retries=config["app"]["n_api_retries"])  # type: ignore
def post_content(post_id: int) -> str:
    query = get_content_query(post_id)
    response = requests.post(config["app"]["leetcode_graphql_url"], json=query)

    if response.status_code != 200:
        raise FetchContentException(
            f"Failed to fetch content for post_id={post_id}): {response.text}"
        )

    data = response.json().get("data")
    if not data:
        raise FetchContentException(
            f"Invalid response data for post_id={post_id}"
        )

    topic = data.get("topic")
    if not topic:
        raise FetchContentException(
            f"No topic found for post_id={post_id}. Response: {data}"
        )
    
    post = topic.get("post")
    if not post:
        raise FetchContentException(
            f"No post found in topic for post_id={post_id}. Topic: {topic}"
        )
    
    content = post.get("content")
    if content is None:
        print(f"Warning: Post {post_id} has no content")
        return ""
    
    return str(content)


@retry_with_exp_backoff(retries=config["app"]["n_api_retries"])  # type: ignore
def parsed_posts(skip: int, first: int) -> Iterator[LeetCodePost]:
    query = get_posts_query(skip, first)
    response = requests.post(config["app"]["leetcode_graphql_url"], json=query)

    if response.status_code != 200:
        raise FetchPostsException(
            f"Failed to fetch content for skip={skip}, first={first}): {response.text}"
        )

    data = response.json().get("data")
    if not data:
        raise FetchPostsException(
            f"Invalid response data for skip={skip}, first={first}"
        )

    posts = data["categoryTopicList"]["edges"]

    if skip == 0:
        posts = posts[1:]  # Skip pinned post

    for post in posts:
        try:
            content = post_content(post["node"]["id"])
            yield LeetCodePost(
                id=post["node"]["id"],
                title=post["node"]["title"],
                content=content,
                vote_count=post["node"]["post"]["voteCount"],
                comment_count=post["node"]["commentCount"],
                view_count=post["node"]["viewCount"],
                creation_date=datetime.fromtimestamp(
                    post["node"]["post"]["creationDate"]
                ),
            )
        except FetchContentException as e:
            print(f"Warning: Skipping post {post['node']['id']} due to error: {e}")
            continue  # Skip this post and continue with the next one
    query = get_posts_query(skip, first)
    response = requests.post(config["app"]["leetcode_graphql_url"], json=query)

    if response.status_code != 200:
        raise FetchPostsException(
            f"Failed to fetch content for skip={skip}, first={first}): {response.text}"
        )

    data = response.json().get("data")
    if not data:
        raise FetchPostsException(
            f"Invalid response data for skip={skip}, first={first}"
        )

    posts = data["categoryTopicList"]["edges"]

    if skip == 0:
        posts = posts[1:]  # Skip pinned post

    for post in posts:
        yield LeetCodePost(
            id=post["node"]["id"],
            title=post["node"]["title"],
            content=str(post_content(post["node"]["id"])),
            vote_count=post["node"]["post"]["voteCount"],
            comment_count=post["node"]["commentCount"],
            view_count=post["node"]["viewCount"],
            creation_date=datetime.fromtimestamp(
                post["node"]["post"]["creationDate"]
            ),
        )


def get_latest_posts(
    comps_path: str, start_date: datetime, till_date: datetime
) -> None:
    skip, first = 0, 50
    has_crossed_till_date = False
    fetched_posts, skips_due_to_lag = 0, 0

    with open(comps_path, "a") as f:
        while not has_crossed_till_date:
            for post in parsed_posts(skip, first):  # type: ignore[unused-ignore]
                if post.creation_date > start_date:
                    skips_due_to_lag += 1
                    continue

                if post.creation_date <= till_date:
                    has_crossed_till_date = True
                    break

                post_dict = asdict(post)
                post_dict["creation_date"] = post.creation_date.strftime(
                    config["app"]["date_fmt"]
                )
                f.write(json.dumps(post_dict) + "\n")
                fetched_posts += 1

                if fetched_posts % 10 == 0:
                    print(
                        f"{post.creation_date} Fetched {fetched_posts} posts..."
                    )

            skip += first

        print(f"Skipped {skips_due_to_lag} posts due to lag...")
        print(f"{post.creation_date} Fetched {fetched_posts} posts in total!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Fetch latest posts from LeetCode Compensations page."
    )
    parser.add_argument(
        "--comps_path",
        type=str,
        default=config["app"]["data_dir"] / "raw_comps.jsonl",
        help="Path to the file to store posts.",
    )
    parser.add_argument(
        "--till_date",
        type=str,
        default="",
        help="Fetch posts till this date (YYYY/MM/DD).",
    )
    args = parser.parse_args()

    if not args.till_date:
        till_date = latest_parsed_date(args.comps_path)
    else:
        till_date = datetime.strptime(args.till_date, "%Y/%m/%d")

    print(f"Fetching posts till {till_date}...")

    start_date = datetime.now() - timedelta(days=config["app"]["lag_days"])
    get_latest_posts(args.comps_path, start_date, till_date)
    sort_and_truncate(args.comps_path, truncate=True)
