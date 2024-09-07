import os
from WAAnalysis.prompts import (
    create_topics_prompt,
    create_key_points_prompt,
    create_sentiment_prompt,
    create_entities_prompt
)
from WAAnalysis.utils import read_file_content
from WAAnalysis.config import OPENAI_API_KEY, DATA_DIR
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

# Set up OpenAI API key from config

def get_openai_response(system_prompt, user_content, model):
    try:
        response = client.chat.completions.create(model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ])
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        return None

def extract_content_based_on_prompt(file_path, create_prompt_fn, model="gpt-4o-mini"):
    document_content = read_file_content(file_path)
    prompt = create_prompt_fn(document_content)
    return get_openai_response(prompt["system"], prompt["user"], model)

def test_topics_extraction(file_path):
    response = extract_content_based_on_prompt(file_path, create_topics_prompt)
    print(f"Topics Extraction Result for {file_path}:")
    print(response)

def test_key_points_extraction(file_path):
    response = extract_content_based_on_prompt(file_path, create_key_points_prompt)
    print(f"Key Points Extraction Result for {file_path}:")
    print(response)

def test_sentiment_analysis(file_path):
    response = extract_content_based_on_prompt(file_path, create_sentiment_prompt)
    print(f"Sentiment Analysis Result for {file_path}:")
    print(response)

def test_entity_extraction(file_path):
    response = extract_content_based_on_prompt(file_path, create_entities_prompt)
    print(f"Entity Extraction Result for {file_path}:")
    print(response)

def run_prompt_test(file_path, prompt_type):
    test_functions = {
        "topics": test_topics_extraction,
        "key_points": test_key_points_extraction,
        "sentiment": test_sentiment_analysis,
        "entities": test_entity_extraction
    }

    if prompt_type in test_functions:
        test_functions[prompt_type](file_path)
    else:
        print("Invalid prompt type. Please choose from: 'topics', 'key_points', 'sentiment', 'entities'.")

if __name__ == "__main__":
    file_to_test = DATA_DIR / "markdown/2018-04-14.md"  # Update this with your file path
    prompt_type_to_test = "key_points"  # Options: 'topics', 'key_points', 'sentiment', 'entities'

    run_prompt_test(file_to_test, prompt_type_to_test)
