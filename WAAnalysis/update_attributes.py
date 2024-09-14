import os
import yaml
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Directory containing the markdown files
MD_DIR = Path("chunked")

def update_file_timestamps(file_path):
    """
    Updates the file's created and last modified timestamps based on the frontmatter.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        if content.startswith('---'):
            frontmatter, body = content.split('---', 2)[1:]
            frontmatter_data = yaml.safe_load(frontmatter.strip())

            create_time = frontmatter_data.get('create_time')
            update_time = frontmatter_data.get('update_time')

            if create_time and update_time:
                # Convert string timestamps to datetime objects
                create_dt = datetime.fromisoformat(create_time)
                update_dt = datetime.fromisoformat(update_time)

                # Convert to epoch time
                create_epoch = create_dt.timestamp()
                update_epoch = update_dt.timestamp()

                # Update file timestamps
                os.utime(file_path, (create_epoch, update_epoch))

                logging.info(f"Updated timestamps for {file_path.name}: create_time={create_time}, update_time={update_time}")
            else:
                logging.warning(f"Missing create_time or update_time in frontmatter for {file_path.name}")
        else:
            logging.warning(f"No frontmatter found in {file_path.name}")

    except Exception as e:
        logging.error(f"Error processing {file_path.name}: {e}", exc_info=True)

def process_files_in_directory(directory):
    """
    Process all markdown files in the directory and update their timestamps.
    """
    for md_file in directory.glob("*.md"):
        update_file_timestamps(md_file)

if __name__ == "__main__":
    # Process all files in the specified directory
    process_files_in_directory(MD_DIR)
    logging.info("Timestamps update completed.")
