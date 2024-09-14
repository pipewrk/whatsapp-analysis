import json
import logging
from pathlib import Path
import tiktoken  # Import tokenizer for counting tokens
from WAAnalysis.utils import (
    clean_conversation,
    load_markdown,
)
from WAAnalysis.config import (
    BATCH_INPUT_DIR,
    CHUNKED_DIR,
    DEBUG
)

log = logging.getLogger(__name__)

# Tokenizer initialization (for token counting)
tokenizer = tiktoken.get_encoding("cl100k_base")
TOKEN_LIMIT = 5000  # 5k tokens

# --------------------------------------
# Helper Functions
# --------------------------------------

def clean_special_characters(text):
    """
    Clean special characters from YAML frontmatter fields to avoid parsing issues.
    """
    text = text.replace('"', '\\"')
    text = text.replace("'", "\\'")
    return text


def generate_system_prompt():
    """
    Generates the system instructions for the assistant.
    """
    system_prompt = """
You are summarizing a chunk of a markdown conversation between a user and an assistant.
Your task is to strictly summarize the key points and important findings from the conversation in bullet point format.
Only provide the summary—nothing else. Do not add suggestions, comments, or extra words.

### Example Input:
User: I want to discuss setting up a server with high availability.
Assistant: Sure, we can look at redundancy and load balancing options.

User: I'd also like to implement automated backups and failover strategies.
Assistant: For backups, you can consider cloud storage or RAID solutions.

### Example Output:
- Discussion on server setup with high availability.
- Considered redundancy and load balancing as options.
- Automated backups and failover strategies were introduced.
- Suggestions: cloud storage and RAID solutions for backups.
"""
    return system_prompt


def count_tokens(text):
    """
    Count tokens using the tokenizer.
    """
    return len(tokenizer.encode(text))


def has_summary_after_title(content):
    """
    Check if the document has a `## Summary` header within the first 5 lines after the main `# Title`.
    """
    lines = content.strip().split("\n")
    
    # We're only interested in the first 5 lines after the frontmatter
    for i, line in enumerate(lines[:5]):  # Limit to first 5 lines
        if line.startswith("# "):  # This is the title (H1)
            # Check the next line for `## Summary`
            if i + 1 < len(lines) and lines[i + 1].startswith("## Summary"):
                return True
    return False


def generate_batch_input(file_name):
    """
    Create a batch input for summarizing markdown chunks.
    """
    file_path = CHUNKED_DIR / file_name
    frontmatter, document_body = load_markdown(file_path)

    if not document_body:
        log.error(f"Failed to retrieve content from {file_name}. Skipping...")
        return None

    # Check if the file already has a summary after the main title
    if has_summary_after_title(document_body):
        log.info(f"Skipping {file_name} as it already has a `## Summary` after the title.")
        return None

    # Clean the conversation text for processing
    clean_text = clean_conversation(document_body)

    # Check token count
    token_count = count_tokens(clean_text)
    if token_count < TOKEN_LIMIT:
        log.info(f"Skipping {file_name} as it has fewer than {TOKEN_LIMIT} tokens (actual: {token_count}).")
        return None

    # Generate system prompt with instructions
    system_prompt = generate_system_prompt()

    # Create the JSONL structure for batch input
    jsonl_line = {
        "custom_id": file_name,  # Use the filename (without extension) as the custom ID
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": clean_text}
            ],
            "max_tokens": 500
        }
    }
    return jsonl_line


def write_jsonl_file(jsonl_data):
    """
    Write the generated batch input to a JSONL file.
    """
    batch_folder = BATCH_INPUT_DIR / "summarization"
    batch_folder.mkdir(parents=True, exist_ok=True)

    batch_file_path = batch_folder / "summarization_batch_input.jsonl"

    # Write the JSONL lines to the file
    with open(batch_file_path, mode='w', encoding='utf-8') as jsonl_file:
        for jsonl_line in jsonl_data:
            if jsonl_line:  # Ensure no None values are written
                json.dump(jsonl_line, jsonl_file)
                jsonl_file.write('\n')

    if DEBUG:
        log.debug(f"JSONL file written to {batch_file_path}")

    return batch_file_path


# --------------------------------------
# Main Function to Process All Chunks
# --------------------------------------

def create_jsonl_for_chunks():
    """
    Generate JSONL input for all markdown chunks in CHUNKED_DIR.
    """
    try:
        chunked_files = list(Path(CHUNKED_DIR).glob("*.md"))

        if not chunked_files:
            log.warning(f"No markdown files found in {CHUNKED_DIR}.")
            return

        jsonl_data = []

        for chunk_file in chunked_files:
            log.info(f"Processing file: {chunk_file.name}")
            batch_input = generate_batch_input(chunk_file.name)
            if batch_input:
                jsonl_data.append(batch_input)

        # Write to JSONL file
        if jsonl_data:
            jsonl_file_path = write_jsonl_file(jsonl_data)
            log.info(f"JSONL file created at: {jsonl_file_path}")
        else:
            log.info("No valid files to process for JSONL.")

    except Exception as e:
        log.error(f"An error occurred while generating JSONL for chunks: {e}", exc_info=True)


# --------------------------------------
# Execution
# --------------------------------------

if __name__ == "__main__":
    log.info("Starting JSONL generation for markdown chunks...")
    create_jsonl_for_chunks()
    log.info("JSONL generation completed.")
