import pytest
import sqlite3
import json
from unittest.mock import patch, MagicMock
from WAAnalysis.extract_messages import (
    connect_to_db,
    fetch_messages,
    process_messages,
    save_messages_to_json,
    main
)
from WAAnalysis.config import PARTICIPANT_JID, DATABASE_PATH


# Test connect_to_db
@patch('sqlite3.connect')
def test_connect_to_db(mock_connect):
    db_path = "test_db.sqlite"
    connect_to_db(db_path)
    mock_connect.assert_called_once_with(db_path)


# Test fetch_messages
def test_fetch_messages():
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        ("Message 1", 600000000, 600000100, "fromJID1", "toJID1", None, None, 12345, None, "/path/to/media1"),
        ("Message 2", 600000200, 600000300, "fromJID2", "toJID2", None, None, 12346, None, "/path/to/media2")
    ]

    messages = fetch_messages(mock_cursor, PARTICIPANT_JID)
    
    # Assert fetch_messages returns the correct output
    assert len(messages) == 2
    assert messages[0][0] == "Message 1"
    assert messages[1][0] == "Message 2"


# Test process_messages
@patch('WAAnalysis.extract_messages.fetch_replied_message')
@patch('WAAnalysis.extract_messages.decode_with_protoc')
def test_process_messages(mock_decode, mock_fetch_replied_message):
    mock_cursor = MagicMock()

    # Mock data
    messages = [
        ("Sample message", 600000000, 600000100, "fromJID", "toJID", None, None, 12345, None, "/path/to/media")
    ]

    # Test process_messages
    result = process_messages(messages, mock_cursor)

    # Assert the processed result
    assert len(result) == 1
    assert result[0]['Message'] == "Sample message"
    assert result[0]['MessageDate'] == "2020-01-01 00:00:00"  # Assuming you handle CoreData timestamp correctly


# Test save_messages_to_json
@patch("builtins.open", new_callable=MagicMock)
def test_save_messages_to_json(mock_open):
    # Mock data
    grouped_by_day = {
        "2024-03-09": [
            {"Message": "Sample message", "MessageDate": "2024-03-09 10:30:00"}
        ]
    }
    output_file = "mock_output.json"

    # Call the function
    save_messages_to_json(grouped_by_day, output_file)

    # Ensure the file write is called with the correct data
    mock_open.assert_called_once_with(output_file, 'w')
    mock_open().write.assert_called_once()


# Integration test for main
@patch('WAAnalysis.extract_messages.fetch_messages', return_value=[("Sample message", 600000000, 600000100, "fromJID", "toJID", None, None, 12345, None, "/path/to/media")])
@patch('WAAnalysis.extract_messages.connect_to_db')
@patch('WAAnalysis.extract_messages.save_messages_to_json')
def test_main(mock_save_json, mock_connect_db, mock_fetch_messages):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Call main
    main(DATABASE_PATH, PARTICIPANT_JID, output_file="mock_output.json")

    # Assertions
    mock_connect_db.assert_called_once_with(DATABASE_PATH)
    mock_fetch_messages.assert_called_once_with(mock_cursor, PARTICIPANT_JID)
    mock_save_json.assert_called_once()


