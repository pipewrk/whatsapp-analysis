import sqlite3
import logging
from WAAnalysis.config import DATABASE_PATH, BLOB_INFO_DIRECTORY, PARTICIPANT_JID
from WAAnalysis.utils import ensure_directories_exist

# -------------------------------
# Setup Logging
# -------------------------------
log = logging.getLogger(__name__)

# Ensure output directory exists
ensure_directories_exist([BLOB_INFO_DIRECTORY])

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
# Fetch Messages and BLOBs
# -------------------------------

def fetch_blob_messages(cursor, participant_jid):
    """Fetch messages and receipt info BLOBs for the specified participant."""
    query = '''
    SELECT 
        ZWAMESSAGE.ZTEXT AS Message,
        ZWAMESSAGE.ZFROMJID AS FromJID,
        ZWAMESSAGE.ZTOJID AS ToJID,
        ZWAMESSAGE.ZSENTDATE AS SentTimeRaw,
        ZWAMESSAGEINFO.ZRECEIPTINFO AS ReceiptInfoBlob
    FROM 
        ZWAMESSAGE
    LEFT JOIN 
        ZWAMESSAGEINFO ON ZWAMESSAGE.Z_PK = ZWAMESSAGEINFO.ZMESSAGE
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
# Save BLOBs to Files
# -------------------------------

def save_blobs(messages, output_directory):
    """Save the BLOBs to binary files and log the messages."""
    for i, row in enumerate(messages):
        blob_data = row[4]  # ZRECEIPTINFO is the 5th column (index 4)
        if blob_data:
            blob_path = f'{output_directory}/blob_{i}.bin'
            with open(blob_path, 'wb') as blob_file:
                blob_file.write(blob_data)

            log.info(f"Saved BLOB to {blob_path}")
        
        # Log message info
        log.info(f"Message: {row[0]}")
        log.info(f"From: {row[1]}")
        log.info(f"To: {row[2]}")
        log.info(f"SentTimeRaw: {row[3]}")

# -------------------------------
# Main Function
# -------------------------------

def main(db_path, participant_jid, output_directory):
    """Main function to orchestrate fetching and saving of BLOBs."""
    conn = connect_to_db(db_path)
    cursor = conn.cursor()

    # Fetch messages with BLOBs
    messages = fetch_blob_messages(cursor, participant_jid)

    # Save the BLOBs to the output directory
    save_blobs(messages, output_directory)

    # Close the database connection
    conn.close()
    log.info("Database connection closed.")


if __name__ == "__main__":
    main(DATABASE_PATH, PARTICIPANT_JID, BLOB_INFO_DIRECTORY)
