import logging
from WAAnalysis.batch_utils import check_batch_status, download_batch_results, update_markdown_from_results
from WAAnalysis.utils import load_json_file, save_to_json
from WAAnalysis.config import BATCH_OUTPUT_DIR, BATCH_TRACKING_FILE, ERROR_LOGS_DIRECTORY


# -------------------------------
# Setup Logging
# -------------------------------
log_file = ERROR_LOGS_DIRECTORY / "batch_results.log"

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)


# -------------------------------
# Update Job Completion
# -------------------------------
def update_job_completion(job_type, output_file):
    """Marks the job as completed and updates the output file path in the tracking file."""
    data = load_json_file(BATCH_TRACKING_FILE)
    
    for job in data["jobs"]:
        if job["job_type"] == job_type:
            job["completed"] = True
            job["output_file"] = str(output_file)
            break
    
    save_to_json(data, BATCH_TRACKING_FILE)


# -------------------------------
# Check and Download Batch Results
# -------------------------------
def check_and_download_results():
    """Checks the status of each job type in the tracking file and downloads results if the batch is completed."""
    data = load_json_file(BATCH_TRACKING_FILE)

    for job in data["jobs"]:
        if not job["completed"] and job["batch_id"]:
            # Check the batch status
            try:
                status = check_batch_status(job["batch_id"])
                logging.info(f"Checked status for batch {job['batch_id']}: {status}")

                if status == "completed":
                    # Download the results and save them in BATCH_OUTPUT_DIR
                    output_file = download_batch_results(job["batch_id"])
                    
                    # Update the markdown file with the results
                    update_markdown_from_results(job)  # Update markdown with the results
                    
                    # Update the tracking file with the completed status and result path
                    update_job_completion(job["job_type"], output_file)
                    logging.info(f"Batch {job['batch_id']} for {job['job_type']} completed and results saved to {output_file}")
                else:
                    logging.info(f"Batch {job['batch_id']} for {job['job_type']} is still {status}.")
            
            except Exception as e:
                logging.error(f"Error checking or downloading results for batch {job['batch_id']} ({job['job_type']}): {str(e)}")
        else:
            logging.info(f"Job for {job['job_type']} is already completed or has no batch_id.")


# -------------------------------
# Script Entry Point
# -------------------------------
if __name__ == "__main__":
    logging.info("Starting to check and download batch results.")
    check_and_download_results()
    logging.info("Finished checking and downloading batch results.")
