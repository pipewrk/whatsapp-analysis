import json
import os
from pathlib import Path
from WAAnalysis.config import WHATSAPP_MESSAGES_FILE, OUTPUT_DIR
from WAAnalysis.utils import generate_markdown_for_day

# Load conversation data from the JSON file
def load_conversation_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Save markdown to a file
def save_markdown(file_name, markdown_content):
    with open(file_name, "w") as file:
        file.write(markdown_content)

def main():
    # Ensure output directory exists
    output_dir = Path(OUTPUT_DIR)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    # Load conversation data
    conversation_data = load_conversation_data(WHATSAPP_MESSAGES_FILE)

    # Generate and save markdown for each day
    for day, messages in conversation_data.items():
        markdown_content = generate_markdown_for_day(day, messages)
        file_name = output_dir / f"{day}.md"
        save_markdown(file_name, markdown_content)
        print(f"Markdown for {day} written to {file_name}")