import os
import re
import yaml
from WAAnalysis.prompts import summarize_text_with_ollama
from WAAnalysis.config import CHUNKED_DIR, SUMMARY_DIR, SUMMARY_MODEL, SUMMARY_LENGTH

# Ensure the output directory exists
os.makedirs(SUMMARY_DIR, exist_ok=True)

# Function to clean up existing YAML frontmatter from a markdown file
def remove_existing_frontmatter(text):
    """
    Removes existing YAML frontmatter from the markdown text.
    """
    if text.startswith("---"):
        # Find the position of the second "---" to remove the frontmatter
        end = text.find('---', 3)  # Start searching after the first '---'
        if end != -1:
            return text[end + 3:].strip()  # Return the content after the second '---'
    return text

# Function to clean up the model's response (special characters only)
def clean_summary(summary):
    """
    Cleans the generated summary by removing special characters or formatting issues.
    """
    # Remove unwanted line breaks or excessive whitespace
    cleaned_summary = re.sub(r'\\n+', '\n', summary)  # Remove escape sequences for newlines
    cleaned_summary = re.sub(r' +', ' ', cleaned_summary)  # Remove extra spaces

    # Additional cleanup can be added if needed for special characters
    return cleaned_summary.strip()

# Function to add the generated summary to the YAML frontmatter
def add_summary_to_chunk(chunk_file, summary, is_first_chunk=False):
    """
    Adds the generated summary as YAML frontmatter to the given markdown chunk file.
    If it's the first chunk, label it as 'Summary of the current chunk'. For subsequent chunks,
    label it as 'Summary of the conversation so far.'
    """
    with open(chunk_file, 'r', encoding='utf-8') as file:
        content = file.read()

    # Remove any existing frontmatter before summarizing the text
    content_without_frontmatter = remove_existing_frontmatter(content)

    # Clean the summary
    cleaned_summary = clean_summary(summary)

    # Prepare YAML frontmatter with the summary
    summary_label = "Summary of the current chunk" if is_first_chunk else "Summary of the conversation so far"
    frontmatter = {
        'summary': f"{summary_label}:\n{cleaned_summary}"
    }
    yaml_frontmatter = yaml.dump(frontmatter)

    # Combine new YAML frontmatter and the chunk content
    combined_content = f"---\n{yaml_frontmatter}---\n{content_without_frontmatter}"

    # Write the combined content to a new file in the SUMMARY_DIR
    output_file = SUMMARY_DIR / chunk_file.name
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(combined_content)

# Function to process all chunked files
def process_chunks_for_summaries():
    """
    Process all chunked files by summarizing the previous chunk and adding YAML frontmatter.
    For the first file, it summarizes itself.
    """
    # Get all chunk files in order
    chunked_files = sorted(CHUNKED_DIR.glob("*.md"))

    for i, chunk_file in enumerate(chunked_files):
        print(f"Processing chunk: {chunk_file.name}")

        # For the first chunk, summarize its own content
        if i == 0:
            with open(chunk_file, 'r', encoding='utf-8') as file:
                first_chunk_content = file.read()
            # Remove existing YAML frontmatter
            first_chunk_content = remove_existing_frontmatter(first_chunk_content)
            summary = summarize_text_with_ollama(first_chunk_content, SUMMARY_MODEL)
            add_summary_to_chunk(chunk_file, summary, is_first_chunk=True)
            print(f"Generated self-summary for {chunk_file.name}: {summary}")
            continue

        # Get the content of the previous chunk for summarization
        previous_chunk_file = chunked_files[i - 1]
        with open(previous_chunk_file, 'r', encoding='utf-8') as file:
            previous_content = file.read()
        # Remove existing YAML frontmatter
        previous_content = remove_existing_frontmatter(previous_content)

        # Summarize the previous chunk
        summary = summarize_text_with_ollama(previous_content, SUMMARY_MODEL)
        print(f"Generated summary for {chunk_file.name}: {summary}")

        # Add the summary as YAML frontmatter to the current chunk
        add_summary_to_chunk(chunk_file, summary)

# Main execution
if __name__ == "__main__":
    process_chunks_for_summaries()
    print(f"Processing completed. Summarized files are saved in: {SUMMARY_DIR}")