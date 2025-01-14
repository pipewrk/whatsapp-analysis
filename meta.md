# META: WHATSAPP-ANALYSIS

## Folder Structure

```plaintext
/Users/jasonnathan/Repos/whatsapp-analysis
├── README.md
├── whatsapp-analysis
│   ├── __init__.py
│   ├── add_summaries_to_chats.py
│   ├── batch_processing.py
│   ├── batch_result_processor.py
│   ├── batch_utils.py
│   ├── chunk_large_files.py
│   ├── clean_summaries.py
│   ├── clean_yaml_frontmatter.py
│   ├── config.py
│   ├── convert_topics_to_tags.py
│   ├── correct_roles.py
│   ├── create_chatgpt_jsonl.py
│   ├── crons
│   ├── extract_messages.py
│   ├── extract_unique_tags.py
│   ├── fm_token_analysis.py
│   ├── generate_markdown.py
│   ├── generate_single_tag_cluster_jsonl.py
│   ├── getblob.py
│   ├── group_tags.py
│   ├── ingest.py
│   ├── large_token_analysis.py
│   ├── ml_tag_clustering.py
│   ├── output_tokens.py
│   ├── prepare_jsonl_db.py
│   ├── pricing.py
│   ├── prompt_testing.py
│   ├── prompts.py
│   ├── receipt_info_pb2.py
│   ├── schemas
│   ├── summarise.py
│   ├── token_analysis.py
│   ├── update_attributes.py
│   ├── update_tags_with_clusters.py
│   └── utils.py
├── chunked
├── data
│   ├── [TRUNCATED JSON AND MD FILES]
├── faiss_index
├── requirements.txt
├── storage
│   ├── ChatStorage.sqlite
├── summarized_chunked
└── tests
    ├── test_extract_messages.py
    └── test_generate_markdown.py

27 directories, 50 files
```
# whatsapp-analysis

whatsapp-analysis is a Python-based project for analysing WhatsApp messages and extracting themes, topics, and entity relationships. It processes message data, parses them into Markdown files, and uses LLMs to extract relevant information.

## Installation

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd whatsapp-analysis
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


## Git Repository

```plaintext
origin	git@github.com:jasonnathan/whatsapp-analysis.git (fetch)
origin	git@github.com:jasonnathan/whatsapp-analysis.git (push)
```
