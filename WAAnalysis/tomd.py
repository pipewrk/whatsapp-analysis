import os
import json
from datetime import datetime
import pytz

# Load conversation data from whatsapp_messages_by_day.json
with open('whatsapp_messages_by_day.json', 'r') as f:
    conversation_data = json.load(f)

# Timezone setup for SGT
sgt = pytz.timezone('Asia/Singapore')

# Participant mapping (replace with actual names if needed)
participant_mapping = {
    "6581574286@s.whatsapp.net": "Elizabeth",
    None: "Jason"
}

# Function to convert to SGT
def convert_to_sgt(utc_time_str):
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)
    sgt_time = utc_time.astimezone(sgt)
    return sgt_time.strftime("%I:%M %p")  # SGT time in 12-hour format

# Function to extract filename from a media path (assuming it's in the data)
def extract_filename_from_path(media_path):
    if media_path:
        return os.path.basename(media_path)
    return None

# Function to format a multi-line message as a quote
def format_as_quote(message_text):
    lines = message_text.splitlines()
    return "\n".join([f"> {line}" for line in lines])

# Function to generate markdown for each day
def generate_markdown_for_day(day, messages, participant_mapping):
    markdown = "---\n"
    markdown += "topics:\nentity_relationships:\ndetailed_summary:\noverall_sentiment:\n---\n\n"
    markdown += f"# {datetime.strptime(day, '%Y-%m-%d').strftime('%A, %d %B %Y')}\n\n"
    
    for message in messages:
        from_participant = participant_mapping.get(message['FromJID'], "Unknown")
        to_participant = participant_mapping.get(message['ToJID'], "Unknown")
        message_time = convert_to_sgt(message['MessageDate'])
        
        # Handle replies
        if message['RepliedToMessageID']:
            markdown += f"**{from_participant}**: _Replying to:_\n\n"
            markdown += format_as_quote(f"**{to_participant}**: {message['Message']}\n")
            markdown += f"{message['Message']}\n"
        else:
            markdown += f"**{from_participant}**: {message['Message']}\n"
        
        # Add time and media info
        markdown += f"  {message_time}\n"
        media_filename = extract_filename_from_path(message.get('MediaPath'))  # Replace 'MediaItemID' with 'MediaPath'
        if media_filename:
            markdown += f"  Attached: {media_filename}\n"
        markdown += "\n"
    
    return markdown

# Directory to store the markdown files
output_directory = "./markdown"
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Generate markdown files for each day
for day, messages in conversation_data.items():
    markdown_content = generate_markdown_for_day(day, messages, participant_mapping)
    # Save each day as an individual markdown file
    file_name = f"{output_directory}/{day}.md"
    with open(file_name, "w") as file:
        file.write(markdown_content)
    print(f"Markdown for {day} written to {file_name}")
