import re
import logging
from WAAnalysis.config import PROJECT_ROOT

# Define the directory containing the markdown files
MARKDOWN_DIR = PROJECT_ROOT / "./chunked"

log = logging.getLogger(__name__)

def find_summary_sections(content):
    """
    Find all sections of the content that start with ## Summary and their positions.
    """
    pattern = re.compile(r'^## Summary', re.MULTILINE)
    matches = [(m.start(), m.end()) for m in pattern.finditer(content)]
    return matches

def clean_markdown_file(file_path):
    """
    Cleans a markdown file by identifying multiple ## Summary sections,
    comparing content between them, and removing duplicates if applicable.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Find the positions of all "## Summary" sections
        summary_positions = find_summary_sections(content)

        if len(summary_positions) < 2:
            # Skip files with fewer than 2 summary sections
            # log.info(f"File '{file_path.name}' has less than 2 '## Summary'. Skipping.")
            return False  # Indicate no changes were made

        # Extract the content between each "## Summary" section
        summaries = []
        for i in range(len(summary_positions) - 1):
            start = summary_positions[i][1]  # End of the current summary header
            end = summary_positions[i + 1][0]  # Start of the next summary header
            summaries.append(content[start:end].strip())

        # Add the last summary chunk from the last "## Summary" to the end of the file
        summaries.append(content[summary_positions[-1][1]:].strip())

        # Compare the smaller chunk with the larger chunk to find duplicates
        cleaned_summaries = []
        for i in range(len(summaries)):
            smaller_chunk = summaries[i]
            if i + 1 < len(summaries):
                larger_chunk = summaries[i + 1]
                if smaller_chunk in larger_chunk:
                    log.info(f"Duplicate summary found in file '{file_path.name}'. Removing smaller chunk.")
                    continue  # Skip the smaller duplicate chunk
            cleaned_summaries.append(smaller_chunk)

        # Rebuild the content with the cleaned summaries
        new_content = content[:summary_positions[0][0]]  # Content before the first summary
        for summary in cleaned_summaries:
            new_content += "## Summary\n" + summary + "\n"

        # Save the cleaned content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)

        log.info(f"Cleaned: {file_path}")
        return True  # Indicate changes were made

    except Exception as e:
        log.error(f"Failed to clean {file_path}: {e}")
        return False

def clean_all_markdown_files(directory):
    """
    Cleans all markdown files in the specified directory by removing duplicate summaries.
    """
    total_cleaned = 0
    for file_path in directory.glob("*.md"):
        if clean_markdown_file(file_path):
            total_cleaned += 1
    log.info(f"Total cleaned files: {total_cleaned}")

if __name__ == "__main__":
    # Clean all markdown files in the specified directory
    clean_all_markdown_files(MARKDOWN_DIR)
