from collections import Counter
from itertools import groupby
import json
import os

from leetcomp import PARSED_FILE, NormalizedEntity
from leetcomp.prompts import get_normalization_prompt
from leetcomp.utils import get_llm_output, Provider


def get_all_entities(file_path: str, entity_type: str) -> list[str]:
    all_recs = []
    with open(file_path, "r") as f:
        for line in f:
            rec = json.loads(line)
            if entity_type in rec:
                all_recs.append(rec[entity_type])
    return all_recs


def get_grouped_entities(file_path: str, entity_type: str):
    entities = get_all_entities(file_path, entity_type)
    cc = Counter(entities)

    to_group = []
    for entity, count in cc.most_common(len(cc)):
        if count < 2:
            break
        to_group.append(f"{entity} [{count}]")
    to_group = sorted(to_group)

    for key, group in groupby(to_group, key=lambda x: x[0]):
        yield key, ", ".join(group)


def clean_llm_output(output: str) -> str:
    output = output.strip()

    if not (output.startswith("```") and output.endswith("```")):
        return output

    # Remove opening ```
    output = output[3:]

    # Remove language identifier if present (e.g., ```text, ```python)
    if "\n" in output:
        first_line_end = output.index("\n")
        first_line = output[:first_line_end].strip()
        # Check if first line is a language identifier (no colons or pipes)
        if first_line and ":" not in first_line and "|" not in first_line:
            output = output[first_line_end + 1 :]

    # Remove closing ```
    output = output.rstrip("`").strip()

    return output


def _llm_mapped_output(entity_type: str, batched_group: list[str]) -> dict[str, str]:
    normalization_prompt = get_normalization_prompt(entity_type, "\n".join(batched_group))
    llm_output = get_llm_output(normalization_prompt, Provider.LM_STUDIO)

    if not llm_output:
        return {}

    llm_output = clean_llm_output(llm_output)
    mapped_entities = {}
    for row in llm_output.strip().split("\n"):
        row = row.strip()
        if not row:
            continue
        if ":" not in row:
            print(f"Warning: Skipping malformed line: {row}")
            continue

        parts = row.split(":", 1)
        if len(parts) != 2:
            print(f"Warning: Skipping invalid line: {row}")
            continue

        originals, final = parts
        for entity in originals.split("|"):
            entity = entity.strip()
            if entity:
                mapped_entities[entity] = final.strip()

    return mapped_entities


def normalized_entity_mapping(file_path: str, entity_type: str, batch_size: int = 4):
    batched_group, mapped_entities = [], {}
    for key, group in get_grouped_entities(file_path, entity_type):
        batched_group.append(group)
        if len(batched_group) == batch_size:
            mapped_entities.update(_llm_mapped_output(entity_type, batched_group))
            batched_group = []
        print(f"Processed key `{key}` for entity {entity_type}...")

    if batched_group:
        mapped_entities.update(_llm_mapped_output(entity_type, batched_group))
        del batched_group

    return mapped_entities


def normalize_all_entities(file_path: str = PARSED_FILE):
    for entity_type in [
        NormalizedEntity.COMPANY,
        NormalizedEntity.ROLE,
        NormalizedEntity.LOCATION,
    ]:
        entity = entity_type.split("-")[0]
        entity_file_path = f"data/{entity}_map.json"
        if not os.path.exists(entity_file_path):
            mapped_entities = normalized_entity_mapping(file_path, entity_type)
            with open(f"data/{entity}_map.json", "w") as f:
                json.dump(mapped_entities, f)
            print(f"Saved {len(mapped_entities)} {entity} mapping\n")
        else:
            print(f"Skipped {entity}; Mapping exists already")


if __name__ == "__main__":
    normalize_all_entities(PARSED_FILE)
