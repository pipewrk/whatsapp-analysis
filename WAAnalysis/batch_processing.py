import json
import logging
from WAAnalysis.config import BATCH_INPUT_DIR, BATCH_TRACKING_FILE, MD_DIR, ERROR_LOGS_DIRECTORY, DEBUG, MANUAL_TESTING
from WAAnalysis.batch_utils import generate_batch_input, upload_batch_file, create_batch, cancel_batch
from WAAnalysis.utils import ensure_directories_exist, read_file_content, save_to_json


# -------------------------------
# Load and Save Tracking File
# -------------------------------

def load_tracking_file():
    """Loads the tracking file if it exists, otherwise returns an empty structure."""
    if BATCH_TRACKING_FILE.exists():
        return read_file_content(BATCH_TRACKING_FILE)
    return {"jobs": []}


def save_tracking_file(data):
    """Saves the updated tracking data to the tracking file."""
    save_to_json(data, BATCH_TRACKING_FILE)


# -------------------------------
# Update Tracking File
# -------------------------------

def update_tracking_file(file_name, job_type, batch_id):
    """Updates the tracking file with new batch job information."""
    data = load_tracking_file()
    
    # Check if the job already exists and update it
    for job in data["jobs"]:
        if job["filename"] == file_name and job["job_type"] == job_type:
            job.update({
                "batch_id": batch_id,
                "completed": False,
                "output_file": None
            })
            break
    else:
        # If the job doesn't exist, create a new one
        data["jobs"].append({
            "filename": file_name,
            "job_type": job_type,
            "batch_id": batch_id,
            "completed": False,
            "output_file": None
        })
    
    save_tracking_file(data)


# -------------------------------
# Rollback on Error
# -------------------------------

def rollback_on_error(batch_id, job_type, file_name, error_message):
    """Cancels the batch job and logs the error in the console and error log."""
    logging.error(f"Error processing {job_type} for {file_name}: {error_message}")
    
    if batch_id:
        logging.info(f"Cancelling batch job {batch_id} for {file_name} ({job_type})...")
        if not MANUAL_TESTING:
            cancel_batch(batch_id)
            logging.info(f"Batch job {batch_id} for {file_name} ({job_type}) cancelled.")

    # Log the error in a separate error file for the job
    with open(ERROR_LOGS_DIRECTORY / f"{file_name}_{job_type}_error.log", "a") as error_log:
        error_log.write(f"Error processing {job_type} for {file_name}:\n{error_message}\n\n")


# -------------------------------
# Main Batch Processing Function
# -------------------------------

def process_markdown_files():
    """Processes markdown files for each job type and generates batch requests."""
    try:
        md_files = [f for f in MD_DIR.iterdir() if f.suffix == '.md']
        total_files = len(md_files)
        job_types = ["topics", "entities", "sentiment", "key_points"]

        # Ensure batch input directories exist
        ensure_directories_exist([BATCH_INPUT_DIR / job for job in job_types])

        logging.info(f"Found {total_files} markdown files. Starting batch processing...")

        for i, file in enumerate(md_files, start=1):
            file_name = file.name
            logging.info(f"Processing file {i}/{total_files}: {file_name}")

            for job_type in job_types:
                try:
                    logging.info(f"Generating batch input for {job_type} ({file_name})...")
                    # Step 1: Generate the batch input
                    jsonl_input = generate_batch_input(file_name, job_type)

                    # Step 2: Write the .jsonl file
                    batch_file = BATCH_INPUT_DIR / job_type / f"{file_name}_{job_type}.jsonl"
                    save_to_json(jsonl_input, batch_file)
                    logging.info(f"Batch input file written: {batch_file}")

                    # Step 3: Upload the batch input file and create the batch
                    if MANUAL_TESTING:
                        logging.info(f"Skipping upload and batch creation due to MANUAL_TESTING mode for {job_type} ({file_name})")
                    else:
                        logging.info(f"Uploading batch input for {job_type} ({file_name})...")
                        file_id = upload_batch_file(batch_file)
                        batch = create_batch(file_id, f"{file_name}_{job_type}_Batch")
                        logging.info(f"Batch created with ID: {batch['id']}")

                        # Step 4: Update the tracking file with batch_id and job details
                        update_tracking_file(file_name, job_type, batch['id'])
                        logging.info(f"Tracking file updated for {job_type} ({file_name}).")

                except Exception as e:
                    # Rollback the batch and log error if something goes wrong
                    batch_id = batch.get('id') if 'batch' in locals() else None
                    rollback_on_error(batch_id, job_type, file_name, str(e))
                    return  # Stop further processing after rollback

    except Exception as e:
        logging.error(f"Failed to process markdown files: {str(e)}")


if __name__ == "__main__":
    if DEBUG:
        logging.info("Running in DEBUG mode.")
    
    process_markdown_files()
