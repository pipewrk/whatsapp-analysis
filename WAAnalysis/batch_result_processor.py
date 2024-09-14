import logging
import json
from pathlib import Path
from WAAnalysis.config import BATCH_OUTPUT_DIR, MD_DIR, DEBUG
from WAAnalysis.utils import update_markdown_frontmatter, load_markdown

# -------------------------------
# Import Global Logger from Config
# -------------------------------
log = logging.getLogger(__name__)

# -------------------------------
# Utility Functions
# -------------------------------

def load_jsonl_file(file_path):
    """Loads a .jsonl file and returns a list of parsed lines."""
    data = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                data.append(json.loads(line.strip()))
        return data
    except Exception as e:
        log.error(f"Failed to load {file_path}: {e}")
        return []

def merge_existing_data(md_file_path, new_data):
    """Merges new batch data with existing frontmatter, ensuring no overwriting of previous results."""
    log.debug(f"Loading existing markdown content from {md_file_path}")
    frontmatter, body = load_markdown(md_file_path)

    log.debug(f"Existing frontmatter for {md_file_path}: {frontmatter}")
    log.debug(f"New data to merge: {new_data}")

    # Merge new data with the existing frontmatter
    for key, value in new_data.items():
        log.debug(f"Processing key: {key}, value: {value}")

        if key in frontmatter:
            if frontmatter[key] is None:
                log.debug(f"Key {key} is None, initializing as an empty list.")
                frontmatter[key] = []

            if isinstance(frontmatter[key], list) and isinstance(value, list):
                if all(isinstance(item, dict) for item in value):
                    # Custom merge logic for lists of dictionaries (like `entity_relationships`)
                    merged_items = {f"{item['person']}_{item['role']}": item for item in frontmatter[key]}

                    for new_item in value:
                        key_for_new_item = f"{new_item['person']}_{new_item['role']}"
                        if key_for_new_item in merged_items:
                            # Merge relationships lists to avoid duplicates
                            merged_items[key_for_new_item]['relationships'] = list(
                                set(merged_items[key_for_new_item]['relationships'] + new_item['relationships'])
                            )
                        else:
                            merged_items[key_for_new_item] = new_item
                    
                    frontmatter[key] = list(merged_items.values())  # Rebuild the list from the merged dictionary
                    log.debug(f"Merged list for {key}: {frontmatter[key]}")
                else:
                    # Merge and deduplicate non-dict lists
                    frontmatter[key] = list(set(frontmatter[key] + value))
                    log.debug(f"Merged list for {key}: {frontmatter[key]}")
            elif isinstance(frontmatter[key], dict) and isinstance(value, dict):
                # Merge dictionaries (for cases like `sentiment`)
                frontmatter[key].update(value)
                log.debug(f"Updated dict for {key}: {frontmatter[key]}")
            else:
                # Overwrite simple values
                frontmatter[key] = value
                log.debug(f"Overwrote {key} with new value: {frontmatter[key]}")
        else:
            frontmatter[key] = value  # Add new key-value pair
            log.debug(f"Added new key {key} with value: {frontmatter[key]}")

    return frontmatter, body


def process_batch_result(batch_data, batch_type):
    """Processes batch results and updates the corresponding markdown file."""
    for result in batch_data:
        try:
            file_name = result['custom_id']
            response_content = json.loads(result['response']['body']['choices'][0]['message']['content'])

            log.info(f"Processing batch result for {file_name} - Type: {batch_type}")
            log.debug(f"Response content: {response_content}")

            document_data = {}
            if batch_type == "topics":
                document_data['topics'] = response_content.get('topics', [])
            elif batch_type == "entities":
                document_data['entity_relationships'] = response_content.get('entities', [])
            elif batch_type == "sentiment":
                document_data['overall_sentiment'] = {
                    "sentiment": response_content.get('sentiment', "Unknown"),
                    "polarity": response_content.get('polarity', 0),
                    "subjectivity": response_content.get('subjectivity', 0)
                }
            elif batch_type == "key_points":
                document_data['detailed_summary'] = response_content.get('key_points', [])

            md_file_path = MD_DIR / file_name
            if md_file_path.exists():
                log.info(f"Updating {md_file_path} with new {batch_type}.")
                new_frontmatter, body = merge_existing_data(md_file_path, document_data)
                update_markdown_frontmatter(md_file_path, new_frontmatter, body)
                log.info(f"Successfully updated {file_name}")
            else:
                log.error(f"Markdown file {file_name} not found in {MD_DIR}. Skipping update.")

        except Exception as e:
            log.error(f"Error processing result for {file_name}: {e}")

# -------------------------------
# Batch Result Processing
# -------------------------------

def process_results():
    """Process batch results for all types."""
    batches = {
        "topics": "topics_results.jsonl",
        "entities": "entities_results.jsonl",
        "sentiment": "sentiment_results.jsonl",
        "key_points": "key_points_results.jsonl"
    }

    for batch_type, result_file in batches.items():
        result_file_path = BATCH_OUTPUT_DIR / result_file
        log.info(f"Processing {batch_type} results from {result_file_path}")

        batch_data = load_jsonl_file(result_file_path)
        if batch_data:
            process_batch_result(batch_data, batch_type)
        else:
            log.error(f"No data found or failed to load {result_file_path}.")

# -------------------------------
# Script Entry Point
# -------------------------------

if __name__ == "__main__":
    if DEBUG:
        log.info("Running in DEBUG mode.")

    log.info("Starting to process batch results.")
    process_results()
    log.info("Finished processing batch results.")
