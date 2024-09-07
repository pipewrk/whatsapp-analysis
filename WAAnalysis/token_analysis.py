import os
import tiktoken
import json

# Directory where markdown files are stored
markdown_dir = "./markdown"

# Define token ranges
token_ranges = {
    "0-500": {"min": 0, "max": 500, "count": 0, "total_tokens": 0},
    "501-1000": {"min": 501, "max": 1000, "count": 0, "total_tokens": 0},
    "1001-2000": {"min": 1001, "max": 2000, "count": 0, "total_tokens": 0},
    "2001+": {"min": 2001, "max": float('inf'), "count": 0, "total_tokens": 0, "documents": []},  # Track documents over 2000 tokens
}

# Initialise tokenizer (use appropriate encoding like cl100k_base)
tokenizer = tiktoken.get_encoding("cl100k_base")

# Function to count tokens in a markdown file
def count_tokens(text):
    tokens = tokenizer.encode(text)
    return len(tokens)

# List to store token counts
token_counts = []

# Iterate through markdown files
for filename in os.listdir(markdown_dir):
    if filename.endswith(".md"):
        filepath = os.path.join(markdown_dir, filename)
        
        with open(filepath, 'r') as file:
            text = file.read()
            token_count = count_tokens(text)
            token_counts.append({"filename": filename, "token_count": token_count})

            # Classify into token ranges and update total tokens
            for token_range, limits in token_ranges.items():
                if limits["min"] <= token_count <= limits["max"]:
                    token_ranges[token_range]["count"] += 1
                    # For ranges up to 2000 tokens, assume maximum tokens for cost calculation
                    token_ranges[token_range]["total_tokens"] += limits["max"]
                    break
                elif token_count > 2000:
                    token_ranges["2001+"]["count"] += 1
                    token_ranges["2001+"]["total_tokens"] += token_count
                    token_ranges["2001+"]["documents"].append({
                        "filename": filename,
                        "token_count": token_count
                    })
                    break

# Calculate the total number of documents
total_documents = len(token_counts)

# Calculate percentages for each token range
for token_range, limits in token_ranges.items():
    count = limits["count"]
    percentage = (count / total_documents) * 100
    token_ranges[token_range]["percentage"] = percentage

# Calculate the total tokens across all ranges
total_tokens_all_ranges = sum(limits["total_tokens"] for limits in token_ranges.values())

# Print the analysis results
print(f"Total documents: {total_documents}")
for token_range, data in token_ranges.items():
    print(f"Range {token_range}: {data['count']} documents ({data['percentage']:.2f}%), Total tokens: {data['total_tokens']}")

# Print total token count
print(f"\nTotal tokens across all documents: {total_tokens_all_ranges}")

# Print details for documents exceeding 2000 tokens
if token_ranges["2001+"]["documents"]:
    print("\nDocuments exceeding 2000 tokens:")
    for doc in token_ranges["2001+"]["documents"]:
        print(f"- {doc['filename']}: {doc['token_count']} tokens")

# Optionally, save the analysis to a JSON file
with open('token_size_analysis.json', 'w') as f:
    json.dump(token_ranges, f, indent=4)
