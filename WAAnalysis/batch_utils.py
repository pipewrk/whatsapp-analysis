import json
import openai
import logging
from WAAnalysis.prompts import (
    create_topics_prompt,
    create_key_points_prompt,
    create_sentiment_prompt,
    create_entities_prompt
)
from WAAnalysis.utils import (
    clean_conversation,
    load_markdown,
    update_markdown_frontmatter,
    save_to_json
)
from WAAnalysis.config import (
    BATCH_INPUT_DIR,
    MD_DIR,
    BATCH_OUTPUT_DIR,
    COMPLETION_WINDOW,
    OPENAI_API_KEY,
    DEBUG,
    MANUAL_TESTING
)

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# Setup logging using the configuration from config.py
log = logging.getLogger(__name__)


# --------------------------------------
# Batch Input Generation Functions
# --------------------------------------

def generate_batch_input(file_name, prompt_type):
    """Generates a batch input for a specific markdown file and prompt type."""
    file_path = MD_DIR / file_name
    document = file_path.read_text()

    # Clean the conversation text for processing
    clean_text = clean_conversation(document)

    # Select the appropriate prompt based on prompt_type
    if prompt_type == "topics":
        system_prompt, user_prompt = create_topics_prompt(clean_text)
    elif prompt_type == "entities":
        system_prompt, user_prompt = create_entities_prompt(clean_text)
    elif prompt_type == "sentiment":
        system_prompt, user_prompt = create_sentiment_prompt(clean_text)
    elif prompt_type == "key_points":
        # Key Points generation uses the context from the frontmatter
        frontmatter = load_markdown(file_path)
        combined_text = f"{frontmatter['topics']}\n{frontmatter['entity_relationships']}\n{frontmatter['overall_sentiment']}\n\n{clean_text}"
        system_prompt, user_prompt = create_key_points_prompt(combined_text)
    else:
        raise ValueError("Invalid prompt type")

    # Create the jsonl structure for batch input
    jsonl_line = {
        "custom_id": file_name,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 1000
        }
    }

    if DEBUG:
        log.debug(f"Generated batch input for {file_name}, type: {prompt_type}")

    return jsonl_line


def write_jsonl_file(prompt_type, jsonl_line):
    """Writes a JSONL file for batch processing."""
    batch_folder = BATCH_INPUT_DIR / prompt_type
    batch_folder.mkdir(parents=True, exist_ok=True)
    
    batch_file_path = batch_folder / f"{prompt_type}.jsonl"
    
    # Append the jsonl line to the file
    save_to_json(jsonl_line, batch_file_path)

    if DEBUG:
        log.debug(f"JSONL file written to {batch_file_path}")

    return batch_file_path


# --------------------------------------
# Batch Processing Functions
# --------------------------------------

def upload_batch_file(file_path):
    """Uploads a batch input file to OpenAI."""
    if MANUAL_TESTING:
        log.info(f"Skipping upload in MANUAL_TESTING mode: {file_path}")
        return None

    with open(file_path, "rb") as file:
        response = openai.File.create(file=file, purpose="batch")
        return response['id']  # Return file ID for creating the batch


def create_batch(input_file_id, description="Batch job"):
    """Creates a batch using OpenAI API."""
    if MANUAL_TESTING:
        log.info(f"Skipping batch creation in MANUAL_TESTING mode for input file ID: {input_file_id}")
        return None

    response = openai.Batch.create(
        input_file_id=input_file_id,
        endpoint="/v1/chat/completions",
        completion_window=COMPLETION_WINDOW,
        metadata={"description": description}
    )

    if DEBUG:
        log.debug(f"Batch created: {response['id']}")

    return response  # Return Batch object with ID and status


def check_batch_status(batch_id):
    """Checks the status of a batch."""
    response = openai.Batch.retrieve(batch_id)
    return response['status']  # Return batch status


def download_batch_results(batch_id):
    """Downloads batch results after completion."""
    batch = openai.Batch.retrieve(batch_id)

    if batch['status'] == "completed":
        output_file_id = batch['output_file_id']
        if output_file_id:
            output_response = openai.File.download(output_file_id)
            output_path = BATCH_OUTPUT_DIR / f"{batch_id}_output.jsonl"
            with open(output_path, 'wb') as f:
                f.write(output_response)
            log.info(f"Results saved to {output_path}")
            return output_path
        else:
            log.warning("No output file found for this batch.")
    else:
        log.info(f"Batch is not completed yet. Current status: {batch['status']}")


def cancel_batch(batch_id):
    """Cancels an ongoing batch."""
    if MANUAL_TESTING:
        log.info(f"Skipping batch cancellation in MANUAL_TESTING mode for batch ID: {batch_id}")
        return None

    response = openai.Batch.cancel(batch_id)
    log.info(f"Batch {batch_id} status: {response['status']}")


def update_markdown_from_results(job):
    """Updates the markdown file frontmatter with the parsed results."""
    file_name = job["filename"]
    job_type = job["job_type"]
    output_file = job["output_file"]

    if not output_file:
        log.warning(f"No output file found for job {job_type} on {file_name}")
        return

    # Load the results from the output JSONL file
    output_file_path = BATCH_OUTPUT_DIR / output_file
    with open(output_file_path, 'r') as f:
        result_data = json.load(f)  # Assuming the batch output is stored as JSON

    # Parse the result data to update the markdown frontmatter
    md_file_path = MD_DIR / file_name
    update_markdown_frontmatter(md_file_path, result_data)

    log.info(f"Updated {file_name} with {job_type} results.")
