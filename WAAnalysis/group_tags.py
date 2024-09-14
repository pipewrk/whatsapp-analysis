import yaml
from collections import defaultdict
import logging
from pathlib import Path

# Setup logging
log = logging.getLogger(__name__)

# Load tags from YAML
def load_tags(yaml_file):
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    return data.get('tags', [])

# Group tags by core terms
def group_tags(tags):
    grouped_tags = defaultdict(list)
    
    for tag in tags:
        # Split by dash and isolate the core
        core_tag = tag.split('-')[0]
        grouped_tags[core_tag].append(tag)
    
    return grouped_tags

# Save grouped tags to YAML
def save_grouped_tags(grouped_tags, output_file):
    with open(output_file, 'w') as f:
        yaml.dump({'grouped_tags': dict(grouped_tags)}, f)
    log.info(f"Grouped tags saved to {output_file}")

# Main processing
def process_tags():
    yaml_file = Path('data/unique_tags.yaml')
    output_file = Path('data/grouped_tags.yaml')

    # Load tags
    tags = load_tags(yaml_file)
    log.info(f"Loaded {len(tags)} tags from {yaml_file}")
    
    # Group tags by core terms
    grouped_tags = group_tags(tags)
    
    # Save grouped tags
    save_grouped_tags(grouped_tags, output_file)

if __name__ == "__main__":
    log.info("Starting tag grouping process.")
    process_tags()
    log.info("Finished tag grouping.")
