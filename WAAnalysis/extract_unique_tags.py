import logging
import yaml
from pathlib import Path
from WAAnalysis.utils import load_markdown
from WAAnalysis.config import MD_DIR, DATA_DIR

# -------------------------------
# Setup Logging
# -------------------------------
log = logging.getLogger(__name__)

# -------------------------------
# Function to Collect Unique Tags
# -------------------------------
def collect_unique_tags():
    """Collect all unique tags from markdown files and return a sorted list."""
    unique_tags = set()  # Use a set to avoid duplicates

    md_files = [f for f in MD_DIR.iterdir() if f.suffix == '.md']

    for file in md_files:
        log.info(f"Processing file: {file}")
        frontmatter, _ = load_markdown(file)

        tags = frontmatter.get('tags', [])
        if tags:
            log.debug(f"Found tags in {file}: {tags}")
            unique_tags.update(tags)

    log.info(f"Collected {len(unique_tags)} unique tags.")
    return sorted(unique_tags)

# -------------------------------
# Save Tags to YAML
# -------------------------------
def save_tags_to_yaml(tags, output_file):
    """Save the collected tags to a YAML file."""
    with open(output_file, 'w') as f:
        yaml.dump({'tags': tags}, f)
    log.info(f"Saved unique tags to {output_file}")

# -------------------------------
# Main Process for Extracting and Saving Tags
# -------------------------------
def process_unique_tags():
    """Extract unique tags and save them into a YAML file."""
    log.info("Starting tag extraction process.")
    unique_tags = collect_unique_tags()

    # Define output YAML file path
    output_file = DATA_DIR / 'unique_tags.yaml'

    # Save unique tags to YAML
    save_tags_to_yaml(unique_tags, output_file)

if __name__ == "__main__":
    log.info("Starting process to extract and save unique tags.")
    process_unique_tags()
    log.info("Finished extracting and saving unique tags.")
