import re
import json
import pytz
import subprocess
import os
import logging
from pathlib import Path
from jsonschema import validate, ValidationError
from datetime import datetime
from WAAnalysis.config import SGT, PARTICIPANT_MAPPING, ERROR_LOGS_DIRECTORY, DEBUG
import yaml  # For working with frontmatter in markdown files

# -------------------------------
# Setup Logging
# -------------------------------
log = logging.getLogger(__name__)

# -------------------------------
# File Handling and Markdown Utilities
# -------------------------------

def read_file_content(file_path):
    """Reads the content of a file."""
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError as e:
        log.error(f"Error reading file {file_path}: {e}")
        return None

def load_markdown(file_path):
    """Reads a markdown file and splits the frontmatter and body content."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        if content.startswith("---"):
            frontmatter, body = content.split('---', 2)[1:]
            frontmatter = yaml.safe_load(frontmatter.strip())
        else:
            frontmatter = {}
            body = content

        return frontmatter, body.strip()

    except FileNotFoundError as e:
        log.error(f"Markdown file not found: {file_path} - {e}")
        return {}, ""

def update_markdown_frontmatter(file_path, document_data):
    """Updates the markdown file's frontmatter with new values."""
    frontmatter, body = load_markdown(file_path)

    # Update frontmatter with new data
    frontmatter.update({
        'topics': document_data.get('topics', []),
        'entity_relationships': document_data.get('entities', []),
        'detailed_summary': document_data.get('key_points', []),
        'overall_sentiment': document_data.get('sentiment', {}).get('sentiment', 'Unknown')
    })

    # Write the updated frontmatter and body back to the markdown file
    try:
        with open(file_path, 'w') as f:
            new_frontmatter = yaml.dump(frontmatter, default_flow_style=False).strip()
            f.write(f"---\n{new_frontmatter}\n---\n\n{body}\n")
        log.info(f"Updated frontmatter for {file_path}")
    except Exception as e:
        log.error(f"Failed to update frontmatter for {file_path}: {e}")

def save_to_json(data, file_path):
    """Saves data to a JSON file."""
    try:
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        log.info(f"Saved data to {file_path}")
    except Exception as e:
        log.error(f"Failed to save data to {file_path}: {e}")

# -------------------------------
# Directory Management
# -------------------------------

def ensure_directories_exist(directories):
    """Ensure that the provided directories exist, creating them if necessary."""
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            log.info(f"Created directory: {directory}")
        else:
            log.debug(f"Directory already exists: {directory}")

# -------------------------------
# Timestamp and Date Utilities
# -------------------------------

def convert_core_data_timestamp(timestamp):
    """Convert Core Data timestamp to a readable date."""
    reference_date = 978307200  # Core Data reference date: Jan 1, 2001
    if timestamp:
        return datetime.utcfromtimestamp(timestamp + reference_date).strftime('%Y-%m-%d %H:%M:%S')
    return None

def convert_to_sgt(utc_time_str):
    """Converts UTC time string to Singapore Time (SGT)."""
    try:
        utc_time = datetime.strptime(utc_time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)
        sgt_time = utc_time.astimezone(SGT)
        return sgt_time.strftime("%I:%M %p")  # Return in 12-hour format
    except ValueError as e:
        log.error(f"Failed to convert time {utc_time_str} to SGT: {e}")
        return None

def calculate_time_to_read(timestamp_received, timestamp_read):
    """Calculates the time difference between received and read timestamps in minutes."""
    if timestamp_received and timestamp_read:
        time_diff = (timestamp_read - timestamp_received) / 60  # Convert to minutes
        return f"{time_diff:.2f} minutes"
    return None

# -------------------------------
# Conversation and Message Utilities
# -------------------------------

def clean_conversation(document):
    """Cleans the conversation text by removing frontmatter, timestamps, etc."""
    try:
        # Remove frontmatter
        clean_doc = re.sub(r'---[\s\S]*?---', '', document).strip()
        # Remove timestamps (12-hour format)
        clean_doc = re.sub(r'\d{2}:\d{2} [APM]{2}', '', clean_doc).strip()
        return clean_doc
    except Exception as e:
        log.error(f"Failed to clean conversation: {e}")
        return document

def format_as_quote(message_text):
    """Formats multi-line message as a quoted block."""
    lines = message_text.splitlines()
    return "\n".join([f"> {line}" for line in lines])

def generate_markdown_for_day(day, messages):
    """Generates markdown for a day's conversation."""
    markdown = "---\n"
    markdown += "topics:\nentity_relationships:\ndetailed_summary:\noverall_sentiment:\n---\n\n"
    markdown += f"# {datetime.strptime(day, '%Y-%m-%d').strftime('%A, %d %B %Y')}\n\n"
    
    for message in messages:
        from_participant = PARTICIPANT_MAPPING.get(message['FromJID'], "Unknown")
        to_participant = PARTICIPANT_MAPPING.get(message['ToJID'], "Unknown")
        message_time = convert_to_sgt(message['MessageDate'])

        if message['RepliedToMessageID']:
            markdown += f"**{from_participant}**: _Replying to:_\n\n"
            markdown += format_as_quote(f"**{to_participant}**: {message['Message']}\n")
        else:
            markdown += f"**{from_participant}**: {message['Message']}\n"

        markdown += f"  {message_time}\n"
        media_filename = extract_filename_from_path(message.get('MediaPath'))
        if media_filename:
            markdown += f"  Attached: {media_filename}\n"
        markdown += "\n"
    
    return markdown

def extract_filename_from_path(media_path):
    """Extracts the filename from a media path."""
    if media_path:
        return os.path.basename(media_path)
    return None

# -------------------------------
# Protobuf and Database Utilities
# -------------------------------

def decode_with_protoc(blob, message_id, blob_info_directory, error_logs_directory):
    """Decode a protobuf blob using protoc --decode_raw and handle errors."""
    blob_file_path = f'{blob_info_directory}/blob_{message_id}.bin'
    with open(blob_file_path, 'wb') as blob_file:
        blob_file.write(blob)

    error_log_path = f'{error_logs_directory}/error_{message_id}.log'
    try:
        with open(blob_file_path, 'rb') as blob_file:
            protoc_output = subprocess.check_output(['protoc', '--decode_raw'], stdin=blob_file)
            return protoc_output.decode('utf-8')
    except subprocess.CalledProcessError as e:
        error_details = f"Error running decode_raw for message ID {message_id}:\n{e.output.decode('utf-8')}"
        with open(error_log_path, 'w') as error_log:
            error_log.write(error_details)
        log.error(f"Failed to decode message {message_id}: {error_details}")
        return None

def fetch_replied_message(cursor, replied_to_message_id):
    """Fetches the original replied-to message from the database."""
    query = '''
    SELECT ZTEXT, ZMESSAGEDATE, ZSENTDATE, ZFROMJID, ZTOJID
    FROM ZWAMESSAGE
    WHERE Z_PK = ?
    '''
    cursor.execute(query, (replied_to_message_id,))
    return cursor.fetchone()

# -------------------------------
# Schema Validation
# -------------------------------

def load_schema(schema_path):
    """Loads a JSON schema from a file."""
    try:
        with open(schema_path, 'r') as schema_file:
            return json.load(schema_file)
    except Exception as e:
        log.error(f"Failed to load schema from {schema_path}: {e}")
        return None

def validate_document(document, schema_path):
    """Validates a document against a given JSON schema."""
    schema = load_schema(schema_path)
    if not schema:
        return False, "Schema not loaded"
    try:
        validate(instance=document, schema=schema)
        return True, None
    except ValidationError as e:
        log.error(f"Validation error: {e.message}")
        return False, e.message

output_schema = {
    "topics": list,
    "key_points": list,
    "sentiment": dict,
    "entities": list
}

def validate_output(output):
    """Validates the structure of the output based on the output schema."""
    if not isinstance(output, dict):
        raise ValueError("Output should be a dictionary.")
    
    for key, expected_type in output_schema.items():
        if key not in output:
            raise ValueError(f"Missing required key: {key}")
        if not isinstance(output[key], expected_type):
            raise TypeError(f"{key} should be of type {expected_type}, but got {type(output[key])}.")
    
    # Optional validation for sentiment keys
    if "sentiment" in output:
        if not all(k in output["sentiment"] for k in ["sentiment", "polarity", "subjectivity"]):
            raise ValueError("Sentiment object is missing required keys.")
    
    return True

# -------------------------------
# API Response Handling
# -------------------------------

def parse_response(response):
    """Parses and validates the response from the API."""
    try:
        parsed_output = json.loads(response)
        if validate_output(parsed_output):
            return parsed_output
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        log.error(f"Error parsing response: {e}")
        return None

def extract_results(parsed_response):
    """Extracts key results from the parsed API response."""
    if not parsed_response:
        return None

    return {
        "topics": parsed_response.get("topics", []),
        "key_points": parsed_response.get("key_points", []),
        "sentiment": parsed_response.get("sentiment", {}),
        "entities": parsed_response.get("entities", [])
    }

def prepare_output_for_frontmatter(parsed_response):
    """Prepares the parsed response for updating markdown frontmatter."""
    if parsed_response:
        return {
            "topics": parsed_response.get("topics", []),
            "entity_relationships": parsed_response.get("entities", []),
            "detailed_summary": parsed_response.get("key_points", []),
            "overall_sentiment": parsed_response.get("sentiment", {})
        }
    return None
