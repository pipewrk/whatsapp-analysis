import yaml
import json
from pathlib import Path
from WAAnalysis.config import DATA_DIR

# -------------------------------
# Load Tags from YAML
# -------------------------------
def load_tags(yaml_file):
    """Load tags from the YAML file."""
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    return data.get('tags', [])

# -------------------------------
# Create JSONL Entry for Tag Clustering
# -------------------------------
def create_jsonl_entry(custom_id, tags, model="gpt-4o-mini", max_tokens=16384):
    """Create a JSONL entry for clustering all tags at once using LLM."""
    prompt = f"""
You are an expert at organizing information into meaningful categories. I will provide you with a list of tags, and your task is to organize them into clusters based on their themes or commonalities. Each cluster should have a descriptive name and contain a list of related tags.

Please format the output as a JSON object with the following structure:

{{
  "clusters": [
    {{
      "cluster_name": "Cluster 1 Name",
      "tags": ["tag1", "tag2", "tag3"]
    }},
    {{
      "cluster_name": "Cluster 2 Name",
      "tags": ["tag4", "tag5", "tag6"]
    }}
  ]
}}

Here is the list of tags:
- {", ".join(tags)}
"""

    # Construct the JSON body
    jsonl_entry = {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI assistant specialized in clustering information based on themes."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens
        }
    }
    
    return jsonl_entry

# -------------------------------
# Write to JSONL
# -------------------------------
def write_to_jsonl(output_file, entry):
    """Write the single entry to a JSONL file."""
    with open(output_file, 'w') as f:
        f.write(json.dumps(entry) + "\n")

# -------------------------------
# Main Process
# -------------------------------
def process_tags_to_single_jsonl():
    """Load tags, create a single JSONL entry, and save the result."""
    yaml_file = DATA_DIR / 'unique_tags.yaml'
    output_file = DATA_DIR / 'tags_cluster_request_single.jsonl'
    
    # Load all tags
    tags = load_tags(yaml_file)
    
    # Create a single JSONL entry
    custom_id = "tag-cluster-full"
    jsonl_entry = create_jsonl_entry(custom_id, tags, max_tokens=16384)  # Adjust max_tokens if needed

    # Write the entry to a JSONL file
    write_to_jsonl(output_file, jsonl_entry)
    print(f"JSONL file created at: {output_file}")

if __name__ == "__main__":
    process_tags_to_single_jsonl()
