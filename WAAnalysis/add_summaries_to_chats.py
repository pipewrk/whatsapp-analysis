import json
import logging
from pathlib import Path
from WAAnalysis.utils import load_markdown, update_markdown_frontmatter
from WAAnalysis.config import BATCH_OUTPUT_DIR

# Set paths
CHUNKED_DIR = Path("chunked")
BATCH_RESULTS_FILE = BATCH_OUTPUT_DIR / "batch_CG2gVgPL6bOZrsL8pEZdHgtg_output.jsonl"
# BATCH_RESULTS_FILE = BATCH_OUTPUT_DIR / "batch_ntnZch6GhHcIwHB120uHosnQ_output.jsonl"

log = logging.getLogger(__name__)

# --------------------------------------
# Helper Function to Load Batch Results
# --------------------------------------

def load_batch_results(results_file):
    """
    Load batch results from the JSONL file and map them to their respective custom_id (filename).
    """
    results_mapping = {}
    try:
        with open(results_file, 'r') as file:
            for line in file:
                result = json.loads(line)
                custom_id = result['custom_id']
                response_content = result['response']['body']['choices'][0]['message']['content']
                results_mapping[custom_id] = response_content
        log.info(f"Batch results loaded successfully from {results_file}.")
    except Exception as e:
        log.error(f"Error loading batch results: {e}")
    return results_mapping

# --------------------------------------
# Function to Insert Summary into Markdown Files
# --------------------------------------

def insert_summary_into_markdown(file_path, summary):
    """
    Inserts the provided summary after the # Header title in the markdown file.
    """
    try:
        frontmatter, body = load_markdown(file_path)
        
        # Split the body into lines to locate the # Header
        body_lines = body.split("\n")
        updated_lines = []
        summary_inserted = False

        for line in body_lines:
            updated_lines.append(line)

            # Find the # Header line and insert the summary after it
            if line.startswith("# ") and not summary_inserted:
                updated_lines.append("## Summary\n")
                updated_lines.append(summary)
                updated_lines.append("")  # Add a blank line for separation
                summary_inserted = True
        
        # Combine the updated body and rewrite the markdown file
        updated_body = "\n".join(updated_lines)
        update_markdown_frontmatter(file_path, frontmatter, updated_body)
        
        log.info(f"Summary inserted into {file_path}.")
    
    except Exception as e:
        log.error(f"Error inserting summary into {file_path}: {e}")

# --------------------------------------
# Main Function to Process All Files
# --------------------------------------

def process_markdown_files_with_summaries():
    """
    For each markdown file in CHUNKED_DIR, insert the corresponding summary after the header.
    """
    # Load the batch results
    batch_results = load_batch_results(BATCH_RESULTS_FILE)
    
    # Process each markdown file in the chunked directory
    for chunk_file in Path(CHUNKED_DIR).glob("*.md"):
        file_name = chunk_file.name
        if file_name in batch_results:
            summary = batch_results[file_name]
            log.info(f"Inserting summary into {file_name}.")
            insert_summary_into_markdown(chunk_file, summary)
        else:
            log.warning(f"No summary found for {file_name}. Skipping...")

# --------------------------------------
# Execution
# --------------------------------------

if __name__ == "__main__":
    log.info("Starting to process markdown files with summaries...")
    process_markdown_files_with_summaries()
    log.info("Processing completed.")
