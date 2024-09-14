import re
import yaml
import logging
from pathlib import Path
from WAAnalysis.config import PROJECT_ROOT

# Define the directory containing the markdown files
MARKDOWN_DIR = PROJECT_ROOT / "./chunked"

log = logging.getLogger(__name__)

def sanitize_yaml_field(field):
    """
    Sanitize a YAML field by escaping problematic characters like quotes.
    Specifically handles cases like title: "Define the word "yeet"".
    """
    # Replace unescaped double quotes within the value with escaped quotes
    field = re.sub(r'(?<!\\)"', r'\"', field)
    return field

def extract_and_sanitize_frontmatter(content):
    """
    Extract YAML frontmatter, attempt to parse it, and sanitize if necessary.
    """
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        try:
            # Try to parse the frontmatter as YAML
            yaml.safe_load(frontmatter)
            return frontmatter, content[len(frontmatter_match.group(0)):].strip(), False
        except yaml.YAMLError as e:
            log.warning(f"YAML parsing failed: {e}. Attempting to sanitize.")
            # Sanitize the frontmatter by escaping problematic characters
            sanitized_frontmatter = sanitize_yaml_field(frontmatter)
            try:
                # Try to parse again after sanitizing
                yaml.safe_load(sanitized_frontmatter)
                log.info("YAML parsing succeeded after sanitizing.")
                return sanitized_frontmatter, content[len(frontmatter_match.group(0)):].strip(), True
            except yaml.YAMLError as e:
                log.error(f"YAML parsing failed even after sanitizing: {e}")
                return None, None, False
    return None, content, False

def process_markdown_file(file_path):
    """
    Process a markdown file by sanitizing its YAML frontmatter if necessary.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        frontmatter, body, updated = extract_and_sanitize_frontmatter(content)
        
        if frontmatter is None:
            # No frontmatter found, or failed parsing, skip file
            log.info(f"No valid YAML frontmatter found in '{file_path.name}'. Skipping.")
            return False

        # Rebuild the file content with sanitized frontmatter
        new_content = f"---\n{frontmatter}\n---\n\n{body}"

        # Write the updated content back to the file if changes were made
        if updated:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            log.info(f"Updated and sanitized: {file_path}")
            return True

        return False

    except Exception as e:
        log.error(f"Failed to process {file_path}: {e}")
        return False

def process_all_markdown_files(directory):
    """
    Process all markdown files in the specified directory by sanitizing their YAML frontmatter.
    """
    total_updated = 0
    for file_path in directory.glob("*.md"):
        if process_markdown_file(file_path):
            total_updated += 1
    log.info(f"Total updated files: {total_updated}")

if __name__ == "__main__":
    # Process all markdown files in the specified directory
    process_all_markdown_files(MARKDOWN_DIR)
