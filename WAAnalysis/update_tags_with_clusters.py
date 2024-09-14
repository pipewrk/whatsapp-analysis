import logging
import json
import re
from pathlib import Path
from WAAnalysis.utils import load_markdown, update_markdown_frontmatter
from WAAnalysis.config import MD_DIR, BATCH_OUTPUT_DIR

# -------------------------------
# Setup Logging
# -------------------------------
log = logging.getLogger(__name__)

# -------------------------------
# Helper Functions
# -------------------------------
def slugify(text):
    """Convert text into a slug (URL-friendly string)."""
    return re.sub(r'[\W_]+', '-', text.lower()).strip('-')

def add_evidence_tag(tags):
    """Ensure the 'evidence' tag is included in the list of tags."""
    if 'evidence' not in tags:
        tags.append('evidence')

def map_existing_tags_to_clusters(existing_tags, clusters):
    """Map the existing tags in the markdown file to the clusters from the JSONL result."""
    new_tags = set(existing_tags)  # Use a set to avoid duplicates
    for cluster in clusters:
        for tag in cluster['tags']:
            if slugify(tag) in existing_tags:
                new_tags.add(slugify(cluster['cluster_name']))
    return list(new_tags)

def update_markdown_tags(file, clusters):
    """Update the markdown file's frontmatter tags with the cluster mappings."""
    frontmatter, body = load_markdown(file)
    
    # Get existing tags from frontmatter or initialize an empty list
    existing_tags = frontmatter.get('tags', [])

    # Add evidence tag
    add_evidence_tag(existing_tags)
    
    # Map existing tags to clusters and update tags
    updated_tags = map_existing_tags_to_clusters(existing_tags, clusters)
    frontmatter['tags'] = updated_tags

    # Update the markdown frontmatter with new tags
    update_markdown_frontmatter(file, frontmatter)
    log.info(f"Updated tags for {file}")

# -------------------------------
# Load Clustered Tags from JSONL
# -------------------------------
def load_clustered_tags(jsonl_file):
    """Load the clustered tags from the JSONL file, handling markdown."""
    clusters = []
    with open(jsonl_file, 'r') as f:
        for line in f:
            data = json.loads(line)
            response_content = data['response']['body']['choices'][0]['message']['content']

            # Remove Markdown code block markers (```json ... ```)
            json_content = re.sub(r'```json|```', '', response_content).strip()

            # Parse the JSON content
            try:
                cluster_data = json.loads(json_content)
                clusters.extend(cluster_data['clusters'])
            except json.JSONDecodeError as e:
                log.error(f"Failed to parse JSON content: {e}")
                continue
    
    return clusters

# -------------------------------
# Process Markdown Files to Update Tags with Clusters
# -------------------------------
def process_markdown_for_clusters():
    """Iterate over markdown files and update the 'tags' with clustered tags."""
    md_files = [f for f in MD_DIR.iterdir() if f.suffix == '.md']
    jsonl_file = BATCH_OUTPUT_DIR / 'clustered_tag_results.jsonl'

    # Load clustered tags from the JSONL file
    clusters = load_clustered_tags(jsonl_file)
    log.info(f"Loaded clusters from {jsonl_file}")

    # Process each markdown file
    for file in md_files:
        log.info(f"Processing file: {file}")
        update_markdown_tags(file, clusters)

if __name__ == "__main__":
    log.info("Starting process to update markdown tags with clusters.")
    process_markdown_for_clusters()
    log.info("Finished updating markdown tags.")
