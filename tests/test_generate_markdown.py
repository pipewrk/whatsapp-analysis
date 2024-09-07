import pytest
import os
import json
from pathlib import Path
from unittest.mock import patch, mock_open
from WAAnalysis.generate_markdown import main, load_conversation_data, save_markdown
from WAAnalysis.config import WHATSAPP_MESSAGES_FILE, OUTPUT_DIR
from WAAnalysis.utils import generate_markdown_for_day, convert_to_sgt

# Sample mock data for conversation
mock_conversation_data = {
    "2024-03-09": [
        {
            "Message": "This is a sample message",
            "MessageDate": "2024-03-09 10:30:00",
            "FromJID": None,
            "ToJID": "6581574286@s.whatsapp.net",
            "RepliedToMessageID": None,
            "MediaPath": None
        }
    ]
}

# Test for loading conversation data
def test_load_conversation_data(mocker):
    mock_open_file = mocker.patch("builtins.open", mock_open(read_data=json.dumps(mock_conversation_data)))
    result = load_conversation_data(WHATSAPP_MESSAGES_FILE)
    assert result == mock_conversation_data
    mock_open_file.assert_called_once_with(WHATSAPP_MESSAGES_FILE, 'r')

# Test for saving markdown to file
def test_save_markdown(mocker):
    file_name = "2024-03-09.md"
    markdown_content = "Sample markdown content"
    mock_open_file = mocker.patch("builtins.open", mock_open())
    
    save_markdown(file_name, markdown_content)
    
    mock_open_file.assert_called_once_with(file_name, 'w')
    mock_open_file().write.assert_called_once_with(markdown_content)

# Test for markdown generation for a single day
def test_generate_markdown_for_day():
    day = "2024-03-09"
    messages = mock_conversation_data[day]

    # Manually calculate the expected time based on mock data
    expected_time = convert_to_sgt("2024-03-09 10:30:00")

    # Call the function to generate markdown
    result = generate_markdown_for_day(day, messages)

    # Expected output based on mock_conversation_data
    expected_output = (
        "---\n"
        "topics:\n"
        "entity_relationships:\n"
        "detailed_summary:\n"
        "overall_sentiment:\n"
        "---\n\n"
        "# Saturday, 09 March 2024\n\n"
        "**Jason**: This is a sample message\n"
        f"  {expected_time}\n\n"
    )

    # Assert that the generated markdown matches the expected output
    assert result == expected_output

# Test for the main function with full flow

@patch('WAAnalysis.generate_markdown.save_markdown')
@patch('WAAnalysis.generate_markdown.load_conversation_data', return_value=mock_conversation_data)
@patch('pathlib.Path.mkdir')  # Mock Path.mkdir to prevent actual directory creation
@patch('pathlib.Path.exists', return_value=False)  # Mock Path.exists to simulate non-existing directory
@patch('WAAnalysis.config.OUTPUT_DIR', new=Path("/Users/jasonnathan/Repos/WAAnalysis/WAAnalysis/markdown"))  # Mock OUTPUT_DIR with the real path
def test_main(mock_exists, mock_mkdir, mock_load_conversation_data, mock_save_markdown):
    # Call the main function
    main()

    # Ensure directory existence check is called with the mocked output directory
    mock_exists.assert_called_once_with()
    
    # Ensure directory creation is called since the directory doesn't exist
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    # Prepare expected markdown content
    expected_markdown_content = (
        "---\n"
        "topics:\n"
        "entity_relationships:\n"
        "detailed_summary:\n"
        "overall_sentiment:\n"
        "---\n\n"
        "# Saturday, 09 March 2024\n\n"
        "**Jason**: This is a sample message\n"
        "  06:30 PM\n\n"
    )
    
    # Ensure the markdown file was saved correctly with the correct content
    mock_save_markdown.assert_called_once_with(
        Path("/Users/jasonnathan/Repos/WAAnalysis/WAAnalysis/markdown/2024-03-09.md"),
        expected_markdown_content
    )