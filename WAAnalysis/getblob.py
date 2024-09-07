import sqlite3
import os

# Replace with the relevant database path
database_path = 'ChatStorage.sqlite'
output_directory = 'blob_output'

# Create output directory if it doesn't exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Connect to the SQLite database
conn = sqlite3.connect(database_path)
cursor = conn.cursor()

# Query to get messages and receipt info BLOBs (you can refine this query as needed)
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
    ZWAMESSAGE.ZFROMJID = '6581574286@s.whatsapp.net' OR ZWAMESSAGE.ZTOJID = '6581574286@s.whatsapp.net'
ORDER BY 
    ZWAMESSAGE.ZSENTDATE ASC
'''

cursor.execute(query)
messages = cursor.fetchall()

# Save BLOBs to files for further analysis
for i, row in enumerate(messages):
    blob_data = row[4]  # ZRECEIPTINFO is the 5th column (index 4)
    if blob_data:
        with open(f'{output_directory}/blob_{i}.bin', 'wb') as blob_file:
            blob_file.write(blob_data)

    # Output message info
    print(f"Message: {row[0]}")
    print(f"From: {row[1]}")
    print(f"To: {row[2]}")
    print(f"SentTimeRaw: {row[3]}")
    print(f"Blob saved to: blob_{i}.bin")
    print()

# Close the database connection
conn.close()
