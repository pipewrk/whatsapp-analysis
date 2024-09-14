import os
import tiktoken
import logging
from pathlib import Path
import re
from WAAnalysis.config import MD_DIR2
from WAAnalysis.utils import ensure_directories_exist

# -------------------------------
# Setup Directories
# -------------------------------
CHUNKED_DIR = Path("chunked")
ensure_directories_exist([CHUNKED_DIR])

# -------------------------------
# Tokenizer Initialization
# -------------------------------
tokenizer = tiktoken.get_encoding("cl100k_base")
TOKEN_LIMIT = 20000  # 20k tokens per chunk

# -------------------------------
# Helper Functions
# -------------------------------

def count_tokens(text):
    """Count tokens in a given text using the tokenizer."""
    tokens = tokenizer.encode(text)
    logging.info(f"Token count for text: {len(tokens)}")
    return len(tokens)

def extract_frontmatter(text):
    """Extract and return the YAML frontmatter from the file content."""
    frontmatter_match = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if frontmatter_match:
        return frontmatter_match.group(0), text[len(frontmatter_match.group(0)):].strip()
    return "", text

def extract_system_message_link(text):
    """Extract and return the system message link from the file content."""
    system_message_match = re.search(r'\[System Messages\]\(.*?\)', text)
    if system_message_match:
        return system_message_match.group(0), text[:system_message_match.start()].strip()
    return "", text

def split_text_by_user(messages):
    """
    Split the conversation by 'User' messages, ensuring that each chunk starts with a 'User' message.
    """
    user_indices = [i for i, msg in enumerate(messages) if msg.startswith("**User**")]
    return [messages[i:j] for i, j in zip(user_indices, user_indices[1:] + [None])]

def write_chunked_file(base_filename, part_number, part_total, chunk, output_dir, frontmatter, system_message):
    """Write each chunk to a markdown file with frontmatter, updated title, and system message."""
    # Inject the updated title with continuation part in the frontmatter
    updated_title = re.sub(r'title: "(.*?)"', f'title: "{base_filename} (continued: Part {part_number} of {part_total})"', frontmatter)
    
    # Create a # Title header based on the base_filename and part number
    title_header = f"# {base_filename} (continued: Part {part_number} of {part_total})"
    
    # Add the frontmatter, title header, chunk content, and system message to the file
    chunk_content = f"{updated_title}\n\n{title_header}\n\n" + "\n".join(chunk) + f"\n\n{system_message}"

    chunk_filename = f"{base_filename}_part_{part_number}.md"
    chunk_filepath = output_dir / chunk_filename

    with open(chunk_filepath, 'w', encoding='utf-8') as chunk_file:
        chunk_file.write(chunk_content)
    
    logging.info(f"Chunk written: {chunk_filename}")

def process_and_chunk_file(filepath, output_dir):
    """Process each markdown file, split it into 20k token chunks, and save them."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            text = file.read()

        base_filename = filepath.stem

        # Extract the frontmatter and system message link
        frontmatter, content = extract_frontmatter(text)
        system_message, content = extract_system_message_link(content)

        # Split the conversation into messages
        messages = content.split("\n")

        # Split by user messages
        chunks = split_text_by_user(messages)
        
        current_chunk = []
        current_token_count = 0
        chunked_messages = []
        chunk_counter = 1

        # Create chunks of messages until the token limit is reached
        for chunk in chunks:
            chunk_tokens = count_tokens("\n".join(chunk))
            
            if current_token_count + chunk_tokens > TOKEN_LIMIT:
                chunked_messages.append(current_chunk)
                current_chunk = chunk
                current_token_count = chunk_tokens
                chunk_counter += 1
            else:
                current_chunk.extend(chunk)
                current_token_count += chunk_tokens
        
        # Add the final chunk
        if current_chunk:
            chunked_messages.append(current_chunk)

        # Write each chunk to a file
        part_total = len(chunked_messages)
        for part_number, chunk in enumerate(chunked_messages, start=1):
            write_chunked_file(base_filename, part_number, part_total, chunk, output_dir, frontmatter, system_message)

    except Exception as e:
        logging.error(f"Failed to process {filepath.name}: {e}")

# -------------------------------
# Copy File If Under 20k Tokens
# -------------------------------

def copy_file(filepath, output_dir):
    """Copy files under 20k tokens without modification."""
    try:
        destination = output_dir / filepath.name
        with open(filepath, 'r', encoding='utf-8') as source_file:
            content = source_file.read()
        
        with open(destination, 'w', encoding='utf-8') as dest_file:
            dest_file.write(content)
        
        logging.info(f"File copied as-is: {filepath.name}")

    except Exception as e:
        logging.error(f"Failed to copy {filepath.name}: {e}")

# -------------------------------
# Main Chunking Function
# -------------------------------

def chunk_large_files():
    """Process all files in MD_DIR2 and chunk those larger than 20k tokens."""
    markdown_files = [f for f in MD_DIR2.iterdir() if f.suffix == '.md']

    logging.info("Starting chunking process for files larger than 20k tokens...")

    for filepath in markdown_files:
        try:
            # Read the file and count tokens
            with open(filepath, 'r', encoding='utf-8') as file:
                text = file.read()
                token_count = count_tokens(text)

            # Chunk files larger than 20k tokens
            if token_count > TOKEN_LIMIT:
                logging.info(f"File {filepath.name} exceeds 20k tokens. Token count: {token_count}")
                process_and_chunk_file(filepath, CHUNKED_DIR)
            else:
                logging.info(f"File {filepath.name} is under 20k tokens. Copying as-is.")
                copy_file(filepath, CHUNKED_DIR)
                
        except Exception as e:
            logging.error(f"Failed to process {filepath.name}: {e}")

    logging.info("Chunking process completed.")

# -------------------------------
# Main Execution
# -------------------------------

if __name__ == "__main__":
    chunk_large_files()
