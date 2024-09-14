import os
import tiktoken
import json
import logging
from pathlib import Path
import frontmatter
# from WAAnalysis.config import MD_DIR, ERROR_LOGS_DIRECTORY
from WAAnalysis.config import MD_DIR2, ERROR_LOGS_DIRECTORY
from WAAnalysis.utils import ensure_directories_exist

# -------------------------------
# Setup Logging
# -------------------------------
log_file = ERROR_LOGS_DIRECTORY / "frontmatter_token_analysis.log"
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
# Token Analysis Configurations
# -------------------------------

# Define token ranges for frontmatter
token_ranges = {
    "0-500": {"min": 0, "max": 500, "count": 0, "total_tokens": 0},
    "501-1000": {"min": 501, "max": 1000, "count": 0, "total_tokens": 0},
    "1001-2000": {"min": 1001, "max": 2000, "count": 0, "total_tokens": 0},
    "2001+": {"min": 2001, "max": float('inf'), "count": 0, "total_tokens": 0, "documents": []},
}

# Initialize tokenizer (use appropriate encoding)
tokenizer = tiktoken.get_encoding("cl100k_base")

# -------------------------------
# Token Counting Functions
# -------------------------------

def count_tokens(text):
    """Count tokens in a given text using the tokenizer."""
    tokens = tokenizer.encode(text)
    return len(tokens)

# -------------------------------
# Main Token Analysis
# -------------------------------

def analyze_tokens_in_frontmatter():
    """Analyze token counts in the frontmatter of markdown files and classify them into ranges."""
    token_counts = []
    markdown_files = [f for f in MD_DIR2.iterdir() if f.suffix == '.md']
    
    # Variables to track the maximum token size and corresponding file
    max_token_count = 0
    max_token_file = None

    total_files = len(markdown_files)
    logging.info(f"Found {total_files} markdown files for frontmatter token analysis.")

    for i, filepath in enumerate(markdown_files, start=1):
        filename = filepath.name
        logging.info(f"Processing file {i}/{total_files}: {filename}")

        try:
            # Load the frontmatter using the frontmatter library
            with open(filepath, 'r', encoding='utf-8') as file:
                file_data = frontmatter.load(file)
            
            # Extract the frontmatter as a string
            frontmatter_content = json.dumps(file_data.metadata)
            
            # Count tokens in the frontmatter
            token_count = count_tokens(frontmatter_content)
            token_counts.append({"filename": filename, "token_count": token_count})

            # Check if this file has the max token count
            if token_count > max_token_count:
                max_token_count = token_count
                max_token_file = filename

            # Classify into token ranges and update totals
            for token_range, limits in token_ranges.items():
                if limits["min"] <= token_count <= limits["max"]:
                    token_ranges[token_range]["count"] += 1
                    token_ranges[token_range]["total_tokens"] += token_count
                    break
                elif token_count > 2000:
                    token_ranges["2001+"]["count"] += 1
                    token_ranges["2001+"]["total_tokens"] += token_count
                    token_ranges["2001+"]["documents"].append({
                        "filename": filename,
                        "token_count": token_count
                    })
                    break
        except Exception as e:
            logging.error(f"Failed to process {filename}: {e}")

    total_documents = len(token_counts)
    logging.info(f"Processed {total_documents} documents in total.")

    # Calculate percentages for each token range
    for token_range, limits in token_ranges.items():
        count = limits["count"]
        percentage = (count / total_documents) * 100 if total_documents else 0
        token_ranges[token_range]["percentage"] = percentage

    # Calculate total tokens across all ranges
    total_tokens_all_ranges = sum(limits["total_tokens"] for limits in token_ranges.values())
    logging.info(f"Total tokens across all frontmatters: {total_tokens_all_ranges}")

    # Log results of token analysis
    for token_range, data in token_ranges.items():
        logging.info(f"Range {token_range}: {data['count']} documents ({data['percentage']:.2f}%), "
                     f"Total tokens: {data['total_tokens']}")

    # Log details for documents exceeding 2000 tokens
    if token_ranges["2001+"]["documents"]:
        logging.info("\nDocuments exceeding 2000 tokens:")
        for doc in token_ranges["2001+"]["documents"]:
            logging.info(f"- {doc['filename']}: {doc['token_count']} tokens")

    # Log the file with the maximum token count
    logging.info(f"File with the maximum frontmatter token count: {max_token_file} ({max_token_count} tokens)")

    # Save the analysis to a JSON file
    output_file = Path(ERROR_LOGS_DIRECTORY) / 'frontmatter_token_size_analysis.json'
    save_token_analysis(output_file)

    return total_documents, total_tokens_all_ranges, max_token_count, max_token_file

# -------------------------------
# Save Analysis to JSON
# -------------------------------

def save_token_analysis(output_file):
    """Save the token analysis results to a JSON file."""
    try:
        with open(output_file, 'w') as f:
            json.dump(token_ranges, f, indent=4)
        logging.info(f"Token analysis results saved to {output_file}")
    except Exception as e:
        logging.error(f"Failed to save token analysis to {output_file}: {e}")


# -------------------------------
# Main Execution
# -------------------------------

if __name__ == "__main__":
    total_documents, total_tokens_all_ranges, max_token_count, max_token_file = analyze_tokens_in_frontmatter()
    logging.info(f"Max token count: {max_token_count} in file: {max_token_file}")
