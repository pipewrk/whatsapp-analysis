import os
import json
import tiktoken
import logging
from pathlib import Path
from WAAnalysis.config import DATA_DIR, ERROR_LOGS_DIRECTORY
from WAAnalysis.utils import ensure_directories_exist

# -------------------------------
# Setup Logging
# -------------------------------
log_file = ERROR_LOGS_DIRECTORY / "token_size_analysis.log"
ensure_directories_exist([ERROR_LOGS_DIRECTORY])

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

logging.getLogger().addHandler(console_handler)

# -------------------------------
# Tokenization Setup
# -------------------------------

# Initialize tokenizer using cl100k_base (modify this if needed)
tokenizer = tiktoken.get_encoding("cl100k_base")

# List of JSON files (adjust paths relative to DATA_DIR)
json_files = [
    DATA_DIR / "2024-03-09.json",
    DATA_DIR / "2024-03-08.json",
    DATA_DIR / "2018-04-14.json"
]

# -------------------------------
# Function to Compute Token Size
# -------------------------------

def compute_token_size(file_path):
    """Compute the token size for a given JSON file."""
    try:
        with open(file_path, "r") as f:
            content = json.load(f)
        json_str = json.dumps(content)
        tokens = tokenizer.encode(json_str)
        token_count = len(tokens)
        logging.info(f"Token count for {file_path.name}: {token_count}")
        return token_count
    except Exception as e:
        logging.error(f"Error processing {file_path.name}: {str(e)}")
        return 0

# -------------------------------
# Main Execution
# -------------------------------

if __name__ == "__main__":
    # Compute token sizes for each JSON file
    token_sizes = {file_path.name: compute_token_size(file_path) for file_path in json_files}
    
    # Log and display the token sizes
    logging.info(f"Token sizes: {token_sizes}")
    print(token_sizes)
