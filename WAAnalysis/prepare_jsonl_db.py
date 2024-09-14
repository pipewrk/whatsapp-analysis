import json
import jsonlines
import logging
from WAAnalysis.config import BATCH_OUTPUT_DIR, DATA_DIR

# File paths
WHATSAPP_MESSAGES_FILE = DATA_DIR / 'whatsapp_messages_by_day.json'
sentiment_results_path = BATCH_OUTPUT_DIR / 'sentiment_results.jsonl'
topics_results_path = BATCH_OUTPUT_DIR / 'topics_results.jsonl'
key_points_results_path = BATCH_OUTPUT_DIR / 'key_points_results.jsonl'
entities_results_path = BATCH_OUTPUT_DIR / 'entities_results.jsonl'
OUTPUT_FILE = DATA_DIR / 'messages.jsonl'


# Function to load a jsonl file into a dictionary with custom_id as keys
def load_jsonl_to_dict(file_path, file_type):
    data_dict = {}
    try:
        with jsonlines.open(file_path) as reader:
            for obj in reader:
                custom_id = obj['custom_id']
                data_dict[custom_id] = obj['response']['body']['choices'][0]['message']['content']
        logging.info(f"{file_type} results loaded successfully.")
    except Exception as e:
        logging.error(f"Failed to load {file_type} results from {file_path}: {e}")
    return data_dict


# Function to process WhatsApp messages
def process_whatsapp_messages():
    try:
        # Load all batch results
        logging.info("Loading batch results...")
        sentiment_data = load_jsonl_to_dict(sentiment_results_path, "Sentiment")
        topics_data = load_jsonl_to_dict(topics_results_path, "Topics")
        key_points_data = load_jsonl_to_dict(key_points_results_path, "Key Points")
        entities_data = load_jsonl_to_dict(entities_results_path, "Entities")
        
        # Process WhatsApp messages
        logging.info("Processing WhatsApp messages...")
        with open(WHATSAPP_MESSAGES_FILE, 'r') as file:
            whatsapp_data = json.load(file)
        logging.info(f"Loaded WhatsApp messages from {WHATSAPP_MESSAGES_FILE}")

        # Open the output file for writing
        with jsonlines.open(OUTPUT_FILE, mode='w') as writer:
            for day, messages in whatsapp_data.items():
                output_object = {
                    'id': day,
                    'sentiment': sentiment_data.get(day, {}),
                    'topics': topics_data.get(day, {}),
                    'summary': key_points_data.get(day, {}),
                    'entity_relationships': entities_data.get(day, {}),
                    'messages': messages
                }
                writer.write(output_object)
                logging.debug(f"Processed data for {day}")

        logging.info(f"Processed messages saved to {OUTPUT_FILE}")

    except Exception as e:
        logging.error(f"An error occurred while processing WhatsApp messages: {e}")


if __name__ == "__main__":
    # Start the processing
    logging.info("Starting the message processing script...")
    process_whatsapp_messages()
    logging.info("Script execution completed.")
