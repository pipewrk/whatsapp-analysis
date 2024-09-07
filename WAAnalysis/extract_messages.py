import sqlite3
import json
import pandas as pd
import logging
from WAAnalysis.config import PARTICIPANT_JID, DATABASE_PATH, BLOB_INFO_DIRECTORY, ERROR_LOGS_DIRECTORY, WHATSAPP_MESSAGES_FILE
from WAAnalysis.utils import (
    ensure_directories_exist,
    decode_with_protoc,
    fetch_replied_message,
    convert_core_data_timestamp,
    calculate_time_to_read,
    save_to_json,
)
from pathlib import Path

# -------------------------------
# Setup Logging
# -------------------------------
log = logging.getLogger(__name__)

# Ensure necessary directories exist
ensure_directories_exist([BLOB_INFO_DIRECTORY, ERROR_LOGS_DIRECTORY])

# -------------------------------
# Database Connection
# -------------------------------

def connect_to_db(db_path):
    """Connect to the SQLite database."""
    try:
        conn = sqlite3.connect(db_path)
        log.info(f"Connected to the database at {db_path}")
        return conn
    except sqlite3.Error as e:
        log.error(f"Failed to connect to database: {e}")
        raise

# -------------------------------
# Fetch Messages Query
# -------------------------------

def fetch_messages(cursor, participant_jid):
    """Fetch messages for the specified participant JID."""
    query = '''
    SELECT 
        ZWAMESSAGE.ZTEXT AS Message,
        ZWAMESSAGE.ZMESSAGEDATE AS MessageDateRaw,
        ZWAMESSAGE.ZSENTDATE AS SentTimeRaw,
        ZWAMESSAGE.ZFROMJID AS FromJID,
        ZWAMESSAGE.ZTOJID AS ToJID,
        ZWAMESSAGE.ZMEDIAITEM AS MediaItemID,
        ZWAMESSAGEINFO.ZRECEIPTINFO AS ReceiptInfoBlob,
        ZWAMESSAGE.Z_PK AS MessageID,
        ZWAMESSAGE.ZPARENTMESSAGE AS RepliedToMessageID,
        ZWAMEDIAITEM.ZMEDIALOCALPATH AS MediaPath
    FROM 
        ZWAMESSAGE
    LEFT JOIN 
        ZWAMESSAGEINFO ON ZWAMESSAGE.Z_PK = ZWAMESSAGEINFO.ZMESSAGE
    LEFT JOIN
        ZWAMEDIAITEM ON ZWAMESSAGE.ZMEDIAITEM = ZWAMEDIAITEM.Z_PK
    WHERE 
        ZWAMESSAGE.ZFROMJID = ? OR ZWAMESSAGE.ZTOJID = ?
    ORDER BY 
        ZWAMESSAGE.ZSENTDATE ASC
    '''
    cursor.execute(query, (participant_jid, participant_jid))
    messages = cursor.fetchall()
    log.info(f"Fetched {len(messages)} messages for participant {participant_jid}")
    return messages

# -------------------------------
# Process Messages
# -------------------------------

def process_messages(messages, cursor):
    """Process messages to include media, replied-to messages, and decode BLOBs."""
    data = []
    for idx, row in enumerate(messages):
        message = {
            'Message': row[0],
            'MessageDate': convert_core_data_timestamp(row[1]),
            'SentTime': convert_core_data_timestamp(row[2]),
            'FromJID': row[3],
            'ToJID': row[4],
            'MediaItemID': row[5],
            'MediaPath': row[9],
            'MessageID': row[7],
            'RepliedToMessageID': row[8]
        }

        # Fetch replied-to message if available
        if row[8]:
            replied_message = fetch_replied_message(cursor, row[8])
            if replied_message:
                message['RepliedToMessage'] = {
                    'Text': replied_message[0],
                    'MessageDate': convert_core_data_timestamp(replied_message[1]),
                    'SentTime': convert_core_data_timestamp(replied_message[2]),
                    'FromJID': replied_message[3],
                    'ToJID': replied_message[4]
                }

        # Decode BLOB if available
        if row[6]:
            decoded_output = decode_with_protoc(row[6], row[7], BLOB_INFO_DIRECTORY, ERROR_LOGS_DIRECTORY)
            if decoded_output:
                message['DecodedReceiptInfo'] = decoded_output
                # Extract received and read timestamps from protobuf fields 3 and 4
                timestamp_received, timestamp_read = extract_protobuf_timestamps(decoded_output)
                if timestamp_received:
                    message['ReceivedTimestamp'] = timestamp_received
                if timestamp_read:
                    message['ReadTimestamp'] = timestamp_read
                if timestamp_received and timestamp_read:
                    message['TimeToRead'] = calculate_time_to_read(timestamp_received, timestamp_read)

        data.append(message)
        log.debug(f"Processed message {idx + 1}/{len(messages)}")

    return data

# -------------------------------
# Protobuf Timestamp Extraction
# -------------------------------

def extract_protobuf_timestamps(decoded_output):
    """
    Extract received (field 3) and read (field 4) timestamps from the protobuf output.
    If only one timestamp is available (due to privacy settings), handle it gracefully.
    """
    try:
        timestamp_received = None
        timestamp_read = None

        for line in decoded_output.splitlines():
            # Look for field 3: received timestamp
            if line.strip().startswith("3:"):
                timestamp_received = int(line.split(":")[1].strip())
            # Look for field 4: read timestamp
            elif line.strip().startswith("4:"):
                timestamp_read = int(line.split(":")[1].strip())

        return timestamp_received, timestamp_read

    except Exception as e:
        log.error(f"Error extracting protobuf timestamps: {e}")
        return None, None

# -------------------------------
# Save Messages to JSON
# -------------------------------

def save_messages_to_json(grouped_by_day, output_file=WHATSAPP_MESSAGES_FILE):
    """Save processed messages grouped by day to a JSON file."""
    save_to_json(grouped_by_day, output_file)
    log.info(f"Messages saved to {output_file}")

# -------------------------------
# Main Function
# -------------------------------

def main(db_path, participant_jid, output_file=WHATSAPP_MESSAGES_FILE):
    """Main function to orchestrate message fetching and processing."""
    conn = connect_to_db(db_path)
    cursor = conn.cursor()

    # Fetch and process messages
    messages = fetch_messages(cursor, participant_jid)
    processed_data = process_messages(messages, cursor)

    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(processed_data)

    # Group by day (MessageDate in 'YYYY-MM-DD' format)
    df['MessageDay'] = df['MessageDate'].apply(lambda x: x.split(' ')[0] if x else None)
    grouped_by_day = df.groupby('MessageDay').apply(lambda x: x.to_dict(orient='records'))

    # Save grouped messages to JSON file
    save_messages_to_json(grouped_by_day, output_file)

    # Close the database connection
    conn.close()
    log.info("Database connection closed.")


if __name__ == "__main__":
    main(DATABASE_PATH, PARTICIPANT_JID)
