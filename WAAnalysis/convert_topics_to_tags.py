import logging
import re
from WAAnalysis.utils import load_markdown, update_markdown_frontmatter
from WAAnalysis.config import MD_DIR

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

def convert_topics_to_tags(frontmatter):
    """Convert the 'topics' frontmatter field into sluggified 'tags'."""
    topics = frontmatter.get('topics', [])
    
    if topics:
        log.debug(f"Original topics: {topics}")
        tags = [slugify(topic) for topic in topics]
        frontmatter['tags'] = tags  # Rename topics to tags
        del frontmatter['topics']  # Remove old 'topics' field
        log.debug(f"Converted tags: {tags}")

    return frontmatter

# -------------------------------
# Process Markdown Files to Update Tags
# -------------------------------
def process_markdown_for_tags():
    """Iterate over markdown files and convert 'topics' to sluggified 'tags'."""
    md_files = [f for f in MD_DIR.iterdir() if f.suffix == '.md']

    for file in md_files:
        log.info(f"Processing file: {file}")
        frontmatter, body = load_markdown(file)

        # Convert topics to tags
        frontmatter = convert_topics_to_tags(frontmatter)

        # Update markdown frontmatter
        update_markdown_frontmatter(file, frontmatter)
        log.info(f"Updated topics to tags for {file}")

if __name__ == "__main__":
    log.info("Starting process to convert topics to tags.")
    process_markdown_for_tags()
    log.info("Finished converting topics to tags.")
