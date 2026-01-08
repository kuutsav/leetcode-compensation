import json
import os
import shutil
import xml.etree.ElementTree as ET

from leetcomp import PARSED_FILE, PARSED_TEMP_FILE
from leetcomp.utils import get_llm_output
from leetcomp.prompts import COMPENSATION_PARSING_PROMPT


def parse_compensation_post(content: str) -> str | None:
    prompt = COMPENSATION_PARSING_PROMPT.format(content=content)
    return get_llm_output(prompt)


def parse_xml_to_json(xml_output: str) -> list[dict]:
    offers = []
    content = xml_output.strip()
    if "```xml" in content:
        blocks = content.split("```xml")
        for block in blocks[1:]:
            if "```" in block:
                xml_content = block.split("```")[0].strip()
                offers.extend(_parse_xml_block(xml_content))
    else:
        offers.extend(_parse_xml_block(content))

    return offers


def _parse_xml_block(xml_content: str) -> list[dict]:
    offers = []
    parts = xml_content.split("<compensation-post>")

    for part in parts[1:]:
        try:
            lines = part.split("\n")
            xml_lines = []

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith("<") or (not xml_lines and stripped):
                    if not xml_lines and stripped:
                        xml_lines.append(f"<compensation-post>{stripped}")
                    else:
                        xml_lines.append(stripped)
                else:
                    break

            xml_str = "\n".join(xml_lines)
            root = ET.fromstring(f"<offer>{xml_str}</offer>")

            offer_dict = {}
            for child in root:
                tag = child.tag
                value = child.text.strip() if child.text else None
                if value:
                    if tag in [
                        "yoe",
                        "base",
                        "total",
                        "total-calculated",
                        "stipend-monthly",
                    ]:
                        try:
                            offer_dict[tag] = (
                                float(value) if "." in value else int(float(value))
                            )
                        except ValueError:
                            offer_dict[tag] = value
                    elif tag in ["compensation-post", "remote-from-india"]:
                        offer_dict[tag] = value.lower() == "true"
                    else:
                        offer_dict[tag] = value

            if offer_dict:
                offers.append(offer_dict)

        except (ET.ParseError, IndexError, ValueError):
            continue

    return offers


def should_parse_post(post: dict) -> bool:
    if post["downvotes"] > post["upvotes"]:
        return False

    return True


def posts_to_parse(posts_file: str):
    with open(posts_file, "r") as f:
        for line in f:
            post = json.loads(line)
            yield post


def write_parsed_rec(parsed_post: dict) -> None:
    with open(PARSED_TEMP_FILE, "a") as f:
        f.write(json.dumps(parsed_post) + "\n")


def prepend_to_parsed_posts(temp_file: str, parsed_posts_file: str) -> None:
    if not os.path.exists(temp_file):
        return

    if not os.path.exists(parsed_posts_file):
        shutil.move(temp_file, parsed_posts_file)
        return

    with open(temp_file, "r") as temp_f:
        new_content = temp_f.read()
    with open(parsed_posts_file, "r") as parsed_f:
        old_content = parsed_f.read()
    with open(parsed_posts_file, "w") as parsed_f:
        parsed_f.write(new_content)
        parsed_f.write(old_content)


def prev_parsed_ids(parsed_posts_file: str) -> set[str]:
    if not os.path.exists(parsed_posts_file):
        return set()

    parsed_ids = set()
    with open(parsed_posts_file, "r") as f:
        for line in f:
            parsed_ids.add(json.loads(line)["id"])
    return parsed_ids


def parse_posts_with_llm(posts_file: str, till_id: int | None) -> None:
    if os.path.exists(PARSED_TEMP_FILE):
        os.remove(PARSED_TEMP_FILE)

    parsed, skip = 0, 0
    for post in posts_to_parse(posts_file):
        if till_id and post["id"] == till_id:
            print(f"Exiting; Found a prev parsed id: {till_id}")
            break
        elif not should_parse_post(post):
            skip += 1
            write_parsed_rec(
                {"id": post["id"], "created_at": post["created_at"], "skip": True}
            )
            continue

        try:
            text_to_parse = post["title"] + "\n---\n" + post["content"]
            result = parse_compensation_post(text_to_parse)
            if not result:
                continue
            parsed_results = parse_xml_to_json(result)
            for parsed_result in parsed_results:
                write_parsed_rec(
                    {
                        "id": post["id"],
                        "created_at": post["created_at"],
                        "skip": False,
                        **parsed_result,
                    }
                )
                parsed += 1
        except Exception:
            print(f"Error parsing post {post['id']}")

        if parsed % 10 == 0:
            print(f"Parsed {parsed}; Skipped {skip}")

    print(f"Parsed {parsed}; Skipped {skip}")

    prepend_to_parsed_posts(PARSED_TEMP_FILE, PARSED_FILE)
