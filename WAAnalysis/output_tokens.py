import os
import json
import tiktoken

# Load JSON files
json_files = [
    "./2024-03-09.json",
    "./2024-03-08.json",
    "./2018-04-14.json"
]

# Initialize tokenizer
tokenizer = tiktoken.get_encoding("cl100k_base")  # Using cl100k_base for tokenization

# Function to compute token size for each JSON document
def compute_token_size(file_path):
    with open(file_path, "r") as f:
        content = json.load(f)
    json_str = json.dumps(content)
    tokens = tokenizer.encode(json_str)
    return len(tokens)

# Compute token sizes for each JSON file
token_sizes = {os.path.basename(file_path): compute_token_size(file_path) for file_path in json_files}

print (token_sizes)
