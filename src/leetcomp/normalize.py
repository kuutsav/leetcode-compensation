from collections import Counter
from itertools import groupby
import json
import os

from leetcomp import (
    NormalizedEntity,
    COMPANY_MAP_FILE,
    ROLE_MAP_FILE,
    LOCATION_MAP_FILE,
)
from leetcomp.prompts import (
    get_normalization_prompt,
    get_normalization_prompt_with_context,
)
from leetcomp.utils import get_llm_output


def get_entity_map_file(entity_type: NormalizedEntity) -> str:
    entity_files: dict[NormalizedEntity, str] = {
        NormalizedEntity.COMPANY: COMPANY_MAP_FILE,
        NormalizedEntity.ROLE: ROLE_MAP_FILE,
        NormalizedEntity.LOCATION: LOCATION_MAP_FILE,
    }
    return entity_files.get(entity_type, COMPANY_MAP_FILE)


def load_mapping(file_path: str) -> dict[str, str]:
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r") as f:
        return json.load(f)


def save_mapping(file_path: str, mapping: dict[str, str]) -> None:
    sorted_mapping = dict(sorted(mapping.items()))
    with open(file_path, "w") as f:
        json.dump(sorted_mapping, f, indent=2)


def get_context_for_char(existing_mapping: dict[str, str], first_char: str) -> str:
    first_char = first_char.lower()
    context_entries = []
    for orig, normalized in existing_mapping.items():
        if orig.lower().startswith(first_char):
            context_entries.append(f"{orig} -> {normalized}")
    return "\n".join(sorted(context_entries))


def get_all_entities(file_path: str, entity_type: str) -> list[str]:
    all_recs = []
    with open(file_path, "r") as f:
        for line in f:
            rec = json.loads(line)
            if entity_type in rec:
                all_recs.append(rec[entity_type])
    return all_recs


def get_new_entities(
    file_path: str,
    entity_type: NormalizedEntity,
    till_id: int | None = None,
    till_timestamp: str | None = None,
    existing_mapping: dict[str, str] | None = None,
) -> list[str]:
    new_entities = []
    with open(file_path, "r") as f:
        for line in f:
            try:
                rec = json.loads(line)
                # stop when we reach already-processed records by id
                if till_id is not None and rec.get("id") == till_id:
                    break
                # stop when we pass the timestamp (posts are ordered by most recent first)
                if (
                    till_timestamp is not None
                    and rec.get("created_at", "") < till_timestamp
                ):
                    break
                if entity_type in rec:
                    entity = rec[entity_type]
                    # only include if not already mapped (lowercase for consistent lookup)
                    if entity.lower() not in existing_mapping:
                        new_entities.append(entity)
            except (TypeError, ValueError, KeyError) as e:
                print(f"Warning: Skipping invalid record in {file_path}: {e}")
                continue
    return new_entities


def get_grouped_new_entities(new_entities: list[str], min_count: int = 1):
    cc = Counter(new_entities)

    to_group = []
    for entity, count in cc.most_common(len(cc)):
        if count < min_count:
            continue
        to_group.append(f"{entity} [{count}]")
    to_group = sorted(to_group)

    for key, group in groupby(to_group, key=lambda x: x[0].lower()):
        yield key, ", ".join(group)


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

    # remove opening ```
    output = output[3:]

    # remove language identifier if present (e.g., ```text, ```python)
    if "\n" in output:
        first_line_end = output.index("\n")
        first_line = output[:first_line_end].strip()
        # Check if first line is a language identifier (no colons or pipes)
        if first_line and ":" not in first_line and "|" not in first_line:
            output = output[first_line_end + 1 :]

    # remove closing ```
    output = output.rstrip("`").strip()

    return output


def _llm_mapped_output(
    entity_type: NormalizedEntity, batched_group: list[str]
) -> dict[str, str]:
    normalization_prompt = get_normalization_prompt(entity_type, "\n".join(batched_group))
    llm_output = get_llm_output(normalization_prompt)

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
                mapped_entities[entity.lower()] = final.strip()

    return mapped_entities


def _llm_mapped_output_with_context(
    entity_type: NormalizedEntity, grouped_data: str, context: str
) -> dict[str, str]:
    normalization_prompt = get_normalization_prompt_with_context(
        entity_type, grouped_data, context
    )
    llm_output = get_llm_output(normalization_prompt)

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
                mapped_entities[entity.lower()] = final.strip()

    return mapped_entities


def normalize_new_entities(
    file_path: str,
    entity_type: NormalizedEntity,
    till_id: int | None = None,
    till_timestamp: str | None = None,
    existing_mapping: dict[str, str] | None = None,
) -> dict[str, str]:
    if existing_mapping is None:
        existing_mapping = {}
    new_entities = get_new_entities(
        file_path, entity_type, till_id, till_timestamp, existing_mapping
    )

    if not new_entities:
        print(f"No new {entity_type} entities to normalize")
        return {}

    print(f"Found {len(new_entities)} new {entity_type} entities to normalize")

    new_mappings = {}
    for first_char, grouped_data in get_grouped_new_entities(new_entities):
        context = get_context_for_char(existing_mapping, first_char)
        char_mappings = _llm_mapped_output_with_context(
            entity_type, grouped_data, context
        )
        new_mappings.update(char_mappings)
        print(f"Processed key `{first_char}` for entity {entity_type}...")

    return new_mappings


def normalized_entity_mapping(
    file_path: str, entity_type: NormalizedEntity, batch_size: int = 4
):
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


def normalize_and_save(
    file_path: str, till_id: int | None = None, till_timestamp: str | None = None
) -> None:
    for entity_type in [
        NormalizedEntity.COMPANY,
        NormalizedEntity.ROLE,
        NormalizedEntity.LOCATION,
    ]:
        map_file = get_entity_map_file(entity_type)

        if not os.path.exists(map_file):
            # generate mappings from scratch when file doesn't exist
            print(f"Mapping file not found for {entity_type}, generating from scratch...")
            mapped_entities = normalized_entity_mapping(file_path, entity_type)
            save_mapping(map_file, mapped_entities)
            print(f"Created {len(mapped_entities)} {entity_type} mappings\n")
        else:
            # incremental update for existing mappings
            existing_mapping = load_mapping(map_file)
            new_mappings = normalize_new_entities(
                file_path, entity_type, till_id, till_timestamp, existing_mapping
            )

            if new_mappings:
                existing_mapping.update(new_mappings)
                save_mapping(map_file, existing_mapping)
                print(f"Added {len(new_mappings)} new {entity_type} mappings\n")
            else:
                print(f"No new mappings for {entity_type}\n")
