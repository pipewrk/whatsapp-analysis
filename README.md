# WAAnalysis

WAAnalysis is a Python-based project for analysing WhatsApp messages and extracting themes, topics, and entity relationships. It processes message data, parses them into Markdown files, and uses LLMs to extract relevant information.

## Project Structure

```bash
.
├── README.md               # Project overview and documentation
├── WAAnalysis              # Main package directory
│   ├── __init__.py         # Initialize the WAAnalysis package
│   ├── batch.py            # Handles batch processing and polling
│   ├── extract.py          # Extracts message data from SQLite database
│   ├── getblob.py          # Helper for processing blobs
│   ├── output_tokens.py    # Script to analyze token usage
│   ├── pricing.py          # Pricing calculations for token-based API calls
│   ├── prompts.py          # Stores all the prompt templates
│   ├── receipt_info_pb2.py # Handles protobuf parsing
│   ├── schemas             # Stores schema definitions for entities
│   ├── token_analysis.py   # Analyzes token sizes of documents
│   ├── tomd.py             # Converts files to markdown
│   └── utils.py            # Contains utility functions for document processing
├── data                    # Contains input JSON files and output markdowns
├── storage                 # Stores SQLite database and other artifacts
├── tests                   # Test cases for the project
└── requirements.txt        # Python dependencies
```

## Installation

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd WAAnalysis
    ```

2. Set up a virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Running the Analysis

1. **Extract WhatsApp data**: 
   Use `extract.py` to extract message data from the WhatsApp SQLite database.
   ```bash
   python src/extract.py
   ```

2. **Process Messages**: 
   Run `batch.py` to process the messages and analyze topics, themes, and entity relationships.
   ```bash
   python src/batch.py
   ```

3. **Token Analysis**: 
   Use `token_analysis.py` to calculate the token size of the processed documents.
   ```bash
   python src/token_analysis.py
   ```

4. **Convert to Markdown**: 
   Use `tomd.py` to convert message data into Markdown files.
   ```bash
   python src/tomd.py
   ```

## Testing

You can add your test scripts in the `tests/` directory and run them with pytest:
```bash
pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
