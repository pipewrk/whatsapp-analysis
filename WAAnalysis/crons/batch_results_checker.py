from WAAnalysis.batch_utils import check_batch_status, download_batch_results, update_markdown_from_results
from WAAnalysis.utils import load_json_file, save_to_json
from WAAnalysis.config import BATCH_OUTPUT_DIR, BATCH_TRACKING_FILE


# -------------------------------
# Update Job Completion
# -------------------------------
def update_job_completion(file_name, job_type, output_file):
    """Marks the job as completed and updates the output file path in the tracking file."""
    data = load_json_file(BATCH_TRACKING_FILE)
    
    for job in data["jobs"]:
        if job["filename"] == file_name and job["job_type"] == job_type:
            job["completed"] = True
            job["output_file"] = str(output_file)
            break
    
    save_to_json(data, BATCH_TRACKING_FILE)


# -------------------------------
# Check and Download Batch Results
# -------------------------------
def check_and_download_results():
    """Checks the status of each job in the tracking file and downloads results if the batch is completed."""
    data = load_json_file(BATCH_TRACKING_FILE)

    for job in data["jobs"]:
        if not job["completed"] and job["batch_id"]:
            # Check the batch status
            status = check_batch_status(job["batch_id"])
            
            if status == "completed":
                # Download the results and save them in BATCH_OUTPUT_DIR
                output_file = download_batch_results(job["batch_id"])
                
                # Update the markdown file with the results
                update_markdown_from_results(job)  # <- Here is where the markdown is updated

                # Update the tracking file with the completed status and result path
                update_job_completion(job["filename"], job["job_type"], output_file)
            else:
                print(f"Batch {job['batch_id']} for {job['filename']} ({job['job_type']}) is still {status}.")


if __name__ == "__main__":
    check_and_download_results()
