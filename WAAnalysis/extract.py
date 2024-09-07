import sqlite3
import os
import json
from datetime import datetime
import pandas as pd
import subprocess

# Replace with the relevant JID and database path
participant_jid = '6581574286@s.whatsapp.net'
database_path = 'ChatStorage.sqlite'
blob_info_directory = './blob_info'
error_logs_directory = './error_logs'

# Ensure the blob_info and error_logs directories exist
if not os.path.exists(blob_info_directory):
    os.makedirs(blob_info_directory)

if not os.path.exists(error_logs_directory):
    os.makedirs(error_logs_directory)

# Connect to the SQLite database
conn = sqlite3.connect(database_path)
cursor = conn.cursor()

# Query to get messages, including media paths and replied-to messages
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
    ZWAMEDIAITEM.ZMEDIALOCALPATH AS MediaPath  -- Include media path
FROM 
    ZWAMESSAGE
LEFT JOIN 
    ZWAMESSAGEINFO ON ZWAMESSAGE.Z_PK = ZWAMESSAGEINFO.ZMESSAGE
LEFT JOIN
    ZWAMEDIAITEM ON ZWAMESSAGE.ZMEDIAITEM = ZWAMEDIAITEM.Z_PK  -- Join media table for media path
WHERE 
    ZWAMESSAGE.ZFROMJID = ? OR ZWAMESSAGE.ZTOJID = ?
ORDER BY 
    ZWAMESSAGE.ZSENTDATE ASC
'''

cursor.execute(query, (participant_jid, participant_jid))
messages = cursor.fetchall()

# Function to decode using `protoc --decode_raw`
def decode_with_protoc(blob, message_id):
    blob_file_path = f'{blob_info_directory}/blob_{message_id}.bin'
    with open(blob_file_path, 'wb') as blob_file:
        blob_file.write(blob)

    error_log_path = f'{error_logs_directory}/error_{message_id}.log'
    try:
        with open(blob_file_path, 'rb') as blob_file:
            protoc_output = subprocess.check_output(['protoc', '--decode_raw'], stdin=blob_file)
            protoc_output = protoc_output.decode('utf-8')
        return protoc_output
    except subprocess.CalledProcessError as e:
        error_details = f"Error running decode_raw for message ID {message_id}:\n{e.output.decode('utf-8')}"
        with open(error_log_path, 'w') as error_log:
            error_log.write(f"Error for Message ID {message_id}\n")
            error_log.write(f"BLOB Path: {blob_file_path}\n")
            error_log.write(error_details)
        return None

# Function to fetch the original replied-to message
def fetch_replied_message(replied_to_message_id):
    query = '''
    SELECT ZTEXT, ZMESSAGEDATE, ZSENTDATE, ZFROMJID, ZTOJID
    FROM ZWAMESSAGE
    WHERE Z_PK = ?
    '''
    cursor.execute(query, (replied_to_message_id,))
    return cursor.fetchone()

# Function to convert Core Data timestamp to readable date
def convert_core_data_timestamp(timestamp):
    reference_date = 978307200  # Core Data reference date: Jan 1, 2001
    if timestamp:
        return datetime.utcfromtimestamp(timestamp + reference_date).strftime('%Y-%m-%d %H:%M:%S')
    return None

# Function to calculate time difference between received and read (in seconds)
def calculate_time_to_read(timestamp_received, timestamp_read):
    if timestamp_received and timestamp_read:
        time_diff = (timestamp_read - timestamp_received) / 60  # Convert to minutes
        return f"{time_diff:.2f} minutes"
    return None

# Process messages and decode BLOBs
data = []
for idx, row in enumerate(messages):
    print(f"Processing message ID: {row[7]} ({idx + 1}/{len(messages)})")
    
    message = {
        'Message': row[0],
        'MessageDate': convert_core_data_timestamp(row[1]),
        'SentTime': convert_core_data_timestamp(row[2]),
        'FromJID': row[3],
        'ToJID': row[4],
        'MediaItemID': row[5],
        'MediaPath': row[9],  # Include media path in the output
        'MessageID': row[7],
        'RepliedToMessageID': row[8]  # Include replied-to message ID
    }
    
    # Fetch the replied-to message if it exists
    if row[8]:  # RepliedToMessageID is present
        replied_message = fetch_replied_message(row[8])
        if replied_message:
            message['RepliedToMessage'] = {
                'Text': replied_message[0],
                'MessageDate': convert_core_data_timestamp(replied_message[1]),
                'SentTime': convert_core_data_timestamp(replied_message[2]),
                'FromJID': replied_message[3],
                'ToJID': replied_message[4]
            }

    # Try to decode the protobuf BLOB using `protoc --decode_raw`
    if row[6]:
        decoded_output = decode_with_protoc(row[6], row[7])
        if decoded_output:
            message['DecodedReceiptInfo'] = decoded_output
            
            # Extract timestamp received and read from the decoded output
            # Placeholder values for now:
            timestamp_received = 1498123700  # Replace with actual extraction logic
            timestamp_read = 1498125982  # Replace with actual extraction logic

            # Calculate TimeToRead if both timestamps are present
            if timestamp_received and timestamp_read:
                message['TimeToRead'] = calculate_time_to_read(timestamp_received, timestamp_read)
        else:
            print(f"Error decoding BLOB for message ID: {row[7]}. Check error logs for details.")

    # Append to data
    data.append(message)

# Convert to DataFrame for easier manipulation
df = pd.DataFrame(data)

# Group by day (MessageDate in 'YYYY-MM-DD' format)
df['MessageDay'] = df['MessageDate'].apply(lambda x: x.split(' ')[0] if x else None)

# Group messages by day
grouped_by_day = df.groupby('MessageDay').apply(lambda x: x.to_dict(orient='records'))

# Print or save the grouped messages
for day, messages in grouped_by_day.items():
    print(f"Messages on {day}:")
    for message in messages:
        print(message)
        print()

# Optionally, you can save the grouped messages to a JSON file
with open('whatsapp_messages_by_day.json', 'w') as f:
    json.dump(grouped_by_day.to_dict(), f, indent=4)

# Close the database connection
conn.close()
